---
description: Generate structured test cases from a ClickUp task, GitHub PR, or feature description for the TaskPulse app. Includes edge cases, risk areas, and coverage gaps.
---

# QA Test Case Generator

## Input

The user will provide one of:
- A ClickUp task URL or ID
- A GitHub PR URL or number
- A feature/area description (e.g., "due dates", "search", "theme toggle")

**User's input:** $ARGUMENTS

## Steps

1. **Gather context**:
   - If ClickUp task: fetch the task details, read the description and comments
   - If PR: run `gh pr view <number>` and `gh pr diff <number>` to understand the changes
   - If description: read `index.html` and the relevant `docs/*.md` module doc to find the feature

2. **Understand the feature/change**:
   - Read the relevant sections of `index.html` (markup, CSS, and JS for the feature)
   - Check the matching module doc (`docs/ui-layout.md`, `docs/state-storage.md`,
     `docs/rendering.md`, `docs/theming.md`, `docs/interactions.md`) for the documented
     expected behavior — the README feature list is the public contract
   - Identify all user-facing behaviors and state transitions
   - Note what persists in localStorage and what resets on reload

3. **Generate test cases** in the 10-column matrix format:

   ```
   ## Test Suite: <Feature/Change Name>

   ### Prerequisites
   - <Browser + starting state, e.g. "fresh localStorage" or "3 seeded tasks, 1 done">

   | Sr.No. | Area | Category | Scenario | Description | Steps | Expected Result | Comments/Ticket/Notes | Results | Tested Version |
   |--------|------|----------|----------|-------------|-------|-----------------|----------------------|---------|----------------|
   | 1 | ... | Happy Path | ... | ... | ... | ... | ... | Not Run | ... |
   | 2 | ... | Edge Case | ... | ... | ... | ... | ... | Not Run | ... |
   | 3 | ... | Negative | ... | ... | ... | ... | ... | Not Run | ... |

   ### Risk Areas
   - <Area 1>: <Why it's risky>
   - <Area 2>: <Why it's risky>

   ### Regression Concerns
   - <What existing features might be affected>
   ```

   Column conventions:
   - **Category**: Happy Path / Edge Case / Negative / Browser-Compat / Regression
   - **Steps**: numbered, concrete actions ("1. Type 'x' in search 2. Press Esc")
   - **Results**: starts as "Not Run"; tester fills Pass/Fail
   - **Tested Version**: the commit hash or PR number under test

4. **Highlight** (TaskPulse-specific concerns):
   - localStorage persistence: does the change survive a page refresh? Corrupt/missing
     storage (private browsing) must not break first render
   - Both themes: every UI change must be checked in dark AND light mode
   - Responsive: check at 375px width (mobile) — stats grid collapses at 520px
   - Keyboard shortcuts: Enter adds, Esc clears — do they still work after the change?
   - Empty states: zero tasks, zero search results, all tasks completed
   - Date edge cases (for due-date features): due today, due yesterday, far future,
     around midnight, no due date at all
   - Search/filter combinations: search + Pending filter, search with zero matches,
     clearing search
   - Areas with recent code churn (check `git log --oneline -10 -- index.html`)

## Important
- Prioritize test cases by risk — put the most critical ones first
- Always include a refresh-persistence scenario for any feature that changes task data
- For UI changes, include both-themes and mobile-width scenarios
- Keep test steps concrete and actionable — no vague "verify it works"
- If asked to file the suite, create ClickUp tasks only after user confirmation
  (per `.claude/settings.json` ask rules)
