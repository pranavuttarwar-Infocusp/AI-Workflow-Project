---
description: QA ticket hygiene check — scans ClickUp tickets in "testing" and splits them by the `feature` tag. Non-feature tickets get the standard checks (PR/commit link, sprint tag). Feature tickets are audited for acceptance criteria and a PR link; a ticket with EITHER one gets core test cases generated and posted as a "QA test cases" comment after approval, while a ticket with NEITHER is bounced to "in review". Always asks the scan window first. Triggers on "/qa-ticket-check", "check tickets for acceptance criteria", "run the AC police".
---

# QA Ticket Check (Acceptance Criteria Police)

Scans tickets that entered the QA stage and bounces back any that are not actually
testable. Tickets tagged `feature` are audited for testable source material and, when they
have it, get core test cases generated and posted for them — this generation step runs on
EVERY run of this skill, not on request. Everything else gets the standard hygiene checks.

**Optional user input:** $ARGUMENTS (may contain a window like "24h", "7d", or "all",
or a specific ticket ID)

## Steps

1. **Always ask the scan window first** (skip only if $ARGUMENTS already specifies one,
   or names a single ticket). Use AskUserQuestion:
   - **Last 24 hours** — tickets updated since yesterday (the daily-run default)
   - **Last 7 days** — tickets updated this sprint
   - **All tickets** — full sweep of every open ticket
   Never start scanning without a confirmed window.

2. **Fetch candidate tickets** with `clickup_filter_tasks`:
   - Space: `AI Workflow Project` (space_id `90167656011`)
   - Status: `testing` (this is the "ready to test / in QA" stage)
   - Paginate until `has_more` is false — never stop at page one
   - If a time window was chosen, keep only tickets whose `date_updated` falls inside it

3. **Split every ticket by the `feature` tag.** Read the full task
   (`clickup_get_task`, include description) and its comments, then route it:
   - **No `feature` tag** → standard flow, step 4
   - **Has `feature` tag** → feature audit, step 5

---

### 4. Standard flow (tickets WITHOUT the `feature` tag)

Two checks. Acceptance criteria are NOT required here — that's a feature-ticket concern.

   **a) Git repo link.** A ticket in `testing` must reference the code change that
   implements it: a GitHub PR or commit URL (e.g. `github.com/.../pull/N`) in the
   description, a comment, or a task link. No repo link = QA doesn't know what
   build/change to test = FAIL.

   **b) Sprint tag.** A ticket in `testing` must carry a sprint tag, normally written
   `sprint-<N>` (convention shared with /qa-daily-report — without it the ticket is
   invisible to sprint reports). Match it LOOSELY — any tag matching `sprint[ -]?<N>`
   case-insensitively counts, so a hand-typed `sprint 1` with a space is NOT bounced.
   This check moves tickets backward to `in review`, so a too-strict match would bounce
   correctly-tagged work. No sprint tag at all = FAIL.

Failures here are bounced per step 7 (Path A).

---

### 5. Feature audit (tickets WITH the `feature` tag)

**The eligibility rule is AC *or* PR — either one is enough.** Test cases can be written
from acceptance criteria alone, from a code diff alone, or from both. Requiring both would
bounce tickets that are perfectly testable, so don't.

Look for these two **source-material** items:

   1. **Acceptance Criteria** — an explicit "Acceptance Criteria" heading/section in the
      description with at least one concrete, checkable item. Vague descriptions ("make it
      better", "needs polish") = MISSING. When genuinely borderline, list it to the user as
      "unsure" instead of acting on it.
   2. **PR / commit link** — a GitHub PR or commit URL in the description, a comment, or a
      task link.

   Routing:
   - **At least one present → Path B** (step 8): generate test cases. This is the normal
     outcome for a feature ticket and happens on every run.
   - **Neither present → Path A** (step 7): there is nothing to generate from and nothing
     for QA to test, so bounce to `in review`. That ticket's flow ends there.

**These three are warnings, never bounce reasons on this path.** Report them under
"⚠️ Worth a look" so they can be fixed, but never send a feature ticket back for them alone:

   - **Target / Test Environment** — where QA should test (browser, OS, URL, or
     "local `index.html`"). No custom fields exist in this space, so this comes from the
     description text or a comment.
   - **Build Details / Build Version** — the commit hash, tag, or PR number under test.
     Feeds the "Tested Version" column in step 8's matrix; when absent, that column reads
     "Not specified".
   - **Sprint tag** — missing means the ticket is invisible to sprint reports, but that is
     a reporting gap, not an untestable ticket.

---

### 6. Report before acting

Show the user one short table covering everything scanned:

| Ticket | Type | Assignee | Verdict |
|---|---|---|---|

- Link tickets by **name**, not bare ID
- Verdict lists whichever checks failed (AC / PR link / sprint tag / unsure), or
  "✅ eligible" for a feature ticket heading to Path B; add any ⚠️ warnings (test env,
  build details, sprint tag) as a separate note rather than a failure
- Group feature tickets and standard tickets so it's obvious which rule set applied
- If nothing is missing anywhere and no feature ticket is eligible, say so and stop

**Then generate test cases for every Path B ticket** — don't ask which ones to do, and
don't skip the step because the user didn't mention test cases. Generation is part of every
run. The user's approval is required to **post** each suite (step 9), not to draft it.

---

### 7. Path A — bounce incomplete tickets (needs approval)

For each failing ticket, after the user confirms the list:

   - Post a comment via `clickup_create_comment`, tagging the ticket's assignee. Friendly,
     never blaming, and itemizing **only** the lines that apply:

     > 👋 **QA check:** this ticket is in `testing` but is missing:
     > • an **Acceptance Criteria** section — how do we know it's done?
     > • a **link to the PR/commit** implementing it (QA doesn't know what to test)
     > • the current **sprint tag** (`sprint-<N>`) — without it the ticket is missing
     >   from sprint reports
     > Please add the missing piece(s) and move it back to `testing`.
     > Moving to `in review` until then. — automated QA ticket check

     For a feature ticket, either an AC section or a PR link clears the bounce — say so,
     so the developer knows one item is enough rather than both.

   - Move the ticket back with `clickup_update_task` → status `in review`
   - Both writes require user approval per `.claude/settings.json` — never skip
   - This ends the flow for that ticket. Do not generate test cases for a bounced ticket.

---

### 8. Path B — generate core test cases

For every Path B ticket:

   - **Inputs — whichever of the two the ticket actually has:**
     - **AC + PR** → generate from the acceptance criteria and cross-check against the diff
       (`gh pr view <n>` / `gh pr diff <n>`). Best case.
     - **AC only** → generate from the acceptance criteria alone. State in the posted
       comment that no PR was linked, so the suite is unvalidated against real code, and
       ask for the PR link.
     - **PR only** → generate from the diff alone. State in the comment that the ticket has
       no AC, so the cases reflect what the code does rather than agreed intent.
   - **Generate only core, essential, critical cases.** Cover each acceptance criterion and
     the primary happy path. Skip low-priority edge cases, browser-compat permutations, and
     speculative negatives — this is a focused smoke suite, not the exhaustive matrix.
     Aim for roughly 5–10 rows; if a feature genuinely needs more, say why.
   - **Non-testable AC items** (sign-offs, "confirm scope with product", process steps) are
     not rows. Call them out below the matrix as open questions instead.
   - **Format**: the same 10-column matrix as /qa-test-cases, so suites stay consistent:

     | Sr.No. | Area | Category | Scenario | Description | Steps | Expected Result | Comments/Ticket/Notes | Results | Tested Version |

     - **Category**: Happy Path / Critical only on this path
     - **Steps**: numbered, concrete ("1. Type 'x' in search 2. Press Esc")
     - **Results**: always starts as "Not Run"
     - **Tested Version**: the build version captured in step 5's audit, or
       "Not specified" when the ticket has none — never invent one
     - **Comments/Ticket/Notes**: the ticket link

---

### 9. Approval gate

Show the draft matrix in chat and ask explicitly, naming the count and the ticket:

   > "Post these 7 test cases as a comment on [<ticket name>](<url>)?"

   - **Rejected** → don't post. Offer to revise (add/remove cases, adjust scope) and
     re-present.
   - **Approved** → step 10

Never post without this gate, even if the user pre-approved a different ticket in the
same run.

---

### 10. Post the comment

`clickup_create_comment` on the ticket. The comment **must start with exactly**:

```
QA test cases
```

then the matrix. Nothing before that header — no greeting, no preamble.

---

### 11. Summarize

Scanned N tickets (window X) → N standard / N feature · N passed · N bounced (with links) ·
N unsure · test cases posted to N tickets.

## Important
- Ask the window FIRST, act LAST — no ClickUp write before the user has seen the verdict
  table.
- Only touch tickets in `testing`. Never change tickets in other statuses.
- Never edit the ticket description itself — that's the developer's job.
- **Test-case generation is unconditional.** Every run of this skill generates suites for
  every eligible feature ticket. Don't wait to be asked, don't ask which tickets to do, and
  don't treat it as an optional extra — the only thing gated on the user is posting.
- **Never generate test cases for a bounced ticket** — a bounced feature ticket had neither
  AC nor PR, so there is no trustworthy source material to generate from.
- **AC or PR, never both required.** A feature ticket with one of the two is eligible. Test
  environment, build details and sprint tag are warnings only and must never trigger a
  bounce on the feature path.
- **Don't duplicate test-case comments.** Before posting, check
  `clickup_get_task_comments` for an existing comment starting with `QA test cases`. If one
  exists, show the user and ask whether to post an updated suite — never silently add a
  second one.
- Link tickets by name in every report — a bare ID isn't traceable for a reader.
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
  "automated QA ticket check" bounce. If one exists and the ticket is STILL incomplete:
  1. Do NOT comment or change status again.
  2. Instead, list these tickets in the chat reply under a heading like
     **"⏳ Already warned, still incomplete"** — one line each: ticket name, clickable
     URL, what's still missing — so the user can check them quickly.
  3. After showing the list, ALWAYS ask the user: "Send a reminder comment on any
     of these?" (AskUserQuestion or plain question). Only re-comment on the ones
     the user picks — a reminder is a human decision, never automatic.
- Connector quirk: assign users by NUMERIC user ID (e.g. Pranav 228106678,
  Shekhar 228119573 — or via `clickup_get_workspace_members`); email/username
  assignment fails silently.
