---
description: Turn a rough bug description into a proper bug report for any project — prerequisites, repro steps, expected vs actual, environment details. Classifies bug vs enhancement first by checking the code and docs. Works with no tracker at all (renders markdown to copy); files the ticket only if a tracker is connected and you confirm. Triggers on "/qa-bug-report", "file a bug", "write up this bug", "raise a ticket for this issue".
---

# Bug Report

Turn a rough description into a report a developer can act on.

**Rule:** nothing about the project is hardcoded here. Look it up in the repo.
Never assume a filename, framework or stack.

**A tracker is optional.** Default output is markdown the user can paste anywhere.
File a ticket only if a tracker is connected and the user confirms.

**User's description:** $ARGUMENTS — e.g. "theme toggle resets to dark after
refresh even though I picked light".

## Step 0 — One look, then decide what to skip

Run this once. Do not use separate commands to discover these facts.

```bash
ls -A && git rev-parse --abbrev-ref HEAD 2>/dev/null && git log --oneline -5 2>/dev/null
```

The output tells you what exists. Apply these skips — they save most of the work:

| Not there | Skip |
|---|---|
| No `README`, no `AGENTS.md`/`CLAUDE.md`, no docs folder | Step 2's doc ladder → classify from code, mark unverified |
| No git | Step 3's history check |
| No test folder | the "should a test have caught this" check |
| No tracker tool available | Step 5 modes 2 and 3 → markdown only, never mention ticketing |

**Read budget: at most 8 files.** Read only the sections that matter, never a
whole large file. Never read the same file twice. Skip `node_modules`, `vendor`,
`dist`, `build`, `.venv`. Never read `.env` or put credentials in the report.

## Step 1 — Fill the gaps

From the description, pull out: what happened, what should have happened, feature
area, likely priority, any environment details given.

**Stop and ask if:**
- Too vague to reproduce → ask what they did, step by step
- You cannot tell what "should have happened" → ask what they expected

**Ask but continue anyway if:**
- Environment unknown → "Which browser / device / OS?" (else `Not provided`)
- Feature area or severity unclear → propose your guess to confirm

Max 4 questions, one message, defaults where possible. Never re-ask.

## Step 2 — Bug or enhancement? Decide before drafting

- **Bug** — contradicts documented or clearly intended behaviour
- **Enhancement** — a net-new ask that was never specified

Check the expectation against the first of these that exists:
`AGENTS.md`/`CLAUDE.md` → `README` → docs folder → existing tests → the code.

- **Contradicts documented behaviour** → Bug. Cite what it violates.
- **Nothing documented backs it** → stop and say: *"This reads as an enhancement —
  I couldn't find documented behaviour it violates. File as enhancement, or dig
  deeper?"*
- **No documentation exists at all** → *"No documented expected behaviour found.
  Classified from code alone — please confirm."*

Never silently file a bug for something with no documented behaviour behind it.

## Step 3 — Confirm it in the code

1. Find the feature's code — handlers, components, routes
2. Read only the part that produces the reported behaviour
3. `git log -5 -- <those paths>` — recent changes are the likely cause
4. Is there a test that should have caught this?

Cite the `file:line` you believe is responsible. Can't find it? Say so rather than
guessing a cause.

## Step 4 — Draft the report

**Title:** `[Area] Short descriptive title`

```
## Prerequisites
- <starting state needed to reproduce>

## Repro Steps
1. <step>
2. <step>

## Actual Result
<what happens>

## Expected Result
<what should happen, and what says so — README, doc, test or ticket>

## Environment Details
- Platform / browser / device: <or "Not provided">
- OS + version: <or "Not provided">
- Screen size: <only for visual or responsive issues>
- Build / commit: <current commit if known>

## Attachment
<Leave blank — the reporter attaches screenshots, recordings or logs>

## Test Plan Link
<Link to the relevant test case if one exists — otherwise omit>

## Note for Developer
<Suspected cause with file:line, related code, workaround — otherwise omit>
```

- **Repro steps concrete.** "Click Add with an empty title" — not "try adding a task".
- **Expected Result names its source.** Nothing documents it? Say "undocumented —
  assumed from code".
- **Environment fields adapt.** A CLI has no browser; an API has no screen size.
- **Omit `Test Plan Link` and `Note for Developer` entirely** when empty. No
  placeholder text.

## Step 5 — Deliver it

Print one line of context first, so a wrong guess is obvious:

> _Bug · violates README "theme choice persists" · likely cause `app.js:212`,
> changed 3 days ago_

**No tracker tool available** — show the markdown, done. Never mention ticketing.

**Tracker available:**
1. Search for duplicates by keyword. Found some? List them and ask first.
2. Pick the destination **by name, never an ID** — list options, let the user
   choose a number. Only one? Use it.
3. Read that destination's real fields, statuses and priorities before building the
   payload. Watch for required custom fields.
4. Show the draft and **ask for confirmation.**
5. Only then create it, tagged to match the Step 2 verdict.

**Creation fails** (no permission, missing field) — fall back to markdown and say
what blocked it.

Never create a ticket without explicit confirmation in this conversation.

## Limits

- Say what you couldn't find: *"No README or tests — expected behaviour inferred
  from code only, confirm before filing"*
- You compare what the code **does** against what the docs **say**. If the
  expectation looks like an unwritten rule, flag it for a human decision rather
  than filing it as a defect
- You read code, you don't run it. A suspected cause is a lead, not a diagnosis
