#!/usr/bin/env python3
"""
半自动语义复查检查器

最小能力：
- 量化声明校验（测试文件数 / 测试目录数 / 指定路径文件数）
- 测试资产拓扑检查（tests/ 与 examples/**/tests/ 是否被文档覆盖）
- 事实源冲突检查（显式强约束语句的 polarity 冲突）
"""

import argparse
import json
import re
import sys
from pathlib import Path


POSITIVE_KEYWORDS = ["推荐", "必须", "优先", "建议", "should", "recommended", "prefer", "需要"]
NEGATIVE_KEYWORDS = ["不建议", "不要", "禁止", "deprecated", "废弃", "avoid", "do not", "不需要", "无需"]
SOURCE_SUFFIXES = {".md", ".py", ".js", ".ts", ".tsx"}


def iter_markdown_files(root):
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def iter_authority_files(repo_root, doc_dir):
    files = []
    readme = repo_root / "README.md"
    if readme.exists():
        files.append(readme)
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        files.extend(path for path in docs_dir.rglob("*") if path.is_file() and path.suffix in SOURCE_SUFFIXES)
    for path in repo_root.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if doc_dir in path.parents:
            continue
        if path.name == "README.md" or path in files:
            continue
        files.append(path)
    return sorted(set(files))


def scan_test_topology(repo_root):
    topology = []
    for path in repo_root.rglob("*"):
        if not path.is_dir():
            continue
        if path.name not in {"tests", "test"}:
            continue
        file_count = sum(1 for child in path.rglob("*") if child.is_file())
        topology.append({
            "path": path.relative_to(repo_root).as_posix() + "/",
            "file_count": file_count,
        })
    topology.sort(key=lambda item: item["path"])
    return topology


def count_files_under(repo_root, relative_path):
    target = repo_root / relative_path
    if not target.exists():
        return None
    if target.is_file():
        return 1
    return sum(1 for child in target.rglob("*") if child.is_file())


def check_metrics(doc_dir, repo_root):
    issues = []
    topology = scan_test_topology(repo_root)
    total_test_files = sum(item["file_count"] for item in topology)
    total_test_dirs = len(topology)
    path_pattern = re.compile(r"`?([\w./-]+)`?\s*下共有\s*(\d+)\s*个文件")
    test_file_pattern = re.compile(r"(\d+)\s*个测试文件")
    test_dir_pattern = re.compile(r"(\d+)\s*个测试目录")
    for doc_path in iter_markdown_files(doc_dir):
        for line_no, line in enumerate(doc_path.read_text(encoding="utf-8").splitlines(), 1):
            for match in path_pattern.finditer(line):
                rel_path, expected = match.group(1), int(match.group(2))
                actual = count_files_under(repo_root, rel_path)
                if actual is not None and actual != expected:
                    issues.append({
                        "type": "metric_drift",
                        "file": str(doc_path),
                        "line": line_no,
                        "metric": f"{rel_path} file_count",
                        "expected": expected,
                        "actual": actual,
                    })
            for match in test_file_pattern.finditer(line):
                expected = int(match.group(1))
                if expected != total_test_files:
                    issues.append({
                        "type": "metric_drift",
                        "file": str(doc_path),
                        "line": line_no,
                        "metric": "test_file_count",
                        "expected": expected,
                        "actual": total_test_files,
                    })
            for match in test_dir_pattern.finditer(line):
                expected = int(match.group(1))
                if expected != total_test_dirs:
                    issues.append({
                        "type": "metric_drift",
                        "file": str(doc_path),
                        "line": line_no,
                        "metric": "test_directory_count",
                        "expected": expected,
                        "actual": total_test_dirs,
                    })
    return issues


def check_test_topology(doc_dir, repo_root):
    issues = []
    topology = scan_test_topology(repo_root)
    document_text = "\n".join(path.read_text(encoding="utf-8") for path in iter_markdown_files(doc_dir))
    for item in topology:
        relative = item["path"]
        basename = relative.rstrip("/").split("/")[-1] + "/"
        covered = relative in document_text
        if not covered and relative.count("/") == 1:
            covered = basename in document_text
        if not covered:
            issues.append({
                "type": "uncovered_test_topology",
                "path": relative,
                "file_count": item["file_count"],
                "message": f"测试目录未被文档覆盖: {relative}",
            })
    return issues


def classify_polarity(line):
    negative = any(keyword in line for keyword in NEGATIVE_KEYWORDS)
    positive = any(keyword in line for keyword in POSITIVE_KEYWORDS)
    if negative and not positive:
        return "negative"
    if positive and not negative:
        return "positive"
    if negative and positive:
        # 以显式否定优先
        return "negative"
    return None


def extract_anchors(line):
    anchors = re.findall(r"`([^`]+)`", line)
    return [anchor.strip() for anchor in anchors if anchor.strip()]


def collect_assertions(files):
    assertions = []
    for path in files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            polarity = classify_polarity(line)
            if not polarity:
                continue
            anchors = extract_anchors(line)
            if not anchors:
                continue
            assertions.append({
                "file": str(path),
                "line": line_no,
                "polarity": polarity,
                "anchors": anchors,
                "text": line.strip(),
            })
    return assertions


def check_fact_conflicts(doc_dir, repo_root):
    issues = []
    doc_assertions = collect_assertions(iter_markdown_files(doc_dir))
    authority_assertions = collect_assertions(iter_authority_files(repo_root, doc_dir))
    for doc_assertion in doc_assertions:
        for authority_assertion in authority_assertions:
            if doc_assertion["polarity"] == authority_assertion["polarity"]:
                continue
            shared = sorted(set(doc_assertion["anchors"]) & set(authority_assertion["anchors"]))
            if not shared:
                continue
            issues.append({
                "type": "fact_conflict",
                "anchor": shared[0],
                "doc_file": doc_assertion["file"],
                "doc_line": doc_assertion["line"],
                "authority_file": authority_assertion["file"],
                "authority_line": authority_assertion["line"],
                "doc_text": doc_assertion["text"],
                "authority_text": authority_assertion["text"],
            })
    return issues


def render_text(payload):
    status = "PASS" if payload["summary"]["passed"] else "FAIL"
    lines = [f"{status}: semantic_review_checker"]
    for name, issues in payload["checks"].items():
        lines.append(f"- {name}: {len(issues)} issue(s)")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="执行 AICC 文档的半自动语义复查")
    parser.add_argument("--doc-dir", required=True, help="dev_docs 目录")
    parser.add_argument("--repo-root", default=".", help="目标仓库根目录")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="输出格式")
    parser.add_argument("--check-fact-conflicts", action="store_true", help="检查事实源冲突")
    parser.add_argument("--check-metrics", action="store_true", help="检查量化声明失真")
    parser.add_argument("--check-test-topology", action="store_true", help="检查测试拓扑是否被文档覆盖")
    parser.add_argument("--full-check", action="store_true", help="执行所有语义复查")
    args = parser.parse_args()

    doc_dir = Path(args.doc_dir).resolve()
    repo_root = Path(args.repo_root).resolve()
    checks = {
        "fact_conflicts": [],
        "metrics": [],
        "test_topology": [],
    }

    if args.full_check or args.check_fact_conflicts:
        checks["fact_conflicts"] = check_fact_conflicts(doc_dir, repo_root)
    if args.full_check or args.check_metrics:
        checks["metrics"] = check_metrics(doc_dir, repo_root)
    if args.full_check or args.check_test_topology:
        checks["test_topology"] = check_test_topology(doc_dir, repo_root)

    if not any([args.full_check, args.check_fact_conflicts, args.check_metrics, args.check_test_topology]):
        parser.print_help()
        return 2

    total_issues = sum(len(issues) for issues in checks.values())
    payload = {
        "summary": {"passed": total_issues == 0, "issues": total_issues},
        "checks": checks,
        "metadata": {"doc_dir": str(doc_dir), "repo_root": str(repo_root)},
    }
    if args.format == "text":
        sys.stdout.write(render_text(payload))
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
