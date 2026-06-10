#!/usr/bin/env python3
"""AICC commit gate (PreToolUse on Bash).

Fires on every Bash call; acts only when the command is a `git commit`.
Validates AICC-managed docs (dev_docs/**/*.md) that are part of the commit:
  - frontmatter summary compliance (scripts/py/summary_validator.py)
  - main-doc section contract (scripts/py/contract_check.py)

Decision policy (git_safety.commit_gate setting):
  "deny" -> block the commit with the failure list
  "ask"  -> surface the failures and let the user confirm (default)
  "off"  -> gate disabled, no opinion

Robustness: a pass or a non-commit command emits no opinion (empty output,
exit 0) so normal permission flow applies. Internal errors fail safe to
"ask" ("deny" if the gate is set to deny), never crash the session.
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _aicc_common as common

GIT_COMMIT_RE = re.compile(r"\bgit\b[^|;&]*?\bcommit\b")


def changed_doc_files(cwd, command):
    """Markdown files under dev_docs/ that this commit would include."""
    def git_lines(args):
        try:
            out = subprocess.run(
                ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=15
            )
            return [l.strip() for l in out.stdout.splitlines() if l.strip()]
        except (OSError, subprocess.SubprocessError):
            return []

    files = git_lines(["diff", "--cached", "--name-only", "--diff-filter=ACM", "--", "*.md"])
    # `git commit -a` / explicit pathspecs commit unstaged changes too.
    if re.search(r"\bcommit\b.*(\s-a\b|\s-am\b|\s--all\b)", command) or not files:
        files += git_lines(["diff", "--name-only", "--diff-filter=ACM", "HEAD", "--", "*.md"])
    seen, result = set(), []
    for f in files:
        if f.startswith("dev_docs/") and f not in seen:
            seen.add(f)
            result.append(f)
    return result


def validate(cwd, files):
    """Run the validators; return a list of English failure strings."""
    scripts = os.path.join(common.plugin_root(), "scripts", "py")
    sys.path.insert(0, scripts)
    import contract_check
    import summary_validator

    failures = []
    for rel in files:
        path = os.path.join(cwd, rel)
        if not os.path.isfile(path):
            continue
        report = summary_validator.validate_file(path, repo_root=cwd)
        for err in report["errors"]:
            failures.append("%s: %s" % (rel, err))
        if os.path.basename(rel) == "AI_Coding_Context.md":
            for issue in contract_check.check_main_doc(path)["issues"]:
                failures.append("%s: %s" % (rel, issue))
    return failures


def main():
    event = common.read_event()
    if event.get("tool_name") != "Bash":
        return
    command = (event.get("tool_input") or {}).get("command", "")
    if not GIT_COMMIT_RE.search(command):
        return

    cwd = event.get("cwd") or os.getcwd()
    settings = common.load_settings(cwd)
    gate = settings["git_safety"].get("commit_gate", "ask")
    if gate == "off":
        return

    files = changed_doc_files(cwd, command)
    if not files:
        return

    failures = validate(cwd, files)
    if not failures:
        return  # pass: no opinion, normal permission flow applies

    shown = failures[:8]
    if len(failures) > len(shown):
        shown.append("... and %d more" % (len(failures) - len(shown)))
    reason = (
        "AICC commit gate: %d doc validation failure(s) in this commit:\n- %s\n"
        "Fix the docs, or set aicc.git_safety.commit_gate to \"off\" to disable the gate."
        % (len(failures), "\n- ".join(shown))
    )
    decision = "deny" if gate == "deny" else "ask"
    common.emit(common.pretooluse_decision(decision, reason))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail safe, never crash the session
        try:
            gate = common.load_settings().get("git_safety", {}).get("commit_gate", "ask")
            decision = "deny" if gate == "deny" else "ask"
            common.emit(common.pretooluse_decision(
                decision, "AICC commit gate internal error (fail-safe): %s" % exc))
        except Exception:
            pass
    sys.exit(0)
