# Rendering — TaskPulse

> Covers `render()` / `renderStats()` and the full re-render model in `index.html`.
> Parent conventions: root `CLAUDE.md`.

## Render Model
- **Full re-render, always.** `render()` clears `#taskList` (`innerHTML = ""`) and
  rebuilds every visible row from `tasks`, then calls `renderStats()`.
- `renderStats()` recomputes total / done / pending / completion %, updates the four
  stat cards, the progress fill width + label, and the Clear-completed disabled state.
- Row event handlers (toggle, delete) are attached per-row at build time — safe because
  rows are rebuilt on every change.

## Flow
```
user action → mutate tasks → save() → render() → renderStats()
```

## Empty State
- When the active filter yields zero rows, an `.empty` block (🎉 + hint) is rendered
  inside the list instead of rows.

## Hard Rules
- **NEVER introduce partial DOM updates** (patching a single row, toggling classes on
  existing nodes as a persistence mechanism). The app's simplicity depends on the
  one-way `state → render` flow.
- **Task titles must be inserted via `textContent`**, never interpolated into
  `innerHTML` — user input must not be parseable as HTML (XSS).
- Static row scaffolding may use `innerHTML`; anything user-authored may not.
- `render()` must remain cheap enough to call on every interaction — if a change makes
  it expensive (e.g. hundreds of rows with heavy per-row work), fix the work, not the
  render model.
