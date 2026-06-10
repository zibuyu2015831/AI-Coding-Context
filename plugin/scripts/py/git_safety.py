#!/usr/bin/env python3
"""AICC git safety classifier: red / yellow / green zones.

Red zone (destructive or shared-history-rewriting; the dangerous-git guard
denies these unless git_safety.mode is "permissive"):
  force push, hard reset, forced clean, history rewrite (rebase,
  filter-branch), forced branch deletion, remote branch/tag deletion,
  and commit/push targeting a protected branch.

Yellow zone (needs explicit user intent; "strict" mode asks):
  commit, push, branch creation.

Everything else is green (status, log, diff, add, pull, local checkout).

Usage:
  python3 git_safety.py --validate-command "git push --force" [--json]
  python3 git_safety.py --check-branch [--json]
Exit code: 0 green, 1 red, 2 yellow.
"""

import argparse
import json
import re
import subprocess
import sys

DEFAULT_PROTECTED = ["main", "master", "production"]

RED_PATTERNS = (
    (r"\bpush\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b)", "force push rewrites shared history"),
    (r"\breset\b.*\s--hard\b", "hard reset discards uncommitted work"),
    (r"\bclean\b.*\s-[a-zA-Z]*f", "forced clean deletes untracked files"),
    (r"\bbranch\b.*\s-D\b", "forced branch deletion discards unmerged work"),
    (r"\bpush\b.*\s--delete\b", "remote branch/tag deletion"),
    (r"\bpush\b.*\s+\S+\s+:\S+", "remote ref deletion (push :ref)"),
    (r"\btag\b.*\s-d\b", "tag deletion"),
    (r"\bfilter-branch\b", "history rewrite"),
    (r"\brebase\b", "rebase rewrites history; do it manually if intended"),
)
YELLOW_PATTERNS = (
    (r"\bcommit\b", "commit"),
    (r"\bpush\b", "push"),
    (r"\b(checkout|switch)\b.*\s-[bc]\b", "branch creation"),
)


def current_branch(cwd=None):
    try:
        out = subprocess.run(["git", "branch", "--show-current"],
                             cwd=cwd, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None  # empty on detached HEAD
    except (OSError, subprocess.SubprocessError):
        return None


def is_protected(branch, protected):
    if not branch:
        return False
    for pattern in protected:
        if pattern.endswith("/*"):
            if branch.startswith(pattern[:-1]):
                return True
        elif branch == pattern:
            return True
    return False


def classify(command, protected=None, cwd=None):
    """Return {"zone": "red"|"yellow"|"green", "findings": [reasons]}."""
    protected = protected or DEFAULT_PROTECTED
    if not re.search(r"\bgit\b", command):
        return {"zone": "green", "findings": []}

    findings = [reason for pattern, reason in RED_PATTERNS
                if re.search(pattern, command)]

    # Direct push to a protected branch.
    push_match = re.search(r"\bpush\b\s+(?:-[^\s]+\s+)*(\S+)\s+(\S+)", command)
    if push_match and is_protected(push_match.group(2).split(":")[-1], protected):
        findings.append("push targets protected branch '%s'" % push_match.group(2))

    # Commit while standing on a protected branch.
    if re.search(r"\bcommit\b", command):
        branch = current_branch(cwd)
        if is_protected(branch, protected):
            findings.append("commit on protected branch '%s' — create a feature branch" % branch)

    if findings:
        return {"zone": "red", "findings": findings}

    for pattern, label in YELLOW_PATTERNS:
        if re.search(pattern, command):
            return {"zone": "yellow", "findings": [label]}
    return {"zone": "green", "findings": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Classify git commands by safety zone.")
    parser.add_argument("--validate-command", metavar="CMD",
                        help="classify a git command string")
    parser.add_argument("--check-branch", action="store_true",
                        help="report whether the current branch is protected")
    parser.add_argument("--protected", default=",".join(DEFAULT_PROTECTED),
                        help="comma-separated protected branch list/globs")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)
    protected = [p.strip() for p in args.protected.split(",") if p.strip()]

    if args.check_branch:
        branch = current_branch()
        result = {"branch": branch, "protected": is_protected(branch, protected)}
        print(json.dumps(result, indent=2) if args.json else
              "branch %s: %s" % (branch, "PROTECTED" if result["protected"] else "ok"))
        return 1 if result["protected"] else 0

    if not args.validate_command:
        parser.error("one of --validate-command or --check-branch is required")
    result = classify(args.validate_command, protected)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("zone: %s" % result["zone"])
        for finding in result["findings"]:
            print("  - %s" % finding)
    return {"green": 0, "red": 1, "yellow": 2}[result["zone"]]


if __name__ == "__main__":
    sys.exit(main())
