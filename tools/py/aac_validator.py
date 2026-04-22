#!/usr/bin/env python3
"""
AaC Validator: 架构即代码静态验证工具 (Architecture as Code)

功能说明:
    从 Markdown ADR 文档中提取 YAML 约束，对代码进行静态扫描验证。
    - 解析 ADR 中的 machine-readable constraints 代码块
    - 支持 regex_check 正则匹配检查
    - 支持 dependency_check 依赖检查
    - 输出架构违规报告

使用方法:
    # 扫描整个目录
    python tools/py/aac_validator.py --scan-dir ./src

    # 扫描特定文件
    python tools/py/aac_validator.py --scan-file src/utils/helpers.ts

    # 指定自定义 ADR 目录
    python tools/py/aac_validator.py --adr-dir docs/architecture/decisions --scan-dir ./src

参数说明:
    --scan-file PATH    扫描特定文件路径
    --scan-dir PATH     扫描目录 (默认: 当前目录)
    --adr-dir PATH      ADR 文档目录 (默认: dev_docs/architecture/decisions)

输出格式:
    文本输出，包含以下信息:
    - 加载的约束数量
    - 扫描的文件数量
    - 违规详情列表 (ADR来源、违规类型、违规信息、文件路径)
    - 或合规确认信息

    退出码:
    - 0: 无违规或未发现约束
    - 1: 发现架构违规

使用示例:
    # 示例 1: 扫描前端代码目录
    python tools/py/aac_validator.py --scan-dir ./frontend/src

    # 示例 2: 验证单个配置文件
    python tools/py/aac_validator.py --scan-file package.json --adr-dir docs/decisions

    # 示例 3: 集成到 CI/CD 流程
    python tools/py/aac_validator.py --scan-dir . || echo "Architecture violations found!"

约束格式 (ADR 中的 YAML 代码块):
    ```yaml
    constraints:
      - type: regex_check
        pattern: ".*\.docx$"
        forbidden_in: ["src/**", "lib/**"]
        message: "禁止在源码目录存放 .docx 文件"
      - type: dependency_check
        required: ["react"]
        forbidden: ["jquery"]
    ```

版本信息:
    版本: 1.0.0
    更新日期: 2026-04-12
"""

import os
import sys
import re
import argparse
import json
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="AaC (Architecture as Code) Validator")
    parser.add_argument("--scan-file", type=str, help="Specific file to scan against ADR constraints")
    parser.add_argument("--scan-dir", type=str, default=".", help="Directory to scan against ADR constraints (defaults to current dir)")
    parser.add_argument("--adr-dir", type=str, default="dev_docs/architecture/decisions", help="Directory containing active ADRs")
    return parser.parse_args()

def naive_parse_yaml_constraints(yaml_text):
    """
    Very naive YAML parser for zero-dependency compliance.
    Specifically parses the 'constraints' block from ADRs.
    """
    lines = yaml_text.split('\n')
    constraints = []
    curr_dict = {}

    for line in lines:
        line = line.rstrip()
        if not line.strip() or line.strip().startswith('#'):
            continue

        # Match list item: "- type: regex_check"
        list_match = re.match(r'^\s*-\s*type:\s*[\'"]?(.*?)[\'"]?$', line)
        if list_match:
            if curr_dict:
                constraints.append(curr_dict)
            curr_dict = {"type": list_match.group(1)}
            continue

        # Match properties: "pattern: '.*\.docx'" or "forbidden_in: [pathA, pathB]"
        prop_match = re.match(r'^\s*([a-zA-Z_]+):\s*(.*)$', line)
        if prop_match and curr_dict is not None:
            key = prop_match.group(1)
            val = prop_match.group(2).strip()

            # Simple array detection [a, b]
            if val.startswith('[') and val.endswith(']'):
                arr_val = val[1:-1].split(',')
                curr_dict[key] = [v.strip().strip("'").strip('"') for v in arr_val if v.strip()]
            else:
                # Handle quoted strings and escaped backslashes
                parsed_val = val.strip("'").strip('"').replace('\\\\', '\\')
                curr_dict[key] = parsed_val

    if curr_dict:
        constraints.append(curr_dict)
    return constraints

def extract_constraints_from_adr(filepath):
    """Extract YAML constraints from ADR's markdown code block"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for constraints: block inside yaml code block
        match = re.search(r'constraints:\s*\n(.*?)(?=\n\w+:|\n```|$)', content, re.DOTALL | re.IGNORECASE)
        if not match:
            # Fallback for simpler match
            match = re.search(r'```yaml\s*?\nconstraints:\n(.*?)\n```', content, re.DOTALL | re.IGNORECASE)

        if not match:
            return []

        return naive_parse_yaml_constraints(match.group(1))
    except Exception as e:
        print(f"Error parsing constraints in {filepath}: {e}", file=sys.stderr)
        return []

def load_all_active_constraints(adr_dir):
    base_dir = Path(adr_dir)
    all_constraints = []

    if not base_dir.exists():
        return []

    for p in base_dir.glob("*.md"):
        if 'archived' in p.parts:
            continue

        c_list = extract_constraints_from_adr(p)
        for c in c_list:
            c['source_adr'] = p.name
            all_constraints.append(c)

    return all_constraints

def match_path_glob(path_str, glob_pattern):
    """Simple glob matching, e.g., 'src/**' or 'frontend/**'"""
    # Replace ** with .* and * with [^/]*
    pattern = glob_pattern.replace('.', '\\.').replace('**', '.*').replace('*', '[^/]*')
    return bool(re.search(f"^{pattern}", path_str.replace('\\', '/')))

def validate_file(filepath, constraints):
    violations = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        # Ignore binary or unreadable files
        return violations

    path_normalized = str(Path(filepath).as_posix())

    for c in constraints:
        c_type = c.get('type')

        if c_type == 'regex_check':
            forbidden_in = c.get('forbidden_in', [])
            pattern = c.get('pattern', '')

            # Check if this file is in the forbidden scope
            in_scope = False
            for glob_pat in forbidden_in:
                if match_path_glob(path_normalized, glob_pat):
                    in_scope = True
                    break

            if in_scope and pattern:
                # Check filename first
                if re.search(pattern, path_normalized, re.IGNORECASE):
                    violations.append({
                        "adr": c["source_adr"],
                        "type": c_type,
                        "message": c.get('message', f"FileName matched forbidden pattern: {pattern}")
                    })
                # Check contents
                elif re.search(pattern, content, re.IGNORECASE):
                     violations.append({
                        "adr": c["source_adr"],
                        "type": c_type,
                        "message": c.get('message', f"Content matched forbidden pattern: {pattern}")
                    })

        elif c_type == 'dependency_check' and 'package.json' in path_normalized:
            required = c.get('required', [])
            forbidden = c.get('forbidden', [])

            # Very naive string checks for package.json MVP
            for req in required:
                if f'"{req}"' not in content:
                    violations.append({
                        "adr": c["source_adr"],
                        "type": c_type,
                        "message": f"Required dependency missing: {req}"
                    })
            for fp in forbidden:
                if f'"{fp}"' in content:
                    violations.append({
                        "adr": c["source_adr"],
                        "type": c_type,
                        "message": f"Forbidden dependency found: {fp}"
                    })

    return violations

def main():
    args = parse_args()

    print("=== AaC (Architecture as Code) Validator ===")
    constraints = load_all_active_constraints(args.adr_dir)

    if not constraints:
        print("No machine-readable constraints found in Active ADRs.")
        sys.exit(0)

    print(f"Loaded {len(constraints)} constraint(s) from ADRs. Scanning...")

    all_violations = []

    if args.scan_file:
        files_to_scan = [Path(args.scan_file)]
    else:
        files_to_scan = Path(args.scan_dir).rglob("*.*")

    scanned_count = 0
    for p in files_to_scan:
        if p.is_file() and not '.git' in p.parts and not 'node_modules' in p.parts:
            scanned_count += 1
            v = validate_file(str(p), constraints)
            if v:
                for viol in v:
                    viol['file'] = str(p)
                    all_violations.append(viol)

    if all_violations:
        print(f"\n❌ Found {len(all_violations)} architecture violation(s) across {scanned_count} files:")
        for v in all_violations:
            print(f"  - [{v['adr']}] in {v['file']}: {v['message']}")
        sys.exit(1)
    else:
        print(f"\n✅ All {scanned_count} scanned file(s) comply with Active ADRs.")
        sys.exit(0)

if __name__ == "__main__":
    main()
