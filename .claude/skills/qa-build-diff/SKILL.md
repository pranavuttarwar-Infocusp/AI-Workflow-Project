---
description: Summarize what changed between two builds, branches, tags or commits in any git repository, what QA needs to test, and where the risk is. Derives the areas from the repo itself, rates risk per area with stated evidence, flags migrations, feature flags, breaking contracts and new permissions, and ends with a prioritized P0/P1/P2 test plan. Triggers on "/qa-build-diff", "what changed between these builds", "build diff", "what do I need to test in this build", "risk areas in this release".
---

# QA Build Diff Analysis

Understand a build before testing it: what changed, what to test, where it can hurt.

**Rule:** nothing about the project is hardcoded here — not the areas, not the
branch names, not the stack. Derive all of it from the repo. Never assume a
filename, framework or default branch.

**Written for QA.** Say what a tester needs to DO. Implementation detail only
where it explains a risk.

**A tracker is optional.** Default output is markdown the user can paste anywhere.
If a tracker is connected, look ticket IDs up for context — but this skill is
**read-only**: never create, update, comment on, or move a ticket from here.

**User's input:** $ARGUMENTS — may be two refs, one ref, a commit range, a PR, or
nothing. Only a git repo is required.

## Step 1 — Resolve the range, and prove it

Everything below is wrong if the range is wrong. Print it, then continue.

| They gave | Range |
|---|---|
| two refs (`release/1.2 develop`) | `<old>..<new>` |
| one ref | `<default-branch>..<ref>` |
| a commit range (`abc123..def456`) | use as given |
| `A...B` (three dots) | keep it — diff against the merge base |
| a PR / MR number | `gh pr view <n>` for head and base. GitHub-only — on GitLab, Bitbucket or no `gh` installed, say so and ask for the two refs instead |
| "latest" / nothing | last 20 commits on the current branch |

Resolve the **real** default branch — `git symbolic-ref refs/remotes/origin/HEAD`,
else whichever of `main`, `master`, `develop`, `develop_*` exists. Never assume.

Verify before trusting:
- `git rev-parse --verify <ref>^{commit}` on both ends — a typo must fail loudly
- `git merge-base --is-ancestor <old> <new>` — false means divergent or backwards;
  say which, don't silently swap
- `git rev-parse --is-shallow-repository` — shallow means history may be missing;
  say so rather than reporting a partial diff as complete
- `git log -1 --format='%h %ad %s' --date=short` each end, for the header

**Stop and ask if:** not a git repo · a ref doesn't resolve · the refs are
divergent and you need `..` vs `...`.

**Ask but continue if:** one ref given (confirm the base) · monorepo with several
apps (confirm which, default all) · no tracker connected but commits cite ticket
IDs (say you'll print raw IDs).

Max 4 questions, one message, defaults everywhere. Never re-ask.

## Step 2 — Derive the areas from THIS repo

Do not reuse another project's category list. Build it from evidence:

1. `AGENTS.md` / `CLAUDE.md` — if it names modules or domains, that is ground truth
2. Top-level source directories, and modules or workspaces from whichever manifest
   the repo actually has — `package.json`, `pyproject.toml`, `requirements.txt`,
   `go.work`/`go.mod`, `pom.xml`, `build.gradle`, `Cargo.toml`, `Gemfile`,
   `*.csproj`, `Package.swift`, `pubspec.yaml`. This list is not exhaustive; read
   what's there
3. Feature or route folder names
4. `README` architecture section

Then map every changed file into an area. Anything that doesn't fit goes in
**Other** — never force a file into a category to make the table look tidy.

Fall back to this spine only when the repo gives you nothing better:

> UI/Presentation · API/Network · Business Logic · Data/Persistence ·
> Auth/Permissions · Infrastructure/Config · Build/CI · Tests · Docs

Skip `node_modules`, `vendor`, `dist`, `build`, `.venv`, lockfiles, generated and
minified output. Never read `.env` or put credentials in the report.

## Step 3 — Gather the evidence

1. `git diff --name-status <range>` — what changed, and how (A/M/D/R)
2. `git diff --stat <range>` — churn per file
3. `git log --oneline <range>` — commits, dates, ticket IDs
4. **Read the diff** for the areas you're about to rate — `git diff <range> -- <paths>`

A changed file is not a behaviour change. Read the hunks and decide whether a user
or a caller can observe a difference. A renamed local variable cannot.

## Step 4 — Rate risk with evidence, not vibes

Give every area **High / Medium / Low** and state which of these drove it. A rating
with no evidence line is not allowed.

| Signal | How to get it |
|---|---|
| **Churn** | lines and files changed, from `--stat` |
| **Criticality** | does it sit on a path whose failure is unrecoverable — auth, payments, data writes, migrations, device or session state |
| **Blast radius** | how many other modules import or call it |
| **Test coverage** | do tests exist for these paths, and did the diff touch them |
| **Bug history** | `git log --oneline -i --grep='fix\|bug\|revert\|hotfix\|patch' -- <paths>` — repeat fixes mean a fragile area. Not every repo writes conventional commits; if this returns nothing, check the log by eye before concluding the area is clean, and say which you did |

Rough guide: **High** = critical path, or wide blast radius with no tests.
**Medium** = real behaviour change, contained, some coverage. **Low** = cosmetic,
additive behind a flag, or fully covered by tests.

## Step 5 — Flag the concerns

Check every one of these against the diff. Mark it `None found` rather than
omitting it — silence should not look like absence.

- **Schema / migrations** — DB migrations, stored-data shape changes, cache or
  local-storage key changes. Is there a rollback? What happens to existing data?
- **Feature flags / config** — flags added, removed, or default flipped. What is
  the state under test?
- **Breaking contracts** — changed public signatures, endpoints, response shapes,
  removed fields, event or message formats
- **Permissions / entitlements / scopes** — anything new the user must grant
- **Dependencies** — added, removed, or major-version bumped
- **Auth and secrets handling** — token, session or credential logic
- **Destructive operations** — delete, purge, overwrite, bulk update
- **Critical paths for this repo** — identify them from the code, then say whether
  the diff touched them

## Step 6 — Output

Open with one line of what you resolved, so a wrong range is obvious:

> _`release/1.2` (Aug 01) → `develop` (Aug 13) · 47 commits · 61 files · 5 areas ·
> Flask + Postgres · tests in `tests/` · no tracker connected_

Then:

```
# Build Diff — <repo name>

Range: <old-ref> (<date>) → <new-ref> (<date>)
Commits: <n>   Files changed: <n>
Areas affected: <list>
Stack: <detected>
Generated: <timestamp>

## Changes by Area

### <Area>  ·  Risk: High | Medium | Low
**What changed:** <plain summary a tester can act on>
**Why that risk:** <the evidence from Step 4 — churn, coverage, blast radius, history>
**Key files:** <file:line, the few that matter — not the whole list>
**What to test:**
- <concrete scenario, reachable from a state a tester can get to>
- <concrete scenario>
**Tickets:** <ID · title · status | raw ID | none>

## Concerns
- **Schema / migrations:** <finding | None found>
- **Feature flags / config:** <finding | None found>
- **Breaking contracts:** <finding | None found>
- **Permissions:** <finding | None found>
- **Dependencies:** <finding | None found>
- **Auth / secrets:** <finding | None found>
- **Destructive operations:** <finding | None found>
- **Critical paths touched:** <finding | None found>

## Priority Test Plan

### P0 — Must test (blocking)
- [ ] <item>  — <the area it covers>

### P1 — Should test (high risk)
- [ ] <item>

### P2 — Nice to test (low risk)
- [ ] <item>

### Regression areas
- [ ] <area not directly changed but downstream of something that was, and why>

## Not worth testing
- <changed area with no observable behaviour change, and why it's safe to skip>

## Summary
- Highest-risk area: <area> — <one line>
- Areas with no test coverage: <list>
- Untouched areas (skip): <list>
- Blocking concerns before sign-off: <list, or "none">
```

**Every P0 must trace to a High-risk area or a concern.** A P0 that maps to nothing
above it is invented — cut it. Keep P0 short enough to run in one sitting; if it
runs long, say what got deferred rather than trimming silently.

**Tickets — only if a tracker is connected.** Pull IDs from commit messages, look
them up, append `ID · title · status`. **Read-only: never create, update, comment
on, or move a ticket from this skill.** No tracker → print the raw ID from the
commit message, or omit the field.

Show the report in chat. Only write a file or post it if asked — and never create or
change a ticket, even if asked. Filing belongs to a bug-report skill, not here.

## Step 7 — Check yourself

Re-read the output once and fix:

- The range in the header is the one that was asked for
- Every area has a risk rating **and** an evidence line
- Every `What to test` item is a scenario, not "verify it works"
- Every P0 traces to a High area or a flagged concern
- All eight concerns are answered, `None found` included
- Areas whose diff changes nothing observable are in **Not worth testing**, not
  padding the test plan

## Limits

- Say what you couldn't find: *"No tests in this repo, so coverage did not feed any
  risk rating — ratings rest on churn and criticality only"*
- You read the diff, you don't run the build. Risk is a prediction; a clean report
  is not a passing build
- A diff can't tell you intent. If a change looks like an accidental regression
  rather than a feature, say so and let a human decide
- Areas the range doesn't touch can still break. Regression areas are reasoned from
  imports and call sites, not measured — treat them as leads
