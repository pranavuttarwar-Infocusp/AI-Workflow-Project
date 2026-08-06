#!/bin/bash
# PreToolUse hook (gh pr create): shows the QA checklist right before a PR is created.
echo '{"systemMessage": "🧪 QA GATE before this PR: 1) Loaded the app and exercised the changed flows? 2) Checked BOTH themes (☀️/🌙)? 3) Checked mobile width (375px)? 4) Refresh persistence still works? 5) README feature list updated? 6) Consider /qa-test-cases for the change."}'
