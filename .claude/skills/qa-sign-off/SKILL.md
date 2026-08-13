---
description: QA sign-off gate before moving a TaskPulse user story from Testing to Done in ClickUp. Verifies no bug/clarification/enhancement ticket in the current sprint is unassigned, and no active blockers or high-priority bugs are still open. Returns a PASS/FAIL verdict with evidence.
---

# QA Sign-Off Gate

Run this **before** moving a user story from `testing` to `done`. It answers one question:
*is the sprint clean enough to sign this story off?*

## Input

The user will provide the story being signed off — a ClickUp task ID, URL, or title
(e.g. "86d40ecg7", "Improve search"). They may also name a sprint explicitly.

If no story is given, still run both sprint-level checks and report the sprint's readiness.

**User's input:** $ARGUMENTS

## Where things live

- Space: **AI Workflow Project**
- Sprints are **Lists** named `Sprint <N> (<start>–<end>)`, e.g. `Sprint 1 (Aug 11–15)`
- Other lists in the space: `Backlog`, `TaskPulse Board`, `List`
- There are **no custom fields** — severity comes from the built-in `priority` field
- Statuses: `backlog`, `to do`, `in progress`, `in review`, `testing`, `blocked`,
  `duplicate`, `done`, `Closed`

Resolve IDs at runtime with `clickup_get_workspace_hierarchy` — never hardcode list IDs,
they change every sprint.

## Definitions used by this gate

State these in the report so the verdict is auditable:

- **In-sprint** = the ticket is **in the sprint List**. List membership is authoritative;
  `sprint-N` tags are advisory only. (Tags and lists have disagreed in practice — see
  step 2's mismatch warning.)
- **Open** = status is NOT `done`, `Closed`, or `duplicate`
- **Ticket type** = the `bug` / `clarification` / `enhancement` tag. If a ticket carries no
  type tag, fall back to the title (`Fix:` / `Bug:` prefix → bug) and flag it as untyped.
- **High-priority bug** = a bug that is **open** with priority `urgent` or `high`
- **Active blocker** = an **open** in-sprint ticket in `blocked` status, or tagged `blocker`

## Steps

1. **Resolve the sprint**:
   - `clickup_get_workspace_hierarchy` → find lists in the **AI Workflow Project** space
     matching `Sprint <N> (...)`
   - Pick the sprint whose date range contains today. If today falls outside every range,
     or two ranges overlap, **stop and ask** which sprint to gate against — don't guess.
   - If the user named a sprint, use that one

2. **Pull every ticket in the sprint**:
   - `clickup_filter_tasks` with `list_ids: [<sprint list id>]` and `include_closed: true`
   - **Paginate**: if `has_more` is true, keep requesting `next_page` until it's false. A
     partial fetch produces a false PASS — this is the single most dangerous failure mode
     of this skill.
   - Note any ticket whose `sprint-N` tag disagrees with the sprint list it sits in, and
     report it under Warnings (non-blocking, but it means someone's board is wrong)

3. **Check 1 — no unassigned bug/clarification/enhancement ticket**:
   - Scope: in-sprint tickets of type `bug`, `clarification`, or `enhancement`
   - Fail if any such ticket has an empty `assignees` array
   - Include tickets in **any** status, closed ones too — an unassigned closed ticket means
     nobody owned the fix, which is exactly the audit gap this check exists to catch. Call
     out closed-vs-open in the evidence so the reader can judge.
   - Untyped tickets: list them separately as a Warning. Don't silently treat them as
     in-scope or out-of-scope — say "N tickets have no type tag, so this check may be
     incomplete."

4. **Check 2 — no active blockers or open high-priority bugs**:
   - Fail if any in-sprint ticket is an **active blocker** (per the definition above)
   - Fail if any **open** in-sprint bug has priority `urgent` or `high`
   - A ticket with **no priority set** cannot be cleared as low-risk — list it as a Warning
     and say the check is inconclusive for it

5. **Check the story itself** (only when a story was named):
   - Confirm it's actually in `testing`. If it's already `done`/`Closed`, say so and stop.
     If it's earlier in the flow (`in progress`, `in review`), warn that it hasn't been
     tested yet and the gate is premature.
   - Confirm it has an assignee

6. **Report** in this format:

   ```
   # QA Sign-Off — <story name> (<id>)
   **Sprint**: <sprint list name>
   **Story status**: <current status>
   **Tickets evaluated**: <n> (<n> open / <n> closed)

   ## VERDICT: PASS — clear to move to Done
   ## VERDICT: FAIL — do not move to Done

   ### Check 1 — Unassigned bug/clarification/enhancement tickets
   PASS / FAIL
   | Ticket | Type | Status | Assignee |
   |--------|------|--------|----------|
   (only rows that fail; on PASS state "N tickets checked, all assigned")

   ### Check 2 — Active blockers & open high-priority bugs
   PASS / FAIL
   | Ticket | Type | Status | Priority | Why it blocks |
   |--------|------|--------|----------|---------------|

   ### Warnings (non-blocking)
   - <untyped tickets, missing priority, sprint tag/list mismatches>

   ### What to do next
   - <for a FAIL: the specific tickets to assign, close, or unblock, with links>
   ```

7. **Do not change anything in ClickUp.** This skill is read-only: it reports a verdict, the
   user moves the story. If the user explicitly asks you to move it after a PASS, confirm the
   target status with them first, then use `clickup_update_task` — never as an automatic
   consequence of a PASS.

## Important
- **FAIL closed, not open.** If a check can't be completed — pagination cut short, a ticket
  type can't be determined, the sprint can't be resolved — report it as **inconclusive**, not
  PASS. A sign-off gate that guesses in the optimistic direction is worse than no gate.
- Always show the **evidence**, not just the verdict — every failing row gets a ticket link
  so it's actionable without re-querying
- Always print the definitions used (in-sprint, open, high-priority bug). Reasonable people
  disagree about these, and an auditable verdict beats a confident one.
- Read-only by default — never move the story, close a ticket, or reassign anything without
  explicit confirmation in that moment
- Priority in ClickUp is `urgent` > `high` > `normal` > `low`. "High priority" for this gate
  means `urgent` **or** `high` — urgent is more severe than high, so excluding it would be
  a bug in the gate.
- Keep the report short enough to read before a standup — failing rows and next actions
  first, warnings after
