# Interactions & Shortcuts — TaskPulse

> Covers user actions and keyboard handling in `index.html`. Parent conventions: root
> `CLAUDE.md`.

## Actions
- **Add**: Add button click OR <kbd>Enter</kbd> in the input. Empty/whitespace-only
  titles are rejected silently (no error UI). Input clears after add; priority select
  keeps its value.
- **Toggle done**: click the checkbox on a row
- **Delete**: click ✕ on a row — immediate, no confirmation (by design; the app is
  low-stakes)
- **Clear completed**: removes all `done` tasks at once; button is `disabled` when
  there are none
- **Filter**: All / Pending / Done pills — exactly one active at a time

## Keyboard Shortcuts
| Key | Context | Effect |
|-----|---------|--------|
| <kbd>Enter</kbd> | task input focused | add task |
| <kbd>Esc</kbd> | task input focused | clear input + blur |

## Hard Rules
- **Every new shortcut must be documented in the app footer** (styled `<kbd>` chips)
  AND in the README feature list, in the same PR.
- Shortcuts attach to the input (or a specific element) — no global `document`-level
  key handlers that could fight browser/OS behavior.
- Destructive bulk actions (like Clear completed) must be disabled when they would do
  nothing — a no-op button that looks tappable reads as broken.
- All mutations flow through the standard path: mutate `tasks` → `save()` → `render()`
  (see `docs/rendering.md`). Event handlers contain no rendering logic of their own.
