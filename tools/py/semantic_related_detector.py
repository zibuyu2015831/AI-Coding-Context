"""
语义关联检测器 - 基于 keywords 字段检测语义关联文档

功能说明:
    - 基于文档的 keywords 字段进行语义关联检测
    - 支持关键词重叠度计算
    - 提供分级语义关联检测
    - 输出详细的语义关联信息
    - 与现有的文档处理工具集成

使用方法:
    # 检测单个文档的语义关联
    python tools/py/semantic_related_detector.py --doc "dev_docs/api_layer.md"

    # 检测语义关联（指定文档目录）
    python tools/py/semantic_related_detector.py --doc "dev_docs/api_layer.md" --doc-dir dev_docs/

    # 递归扫描文档目录
    python tools/py/semantic_related_detector.py --doc "dev_docs/api_layer.md" --doc-dir dev_docs/ --recursive

    # 调整最小重叠度（默认 1）
    python tools/py/semantic_related_detector.py --doc "dev_docs/api_layer.md" --min-overlap 2

    # 输出详细信息
    python tools/py/semantic_related_detector.py --doc "dev_docs/api_layer.md" --verbose

    # 批量检测多个文档
    python tools/py/semantic_related_detector.py --batch --doc-list "dev_docs/api_layer.md,dev_docs/state_management.md"

参数说明:
    --doc PATH               目标文档路径
    --doc-dir PATH           文档目录，默认 dev_docs/
    --recursive              递归扫描文档目录
    --min-overlap NUM        关键词最小重叠度，默认 1
    --batch                  批量检测模式
    --doc-list DOCS          逗号分隔的文档列表（批量模式）
    --verbose                输出详细信息
    --timeout SECONDS        超时时间，默认 10 秒

输出格式:
    {
      "success": true,
      "data": {
        "target_doc": "dev_docs/api_layer.md",
        "semantic_related": [
          {
            "file": "dev_docs/data_layer.md",
            "overlap_keywords": ["API", "HTTP", "接口"],
            "overlap_count": 3,
            "target_keywords": ["API", "HTTP", "接口", "RESTful"],
            "doc_keywords": ["API", "HTTP", "接口", "数据库"],
            "similarity_score": 0.75
          }
        ],
        "total_docs_scanned": 50,
        "total_related": 3
      },
      "metadata": {
        "version": "1.0.0"
      }
    }

版本信息:
    Version: 1.0.0
    Created: 2026-04-13
    Purpose: Support 011-Document Error Fix Workflow
"""

import os
import re
import json
import time
import argparse
from pathlib import Path

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


def extract_keywords(doc_path):
    """从文档中提取 keywords 字段"""
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        summary = extract_frontmatter(content)

        if not summary or 'keywords' not in summary:
            return []

        keywords = summary['keywords']
        if isinstance(keywords, list):
            return [k for k in keywords if k and k != '无']
        elif isinstance(keywords, str) and keywords != '无':
            if '|' in keywords:
                return [k.strip() for k in keywords.split('|') if k.strip()]
            return [keywords]

        return []

    except Exception as e:
        return []


def calculate_similarity(target_keywords, doc_keywords):
    """计算语义相似度分数"""
    target_set = set(target_keywords)
    doc_set = set(doc_keywords)
    overlap = target_set & doc_set

    # 使用 Jaccard 相似度
    if len(target_set) == 0 or len(doc_set) == 0:
        return 0.0

    jaccard_similarity = len(overlap) / len(target_set | doc_set)
    return jaccard_similarity


def detect_semantic_related(target_doc, doc_dir, recursive=False, min_overlap=1):
    """
    检测语义关联文档

    Args:
        target_doc: 目标文档
        doc_dir: 文档目录
        recursive: 是否递归扫描
        min_overlap: 关键词最小重叠度

    Returns:
        dict: 语义关联检测结果
    """
    target_keywords = extract_keywords(target_doc)

    if not target_keywords:
        return {
            "success": True,
            "target_doc": target_doc,
            "semantic_related": [],
            "total_docs_scanned": 0,
            "total_related": 0,
            "warning": "目标文档没有关键词字段"
        }

    md_files = find_markdown_files(doc_dir, recursive)

    semantic_related = []
    total_docs_scanned = 0

    for doc in md_files:
        if doc == target_doc:
            continue

        total_docs_scanned += 1

        doc_keywords = extract_keywords(doc)
        if not doc_keywords:
            continue

        # 计算关键词重叠
        target_set = set(target_keywords)
        doc_set = set(doc_keywords)
        overlap = target_set & doc_set

        if len(overlap) >= min_overlap:
            similarity = calculate_similarity(target_keywords, doc_keywords)

            semantic_related.append({
                "file": doc,
                "overlap_keywords": list(overlap),
                "overlap_count": len(overlap),
                "target_keywords": target_keywords,
                "doc_keywords": doc_keywords,
                "similarity_score": round(similarity, 2)
            })

    # 按相似度降序排序
    semantic_related.sort(key=lambda x: x["similarity_score"], reverse=True)

    return {
        "success": True,
        "target_doc": target_doc,
        "semantic_related": semantic_related,
        "total_docs_scanned": total_docs_scanned,
        "total_related": len(semantic_related)
    }


def batch_detect(doc_list, doc_dir, recursive=False, min_overlap=1):
    """
    批量检测语义关联

    Args:
        doc_list: 文档列表
        doc_dir: 文档目录
        recursive: 是否递归扫描
        min_overlap: 关键词最小重叠度

    Returns:
        dict: 批量检测结果
    """
    results = []

    for doc in doc_list:
        doc_path = os.path.join(doc_dir, doc) if not doc.startswith(doc_dir) else doc

        if not os.path.exists(doc_path):
            results.append({
                "doc": doc,
                "success": False,
                "error": "文件不存在"
            })
            continue

        result = detect_semantic_related(doc_path, doc_dir, recursive, min_overlap)
        results.append({
            "doc": doc,
            **result
        })

    return {
        "success": True,
        "results": results,
        "total_docs": len(doc_list),
        "successful_detections": sum(1 for r in results if r.get("success", False)),
        "failed_detections": sum(1 for r in results if not r.get("success", False))
    }


def main():
    parser = argparse.ArgumentParser(
        description="语义关联检测器 - 基于 keywords 字段检测语义关联文档",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--doc", help="目标文档路径")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录，默认: {DEFAULT_DOC_DIR}")
    parser.add_argument("--recursive", action="store_true", help="递归扫描文档目录")
    parser.add_argument("--min-overlap", type=int, default=1, help="关键词最小重叠度，默认: 1")
    parser.add_argument("--batch", action="store_true", help="批量检测模式")
    parser.add_argument("--doc-list", help="逗号分隔的文档列表（批量模式）")
    parser.add_argument("--verbose", action="store_true", help="输出详细信息")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间（秒），默认: {DEFAULT_TIMEOUT}")

    args = parser.parse_args()

    # 参数验证
    if args.batch and not args.doc_list:
        parser.error("批量检测模式需要 --doc-list 参数")

    if not args.batch and not args.doc:
        parser.error("单个文档检测需要 --doc 参数")

    result = {
        "success": True,
        "data": {},
        "metadata": {
            "version": VERSION
        }
    }

    try:
        if args.batch:
            # 批量检测
            doc_list = args.doc_list.split(',')
            doc_list = [d.strip() for d in doc_list if d.strip()]

            if not doc_list:
                result["success"] = False
                result["error"] = "文档列表不能为空"
            else:
                batch_result = batch_detect(doc_list, args.doc_dir, args.recursive, args.min_overlap)
                result["data"] = {
                    "action": "batch_detection",
                    "result": batch_result
                }
        else:
            # 单个文档检测
            if not os.path.exists(args.doc):
                result["success"] = False
                result["error"] = f"文档不存在: {args.doc}"
            elif not os.path.isfile(args.doc):
                result["success"] = False
                result["error"] = f"不是有效的文件: {args.doc}"
            else:
                detection_result = detect_semantic_related(
                    args.doc,
                    args.doc_dir,
                    args.recursive,
                    args.min_overlap
                )
                result["data"] = {
                    "action": "single_detection",
                    "result": detection_result
                }
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
