#!/usr/bin/env python3
"""Reverse-entropy lint for the AICC plugin tree.

Standing checks (run by build.py and usable standalone / in CI):
  1. English only: no CJK characters in any shipped file under plugin/.
  2. Skill descriptions: present, start with "Use when", <= 1024 chars.
  3. Skill body budgets: SKILL.md line counts within the per-skill budget.
  4. Reference depth: references/ trees are exactly one layer deep.
  5. Settings consumption: every aicc.* settings key is referenced by at
     least one skill body, hook, or script.
  6. Skill dirs are not prefixed "aicc-" (would double the namespace).

Usage: python3 lint.py [--plugin-root PATH]   (exit 0 = clean)
"""

import argparse
import json
import os
import re
import sys

SKILL_BODY_BUDGETS = {
    "init": 300,
    "health-check": 250,
    "incremental-update": 300,
    "design-thinking": 250,
    "mutual-review": 250,
    "adr": 200,
    "complexity-dashboard": 200,
    "doc-fallacy-fix": 250,
    "systematic-review": 250,
    "doc-reading-habit": 150,
    "knowledge-reuse": 200,
}

# CJK unified ideographs + extensions, CJK punctuation, fullwidth forms,
# hiragana, katakana, hangul. Escapes only, so this file stays CJK-free.
CJK_RE = re.compile(
    u"[\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
    u"\uac00-\ud7af\uf900-\ufaff\uff00-\uffef]"
)
TEXT_EXTENSIONS = (".md", ".json", ".py", ".js", ".sh", ".yaml", ".yml", ".txt", "")


def iter_shipped_files(root):
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for name in sorted(names):
            if os.path.splitext(name)[1] in TEXT_EXTENSIONS:
                yield os.path.join(base, name)


def check_no_cjk(root, problems):
    for path in iter_shipped_files(root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, start=1):
                    if CJK_RE.search(line):
                        problems.append("CJK character in %s:%d" % (path, lineno))
                        break
        except OSError as exc:
            problems.append("unreadable file %s: %s" % (path, exc))


def parse_skill_frontmatter(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fields = {}
    if match:
        for line in match.group(1).splitlines():
            kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
            if kv:
                fields[kv.group(1)] = kv.group(2).strip().strip('"')
    return fields, text


def check_skills(root, problems):
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        return
    for name in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, name)
        if not os.path.isdir(skill_dir):
            continue
        if name.startswith("aicc-"):
            problems.append(
                "skill dir %s must not be prefixed 'aicc-' (namespace is automatic)" % name)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_md):
            problems.append("skill %s has no SKILL.md" % name)
            continue
        fields, text = parse_skill_frontmatter(skill_md)
        description = fields.get("description", "")
        if not description:
            problems.append("skill %s: missing frontmatter description" % name)
        elif not description.startswith("Use when"):
            problems.append("skill %s: description must start with 'Use when'" % name)
        if len(description) > 1024:
            problems.append("skill %s: description exceeds 1024 chars (%d)"
                            % (name, len(description)))
        budget = SKILL_BODY_BUDGETS.get(name)
        lines = text.count("\n") + 1
        if budget and lines > budget:
            problems.append("skill %s: SKILL.md is %d lines, budget is %d"
                            % (name, lines, budget))


def check_reference_depth(root, problems):
    candidates = [os.path.join(root, "references")]
    skills_dir = os.path.join(root, "skills")
    if os.path.isdir(skills_dir):
        for name in os.listdir(skills_dir):
            candidates.append(os.path.join(skills_dir, name, "references"))
    for ref_dir in candidates:
        if not os.path.isdir(ref_dir):
            continue
        for entry in os.listdir(ref_dir):
            if os.path.isdir(os.path.join(ref_dir, entry)):
                problems.append(
                    "references must be one layer deep: %s contains directory %s"
                    % (ref_dir, entry))


def settings_keys(value, prefix=""):
    keys = []
    if isinstance(value, dict):
        for key, sub in value.items():
            path = "%s.%s" % (prefix, key) if prefix else key
            keys.append(path)
            keys.extend(settings_keys(sub, path))
    return keys


def check_settings_consumed(root, problems):
    settings_path = os.path.join(root, "settings.json")
    if not os.path.isfile(settings_path):
        return
    try:
        with open(settings_path, "r", encoding="utf-8") as fh:
            aicc = json.load(fh).get("aicc", {})
    except (OSError, json.JSONDecodeError) as exc:
        problems.append("settings.json unreadable: %s" % exc)
        return
    leaf_keys = [k.split(".")[-1] for k in settings_keys(aicc)
                 if not isinstance(_lookup(aicc, k), dict)]
    corpus = ""
    for sub in ("skills", "hooks", "scripts", "agents", "references", "README.md"):
        path = os.path.join(root, sub)
        if os.path.isfile(path):
            corpus += open(path, "r", encoding="utf-8", errors="replace").read()
        elif os.path.isdir(path):
            for f in iter_shipped_files(path):
                corpus += open(f, "r", encoding="utf-8", errors="replace").read()
    for key in leaf_keys:
        if key not in corpus:
            problems.append(
                "settings key aicc...%s is not referenced by any skill/hook/script" % key)


def _lookup(data, dotted):
    node = data
    for part in dotted.split("."):
        node = node[part]
    return node


def run(root):
    problems = []
    check_no_cjk(root, problems)
    check_skills(root, problems)
    check_reference_depth(root, problems)
    check_settings_consumed(root, problems)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lint the AICC plugin tree.")
    parser.add_argument("--plugin-root",
                        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = parser.parse_args(argv)
    problems = run(args.plugin_root)
    for problem in problems:
        print("LINT: %s" % problem)
    print("lint: %d problem(s)" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
