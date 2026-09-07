---
description: Turn raw notes, requests or chat messages into a proper agile user story ticket in ClickUp — user story, description, acceptance criteria, out of scope, priority, feature and sprint tags. Asks the user about anything missing instead of assuming it, checks for duplicates, refuses to file bugs as stories, and offers to split a story that is too big. Always shows the draft in chat and files nothing until you confirm. Triggers on "/story-ticket", "make this a story", "convert this into a story ticket", "write a user story for this".
---

# Story Ticket

Turn raw data into one agile user story a developer can pick up.

**The one rule that matters:** this skill NEVER writes to ClickUp without an explicit
`yes` in this conversation. It drafts, it shows, it waits. No confirmation = no ticket.

**The second rule:** ask, don't assume. Anything missing from the raw data that cannot
be looked up gets asked — in one message, with suggested answers. Nothing in a filed
story is invented.

**Raw data:** $ARGUMENTS — anything. A one-line request, a pasted chat message, a
meeting note, five bullet points.

Nothing about the board is hardcoded here. Read the real lists, tags and priorities
from ClickUp before building any payload.

---

## Step 1 — Read the raw data

Pull out whatever is actually there:

- **Who** wants it (the user type)
- **What** they want
- **Why** — the benefit
- **Feature area** it touches
- **Priority** signals ("urgent", "nice to have", "blocking the demo")

Multiple unrelated requests in one paste → treat each as its own story and draft
them numbered 1..N in one message.

## Step 2 — Is this actually a story?

Decide before drafting. Read the raw data against the repo when it helps
(`AGENTS.md` → `README` → the code).

| Raw data describes | Verdict | Action |
|---|---|---|
| New behaviour that does not exist yet | **Story** | Continue to step 3 |
| Existing behaviour that is broken or contradicts docs | **Bug** | Stop. Say so, offer `/qa-bug-report` |
| A small change to behaviour that already works | **Enhancement** | Continue, but label it in the draft context line |
| A question, or too vague to be work | **Neither** | Stop and ask what the desired outcome is |

Say the verdict out loud before the draft. Never file a bug as a story — a bug
filed as a story loses its repro steps and skips the bug workflow entirely.

## Step 3 — Anything missing, ask the user

**Never fill a gap with an assumption.** Raw data is almost always incomplete. Work
through this checklist and ask about every item you cannot answer.

| Needed | Where to get it | If still missing |
|---|---|---|
| User type ("As a ...") | The raw data | **Ask** |
| What they want | The raw data | **Ask** |
| Benefit ("So that ...") | The raw data | **Ask** |
| Feature area | Raw data, or the repo | **Ask** |
| Acceptance criteria | Written from the above | **Ask** — see step 8 |
| Out of scope | The raw data | **Ask** |
| Priority | Words like "urgent", "blocking" | **Ask** |
| Sprint number | Tags on recent tickets | **Ask** |
| Destination list | The board | **Ask** |

**Look it up first.** Anything readable from the repo or from ClickUp is not a
question — read it. Only genuinely unknowable things get asked.

**How to ask:**

1. **One message, all of it.** Never drip-feed questions across turns.
2. **Numbered**, so the answers can come back numbered.
3. **Each question carries your suggested answer**, so a reply of `all ok` is enough:

> A few things missing before I draft this:
>
> **1. Who is this for?** — suggest: *TaskPulse user*
> **2. Why do they want it?** — suggest: *so the view survives a refresh*
> **3. Priority?** — suggest: *Medium*
> **4. Sprint?** — `sprint-12` is the one in use, use that?
> **5. Which list?** — 1) Backlog  2) Sprint Board  3) Ideas
>
> Reply with the numbers, or `all ok` to take every suggestion.

4. **Never re-ask** something already answered in this conversation.
5. **Answers you get are used verbatim** — do not improve on them.

**If the user skips a question** or says "just fill it in": write
`Needs input: <what is missing>` in that section of the draft. Never invent content
to fill it, and never quietly drop the section. A visible gap gets fixed; an invented
line gets shipped.

## Step 4 — Check for duplicates

Before drafting, search the board for the same story. Search by the 2–3 strongest
keywords from the raw data (`clickup_search`, or `clickup_filter_tasks` on the
candidate lists). Search open AND closed tickets.

- **Close match found** → show it with its ID, status and link, then ask:
  *"This looks like the same thing. Add to that ticket, file a new one, or drop it?"*
  Wait for the answer before anything else.
- **Loose match found** → mention it as a note in the draft, keep going.
- **Nothing** → say `No duplicates found` in the context line, keep going.

Never skip this. A silent duplicate costs someone a whole sprint item.

## Step 5 — Too big? Suggest a split

A story is too big when any of these is true:

- More than **6** acceptance criteria are genuinely needed
- It has **two unrelated benefits** — two different "so that" clauses
- It spans two feature areas that ship independently

When it is too big, do NOT file it. Show the proposed split instead:

> ⚠️ This is two stories, not one. I'd split it:
> **1.** Save the selected filter — *so the choice is remembered*
> **2.** Add a Clear filters button — *so the view can be reset in one click*
> File both, just one, or keep it as a single story?

Wait for the choice. If the user says keep it as one, file it as one — their call.

## Step 6 — Pick the tags

Two tags, and they must match the board's real conventions or the other QA skills
will not see this ticket.

**Feature tag — the bare tag `feature`.** Every story gets it. This is the work-type
marker `/qa-ticket-check` and `/qa-sprint-report` split on. Do NOT invent
`feature:<name>` style tags — the feature area belongs in the title prefix instead.

**Sprint tag — `sprint-<N>`.** Find the current sprint by reading the tags already on
recently-updated tickets. Match loosely (`sprint 1`, `Sprint-1`, `sprint_1` all count)
but write new tags in the canonical `sprint-<N>` form.

- One sprint clearly in use → use it
- More than one open → ask which
- None found → ask for the sprint number, or file with `feature` only and say so

Any tag that does not already exist on the board → say so in the draft and get
approval before creating it.

## Step 7 — Pick the destination

List the candidate lists **by name, never by ID** — let the user pick a number.
Only one list? Use it. Remember the choice for the rest of the conversation so a
batch of stories is not asked five times.

Read that list's real statuses and priorities before building the payload. Watch for
required custom fields.

## Step 8 — Draft the story

**Title:** `[Area] Short action-based title` — states the outcome, not the task.

```
## User Story
As a <type of user>
I want <what they want>
So that <the benefit>

## Description
<2-4 lines of plain context: what happens today, what should change>

## Acceptance Criteria
- [ ] <condition>
- [ ] <condition>
- [ ] <condition>

## Out of Scope
- <what this story deliberately does not cover>

## Priority
<High | Medium | Low>

## Original Request
> <the raw data, verbatim>
```

### Acceptance criteria rules

Always written. Never empty, never a placeholder.

| Raw data has | Do this |
|---|---|
| Clear conditions already | Use them, cleaned up |
| Only a request | Write them from the request |
| Nothing testable in it | **Ask** what "done" looks like — never guess |

Each criterion must be:

- **Checkable** — a person can test it and say pass or fail
- **One thing per line** — no "and also" bundles
- **Plain language** — no code, no field names, no jargon
- **3 to 6 lines total** — fewer means under-thought, more means step 5 applies
- **Covering the unhappy path** — empty input, missing data, corrupt stored value

```
BAD                                 GOOD
- [ ] Filter works                  - [ ] Selecting a filter saves it
- [ ] Should be saved properly      - [ ] Refreshing restores the last filter
                                    - [ ] First-time users see All by default
                                    - [ ] A corrupt saved value falls back to All
```

Cannot write a testable condition for part of the request? Put a note in the draft
rather than a vague line:

> ⚠️ Couldn't write a testable condition for "make it faster" — how fast is acceptable?

### Other section rules

- **Out of Scope** — 1–3 lines. Nothing genuinely excluded? Write `Nothing excluded`
  rather than deleting the section.
- **Original Request** — the raw data verbatim, in a quote block. Never reworded,
  never trimmed. This is the record of what was actually asked.
- **Description** — what exists today, then what should change. No implementation
  design, no file names.

## Step 9 — Show the draft and stop

Print one line of context first, so a wrong read is obvious at a glance:

> _Story · no duplicates found · `feature`, `sprint-12` · → TaskPulse › Backlog_

Then the full draft under a clear "not filed yet" heading, then:

> Reply **yes** to file this, or tell me what to change.

**Stop here.** Do not call any ClickUp write tool.

Handle the reply:

| Reply | Action |
|---|---|
| `yes` / `file it` | Create it (step 10) |
| A change | Redraft, show again, ask again |
| `no` / silence | Nothing filed. Say so plainly and stop |
| `yes to 1, 3` (batch) | File only those, leave the rest as drafts |

A `yes` covers only the drafts on screen right now. It never carries forward to a
later story.

## Step 10 — File it as `to do`

1. Create the task in the chosen list with the title and the drafted body
2. **Status: the list's first / not-started status** — normally `to do`. Read the
   list's real statuses and use its opening one. Never file into `in review`,
   `testing` or anything further along
3. Apply `feature` and the sprint tag
4. Set the priority
5. Report the result:

> ✅ Filed: **CU-86d4abc12** — [Filters] Remember the selected filter after refresh
> https://app.clickup.com/t/86d4abc12
> Status: `to do` · Tags: `feature`, `sprint-12`

**Creation fails** (no permission, required custom field, tag rejected) → do not
retry blindly. Show the markdown so nothing is lost, and say exactly what blocked it.

**Partial success** — task created but a tag failed → say which tag is missing and
that the ticket is invisible to sprint reports until it is added.

## Where this skill stops

Filing the story is the end. This skill does not run any QA step and does not offer to.

A brand-new story is in `to do` — nothing is built yet, so there is nothing to test
and the acceptance criteria have not been reviewed by anyone. Test cases belong later,
when the ticket reaches `testing`, and `/qa-ticket-check` already generates them there
(once per ticket, after approval). Generating them here would duplicate that work and
produce cases against unreviewed criteria.

Do not call `/qa-test-cases`, `/qa-ticket-check` or any other QA skill from here, even
if the user's raw data mentions testing.

---

## Limits

- Asks rather than assumes. Every gap is either looked up, asked about, or shown as
  `Needs input` in the draft — never filled with invented content
- Reads code to classify story vs bug; it does not run anything
- Writes what was asked for, not what it thinks would be better — extra ideas go in
  the context line, not into the acceptance criteria
- Estimates nothing. Story points and assignees are planning decisions, left to the
  team
- Files new stories as `to do` and stops there. It never advances a status, and never
  touches an existing ticket's status — status flow is automated in ClickUp
- Generates no test cases. That happens at `testing`, via `/qa-ticket-check`
