#!/usr/bin/env python3
"""
框架契约检查器

最小能力：
- 检查主文档模板是否满足 main_doc_contract.yaml 必需章节
- 检查 workflow 是否引入了未被 spec 收录的标准产物路径
- 提供框架自检模式，直接扫描当前仓库关键模板和 workflow
"""

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "core" / "contracts"
DEFAULT_TEMPLATE = ROOT / "templates" / "AI_Coding_Context_TEMPLATE.md"
DEFAULT_SPEC = ROOT / "core" / "framework_spec.md"
DEFAULT_WORKFLOWS = [
    ROOT / "workflows" / "generation_workflow.md",
    ROOT / "workflows" / "path_a_first_generation.md",
]


def load_required_titles(contract_path):
    titles = []
    for line in contract_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r'^\s*title:\s*"?(.*?)"?\s*$', line)
        if match:
            titles.append(match.group(1))
    return titles


def extract_h2_titles(text):
    return [match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)]


def check_template(template_path, contract_path):
    required_titles = load_required_titles(contract_path)
    actual_titles = extract_h2_titles(template_path.read_text(encoding="utf-8"))
    issues = []
    for title in required_titles:
        if title not in actual_titles:
            issues.append({
                "file": str(template_path),
                "type": "missing_required_section",
                "section": title,
                "message": f"缺少必需章节: {title}",
            })
    return {"checked": 1, "issues": issues}


def extract_standard_paths(spec_path):
    text = spec_path.read_text(encoding="utf-8")
    return set(re.findall(r"`(dev_docs/[^`]+)`", text))


def _context_is_optional(lines, index):
    section_start = 0
    for cursor in range(index, -1, -1):
        if re.match(r"^#{2,6}\s+", lines[cursor]):
            section_start = cursor
            break
    window = lines[section_start:min(len(lines), index + 4)]
    context = "\n".join(window)
    optional_markers = ["[OPTIONAL]", "不属于", "只有在用户明确需要", "可选", "不是必需"]
    return any(marker in context for marker in optional_markers)


def check_workflow(workflow_path, spec_path):
    spec_paths = extract_standard_paths(spec_path)
    lines = workflow_path.read_text(encoding="utf-8").splitlines()
    issues = []
    for index, line in enumerate(lines):
        for matched in re.findall(r"(dev_docs/[\w./-]*review/[\w./-]*)", line):
            if matched not in spec_paths and not _context_is_optional(lines, index):
                issues.append({
                    "file": str(workflow_path),
                    "line": index + 1,
                    "type": "workflow_path_drift",
                    "path": matched,
                    "message": f"workflow 使用了未被 spec 收录的标准路径: {matched}",
                })
    return {"checked": 1, "issues": issues}


def render_text(payload):
    summary = payload["summary"]
    status = "PASS" if summary["passed"] else "FAIL"
    lines = [f"{status}: framework_contract_checker"]
    for check_name, result in payload["checks"].items():
        lines.append(f"- {check_name}: {len(result['issues'])} issue(s)")
        for issue in result["issues"]:
            location = issue.get("file", "")
            if issue.get("line"):
                location = f"{location}:{issue['line']}"
            lines.append(f"  - {issue['type']} {location} {issue.get('message', '')}".rstrip())
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="检查 AICC 框架契约与 workflow 漂移")
    parser.add_argument("--self-check", action="store_true", help="检查当前仓库关键模板与 workflow")
    parser.add_argument("--check-template", help="检查指定模板或文档是否满足主文档契约")
    parser.add_argument("--check-workflow", help="检查指定 workflow 是否与 spec 路径一致")
    parser.add_argument("--contract", default=str(CONTRACTS_DIR / "main_doc_contract.yaml"), help="主文档契约文件路径")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC), help="规范文档路径，用于 workflow 漂移检查")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="输出格式")
    args = parser.parse_args()

    checks = {}

    if args.check_template:
        checks["template"] = check_template(Path(args.check_template), Path(args.contract))

    if args.check_workflow:
        checks["workflow"] = check_workflow(Path(args.check_workflow), Path(args.spec))

    if args.self_check:
        checks["template"] = check_template(DEFAULT_TEMPLATE, Path(args.contract))
        workflow_issues = []
        for workflow_path in DEFAULT_WORKFLOWS:
            workflow_issues.extend(check_workflow(workflow_path, Path(args.spec))["issues"])
        checks["workflow"] = {"checked": len(DEFAULT_WORKFLOWS), "issues": workflow_issues}

    if not checks:
        parser.print_help()
        return 2

    total_issues = sum(len(result["issues"]) for result in checks.values())
    payload = {
        "summary": {
            "passed": total_issues == 0,
            "issues": total_issues,
        },
        "checks": checks,
    }

    if args.format == "text":
        sys.stdout.write(render_text(payload))
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
