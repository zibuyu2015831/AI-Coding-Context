#!/usr/bin/env python3
"""AICC documentation health checker.

Machine checks over an AICC-managed doc tree (default: dev_docs/):

  quick     structure completeness + frontmatter validity + staleness
  standard  quick + internal link / file-path accuracy
  deep      standard + python code-block syntax check

Scoring starts at 100 with capped deductions per category; grades follow
the AICC bands: >=90 excellent, >=70 good, >=50 fair, >=30 poor, else
critical.

Usage:
  python3 doc_health.py [--doc-dir dev_docs] [--mode quick|standard|deep]
                        [--json] [--fail-under N]
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import summary_validator

MAIN_DOC = "AI_Coding_Context.md"
GRADE_BANDS = ((90, "excellent"), (70, "good"), (50, "fair"), (30, "poor"))
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#?\s]+)[^)]*\)")


def grade(score):
    for floor, name in GRADE_BANDS:
        if score >= floor:
            return name
    return "critical"


def markdown_files(doc_dir):
    found = []
    for base, dirs, names in os.walk(doc_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in sorted(names):
            if name.endswith(".md"):
                found.append(os.path.join(base, name))
    return found


def check_structure(doc_dir, issues):
    deduction = 0
    if not os.path.isfile(os.path.join(doc_dir, MAIN_DOC)):
        issues.append("structure: main doc %s is missing" % MAIN_DOC)
        deduction += 30
    if not os.path.isdir(os.path.join(doc_dir, "_analysis")):
        issues.append("structure: _analysis/ directory is missing")
        deduction += 5
    return deduction


def check_frontmatter(files, repo_root, issues):
    deduction, stale = 0, 0
    for path in files:
        report = summary_validator.validate_file(path, repo_root=repo_root)
        for err in report["errors"]:
            issues.append("frontmatter: %s: %s" % (path, err))
            deduction = min(deduction + 5, 20)
        if any("stale" in w for w in report["warnings"]):
            stale += 1
    if stale:
        issues.append("staleness: %d doc(s) older than %d days"
                      % (stale, summary_validator.STALE_DAYS))
        deduction += min(2 * stale, 20)
    return deduction, stale


def check_links(files, repo_root, issues):
    deduction = 0
    for path in files:
        try:
            text = open(path, "r", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            candidates = (
                os.path.join(os.path.dirname(path), target),
                os.path.join(repo_root, target),
            )
            if not any(os.path.exists(c) for c in candidates):
                issues.append("link: %s -> %s does not exist" % (path, target))
                deduction = min(deduction + 3, 20)
    return deduction


def check_code_samples(files, issues):
    deduction = 0
    block_re = re.compile(r"```(python|py)\n(.*?)```", re.DOTALL)
    for path in files:
        try:
            text = open(path, "r", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _, code in block_re.findall(text):
            try:
                compile(code, path, "exec")
            except SyntaxError as exc:
                issues.append("code-sample: %s: python block does not parse (%s)"
                              % (path, exc.msg))
                deduction = min(deduction + 2, 10)
    return deduction


def health_snapshot(doc_dir, mode="quick"):
    """Importable entry point (used by the SessionStart hook and bin CLI)."""
    repo_root = os.path.dirname(os.path.abspath(doc_dir)) or "."
    snapshot = {
        "doc_dir": doc_dir,
        "present": os.path.isdir(doc_dir),
        "mode": mode,
        "doc_count": 0,
        "stale_count": 0,
        "score": 0,
        "grade": "critical",
        "issues": [],
    }
    if not snapshot["present"]:
        snapshot["issues"].append("doc dir %s does not exist" % doc_dir)
        return snapshot

    files = markdown_files(doc_dir)
    snapshot["doc_count"] = len(files)
    issues = snapshot["issues"]
    score = 100
    score -= check_structure(doc_dir, issues)
    fm_deduction, stale = check_frontmatter(files, repo_root, issues)
    score -= fm_deduction
    snapshot["stale_count"] = stale
    if mode in ("standard", "deep"):
        score -= check_links(files, repo_root, issues)
    if mode == "deep":
        score -= check_code_samples(files, issues)
    snapshot["score"] = max(score, 0)
    snapshot["grade"] = grade(snapshot["score"])
    return snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(description="AICC documentation health check.")
    parser.add_argument("--doc-dir", default="dev_docs")
    parser.add_argument("--mode", choices=("quick", "standard", "deep"),
                        default="standard")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fail-under", type=int, default=0,
                        help="exit 1 when the score is below this value")
    args = parser.parse_args(argv)

    snapshot = health_snapshot(args.doc_dir, args.mode)
    if args.json:
        print(json.dumps(snapshot, indent=2))
    else:
        print("doc health: %s (%d/100), %d doc(s), %d stale, mode=%s"
              % (snapshot["grade"], snapshot["score"], snapshot["doc_count"],
                 snapshot["stale_count"], snapshot["mode"]))
        for issue in snapshot["issues"]:
            print("  - %s" % issue)
    return 1 if snapshot["score"] < args.fail_under else 0


if __name__ == "__main__":
    sys.exit(main())
