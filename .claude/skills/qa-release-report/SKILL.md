---
description: Release go/no-go report — what is shipping, whether it is safe to ship, and the raw commit log behind it. Cross-checks the ClickUp board against git so a ticket closed with nothing merged is caught. Supports release candidates in any spelling (rc-2, RC_2, release_candidate_01, release-candidate-2) when the repo uses them, and falls back to tags, a marker file or the sprint window when it does not. Renders in chat only. Triggers on "/qa-release-report", "release report", "release notes", "is this safe to ship", "go no-go", "what is in this release", "RC report".
---

# QA Release Report

The go/no-go report you run just before shipping. The daily report says what
moved today; the sprint report says how good the sprint's work was; this one
says **what is actually going out and whether it is safe to send.**

It is the only QA skill that reads the board and the code together, so it is
the only one that catches a ticket marked `done` with nothing merged behind it.

**Optional user input:** $ARGUMENTS — see *Arguments* below. Default = resolve
the range automatically.

## Arguments

Parsed in this order, first match wins. This ordering is what makes an
ambiguous argument predictable — resolve it the same way every run:

| Test on $ARGUMENTS | Meaning | Example |
|---|---|---|
| contains `..` | explicit range, used verbatim | `rc-1..rc-3`, `v1.0..v1.1`, `d09cd07..HEAD` |
| matches the RC pattern (see *Release candidates*) | release candidate N | `RC2`, `rc-2`, `release_candidate_01` |
| starts with `sprint` | sprint tag scope | `sprint 2` |
| starts with `--` | flag (see below) | `--strict` |
| anything else | feature keyword scope | `search-filter` |

Flags, combinable with any of the above:

- `--full-log` — print every commit, ignoring the 40-commit cap in step 3
- `--strict` — soft warnings become blockers (see *Verdict rules*)

`/qa-release-report RC2 --strict` is a valid combination: RC2's range, strict
verdict.

## Configuration

- **Space:** `AI Workflow Project` (space_id `90167656011`)
- **Repo:** the project repo in the working directory. All git reads are local
  and cost no ClickUp API calls.
- **Destination: CHAT ONLY.** This report is rendered in the conversation and
  nowhere else. Do NOT create a ClickUp doc, do NOT create or update a doc page,
  do NOT post a comment — no `clickup_create_document`,
  `clickup_create_document_page` or `clickup_update_document_page` for this
  skill. If the user later wants it persisted they will say so and name the
  destination; never infer one, and never fall back to the daily report's doc.
- **Sprint tags** are matched the same loose way as the other QA skills: any tag
  matching `sprint[ -]?<N>` case-insensitively is sprint N. Never match the
  exact literal — the board uses a space (`sprint 2`) and a hyphen must match
  too, or the report silently scopes to nothing.
- Report timezone: user's local (Asia/Kolkata)

## Range resolution

The range is the single most important thing this report gets right — every
count downstream depends on it. Walk this chain top to bottom and **stop at the
first rung that resolves**. Always print which rung was used in the report
header, so a wrong guess is visible rather than silent.

1. **Explicit range in $ARGUMENTS** (`a..b`) — use verbatim, no validation
   beyond `git rev-parse` succeeding on both ends.
2. **Named release candidate** (`RC2`) — resolve per *Release candidates* below.
3. **RC refs present in the repo** — no RC named, but the repo has them:
   use `<previous RC>..<latest RC>`.
4. **Release tags exist** — `git tag` is non-empty and no RC refs matched: use
   `<latest tag>..HEAD`, latest by version sort (`git tag --sort=-v:refname`).
5. **`.claude/last-release` marker file exists** — read the SHA it contains and
   use `<sha>..HEAD`. Ignore blank lines and `#` comments.
6. **Nothing found** — fall back to the sprint window: resolve the current
   sprint tag (highest N on the board) and use
   `git log --since="<sprint start date> 00:00"`. **This rung is approximate and
   must be labelled as such in the header** — commits merged on the day a sprint
   flipped can land on the wrong side. If the sprint start date is unknown, use
   the last 14 days and say so plainly rather than inventing a date.

Rungs 2 and 3 fire only when RC refs actually exist. **On a repo with no RCs the
report must never mention release candidates at all** — no warning, no "no RCs
found" line. The RC path is invisible on repos that do not use it. TaskPulse has
no RC refs and no tags today, so it lands on rung 6; that is the normal case
here, not a failure.

### Release candidates

- **Refresh remotes first:** `git fetch --all --tags`. RC branches are usually
  cut by someone else, so a stale remote-tracking list is the most likely reason
  a candidate that exists on the server is "not found" locally. This is a
  read-only fetch — it updates tracking refs and touches no working files.
- **Look in branches and tags, local AND remote** — `git branch -a` and
  `git tag`. RC branches commonly exist only on `origin`, so checking local refs
  alone misses them entirely.
- **What counts as an RC ref — use this regex, not a list of examples.**
  Case-insensitive, matched anywhere in the ref name:

  ```
  (^|[^a-z0-9])(rc|release[-_. ]?candidate)[-_. ]?0*([0-9]+)
  ```

  Both the short form (`rc`) and the long form (`release candidate`) are
  covered, with `-`, `_`, `.`, a space, or nothing as the separator. All of
  these match, and every one of them must:

  ```
  rc-1   rc2   RC_2   release/rc-2   v1.4-rc2
  release-candidate-2   release_candidate_01   RELEASE_CANDIDATE_10
  ```

  Teams spell this differently and the long underscore form
  (`release_candidate_01`) is common — matching only the short `rc` form finds
  nothing on those repos and silently drops to a lower rung.

- **The leading `[^a-z0-9]` guard is load-bearing.** Plenty of ordinary words
  contain the letters `rc` — `search-filter`, `archive-chat`, `source2`. Without
  the boundary they match as release candidates and the report compares two
  unrelated branches. Verified against this repo's ~60 branches: zero false
  positives.

- **N is capture group 3, with leading zeros stripped by the `0*`.** So
  `release_candidate_01` → N=1 and `release_candidate_09` → N=9. Parse base 10
  explicitly; `08` and `09` must never be read as octal.

- **Sort by N NUMERICALLY, never as text.** `rc-10` must beat `rc-9`; sorted as
  strings, `rc-10` sorts before `rc-2` and the report compares the wrong pair.
  A wrong range that looks right is the worst outcome this skill can produce.

- **Padding is cosmetic — unify on N.** `release_candidate_01` and
  `release_candidate_2` are candidates 1 and 2 of one series. Never treat
  different padding as different series.

- **If the user NAMES an RC that does not exist, stop and say so** — do not fall
  through to a lower rung. Falling through would silently report a different
  range than the one asked for, which is exactly the failure this chain exists
  to prevent. Name what was searched and list the RC refs that DO exist:

  > No ref matching release candidate 3 was found (searched local and remote
  > branches and tags). Found: `release_candidate_01`, `release_candidate_02`.
  > Did you mean RC2, or does the branch need fetching?

  If none exist at all, say the repo has no RC refs and suggest running without
  an argument.
- **Current RC** = the one named in $ARGUMENTS, else the highest N found.
  **Previous RC** = the next lower N that actually exists.
- **Only `rc-1` exists** → range runs from the latest release tag (or the repo's
  first commit if there are no tags) up to `rc-1`. State that in the header.
- **Gap in numbering** (`rc-1`, `rc-4`) → use `rc-1..rc-4` and note the gap in
  one line. Never invent the missing candidates.
- Print ref names **exactly as git has them**, whatever the spelling.

## Steps

1. **Resolve the range** per the chain above. Record: the resolved range string,
   which rung produced it, and the commit count
   (`git rev-list --count <range>`). All three go in the header.

2. **Read the code side** (local git, no API cost):
   - `git log --oneline <range>` — the commit list
   - `git log --oneline --merges <range>` — the PR/merge count
   - `git diff --name-only <range> | sort -u` — files touched
   - Map each commit to a ClickUp ticket via the repo convention: `(#<task-id>)`
     in the message, or `<type>/<task-id>-slug` in a merge commit's branch name.
     A commit with no ticket ID is **unlinked** — list it as such. Never infer
     which ticket an unlinked commit belongs to.

3. **Cap the commit list.** Above 40 commits, show merges only
   (`git log --oneline --merges <range>`) and print one line stating what was
   hidden and how to get it:
   *"Showing 12 merges; 203 commits total. Full log: `git log --oneline <range>`"*
   A silently truncated log is worse than no log — it reads as complete.
   `--full-log` disables the cap entirely.

4. **Read the board side.** One `clickup_filter_tasks` call for the space with
   `include_closed: true`, paginated until `has_more` is false. Scope it:
   - RC / tag / commit range → the current sprint tag (the tickets in flight)
   - `sprint N` → that tag
   - feature keyword → tickets whose title, tags or list match the keyword
   Keep each ticket's TITLE alongside its ID from here on — every list in this
   report is read by a human who must not have to open ClickUp to identify a
   ticket.

5. **Cross-check board against code.** This is the step that justifies the
   skill. Split every ticket in scope into exactly one bucket:
   - **Shipping** — `done`/`Closed` AND at least one commit in the range
     references it
   - **Closed with nothing merged** — `done`/`Closed` but NO commit in the range
     references it. Flag every one of these prominently. It means the ticket was
     closed early, the PR was never merged, or the work is not in this range.
     Do not diagnose which; report the fact.
   - **Not shipping** — anything not `done`/`Closed`, with its current status
   The three buckets must sum to the ticket count in scope. If they do not, say
   so in the report rather than quietly adjusting a number.

6. **Compute the verdict** per *Verdict rules* below. Every blocker names the
   ticket that caused it — a verdict without evidence is an opinion.

7. **Collect known issues.** From the step 4 fetch, every bug-tagged ticket NOT
   `done`/`Closed`, grouped by `priority` (`urgent`, `high`, `normal`, `low`,
   and `null` = no priority set). Every ticket carries title, ID and assignee.

8. **Derive "watch after release"** — 2–3 observations from what THIS run found,
   each naming its evidence. Never generic advice. Good sources: a file every
   change touches (blast radius), a cluster of PRs in one area, a feature
   shipping with open normal-priority bugs, a large unlinked-commit count.
   Observations, not diagnoses — say what the data shows, not why.

9. **Render the report** (template below) and **show it in chat. That is the
   whole output** — the run ends here. Nothing is written to ClickUp or git. Do
   not offer to post it and do not ask where to put it.

10. **Suggest the tag command on a GO verdict** — show it, never run it.
    Tagging writes to the user's repo and stays their call:
    `git tag rc-3 && git push --tags`

## Verdict rules

Three **hard blockers**. Any one of them → **NO-GO**:

1. An open `urgent` or `high` bug on a feature in this release
2. Any ticket in scope with status `blocked`
3. A ticket claimed as part of the release still sitting in `testing`

**Soft warnings** — reported, never blocking on their own:

- Tickets with no assignee
- Bugs with no priority set
- Repeat bouncers (2+ `bounced-<N>` tags, per the /qa-ticket-check convention)
- Unlinked commits
- Tickets closed with nothing merged

Verdict badges:

- 🟢 **GO** — no blockers, no soft warnings
- 🟡 **GO WITH CAUTION** — no blockers, but soft warnings present
- 🔴 **NO-GO** — one or more blockers

`--strict` promotes every soft warning to a blocker. Say in the footer which
mode ran, so a GO under default rules is never mistaken for a GO under strict.

## Report template

```
# 🚀 Release Report — <RC2 | Sprint N · DD Mon YYYY>

**Range:** `<range>` · N commits · N PRs · **<DD Mon YYYY>** · <sprint tag>
<On rung 6 add: "— inferred, no release tag found">

---

## <🟢|🟡|🔴> Verdict: <GO | GO WITH CAUTION | NO-GO>

> **N blockers.** <one plain sentence naming what is wrong, or what is clean>

| Blocker | Why it blocks | Ticket |
|---|---|---|
| **<title>** | <reason> | `<ID>` |

*Soft warnings — noted, not blocking: <list, or "none">*

---

## 📝 The short answer

<Two or three plain sentences: what is in this release, and the one thing that
matters most. This is the part the person shipping actually reads — name
features in words, never bare IDs.>

---

## 📦 What is shipping — N tickets

| Ticket | Type | Who | PR |
|---|---|---|---|
| **<title>** · `<ID>` | 🟦 Feature / 🟥 Bug | <first name> | #<n> |

⚠️ **Closed with nothing merged: N** — **<title>** · `<ID>` is marked `done`
but no commit in this range references it.
<Omit this line entirely when the count is 0.>

---

## 🔀 What changed in the code

**N PRs** merged · **N commits** · **N files** touched (`<names>`) · **N** unlinked

### Commits in this release

​```
<raw git log --oneline output, unedited>
​```

*Unlinked (no ticket ID): `<sha> <message>`*

---

## 🐞 Known issues shipping with it — N open bugs

| Priority | Open | Tickets |
|---|---|---|
| 🔴 Urgent | **N** | **<title>** · `<ID>` — <assignee> |
| 🟠 High | **N** | — |
| 🟡 Normal | **N** | ... |
| 🟢 Low | **N** | — |
| ⚪ No priority set | **N** | ... |

<One or two plain sentences on what this means for shipping.>

---

## 🚧 Planned but not in this release — N tickets

| Ticket | Stuck at | Who has it |
|---|---|---|
| **<title>** · `<ID>` | <status> | <first name> |

---

## 👀 Watch after release

- **<Short bold label>** — <the observation, naming its evidence>

---

## 🧭 Next step

<What to do about the verdict. On NO-GO: fix which ticket, then re-run. On GO:
the tag command, shown not run.>

---

*Verdict rule: open urgent/high bugs on shipping features block. Soft warnings
don't. Run with `--strict` to block on those too.*

## ⚠️ What I could not check
<Only when something genuinely failed. Name the missing thing, why it matters
in one sentence, and the concrete fix.>
```

## Formatting rules

These are what make it readable — the same rules the daily report follows:

- **A blank line between every section, and a `---` rule between blocks.**
  Spacing is never what gets cut when the report runs long.
- **ALWAYS print the ticket TITLE next to the ID — never a bare ID.** A reader
  given `86d4103zv` has to open ClickUp; `86d4103zv — Search filter drops the
  last result` they can act on. Titles come from the step 4 fetch and cost
  nothing. Truncate past ~50 characters at a word boundary, keeping any leading
  `[Area]` prefix. Never drop a title to save a line.
- **Ticket lines lead with the bold title; the ID goes last in backticks.**
- **One person per ticket line: the assignee.** Never the creator or reporter
  alongside. Print `unassigned` explicitly rather than leaving it blank.
- **A zero is information — print it.** Every priority row appears with its real
  count, `🔴 Urgent 0` included, with an em dash for the ticket cell. A missing
  row is indistinguishable from a check that never ran.
- **Known-issues rows cap at 3 tickets, then `*+N more*`** — except **urgent and
  high, which are NEVER capped**, because those rows drive the verdict. The
  count column always shows the true total, so a capped row still reports the
  real number; the cap hides names, never a number.
- **Sections with nothing to say still appear**, with one italic line in that
  section's own terms — *No blockers*, *Nothing planned that slipped*, *No open
  bugs*. A vanished section reads as a check that never ran.
- **Order is fixed:** verdict → summary → shipping → code → known issues →
  spillover → watch → next step. The decision is first; caveats are last,
  because nobody acts on them.
- **Explain jargon inline the first time.** "Release candidate", "blocker" and
  "unlinked commit" are not obvious to a reader outside the team.
- The report must be skimmable in under a minute by someone who does not know
  the board.

## Important

- **Fully read-only.** This skill never changes ticket state, never writes to
  ClickUp, and never runs a git write. The tag command in step 10 is *shown*,
  never executed.
- **The raw commit block is raw.** Exactly what `git log --oneline` printed —
  not reworded, reordered or filtered. The moment it is tidied it stops being
  usable in a postmortem, which is half the reason the section exists.
- **Print the range in the header, always.** With no tags the range is inferred,
  so it must be visible and reproducible by anyone reading the report later.
- Budget API calls: **one** `clickup_filter_tasks` fetch is the target. Git is
  local and free. No per-ticket reads unless a specific ticket needs a detail.
- If the ClickUp API rate limit blocks the fetch, report that plainly and stop.
  Never fabricate counts. If it fails partway, keep the git side (it is real),
  mark the board-derived lines "unavailable — rate limited", and still show the
  report. A partial report labelled honestly beats no report.
- **Never infer which ticket an unlinked commit belongs to.** Report it as
  unlinked and let a human decide.
- Every count must be traceable to a ticket or commit the report names. If a
  number cannot be broken down, do not print it.
- Sample/test tickets on the board are fake; count them but write `*(sample)*`
  after the title so the numbers are not misread.
- Watch items are observations, not conclusions. "3 of 4 PRs touch theming" —
  do not diagnose why, and never guess at a cause the data does not show.
