---
description: Generate essential test cases from any git repository, in any language or stack. Reads the repo to work out what the app is, scopes to the branch diff or a named feature, and produces a short ranked suite covering edge, negative, network, UI and regression. Triggers on "/qa-test-cases", "generate test cases", "write test cases for this change", "QA cases for this branch".
---

# Test Case Generator

Write a short, high-value test suite for whatever repo you are in.

**Rule:** nothing about the project is hardcoded here. Look it up in the repo.
Never assume a filename, framework or stack.

**User's input:** $ARGUMENTS — may be empty, or may name a feature, path, branch,
commit range, ticket or PR. Only the repo is required; anything else is a bonus.

## Step 1 — Check before you start

Look first. Only ask about what you genuinely cannot find yourself.

**Stop and ask if:**
- No source code here → ask for the repo path
- No way to scope (not a git repo, or on the default branch with nothing changed
  and no feature named) → ask what to test
- Several apps in subfolders and no path given → ask which app

**Ask but continue anyway if:**
- No README → "What does this app do, in one line?" (skippable)
- No tests found → "No automated tests, correct?" (assume none)
- Base branch or stack uncertain → confirm your guess
- Test environment unclear → "Browser, mobile, API or CLI?"

Max 4 questions, all in one message, each with a default. Never re-ask something
already answered. If they skip everything, still produce the suite and say what it
was based on.

## Step 2 — Pick what to test

First one that applies. Say which you used.

1. What the user named
2. Diff vs the default branch — `git diff --name-only <base>...HEAD`
3. Uncommitted changes — `git status --porcelain`
4. Last 10 commits — `git log --oneline -10`
5. Ask

Resolve the real base branch (`main`, `master`, `develop`) instead of assuming. On
a shallow clone there is no history — say so and read code instead.

## Step 3 — Learn the project

Cheapest first. Stop when you know enough.

1. `AGENTS.md` / `CLAUDE.md` — if present, this is ground truth
2. `README` — what it does, and what it promises
3. Manifest (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Gemfile`,
   `*.csproj`, `Package.swift`) — stack and test runner
4. Entry points, routes, screens, handlers, models in the scoped paths
5. Existing tests — their style, and what they already cover
6. **The code itself — always available, so this always works**
7. `git log -10 -- <scoped paths>` — recent changes mark risk

Ignore third-party and build folders (`node_modules`, `vendor`, `dist`, `build`,
`.venv`). Never read `.env` or put credentials in the output.

## Step 4 — Cover these 12 things

For each one: write cases, or write `N/A — <reason>`. Never skip one silently.
Most give 0–2 cases. That is fine.

1. **Happy path** — the intended behaviour
2. **Boundary** — zero, one, many, max, empty, very long
3. **Negative** — bad input, wrong type, missing field
4. **Error handling** — what happens when it fails
5. **Persistence** — survives restart; corrupt or missing stored data
6. **Network** — offline, timeout, 500, slow, retry
7. **UI** — smallest viewport, long text, appearance modes, empty states
8. **Interaction** — keyboard, focus, double-click, back button
9. **Auth** — not logged in, wrong role, expired session
10. **Regression** — what this change might have broken
11. **Concurrency** — two at once, double submit, partial failure
12. **Accessibility** — labels, alt text, keyboard-only

Read each one against this repo. "Persistence" is localStorage in one project and
Postgres in another. "Restart" is a page refresh in one and a service restart in
another. No network calls in the app? Category 6 is `N/A` — do not invent it.

**1, 2, 3, 4 and 10 always apply**, whatever the project is. They keep the output
useful for firmware, data pipelines and infra repos too.

## Step 5 — Keep only what matters

A case earns a row only if all four are true:

1. It touches what changed, or something just downstream of it
2. Failing it is a bug someone would actually report
3. An existing automated test doesn't already cover it
4. It isn't a variant of another row — **one risky boundary, not six**

How many: 6–10 for a small change, 12–20 for a branch diff, 20–30 for a whole
feature. Never more than 30 in one pass — cover the riskiest area, then say what's
left ("Covered checkout. Remaining: cart, profile"). Never cut silently.

Split into **Must test** (8–12) and **Should test** (4–8). Neither? Drop it.

## Step 6 — Output

Start with one line of what you assumed, so a wrong guess is obvious:

> _Scope: 6 files vs `main` on `feat/search-filters` · Flask + Postgres · tests in
> `tests/` · read README + code_

Then:

```
## Test Suite: <name>

### Prerequisites
- <environment and starting state the tester needs>

### Must Test

| Sr.No. | Area | Category | Scenario | Description | Steps | Expected Result | Source | Comments/Ticket/Notes | Results | Tested Version |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ... | Happy Path | ... | ... | ... | ... | routes.py:88 | ... | Not Run | ... |

### Should Test
(same columns)

### Coverage
| Category | Cases | Note |
|---|---|---|
| Happy path | 3 | |
| Auth | 0 | N/A — no login in this app |

### Risk Areas
- <area>: <why — recent churn, complex logic, no tests>

### Regression Concerns
- <what this change might have broken>

### Coverage Gaps
- <what existing tests cover vs what is new and untested>

### Also worth a look
- <3–5 one-liners that don't need a full row>
```

Columns:
- **Category** — one of the 12 above
- **Steps** — numbered and concrete. Never "verify it works"
- **Source** — the `file:line` behind this case. **Required.** No source line means
  you probably invented it — cut it
- **Results** — starts `Not Run`; the tester fills Pass/Fail
- **Tested Version** — commit, branch or PR under test

Show it in chat. Only write a file or create tickets if asked.

## Step 7 — Check yourself

Re-read your output once and fix:

- Every row has a real `file:line`
- All 12 categories are either filled in or marked `N/A` with a reason
- Each `N/A` — was that actually right?
- No two rows testing the same idea with different numbers
- Nothing already covered by an existing test

## Limits

- Say what you couldn't find: *"No README or tests found — derived from code only,
  please sanity-check the assumptions"*
- You test what the code **does**, against what the docs **say**. A rule that only
  exists in someone's head can't be checked — flag anything that looks like an
  unwritten rule instead of assuming current behaviour is correct
