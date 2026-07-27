# TaskPulse ⚡

A tiny, self-contained task tracker with a live stats dashboard. Built as a
presentable demo project — no build step, no dependencies, just one HTML file.

## Features

- ➕ Add tasks with a priority (High / Medium / Low)
- ✅ Toggle done / pending with one click
- 🗑️ Delete tasks
- 🔍 Filter by All / Pending / Done
- 📊 Live stats: total, done, pending, completion rate + animated progress bar
- 💾 Persists in the browser via `localStorage` (survives refresh)
- 🌙 Polished dark UI, responsive down to mobile widths

## Running it

Just open the file in any browser:

```
open index.html
```

Or serve it locally:

```
python3 -m http.server 8080
# → http://localhost:8080
```

## Tech

Plain HTML + CSS + vanilla JavaScript. No frameworks, no build tools.

## Project structure

```
DummyProject-TaskPulse/
├── index.html   # the entire app (markup, styles, logic)
└── README.md
```
