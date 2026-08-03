# POC Document — AI-Assisted QA Workflow with Claude Code

**Project:** TaskPulse (AI-Workflow-Project)
**Author:** Pranav Uttarwar
**Date:** July 2026
**Repo:** https://github.com/pranavuttarwar-Infocusp/AI-Workflow-Project
**Live App:** https://pranavuttarwar-infocusp.github.io/AI-Workflow-Project/

---

## 1. Why This POC Was Created (Purpose)

The goal of this POC is to learn and demonstrate a complete **AI-assisted development & QA workflow** on a safe practice project, before applying the same patterns to real company repositories.

Specifically, it proves that one person can:

1. Build and deploy a working app using Claude Code (AI pair-programmer)
2. Follow a professional Git/GitHub workflow (branch → PR → review → merge)
3. Connect external tools (ClickUp, Figma) to Claude through MCP connectors
4. Put **guard rails** on the AI so it cannot change code, push code, or write to
   ClickUp without human permission
5. Teach the AI project-specific rules (CLAUDE.md) and reusable QA workflows (skills)

Everything was done on a dummy project (TaskPulse — a small task-tracker web app) so
no company code or data was ever involved.

---

## 2. Key Definitions (Simple)

| Term | What it means | Why it matters |
|---|---|---|
| **Claude Code** | An AI assistant that runs on your machine, can read/edit files, run commands, and use git | The "AI developer" in this workflow |
| **Repository (repo)** | A project folder tracked by git, hosted on GitHub | The single source of truth for the code |
| **Branch** | A parallel copy of the code where you make changes safely | Keeps unfinished work away from the official version |
| **Pull Request (PR)** | A request to merge a branch into `main`, with a visible diff | The review checkpoint — nothing enters main without an explicit yes |
| **GitHub Pages** | Free hosting that serves the app straight from the repo | Turns the repo into a live shareable URL, auto-updates on every merge |
| **MCP (Model Context Protocol)** | The standard that lets Claude talk to external tools (ClickUp, Figma, Slack…) | How the AI reads/creates tickets or reads designs |
| **Connector** | One MCP integration (e.g., "the ClickUp connector") | Installed/approved per workspace; each needs a one-time login |
| **CLAUDE.md** | A rules file in the repo root that Claude reads automatically every session | The project's "constitution" for the AI — conventions it must follow |
| **settings.json** | Claude Code's permission + automation config (`.claude/settings.json`) | The guard rails: what AI may do silently, must ask for, or can never do |
| **Hook** | A command that runs automatically at a lifecycle point (e.g., after every file edit) | Automated checks that don't rely on anyone remembering |
| **Skill** | A reusable prompt playbook invoked with `/skill-name` | Packages a whole QA workflow (e.g., test-case generation) into one command |

---

## 3. Final Folder Structure

```
AI-Workflow-Project/
├── index.html                        # The entire app (markup + CSS + JS in one file)
├── README.md                         # Public docs: features, how to run, structure
├── LICENSE                           # MIT license
├── .gitignore                        # Files git must ignore (incl. personal settings)
├── CLAUDE.md                         # Root AI rules — loaded automatically each session
├── POC.md                            # This document
├── docs/                             # Module-wise docs (keeps root CLAUDE.md short)
│   ├── ui-layout.md                  #   Component map + layout/CSS rules
│   ├── state-storage.md              #   Data model + localStorage rules
│   ├── rendering.md                  #   Render model + XSS rule
│   ├── theming.md                    #   Dark/light theme system rules
│   └── interactions.md              #   User actions + keyboard shortcuts
└── .claude/                          # All Claude Code configuration
    ├── settings.json                 # Permissions (allow/ask/deny) + hooks
    └── skills/
        ├── qa-test-cases/
        │   └── SKILL.md              # /qa-test-cases — test-case generator skill
        └── qa-bug-report/
            └── SKILL.md              # /qa-bug-report — ClickUp bug ticket creator skill
```

**Why this structure:** it mirrors how large production repos organize AI-assisted
development — one short root rules file, detailed docs per module, and all AI
configuration inside `.claude/` so it travels with the repo to every teammate.

---

## 4. Step-by-Step: How Everything Was Built

### Phase 1 — Create the project
- Asked Claude Code to create a small presentable app → **TaskPulse**, a task tracker
  (add/complete/delete tasks, priorities, filters, live stats, dark/light theme,
  localStorage persistence). Single HTML file, zero dependencies.
- Verified in the browser before shipping (Claude opens the app and tests it).

### Phase 2 — GitHub setup and first push
1. Created a new **empty repository** on GitHub (`AI-Workflow-Project`).
2. Machine already had GitHub credentials (`gh` CLI logged in). Because the repo
   belonged to a second account, the owner account sent a **collaborator invitation**
   to the machine account (Repo → Settings → Collaborators → Add people), which was
   accepted — after that, pushing worked.
3. Initialized git locally, committed, added the remote, pushed to `main`.

**Why:** GitHub is the backup, the collaboration point, and (later) the deployment
source. The collaborator flow is the standard way to grant a second account write
access.

### Phase 3 — Learn the PR workflow
- Practiced all three browser-based flows: edit-a-file PR, upload-files PR, and
  create-new-file PR.
- Practiced the terminal flow: `git checkout -b` → edit → `commit` → `push` →
  open PR → merge → `git pull`.
- **18+ PRs merged** over the course of the POC; every change (features, docs,
  config) went through a PR — never a direct commit to `main`.

**Why:** PRs are the industry-standard checkpoint. The diff is visible, reviewable,
and nothing reaches the official branch without an explicit merge.

### Phase 4 — Deploy with GitHub Pages
- Repo → Settings → Pages → Branch: `main`, folder: `/ (root)` → Save.
- App became live at the `github.io` URL within a minute; **every merge to main
  redeploys automatically**.

**Why:** a live URL anyone can open beats "clone it and open index.html" for demos,
testing, and sharing with the team.

### Phase 5 — CLAUDE.md + module docs (teach the AI the rules)
- **Root `CLAUDE.md`**: project structure, tech constraints (single file, no
  dependencies), styling rules (CSS variables, both themes), storage rules
  (namespaced localStorage keys), git rules (conventional commits, always PR).
- **5 module docs in `docs/`** so the root file stays short — each covers one logical
  module with its own "Hard Rules" section. The root file lists them in a
  **Nested:** line so readers (and the AI) know they exist.

**Why:** Claude reads CLAUDE.md automatically at session start. Rules written once
are then enforced every session, for every user of the repo — no need to repeat
instructions. Splitting into module docs keeps the always-loaded root file small.

### Phase 6 — Connect ClickUp (MCP connector process)
The full connection process, as experienced:

1. **Request**: In the Claude app → Settings → Connectors, clicked ClickUp — it
   showed **"Requested"** instead of connecting, because the workspace admin controls
   the connector allowlist.
2. **Admin approval**: The workspace admin approved the request in the admin console.
3. **OAuth login**: After approval, clicked Connect → logged into ClickUp in the
   browser popup → authorized access.
4. **Verification**: Claude successfully read the ClickUp workspace hierarchy
   (Spaces → Lists), proving the connection worked end-to-end.

**Why ClickUp:** it's the ticket tracker for this workflow. With the connector,
Claude can read tasks, create bug tickets in proper QA format, and update statuses —
turning "found a bug" into "filed a structured ticket" in seconds.

**Key learning:** whether a connector needs admin approval is **workspace policy**,
not a property of the connector. Buttons showing "Connect" are self-serve; buttons
showing "Request" go to the admin.

### Phase 7 — Figma (design connector)
Figma connects through the same MCP process (Settings → Connectors → Figma → OAuth).
Not exercised in this POC because TaskPulse has no Figma designs, but the intended
QA uses are:
- Open a Figma design and compare it against the implemented UI (design-vs-build
  review)
- Pull exact spacing/colors/text from the design when filing UI bugs ("expected per
  Figma: 16px padding; actual: 8px")
- Generate test cases directly from design screens before the feature is even built

**Why it's in this document:** it's the natural next connector for a QA workflow, and
the connection process is identical to ClickUp's (request → approve if gated → OAuth).

### Phase 8 — settings.json (guard rails on the AI)
Created `.claude/settings.json` with three permission tiers plus hooks:

- **allow** (runs silently): reading files, `git status/diff/log/branch/add/commit/pull`,
  viewing PRs, running the local dev server
- **ask** (always prompts the human first):
  - `Edit` / `Write` — **the AI cannot change any code without permission**
  - `git checkout`, `git push`, `gh pr create`, `gh pr merge` — nothing leaves the
    machine without a yes
  - All ClickUp **write** actions (create/update/delete task, lists, folders,
    comments, move, merge) — **no ticket is filed/closed/deleted without a
    confirmation prompt**
- **deny** (never allowed): `rm -rf` (all spelling variants), force-push (both
  `--force` and `-f`)
- **hooks** (automation):
  - *PostToolUse*: after every AI edit to an `.html` file, a structural check runs
    (file must end with `</html>`, `<script>/<style>/<body>/<head>` tags must be
    balanced). If broken, the error is fed straight back to the AI to fix.
  - *Stop*: at session end, a reminder prints to keep the README feature list in
    sync with any feature change (a CLAUDE.md rule).

**Why:** this is the difference between "AI that does things to your project" and
"AI that proposes, human approves." Every risky category — code changes, pushes,
ticket writes, destructive commands — has an explicit human checkpoint or a hard block.

### Phase 9 — Skills (reusable QA workflows)
Two skills were created under `.claude/skills/`:

**Skill 1 — `/qa-test-cases <feature>`** (test case generator):
1. Reads the actual code (`index.html`) and the module docs for expected behavior
2. Generates a test suite in a fixed **10-column matrix**
   (Sr.No. / Area / Category / Scenario / Description / Steps / Expected Result /
   Comments / Results / Tested Version)
3. Covers happy path, edge cases, negatives, both themes, mobile width, refresh
   persistence, and date edge cases
4. Files to ClickUp **only after user confirmation** (respecting the settings.json
   guard rails)

**Skill 2 — `/qa-bug-report <description>`** (bug ticket creator):
1. Classifies the report first: real bug vs enhancement vs question
2. Writes a standardized ClickUp task — prerequisites, reproduction steps,
   expected vs actual results, build/device details, attachments
3. Creates the ClickUp task **only after user confirmation** (ask-first guard rail)

**Why:** a skill turns a repeatable QA process into a one-line command with a
guaranteed output format — consistent test cases and bug tickets regardless of who
runs it or when. Skills are committed to the repo, so every teammate (and every
future session) gets them automatically.

### Phase 10 — Ship features through the workflow
Two features were built and shipped, each as its own branch + PR:
- **Due dates** (date picker, 📅 badge, ⏰ overdue flag only after the date passes)
- **Live search** (case-insensitive, combines with filters, Esc clears)

Each was verified in the browser before merge, and the README was updated in the
same PR (per the CLAUDE.md rule). Both are live on the deployed site.

---

## 5. Connection Processes — Quick Reference

### GitHub (machine ↔ repo)
```
gh auth login                     # one-time: authenticate the GitHub CLI
git clone <repo-url>              # download the repo
git push / git pull               # sync changes up / down
```
If the repo belongs to another account/org: owner adds you as **collaborator**
(Repo → Settings → Collaborators) and you accept the invitation.

### Any MCP connector (ClickUp, Figma, Slack, …)
```
Claude app → Settings → Connectors
  ├── Button says "Connect"  → self-serve: click, OAuth login, done
  └── Button says "Request"  → goes to workspace admin → after approval, Connect + OAuth
```
Then verify with a harmless read (e.g., "list my ClickUp spaces").

### GitHub Pages (repo → live URL)
```
Repo → Settings → Pages → Branch: main, folder: / (root) → Save
→ live at https://<owner>.github.io/<repo>/ within ~1 minute
→ redeploys automatically on every merge to main
```

### Claude GitHub App (@claude bot on issues and PRs) — setup flow
Not yet installed in this POC (listed in Next Steps); the setup process is:

1. Open a terminal in a clone of the repo and run `claude`, then type:
   `/install-github-app`
2. A guided wizard starts:
   - Choose the repository to install on
   - Authorize the **Claude GitHub App** in the browser window it opens
   - Provide the AI credential: either reuse an existing Claude Pro/Max
     subscription (OAuth token) or an Anthropic API key — stored as a repo
     secret (`ANTHROPIC_API_KEY`), never in code
3. The wizard opens a PR adding `.github/workflows/claude.yml` — review and merge it.
4. Done. Total time ≈ 10–15 minutes.

What it enables after setup:
- Comment `@claude fix this` on an issue → Claude writes the fix and opens a PR
- Comment `@claude review this` on a PR → Claude reviews the diff and leaves comments
- Comment `@claude <any change request>` on a PR → Claude pushes to that PR's branch

How it works: each `@claude` mention triggers a **GitHub Actions** run that executes
Claude Code against the repo in GitHub's cloud — no laptop needed, and it follows the
repo's CLAUDE.md rules just like a local session.

---

## 6. The Workflow in One Picture

```
                    ┌─────────────────────────────────────────────┐
                    │                 HUMAN (QA)                  │
                    │   approves edits, pushes, PRs, tickets      │
                    └──────────────────────┬──────────────────────┘
                                           │ ask-first prompts
                                           ▼
   CLAUDE.md ────rules────►  ┌─────────────────────────┐
   docs/*.md ───details───►  │       CLAUDE CODE       │ ◄──── skills (/qa-test-cases)
   settings.json ─guards──►  │     (AI assistant)      │
                             └───────┬─────────┬───────┘
                                     │         │ MCP connectors
                          git branch │         ▼
                                     │   ┌──────────┐   ┌──────────┐
                                     ▼   │ ClickUp  │   │  Figma   │
                             ┌──────────┐│ tickets  │   │ designs  │
                             │  GitHub  │└──────────┘   └──────────┘
                             │ PR→merge │
                             └────┬─────┘
                                  ▼
                         GitHub Pages (live app)
```

---

## 7. Results

| Metric | Value |
|---|---|
| Working deployed app | ✅ live URL, auto-deploys on merge |
| Pull requests merged | 18+ (several done fully manually as practice) |
| AI rule files | 1 root CLAUDE.md + 5 module docs |
| Guard rails | 3-tier permissions + 2 automated hooks |
| Connectors verified | ClickUp (end-to-end), GitHub (CLI) |
| Custom skills | 2 (`/qa-test-cases`, `/qa-bug-report`) |
| Company data used | **None** — fully isolated practice project |

---

## 8. How to Replicate This in Your Project

Anyone can rebuild this setup by combining this document (the process and the why)
with this repository (the reference files to copy).

### Prerequisites checklist
- [ ] **Claude Code** installed (desktop app or CLI) and signed in
- [ ] **git** installed (`git --version` works in a terminal)
- [ ] **GitHub CLI** authenticated: run `gh auth login` once
- [ ] A **GitHub account** with permission to create a repository
- [ ] A **ClickUp account** (or your team's tracker) — connector enabled in your
      Claude workspace (may require an admin request, see Section 5)

### Replication steps
1. **Create your repo** on GitHub (empty), clone it locally, open Claude Code in it.
2. **Copy the reference files from this repo** as starting templates:
   - `CLAUDE.md` → rewrite the rules for *your* project (structure, tech stack,
     conventions). Keep the format: short root file + Hard Rules + Nested docs line.
   - `docs/*.md` → replace with docs for your project's real modules.
   - `.claude/settings.json` → keep the allow/ask/deny skeleton; adjust the
     commands to your stack (e.g., `npm test` instead of `python3 -m http.server`).
   - `.claude/skills/` → copy both skills and edit the project-specific parts
     (file names to read, tracker to file into, output columns).
3. **⚠️ The one thing that MUST change:** the ClickUp rules in settings.json contain
   a connector ID (`mcp__<long-id>__clickup_*`) that is **specific to our workspace**.
   Get your own ID by connecting ClickUp in your Claude workspace and asking Claude:
   *"what is the tool name of the ClickUp create-task tool?"* — then replace the ID
   in every rule.
4. **Set up deployment** (optional, for web projects): Settings → Pages, per Section 5.
5. **Work only through PRs** from day one — branch, push, PR, merge (Section 4, Phase 3).
6. **Verify the guard rails**: in a fresh Claude session in the repo, ask Claude to
   edit a file — it must prompt for permission. Ask it to create a ClickUp task —
   it must prompt again. If either runs silently, re-check `.claude/settings.json`.

**Rule of thumb:** the *structure* (files, tiers, workflow) transfers to any project
unchanged; the *contents* (rules, commands, connector IDs, skill details) are always
project-specific.

## 9. Next Steps

1. **Bug workflow**: reproduce the one known live bug ("Clear completed" button does
   nothing — its click handler is overwritten by the filter-pill handler), file it to
   ClickUp through the ask-first flow, fix it via PR, verify, close the ticket.
2. **Claude GitHub App** (`/install-github-app`): enable `@claude` comments on
   issues/PRs so the AI can fix bugs and review PRs directly from GitHub (~15 min setup).
3. **Branch protection** on `main`: require PRs at the platform level, so the
   workflow is enforced for everyone, not just for the AI.
4. **Figma connector**: connect and trial a design-vs-implementation review.
5. **Apply to real repos**: replicate this scaffolding (CLAUDE.md, settings.json,
   skills) on the QA automation repos after their GitLab → GitHub migration.
