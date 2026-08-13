---
description: Sprint-close quality report for the TaskPulse board — completed vs spillover, tickets reopened during testing (via status history), repeat bouncers, and bugs filed during the sprint. Shows the report in chat first, then posts it to a ClickUp doc page after user approval. Triggers on "/qa-sprint-report", "sprint quality report", "sprint review report", "sprint reopen report".
---

# QA Sprint Report

Sprint-close quality check. The daily report says how much moved today; this one
says how GOOD the sprint's work was — reopens, bounce-backs, and what spills
over into the next sprint.

**Optional user input:** $ARGUMENTS (may contain a sprint tag like "sprint-1";
default = resolve the current sprint automatically)

## Configuration

- **Space:** `AI Workflow Project` (space_id `90167656011`)
- **Sprint — how the sprint is determined:** sprints are TAGS, not list names.
  Every ticket in a sprint carries a tag naming the sprint number, normally
  written `sprint-1`, `sprint-2`. Match it LOOSELY: treat any tag matching
  `sprint[ -]?<N>` case-insensitively as sprint N, so a hand-typed `sprint 1`
  with a space still resolves. Matching the exact literal instead makes a board
  using the other spelling report an empty sprint with no error.
  1. If $ARGUMENTS names a sprint tag, use it (match it the same loose way).
  2. Otherwise collect all sprint tags present on the board's tickets and
     use the highest N (= the current sprint).
  3. On an interactive run, confirm the resolved tag with the user before the
     heavy per-ticket work. On a scheduled run, never ask — resolve and state
     which tag was used in the report.
- **Reopen definition:** a backward status move out of `testing` — i.e. the
  status history shows `testing` followed later by `in progress` or `in review`.
  Each such backward move = one bounce. A ticket with 2+ bounces is a
  **repeat bouncer**.
- **Spillover definition:** any ticket carrying the sprint tag whose current
  status is not `done`/`Closed` at report time. Carrying it forward = adding the
  next sprint's tag (the report suggests this; it never re-tags by itself).
- **Destination (behind approval):** ClickUp Doc
  **"QA Sprint Reports — TaskPulse"** in the AI Workflow Project space — ONE
  PAGE PER SPRINT: each run creates a page titled `Sprint <N> (<start> – <end>)`
  via `clickup_create_document_page`. Create the doc itself via
  `clickup_create_document` on first run if missing, and record its ID here:
  _not yet created_.
  If the sprint's page already exists (re-run), update it with
  `clickup_update_document_page` instead of creating a duplicate.
- Report timezone: user's local (Asia/Kolkata)

## Steps

1. **Fetch the sprint's tickets.** `clickup_filter_tasks` for the space with
   the `tags` filter set to the sprint tag (paginate until `has_more` is false,
   `include_closed: true` — closed tickets are the successes, they must be in).
   Also fetch bug-tagged tickets created during the sprint window (see step 4).

2. **Split completed vs spillover** from current status:
   - `done` / `Closed` → completed
   - anything else → spillover (list each with TITLE, status and assignee)
   Keep each ticket's title from the step 1 fetch alongside its ID from here on
   — every list in this report is read by a human who needs to know which
   ticket it is without opening ClickUp.

3. **Detect reopens via status history.** Call
   `clickup_get_bulk_tasks_time_in_status` for the sprint's ticket IDs (bulk —
   one call for many tickets; batch if the sprint is large; the API rate limit
   is tight). For each ticket, walk the status-history order and count
   backward moves out of `testing` per the Reopen definition above. The bulk
   call returns IDs only — join its results back to the titles from step 1 so
   the reopen and bouncer lists carry titles, not bare IDs. Record:
   - reopened tickets (with title, bounce count and assignee)
   - repeat bouncers (2+ bounces) — the list most likely to be acted on, so
     titles matter most here
   - any pattern worth a human sentence (e.g. both reopens on one feature)
   If the bulk history call is unavailable or rate-limited, say so in the
   report and mark the reopen section "no data" — never infer reopens from
   `date_updated`.

4. **Count bugs filed during the sprint:** tickets created between the sprint's
   start and end dates that are bugs (bug tag, or "bug"-type name per the
   `/qa-bug-report` convention). Sprint dates come from the sprint list name or
   the user; if unknown, use the earliest/latest activity on the sprint's
   tickets and say the window is approximate.

5. **Render the report** in this exact compact format:

   ```
   🏁 QA Sprint Report — sprint-<N> (<DD Mon> – <DD Mon YYYY>)

   Scope: N tickets · ✅ done N · 📦 spillover N
   🔁 Reopened in testing: N ("none" if 0; one line each)
      <ID> — <title> — <assignee> — <N> bounce(s)
   🔥 Repeat bouncers (2+): N ("none" if 0; one line each)
      <ID> — <title> — <assignee> — <N> bounces
   🐞 Bugs filed this sprint: N
   📦 Spillover → next sprint: N ("none" if 0; one line each)
      <ID> — <title> — <current status> — <assignee>

   Quality line: <one plain sentence a manager can read, e.g.
   "14 tickets, 11 done, 3 spill over; 2 reopens, both on the login feature.">
   ```

   **ALWAYS print the ticket TITLE next to the ID — never a bare ID.** A tester
   reading `86d40ecg7` has to go look it up; `86d40ecg7 — Improve search` they
   can act on immediately. This applies to every ticket mentioned anywhere in
   the report, including the Quality line, which should name features in words
   ("both reopens on the search feature"), not IDs. Titles come from the fetch
   in step 1 — no extra API calls. Truncate a long title to ~60 characters with
   an ellipsis rather than dropping it or wrapping the line.

6. **Show the report in chat FIRST.** The user sees exactly what will be
   posted.

7. **Post after approval** to the ClickUp doc per Configuration. If the user
   approves re-tagging spillover tickets to the next sprint, do that as a
   separate, second approval — never bundle it with the post.

8. **Suggest scheduling** (once, not every run): when the user is happy with
   the format, offer to schedule this skill to run at sprint close (Friday
   evening) hands-free (Phase 5 of the rollout plan).

## Important

- Read-only except the final post (and the optional, separately-approved
  spillover re-tag) — the report itself never changes ticket state.
- Show before send, every time. No silent posting, even when scheduled.
- Budget API calls: one filtered fetch + one bulk time-in-status call is the
  target. No per-ticket reads unless a specific ticket needs a detail.
- If the ClickUp API rate limit blocks a step, report that plainly and stop —
  never fabricate counts or present stale/partial data as complete.
- Ticket titles are never dropped to save space — a bare ID costs the reader a
  ClickUp lookup, which defeats the point of the report. If a section runs long,
  cut the number of tickets listed (with "+N more") rather than their titles.
- Keep the report to ~20 lines; the "Quality line" is the part the manager
  actually reads — make it concrete, not generic.
- Sample/test tickets on the board are fake; if the sprint contains known
  sample tickets, count them but mark them so the numbers aren't misread.
