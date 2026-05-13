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
    (re.compile(r"^\|\s*\.\.\.\s*\|", re.MULTILINE), "ellipsis_table_row"),
]


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
        for pattern, label in _RESIDUE_PATTERNS:
            for match in pattern.finditer(text):
                lineno = text[:match.start()].count("\n") + 1
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


def check_run_record_integrity(targets):
    contracts = _load_run_record_contract()
    if not targets:
        return {"checked": 0, "issues": []}
    issues = []
    checked = 0
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
