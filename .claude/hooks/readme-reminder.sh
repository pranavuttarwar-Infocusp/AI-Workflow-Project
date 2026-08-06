#!/bin/bash
# Stop hook: end-of-session reminder to keep the README feature list in sync (AGENTS.md rule).
echo '{"systemMessage": "Reminder: if this session changed app features, update the README feature list in the same PR (AGENTS.md rule)."}'
