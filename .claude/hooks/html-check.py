#!/usr/bin/env python3
# PostToolUse hook (Write|Edit): structural sanity check for HTML files.
# Reads the hook JSON on stdin; if the edited file is *.html, verifies the file
# still ends with </html> and has balanced script/style/body/head tags.
# Exit 2 feeds the problem back to Claude so it fixes the breakage immediately.
import json
import sys

payload = json.load(sys.stdin)
tool_input = payload.get("tool_input", {})
tool_response = payload.get("tool_response", {})
file_path = tool_input.get("file_path") or tool_response.get("filePath") or ""

if not file_path.endswith(".html"):
    sys.exit(0)

try:
    with open(file_path) as handle:
        text = handle.read()
except OSError:
    sys.exit(0)

problems = []
if not text.rstrip().endswith("</html>"):
    problems.append("file does not end with </html> (truncated?)")
for tag in ("script", "style", "body", "head"):
    opens = text.count("<" + tag + ">") + text.count("<" + tag + " ")
    closes = text.count("</" + tag + ">")
    if opens != closes:
        problems.append("unbalanced <%s> tags (%d open, %d close)" % (tag, opens, closes))

if problems:
    print("HTML CHECK FAILED: " + "; ".join(problems))
    sys.exit(2)
