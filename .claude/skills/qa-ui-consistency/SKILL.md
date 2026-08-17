---
description: Check that colours, fonts, spacing, padding, radius and component styling are consistent across every module of any app, in any language or UI stack. Finds hardcoded values that should use the project's design tokens, values that drift from the standard, buttons or inputs of the same kind that differ in colour or size for no reason, and styles that break in one theme. Written for QA — plain-language report, grouped by module, with file:line for the developer. Triggers on "/qa-ui-consistency", "check UI consistency", "are the colours consistent", "check fonts and spacing across modules", "are all the buttons the same colour", "why do these buttons look different", "design token check".
---

# UI Consistency Check

**Why this exists:** anyone can spot a button that is obviously the wrong colour.
Nobody can spot a blue two shades off, across forty screens, by eye. This skill is
for the differences a human cannot see — so rank findings by how invisible they
are, not by how dramatic they sound.

**Rule:** nothing about any project is hardcoded here — not the stack, file names,
token names, or what the "correct" value is. Derive it all from this repo. Examples
illustrate a *pattern*, never a value to look for.

**Never read whole files.** Extract style lines with search tools and reason over
the aggregate (Step 3). Opening files costs 10–20x more than grepping them and adds
nothing — a component's logic tells you nothing about its colours.

**Input:** $ARGUMENTS — empty (whole app), or a module / path / feature name, or
`--changed` (only files changed vs the default branch).

## Step 1 — Preflight

**Stop if:** no source code (ask for the path) · **no UI at all** — backend, CLI,
library, pipeline (say "nothing to check, this repo has no user interface" and stop;
never invent a report) · several apps in subfolders, none named.

**Ask but continue if:** no tokens found ("treat most-used values as the standard?"
— assume yes) · one theme found but the app looks like it has a switcher.

Max 2 questions, one message, each with a default.

## Step 2 — Name the stack, find the standard

State the styling system in the report — it caps what you can honestly claim:

| Stack | Coverage |
|---|---|
| Plain CSS / custom properties, SCSS / LESS vars, CSS Modules, utility-class config | **Full** |
| CSS-in-JS themes, native theme classes, style-constant modules | **Partial** — literals yes, runtime no |
| Component library whose theme lives in a dependency | **Partial** — only the project's overrides are visible |
| No recognisable styling layer | **Low** — literal scan only |

Never claim more than the stack allows. An honest "partial" beats a clean report
that missed half the app.

**The standard**, cheapest first: agent instruction files (`AGENTS.md`, `CLAUDE.md`)
if they state styling rules → whatever this project uses to declare design values
(token source, theme object, style config, constants, asset catalog — find it, don't
assume its name) → **nothing declared?** build it by frequency, and say you did,
because it changes what the results mean.

## Step 3 — Extract, don't read

**Scope**, first that applies: what the user named → `--changed` → everything.
Named something? Resolve it and say what you resolved it to: a **path** if it
matches → else a **module** whose folder/route/screen name matches → else a
**feature**, searched by name across file names, component names, routes and
labels. **No match?** Say so and list the modules you found — never silently scan
everything instead.

Then build the picture with search tools, in this order. Stop as soon as you can
answer the checks.

1. **The token set** — read only the file(s) that declare design values. This is
   the one place reading whole files is right; it is usually small.
2. **Every style value with counts and locations** — one search pass per family
   (colour, font, spacing, radius, size), matching the syntax *this* stack uses.
   Output you want per value: the value, how many times it appears, and where.
   Sort by count. This aggregate is what you reason over.
3. **Only then open files** — at most a handful, and only when a specific finding
   needs surrounding context (which component a value belongs to, whether a variant
   modifier explains it). Never open a file "to have a look".

Frequency comes free with this approach, and the near-duplicate and odd-one-out
checks need frequency to work at all — so the cheap path is also the accurate one.

Skip dependency, build and generated directories — names differ by ecosystem, so
read the repo rather than matching a fixed list. Skip minified files. Never read env
or secrets files, and never put credentials in the output.

## Step 4 — The 7 checks

For each: findings, or `N/A — <reason>`. Never skip one silently.

1. **Colour** — (a) literals written inline where an approved value exists.
   (b) **Near-duplicates** — the most common real drift and the hardest to see.
   **Normalise first**: one colour can be written as hex, decimal, percentage,
   named, with or without alpha — convert to one form or you compare text, not
   colour. **Compare perceptually**, not as strings. Split into *indistinguishable*
   (no visible difference — almost always a mistake) and *close but visibly
   different* (could be a hover state, border, or real second shade — check whether
   the project defines one). **Name the outlier by count**: "34 places" vs "here
   only" is what makes it actionable; never report "two similar colours exist" with
   no direction. Group all occurrences of one drifted value into one finding.
2. **Font** — families, sizes, weights, line-heights outside the set. One off-scale
   size among a regular scale is the classic miss. Units vary by platform.
3. **Spacing & padding** — margin/padding/gap/inset off the scale.
4. **Radius & borders** — radii and border colours that don't match.
5. **Theme parity** — what ships broken and what QA catches last. **One theme?**
   `N/A — single theme`. **More?** Learn how this stack resolves a value the other
   theme omits. Where an omitted value falls back to a base definition that is
   *correct* for theme-neutral things (radius, spacing, sizes) and only a problem
   for **colours** tuned to one background — those go in **Ask first** with the
   contrast ratio as evidence. Reserve **Ready to log** for a value that cannot
   switch at all, or a component styled in one theme with no counterpart. Get this
   wrong and you report bugs that don't exist.
6. **Broken references** — a token used but never defined (typos fall back
   silently), and tokens defined but never used.
7. **Component consistency** — the only check comparing components **to each
   other**, so the only one that catches two elements each individually valid that
   still disagree: the same kind of button in two different approved colours, or at
   two slightly different heights.
   - Group by what elements are (buttons, inputs, cards, icons, modals) using
     whatever this repo calls them. Derive groups from the code.
   - Compare **colour** (background, text, border — highest value here, even when
     both are legitimate tokens), then **size**, then **shape and weight**.
   - **Variants are not drift.** Primary/secondary/danger are meant to differ;
     small/medium/large is a real ladder. Look for intent — a named variant,
     modifier, prop, distinct role. Drift is same-role elements that disagree, or
     values clustered close with no ladder behind them.
   - **Name the odd one out.** Nine buttons one colour, one different — say which.
   - Mostly **Ask first**. Promote to **Ready to log** only when the code shows
     intent: elements sharing a component or class that still render differently.

Then **contrast** — for text/background pairs actually used together, flag below
WCAG AA (4.5:1 normal, 3:1 large).

## Step 5 — Cut the noise

**Always skip** — hardcoded on purpose: keywords meaning "no colour" or "inherit" ·
icons, logos, illustrations, brand assets · chart palettes, syntax highlighting,
data-visualisation scales · third-party overrides, email templates, print styles.

**Two buckets:** **Ready to log** — the inline value equals an existing token, a
reference is broken, or a theme visibly loses styling; mechanical. **Ask first**
— near-duplicate, off-scale, or matching nothing; might be deliberate.

Never write "wrong" — write "doesn't match the project's <value>". Over 15 findings
in a module: show the top 10, count the rest, say you truncated.

## Step 6 — Output

**The report is a list of bugs a tester can log, not a code review.** Every finding
is written so it can be pasted into a ticket and discussed with a developer without
anyone translating it first. No jargon in the tester-facing lines — no "token",
"cascade", "literal", "hex". All code detail goes on the one developer line.

Open with the scope you assumed — `<whole app | "what they asked" → what you
scanned>`, module and file counts, styling system, theme count, coverage — so a
wrong guess is obvious. Then:

```
## UI Consistency Report

<One sentence anyone understands: is this app consistent, and what is the single
biggest problem.>

Checked <n> modules · <n> files · coverage <full | partial | low>
<n> ready to log · <n> to ask about

---

## Ready to log

These are clear mistakes. Log them as-is.

### <n>. <Short bug title, as you would type it into a ticket>

- **What you'd see:** <what appears on screen, and when — the step that shows it.>
- **What should happen:** <the correct behaviour.>
- **How bad:** <High | Medium | Low> — <one clause of why>
- **Developer note:** `<file:line>` — <the change, in code terms>

---

## Ask first

These might be deliberate. Check with the developer before logging.

### <n>. <Short title>

- **What you'd see:** <plain description.>
- **Why it might be on purpose:** <the innocent explanation.>
- **Question for the developer:** <the one thing to ask.>
- **Developer note:** `<file:line>` — <detail, with counts where relevant>

---

## What was checked

One line each — Colour, Font, Spacing & padding, Radius & borders, Theme parity,
Broken references, Component consistency, Contrast — "<n> found", "clean", or
"N/A — <reason>".

## Not checked — needs your eyes

- <where> — <plain reason, e.g. this colour is decided while the app runs>
- The screens were not opened — this reads the code, not the finished screen
```

Rules:

- **A title per finding**, phrased as a bug title someone would type — "Logo stays
  dark blue in light mode", not "hardcoded accent value".
- **"What you'd see" must be observable.** Say what appears on screen and when. If
  you cannot describe it that way, the finding may not matter — reconsider it.
- **How bad:** High = users notice or cannot read something · Medium = visible if
  you look · Low = invisible now but will break later.
- **Order by invisibility, not drama** — what a tester could never catch by eye
  first; obvious problems last, since someone would have found those anyway.
- Number continuously across both sections so anyone can say "number 4".
- One problem per number. Every finding needs a real `file:line` from your search
  results.
- **Grade every sentence outside the developer note:** could a tester who has never
  seen the code read it aloud in a stand-up? If not, rewrite it.
- Empty sections say "Nothing found" rather than disappearing — a missing section
  looks like a check that never ran. Clean app? Say so and still show "What was
  checked".

Show the report in chat. Only write a file or raise tickets if asked.

## Step 7 — Check yourself

- You did not read whole source files where a search would have done
- Colours were normalised before comparing, so one colour written two ways isn't
  reported as two
- Every near-duplicate names the standard and the outlier, with counts
- Every finding has a real `file:line`, and leads with a plain sentence about what
  the user sees — not a code value or jargon
- Nothing from the Step 5 skip list leaked in
- Every "Needs fixing" is mechanical; judgement calls moved to "Worth a look"
- Nothing flagged as drift is actually a named variant
- All 7 checks plus contrast are filled in or `N/A` — and each `N/A` was right
- Stated coverage matches the stack you found
- **No value, token name or file path from any example in this skill appears in
  your report** — if one does, you copied instead of reading the repo

## Limits

- Expect most drift, not all. Runtime-composed styles and precedence-dependent
  rendering are outside what code reading can see — say so every time.
- You compare the code against the project's **own** standard, so you find internal
  inconsistency. If the real standard lives in a design tool and was never encoded,
  an app can be perfectly self-consistent and still entirely off-spec. Say which
  case you are in.
- A rule that only lives in a designer's head can't be checked. Flag anything that
  looks like an unwritten rule rather than assuming current behaviour is correct.
