#!/usr/bin/env python3
"""Regression test for the Codex flat projection + .codex/ hooks bundle.

Codex (>= v0.117) runs lifecycle hooks whose stdin/stdout contract matches
Claude Code's, so codex_projection.py emits a self-contained .codex/
enforcement bundle. This test guards two things that must not silently
regress:

  1. STRUCTURE — the bundle ships hooks.json (SessionStart + PreToolUse +
     PostToolUse on ^Bash$), the hook scripts, their scripts/py deps, and
     settings.json; and the package wording no longer claims "no hooks".
  2. ENFORCEMENT — a projected hook script, run as a project-local install
     (CLAUDE_PLUGIN_ROOT UNSET, so it must self-resolve its root, settings,
     and scripts/py deps from __file__), actually DENIES a red-zone git
     command with the Codex/Claude-shared permissionDecision envelope, and
     stays silent on a green command.

Run: python3 test_codex_projection.py   (exit 0 = pass)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import codex_projection


def _check(cond, label):
    if not cond:
        raise AssertionError(label)
    print("  ok: %s" % label)


def test_structure(out_dir):
    codex_dir = os.path.join(out_dir, ".codex")
    _check(os.path.isdir(codex_dir), ".codex/ bundle exists")

    hooks = json.load(open(os.path.join(codex_dir, "hooks.json"), encoding="utf-8"))
    events = hooks["hooks"]
    _check(set(events) == {"SessionStart", "PreToolUse", "PostToolUse"},
           "hooks.json declares SessionStart + PreToolUse + PostToolUse")
    pre_cmds = " ".join(h["command"] for h in events["PreToolUse"][0]["hooks"])
    _check(events["PreToolUse"][0]["matcher"] == "^Bash$",
           "PreToolUse matcher is ^Bash$")
    _check("pre_commit_gate.py" in pre_cmds and "dangerous_git_guard.py" in pre_cmds,
           "PreToolUse wires commit gate + git guard")

    for rel in ("hooks/_aicc_common.py", "hooks/pre_commit_gate.py",
                "hooks/dangerous_git_guard.py", "hooks/session_inject.py",
                "hooks/post_tool_audit.py", "scripts/py/git_safety.py",
                "scripts/py/summary_validator.py", "settings.json"):
        _check(os.path.isfile(os.path.join(codex_dir, rel)), "bundle ships %s" % rel)

    agents = open(os.path.join(out_dir, "AGENTS.md"), encoding="utf-8").read().lower()
    _check("no hooks" not in agents and "advisory mode" not in agents,
           "AGENTS.md no longer claims 'no hooks' / 'advisory mode'")
    _check(".codex/" in agents and "hooks" in agents,
           "AGENTS.md points at the .codex/ hooks bundle")


def _run_guard(out_dir, command):
    """Run the PROJECTED git guard as a project-local install would:
    CLAUDE_PLUGIN_ROOT unset, so it self-resolves root from __file__."""
    script = os.path.join(out_dir, ".codex", "hooks", "dangerous_git_guard.py")
    event = json.dumps({
        "hook_event_name": "PreToolUse", "tool_name": "Bash",
        "tool_input": {"command": command}, "cwd": "/tmp",
    })
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
    proc = subprocess.run([sys.executable, script], input=event,
                          capture_output=True, text=True, env=env, timeout=30)
    return proc.stdout.strip()


def test_enforcement(out_dir):
    out = _run_guard(out_dir, "git push --force origin main")
    _check(out, "force-push produces a decision (self-resolved with env unset)")
    decision = json.loads(out)["hookSpecificOutput"]
    _check(decision["permissionDecision"] == "deny",
           "force-push is DENIED via the Codex/Claude permissionDecision envelope")

    _check(_run_guard(out_dir, "git reset --hard HEAD~3"),
           "hard-reset also produces a deny decision")
    _check(_run_guard(out_dir, "git status") == "",
           "green 'git status' stays silent (no opinion)")


def main():
    out_dir = tempfile.mkdtemp(prefix="aicc-codex-test-")
    try:
        codex_projection.run(PLUGIN_ROOT, out_dir)
        print("structure:")
        test_structure(out_dir)
        print("enforcement:")
        test_enforcement(out_dir)
        print("PASS: codex projection emits an enforcing .codex/ bundle")
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
