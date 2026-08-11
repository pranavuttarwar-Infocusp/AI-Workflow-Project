# TaskPulse — AI-Workflow-Project

> Agent instructions for ANY AI coding tool (Claude Code, Cursor, Gemini CLI, Codex, ...).
> Tools that look for their own file (e.g. CLAUDE.md) are pointed here.

> A single-file, dependency-free task tracker. The entire app lives in `index.html` —
> keep it that way.

## Project Structure
- `index.html` — the whole app: markup, styles (`<style>`), and logic (`<script>`) in one file
- `README.md` — user-facing docs; keep the feature list in sync with the app
- `LICENSE` — MIT
- `.gitignore` — macOS artifacts, logs, node_modules
- Main branch: `main`

## Tech Stack
- Plain HTML + CSS + vanilla JavaScript (ES6+)
- **No frameworks, no build step, no package manager, no network calls** — the app must
  always run by simply opening `index.html` in a browser
- Persistence: browser `localStorage` only

## Running & Verifying
- Open directly: `open index.html`
- Or serve locally: `python3 -m http.server 8080` → `http://localhost:8080`
- There is no test suite — verify changes by loading the page in a browser and
  exercising the changed behavior (add/toggle/delete tasks, filters, theme, shortcuts)

## Domain Glossary
- **Task**: `{ id, title, priority, done }` — `id` is `Date.now()` at creation
- **Priority**: `high` | `medium` | `low` — rendered as colored badges
- **Filter**: All / Pending / Done — view-only, never mutates the task list
- **Stats**: total, done, pending, completion % — always derived from the task array,
  never stored separately

## Hard Rules

### Architecture
- **NEVER add external dependencies** — no CDN scripts, no npm, no web fonts, no
  external images. Everything ships inside `index.html`.
- **NEVER split the app into multiple JS/CSS files.** One file is the product's design
  constraint, not an accident.
- All state lives in the `tasks` array + `localStorage`. Render is always a full
  re-render via `render()` — don't introduce partial-update paths.

### Styling
- **ALWAYS use the CSS variables** defined in `:root` (dark) and `body.light` (light)
  for colors — never hardcode hex values in component rules.
- Any new UI must look correct in **both themes**; toggle ☀️/🌙 to verify before
  committing.
- Respect the existing look: `--radius` for corners, `--surface`/`--border` for cards,
  responsive down to ~375px width (stats grid collapses at 520px).

### Storage
- **Namespace all localStorage keys** with `taskpulse.` (existing: `taskpulse.tasks`,
  `taskpulse.theme`).
- Wrap `localStorage` reads in try/catch and fall back to defaults — never let corrupt
  stored data break first render.

### Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Changes go through **feature branch → PR → merge** — don't commit directly to `main`
- Keep PRs small and single-purpose; describe the user-visible behavior in the PR body

### ClickUp integration
- Work driven by a ClickUp task must carry the **task ID** so ClickUp's GitHub
  integration links the PR and its Automations can move the task's status:
  - Branch name: `<type>/<task-id>-short-slug` (e.g. `feat/86d40enkv-remove-due-date`)
  - PR title: append `(#<task-id>)` (e.g. `feat: remove due date field (#86d40enkv)`)
  - PR body: include the full task URL (`https://app.clickup.com/t/<task-id>`)
- Status flow is automated in ClickUp: PR opened → *in review*, PR merged → *done*.
  Don't change these statuses manually when a PR exists.

### Documentation
- Any user-visible feature change must update the README feature list in the same PR
- New keyboard shortcuts must also be documented in the app footer

**Nested**: `docs/ui-layout.md`, `docs/state-storage.md`, `docs/rendering.md`, `docs/theming.md`, `docs/interactions.md` | **Updated**: 2026-07-27
