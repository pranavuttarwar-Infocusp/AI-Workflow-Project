---
description: QA ticket hygiene check — scans ClickUp tickets in "testing" and splits them by the `feature` tag. Non-feature tickets get the standard checks (PR/commit link, sprint tag). Feature tickets are audited for acceptance criteria and a PR link; a ticket with EITHER one gets core test cases generated ONCE and posted as a "QA test cases" comment after approval, while a ticket with NEITHER is bounced to "in review". A ticket that already has its suite is skipped on later runs, so a daily run never re-posts. Also stamps a `reached-testing` tag on every ticket it scans, which is how the release report spots tickets closed without ever being tested. Always asks the scan window first. Triggers on "/qa-ticket-check", "check tickets for acceptance criteria", "run the AC police".
---

# QA Ticket Check (Acceptance Criteria Police)

Scans tickets that entered the QA stage and bounces back any that are not actually
testable. Tickets tagged `feature` are audited for testable source material and, when they
have it, get core test cases generated and posted for them without being asked — but only
**once per ticket**. A feature ticket that already carries its `QA test cases` comment is
recognised and skipped, so a ticket parked in `testing` for weeks is covered on the first
run and silent on every run after. Everything else gets the standard hygiene checks.

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
   (`clickup_get_task`, include description) and its comments
   (`clickup_get_task_comments` — you need them for step 5a, so fetch them here rather
   than twice), then route it:
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

#### 5a. First: has this ticket already been covered?

**Check this BEFORE anything else, and before generating a single row.** The posted
comment is the record — there is no state file to keep, and none should be added: both QA
engineers run this skill, and only ClickUp is shared between them.

Scan the comments fetched in step 3 for one starting with `QA test cases`:

   - **No such comment** → this ticket has never been covered. Continue to 5b.
   - **Comment exists, and the ticket's PR/commit link is the same one the comment was
     generated from** → **Path C: skip silently.** Do not read the diff, do not draft a
     matrix, do not ask the user anything. Report it in step 6 as
     `✅ cases already posted` and move on. This is the normal outcome for any feature
     ticket that has been sitting in `testing` since a previous run.
   - **Comment exists, but the ticket now carries a PR/commit link that is not the one in
     the posted comment** → **Path C-changed.** Still post nothing automatically. List the
     ticket in step 6 under **"⚠️ Cases posted, but the PR has changed since"** with both
     links, and ask once whether to draft a refreshed suite. Only if the user says yes does
     it go to Path B, and the new comment must say it supersedes the earlier one.

Rationale: strict once-ever would leave QA testing an outdated suite after a developer
pushes a new PR to the same ticket. Keying on the PR link means the skill stays quiet on
every ordinary day and speaks up only when the thing under test actually changed.

#### 5b. Then: is there anything to generate from?

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

   Routing (only reached when 5a found no existing suite):
   - **At least one present → Path B** (step 8): generate test cases. This is the normal
     outcome the first time a feature ticket is seen.
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
  "✅ eligible" for a feature ticket heading to Path B, or "✅ cases already posted" for a
  Path C skip; add any ⚠️ warnings (test env, build details, sprint tag) as a separate note
  rather than a failure
- **Always list Path C skips in the table** — never omit them. A ticket that silently
  disappears from the report reads as "it left `testing`", which is a different and much
  more alarming thing than "it's already covered"
- Group feature tickets and standard tickets so it's obvious which rule set applied
- If nothing is missing anywhere and every feature ticket is either already covered or
  ineligible, say so and stop

**Then generate test cases for every Path B ticket** — don't ask which ones to do, and
don't skip the step because the user didn't mention test cases. Generation is automatic for
any feature ticket that reaches Path B. The user's approval is required to **post** each
suite (step 9), not to draft it.

---

### 6b. Mark every scanned ticket as having reached `testing` (needs approval)

Every ticket fetched in step 2 was in `testing` when this skill saw it — that is
the filter. Record that fact so it survives, because nothing else does:
`Total time in Status`, the ClickApp that exposes real status history to the
API, needs the ClickUp **Business** plan and this workspace is on **Free**. With
no record, a ticket dragged straight from `in review` to `done` is
indistinguishable from one QA actually tested. /qa-release-report reads this tag
to answer "what shipped without being tested".

   - Add the tag `reached-testing` with `clickup_add_tag_to_task` to every
     ticket scanned this run that does not already carry it. You already have
     each ticket's tags from step 2, so the check costs nothing.
   - **One tag, ever. Never incremented, never removed.** It records a fact that
     cannot become false — the ticket reached `testing` once, and re-reaching it
     later changes nothing. This is deliberately unlike `bounced-<N>`, which
     counts events.
   - **Applies to every scanned ticket, whatever its verdict** — passed,
     bounced, already covered, unsure. The fact recorded is "QA saw this in
     `testing`", not "QA approved it". Skipping the bounced ones would make a
     bounced ticket look untested forever, which is exactly backwards: a bounce
     is proof it was in `testing`.
   - Bundle it into ONE approval for the whole batch, asked after the step 6
     table so no write happens before the user has seen the verdicts:
     *"Tag these 5 tickets `reached-testing`?"* Never ask per ticket.
   - **If the user declines, do not tag and say what it costs in one line** —
     those tickets will show up in the next release report as having no record
     of reaching Testing. Then carry on with the rest of the run; this step
     never blocks a bounce or a test-case post.

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

   - **Record the bounce as a tag** — this is what makes reopen counting possible
     at all on a Free ClickUp plan. `Total time in Status` (the ClickApp that
     exposes real status history to the API) requires the Business plan, so on
     this workspace `clickup_get_bulk_tasks_time_in_status` returns no data for
     every ticket. A tag is the substitute, and tags come back in the ordinary
     `clickup_filter_tasks` response, so /qa-sprint-report reads the count with
     no extra API calls.

     Scheme — cumulative, one tag per bounce:
     1. Read the ticket's existing tags for any matching `bounced-<N>`
        (case-insensitive). You already have them from the step 2 fetch.
     2. Take the HIGHEST N present; if none, N = 0.
     3. Add `bounced-<N+1>` with `clickup_add_tag_to_task`.

     Keep the earlier `bounced-*` tags — do NOT remove them. Removing costs an
     extra call per bounce and a failed removal would leave the count wrong in
     a way nothing can detect later; leaving them gives an audit trail and the
     reader can still see the count at a glance.

   - All three writes (comment, status, tag) require user approval per
     `.claude/settings.json` — never skip. The tag is part of the same bounce
     approval, not a separate question: a bounce that moves the status but
     skips the tag is invisible to every future sprint report.
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
   - **Format**: the same 11-column matrix as /qa-test-cases, so suites stay consistent
     wherever they were generated:

     | Sr.No. | Area | Category | Scenario | Description | Steps | Expected Result | Source | Comments/Ticket/Notes | Results | Tested Version |

     - **Category**: Happy Path / Critical only on this path
     - **Steps**: numbered, concrete ("1. Type 'x' in search 2. Press Esc")
     - **Source**: where the case comes from, and it must never be blank —
       `file:line` when generated from a diff, or the acceptance-criterion it covers
       (e.g. `AC #2`) on the AC-only path. A row you cannot source is a row you invented;
       cut it
     - **Results**: always starts as "Not Run"
     - **Tested Version**: the build version captured in step 5b's audit, or
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

For a refreshed suite on the Path C-changed route, say so in the question — "Post a
refreshed suite on <ticket>? The PR changed from #12 to #18 since the last one" — so the
user knows they are approving a second comment, not a first.

---

### 10. Post the comment

`clickup_create_comment` on the ticket. The comment **must start with exactly**:

```
QA test cases
```

then the matrix. Nothing before that header — no greeting, no preamble.

**That header is load-bearing.** Step 5a detects prior coverage by looking for a comment
starting with `QA test cases`, so a suite posted under any other opening line is invisible
to the next run and the ticket gets a duplicate suite tomorrow. Never reword it.

On the Path C-changed route, add one line directly under the header naming the PR the
earlier suite was built from, so the two comments can be told apart:
`Supersedes the suite posted for PR #12 — regenerated for PR #18.`

---

### 11. Summarize

Scanned N tickets (window X) → N standard / N feature · N passed · N bounced (with links) ·
N unsure · test cases posted to N tickets · N already covered (skipped) ·
N newly tagged `reached-testing`.

## Important
- Ask the window FIRST, act LAST — no ClickUp write before the user has seen the verdict
  table.
- Only touch tickets in `testing`. Never change tickets in other statuses.
- Never edit the ticket description itself — that's the developer's job.
- **Test-case generation is automatic, but once per ticket.** For any feature ticket
  reaching Path B, generate without being asked and without asking which tickets to cover —
  the only thing gated on the user is posting. But a ticket that already has its suite is
  skipped at 5a, so re-running this skill daily costs nothing and posts nothing.
- **Check for an existing suite BEFORE generating, not before posting.** The order matters:
  checking late means the diff is read and the matrix drafted every single day for a ticket
  that has been covered for weeks, and the user is asked about it every time. Checking at 5a
  makes it a genuine skip.
- **The `QA test cases` comment is the only record of coverage.** Never introduce a local
  state file, cache or ticket list to track what's been posted — a file on one machine is
  invisible to the other QA engineer running the same skill, so they would re-post
  everything. ClickUp is the shared state; keep it that way.
- **Never generate test cases for a bounced ticket** — a bounced feature ticket had neither
  AC nor PR, so there is no trustworthy source material to generate from. Bouncing does not
  block it forever: it has no `QA test cases` comment, so once the developer adds the AC or
  the PR it becomes eligible on a later run.
- **AC or PR, never both required.** A feature ticket with one of the two is eligible. Test
  environment, build details and sprint tag are warnings only and must never trigger a
  bounce on the feature path.
- **Never post a second `QA test cases` comment silently.** A refreshed suite is posted only
  when the PR link has changed since the original AND the user approved it, and it must say
  it supersedes the earlier comment.
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
- **Increment `bounced-<N>` only on a real bounce.** The "⏳ Already warned, still
  incomplete" path does not comment or change status, so it must not add a tag
  either — the ticket has not bounced again, it simply has not been fixed. Adding
  one there would inflate every reopen count by one per daily run, which is worse
  than having no count at all. A reminder comment the user approves is also not a
  bounce and gets no tag.
- **`reached-testing` and `bounced-<N>` are different kinds of tag — don't merge
  them.** `reached-testing` records a fact (this ticket was in `testing`): added
  once, never removed, added to every scanned ticket. `bounced-<N>` counts events
  and only ever increments on a real bounce. Adding `reached-testing` more than
  once, or only to passing tickets, breaks the release report's skipped-Testing
  check in a way that looks like clean data.
- **What the `reached-testing` tag doesn't measure.** It marks tickets THIS skill
  scanned. A ticket that entered `testing` and left again between two runs is
  never marked, so /qa-release-report's skipped-Testing list is a ceiling — a
  list of tickets to ask about, not proven QA misses. Running this skill daily is
  what keeps that list honest; the real fix is still the `Total time in Status`
  ClickApp on Business.
- **What the bounce tags do and don't measure.** They count bounces made by THIS
  skill. If a developer or QA drags a ticket from `testing` back to `in progress`
  by hand in the ClickUp UI, nothing records it. So the count is a floor, not a
  total, and /qa-sprint-report must label it that way rather than presenting it as
  a complete reopen count. This is a Free-plan limitation, not a design choice:
  the real fix is the `Total time in Status` ClickApp on Business, which reads
  actual status history including manual moves.
- Connector quirk: assign users by NUMERIC user ID (e.g. Pranav 228106678,
  Shekhar 228119573 — or via `clickup_get_workspace_members`); email/username
  assignment fails silently.
