# Scheduled Routines (Cloud Agents)

Runbook for the project's scheduled Claude Code cloud agents ("routines").
Routines are tied to a personal claude.ai account — if that account changes
(e.g. NextSense → Infocusp migration), recreate them from this file.

## Active routines

### qa-daily-report

- **What:** runs the [`/qa-daily-report`](../.claude/skills/qa-daily-report/SKILL.md)
  skill autonomously — fetches the ClickUp board, builds the daily QA summary,
  writes it as a dated page into the ClickUp Doc **"QA Daily Reports — TaskPulse"**
  (doc-only writes; never touches tasks/lists/comments; refuses to fabricate
  numbers if the ClickUp API is rate-limited).
- **Schedule:** weekdays 9:00 AM IST (cron `30 3 * * 1-5`, UTC)
- **Model:** claude-sonnet-5
- **Repo attached:** `pranavuttarwar-Infocusp/AI-Workflow-Project` (agent reads
  the skill file from the **default branch** — skills must be merged to `main`)
- **MCP connection:** ClickUp (`https://mcp.clickup.com/mcp`)
- **Currently registered under:** pranav.uttarwar@nextsense.io
  (routine id `trig_017xrXoVsfQo6MygcM4ho4ss`,
  manage at https://claude.ai/code/routines)

## How to recreate a routine under a new account

1. Log into claude.ai / Claude Code with the new account.
2. Connect the **ClickUp** connector for that account (Settings → Connectors →
   ClickUp → OAuth; may need workspace-admin approval).
3. In a Claude Code session on this repo, run `/schedule` and ask for:
   *"run /qa-daily-report every weekday at 9:00 AM IST, repo
   pranavuttarwar-Infocusp/AI-Workflow-Project, ClickUp connector attached,
   doc-only writes"* — the skill file in this repo is the source of truth for
   the report itself.
4. Trigger a manual test run and verify a dated page appears in the
   "QA Daily Reports — TaskPulse" doc in ClickUp.
5. Disable the old account's routine at https://claude.ai/code/routines.

## Gotchas learned

- Routines run in Anthropic's cloud: no local files, no local connector auth —
  the claude.ai account's own connectors are used.
- The agent checks out the repo's default branch; unmerged feature-branch
  skills are invisible to it.
- ClickUp assignment via email/username fails silently — use numeric user IDs.
- ClickUp API rate limits are per token; heavy iterative testing can exhaust a
  day's quota (error says how long to wait).
