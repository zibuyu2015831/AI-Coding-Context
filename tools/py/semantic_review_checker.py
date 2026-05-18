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
SOURCE_SUFFIXES = {".md", ".py", ".js", ".ts", ".tsx", ".swift"}


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
        is_standard_test_dir = path.name in {"tests", "test"}
        is_xcode_test_dir = path.name.endswith("Tests") or path.name.endswith("UITests")
        if not (is_standard_test_dir or is_xcode_test_dir):
            continue
        if is_xcode_test_dir:
            swift_test_file_count = sum(
                1 for child in path.rglob("*")
                if child.is_file() and (child.name.endswith("Tests.swift") or child.name.endswith("UITests.swift"))
            )
            file_count = swift_test_file_count or sum(1 for child in path.rglob("*") if child.is_file())
        else:
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


def _line_number(text, offset):
    return text[:offset].count("\n") + 1


def check_review_consistency(doc_dir, repo_root):
    issues = []
    path_pattern = re.compile(r"`([^`]+)`")
    for doc_path in iter_markdown_files(doc_dir):
        text = doc_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        summary_counts = []
        for line_no, line in enumerate(lines, 1):
            if "疑问" not in line:
                continue
            match = re.search(r"\|\s*[^|\n]*疑问[^|\n]*\|\s*(\d+)\s*\|", line)
            if match:
                summary_counts.append((line_no, int(match.group(1))))
        open_questions = [
            line for line in lines
            if re.search(r"- \[ \].*疑问", line) or re.search(r"待用户确认", line)
        ]
        if summary_counts and open_questions:
            actual = len(open_questions)
            for line_no, expected in summary_counts:
                if expected != actual:
                    issues.append({
                        "type": "summary_question_count_mismatch",
                        "file": str(doc_path),
                        "line": line_no,
                        "expected": expected,
                        "actual": actual,
                        "message": "摘要疑问数量与当前待确认清单数量不一致",
                    })

        if "技术债务评估" in text and "证据等级" not in text:
            for line_no, line in enumerate(lines, 1):
                if any(marker in line for marker in ("P0", "必须修复", "预计")):
                    issues.append({
                        "type": "unevidenced_strong_conclusion",
                        "file": str(doc_path),
                        "line": line_no,
                        "message": "Phase 1 强结论缺少证据等级或验证状态",
                    })
                    break

        for match in path_pattern.finditer(text):
            raw_ref = match.group(1)
            if "/" not in raw_ref:
                continue
            ref_path = raw_ref.split(":", 1)[0]
            if ref_path.startswith(("http://", "https://")):
                continue
            line_no = _line_number(text, match.start())
            if "xcsharedata" in ref_path:
                issues.append({
                    "type": "invalid_evidence_path",
                    "file": str(doc_path),
                    "line": line_no,
                    "path": ref_path,
                    "message": "Xcode SwiftPM 路径疑似拼写错误：应为 xcshareddata",
                })
                continue
            candidate = repo_root / ref_path
            if any(marker in ref_path for marker in ("Package.resolved", ".xcodeproj", ".xcworkspace")) and not candidate.exists():
                issues.append({
                    "type": "invalid_evidence_path",
                    "file": str(doc_path),
                    "line": line_no,
                    "path": ref_path,
                    "message": "关键证据路径不存在",
                })
    return issues


def _analysis_file(doc_dir, name):
    return doc_dir / "_analysis" / name


def _read_if_exists(path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def _is_phase1_pass_or_recommendation(text):
    if "Phase 1" not in text and "phase1" not in text.lower():
        return False
    return bool(re.search(r"\bPASS\b|verdict\s*=\s*PASS|建议通过|可进入正式文档生成", text, flags=re.IGNORECASE))


def _repo_has_any(repo_root, names):
    return any((repo_root / name).exists() for name in names)


def _repo_text_signals(repo_root):
    chunks = []
    for rel in ("README.md", "CONTRIBUTING.md"):
        path = repo_root / rel
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    manual = repo_root / "manual"
    if manual.exists():
        for path in manual.rglob("*.md"):
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def check_phase1_analysis_gate(doc_dir, repo_root):
    issues = []
    plan_path = _analysis_file(doc_dir, "generation_plan.md")
    report_path = _analysis_file(doc_dir, "project_analysis_report.md")
    progress_path = _analysis_file(doc_dir, "generation_progress.md")
    plan = _read_if_exists(plan_path)
    report = _read_if_exists(report_path)
    progress = _read_if_exists(progress_path)
    phase1_pass = _is_phase1_pass_or_recommendation(progress)
    strict_phase1_review = phase1_pass or "Phase 1 方案复查记录" in progress or "Phase 1 方案复查清单" in plan

    if strict_phase1_review and plan and "证据与验证记录" in plan and "证据等级" not in plan:
        issues.append({
            "type": "evidence_level_completeness",
            "severity": "blocker",
            "file": str(plan_path),
            "message": "generation_plan.md 的证据与验证记录缺少证据等级",
        })

    report_has_issues = any(marker in report for marker in ("严重问题", "警告", "疑问", "优化建议", "建议"))
    if strict_phase1_review and report and report_has_issues:
        missing = [field for field in ("证据等级", "当前状态", "blocks_phase1", "回写目标") if field not in report]
        if missing:
            issues.append({
                "type": "project_analysis_issue_status_missing",
                "severity": "blocker",
                "file": str(report_path),
                "missing": missing,
                "message": "project_analysis_report.md 的问题项缺少证据等级、状态、阻断标记或回写目标",
            })

    if phase1_pass:
        if "Phase 1 方案复查记录" not in progress or "writeback_summary" not in progress:
            issues.append({
                "type": "phase1_progress_only_review",
                "severity": "blocker",
                "file": str(progress_path),
                "message": "generation_progress.md 声明 Phase 1 PASS/建议通过，但缺少可审计复查记录或回写摘要",
            })
        if report_path.exists() and "证据等级" not in report:
            issues.append({
                "type": "phase1_progress_only_review",
                "severity": "blocker",
                "file": str(report_path),
                "message": "progress 声明 Phase 1 PASS/建议通过，但 project_analysis_report.md 未同步补齐证据等级",
            })

    confirmable_markers = [
        ("贡献者指南", "CONTRIBUTING.md", repo_root / "CONTRIBUTING.md"),
        ("Docker", "docker-compose.yml", repo_root / "docker-compose.yml"),
    ]
    combined_analysis = f"{plan}\n{report}"
    for marker, evidence, path in confirmable_markers:
        if strict_phase1_review and path.exists() and marker in combined_analysis and re.search(rf"(待确认|需确认|是否).*{re.escape(marker)}|{re.escape(marker)}.*(待确认|需确认|是否)", combined_analysis):
            issues.append({
                "type": "confirmable_fact_misclassified",
                "severity": "blocker",
                "file": str(report_path if marker in report else plan_path),
                "fact": marker,
                "evidence": evidence,
                "message": f"可由仓库文件确认的事实被放入用户确认项: {marker}",
            })

    positioning_requirements = []
    if (repo_root / "CONTRIBUTING.md").exists():
        positioning_requirements.append(("open_source_maintenance", ["贡献", "维护", "开源"]))
    if (repo_root / "manual").exists():
        positioning_requirements.append(("user_manual", ["用户手册", "manual", "使用指南", "使用"]))
    if _repo_has_any(repo_root, ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]):
        positioning_requirements.append(("self_hosted_ops", ["Docker", "部署", "运维", "自托管"]))
    repo_signals = _repo_text_signals(repo_root)
    if any(signal.lower() in repo_signals.lower() for signal in ("deepl", "anki", "jellyfin", "dictionary", "external api")):
        positioning_requirements.append(("external_data_api", ["外部", "API", "授权", "集成", "DeepL", "Anki", "Jellyfin", "dictionary"]))
    for signal, keywords in positioning_requirements:
        if strict_phase1_review and not any(keyword in plan for keyword in keywords):
            issues.append({
                "type": "project_positioning_coverage_missing",
                "severity": "warning",
                "file": str(plan_path),
                "signal": signal,
                "message": f"项目定位触发项未进入 generation_plan.md 子文档规划: {signal}",
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
        "review_consistency": [],
        "phase1_analysis_gate": [],
    }

    if args.full_check or args.check_fact_conflicts:
        checks["fact_conflicts"] = check_fact_conflicts(doc_dir, repo_root)
    if args.full_check or args.check_metrics:
        checks["metrics"] = check_metrics(doc_dir, repo_root)
    if args.full_check or args.check_test_topology:
        checks["test_topology"] = check_test_topology(doc_dir, repo_root)
    if args.full_check:
        checks["review_consistency"] = check_review_consistency(doc_dir, repo_root)
        checks["phase1_analysis_gate"] = check_phase1_analysis_gate(doc_dir, repo_root)

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
