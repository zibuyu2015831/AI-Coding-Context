#!/usr/bin/env python3
"""
文档健康检查工具 — Hybrid Orchestrator (B4#017)

功能说明：
    薄编排层（thin orchestrator），不重新实现已存在的能力，而是 delegate 到现有工具
    并仅补差缺能力（代码示例语法 / 依赖版本对照）。

    检查项：
      - 文件路径准确性（delegate 到 doc_dependency_tracer.py）
      - 代码示例语法有效性（新增最小检查）
      - 依赖版本对照（新增最小检查）
      - frontmatter 摘要合规（delegate 到 summary_validator.py）

使用方法：
    # 单文件子集检查（仅链接 + 代码示例 + frontmatter）
    python tools/py/doc_health_checker.py --file dev_docs/api_layer.md

    # 按 mode 触发的组合检查
    python tools/py/doc_health_checker.py --mode quick      # 仅 file-paths
    python tools/py/doc_health_checker.py --mode standard   # quick + code-samples
    python tools/py/doc_health_checker.py --mode deep       # standard + dependencies + frontmatter

    # 显式单项检查
    python tools/py/doc_health_checker.py --check-code-samples [--doc-dir DIR]
    python tools/py/doc_health_checker.py --check-file-paths  [--doc-dir DIR]
    python tools/py/doc_health_checker.py --check-dependencies [--doc-dir DIR]

    # 综合检查（等价 --mode deep 但作用于全 dev_docs/）
    python tools/py/doc_health_checker.py --full-check

参数说明：
    --file FILE              单文件子集检查
    --mode quick|standard|deep   预设组合模式
    --check-file-paths       文件路径准确性
    --check-code-samples     代码示例有效性
    --check-dependencies     依赖版本对照
    --full-check             全部检查（mode deep × 全 dev_docs/）
    --doc-dir DIR            文档目录（默认 dev_docs/）
    --output FILE            JSON 输出（默认 stdout）
    --timeout SECONDS        子工具超时（默认 30）

输出格式：
    {
      "summary": {"file": "...", "modes": [...], "passed": true},
      "checks": {
        "file_paths":    {"checked": N, "issues": [...]},
        "code_samples":  {"checked": N, "issues": [...]},
        "dependencies":  {"checked": N, "issues": [...]},
        "frontmatter":   {"checked": N, "issues": [...]}
      }
    }

退出码：
    - 0: 健康（无 issue）
    - 1: 发现问题
    - 2: 工具或参数错误

设计决策（V3.0 红线）：
    - 零依赖：仅标准库 + subprocess 调用其他 tools/py/*.py
    - 双脚本对称：与 tools/js/doc_health_checker.js 完全镜像
    - Hybrid 模式：delegate > 重写；编排 > 实现
    - 现有工具复用：doc_dependency_tracer / summary_validator
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS_PY = ROOT / "tools" / "py"
CONTRACTS_DIR = ROOT / "core" / "contracts"


def _run_tool(args, timeout=30):
    """Subprocess 调用 framework 内 Python 工具。"""
    cmd = [sys.executable] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except Exception as e:
        return 2, "", str(e)


def check_file_paths(targets, timeout=30):
    """delegate 到 doc_dependency_tracer.py。targets 为文件列表。"""
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    for f in targets:
        if not Path(f).exists():
            issues.append({"file": f, "type": "doc_missing", "message": "目标文档不存在"})
            continue
        code, out, err = _run_tool([
            str(TOOLS_PY / "doc_dependency_tracer.py"),
            "--doc", f, "--strategy", "all", "--output-format", "json"
        ], timeout=timeout)
        if code not in (0, 1):
            issues.append({"file": f, "type": "tool_error", "message": err.strip()[:200]})
            continue
        try:
            data = json.loads(out) if out.strip() else {}
        except json.JSONDecodeError:
            data = {}
        broken = data.get("broken_references", []) or data.get("missing_files", []) or []
        for b in broken:
            issues.append({"file": f, "type": "broken_link", "target": b})
    return {"checked": len(targets), "issues": issues}


def _extract_code_blocks(text):
    """提取 ```lang ... ``` 块；返回 [(lang, content)]。"""
    pattern = re.compile(r"```([a-zA-Z0-9_+\-]*)\n(.*?)```", re.DOTALL)
    return [(m.group(1).lower() or "text", m.group(2)) for m in pattern.finditer(text)]


def _check_python_block(code):
    """最小语法检查：compile 失败即报错。"""
    try:
        compile(code, "<doc-block>", "exec")
        return None
    except SyntaxError as e:
        return f"SyntaxError L{e.lineno}: {e.msg}"


def _check_bash_block(code):
    """轻量校验：检查命令首词是否在 PATH（仅前 5 行）。"""
    issues = []
    for i, line in enumerate(code.splitlines()[:5], 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("$"):
            continue
        first = line.split()[0]
        if first in ("python", "node", "git", "cd", "ls", "cat", "echo", "test", "for"):
            continue
        if "/" in first or first.endswith(".py") or first.endswith(".js"):
            continue
        # 不深查；记录为 informational
        if first in ("rm", "sudo", "kill"):
            issues.append(f"L{i}: 危险命令 {first}")
    return "; ".join(issues) if issues else None


def check_code_samples(targets):
    """提取代码块并执行最小语法检查。"""
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    blocks_total = 0
    for f in targets:
        if not Path(f).exists():
            continue
        try:
            text = Path(f).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            issues.append({"file": f, "type": "read_error", "message": str(e)[:100]})
            continue
        for idx, (lang, code) in enumerate(_extract_code_blocks(text)):
            blocks_total += 1
            err = None
            if lang in ("python", "py", "python3"):
                err = _check_python_block(code)
            elif lang in ("bash", "sh", "shell"):
                err = _check_bash_block(code)
            # JS / TS / 其他暂不检查（避免误报）
            if err:
                issues.append({"file": f, "type": "code_sample", "block": idx, "lang": lang, "message": err})
    return {"checked": blocks_total, "issues": issues}


_DEP_PATTERNS = [
    re.compile(r"\b([a-zA-Z][\w\-]*)\s*[~^>=]+\s*([0-9][\w\.\-]*)"),
]


def check_dependencies(targets, project_root=None):
    """对照 package.json / requirements.txt 与文档中"版本号"提及。"""
    if not targets:
        return {"checked": 0, "issues": []}
    project_root = Path(project_root or ROOT)
    declared = {}
    pkg = project_root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            for k in ("dependencies", "devDependencies"):
                declared.update(data.get(k) or {})
        except Exception:
            pass
    req = project_root / "requirements.txt"
    if req.exists():
        for line in req.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"([A-Za-z][\w\-]*)\s*[~=<>]=?\s*([\w\.\-]+)", line)
            if m:
                declared[m.group(1)] = m.group(2)
    issues = []
    for f in targets:
        if not Path(f).exists():
            continue
        text = Path(f).read_text(encoding="utf-8", errors="ignore")
        for pat in _DEP_PATTERNS:
            for m in pat.finditer(text):
                name, ver = m.group(1), m.group(2)
                actual = declared.get(name)
                if actual and actual.lstrip("^~>=<") != ver.lstrip("^~>=<"):
                    issues.append({"file": f, "type": "dep_version_drift", "package": name, "doc_says": ver, "manifest_says": actual})
    return {"checked": len(targets), "issues": issues}


def check_frontmatter(targets, timeout=30):
    """delegate 到 summary_validator.py --strict。"""
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    checked = 0
    for f in targets:
        path = Path(f)
        if "_analysis" in path.parts:
            try:
                has_frontmatter = path.read_text(encoding="utf-8", errors="ignore").lstrip().startswith("---")
            except OSError:
                has_frontmatter = False
            if not has_frontmatter:
                continue
        checked += 1
        code, out, err = _run_tool([
            str(TOOLS_PY / "summary_validator.py"),
            "--file", f, "--strict"
        ], timeout=timeout)
        if not out.strip():
            issues.append({"file": f, "type": "tool_error", "message": err.strip()[:200]})
            continue
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            issues.append({"file": f, "type": "tool_error", "message": "non-JSON output"})
            continue
        if not data.get("data", {}).get("valid"):
            for e in data.get("data", {}).get("errors", []):
                issues.append({"file": f, "type": "frontmatter", "message": e})
    return {"checked": checked, "issues": issues}


def _extract_yaml_list_items(lines, anchor):
    items = []
    capture = False
    base_indent = None
    for line in lines:
        if not capture:
            if line.strip() == anchor:
                capture = True
            continue
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if base_indent is None and line.lstrip().startswith("- "):
            base_indent = indent
        if base_indent is not None and indent < base_indent:
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip('"'))
    return items


def _load_main_doc_required_titles():
    contract_path = CONTRACTS_DIR / "main_doc_contract.yaml"
    if not contract_path.exists():
        return []
    titles = []
    for line in contract_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\s*title:\s*"?(.*?)"?\s*$', line)
        if m:
            titles.append(m.group(1))
    return titles


def _load_run_record_contract():
    contract_path = CONTRACTS_DIR / "run_record_contract.yaml"
    if not contract_path.exists():
        return {"generation_plan": [], "generation_progress": []}
    lines = contract_path.read_text(encoding="utf-8").splitlines()
    docs = {"generation_plan": [], "generation_progress": []}
    current_doc = None
    current_key = None
    for line in lines:
        any_doc_match = re.match(r"\s{2}([A-Za-z0-9_]+):\s*$", line)
        if any_doc_match and any_doc_match.group(1) not in docs:
            current_doc = None
            current_key = None
            continue
        doc_match = re.match(r"\s{2}(generation_plan|generation_progress):\s*$", line)
        if doc_match:
            current_doc = doc_match.group(1)
            current_key = None
            continue
        key_match = re.match(r"\s{4}(required_headings|required_fields):\s*$", line)
        if key_match and current_doc:
            current_key = key_match.group(1)
            continue
        item_match = re.match(r'\s{6}-\s*"(.*?)"\s*$', line)
        if item_match and current_doc and current_key:
            docs[current_doc].append(item_match.group(1))
    return docs


def _extract_h2_titles(text):
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]


def check_required_sections(targets):
    required_titles = _load_main_doc_required_titles()
    if not targets or not required_titles:
        return {"checked": 0, "issues": []}
    issues = []
    checked = 0
    for f in targets:
        if Path(f).name != "AI_Coding_Context.md" or not Path(f).exists():
            continue
        checked += 1
        text = Path(f).read_text(encoding="utf-8", errors="ignore")
        headings = set(_extract_h2_titles(text))
        for title in required_titles:
            if title not in headings:
                issues.append({
                    "file": f,
                    "type": "missing_required_section",
                    "section": title,
                    "message": f"缺少必需章节: {title}",
                })
    return {"checked": checked, "issues": issues}


_RESIDUE_PATTERNS = [
    (re.compile(r"\[填写\]"), "[填写]"),
    (re.compile(r"\[PROJECT_NAME\]"), "[PROJECT_NAME]"),
    (re.compile(r"\bTODO\b"), "TODO"),
    (re.compile(r"待补充"), "待补充"),
    (re.compile(r"^\|\s*\.\.\.\s*\|", re.MULTILINE), "ellipsis_table_row"),
]


def _is_template_residue_scan_line(line):
    stripped = line.strip()
    if "rg " not in stripped and "ripgrep" not in stripped:
        return False
    scan_markers = ("<marker:T-O-D-O>", "<marker:T-B-D>", "<marker:fill>", "待补充", "TODO", "TBD")
    return any(marker in stripped for marker in scan_markers)


def _template_residue_exempt_lines(lines):
    exempt = set()
    in_fence = False
    fence_start = ""
    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_start = stripped.lower()
            else:
                in_fence = False
                fence_start = ""
            continue
        if _is_template_residue_scan_line(line):
            if in_fence and any(lang in fence_start for lang in ("bash", "sh", "shell", "zsh", "console")):
                exempt.add(index)
            elif stripped.startswith("|") and stripped.endswith("|"):
                exempt.add(index)
            elif "`" in stripped:
                exempt.add(index)
    return exempt


def check_template_residue(targets):
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    checked = 0
    for f in targets:
        if not Path(f).exists():
            continue
        checked += 1
        text = Path(f).read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        exempt_lines = _template_residue_exempt_lines(lines)
        for pattern, label in _RESIDUE_PATTERNS:
            for match in pattern.finditer(text):
                lineno = text[:match.start()].count("\n") + 1
                if lineno in exempt_lines:
                    continue
                issues.append({
                    "file": f,
                    "type": "template_residue",
                    "marker": label,
                    "line": lineno,
                    "message": f"检测到模板残留: {label}",
                })
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "..." or stripped == "- ...":
                issues.append({
                    "file": f,
                    "type": "template_residue",
                    "marker": "...",
                    "line": idx,
                    "message": "检测到省略型占位符",
                })
    return {"checked": checked, "issues": issues}


PHASE1_REVIEW_FIELDS = [
    "review_trigger",
    "review_started_at",
    "review_completed_at",
    "reviewed_files",
    "machine_checks",
    "manual_review_summary",
    "writeback_summary",
    "blocker_count",
    "warning_count",
    "waived_issue_count",
    "phase1_recommendation",
    "user_confirmation_status",
    "formal_generation_authorization",
    "authorization_source_summary",
]

PHASE1_REQUIRED_TOOL_IMPLEMENTATIONS = {
    ("summary_validator", "python"),
    ("doc_health_checker", "python"),
    ("doc_health_checker", "js"),
    ("semantic_review_checker", "python"),
    ("semantic_review_checker", "js"),
}

HEALTH_CHECK_REQUIRED_TOOLS = {
    ("summary_validator", "python"),
    ("doc_health_checker", "python"),
    ("doc_health_checker", "js"),
    ("semantic_review_checker", "python"),
    ("semantic_review_checker", "js"),
}

ACCEPTED_ISSUE_REQUIRED_FIELDS = [
    "issue_id",
    "tool",
    "implementation",
    "file",
    "issue_type",
    "original_status",
    "accepted_reason",
    "residual_risk",
    "follow_up",
]

NON_WAIVABLE_ACCEPTED_ISSUE_TYPES = (
    "sensitive",
    "secret",
    "ai_rules",
    "runtime_stack",
    "required_doc",
    "doc_missing",
    "health_report",
)


def _is_phase1_pass_or_recommendation(text):
    if "Phase 1" not in text and "phase1" not in text.lower():
        return False
    return bool(re.search(r"\bPASS\b|verdict\s*=\s*PASS|建议通过|可进入正式文档生成", text, flags=re.IGNORECASE))


def _has_user_confirmation(text):
    return bool(re.search(r"当前状态\*\*:\s*已获用户确认|user_confirmation_status\*\*:\s*(confirmed|已确认)", text, flags=re.IGNORECASE))


def _has_formal_generation_authorization(text):
    patterns = (
        r"user_confirmation_status\*\*:\s*(confirmed|已确认)",
        r"当前状态\*\*:\s*已获用户确认",
        r"formal_generation_authorization\*\*:\s*(confirmed|explicit|已授权|已确认)",
        r"user_authorized_formal_generation\*\*:\s*(true|yes|是)",
        r"授权来源\s*[:：].*(用户|user)",
        r"明确授权跳过审核",
        r"用户确认.*正式文档生成",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _is_analysis_path(path):
    return "_analysis" in Path(path).parts


def _is_formal_doc_path(path):
    p = Path(path)
    if p.name in {"health_check_report.md"} or _is_analysis_path(p):
        return False
    if p.name in {"AI_Coding_Context.md", "AI_RULES.md"}:
        return True
    return True


def _formal_doc_paths(targets):
    paths = [Path(target) for target in targets if Path(target).exists() and Path(target).suffix == ".md" and _is_formal_doc_path(target)]
    if len(paths) <= 1 and all(path.name == "AI_Coding_Context.md" for path in paths):
        return []
    return paths


def _nearest_dev_docs_dir(path):
    current = path if path.is_dir() else path.parent
    for candidate in (current, *current.parents):
        if candidate.name == "dev_docs":
            return candidate
    return None


def _find_analysis_file_near_targets(targets, filename):
    for target in targets:
        path = Path(target)
        if not path.exists():
            continue
        dev_docs_dir = _nearest_dev_docs_dir(path)
        if not dev_docs_dir:
            continue
        candidate = dev_docs_dir / "_analysis" / filename
        if candidate.exists():
            return candidate
    return None


def _extract_section_after_heading(text, heading):
    match = re.search(rf"^##+\s+{re.escape(heading)}\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if not match:
        return ""
    next_match = re.search(r"^##+\s+", text[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end():end]


def _parse_first_markdown_table(section):
    rows = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            rows.append(stripped)
        elif rows:
            break
    if len(rows) < 2:
        return [], []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    body = []
    for row in rows[2:]:
        if re.match(r"^\|\s*-+", row):
            continue
        body.append([cell.strip() for cell in row.strip("|").split("|")])
    return headers, body


def _table_rows_as_dicts(headers, rows):
    return [
        {header: row[index] if index < len(row) else "" for index, header in enumerate(headers)}
        for row in rows
    ]


def _extract_final_verdict(text):
    match = re.search(r"(?:最终\s*)?verdict\*\*?\s*[:：]\s*\*{0,2}([A-Z_]+)", text, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"(?:最终\s*)?verdict\s*=\s*([A-Z_]+)", text, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).upper()


def _check_health_report_self_residue(path, text):
    issues = []
    for pattern, label in _RESIDUE_PATTERNS:
        for match in pattern.finditer(text):
            issues.append({
                "file": str(path),
                "type": "health_report_self_template_residue",
                "severity": "blocker",
                "marker": label,
                "line": _line_number(text, match.start()) if "_line_number" in globals() else text[:match.start()].count("\n") + 1,
                "message": f"健康报告自身包含模板残留: {label}",
            })
    return issues


def _check_accepted_issues_table(path, text, has_accepted_machine_check):
    issues = []
    section = _extract_section_after_heading(text, "accepted_issues")
    if not section:
        if has_accepted_machine_check or "accepted" in text.lower():
            issues.append({
                "file": str(path),
                "type": "health_report_accepted_issue_missing_detail",
                "severity": "blocker",
                "message": "存在 accepted issue，但缺少 accepted_issues 结构化章节",
            })
        return issues
    if "无 accepted issue" in section and not has_accepted_machine_check:
        return issues
    headers, rows = _parse_first_markdown_table(section)
    if not headers:
        if has_accepted_machine_check:
            issues.append({
                "file": str(path),
                "type": "health_report_accepted_issue_missing_detail",
                "severity": "blocker",
                "message": "accepted_issues 必须使用可解析表格逐项记录",
            })
        return issues
    missing = [field for field in ACCEPTED_ISSUE_REQUIRED_FIELDS if field not in headers]
    if missing:
        issues.append({
            "file": str(path),
            "type": "health_report_accepted_issue_missing_detail",
            "severity": "blocker",
            "missing": missing,
            "message": "accepted_issues 表缺少必填列",
        })
        return issues
    for row in _table_rows_as_dicts(headers, rows):
        empty_fields = [field for field in ACCEPTED_ISSUE_REQUIRED_FIELDS if not row.get(field)]
        if empty_fields:
            issues.append({
                "file": str(path),
                "type": "health_report_accepted_issue_missing_detail",
                "severity": "blocker",
                "issue_id": row.get("issue_id"),
                "missing": empty_fields,
                "message": "accepted issue 缺少原因、残余风险或 follow-up 等必填信息",
            })
        issue_type = row.get("issue_type", "").lower()
        if any(marker in issue_type for marker in NON_WAIVABLE_ACCEPTED_ISSUE_TYPES):
            issues.append({
                "file": str(path),
                "type": "health_report_accepted_issue_not_allowed",
                "severity": "blocker",
                "issue_id": row.get("issue_id"),
                "issue_type": row.get("issue_type"),
                "message": "该类型问题不得通过 accepted issue 豁免",
            })
    return issues


def _check_health_report(path, text, target_count):
    issues = []
    verdict = _extract_final_verdict(text)
    section = _extract_section_after_heading(text, "machine_checks")
    headers, rows = _parse_first_markdown_table(section)
    if not headers:
        issues.append({
            "file": str(path),
            "type": "health_report_machine_checks_missing",
            "severity": "blocker",
            "message": "health_check_report.md 缺少结构化 machine_checks 表",
        })
        return issues
    required = ["round", "tool", "implementation", "command", "exit_code", "issue_count", "status", "disposition"]
    missing = [field for field in required if field not in headers]
    if missing:
        issues.append({
            "file": str(path),
            "type": "health_report_machine_checks_missing",
            "severity": "blocker",
            "missing": missing,
            "message": "health_check_report.md 的 machine_checks 表缺少必需列",
        })
        return issues
    machine_rows = _table_rows_as_dicts(headers, rows)
    seen = {(row.get("tool"), row.get("implementation")) for row in machine_rows}
    for tool, implementation in sorted(HEALTH_CHECK_REQUIRED_TOOLS):
        if (tool, implementation) not in seen:
            issues.append({
                "file": str(path),
                "type": "health_report_machine_checks_missing",
                "severity": "blocker",
                "tool": tool,
                "implementation": implementation,
                "message": f"health_check_report.md 缺少 {implementation} {tool} 运行记录",
            })
    has_failed = False
    has_accepted = False
    has_unaccepted_failure = False
    for row in machine_rows:
        exit_code_text = row.get("exit_code", "")
        issue_count_text = row.get("issue_count", "")
        status = row.get("status", "").upper()
        disposition = row.get("disposition", "").lower()
        if not re.fullmatch(r"\d+", exit_code_text) or not re.fullmatch(r"\d+", issue_count_text):
            issues.append({
                "file": str(path),
                "type": "health_report_machine_checks_missing",
                "severity": "blocker",
                "message": "machine_checks exit_code 与 issue_count 必须为数字",
            })
            continue
        failed = int(exit_code_text) != 0 or int(issue_count_text) != 0 or status in {"FAIL", "ERROR"}
        if failed:
            has_failed = True
            if disposition == "accepted":
                has_accepted = True
            elif disposition not in {"fixed", "verified"}:
                has_unaccepted_failure = True
    if verdict == "PASS" and (has_failed or has_accepted):
        issues.append({
            "file": str(path),
            "type": "health_report_verdict_conflicts_with_checks",
            "severity": "blocker",
            "message": "health_check_report.md 写 PASS，但 machine_checks 存在失败或 accepted issue",
        })
    if verdict in {"PASS", "PASS_WITH_ACCEPTED_ISSUES", "建议通过"} and has_unaccepted_failure:
        issues.append({
            "file": str(path),
            "type": "health_report_verdict_conflicts_with_checks",
            "severity": "blocker",
            "message": "health_check_report.md 存在未修复/未豁免的失败检查",
        })
    if has_accepted and verdict == "PASS":
        issues.append({
            "file": str(path),
            "type": "health_report_verdict_conflicts_with_checks",
            "severity": "blocker",
            "message": "存在 accepted issue 时最终结论不得写裸 PASS",
        })
    issues.extend(_check_accepted_issues_table(path, text, has_accepted))
    issues.extend(_check_health_report_self_residue(path, text))
    for match in re.finditer(r"全部\s*(\d+)\s*个(?:产物|文档)|已完成\s*(\d+)\s*/\s*(\d+)\s*个产物|总文件数\s*(\d+)", text):
        expected = int(match.group(1) or match.group(3) or match.group(4))
        if expected != target_count:
            issues.append({
                "file": str(path),
                "type": "artifact_count_mismatch",
                "severity": "blocker",
                "expected": expected,
                "actual": target_count,
                "message": "健康报告或进度记录中的产物数量与实际 Markdown 文件数量不一致",
            })
    return issues


def _check_machine_checks_table(path, text, phase1_pass):
    issues = []
    section = _extract_section_after_heading(text, "machine_checks")
    headers, rows = _parse_first_markdown_table(section)
    if not headers:
        issues.append({
            "file": str(path),
            "type": "machine_check_table_missing",
            "severity": "blocker",
            "message": "Phase 1 建议通过时必须用可解析表格记录 machine_checks",
        })
        return issues
    required = ["phase", "tool", "implementation", "command", "exit_code", "issue_count", "status", "required", "disposition"]
    missing = [field for field in required if field not in headers]
    if missing:
        issues.append({
            "file": str(path),
            "type": "machine_check_table_column_missing",
            "severity": "blocker",
            "missing": missing,
            "message": "machine_checks 表缺少必需列",
        })
        return issues
    machine_rows = _table_rows_as_dicts(headers, rows)
    seen = {(row.get("tool"), row.get("implementation")) for row in machine_rows}
    for required_tool, required_implementation in sorted(PHASE1_REQUIRED_TOOL_IMPLEMENTATIONS):
        if (required_tool, required_implementation) not in seen:
            issues.append({
                "file": str(path),
                "type": "machine_check_required_tool_missing",
                "severity": "blocker",
                "tool": required_tool,
                "implementation": required_implementation,
                "message": f"machine_checks 缺少工具运行记录: {required_implementation} {required_tool}",
            })
    has_required_failure = False
    for row in machine_rows:
        if not re.fullmatch(r"\d+", row.get("exit_code", "")):
            issues.append({
                "file": str(path),
                "type": "machine_check_exit_code_missing",
                "severity": "blocker",
                "message": "machine_checks exit_code 必须为数字",
            })
        if not re.fullmatch(r"\d+", row.get("issue_count", "")):
            issues.append({
                "file": str(path),
                "type": "machine_check_issue_count_mismatch",
                "severity": "blocker",
                "message": "machine_checks issue_count 必须为数字",
            })
        status = row.get("status", "").upper()
        disposition = row.get("disposition", "")
        required_value = row.get("required", "").lower()
        if required_value == "yes" and status != "PASS":
            has_required_failure = True
        if status in {"FAIL", "ERROR", "UNAVAILABLE", "NOT_RUN"} and not disposition:
            issues.append({
                "file": str(path),
                "type": "machine_check_unresolved_failure",
                "severity": "blocker",
                "message": "失败的 machine_checks 行必须说明 disposition",
            })
    verdict = _extract_phase1_verdict(text)
    if phase1_pass and has_required_failure and verdict != "BLOCKED_NEEDS_FIX":
        issues.append({
            "file": str(path),
            "type": "phase1_verdict_conflicts_with_machine_checks",
            "severity": "blocker",
            "message": "存在 required machine check 失败时，phase1_review_verdict 必须为 BLOCKED_NEEDS_FIX",
        })
    return issues


def _extract_phase1_verdict(text):
    section = _extract_section_after_heading(text, "phase1_review_verdict")
    if section:
        headers, rows = _parse_first_markdown_table(section)
        for row in _table_rows_as_dicts(headers, rows):
            if row.get("field") == "verdict":
                return row.get("value", "").strip().upper()
    match = re.search(r"phase1_review_verdict[^\n]*(BLOCKED_NEEDS_FIX|READY_FOR_USER_REVIEW|USER_APPROVED_FORMAL_GENERATION)", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _check_checker_status_conflicts(path, text):
    issues = []
    if "checker_status_matrix" not in text or "machine_checks" not in text:
        return issues
    status_by_tool = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        for tool in ("summary_validator", "doc_health_checker", "semantic_review_checker", "health_check_report"):
            if tool not in line:
                continue
            status_match = re.search(r"\b(PASS|FAIL|NOT_RUN|UNAVAILABLE|WAIVED_WITH_REASON)\b", line)
            if status_match:
                status_by_tool.setdefault(tool, set()).add(status_match.group(1))
    for tool, statuses in status_by_tool.items():
        if "NOT_RUN" in statuses and ("PASS" in statuses or "FAIL" in statuses):
            issues.append({
                "file": str(path),
                "type": "checker_status_matrix_conflict",
                "severity": "blocker",
                "tool": tool,
                "statuses": sorted(statuses),
                "message": "同一工具在 checker_status_matrix 和 machine_checks 中出现 NOT_RUN 与已运行状态冲突",
            })
    return issues


def _check_phase1_review_record(path, text):
    issues = []
    phase1_pass = _is_phase1_pass_or_recommendation(text)
    has_record = "Phase 1 方案复查记录" in text
    if phase1_pass and not has_record:
        issues.append({
            "file": str(path),
            "type": "phase1_pass_without_plan_review_record",
            "severity": "blocker",
            "message": "进度记录声明 Phase 1 PASS/建议通过，但缺少 Phase 1 方案复查记录",
        })
    if has_record:
        for field in PHASE1_REVIEW_FIELDS:
            if field not in text:
                issue_type = "phase1_plan_review_writeback_missing" if field == "writeback_summary" else "phase1_plan_review_record_missing"
                issues.append({
                    "file": str(path),
                    "type": issue_type,
                    "severity": "blocker" if phase1_pass else "warning",
                    "missing": field,
                    "message": f"Phase 1 方案复查记录缺少字段: {field}",
                })
        if "phase1_review_verdict" not in text:
            issues.append({
                "file": str(path),
                "type": "phase1_review_verdict_missing",
                "severity": "blocker" if phase1_pass else "warning",
                "message": "Phase 1 方案复查记录缺少 phase1_review_verdict",
            })
        else:
            verdict = _extract_phase1_verdict(text)
            if verdict not in {"BLOCKED_NEEDS_FIX", "READY_FOR_USER_REVIEW", "USER_APPROVED_FORMAL_GENERATION"}:
                issues.append({
                    "file": str(path),
                    "type": "phase1_review_verdict_invalid",
                    "severity": "blocker",
                    "verdict": verdict,
                    "message": "phase1_review_verdict 取值不合法",
                })
            if verdict == "USER_APPROVED_FORMAL_GENERATION" and not _has_user_confirmation(text):
                issues.append({
                    "file": str(path),
                    "type": "phase1_approved_without_user_confirmation",
                    "severity": "blocker",
                    "message": "没有用户确认时不得记录 USER_APPROVED_FORMAL_GENERATION",
                })
        issues.extend(_check_machine_checks_table(path, text, phase1_pass))
        issues.extend(_check_checker_status_conflicts(path, text))
    if phase1_pass and "可进入正式文档生成" in text and not _has_user_confirmation(text):
        issues.append({
            "file": str(path),
            "type": "phase1_pass_before_user_confirmation",
            "severity": "blocker",
            "message": "用户确认前不得将 Phase 1 建议通过表述为可进入正式文档生成",
        })
    return issues


def check_run_record_integrity(targets):
    contracts = _load_run_record_contract()
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    checked = 0
    target_count = len([target for target in targets if Path(target).exists() and Path(target).suffix == ".md"])
    target_by_name = {Path(target).name: Path(target) for target in targets if Path(target).exists()}
    health_report_path = target_by_name.get("health_check_report.md") or _find_analysis_file_near_targets(targets, "health_check_report.md")
    formal_docs = _formal_doc_paths(targets)
    main_doc_path = target_by_name.get("AI_Coding_Context.md")
    if health_report_path and main_doc_path and not formal_docs:
        formal_docs = [main_doc_path]
    progress_text = ""
    progress_path = target_by_name.get("generation_progress.md")
    if progress_path:
        progress_text = progress_path.read_text(encoding="utf-8", errors="ignore")
    if formal_docs and not health_report_path:
        issues.append({
            "file": str(progress_path) if progress_path else str(formal_docs[0]),
            "type": "formal_docs_without_health_report",
            "severity": "blocker",
            "formal_docs": [str(path) for path in formal_docs],
            "message": "正式文档已生成，但缺少 dev_docs/_analysis/health_check_report.md",
        })
    if formal_docs and progress_text and not _has_formal_generation_authorization(progress_text):
        issues.append({
            "file": str(progress_path),
            "type": "formal_docs_generated_without_phase1_confirmation",
            "severity": "blocker",
            "formal_docs": [str(path) for path in formal_docs],
            "message": "正式文档已生成，但 generation_progress.md 缺少用户确认或明确授权记录",
        })
    health_report_issues = []
    health_report_verdict = ""
    if health_report_path:
        checked += 1
        health_text = health_report_path.read_text(encoding="utf-8", errors="ignore")
        health_report_verdict = _extract_final_verdict(health_text)
        health_report_issues = _check_health_report(health_report_path, health_text, target_count)
        issues.extend(health_report_issues)
    for f in targets:
        path = Path(f)
        if path.name not in ("generation_plan.md", "generation_progress.md") or not path.exists():
            continue
        checked += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        required_items = contracts["generation_plan"] if path.name == "generation_plan.md" else contracts["generation_progress"]
        for item in required_items:
            if item not in text:
                issues.append({
                    "file": f,
                    "type": "run_record_integrity",
                    "missing": item,
                    "message": f"运行记录缺少必需项: {item}",
                })
        current_status_match = re.search(r"\*\*当前状态\*\*:\s*([^\n]+)", text)
        current_status = current_status_match.group(1).strip() if current_status_match else ""
        if path.name == "generation_progress.md" and current_status == "已完成" and "health_check_report" not in text:
            issues.append({
                "file": f,
                "type": "run_record_integrity",
                "missing": "health_check_report",
                "message": "进度记录声明已完成，但未见 health_check_report 留痕",
            })
        if path.name == "generation_progress.md":
            has_summary_validator_pass = re.search(r"summary_validator[^\n|]*(?:PASS|通过)", text, flags=re.IGNORECASE)
            claims_validation_passed = re.search(r"验证(?:已)?通过|检查(?:已)?通过|验收(?:已)?通过", text)
            has_required_quality_tools = "doc_health_checker" in text and "semantic_review_checker" in text
            if has_summary_validator_pass and claims_validation_passed and not has_required_quality_tools:
                issues.append({
                    "file": f,
                    "type": "summary_only_validation_misrepresented",
                    "severity": "blocker",
                    "message": "进度记录只记录 summary_validator 通过，却表述为整体验证通过",
                })
            first_release_done = any(marker in text for marker in ("首版建议通过", "首版验收 verdict = PASS", "首版验收完成", "Step 9/9 已完成"))
            if first_release_done and not health_report_path:
                issues.append({
                    "file": f,
                    "type": "progress_completion_without_valid_health_report",
                    "severity": "blocker",
                    "message": "进度记录声明首版完成或建议通过，但缺少 health_check_report.md",
                })
            if first_release_done and health_report_path and (health_report_issues or health_report_verdict in {"FAIL", ""}):
                issues.append({
                    "file": f,
                    "type": "progress_completion_without_valid_health_report",
                    "severity": "blocker",
                    "message": "进度记录声明首版完成或建议通过，但健康报告未通过结构化验收",
                })
            for match in re.finditer(r"全部\s*(\d+)\s*个(?:产物|文档)|已完成\s*(\d+)\s*/\s*(\d+)\s*个产物|总文件数\s*(\d+)", text):
                expected = int(match.group(1) or match.group(3) or match.group(4))
                if expected != target_count:
                    issues.append({
                        "file": f,
                        "type": "artifact_count_mismatch",
                        "severity": "blocker",
                        "expected": expected,
                        "actual": target_count,
                        "message": "进度记录中的产物数量与实际 Markdown 文件数量不一致",
                    })
            issues.extend(_check_phase1_review_record(path, text))
            last_updates = re.findall(r"\*\*最后更新\*\*:\s*([^\n]+)", text)
            if len(set(last_updates)) > 1:
                issues.append({
                    "file": f,
                    "type": "progress_metadata_mismatch",
                    "field": "最后更新",
                    "values": sorted(set(last_updates)),
                    "message": "进度记录中存在多个不一致的最后更新时间",
                })
            progress_labels = re.findall(r"\*\*([^*\n]*进度[^*\n]*)\*\*:\s*[^\n]*\d+%", text)
            ambiguous = [label for label in progress_labels if label.strip() == "进度"]
            if len(ambiguous) > 1:
                issues.append({
                    "file": f,
                    "type": "ambiguous_progress_percentage",
                    "message": "同一进度文件中存在多个未标明含义的百分比进度",
                })
        if path.name == "generation_plan.md":
            if "Package.resolved" in text and any(marker in text for marker in ("Package.resolved 待确认", "检查 Package.resolved", "未发现 Package.resolved")):
                issues.append({
                    "file": f,
                    "type": "stale_review_conclusion",
                    "fact": "Package.resolved",
                    "message": "文档已引用 Package.resolved，但正文仍残留依赖待确认旧结论",
                })
    return {"checked": checked, "issues": issues}


def _collect_targets(args):
    """根据 --file / --doc-dir 决定检查目标。

    Fallback 优先级（与 B3#021 同源 dogfood 治理）：
      1. CLI 显式 --doc-dir 指定 → 使用之
      2. dev_docs/ 存在（用户项目场景）
      3. dev/ 存在（框架自审 / dogfood 场景）
      4. 当前目录
    """
    if args.file:
        return [args.file]
    if args.doc_dir:
        candidates = [Path(args.doc_dir)]
    else:
        candidates = [ROOT / "dev_docs", ROOT / "dev", Path(".")]
    for d in candidates:
        if d.exists() and d.is_dir():
            return [str(p) for p in d.rglob("*.md")]
    return []


def main():
    p = argparse.ArgumentParser(description="AICC 文档健康检查工具（hybrid orchestrator）")
    p.add_argument("--file", help="单文件子集检查")
    p.add_argument("--mode", choices=["quick", "standard", "deep"], help="预设模式")
    p.add_argument("--check-file-paths", action="store_true")
    p.add_argument("--check-code-samples", action="store_true")
    p.add_argument("--check-dependencies", action="store_true")
    p.add_argument("--check-required-sections", action="store_true")
    p.add_argument("--check-template-residue", action="store_true")
    p.add_argument("--check-run-record-integrity", action="store_true")
    p.add_argument("--full-check", action="store_true", help="综合检查（mode deep × 全文档目录）")
    p.add_argument("--doc-dir", help="文档目录（默认 dev_docs/）")
    p.add_argument("--output", help="JSON 输出文件")
    p.add_argument("--timeout", type=int, default=30, help="子工具超时秒数")
    args = p.parse_args()

    # 决定要执行哪些检查
    do_paths = bool(args.check_file_paths or args.full_check or args.mode in ("quick", "standard", "deep") or args.file)
    do_samples = bool(args.check_code_samples or args.full_check or args.mode in ("standard", "deep") or args.file)
    do_deps = bool(args.check_dependencies or args.full_check or args.mode == "deep")
    do_fm = bool(args.full_check or args.mode == "deep" or args.file)
    do_required = bool(args.check_required_sections or args.full_check or args.mode == "deep")
    do_residue = bool(args.check_template_residue or args.full_check or args.mode == "deep")
    do_run_records = bool(args.check_run_record_integrity or args.full_check or args.mode == "deep")

    if not any([do_paths, do_samples, do_deps, do_fm, do_required, do_residue, do_run_records]):
        p.error("请提供 --file / --mode / --check-* / --full-check 之一")

    targets = _collect_targets(args)
    if not targets:
        print(json.dumps({"summary": {"passed": False}, "error": "no targets found"}, ensure_ascii=False))
        sys.exit(2)

    checks = {}
    if do_paths:
        checks["file_paths"] = check_file_paths(targets, timeout=args.timeout)
    if do_samples:
        checks["code_samples"] = check_code_samples(targets)
    if do_deps:
        checks["dependencies"] = check_dependencies(targets)
    if do_fm:
        checks["frontmatter"] = check_frontmatter(targets, timeout=args.timeout)
    if do_required:
        checks["required_sections"] = check_required_sections(targets)
    if do_residue:
        checks["template_residue"] = check_template_residue(targets)
    if do_run_records:
        checks["run_record_integrity"] = check_run_record_integrity(targets)

    total_issues = sum(len(v["issues"]) for v in checks.values())
    summary = {
        "file": args.file,
        "doc_dir": args.doc_dir or "dev_docs",
        "modes": {"file": bool(args.file), "mode": args.mode, "full_check": args.full_check},
        "targets_count": len(targets),
        "total_issues": total_issues,
        "passed": total_issues == 0
    }
    result = {"summary": summary, "checks": checks}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    sys.exit(0 if total_issues == 0 else 1)


if __name__ == "__main__":
    main()
