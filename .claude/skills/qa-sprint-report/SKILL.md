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
  Every ticket in a sprint carries a tag following the convention `sprint-<N>`
  (e.g. `sprint-1`, `sprint-2`).
  1. If $ARGUMENTS names a sprint tag, use it.
  2. Otherwise collect all `sprint-<N>` tags present on the board's tickets and
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
   - anything else → spillover (list each with status and assignee)

3. **Detect reopens via status history.** Call
   `clickup_get_bulk_tasks_time_in_status` for the sprint's ticket IDs (bulk —
   one call for many tickets; batch if the sprint is large; the API rate limit
   is tight). For each ticket, walk the status-history order and count
   backward moves out of `testing` per the Reopen definition above. Record:
   - reopened tickets (with bounce count and assignee)
   - repeat bouncers (2+ bounces)
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
   🔁 Reopened in testing: N <ticket links + assignees, "none" if 0>
   🔥 Repeat bouncers (2+): N <links, or "none">
   🐞 Bugs filed this sprint: N
   📦 Spillover → next sprint: <ticket links + current status, or "none">

   Quality line: <one plain sentence a manager can read, e.g.
   "14 tickets, 11 done, 3 spill over; 2 reopens, both on the login feature.">
   ```

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
- Keep the report under ~15 lines; the "Quality line" is the part the manager
  actually reads — make it concrete, not generic.
- Sample/test tickets on the board are fake; if the sprint contains known
  sample tickets, count them but mark them so the numbers aren't misread.
