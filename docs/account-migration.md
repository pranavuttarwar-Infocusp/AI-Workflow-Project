# Claude Account Migration Guide — NextSense → Infocusp

Step-by-step runbook for moving this project's AI workflow to a new Claude
account. Written 2026-08-12, when the setup ran under pranav.uttarwar@nextsense.io.

> **Golden rule:** everything durable lives in this repo. The Claude account is
> just the engine — swap it, plug the connectors back in, recreate one routine.

---

## Phase A — Before the switch (while the old account still works)

- [ ] **A1. Ask the Infocusp Claude workspace admin** whether these connectors
      are allowed (they'll show "Connect" if self-serve, "Request" if
      admin-gated): **ClickUp** (required), **Slack** (wanted for reports),
      Figma / Google Drive (optional). Start any "Request" approvals now —
      this is the only step with a wait you don't control.
- [ ] **A2. Confirm repo access**: the Infocusp GitHub account (or your
      existing one) must be a collaborator on
      `pranavuttarwar-Infocusp/AI-Workflow-Project`. `gh auth status` on your
      machine shows which account the CLI uses — this is independent of Claude.
- [ ] **A3. Note the current routine** so you can compare after migration:
      https://claude.ai/code/routines — routine `qa-daily-report`
      (`trig_017xrXoVsfQo6MygcM4ho4ss`), weekdays 9:00 IST.

## Phase B — Set up the Infocusp account

- [ ] **B1. Sign in** to Claude (app + claude.ai) with the Infocusp ID.
- [ ] **B2. Connect ClickUp**: Settings → Connectors → ClickUp → Connect →
      OAuth into the same ClickUp workspace. Verify with a harmless read:
      *"list my ClickUp spaces"* → should show "AI Workflow Project".
- [ ] **B3. Connect Slack** (if approved): pick the **Infocusp** workspace in
      the OAuth popup — this is the workspace the team wants QA reports in.
- [ ] **B4. Open this repo** in Claude Code with the new account. CLAUDE.md,
      the skills (`/qa-ticket-check`, `/qa-daily-report`, `/qa-test-cases`,
      `/qa-bug-report`), hooks, and guardrails all load automatically — no
      setup needed.

## Phase C — Fix the one account-specific config

- [ ] **C1. Update the ClickUp connector ID in `.claude/settings.json`.**
      The `ask` rules contain tool names like
      `mcp__2524e66b-d0fd-4bad-b014-f7b70b682b4f__clickup_create_task` — that
      long UUID is **per-connection** and changes with the new account.
      In a new-account session, ask Claude:
      *"what is the full tool name of the ClickUp create-task tool?"* — then
      find-replace the old UUID with the new one in settings.json and merge it
      via a small PR.
- [ ] **C2. Verify the guardrails**: ask Claude to edit a file → it must
      prompt. Ask it to create a ClickUp task → it must prompt. If either runs
      silently, the connector ID in C1 is wrong.

## Phase D — Recreate the scheduled routine

- [ ] **D1.** In a Claude Code session on this repo (new account), run
      `/schedule` and ask:
      *"Run /qa-daily-report every weekday at 9:00 AM IST. Repo
      pranavuttarwar-Infocusp/AI-Workflow-Project, ClickUp connector attached.
      Doc-only writes — never create/update tasks, lists, or comments. If the
      ClickUp API is rate-limited, report the error instead of fabricating
      numbers."*
      (Full spec of the old routine: see `docs/routines.md`.)
- [ ] **D2. Test-fire it once** ("run the routine now") and verify a dated
      page appears in the ClickUp Doc **"QA Daily Reports — TaskPulse"**.
- [ ] **D3.** If Slack got connected in B3: add the Infocusp channel ID to the
      Slack destination slot in `.claude/skills/qa-daily-report/SKILL.md`
      (currently a placeholder) via PR.

## Phase E — Decommission the old account

- [ ] **E1. Disable the NextSense routine** at https://claude.ai/code/routines
      (old account) so it doesn't fail-spam when its connectors die.
- [ ] **E2.** Nothing else to clean up — chat history and memory on the old
      account are lost with it; everything that matters is in this repo.

---

## What survives vs. what doesn't (reference)

| Item | Survives the switch? |
|---|---|
| Repo: skills, CLAUDE.md, guardrails, hooks, docs | ✅ automatic |
| ClickUp board, tickets, docs | ✅ untouched |
| GitHub access / PRs / Pages live site | ✅ untouched |
| Connector authorizations | ❌ redo (B2–B3) |
| ClickUp connector UUID in settings.json | ❌ update (C1) |
| Scheduled routine | ❌ recreate (D1) |
| Old chat history & Claude memory | ❌ lost |

**Total effort: ~15–20 minutes** (plus any admin-approval wait from A1).
