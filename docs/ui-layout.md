# UI & Layout — TaskPulse

> Covers the markup structure and CSS conventions in `index.html` (the `<style>` block
> and `<body>` markup). Parent conventions: root `CLAUDE.md`.

## Component Map (top to bottom)
- **Header**: logo tile (⚡ gradient), app title + subtitle, theme toggle button (right-aligned)
- **Stats grid**: 4 cards — Total / Done / Pending / Completion % (`.stat.total|.done|.pending|.rate`)
- **Progress bar**: animated fill + right-aligned label (`X of Y tasks complete`)
- **Input row**: text input + priority `<select>` + Add button
- **Filters row**: All / Pending / Done pills + right-aligned Clear completed button
- **Task list**: `<ul id="taskList">` of `.task` cards
- **Footer**: persistence note + keyboard shortcut hints (`<kbd>` chips)

## Layout Rules
- Content column: `.container { max-width: 720px }`, centered
- Stats: CSS grid `repeat(4, 1fr)`; collapses to `repeat(2, 1fr)` below 520px
- Input row and task cards: flexbox; task title takes `flex: 1`
- Right-aligned items inside flex rows use `margin-left: auto` (theme toggle, Clear completed)

## Hard Rules
- **ALWAYS use CSS variables for colors** (`--bg`, `--surface`, `--surface-2`, `--border`,
  `--text`, `--text-dim`, `--accent`, `--green`, `--amber`, `--red`). Hardcoded hex is
  allowed ONLY for the logo/progress gradients and priority badge tints.
- **Corner radii come from `--radius`** (cards, inputs, buttons) or `99px` (pills, toggles).
- New components must be verified at 375px width (iPhone SE) — nothing may overflow
  horizontally.
- Task rows animate in via the `slideIn` keyframe — reuse it for any new list-item type.
- Interactive elements need a hover state (existing pattern: brightness filter on solid
  buttons, border-color change on outlined ones).
