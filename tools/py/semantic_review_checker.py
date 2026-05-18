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


POSITIVE_KEYWORDS = ["推荐", "必须", "优先", "建议", "should", "recommended", "prefer", "需要", "统一", "集中", "centralize"]
NEGATIVE_KEYWORDS = ["不建议", "不要", "禁止", "deprecated", "废弃", "avoid", "do not", "should not", "not be edited", "不需要", "无需"]
SOURCE_SUFFIXES = {".md", ".py", ".js", ".ts", ".tsx", ".swift"}
FRAMEWORK_DIR_NAMES = {"AI-Coding-Context", "ai_coding_context", "ai-coding-context", ".ai", ".git", "node_modules", "vendor", "storage"}
FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]


def _is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _is_project_scan_excluded(path, repo_root, doc_dir=None):
    resolved = path.resolve()
    repo_resolved = repo_root.resolve()
    fixture_root = FRAMEWORK_ROOT / "tools" / "testdata"
    try:
        rel_parts = path.relative_to(repo_root).parts
    except ValueError:
        rel_parts = path.parts
    rel_names = set(rel_parts)
    if rel_parts and rel_parts[0] in FRAMEWORK_DIR_NAMES:
        return True
    if "bootstrap" in rel_names and "cache" in rel_names:
        return True
    if doc_dir and _is_relative_to(resolved, doc_dir.resolve()):
        return True
    if _is_relative_to(resolved, FRAMEWORK_ROOT) and repo_resolved != FRAMEWORK_ROOT and not _is_relative_to(repo_resolved, fixture_root):
        return True
    if repo_resolved == FRAMEWORK_ROOT and _is_relative_to(resolved, fixture_root):
        return True
    return False


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
        if _is_project_scan_excluded(path, repo_root, doc_dir):
            continue
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if path.name == "README.md" or path in files:
            continue
        files.append(path)
    return sorted(set(files))


def scan_test_topology(repo_root):
    topology = []
    for path in repo_root.rglob("*"):
        if _is_project_scan_excluded(path, repo_root):
            continue
        if not path.is_dir():
            continue
        is_standard_test_dir = path.name in {"tests", "test", "integration_test", "__tests__", "spec", "androidTest"}
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
        if file_count == 0:
            continue
        topology.append({
            "path": path.relative_to(repo_root).as_posix() + "/",
            "file_count": file_count,
        })
    topology.sort(key=lambda item: item["path"])
    return topology


def count_files_under(repo_root, relative_path):
    target = repo_root / relative_path
    if not target.exists() or _is_project_scan_excluded(target, repo_root):
        return None
    if target.is_file():
        return 1
    return sum(1 for child in target.rglob("*") if child.is_file() and not _is_project_scan_excluded(child, repo_root))


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
    lower_line = line.lower()
    negative = any(_keyword_in_line(keyword, lower_line) for keyword in NEGATIVE_KEYWORDS)
    positive = any(_keyword_in_line(keyword, lower_line) for keyword in POSITIVE_KEYWORDS)
    if negative and not positive:
        return "negative"
    if positive and not negative:
        return "positive"
    if negative and positive:
        # 以显式否定优先
        return "negative"
    return None


def _keyword_in_line(keyword, lower_line):
    lower_keyword = keyword.lower()
    if re.fullmatch(r"[a-z ]+", lower_keyword):
        return bool(re.search(rf"(?<![a-z]){re.escape(lower_keyword)}(?![a-z])", lower_line))
    return lower_keyword in lower_line


def extract_anchors(line):
    anchors = re.findall(r"`([^`]+)`", line)
    return [anchor.strip() for anchor in anchors if anchor.strip()]


def collect_assertions(files):
    assertions = []
    for path in files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _is_attention_only_rule(line):
                continue
            anchors = extract_anchors(line)
            if not anchors:
                continue
            for anchor in anchors:
                polarity = _classify_anchor_polarity(line, anchor)
                if not polarity:
                    continue
                assertions.append({
                    "file": str(path),
                    "line": line_no,
                    "polarity": polarity,
                    "anchors": [anchor],
                    "text": line.strip(),
                })
    return assertions


def _is_attention_only_rule(line):
    lower = line.lower()
    return "sensitive keyword" in lower and "not necessarily wrong" in lower


def _classify_anchor_polarity(line, anchor):
    anchor_index = line.find(f"`{anchor}`")
    if anchor_index < 0:
        return classify_polarity(line)
    window = line[max(0, anchor_index - 80): anchor_index + len(anchor) + 80]
    return classify_polarity(window) or classify_polarity(line)


def _is_rule_anchor(anchor):
    lower = anchor.lower()
    return any(marker in lower for marker in ("*.g.dart", "generated", "router", "rules", "policy"))


def _fact_conflict_type(anchor):
    return "rule_conflict" if _is_rule_anchor(anchor) else "fact_conflict"


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
                "type": _fact_conflict_type(shared[0]),
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


def _load_package_deps(repo_root):
    package_path = repo_root / "package.json"
    if not package_path.exists():
        return {}
    try:
        data = json.loads(package_path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return {}
    deps = {}
    deps.update(data.get("dependencies") or {})
    deps.update(data.get("devDependencies") or {})
    return deps


def _major_version(version):
    match = re.search(r"(\d+)", version or "")
    return int(match.group(1)) if match else None


def _repo_uses_apache(repo_root):
    docker_text = []
    for path in repo_root.rglob("*Dockerfile*"):
        if _is_project_scan_excluded(path, repo_root):
            continue
        docker_text.append(path.read_text(encoding="utf-8", errors="ignore"))
    for name in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "config/supervisord.conf"):
        path = repo_root / name
        if path.exists() and not _is_project_scan_excluded(path, repo_root):
            docker_text.append(path.read_text(encoding="utf-8", errors="ignore"))
    combined = "\n".join(docker_text).lower()
    return "apache" in combined or "apache2-foreground" in combined


def _doc_mentions_nginx_php_fpm(text):
    return bool(re.search(r"Nginx\s*/\s*PHP-FPM|PHP-FPM\s*\+\s*Nginx|Nginx.*FastCGI", text, flags=re.IGNORECASE | re.DOTALL))


def _formal_markdown_files(doc_dir):
    return [path for path in iter_markdown_files(doc_dir) if "_analysis" not in path.parts]


def _read_formal_docs(doc_dir):
    chunks = []
    for path in _formal_markdown_files(doc_dir):
        chunks.append((path, path.read_text(encoding="utf-8", errors="ignore")))
    return chunks


def _vuex_module_names(repo_root):
    vuex_dir = repo_root / "resources" / "js" / "vuex"
    if not vuex_dir.exists():
        return set()
    names = set()
    for path in vuex_dir.glob("*.js"):
        stem = path.stem
        names.add(stem)
        names.add(stem[:1].lower() + stem[1:])
        names.add(stem.lower())
    return names


def _declares_redaction_policy(doc_dir):
    analysis_text = "\n".join(_read_if_exists(path) for path in (doc_dir / "_analysis").glob("*.md")) if (doc_dir / "_analysis").exists() else ""
    return any(marker in analysis_text for marker in ("脱敏", "不复述密码", "不复述", "Token", "密钥", "敏感"))


def _is_placeholder_value(value):
    stripped = value.strip().strip("`").strip()
    return not stripped or stripped.startswith("<") or stripped.startswith("${") or stripped.upper() in {"DB_PASSWORD", "PUSHER_APP_KEY", "REVERB_APP_KEY", "TOKEN", "PASSWORD"}


def check_first_release_acceptance(doc_dir, repo_root):
    issues = []
    deps = _load_package_deps(repo_root)
    vue_major = _major_version(deps.get("vue", ""))
    vuex_major = _major_version(deps.get("vuex", ""))
    uses_apache = _repo_uses_apache(repo_root)
    formal_docs = _read_formal_docs(doc_dir)
    ai_rules_path = doc_dir / "rules" / "combined" / "AI_RULES.md"
    ai_rules = _read_if_exists(ai_rules_path)

    if uses_apache:
        for doc_path, text in formal_docs:
            if _doc_mentions_nginx_php_fpm(text):
                issues.append({
                    "type": "runtime_stack_conflict",
                    "severity": "blocker",
                    "file": str(doc_path),
                    "message": "仓库 Docker/Supervisor 事实显示使用 Apache，但正式文档写成 Nginx/PHP-FPM",
                })
        if ai_rules and _doc_mentions_nginx_php_fpm(ai_rules):
            issues.append({
                "type": "ai_rules_runtime_stack_conflict",
                "severity": "blocker",
                "file": str(ai_rules_path),
                "message": "AI_RULES.md 的运行栈与 Dockerfile / Compose 事实冲突",
            })

    if ai_rules:
        if vuex_major and re.search(r"Vuex\s*4\b", ai_rules, flags=re.IGNORECASE) and vuex_major != 4:
            issues.append({
                "type": "ai_rules_dependency_version_conflict",
                "severity": "blocker",
                "file": str(ai_rules_path),
                "package": "vuex",
                "doc_says": "Vuex 4",
                "manifest_says": deps.get("vuex"),
                "message": "AI_RULES.md 写的 Vuex 版本与 package.json 冲突",
            })
        if vue_major and re.search(r"Vue\s*3\b|Vue\s*2\.7\b", ai_rules, flags=re.IGNORECASE) and vue_major == 2 and "Vue 2 + Vuex" not in ai_rules:
            issues.append({
                "type": "ai_rules_dependency_version_conflict",
                "severity": "blocker",
                "file": str(ai_rules_path),
                "package": "vue",
                "manifest_says": deps.get("vue"),
                "message": "AI_RULES.md 写的 Vue 版本与 package.json 冲突",
            })
        module_names = _vuex_module_names(repo_root)
        if module_names:
            module_line_match = re.search(r"(?:状态管理模块|按模块组织)[:：]\s*([^\n]+)", ai_rules)
            module_text = module_line_match.group(1) if module_line_match else ai_rules
            mentioned = set(re.findall(r"`([^`]+)`", module_text))
            mentioned.update(re.findall(r"\b(user_storage|theme)\b", module_text))
            invalid = sorted(name for name in mentioned if name not in module_names and "/" not in name and "." not in name)
            for name in invalid:
                issues.append({
                    "type": "ai_rules_state_module_conflict",
                    "severity": "blocker",
                    "file": str(ai_rules_path),
                    "module": name,
                    "message": "AI_RULES.md 写了源码中不存在的状态管理模块",
                })
        contributing = _read_if_exists(repo_root / "CONTRIBUTING.md").lower()
        if "please do not write any" in contributing and "test" in contributing and re.search(r"(补|新增|增加|默认).{0,12}(测试|test)", ai_rules, flags=re.IGNORECASE):
            issues.append({
                "type": "ai_rules_test_policy_conflict",
                "severity": "blocker",
                "file": str(ai_rules_path),
                "message": "AI_RULES.md 的测试建议与 CONTRIBUTING.md 冲突",
            })

    redaction_declared = _declares_redaction_policy(doc_dir)
    sensitive_line_pattern = re.compile(r"\b[A-Z0-9_]*(?:PASSWORD|TOKEN|SECRET|KEY)[A-Z0-9_]*\b[^`\n]{0,80}`([^`]+)`")
    secret_like_pattern = re.compile(r"`([A-Za-z0-9_-]{16,})`")
    for doc_path, text in formal_docs:
        for line_no, line in enumerate(text.splitlines(), 1):
            if "只列变量名" in line or ("变量名" in line and not any(marker in line for marker in ("默认值", "值为", "密码为", "key 为", "KEY 为"))):
                continue
            for match in sensitive_line_pattern.finditer(line):
                value = match.group(1)
                if _is_placeholder_value(value):
                    continue
                issue_type = "sensitive_policy_declared_but_violated" if redaction_declared else "sensitive_default_value_repeated"
                issues.append({
                    "type": issue_type,
                    "severity": "blocker",
                    "file": str(doc_path),
                    "line": line_no,
                    "message": "正式文档复述了密码、Token、key 或默认敏感值",
                })
            for match in secret_like_pattern.finditer(line):
                value = match.group(1)
                if _is_placeholder_value(value) or value.upper().endswith("_KEY"):
                    continue
                if re.search(r"\b[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*\b|Pusher|Reverb|PUSHER|REVERB", line):
                    issues.append({
                        "type": "secret_like_value_in_docs",
                        "severity": "blocker",
                        "file": str(doc_path),
                        "line": line_no,
                        "message": "正式文档出现疑似 token/key/password 具体值",
                    })
    return issues


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


def _section_text(text, heading):
    pattern = re.compile(rf"^##+\s+.*{re.escape(heading)}.*$", flags=re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", text[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end():end]


def _markdown_tables(section):
    tables = []
    current = []
    for line in section.splitlines():
        if line.strip().startswith("|") and line.strip().endswith("|"):
            current.append(line.strip())
            continue
        if current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _table_cells(row):
    return [cell.strip().strip("`") for cell in row.strip().strip("|").split("|")]


def _check_evidence_table(plan_path, plan):
    issues = []
    section = _section_text(plan, "证据与验证记录")
    if not section:
        return issues
    tables = _markdown_tables(section)
    evidence_tables = []
    for table in tables:
        if len(table) < 2:
            continue
        headers = _table_cells(table[0])
        if any("结论" in header for header in headers) and any("证据" in header for header in headers):
            evidence_tables.append((headers, table[2:]))
    if not evidence_tables:
        return issues
    for headers, rows in evidence_tables:
        has_level = any("证据等级" == header or "证据等级" in header for header in headers)
        if not has_level:
            issues.append({
                "type": "evidence_table_level_column_missing",
                "severity": "blocker",
                "file": str(plan_path),
                "message": "证据与验证记录表缺少 `证据等级` 列",
            })
            if "证据等级" in plan:
                issues.append({
                    "type": "evidence_table_claim_mismatch",
                    "severity": "blocker",
                    "file": str(plan_path),
                    "message": "复查清单声称证据表包含证据等级，但实际表格缺少该列",
                })
            continue
        level_index = next(index for index, header in enumerate(headers) if "证据等级" in header)
        for row in rows:
            if re.match(r"^\|\s*-+", row):
                continue
            cells = _table_cells(row)
            value = cells[level_index].strip() if level_index < len(cells) else ""
            if not re.fullmatch(r"E[1-4]", value):
                issues.append({
                    "type": "evidence_table_level_value_invalid",
                    "severity": "blocker",
                    "file": str(plan_path),
                    "value": value,
                    "message": "证据等级必须为 E1/E2/E3/E4",
                })
    return issues


def _question_blocks(section):
    blocks = []
    current = []
    for line in section.splitlines():
        if re.match(r"^\s*\d+[\.\)、]", line):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return [block for block in blocks if block.strip()]


def _check_user_confirmation_items(plan_path, plan):
    issues = []
    section = (
        _section_text(plan, "等待用户审核的问题")
        or _section_text(plan, "待用户确认")
        or _section_text(plan, "需要人工确认")
        or _section_text(plan, "用户确认")
    )
    if not section:
        return issues
    blocks = _question_blocks(section)
    requirements = [
        ("当前保守结论", "user_confirmation_default_missing", "待确认项缺少当前保守结论"),
        ("已检查证据", "user_confirmation_evidence_missing", "待确认项缺少已检查证据"),
        ("为什么代码或仓库文档无法回答", "user_confirmation_rationale_missing", "待确认项缺少为何代码或仓库文档无法回答"),
        ("blocks_phase1", "user_confirmation_blocks_phase1_missing", "待确认项缺少 blocks_phase1 标记"),
        ("回写目标", "user_confirmation_writeback_missing", "待确认项缺少回写目标"),
    ]
    for index, block in enumerate(blocks, 1):
        for marker, issue_type, message in requirements:
            if marker not in block:
                issues.append({
                    "type": issue_type,
                    "severity": "blocker",
                    "file": str(plan_path),
                    "question_index": index,
                    "message": message,
                })
    return issues


def _check_maintainer_rule_conflicts(repo_root, plan, report, report_path):
    issues = []
    contributing = repo_root / "CONTRIBUTING.md"
    if not contributing.exists():
        return issues
    text = contributing.read_text(encoding="utf-8", errors="ignore").lower()
    no_tests = any(marker in text for marker in (
        "do not write any",
        "don't use tests",
        "dont use tests",
        "please do not write any",
        "不要写测试",
        "不写测试",
    )) and "test" in text
    if not no_tests:
        return issues
    analysis = f"{plan}\n{report}"
    recommends_tests = re.search(r"(优先|建议|需要|补|增加|新增).{0,12}(测试|回归测试)|回归测试", analysis)
    acknowledges_rule = any(marker in analysis for marker in ("维护者规则", "CONTRIBUTING", "不直接新增测试", "不写测试"))
    if recommends_tests and not acknowledges_rule:
        issues.append({
            "type": "test_recommendation_conflicts_with_contributing",
            "severity": "blocker",
            "file": str(report_path),
            "message": "分析文档建议补测试，但 CONTRIBUTING 明确限制 PR 新增测试，需改为先记录维护者规则或提出非阻断建议",
        })
    return issues


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

    if strict_phase1_review and plan and "证据与验证记录" in plan:
        table_issues = _check_evidence_table(plan_path, plan)
        if table_issues:
            issues.extend(table_issues)
        elif "证据等级" not in plan:
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

    if strict_phase1_review:
        issues.extend(_check_user_confirmation_items(plan_path, plan))
        issues.extend(_check_maintainer_rule_conflicts(repo_root, plan, report, report_path))

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
        "first_release_acceptance": [],
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
        checks["first_release_acceptance"] = check_first_release_acceptance(doc_dir, repo_root)

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
