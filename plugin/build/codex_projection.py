#!/usr/bin/env python3
"""Project the AICC plugin into a flat Codex package (spec §7).

Codex has no plugin namespace, no hooks, no SessionStart injection. The
projection is a pure transformation of the SAME skill sources:

  - skills/<name>/        -> dist/codex/aicc-<name>/   (flat, prefixed)
  - /aicc:<name> mentions -> aicc-<name>
  - ${CLAUDE_PLUGIN_ROOT}/x -> ../x (package-relative)
  - every skill gets an advisory degradation note: hook-enforced gates
    become "run the validators yourself" recommendations
  - shared references/, scripts/py/, bin/, agents/ copied alongside
  - AGENTS.md index generated at the package root

Run via `python3 build.py --codex` (or standalone).
"""

import os
import re
import shutil

DEGRADATION_NOTE = """\
> **Codex package note (advisory mode).** This platform has no enforcement
> hooks: nothing here can block a commit or a dangerous git command. The
> gates described below are recommendations you must run yourself:
> - before any commit: `bin/aicc-summary-validate --dir dev_docs/ --recursive`
>   and `bin/aicc-doc-health --mode quick`
> - before any risky git command: `bin/aicc-git-safety --validate-command "<cmd>"`
>   (red zone = do not run it)
"""


def transform_markdown(text, skill_names):
    for name in skill_names:
        text = text.replace("/aicc:%s" % name, "aicc-%s" % name)
    text = text.replace("/aicc:", "aicc-")  # generic mentions
    text = text.replace("${CLAUDE_PLUGIN_ROOT}/", "../")
    text = text.replace(
        "is enforced, not advisory",
        "is enforced by hooks on Claude Code; in this package it is advisory")
    return text


def inject_note(skill_md_text):
    """Insert the degradation note right after the H1 (or frontmatter)."""
    match = re.search(r"^# .+$", skill_md_text, re.MULTILINE)
    if match:
        pos = match.end()
        return skill_md_text[:pos] + "\n\n" + DEGRADATION_NOTE + skill_md_text[pos:]
    return DEGRADATION_NOTE + "\n" + skill_md_text


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

    # AGENTS.md index.
    lines = [
        "# AICC for Codex — Skill Index",
        "",
        "Flat projection of the AICC Claude Code plugin. **Advisory mode**:",
        "Codex has no hooks, so AICC's commit gate and git-safety guard do",
        "not run automatically here — each skill body tells you which",
        "validator to run instead (`bin/aicc-*`, Python 3 required).",
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
        "`scripts/py/` + `bin/` (validators and scanners).",
        "",
    ]
    with open(os.path.join(out_dir, "AGENTS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    files += 1

    return {"out_dir": out_dir, "skills": len(skill_names), "files": files}


if __name__ == "__main__":
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = run(plugin_root,
                 os.path.join(os.path.dirname(plugin_root), "dist", "codex"))
    print("codex package: %(skills)d skills, %(files)d files -> %(out_dir)s" % result)
