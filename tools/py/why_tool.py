#!/usr/bin/env python3
"""
Why-Tool: 架构探针检索工具 (Architecture Context Retriever)

功能说明:
    通过代码中的隐性注解或语义搜索，检索对应的技术决策理由(ADR)。
    - L1 注解优先检索: 扫描代码中的 @architecture 或 @reason 注解
    - 语义搜索兜底: 对 ADR 标题、摘要与正文进行关键词匹配

使用方法:
    # 通过查询搜索相关 ADR
    python tools/py/why_tool.py --query "why use pinia"

    # 扫描源代码文件中的注解
    python tools/py/why_tool.py --file src/store/index.ts

    # 组合使用: 先扫描注解，再语义搜索
    python tools/py/why_tool.py --file src/app.ts --query "state management"

参数说明:
    --query TEXT       搜索关键词或问题 (例如: "why use pinia")
    --file PATH        源代码文件路径，扫描 @architecture/@reason 注解
    --adr-dir PATH     ADR 文档目录 (默认: dev_docs/architecture/decisions)

输出格式:
    文本输出，包含以下信息:
    - 扫描到的 L1 注解列表 (文件路径、行号、ADR编号、描述)
    - 精确匹配的 ADR 详情
    - 语义搜索的 Top 3 推荐结果

使用示例:
    # 示例 1: 搜索为何选择 Pinia
    python tools/py/why_tool.py --query "pinia state management"

    # 示例 2: 扫描文件中的架构注解
    python tools/py/why_tool.py --file src/components/UserList.vue

    # 示例 3: 指定自定义 ADR 目录
    python tools/py/why_tool.py --adr-dir docs/decisions --query "database"

版本信息:
    版本: 1.0.0
    更新日期: 2026-04-12
"""

import os
import sys
import re
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Why-Tool: Architecture Context Retriever")
    parser.add_argument("--query", type=str, help="Question or keywords regarding architecture (e.g. 'why use pinia')")
    parser.add_argument("--file", type=str, help="Source code file path to scan for L1 annotations like '@architecture ADR-XXX:'")
    parser.add_argument("--adr-dir", type=str, default="dev_docs/architecture/decisions", help="Directory where ADRs are stored")
    return parser.parse_args()

def extract_frontmatter_and_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try parsing frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        body = fm_match.group(2)

        metadata = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                metadata[k.strip()] = v.strip().strip('"').strip("'")
        return metadata, body
    return {}, content

def scan_file_for_annotations(filepath):
    """Scan source code for @architecture or @reason annotations"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        annotations = []
        for i, line in enumerate(lines):
            match = re.search(r'@architecture\s+(ADR-\d+):?\s*(.*)', line, re.IGNORECASE)
            if match:
                annotations.append({
                    "line": i + 1,
                    "adr": match.group(1).upper(),
                    "desc": match.group(2).strip()
                })

            reason_match = re.search(r'@reason\s+(.*)', line, re.IGNORECASE)
            if reason_match:
                annotations.append({
                    "line": i + 1,
                    "adr": "IMPLICIT",
                    "desc": reason_match.group(1).strip()
                })
        return annotations
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return []

def search_adrs(query, adr_dir):
    """Fallback search by matching keywords in ADR summaries and contents"""
    base_dir = Path(adr_dir)
    if not base_dir.exists():
        return []

    results = []
    query_terms = [q.lower() for q in re.split(r'\s+', query) if q]

    for p in base_dir.glob("*.md"):
        if 'archived' in p.parts:
            continue

        meta, body = extract_frontmatter_and_content(p)
        score = 0
        title = meta.get('title', p.name)
        summary = meta.get('summary', '')

        search_target = f"{title} {summary} {body}".lower()

        for term in query_terms:
            if term in search_target:
                score += 1
                if term in summary.lower() or term in title.lower():
                    score += 2 # extra weight for title/summary hit

        if score > 0:
            results.append({
                "file": str(p),
                "title": title,
                "summary": summary,
                "score": score
            })

    # Sort by descending score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def main():
    args = parse_args()

    if not args.query and not args.file:
        print("Please provide either --query or --file argument.")
        sys.exit(1)

    print("=== Why-Tool: Architecture Context Retriever ===")

    # 1. First Pass: Check L1 Annotations if file is provided
    found_adrs = set()
    if args.file and os.path.exists(args.file):
        print(f"Scanning {args.file} for L1 annotations...")
        annots = scan_file_for_annotations(args.file)
        if annots:
            for ann in annots:
                print(f"[Line {ann['line']}] Found Annotation: {ann['adr']} - {ann['desc']}")
                if ann['adr'].startswith("ADR-"):
                    found_adrs.add(ann['adr'])
        else:
            print("No @architecture annotations found in file.")

    # 2. Extract context by specific ADR identity if found
    for adr_id in found_adrs:
        # Just find the file containing the adr_id
        for p in Path(args.adr_dir).glob("*.md"):
            if adr_id.lower() in p.name.lower():
                meta, body = extract_frontmatter_and_content(p)
                print(f"\n=> 🎯 Exact Match: {p.name}")
                print(f"   Title: {meta.get('title', 'N/A')}")
                print(f"   Summary: {meta.get('summary', 'N/A')}")

    # 3. If query provided, fallback to heuristic text search
    if args.query:
        print(f"\nRunning semantic keyword search for: '{args.query}'...")
        results = search_adrs(args.query, args.adr_dir)
        if not results:
            print("No matching active ADRs found.")
        else:
            print("\n=> 🔎 Top Matching Active ADRs:")
            for res in results[:3]:
                print(f" - [{res['score']} pts] {res['file']}")
                print(f"   Title: {res['title']}")
                print(f"   Summary: {res['summary']}")

if __name__ == "__main__":
    main()
