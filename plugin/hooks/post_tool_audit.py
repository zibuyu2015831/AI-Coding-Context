#!/usr/bin/env python3
"""AICC telemetry (PostToolUse on Bash).

Appends one minimal JSONL record per Bash call so that AICC effectiveness
claims can eventually rest on real data instead of assertions (the
clone-form framework's quantified claims were withdrawn for lack of
exactly this evidence).

Record: {ts, tool, cwd, git_cmd, dev_docs_touched, interrupted}
Destination: ${CLAUDE_PLUGIN_DATA}/telemetry.jsonl when set, else
~/.claude/aicc/telemetry.jsonl. No command text or file contents are
recorded — flags only.

Fail-open: any error is swallowed; this hook never blocks or breaks a
session.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _aicc_common as common


def data_dir():
    root = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not root:
        root = os.path.join(os.path.expanduser("~"), ".claude", "aicc")
    os.makedirs(root, exist_ok=True)
    return root


def main():
    event = common.read_event()
    if event.get("tool_name") != "Bash":
        return
    tool_input = event.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    response = event.get("tool_response")
    if not isinstance(response, dict):
        response = {}
    git_match = re.search(r"\bgit\s+(?:-[^\s]+\s+)*([a-z-]+)", command)
    record = {
        "ts": int(time.time()),
        "tool": "Bash",
        "cwd": event.get("cwd", ""),
        "git_cmd": git_match.group(1) if git_match else None,
        "dev_docs_touched": "dev_docs/" in command,
        "interrupted": bool(response.get("interrupted", False)),
    }
    path = os.path.join(data_dir(), "telemetry.jsonl")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open: telemetry must never break a session
    sys.exit(0)
