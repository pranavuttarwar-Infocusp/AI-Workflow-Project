---
description: Daily QA summary report for the TaskPulse board — counts tickets per status, filed today, entered testing, closed today, plus blockers, open tickets by priority, merges landed today, hygiene flags and trend insights. Shows the report in chat first, then posts it to the configured destination (ClickUp comment and/or Slack) after user approval. Triggers on "/qa-daily-report", "daily QA summary", "QA standup report".
---

# QA Daily Report

One glance = full board state. Replaces the manual morning ritual of counting
tickets by hand.

**Optional user input:** $ARGUMENTS (may contain a date like "yesterday" or
"2026-08-12"; default = today)

## Configuration

- **Space:** `AI Workflow Project` (space_id `90167656011`)
- **Sprint — how the current sprint is determined:** sprints are TAGS, not list
  names. Every ticket in a sprint carries a tag naming the sprint number. Match
  the tag loosely — the board currently uses a SPACE (`sprint 1`, `sprint 2`),
  and a hyphen (`sprint-1`) must match too. Treat any tag matching
  `sprint[ -]?<N>` case-insensitively as sprint N; never match on the exact
  literal, or a board using the other spelling silently reports zero sprints.
  1. Collect all sprint tags present on the board's tickets
  2. The CURRENT sprint = the highest N found
  3. Report scope = tickets carrying that tag — read them from the board fetch
     already in hand, do NOT spend a second `clickup_filter_tasks` call on a
     `tags` filter; the board snapshot still shows the whole space
  4. State in the report which sprint tag was used, spelled as it appears on
     the board
  Never ask the user which sprint it is on a scheduled run — resolve it.
- **Hygiene rule that comes with tags:** any ticket in `to do`/`in progress`/
  `in review`/`testing` WITHOUT a sprint tag (matched as above) is invisible to sprint
  reports — list such tickets under ⚠️ Flags ("in flight but not tagged to a
  sprint") so they get tagged.
- **Destinations (each behind its own approval):**
  1. ClickUp Doc **"QA Daily Reports — TaskPulse"** in the AI Workflow Project
     space — ONE PAGE PER DAY: each run creates a new page titled
     `YYYY-MM-DD (Weekday)` via `clickup_create_document_page` containing that
     day's report. The doc EXISTS — do not create another one:
     **document_id `2kz0xde9-556`** (workspace `90161722825`), at
     https://app.clickup.com/90161722825/docs/2kz0xde9-556
     Before writing, call `clickup_list_document_pages` on that ID and look for a
     page whose name is today's `YYYY-MM-DD (Weekday)`. If it exists (a re-run),
     UPDATE it with `clickup_update_document_page`; only call
     `clickup_create_document_page` when today has no page yet. Never call
     `clickup_create_document` — a second doc with the same name would split the
     history silently.
  2. Slack: _(not configured — the team wants Infocusp Slack, which is not yet
     authorized; add the channel ID here once connected)_
- Report timezone: user's local (Asia/Kolkata)

## Steps

1. **Fetch the board — the API budget matters, read this before calling.**

   ClickUp rate limits are tight, so the fetch order below is deliberate.
   The important constraint: **`clickup_filter_tasks` does NOT return
   `date_created` or `date_updated`** — only `date_closed`. Every other
   date-based number therefore needs either a filter that answers the question
   server-side, or a `clickup_get_task` read per ticket. Per-ticket reads are
   the expensive path and must stay bounded.

   - **Call 1 — the board.** `clickup_filter_tasks` for the space with
     `include_closed: true`, `order_by: "created"`, and `reverse` omitted, which
     returns NEWEST first. Paginate until `has_more` is false. This one call
     gives statuses, priorities, assignees, tags and list names for everything,
     plus creation ORDER (verified: `reverse: true` flips it to oldest-first).
   - **Call 2 — closed today.** `clickup_filter_tasks` with
     `date_closed_from` and `date_closed_to` both set to the report date. This
     answers "closed today" server-side with zero per-ticket reads. Never
     compute this by reading tickets one by one.
   - **Bounded date probes.** Only for the numbers that genuinely need exact
     timestamps, and always walking from the end of the sorted list where the
     answer lives, stopping as soon as a ticket falls outside the window:
     - *Filed today*: walk the NEWEST end of call 1, reading tickets until one
       was created before the report date, then stop. On a normal day this is a
       handful of reads, not the whole board.
     - *Entered testing today* and *stuck in testing*: read only tickets whose
       current status is `testing` — that queue is small by design.
     - *Oldest open*: the OLDEST end of call 1 already gives the ranking with no
       reads at all. Read at most the 3 oldest open tickets to put exact ages on
       them, and skip even that if the budget below is tight.
   - **Hard budget: at most 10 `clickup_get_task` reads per run.** If a probe
     would exceed it, stop probing and mark the affected line "approx (API
     budget reached)". Report the ranking you do have rather than a number you
     had to guess. Cost scales with the board: this keeps a 100-ticket board at
     roughly a dozen calls instead of 101.

2. **Compute the numbers** (all derived from the fetched tasks — never guess):
   - **Board snapshot:** count of tickets per status (backlog / to do /
     in progress / in review / testing / done / Closed)
   - **Filed today:** `date_created` = report date, from the newest-end probe
   - **In testing now:** current status `testing` (the QA queue) — from call 1,
     no reads needed
   - **Entered testing today:** status is `testing` and `date_updated` = report
     date (approximation — note it as such in the report)
   - **Closed today:** straight from call 2's result count
   - **Blocked:** current status `blocked`, with assignee names
   - **By priority:** among OPEN tickets (anything not `done`/`Closed`), count
     per ClickUp priority — `urgent` / `high` / `normal` / `low` / none set.
     Urgent and high tickets are listed individually with ID, title, assignee
     and current status; normal and low are counted only. A ticket with no
     priority set that is in `in progress` or `testing` is a hygiene flag.
   - **Hygiene flags:** tickets in `testing` or `in progress` with no assignee;
     tickets in `testing` with no acceptance criteria per the last
     `/qa-ticket-check` run if known (do NOT re-scan descriptions here — that is
     qa-ticket-check's job; just link to it)

3. **Check what shipped into the QA queue.** Run
   `git log --oneline --since="<report date> 00:00" main` in the project repo to
   list merges landed since the start of the report day. These are the builds QA
   should be testing today. Map a commit to a ticket when its branch name or
   message carries a task ID (the repo convention is `<type>/<task-id>-slug` and
   `(#<task-id>)` in the PR title) and show that ID alongside. This is a local
   read — it costs no ClickUp API calls. If the repo is unavailable or the log is
   empty, print "no merges" rather than omitting the section.

4. **Derive the insights** from data already fetched in step 1 — no new calls
   beyond the bounded probes already budgeted there. Only include a bullet when
   it is actually true; skip the section entirely when nothing is worth saying:
   - **Oldest open:** the 3 open tickets sitting at the oldest end of call 1's
     ordering, with their age in days — these are the ones quietly rotting. If
     the read budget is exhausted, list them in order without exact ages rather
     than dropping the bullet.
   - **Stuck in testing:** tickets in `testing` whose `date_updated` is more than
     3 days old — the QA queue is not moving on them
   - **Trend:** whether open-ticket count rose or fell versus the previous day's
     report page, when one exists
   - **Clustering:** if 3 or more tickets filed in the last 7 days share a tag or
     an obvious feature area, name it — that area likely needs deeper testing

5. **Render the report** in this exact compact format:

   ```
   📊 QA Daily Report — <Weekday, DD Mon YYYY>
   Sprint: <the sprint-<N> tag resolved in Configuration>

   Board: backlog N · to do N · in progress N · in review N · testing N · done N

   🆕 Filed today: N <(links if 1–3, count only if more)>
   🧪 In testing: N (entered today: N)
   ✅ Closed today: N
   🚫 Blocked: N <assignees>
   🔥 Open by priority: urgent N · high N · normal N · low N · unset N
      <one line per urgent/high ticket: ID — title — assignee — status>
   📈 Sprint-wise: sprint-1 N open / N done · sprint-2 N open / N done
      (one entry per sprint tag that still has OPEN tickets — fully closed
      sprints drop off; leftovers from old sprints are the signal here)
   🔀 Merged today: N <ticket ID + one-line summary each, or "no merges">
   ⚠️ Flags: <unassigned-in-flight tickets, or "none">
   💡 Watch: <insight bullets from step 4 — omit the line if there are none>

   Yesterday vs today: testing N→N, done N→N   (only if prior data available)
   ```

   Order matters: urgent and high tickets come before everything optional, so
   the first thing read is the thing that needs action.

6. **Show the report in chat FIRST.** The user sees exactly what will be posted.

7. **Post after approval** to whatever is configured in Configuration:
   - ClickUp Doc: create/update today's dated page in the
     "QA Daily Reports — TaskPulse" doc (see Configuration for the exact flow)
   - Slack (when configured): `slack_send_message` to the configured channel —
     sending a Slack message ALWAYS requires explicit user approval in chat
   - Each destination's write gets its own approval

8. **Suggest scheduling** (once, not every run): when the user is happy with the
   format, offer to schedule this skill as a recurring weekday morning task so
   it runs hands-free (Phase 5 of the rollout plan).

## Important

- Read-only except the final post — the report never changes ticket state.
- Show before send, every time. No silent posting, even when scheduled.
- If the ClickUp API rate limit blocks the fetch, report that plainly and stop —
  never fabricate counts or reuse stale numbers as if they were current. If it
  hits partway through the date probes, keep the counts from call 1 (they are
  real), mark the date-based lines "unavailable — rate limited", and still show
  the report. A partial report labelled honestly beats no report.
- Keep the report under ~20 lines — a summary nobody reads is worse than none.
  The optional sections (merges, insights) are the first things to cut when it
  runs long; the counts and the urgent/high list never get cut.
- Insights are observations, not conclusions. Say "3 of this week's tickets are
  on the filter UI" — do not diagnose why, and never guess at a cause the data
  does not show.
- The merge list reports what git actually says. If a commit carries no task ID,
  show it without one rather than inferring which ticket it belongs to.
- "Entered testing today" via `date_updated` is an approximation (any update
  bumps it); mention the caveat in-report until real status-history data is
  wired in (`clickup_get_bulk_tasks_time_in_status` can replace it later, at
  the cost of extra API calls).
