#!/usr/bin/env python3
"""
文档依赖追踪器 - 基于 dependencies 字段追踪文档间的依赖关系

功能说明:
    - 读取目标文档的 dependencies 字段
    - 查找依赖当前文档的其他文档（反向依赖）
    - 支持三级检测策略: dependencies > keywords > 全文搜索
    - 生成依赖关系图谱和修复建议
    - 支持批量文档分析和影响范围评估

使用方法:
    # 分析单个文档的依赖关系
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md"

    # 分析多个文档
    python tools/py/doc_dependency_tracer.py --docs "doc1.md,doc2.md"

    # 指定文档目录和输出格式
    python tools/py/doc_dependency_tracer.py --doc-dir docs/ --format json

参数说明:
    --doc PATH          要分析的文档路径
    --docs LIST         逗号分隔的多个文档路径
    --doc-dir PATH      文档目录 (默认: dev_docs)
    --strategy STRATEGY 检测策略: dependencies, keywords, fulltext (默认: dependencies)
    --format FORMAT     输出格式: text, json (默认: text)
    --min-overlap N     最小关键词重叠数 (默认: 1)

输出格式:
    text 格式：
    - 文档依赖关系图谱
    - 正向依赖列表 (本文档依赖的其他文档)
    - 反向依赖列表 (依赖本文档的其他文档)
    - 影响范围评估

    json 格式：
    {
      "doc_path": "path/to/doc.md",
      "dependencies": {
        "forward": [...],
        "reverse": [...]
      },
      "strategy": "dependencies",
      "impact_score": 0.85,
      "suggestions": [...]
    }

版本信息:
    Version: 1.0.0
    Created: 2026-04-20
    Purpose: Support 011-Doc Error Fix Workflow
"""

import os
import re
import json
import sys
import time
import argparse
from pathlib import Path
from collections import defaultdict

VERSION = "1.0.0"
DEFAULT_TIMEOUT = 10
DEFAULT_DOC_DIR = "dev_docs"

def extract_frontmatter(content):
    """提取YAML Frontmatter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None
    yaml_content = match.group(1)
    return parse_yaml_simple(yaml_content)

def parse_yaml_simple(yaml_str):
    """简单的YAML解析器"""
    result = {}
    lines = yaml_str.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        if not value or value.lower() in ['无', 'none', '']:
            result[key] = None
        elif '|' in value:
            result[key] = [item.strip() for item in value.split('|') if item.strip()]
        else:
            value = value.strip('"\'')
            result[key] = value
    return result

def extract_dependencies(file_path):
    """从文档提取dependencies字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        summary = extract_frontmatter(content)
        if not summary or 'dependencies' not in summary:
            return None
        dependencies = summary['dependencies']
        if isinstance(dependencies, list):
            return [d for d in dependencies if d and d != '无']
        elif isinstance(dependencies, str) and dependencies != '无':
            if '|' in dependencies:
                return [d.strip() for d in dependencies.split('|') if d.strip()]
            return [dependencies]
        return None
    except Exception as e:
        return None


def extract_keywords(file_path):
    """从文档提取keywords字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        summary = extract_frontmatter(content)
        if not summary or 'keywords' not in summary:
            return None
        keywords = summary['keywords']
        if isinstance(keywords, list):
            return [k for k in keywords if k and k != '无']
        elif isinstance(keywords, str) and keywords != '无':
            if '|' in keywords:
                return [k.strip() for k in keywords.split('|') if k.strip()]
            return [keywords]
        return None
    except Exception as e:
        return None

def find_markdown_files(directory, recursive=False):
    """查找目录下的所有Markdown文件"""
    md_files = []
    if recursive:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith('.md'):
                md_files.append(file_path)
    return md_files

def normalize_path(path):
    """标准化路径用于比较"""
    return os.path.normpath(path).replace('\\', '/')

def get_relative_path(full_path, base_dir):
    """获取相对路径"""
    try:
        return os.path.relpath(full_path, base_dir)
    except:
        return full_path

def analyze_dependencies(target_docs, doc_dir, recursive=False, strategy="dependencies", min_overlap=1):
    """分析文档的依赖关系"""
    # 标准化目标文档路径
    target_docs_normalized = []
    for doc in target_docs:
        if not os.path.isabs(doc):
            doc = os.path.join(doc_dir, doc)
        target_docs_normalized.append(normalize_path(doc))

    # 查找所有文档
    all_docs = find_markdown_files(doc_dir, recursive)
    results = []

    for target_doc in target_docs_normalized:
        if not os.path.exists(target_doc):
            results.append({
                "target_doc": target_doc,
                "error": "文件不存在",
                "forward_deps": [],
                "backward_deps": [],
                "semantic_related": []
            })
            continue

        result = {
            "target_doc": target_doc,
            "forward_deps": [],
            "backward_deps": [],
            "semantic_related": []
        }

        # 正向依赖 - 当前文档依赖的其他文档
        if strategy in ["dependencies", "all"]:
            deps = extract_dependencies(target_doc)
            if deps:
                result["forward_deps"] = deps

        # 反向依赖 - 依赖当前文档的其他文档
        if strategy in ["dependencies", "all"]:
            backward_deps = []
            for other_doc in all_docs:
                if normalize_path(other_doc) == normalize_path(target_doc):
                    continue
                other_deps = extract_dependencies(other_doc)
                if other_deps:
                    for dep in other_deps:
                        if dep in target_doc or target_doc in dep:
                            rel_path = get_relative_path(other_doc, doc_dir)
                            backward_deps.append(rel_path)
                            break
            result["backward_deps"] = backward_deps

        # 语义关联 - 基于关键词
        if strategy in ["keywords", "all"]:
            target_keywords = extract_keywords(target_doc)
            if target_keywords:
                semantic_related = []
                for other_doc in all_docs:
                    if normalize_path(other_doc) == normalize_path(target_doc):
                        continue
                    other_keywords = extract_keywords(other_doc)
                    if not other_keywords:
                        continue
                    target_set = set(k.lower() for k in target_keywords)
                    other_set = set(k.lower() for k in other_keywords)
                    overlap = target_set & other_set
                    if len(overlap) >= min_overlap:
                        rel_path = get_relative_path(other_doc, doc_dir)
                        semantic_related.append({
                            "doc": rel_path,
                            "overlap": len(overlap),
                            "common_keywords": list(overlap)
                        })
                semantic_related.sort(key=lambda x: x["overlap"], reverse=True)
                result["semantic_related"] = semantic_related

        results.append(result)

    # 计算影响评分
    total_deps = 0
    for r in results:
        total_deps += len(r.get("forward_deps", []))
        total_deps += len(r.get("backward_deps", []))
    impact_score = min(1.0, total_deps / 10) if total_deps > 0 else 0.0

    return {
        "results": results,
        "total_docs_scanned": len(all_docs),
        "impact_score": impact_score,
        "strategy": strategy
    }

def generate_fix_suggestions(analysis_result, changed_files=None):
    """生成修复建议"""
    suggestions = []
    for result in analysis_result.get("results", []):
        target_doc = result.get("target_doc", "")
        if "error" in result:
            suggestions.append({
                "doc": target_doc,
                "type": "error",
                "severity": "high",
                "message": f"文档分析失败: {result['error']}",
                "action": "检查文件是否存在"
            })
            continue

        forward_deps = result.get("forward_deps", [])
        if forward_deps:
            for dep in forward_deps:
                suggestions.append({
                    "doc": target_doc,
                    "type": "dependency_update",
                    "severity": "medium",
                    "message": f"此文档依赖 {dep}，请检查是否需要更新",
                    "action": "检查引用的依赖文档是否仍然有效",
                    "related_doc": dep
                })

        backward_deps = result.get("backward_deps", [])
        if backward_deps:
            suggestions.append({
                "doc": target_doc,
                "type": "impact_notification",
                "severity": "medium",
                "message": f"此文档被 {len(backward_deps)} 个其他文档依赖",
                "action": "修改此文档时，请同时检查依赖它的文档是否需要更新",
                "dependent_docs": backward_deps
            })

        semantic_related = result.get("semantic_related", [])
        if semantic_related:
            high_overlap = [s for s in semantic_related if s.get("overlap", 0) >= 3]
            if high_overlap:
                suggestions.append({
                    "doc": target_doc,
                    "type": "semantic_consistency",
                    "severity": "low",
                    "message": f"发现 {len(high_overlap)} 个高度相关的文档",
                    "action": "建议检查这些文档之间的一致性",
                    "related_docs": high_overlap[:5]
                })
    return suggestions

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="文档依赖追踪器 - 基于 dependencies 字段追踪文档间的依赖关系",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--doc", required=True, help="逗号分隔的目标文档路径列表")
    parser.add_argument("--strategy", default="dependencies", choices=["dependencies", "keywords", "all"], help="检测策略")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录, 默认 {DEFAULT_DOC_DIR}")
    parser.add_argument("--recursive", action="store_true", help="递归扫描文档目录")
    parser.add_argument("--suggest-fixes", action="store_true", help="生成修复建议")
    parser.add_argument("--min-overlap", type=int, default=1, help="关键词最小重叠度，默认 1")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间(秒), 默认 {DEFAULT_TIMEOUT} 秒")
    parser.add_argument("--output-format", default="json", choices=["json", "markdown"], help="输出格式")

    args = parser.parse_args()
    target_docs = [d.strip() for d in args.doc.split(',') if d.strip()]

    result = {
        "success": True,
        "data": {},
        "metadata": {
            "elapsed_seconds": 0,
            "version": VERSION,
            "target_docs": target_docs,
            "strategy": args.strategy
        }
    }

    try:
        analysis_result = analyze_dependencies(
            target_docs, args.doc_dir, args.recursive, args.strategy, args.min_overlap
        )
        result["data"]["analysis"] = analysis_result
        if args.suggest_fixes:
            suggestions = generate_fix_suggestions(analysis_result)
            result["data"]["suggestions"] = suggestions
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()

    elapsed_time = round(time.time() - start_time, 2)
    result["metadata"]["elapsed_seconds"] = elapsed_time

    if args.output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"# 文档依赖分析报告\n")
        print(f"**分析时间**: {elapsed_time}s\n")
        print(f"**目标文档**: {', '.join(target_docs)}\n")
        print(f"**策略**: {args.strategy}\n")
        if result["success"]:
            for res in result["data"]["analysis"].get("results", []):
                doc_name = res.get("target_doc", "")
                print(f"## {doc_name}\n")
                print(f"**正向依赖**: {', '.join(res.get('forward_deps', [])) or '无'}\n")
                print(f"**反向依赖**: {', '.join(res.get('backward_deps', [])) or '无'}\n")

    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()

