# Theming — TaskPulse

> Covers the dark/light theme system in `index.html`. Parent conventions: root `CLAUDE.md`.

## How It Works
- **Dark is the default**: variables defined on `:root`
- **Light is an override**: `body.light { ... }` redefines only the variables that
  differ (`--bg`, `--surface`, `--surface-2`, `--border`, `--text`, `--text-dim`,
  `--accent`, `--accent-soft`)
- Semantic colors (`--green`, `--amber`, `--red`) are shared across both themes
- Toggle: `#themeToggle` button in the header — shows ☀️ in dark mode (tap for light),
  🌙 in light mode (tap for dark)
- Persistence: `taskpulse.theme` in localStorage (`"light"` | `"dark"`); `applyTheme()`
  runs at startup before first paint of interactions

## Hard Rules
- **A theme is ONLY a set of CSS variable values.** Never write
  `body.light .some-component { ... }` component overrides — if a component needs a
  different color per theme, it's using the wrong variable (or a new variable belongs
  in both blocks).
- Any new variable added to `:root` that encodes a *surface, border, or text* color
  MUST get a light-mode value in `body.light`.
- **Verify every UI change in both themes before committing** — toggle ☀️/🌙 and check
  contrast (dim text on light surfaces is the usual regression).
- The toggle icon shows the theme you'll GET, not the one you're in — keep it that way.
