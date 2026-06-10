#!/usr/bin/env python3
"""AICC complexity scanner: static size/complexity metrics for a project.

Reports per-language LOC, the largest files, and rough hotspots (very long
files / deeply nested code) — raw metrics only, no scores or grades: the
dashboard layer that interpreted these was not shipped (see BUILD_NOTES).

Usage: python3 complexity_scan.py [--root .] [--top 10] [--json]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project_scan

LONG_FILE_LINES = 800
DEEP_INDENT_LEVELS = 5


def file_metrics(path):
    lines = 0
    deep_lines = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                lines += 1
                stripped = line.expandtabs(4)
                indent = len(stripped) - len(stripped.lstrip(" "))
                if stripped.strip() and indent >= DEEP_INDENT_LEVELS * 4:
                    deep_lines += 1
    except OSError:
        pass
    return lines, deep_lines


def scan(root, top):
    inventory = project_scan.scan(root)
    files = []
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs
                   if d not in project_scan.EXCLUDED_DIRS and not d.startswith(".")]
        for name in names:
            if os.path.splitext(name)[1].lower() in project_scan.CODE_EXTENSIONS:
                path = os.path.join(base, name)
                lines, deep = file_metrics(path)
                files.append({"path": os.path.relpath(path, root),
                              "lines": lines, "deeply_nested_lines": deep})
    files.sort(key=lambda f: f["lines"], reverse=True)
    return {
        "root": inventory["root"],
        "code_files": inventory["code_files"],
        "code_lines": inventory["code_lines"],
        "languages": inventory["languages"],
        "largest_files": files[:top],
        "long_files": [f for f in files if f["lines"] > LONG_FILE_LINES],
        "nesting_hotspots": sorted(
            (f for f in files if f["deeply_nested_lines"] > 0),
            key=lambda f: f["deeply_nested_lines"], reverse=True)[:top],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Static complexity metrics.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = scan(args.root, args.top)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print("code: %d files, %d lines" % (result["code_files"], result["code_lines"]))
    print("largest files:")
    for f in result["largest_files"]:
        print("  %6d  %s" % (f["lines"], f["path"]))
    if result["long_files"]:
        print("files over %d lines: %d" % (LONG_FILE_LINES, len(result["long_files"])))
    if result["nesting_hotspots"]:
        print("nesting hotspots (lines at %d+ indent levels):" % DEEP_INDENT_LEVELS)
        for f in result["nesting_hotspots"]:
            print("  %6d  %s" % (f["deeply_nested_lines"], f["path"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
