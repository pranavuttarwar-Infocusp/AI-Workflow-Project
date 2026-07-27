# TaskPulse — AI-Workflow-Project

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

### Documentation
- Any user-visible feature change must update the README feature list in the same PR
- New keyboard shortcuts must also be documented in the app footer

**Updated**: 2026-07-27
