#!/usr/bin/env python3
"""AICC session injection (SessionStart).

Replaces the clone-era "paste AI_ENTRY_POINT.md" bootstrap: every session
automatically learns which AICC skills exist and whether the project has
AICC docs (plus a quick health snapshot when it does).

Output: SessionStart additionalContext JSON. Fails open — any internal
error results in no output and exit 0; this hook must never break a session.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _aicc_common as common


def skill_catalog(root):
    """[(name, first clause of description)] from shipped SKILL.md files."""
    catalog = []
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        return catalog
    for name in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        description = ""
        try:
            text = open(skill_md, "r", encoding="utf-8").read()
            match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            if match:
                description = match.group(1).strip().strip('"')
        except OSError:
            pass
        clause = re.split(r"[.;](\s|$)", description, maxsplit=1)[0]
        clause = re.sub(r"^Use when\s+", "", clause)
        catalog.append((name, clause))
    return catalog


def build_context(cwd):
    root = common.plugin_root()
    lines = []
    catalog = skill_catalog(root)
    if catalog:
        lines.append("AICC plugin skills available:")
        for name, clause in catalog:
            lines.append("  /aicc:%s — %s" % (name, clause))

    doc_dir = os.path.join(cwd, "dev_docs")
    if not os.path.isdir(doc_dir):
        lines.append("Project: no dev_docs/ AICC documentation yet. "
                     "Run /aicc:init to generate the AI coding context.")
    else:
        try:
            sys.path.insert(0, os.path.join(root, "scripts", "py"))
            import doc_health
            snap = doc_health.health_snapshot(doc_dir, mode="quick")
            lines.append(
                "Project: dev_docs/ present — %d doc(s), %d stale, "
                "health %s (%d/100)."
                % (snap["doc_count"], snap["stale_count"], snap["grade"],
                   snap["score"]))
            if snap["score"] < 70:
                lines.append("Run /aicc:health-check for a full assessment "
                             "before relying on these docs.")
        except Exception:
            lines.append("Project: dev_docs/ present. Run /aicc:health-check "
                         "to assess documentation health.")
    return "\n".join(lines)


def main():
    event = common.read_event()
    cwd = event.get("cwd") or os.getcwd()
    context = build_context(cwd)
    if context:
        common.emit({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        })


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open: never break the session
    sys.exit(0)
