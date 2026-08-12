---
description: QA ticket hygiene check — scans ClickUp tickets in "testing" for missing acceptance criteria, missing PR/commit link, and missing sprint tag. Always asks the scan window first (last 24 hrs vs all tickets). For each bad ticket, posts a comment tagging the assigned developer and moves the status back to "in review"; repeat offenders are listed for review instead of re-commented. Triggers on "/qa-ticket-check", "check tickets for acceptance criteria", "run the AC police".
---

# QA Ticket Check (Acceptance Criteria Police)

Scans tickets that entered the QA stage and bounces back any that are not actually
testable because acceptance criteria are missing.

**Optional user input:** $ARGUMENTS (may contain a window like "24h", "7d", or "all")

## Steps

1. **Always ask the scan window first** (skip only if $ARGUMENTS already specifies one).
   Use AskUserQuestion:
   - **Last 24 hours** — tickets updated since yesterday (the daily-run default)
   - **Last 7 days** — tickets updated this sprint
   - **All tickets** — full sweep of every open ticket
   Never start scanning without a confirmed window.

2. **Fetch candidate tickets** with `clickup_filter_tasks`:
   - Space: `AI Workflow Project` (space_id `90167656011`)
   - Status: `testing` (this is the "ready to test / in QA" stage)
   - Paginate until `has_more` is false — never stop at page one
   - If a time window was chosen, keep only tickets whose `date_updated` falls inside it

3. **Check each ticket for THREE things.** Read the full task (`clickup_get_task`,
   include description) and its comments:

   **a) Acceptance criteria.** PRESENT only if the description has:
   - An explicit "Acceptance Criteria" heading/section with at least one concrete item, OR
   - For bugs: both "Expected Result" and repro steps (that is the testable contract)
   Vague descriptions ("make it better", "needs polish") = MISSING. When genuinely
   borderline, list it to the user as "unsure" instead of acting on it.

   **b) Git repo link.** A ticket in `testing` must reference the code change that
   implements it: a GitHub PR or commit URL (e.g. `github.com/.../pull/N`) in the
   description, a comment, or a task link. No repo link = QA doesn't know what
   build/change to test = FAIL. Bounce it with a comment asking the developer to
   link the PR.

   **c) Sprint tag.** A ticket in `testing` must carry a `sprint-<N>` tag
   (convention shared with /qa-daily-report — without it the ticket is invisible
   to sprint reports). No sprint tag = FAIL; the bounce comment asks for the
   current sprint's tag to be added.

4. **Report before acting.** Show the user a short table: ticket, assignee,
   verdict listing whichever checks failed (AC / repo link / sprint tag / unsure).
   If nothing is missing, say so and stop.

5. **For each ticket missing criteria** (after the user confirms the list):
   - Post a comment via `clickup_create_comment`, assigning/tagging the ticket's
     assignee (the developer). Keep the tone friendly, never blaming:

     > 👋 **QA check:** this ticket is in `testing` but is missing:
     > <only the lines that apply>
     > • an **Acceptance Criteria** section (how do we know it's done?)
     > • a **link to the PR/commit** implementing it (QA doesn't know what to test)
     > • the current **sprint tag** (`sprint-<N>`) — without it the ticket is
     >   missing from sprint reports
     > Please add the missing piece(s) and move it back to `testing`.
     > Moving to `in review` until then. — automated QA ticket check

   - Move the ticket back with `clickup_update_task` → status `in review`
   - Both writes require user approval per `.claude/settings.json` — never skip

6. **Summarize:** scanned N tickets (window X), N passed, N bounced (with links),
   N unsure. This summary is what gets pasted into standup/Slack.

## Important
- Ask the window FIRST, act LAST — no ClickUp write before the user has seen the
  verdict table.
- Only touch tickets in `testing`. Never change tickets in other statuses.
- Never edit the ticket description itself — that's the developer's job.
- Who to tag in the bounce comment (fallback chain):
  1. The ticket's **assigned developer** — the normal case.
  2. If unassigned → the **dev lead** (configured below), asking them to assign a
     developer.
  3. If no dev lead configured → the **ticket creator/owner**, with the message:
     "No developer is assigned on this ticket — sending it back for assignment."
  Never hardcode a person's name in the message; always resolve from the ticket
  or the config line below.
- **Dev lead:** _(not configured — set a name/user ID here to enable step 2)_
- Idempotency — never repeat the bounce comment automatically. Before commenting,
  check the ticket's comments (`clickup_get_task_comments`) for a previous
  "automated QA ticket check" bounce. If one exists and AC is STILL missing:
  1. Do NOT comment or change status again.
  2. Instead, list these tickets in the chat reply under a heading like
     **"⏳ Already warned, still missing acceptance criteria"** — one line each:
     ticket id, title, clickable URL — so the user can check them quickly.
  3. After showing the list, ALWAYS ask the user: "Send a reminder comment on any
     of these?" (AskUserQuestion or plain question). Only re-comment on the ones
     the user picks — a reminder is a human decision, never automatic.
- Connector quirk: assign users by NUMERIC user ID (e.g. Pranav 228106678,
  Shekhar 228119573 — or via `clickup_get_workspace_members`); email/username
  assignment fails silently.
