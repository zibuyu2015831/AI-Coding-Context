#!/usr/bin/env python3
"""Project the AICC plugin into a flat Codex package (spec §7).

The projection is a pure transformation of the SAME plugin sources:

  - skills/<name>/        -> dist/codex/aicc-<name>/   (flat, prefixed)
  - /aicc:<name> mentions -> aicc-<name>
  - ${CLAUDE_PLUGIN_ROOT}/x -> ../x (package-relative)
  - shared references/, scripts/py/, bin/, agents/ copied alongside
  - AGENTS.md index generated at the package root

Codex (>= v0.117) supports lifecycle hooks whose stdin/stdout contract
matches Claude Code's: tool_name / tool_input.command / cwd on stdin,
hookSpecificOutput.permissionDecision(+Reason) on stdout, and a
CLAUDE_PLUGIN_ROOT env alias. The AICC hook scripts are therefore
already Codex-compatible at the I/O level, so the projection ALSO emits a
self-contained `.codex/` enforcement bundle (hooks.json + the hook
scripts + their Python deps + settings.json) that the user installs at
their repo root. Once trusted via `/hooks`, the commit gate and
git-safety guard run automatically — same enforcement as the plugin.

Codex hook interception still has gaps (notably some shell paths), so
every skill keeps an advisory note pointing at the `bin/aicc-*`
validators to run by hand as a backstop.

Run via `python3 build.py --codex` (or standalone).
"""

import json
import os
import re
import shutil

ADVISORY_NOTE = """\
> **Codex enforcement note.** AICC ships a `.codex/` hooks bundle (Codex
> >= v0.117): copy it to your repo root and run `/hooks` to trust it, and
> the commit gate + git-safety guard below run automatically (PreToolUse).
> Codex hook interception has gaps, so for any command it does not catch,
> run the validators yourself:
> - before any commit: `bin/aicc-summary-validate --dir dev_docs/ --recursive`
>   and `bin/aicc-doc-health --mode quick`
> - before any risky git command: `bin/aicc-git-safety --validate-command "<cmd>"`
>   (red zone = do not run it)
"""

# Hook scripts copied verbatim (no markdown transform) into .codex/hooks/.
HOOK_SCRIPTS = (
    "_aicc_common.py",
    "session_inject.py",
    "pre_commit_gate.py",
    "dangerous_git_guard.py",
    "post_tool_audit.py",
)

# Codex hooks.json: same event model as the plugin. Commands resolve the
# script from the repo root so the bundle works as a project-local
# `.codex/` install (CLAUDE_PLUGIN_ROOT is unset there; each script
# self-locates its root from __file__, i.e. <repo>/.codex/).
CODEX_HOOKS_JSON = {
    "hooks": {
        "SessionStart": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/session_inject.py"',
                        "timeout": 30,
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "^Bash$",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/pre_commit_gate.py"',
                        "timeout": 30,
                    },
                    {
                        "type": "command",
                        "command": 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/dangerous_git_guard.py"',
                        "timeout": 30,
                    },
                ],
            }
        ],
        "PostToolUse": [
            {
                "matcher": "^Bash$",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/post_tool_audit.py"',
                        "timeout": 30,
                    }
                ],
            }
        ],
    }
}

CODEX_BUNDLE_README = """\
# AICC enforcement bundle for Codex

Codex (>= v0.117) runs lifecycle hooks whose stdin/stdout contract matches
the AICC plugin's, so these hooks are the SAME scripts the Claude Code
plugin ships — enforcement parity, not a reimplementation.

## Install

1. Copy this `.codex/` directory to the root of your project repository.
2. In Codex, run `/hooks` and trust the three AICC hooks (Codex records
   trust against each hook's hash; re-trust after updates).
3. Python 3 must be on PATH (the hooks shell out to `python3`).

## What runs

- **PreToolUse / `^Bash$`** — `pre_commit_gate.py` blocks a `git commit`
  that includes AICC docs failing frontmatter / contract checks;
  `dangerous_git_guard.py` denies red-zone git (force-push, hard-reset,
  history rewrite, protected-branch writes). Policy comes from
  `settings.json` (`aicc.git_safety.{mode,commit_gate}`).
- **PostToolUse / `^Bash$`** — `post_tool_audit.py` appends minimal,
  fail-open telemetry.
- **SessionStart** — `session_inject.py` surfaces a dev_docs/ health
  snapshot.

## Caveat

Codex hook interception has gaps on some shell paths; the gates are a
guardrail, not a complete boundary. The flat package's `bin/aicc-*`
validators remain the manual backstop (see `../AGENTS.md`).
"""


def transform_markdown(text, skill_names):
    for name in skill_names:
        text = text.replace("/aicc:%s" % name, "aicc-%s" % name)
    text = text.replace("/aicc:", "aicc-")  # generic mentions
    text = text.replace("${CLAUDE_PLUGIN_ROOT}/", "../")
    text = text.replace(
        "is enforced, not advisory",
        "is enforced by hooks (install the .codex/ bundle); otherwise advisory")
    return text


def inject_note(skill_md_text):
    """Insert the advisory note right after the H1 (or frontmatter)."""
    match = re.search(r"^# .+$", skill_md_text, re.MULTILINE)
    if match:
        pos = match.end()
        return skill_md_text[:pos] + "\n\n" + ADVISORY_NOTE + skill_md_text[pos:]
    return ADVISORY_NOTE + "\n" + skill_md_text


def copy_transformed(src, dst, skill_names, is_skill_md=False):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if src.endswith((".md", ".json", ".py")):
        text = open(src, "r", encoding="utf-8").read()
        text = transform_markdown(text, skill_names)
        if is_skill_md:
            text = inject_note(text)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        shutil.copy2(src, dst)


def project_enforcement(plugin_root, out_dir):
    """Emit the self-contained `.codex/` hooks bundle (enforcement parity).

    Hook scripts and their Python deps are copied VERBATIM (no markdown
    transform) because they self-locate via __file__ and rely on the
    Codex/Claude-shared stdin/stdout contract.
    """
    codex_dir = os.path.join(out_dir, ".codex")
    files = 0

    # Hook scripts.
    hooks_dst = os.path.join(codex_dir, "hooks")
    os.makedirs(hooks_dst, exist_ok=True)
    for fname in HOOK_SCRIPTS:
        src = os.path.join(plugin_root, "hooks", fname)
        dst = os.path.join(hooks_dst, fname)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)
        files += 1

    # Python deps the hooks import (plugin_root()/scripts/py resolves to
    # .codex/scripts/py via the script's __file__ fallback).
    scripts_src = os.path.join(plugin_root, "scripts", "py")
    scripts_dst = os.path.join(codex_dir, "scripts", "py")
    os.makedirs(scripts_dst, exist_ok=True)
    for fname in sorted(os.listdir(scripts_src)):
        if fname.endswith(".py"):
            shutil.copy2(os.path.join(scripts_src, fname),
                         os.path.join(scripts_dst, fname))
            files += 1

    # Settings (aicc block) + hooks.json + install README.
    shutil.copy2(os.path.join(plugin_root, "settings.json"),
                 os.path.join(codex_dir, "settings.json"))
    files += 1
    with open(os.path.join(codex_dir, "hooks.json"), "w", encoding="utf-8") as fh:
        json.dump(CODEX_HOOKS_JSON, fh, indent=2)
        fh.write("\n")
    files += 1
    with open(os.path.join(codex_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(CODEX_BUNDLE_README)
    files += 1
    return files


def run(plugin_root, out_dir):
    skills_dir = os.path.join(plugin_root, "skills")
    skill_names = sorted(d for d in os.listdir(skills_dir)
                         if os.path.isdir(os.path.join(skills_dir, d)))
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)

    files = 0
    # Skills, flat with aicc- prefix.
    for name in skill_names:
        src_root = os.path.join(skills_dir, name)
        dst_root = os.path.join(out_dir, "aicc-%s" % name)
        for base, dirs, names in os.walk(src_root):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fname in names:
                src = os.path.join(base, fname)
                rel = os.path.relpath(src, src_root)
                copy_transformed(src, os.path.join(dst_root, rel), skill_names,
                                 is_skill_md=(rel == "SKILL.md"))
                files += 1

    # Shared layers, package-relative.
    for sub in ("references", "agents", "bin"):
        src_root = os.path.join(plugin_root, sub)
        if not os.path.isdir(src_root):
            continue
        for fname in sorted(os.listdir(src_root)):
            src = os.path.join(src_root, fname)
            if os.path.isfile(src):
                copy_transformed(src, os.path.join(out_dir, sub, fname), skill_names)
                if sub == "bin":
                    os.chmod(os.path.join(out_dir, sub, fname), 0o755)
                files += 1
    scripts_src = os.path.join(plugin_root, "scripts", "py")
    for fname in sorted(os.listdir(scripts_src)):
        if fname.endswith(".py"):
            copy_transformed(os.path.join(scripts_src, fname),
                             os.path.join(out_dir, "scripts", "py", fname), skill_names)
            files += 1

    # Self-contained .codex/ enforcement bundle (hooks parity).
    enforcement_files = project_enforcement(plugin_root, out_dir)
    files += enforcement_files

    # AGENTS.md index.
    lines = [
        "# AICC for Codex — Skill Index",
        "",
        "Flat projection of the AICC Claude Code plugin. AICC ships a",
        "`.codex/` hooks bundle (Codex >= v0.117 supports lifecycle hooks):",
        "copy `.codex/` to your repo root and run `/hooks` to trust it, and",
        "the commit gate and git-safety guard enforce automatically. Codex",
        "hook interception has gaps, so each skill body also names the",
        "validator to run by hand (`bin/aicc-*`, Python 3 required) as a",
        "backstop. See `.codex/README.md` to install the hooks.",
        "",
        "Read the skill file that matches the task, then follow it:",
        "",
    ]
    for name in skill_names:
        text = open(os.path.join(skills_dir, name, "SKILL.md"), encoding="utf-8").read()
        match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        description = match.group(1).strip() if match else ""
        lines.append("- `aicc-%s/SKILL.md` — %s" % (name, description))
    lines += [
        "",
        "Supporting layers: `references/` (shared rules and specs),",
        "`agents/` (role prompts to paste when a specialist lens is needed),",
        "`scripts/py/` + `bin/` (validators and scanners),",
        "`.codex/` (installable PreToolUse/SessionStart hooks for enforcement).",
        "",
    ]
    with open(os.path.join(out_dir, "AGENTS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    files += 1

    return {"out_dir": out_dir, "skills": len(skill_names), "files": files,
            "enforcement_files": enforcement_files}


if __name__ == "__main__":
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = run(plugin_root,
                 os.path.join(os.path.dirname(plugin_root), "dist", "codex"))
    print("codex package: %(skills)d skills, %(files)d files "
          "(%(enforcement_files)d in .codex/ bundle) -> %(out_dir)s" % result)
