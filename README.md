# TaskPulse ⚡

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Vanilla JS](https://img.shields.io/badge/built%20with-vanilla%20JS-f7df1e.svg)

A tiny, self-contained task tracker with a live stats dashboard. No build step,
no dependencies — the entire app lives in one HTML file.

## Features

- ➕ Add tasks with a priority (High / Medium / Low) and an optional due date
- 📅 Due-date badge on each task; a task is flagged **overdue only after its due date has passed** (due today = not overdue). Works whether the task is added via the Add button or the Enter key
- 🔎 Live search across task titles — **case-insensitive**; clearing the search box immediately restores the full list
- ✅ Toggle done / pending with one click
- 🗑️ Delete individual tasks, or **Clear completed** in one click
- 🔍 Filter by All / Pending / Done
- 📊 Live stats: total, done, pending, completion rate + animated progress bar
- 🌗 Light / dark theme toggle (persists across reloads)
- ⌨️ Keyboard shortcuts: <kbd>Enter</kbd> adds a task, <kbd>Esc</kbd> clears the input
- 💾 Persists in the browser via `localStorage` (survives refresh)
- 📱 Responsive down to mobile widths

## Running it

Just open the file in any browser:

```sh
open index.html
```

Or serve it locally:

```sh
python3 -m http.server 8080
# → http://localhost:8080
```

## Tech

Plain HTML + CSS + vanilla JavaScript. No frameworks, no build tools, no
network calls — everything runs and stays in your browser.

## Project structure

```
.
├── index.html   # the entire app (markup, styles, logic)
├── README.md
├── LICENSE      # MIT
└── .gitignore
```

docs: add author by pranav

## License

[MIT](LICENSE)
