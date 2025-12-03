"""
文档摘要提取工具 - 从Markdown文档中提取YAML Frontmatter摘要

功能说明:
    - 从Markdown文档中提取YAML Frontmatter格式的摘要
    - 支持单文件和批量目录处理
    - YAML解析优先，正则表达式作为备用方案
    - JSON格式统一输出
    - 超时机制保护（默认10秒）

使用方法:
    # 单文件提取
    python tools/py/summary_extractor.py --file dev_docs/api_layer.md
    
    # 批量提取目录下所有.md文件
    python tools/py/summary_extractor.py --dir dev_docs/
    
    # 递归扫描子目录
    python tools/py/summary_extractor.py --dir dev_docs/ --recursive

参数说明:
    --file PATH          单个Markdown文件路径
    --dir PATH           批量处理目录路径
    --recursive          递归扫描子目录（仅与--dir配合使用）
    --timeout SECONDS    超时时间，默认10秒

输出格式:
    {
      "success": true,
      "data": {
        "file": "dev_docs/api_layer.md",
        "summary": {
          "title": "API层设计规范",
          "summary": "定义前端API调用的统一接口规范...",
          "keywords": ["API", "HTTP", "Axios"],
          "scope": "前端API层 (src/api/)",
          "related_files": ["src/api/http.ts", "src/api/types.ts"],
          "dependencies": ["dev_docs/state_management.md"],
          "verified_at": "2025-12-03"
        }
      },
      "metadata": {
        "elapsed_seconds": 0.15,
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }
    
    # 批量模式输出
    {
      "success": true,
      "data": {
        "summaries": [
          {"file": "...", "summary": {...}},
          {"file": "...", "summary": {...}}
        ],
        "total_files": 5,
        "successful": 5,
        "failed": 0
      },
      "metadata": {...}
    }

使用示例:
    # 1. 提取单个文档摘要
    python tools/py/summary_extractor.py --file reference/examples/summary_examples/architecture_doc_example.md
    
    # 2. 批量提取示例目录
    python tools/py/summary_extractor.py --dir reference/examples/summary_examples/
    
    # 3. 递归扫描整个dev_docs目录
    python tools/py/summary_extractor.py --dir dev_docs/ --recursive
    
    # 4. 自定义超时时间
    python tools/py/summary_extractor.py --dir dev_docs/ --timeout 20

版本信息:
    Version: 1.0.0
    Created: 2025-12-03
    Purpose: Support 012-Mandatory Document Summary mechanism
"""

import os
import re
import json
import time
import argparse
from pathlib import Path

VERSION = "1.0.0"
DEFAULT_TIMEOUT = 10

def extract_frontmatter(content):
    """
    提取YAML Frontmatter
    
    优先使用YAML块匹配，备用正则表达式方案
    """
    # 匹配YAML Frontmatter块：开头的---到第二个---
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    yaml_content = match.group(1)
    return parse_yaml_simple(yaml_content)

def parse_yaml_simple(yaml_str):
    """
    简单的YAML解析器（仅使用标准库）
    
    支持单行键值对格式，使用 | 分隔列表
    """
    result = {}
    lines = yaml_str.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 解析 key: value 格式
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # 处理值
        if not value or value.lower() in ['无', 'none', '']:
            result[key] = None
        elif '|' in value:
            # 使用 | 分隔的列表
            result[key] = [item.strip() for item in value.split('|') if item.strip()]
        else:
            # 移除引号
            value = value.strip('"\'')
            result[key] = value
    
    return result

def extract_summary_from_file(file_path):
    """
    从单个文件提取摘要
    
    Returns:
        dict: 包含file和summary的字典，失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = extract_frontmatter(content)
        
        if not summary:
            return {
                "file": file_path,
                "summary": None,
                "error": "No YAML Frontmatter found"
            }
        
        # 验证必须字段是否存在
        required_fields = ['title', 'summary', 'keywords', 'scope', 'related_files', 'dependencies', 'verified_at']
        missing_fields = [field for field in required_fields if field not in summary]
        
        result = {
            "file": file_path,
            "summary": summary
        }
        
        if missing_fields:
            result["warning"] = f"Missing fields: {', '.join(missing_fields)}"
        
        return result
        
    except Exception as e:
        return {
            "file": file_path,
            "summary": None,
            "error": str(e)
        }

def find_markdown_files(directory, recursive=False):
    """
    查找目录下的所有Markdown文件
    """
    md_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            # 排除常见的忽略目录
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    else:
        # 仅扫描当前目录
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith('.md'):
                md_files.append(file_path)
    
    return md_files

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(
        description="从Markdown文档中提取YAML Frontmatter摘要",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--file", help="单个Markdown文件路径")
    parser.add_argument("--dir", help="批量处理目录路径")
    parser.add_argument("--recursive", action="store_true", help="递归扫描子目录")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间（秒），默认{DEFAULT_TIMEOUT}秒")
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.file and not args.dir:
        parser.error("必须指定 --file 或 --dir 参数")
    
    if args.file and args.dir:
        parser.error("--file 和 --dir 不能同时使用")
    
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
        # 单文件模式
        if args.file:
            if not os.path.isfile(args.file):
                result["success"] = False
                result["error"] = f"File not found: {args.file}"
            else:
                extraction = extract_summary_from_file(args.file)
                result["data"] = extraction
                
                if "error" in extraction:
                    result["success"] = False
        
        # 批量模式
        else:
            if not os.path.isdir(args.dir):
                result["success"] = False
                result["error"] = f"Directory not found: {args.dir}"
            else:
                md_files = find_markdown_files(args.dir, args.recursive)
                
                summaries = []
                successful = 0
                failed = 0
                
                for md_file in md_files:
                    # 检查超时
                    if time.time() - start_time > args.timeout:
                        result["warning"] = "Timeout reached, partial results returned"
                        break
                    
                    extraction = extract_summary_from_file(md_file)
                    summaries.append(extraction)
                    
                    if "error" not in extraction or extraction.get("summary") is not None:
                        successful += 1
                    else:
                        failed += 1
                
                result["data"] = {
                    "summaries": summaries,
                    "total_files": len(md_files),
                    "processed": len(summaries),
                    "successful": successful,
                    "failed": failed
                }
    
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
