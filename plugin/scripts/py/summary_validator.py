#!/usr/bin/env python3
"""Validate AICC YAML-frontmatter summaries in markdown docs.

Checks (per the AICC summary format, see references/summary-format-spec.md):
  - frontmatter block present and parseable
  - required fields: title, summary, keywords, scope, related_files,
    dependencies, verified_at
  - list fields use " | " separation (keywords, related_files, dependencies)
  - referenced files exist (warning only)
  - verified_at is YYYY-MM-DD; older than 90 days -> staleness warning

Usage:
  python3 summary_validator.py --file dev_docs/api_layer.md
  python3 summary_validator.py --dir dev_docs/ --recursive [--strict] [--json]

Exit code 0 when all files are valid (warnings allowed unless --strict).
"""

import argparse
import json
import os
import re
import sys
from datetime import date, datetime

REQUIRED_FIELDS = (
    "title", "summary", "keywords", "scope",
    "related_files", "dependencies", "verified_at",
)
LIST_FIELDS = ("keywords", "related_files", "dependencies")
PATH_FIELDS = ("related_files", "dependencies")
NONE_VALUES = ("none", "n/a", "-", "")
STALE_DAYS = 90


def parse_frontmatter(text):
    """Return (fields dict, error string or None)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing frontmatter block (file must start with '---')"
    fields, end = {}, None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    if end is None:
        return None, "frontmatter block is not closed (no terminating '---')"
    return fields, None


def split_list(value):
    return [item.strip() for item in value.split("|") if item.strip()]


def validate_file(path, repo_root=None):
    """Validate one markdown file; return {file, valid, errors, warnings}."""
    report = {"file": path, "valid": True, "errors": [], "warnings": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        report["errors"].append("cannot read file: %s" % exc)
        report["valid"] = False
        return report

    fields, error = parse_frontmatter(text)
    if error:
        report["errors"].append(error)
        report["valid"] = False
        return report

    for field in REQUIRED_FIELDS:
        if not fields.get(field, "").strip():
            report["errors"].append("missing required field: %s" % field)

    for field in LIST_FIELDS:
        value = fields.get(field, "")
        if value and value.lower() not in NONE_VALUES:
            if field == "keywords" and len(split_list(value)) < 2 and "|" not in value:
                report["warnings"].append(
                    "keywords should list 2+ entries separated by ' | '")

    root = repo_root or os.path.dirname(os.path.abspath(path)) or "."
    for field in PATH_FIELDS:
        value = fields.get(field, "")
        if not value or value.lower() in NONE_VALUES:
            continue
        for entry in split_list(value):
            if re.match(r"^[a-z]+://", entry) or " " in entry:
                continue
            candidates = (
                os.path.join(root, entry),
                os.path.join(os.path.dirname(os.path.abspath(path)), entry),
            )
            if not any(os.path.exists(c) for c in candidates):
                report["warnings"].append(
                    "%s entry not found on disk: %s" % (field, entry))

    verified = fields.get("verified_at", "").strip()
    if verified:
        try:
            stamp = datetime.strptime(verified, "%Y-%m-%d").date()
            age = (date.today() - stamp).days
            if age > STALE_DAYS:
                report["warnings"].append(
                    "summary is stale: verified_at is %d days old (limit %d)"
                    % (age, STALE_DAYS))
            elif age < 0:
                report["warnings"].append("verified_at is in the future")
        except ValueError:
            report["errors"].append(
                "verified_at must be a YYYY-MM-DD date, got: %s" % verified)

    report["valid"] = not report["errors"]
    return report


def collect_files(directory, recursive):
    if recursive:
        for base, dirs, names in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in sorted(names):
                if name.endswith(".md"):
                    yield os.path.join(base, name)
    else:
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if name.endswith(".md") and os.path.isfile(path):
                yield path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate AICC frontmatter summaries in markdown docs.")
    parser.add_argument("--file", help="validate a single markdown file")
    parser.add_argument("--dir", help="validate every .md file in a directory")
    parser.add_argument("--recursive", action="store_true",
                        help="with --dir, descend into subdirectories")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    if not args.file and not args.dir:
        parser.error("one of --file or --dir is required")

    paths = [args.file] if args.file else list(collect_files(args.dir, args.recursive))
    reports = [validate_file(p) for p in paths]
    failed = [r for r in reports
              if not r["valid"] or (args.strict and r["warnings"])]

    if args.json:
        print(json.dumps({"success": not failed, "data": reports}, indent=2))
    else:
        for r in reports:
            status = "OK" if r["valid"] else "FAIL"
            print("[%s] %s" % (status, r["file"]))
            for err in r["errors"]:
                print("  error: %s" % err)
            for warn in r["warnings"]:
                print("  warning: %s" % warn)
        print("%d file(s) checked, %d failed" % (len(reports), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
