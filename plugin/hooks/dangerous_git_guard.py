#!/usr/bin/env python3
"""AICC dangerous-git guard (PreToolUse on Bash).

Denies red-zone git operations (force push, hard reset, forced clean,
history rewrite, branch/tag deletion, protected-branch commit/push) unless
`aicc.git_safety.mode` is "permissive". In "strict" mode, yellow-zone
operations (commit/push/branch creation) surface an ask instead of flowing
through silently.

Robustness: green commands and non-git commands emit no opinion. Internal
errors fail safe to "ask" with the error as reason.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _aicc_common as common


def main():
    event = common.read_event()
    if event.get("tool_name") != "Bash":
        return
    command = (event.get("tool_input") or {}).get("command", "")
    if "git" not in command:
        return

    cwd = event.get("cwd") or os.getcwd()
    settings = common.load_settings(cwd)
    safety = settings["git_safety"]
    mode = safety.get("mode", "standard")

    sys.path.insert(0, os.path.join(common.plugin_root(), "scripts", "py"))
    import git_safety
    result = git_safety.classify(command, safety.get("protected_branches"), cwd=cwd)

    if result["zone"] == "red":
        if mode == "permissive":
            return  # user chose to disarm the guard
        common.emit(common.pretooluse_decision(
            "deny",
            "AICC git safety: destructive operation blocked:\n- %s\n"
            "Set aicc.git_safety.mode to \"permissive\" if you really intend this."
            % "\n- ".join(result["findings"])))
    elif result["zone"] == "yellow" and mode == "strict":
        common.emit(common.pretooluse_decision(
            "ask",
            "AICC git safety (strict mode): %s requires explicit confirmation."
            % ", ".join(result["findings"])))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        try:
            common.emit(common.pretooluse_decision(
                "ask", "AICC git safety internal error (fail-safe): %s" % exc))
        except Exception:
            pass
    sys.exit(0)
