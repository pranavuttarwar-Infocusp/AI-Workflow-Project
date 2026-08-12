---
description: Daily QA summary report for the TaskPulse board — counts tickets per status, filed today, entered testing, closed today, plus blockers and hygiene flags. Shows the report in chat first, then posts it to the configured destination (ClickUp comment and/or Slack) after user approval. Triggers on "/qa-daily-report", "daily QA summary", "QA standup report".
---

# QA Daily Report

One glance = full board state. Replaces the manual morning ritual of counting
tickets by hand.

**Optional user input:** $ARGUMENTS (may contain a date like "yesterday" or
"2026-08-12"; default = today)

## Configuration

- **Space:** `AI Workflow Project` (space_id `90167656011`)
- **Sprint — how the current sprint is determined:** sprints are TAGS, not list
  names. Every ticket in a sprint carries a tag following the convention
  `sprint-<N>` (e.g. `sprint-1`, `sprint-2`).
  1. Collect all `sprint-<N>` tags present on the board's tickets
  2. The CURRENT sprint = the highest N found
  3. Report scope = tickets carrying that tag (use `clickup_filter_tasks` with
     the `tags` filter); board snapshot section may still show the whole space
  4. State in the report which sprint tag was used
  Never ask the user which sprint it is on a scheduled run — resolve it.
- **Hygiene rule that comes with tags:** any ticket in `to do`/`in progress`/
  `in review`/`testing` WITHOUT a `sprint-<N>` tag is invisible to sprint
  reports — list such tickets under ⚠️ Flags ("in flight but not tagged to a
  sprint") so they get tagged.
- **Destinations (post to BOTH, each behind its own approval):**
  1. ClickUp comment on the current sprint list — the daily visibility ping
  2. ClickUp Doc **"QA Daily Reports"** in the AI Workflow Project space —
     append today's report under a dated heading, newest on top (create the doc
     via `clickup_create_document` on first run if it doesn't exist, and record
     its ID here: _not yet created — pending API quota reset_)
  3. Slack: _(not configured — the team wants Infocusp Slack, which is not yet
     authorized; add the channel ID here once connected)_
- Report timezone: user's local (Asia/Kolkata)

## Steps

1. **Fetch the board.** `clickup_filter_tasks` for the space (paginate until
   `has_more` is false, `include_closed: true` so closed tickets are counted).
   Keep API calls minimal — one filtered fetch, no per-ticket reads unless a
   check below needs it (ClickUp rate limits are tight).

2. **Compute the numbers** (all derived from the fetched tasks — never guess):
   - **Board snapshot:** count of tickets per status (backlog / to do /
     in progress / in review / testing / done / Closed)
   - **Filed today:** `date_created` = report date
   - **In testing now:** current status `testing` (the QA queue)
   - **Entered testing today:** status is `testing` and `date_updated` = report
     date (approximation — note it as such in the report)
   - **Closed today:** `date_closed` = report date
   - **Blocked:** current status `blocked`, with assignee names
   - **Hygiene flags:** tickets in `testing` or `in progress` with no assignee;
     tickets in `testing` with no acceptance criteria per the last
     `/qa-ticket-check` run if known (do NOT re-scan descriptions here — that is
     qa-ticket-check's job; just link to it)

3. **Render the report** in this exact compact format:

   ```
   📊 QA Daily Report — <Weekday, DD Mon YYYY>
   Sprint: <sprint list name>

   Board: backlog N · to do N · in progress N · in review N · testing N · done N

   🆕 Filed today: N <(links if 1–3, count only if more)>
   🧪 In testing: N (entered today: N)
   ✅ Closed today: N
   🚫 Blocked: N <assignees>
   📈 Sprint-wise: sprint-1 N open / N done · sprint-2 N open / N done
      (one entry per sprint tag that still has OPEN tickets — fully closed
      sprints drop off; leftovers from old sprints are the signal here)
   ⚠️ Flags: <unassigned-in-flight tickets, or "none">

   Yesterday vs today: testing N→N, done N→N   (only if prior data available)
   ```

4. **Show the report in chat FIRST.** The user sees exactly what will be posted.

5. **Post after approval** to whatever is configured in Configuration:
   - ClickUp: `clickup_create_comment` with `entity_type: "list"` on the sprint
     list (falls back to a comment on the sprint list's first view if list
     comments are unsupported)
   - Slack (when configured): `slack_send_message` to the configured channel —
     sending a Slack message ALWAYS requires explicit user approval in chat
   - Posting to both is fine; each write gets its own approval

6. **Suggest scheduling** (once, not every run): when the user is happy with the
   format, offer to schedule this skill as a recurring weekday morning task so
   it runs hands-free (Phase 5 of the rollout plan).

## Important

- Read-only except the final post — the report never changes ticket state.
- Show before send, every time. No silent posting, even when scheduled.
- If the ClickUp API rate limit blocks the fetch, report that plainly and stop —
  never fabricate counts or reuse stale numbers as if they were current.
- Keep the report under ~15 lines — a summary nobody reads is worse than none.
- "Entered testing today" via `date_updated` is an approximation (any update
  bumps it); mention the caveat in-report until real status-history data is
  wired in (`clickup_get_bulk_tasks_time_in_status` can replace it later, at
  the cost of extra API calls).
