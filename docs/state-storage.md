# State & Storage — TaskPulse

> Covers the data model, persistence, and seed data in `index.html`'s `<script>` block.
> Parent conventions: root `CLAUDE.md`.

## Data Model
- Single source of truth: the `tasks` array (module-level `let`)
- Task shape: `{ id: number, title: string, priority: "high"|"medium"|"low", done: boolean }`
- `id` is `Date.now()` at creation — sufficient for a single-user, single-tab app
- New tasks are `unshift`ed (newest first); order is otherwise never re-sorted
- `filter` (`"all" | "pending" | "done"`) is view state only — it never mutates `tasks`

## Persistence
- Key: `taskpulse.tasks` (JSON-serialized array), written by `save()` after EVERY mutation
- `load()` reads once at startup; falls back to `seedTasks` if the key is missing OR
  JSON.parse throws
- Theme key: `taskpulse.theme` (see `docs/theming.md`)

## Seed Data
- Three demo tasks (one per priority, one pre-completed) so the app presents well on
  first load. Keep exactly one `done: true` seed so the stats/progress UI shows a
  non-zero state out of the box.

## Hard Rules
- **Namespace every localStorage key with `taskpulse.`** — no exceptions.
- **Every mutation of `tasks` must be followed by `save()` then `render()`** — no direct
  DOM patching, no deferred saves.
- **Wrap all localStorage reads in try/catch** and fall back to defaults. Corrupt or
  blocked storage (private browsing) must never break first render.
- Derived values (counts, completion %) are always computed from `tasks` at render time —
  NEVER stored.
- If the task shape gains a field, old stored tasks without it must still load — use
  defaults on read, don't migrate-in-place.
