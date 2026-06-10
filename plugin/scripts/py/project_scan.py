#!/usr/bin/env python3
"""AICC project scanner: type detection + inventory + complexity tier.

Scans a user project (respecting the framework boundary: build artifacts,
VCS metadata, dependency dirs, and dev_docs/ are excluded) and reports:
  - detected project type signals (marker files, frameworks)
  - file/line counts by language
  - a suggested AICC complexity tier (trivial/simple/medium/complex/critical)

Usage: python3 project_scan.py [--root .] [--json]
"""

import argparse
import json
import os
import sys

EXCLUDED_DIRS = {
    ".git", ".svn", ".hg", ".idea", ".vscode", ".qoder", ".kiro",
    "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", "target", "out", ".next", ".nuxt", "coverage",
    "dev_docs",
}
CODE_EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "typescript", ".jsx": "javascript", ".vue": "vue",
    ".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust",
    ".rb": "ruby", ".php": "php", ".cs": "csharp", ".swift": "swift",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp",
    ".scala": "scala", ".sh": "shell", ".sql": "sql",
}
TYPE_MARKERS = (
    ("package.json", "node project"),
    ("pyproject.toml", "python project"),
    ("requirements.txt", "python project"),
    ("go.mod", "go project"),
    ("Cargo.toml", "rust project"),
    ("pom.xml", "java (maven) project"),
    ("build.gradle", "java/kotlin (gradle) project"),
    ("composer.json", "php project"),
    ("Gemfile", "ruby project"),
    ("Dockerfile", "containerized"),
    ("docker-compose.yml", "containerized (compose)"),
    ("serverless.yml", "serverless"),
    ("pubspec.yaml", "flutter/dart project"),
)
# Tier thresholds are calibration defaults by code file count (adjust per
# project; monorepo/microservices typically bump one tier up).
TIER_THRESHOLDS = ((10, "trivial"), (100, "simple"), (500, "medium"),
                   (2000, "complex"))


def suggest_tier(code_files):
    for limit, tier in TIER_THRESHOLDS:
        if code_files < limit:
            return tier
    return "critical"


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def scan(root):
    result = {
        "root": os.path.abspath(root),
        "markers": [],
        "languages": {},
        "code_files": 0,
        "code_lines": 0,
        "total_files": 0,
        "has_dev_docs": os.path.isdir(os.path.join(root, "dev_docs")),
        "top_dirs": [],
    }
    for marker, label in TYPE_MARKERS:
        if os.path.exists(os.path.join(root, marker)):
            result["markers"].append({"file": marker, "signal": label})

    for entry in sorted(os.listdir(root)):
        if entry in EXCLUDED_DIRS or entry.startswith("."):
            continue
        if os.path.isdir(os.path.join(root, entry)):
            result["top_dirs"].append(entry)

    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for name in names:
            result["total_files"] += 1
            ext = os.path.splitext(name)[1].lower()
            lang = CODE_EXTENSIONS.get(ext)
            if lang:
                path = os.path.join(base, name)
                stats = result["languages"].setdefault(lang, {"files": 0, "lines": 0})
                stats["files"] += 1
                stats["lines"] += count_lines(path)
                result["code_files"] += 1

    result["code_lines"] = sum(v["lines"] for v in result["languages"].values())
    result["suggested_tier"] = suggest_tier(result["code_files"])
    if len(result["languages"]) >= 3:
        result["tier_note"] = ("3+ languages detected; consider one tier up "
                               "from %s" % result["suggested_tier"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scan a project for AICC doc generation planning.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    result = scan(args.root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        signals = ", ".join(m["signal"] for m in result["markers"]) or "none detected"
        print("project: %s" % result["root"])
        print("type signals: %s" % signals)
        print("code: %d files, %d lines across %d language(s)"
              % (result["code_files"], result["code_lines"], len(result["languages"])))
        for lang, stats in sorted(result["languages"].items()):
            print("  %-12s %5d files %8d lines" % (lang, stats["files"], stats["lines"]))
        print("dev_docs/: %s" % ("present" if result["has_dev_docs"] else "absent"))
        print("suggested complexity tier: %s" % result["suggested_tier"])
        if "tier_note" in result:
            print("note: %s" % result["tier_note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
