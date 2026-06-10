#!/usr/bin/env python3
"""Check an AICC main doc against the plugin's section contract.

The plugin's /aicc:init skill generates an English main doc
(dev_docs/AI_Coding_Context.md). This checker verifies the sections that
every main doc must keep so AI sessions can navigate it. Matching is
tolerant: emoji, numbering, and case are ignored.

Usage:
  python3 contract_check.py [--file dev_docs/AI_Coding_Context.md] [--json]

Exit code 0 when all required sections are present.
"""

import argparse
import json
import re
import sys

# Contract v1 (plugin-generated English main doc). Each entry: (id, match key).
REQUIRED_SECTIONS = (
    ("project_overview", "project overview"),
    ("key_directories", "key directories"),
    ("documentation_index", "documentation index"),
    ("development_workflow", "development workflow"),
    ("common_tasks", "common tasks"),
    ("maintenance_triggers", "maintenance triggers"),
    ("ai_coding_taboos", "ai coding taboos"),
)


def normalize(title):
    """Lowercase and strip emoji/numbering/punctuation from a heading."""
    title = re.sub(r"[^A-Za-z0-9 ]+", " ", title).lower()
    return re.sub(r"\s+", " ", title).strip()


def check_main_doc(path):
    """Return {file, issues: [english strings]}."""
    result = {"file": path, "issues": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        result["issues"].append("cannot read file: %s" % exc)
        return result

    headings = [normalize(m.group(1))
                for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]
    for section_id, key in REQUIRED_SECTIONS:
        if not any(key in heading for heading in headings):
            result["issues"].append(
                "missing required section (%s): a '## ... %s ...' heading"
                % (section_id, key.title()))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check an AICC main doc against the section contract.")
    parser.add_argument("--file", default="dev_docs/AI_Coding_Context.md")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    result = check_main_doc(args.file)
    if args.json:
        print(json.dumps({"success": not result["issues"], "data": result}, indent=2))
    else:
        if result["issues"]:
            print("[FAIL] %s" % args.file)
            for issue in result["issues"]:
                print("  %s" % issue)
        else:
            print("[OK] %s — all %d required sections present"
                  % (args.file, len(REQUIRED_SECTIONS)))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
