"""
文档依赖追踪器 - 基于 dependencies 和 keywords 字段检测关联文档

功能说明:
    - 基于文档的 dependencies 字段检测直接关联文档
    - 基于文档的 keywords 字段检测语义关联文档
    - 支持双向关联检测（正向依赖和反向依赖）
    - 提供分级关联检测策略（dependencies > keywords > 全文搜索）
    - 输出 JSON 格式的关联文档信息

使用方法:
    # 检测单个文档的关联文档
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md"

    # 指定文档目录
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --doc-dir dev_docs/

    # 递归扫描
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --doc-dir dev_docs/ --recursive

    # 使用 dependencies 字段检测
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --strategy dependencies

    # 使用 keywords 字段检测
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --strategy keywords

    # 使用全文搜索兜底
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --strategy fulltext

    # 输出详细信息
    python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --verbose

参数说明:
    --doc PATH                要检测的目标文档路径
    --doc-dir PATH            文档目录，默认为 dev_docs/
    --recursive               递归扫描文档目录
    --strategy STRATEGY       检测策略: dependencies (默认), keywords, fulltext
    --min-overlap NUM         关键词最小重叠度，默认 1
    --verbose                 输出详细信息
    --timeout SECONDS         超时时间，默认 10 秒

输出格式:
    {
      "success": true,
      "data": {
        "target_doc": "dev_docs/api_layer.md",
        "strategy": "dependencies",
        "related_docs": {
          "direct": [
            {
              "file": "dev_docs/state_management.md",
              "type": "direct",
              "reason": "dependencies 字段中引用"
            }
          ],
          "reverse": [
            {
              "file": "dev_docs/user_profile.md",
              "type": "reverse",
              "reason": "被该文档的 dependencies 字段引用"
            }
          ],
          "semantic": [
            {
              "file": "dev_docs/data_layer.md",
              "type": "semantic",
              "reason": "关键词重叠度: 3 (API, HTTP, 接口)",
              "overlap_keywords": ["API", "HTTP", "接口"]
            }
          ]
        },
        "total_related": 3,
        "total_docs_scanned": 50
      },
      "metadata": {
        "elapsed_seconds": 0.35,
        "timeout_threshold": 10,
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

def normalize_path(path_str):
    """标准化路径用于比较"""
    return os.path.normpath(path_str).replace('\\', '/')

def extract_dependencies(doc_path):
    """从文档中提取 dependencies 字段"""
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        summary = extract_frontmatter(content)

        if not summary or 'dependencies' not in summary:
            return []

        dependencies = summary['dependencies']
        if isinstance(dependencies, list):
            return [d for d in dependencies if d and d != '无']
        elif isinstance(dependencies, str) and dependencies != '无':
            if '|' in dependencies:
                return [d.strip() for d in dependencies.split('|') if d.strip()]
            return [dependencies]

        return []

    except Exception as e:
        return []

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

def detect_related_by_dependencies(target_doc, all_docs):
    """基于 dependencies 字段检测关联文档"""
    direct_related = []
    reverse_related = []

    # 提取目标文档的 dependencies 字段
    target_deps = extract_dependencies(target_doc)

    # 检测直接关联文档（目标文档依赖的文档）
    for doc in all_docs:
        if doc == target_doc:
            continue

        doc_name = os.path.basename(doc)
        for dep in target_deps:
            if dep in doc or doc_name in dep:
                direct_related.append({
                    "file": doc,
                    "type": "direct",
                    "reason": "dependencies 字段中引用"
                })
                break

    # 检测反向关联文档（依赖目标文档的文档）
    for doc in all_docs:
        if doc == target_doc:
            continue

        doc_deps = extract_dependencies(doc)
        target_name = os.path.basename(target_doc)

        for dep in doc_deps:
            if target_doc in dep or target_name in dep:
                reverse_related.append({
                    "file": doc,
                    "type": "reverse",
                    "reason": "被该文档的 dependencies 字段引用"
                })
                break

    return direct_related, reverse_related

def detect_related_by_keywords(target_doc, all_docs, min_overlap=1):
    """基于 keywords 字段检测语义关联文档"""
    semantic_related = []

    # 提取目标文档的 keywords 字段
    target_keywords = set(extract_keywords(target_doc))

    for doc in all_docs:
        if doc == target_doc:
            continue

        # 提取其他文档的 keywords 字段
        doc_keywords = set(extract_keywords(doc))

        # 计算关键词重叠度
        overlap = target_keywords & doc_keywords

        if len(overlap) >= min_overlap:
            semantic_related.append({
                "file": doc,
                "type": "semantic",
                "reason": f"关键词重叠度: {len(overlap)} ({', '.join(overlap)})",
                "overlap_keywords": list(overlap)
            })

    # 按重叠度降序排序
    semantic_related.sort(key=lambda x: len(x["overlap_keywords"]), reverse=True)

    return semantic_related

def detect_related_by_fulltext(target_doc, all_docs):
    """使用全文搜索检测关联文档（兜底方案）"""
    fulltext_related = []

    try:
        with open(target_doc, 'r', encoding='utf-8') as f:
            target_content = f.read().lower()

        # 提取目标文档的关键词
        target_words = re.findall(r'\b\w{3,}\b', target_content)
        target_word_set = set(target_words)

        for doc in all_docs:
            if doc == target_doc:
                continue

            try:
                with open(doc, 'r', encoding='utf-8') as f:
                    doc_content = f.read().lower()

                doc_words = re.findall(r'\b\w{3,}\b', doc_content)
                doc_word_set = set(doc_words)

                # 计算词汇重叠度
                overlap = target_word_set & doc_word_set

                if len(overlap) > 3:  # 至少 4 个相同的长单词
                    fulltext_related.append({
                        "file": doc,
                        "type": "fulltext",
                        "reason": f"词汇重叠度: {len(overlap)}"
                    })

            except Exception as e:
                continue

    except Exception as e:
        pass

    return fulltext_related

def trace_dependencies(target_doc, doc_dir, recursive=False, strategy="dependencies", min_overlap=1):
    """追踪文档的关联文档"""
    # 查找所有文档
    all_docs = find_markdown_files(doc_dir, recursive)

    if target_doc not in all_docs:
        all_docs.append(target_doc)

    related_docs = {
        "direct": [],
        "reverse": [],
        "semantic": [],
        "fulltext": []
    }

    if strategy in ["dependencies", "all"]:
        direct, reverse = detect_related_by_dependencies(target_doc, all_docs)
        related_docs["direct"] = direct
        related_docs["reverse"] = reverse

    if strategy in ["keywords", "all"]:
        semantic = detect_related_by_keywords(target_doc, all_docs, min_overlap)
        related_docs["semantic"] = semantic

    if strategy in ["fulltext", "all"]:
        fulltext = detect_related_by_fulltext(target_doc, all_docs)
        related_docs["fulltext"] = fulltext

    # 去重
    seen = set()
    for key in related_docs:
        unique = []
        for doc in related_docs[key]:
            if doc["file"] not in seen:
                seen.add(doc["file"])
                unique.append(doc)
        related_docs[key] = unique

    total_related = sum(len(docs) for docs in related_docs.values())

    return {
        "target_doc": target_doc,
        "strategy": strategy,
        "related_docs": related_docs,
        "total_related": total_related,
        "total_docs_scanned": len(all_docs)
    }

def main():
    start_time = time.time()

    parser = argparse.ArgumentParser(
        description="文档依赖追踪器 - 基于 dependencies 和 keywords 字段检测关联文档",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--doc", required=True, help="要检测的目标文档路径")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录，默认{DEFAULT_DOC_DIR}")
    parser.add_argument("--recursive", action="store_true", help="递归扫描文档目录")
    parser.add_argument("--strategy", default="dependencies", choices=["dependencies", "keywords", "fulltext", "all"], help="检测策略: dependencies (默认), keywords, fulltext, all")
    parser.add_argument("--min-overlap", type=int, default=1, help="关键词最小重叠度，默认 1")
    parser.add_argument("--verbose", action="store_true", help="输出详细信息")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间（秒），默认{DEFAULT_TIMEOUT}秒")

    args = parser.parse_args()

    result = {
        "success": True,
        "data": {},
        "metadata": {
            "elapsed_seconds": 0,
            "timeout_threshold": args.timeout,
            "version": VERSION
        }
    }

    try:
        # 验证目标文档是否存在
        if not os.path.isfile(args.doc):
            result["success"] = False
            result["error"] = f"Target document not found: {args.doc}"
        elif not args.doc.endswith('.md'):
            result["success"] = False
            result["error"] = "Target document must be a Markdown file (.md)"
        elif not os.path.isdir(args.doc_dir):
            result["success"] = False
            result["error"] = f"Document directory not found: {args.doc_dir}"
        else:
            # 执行依赖追踪
            tracing_result = trace_dependencies(
                args.doc,
                args.doc_dir,
                args.recursive,
                args.strategy,
                args.min_overlap
            )
            result["data"] = tracing_result

            if args.verbose:
                print(f"Scanned {tracing_result['total_docs_scanned']} documents, found {tracing_result['total_related']} related docs")

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    # 计算耗时
    elapsed_time = round(time.time() - start_time, 2)
    result["metadata"]["elapsed_seconds"] = elapsed_time

    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
