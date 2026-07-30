---
description: Create a ClickUp bug task from a quick description of a TaskPulse issue. Classifies bug vs enhancement first, then writes a standardized task with prerequisites, repro steps, expected/actual results, build/device details, and attachments.
---

# ClickUp Bug Report

## Input

The user will provide a quick, informal description of the bug they found in TaskPulse. It may be brief or detailed. Example:
- "theme toggle resets to dark mode after refresh even though I picked light"
- "adding a task with an empty title still creates a blank task card"

**User's description:** $ARGUMENTS

## Steps

0. **Classify first — bug or enhancement?** Before drafting anything, decide whether this is
   an actual **defect** (behavior contradicts documented/expected behavior) or an
   **enhancement / suggestion** (a net-new ask that was never specified). Check against:
   - The README feature list (the public contract for what TaskPulse does)
   - The relevant `docs/*.md` module doc (`ui-layout`, `state-storage`, `rendering`,
     `theming`, `interactions`)
   - The current behavior in `index.html`
   - If it clearly **contradicts documented behavior** → it's a Bug. Continue below.
   - If **no documented behavior backs the expectation**, or it asks for something beyond
     what's specified → it's likely an **Enhancement**. **Tell the user plainly:**
     *"This reads as an enhancement, not a defect — I couldn't find documented behavior it
     violates. File it as an Enhancement, or should I dig deeper?"* Do NOT silently create a
     Bug task. Only proceed once the user confirms bug vs. enhancement, and set the task
     tag/type accordingly.

1. **Parse the description** and identify:
   - What happened (actual result)
   - What should have happened (expected result)
   - Feature area (Tasks, Filters, Stats, Theme, Search, Shortcuts, Storage, etc.)
   - Likely priority (Urgent/High/Normal/Low)
   - Any build/browser/device details mentioned

2. **Check the code** to understand the feature area:
   - Read the relevant markup/CSS/JS section in `index.html` for the feature
   - Check the matching `docs/*.md` module doc for documented expected behavior
   - Note any recent changes to that area (`git log --oneline -10 -- index.html`)

3. **Check ClickUp for duplicates**:
   - Use `clickup_search` or `clickup_filter_tasks` for similar existing tasks using
     relevant keywords
   - If potential duplicates are found, list them and ask the user before creating a new one

4. **Draft the task** with this structure:

   **Title**: `[Area] Short descriptive title`

   **Description** (markdown):
   ```
   ## Prerequisites
   - <Starting state needed to reproduce, e.g. "fresh localStorage, light theme, 3 tasks (1 done)">

   ## Repro Steps
   1. <Step 1>
   2. <Step 2>
   3. ...

   ## Actual Result
   <What actually happens>

   ## Expected Result
   <What should happen instead>

   ## Build and Device Details
   - Browser + version: <ask if not provided>
   - OS: <ask if not provided>
   - Screen size / viewport: <ask if not provided, especially for responsive issues>
   - Build/commit: <current commit hash if known>

   ## Attachment
   <Leave blank — reporter/QA will attach screenshots, screen recordings, or console logs manually>

   ## Test Plan Link
   <Link to the relevant test suite/case if one exists, e.g. from the qa-test-cases skill — otherwise omit this section>

   ## Note for Developer
   <Any special context: suspected root cause, related code area, workaround in place — omit this section if nothing to add>
   ```

5. **Ask the user to confirm** the task details, then create it in ClickUp:
   - List: ask the user which List to file it in if not already clear (use
     `clickup_get_workspace_hierarchy` or `clickup_search` to help locate it)
   - Priority: based on the assessment in step 1
   - Tags: `bug` if step 0 confirmed a defect; `enhancement` if it's a net-new ask
   - Creating the task itself (`clickup_create_task`) requires user confirmation per
     `.claude/settings.json` ask rules — never skip this

## Important
- **Classify bug vs enhancement (step 0) before drafting** — never auto-file a "Bug" for
  something with no documented behavior behind it. Set the tag to match the verdict.
- Always ask the user to confirm before creating the task
- If the description is too vague, ask clarifying questions FIRST (especially build/device
  details and repro steps — these are required fields, not optional)
- Check for duplicates before creating
- Keep the artifact list exactly as above: Title, Prerequisites, Repro Steps, Actual Result,
  Expected Result, Build and Device Details, Attachment, Test Plan Link (if applicable),
  Note for Developer (if applicable)
- Omit "Test Plan Link" and "Note for Developer" sections entirely when not applicable —
  don't leave placeholder text in the final task
