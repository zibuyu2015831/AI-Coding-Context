"""
文档关联检查工具 - 检测哪些文档的related_files包含已变更的代码

功能说明:
    - 提取所有文档的related_files字段
    - 对比代码变更文件列表
    - 输出受影响的文档列表
    - 支持从stdin读取(配合git_diff_analyzer)
    - 提供更新建议

使用方法:
    # 指定变更文件列表
    python tools/py/summary_related_checker.py --changed-files "src/api/user.ts,src/api/post.ts"
    
    # 从stdin读取(配合git_diff_analyzer)
    python tools/py/git_diff_analyzer.py --since "7 days ago" | python tools/py/summary_related_checker.py --from-stdin
    
    # 指定文档目录
    python tools/py/summary_related_checker.py --changed-files "src/api/user.ts" --doc-dir dev_docs/
    
    # 递归扫描
    python tools/py/summary_related_checker.py --changed-files "src/api/user.ts" --doc-dir dev_docs/ --recursive

参数说明:
    --changed-files FILES    逗号分隔的变更文件列表
    --from-stdin             从stdin读取变更文件(JSON格式,来自git_diff_analyzer)
    --doc-dir PATH           文档目录,默认为dev_docs/
    --recursive              递归扫描文档目录
    --timeout SECONDS        超时时间,默认10秒

输出格式:
    {
      "success": true,
      "data": {
        "affected_docs": [
          {
            "file": "dev_docs/api_layer.md",
            "matched_files": ["src/api/user.ts"],
            "suggestion": "建议更新此文档,因为关联文件已变更"
          }
        ],
        "total_docs_scanned": 50,
        "total_affected": 3,
        "changed_files": ["src/api/user.ts", "src/api/post.ts"]
      },
      "metadata": {
        "elapsed_seconds": 0.25,
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }

版本信息:
    Version: 1.0.0
    Created: 2025-12-03
    Purpose: Support 012-Mandatory Document Summary mechanism
"""

import os
import re
import json
import sys
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

def extract_related_files(file_path):
    """
    从文档提取related_files
    
    Returns:
        list or None: 关联文件列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = extract_frontmatter(content)
        
        if not summary or 'related_files' not in summary:
            return None
        
        related = summary['related_files']
        if isinstance(related, list):
            # 过滤掉'无'等占位符
            return [f for f in related if f and f != '无']
        elif isinstance(related, str) and related != '无':
            return [related]
        
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

def check_affected_docs(changed_files, doc_dir, recursive=False):
    """
    检查哪些文档受变更文件影响
    
    Args:
        changed_files: 变更文件列表
        doc_dir: 文档目录
        recursive: 是否递归扫描
    
    Returns:
        dict: 受影响的文档信息
    """
    # 标准化变更文件路径
    changed_files_normalized = [normalize_path(f) for f in changed_files]
    
    # 查找所有文档
    md_files = find_markdown_files(doc_dir, recursive)
    
    affected_docs = []
    
    for md_file in md_files:
        related_files = extract_related_files(md_file)
        
        if not related_files:
            continue
        
        # 检查是否有匹配的文件
        matched_files = []
        for related in related_files:
            related_normalized = normalize_path(related)
            for changed in changed_files_normalized:
                # 支持部分路径匹配
                if related_normalized in changed or changed in related_normalized:
                    matched_files.append(related)
                    break
        
        if matched_files:
            affected_docs.append({
                "file": md_file,
                "matched_files": matched_files,
                "all_related_files": related_files,
                "suggestion": "建议更新此文档,因为关联文件已变更"
            })
    
    return {
        "affected_docs": affected_docs,
        "total_docs_scanned": len(md_files),
        "total_affected": len(affected_docs),
        "changed_files": changed_files
    }

def parse_git_diff_output(json_str):
    """解析git_diff_analyzer的JSON输出"""
    try:
        data = json.loads(json_str)
        
        if not data.get("success"):
            return None
        
        # 提取文件列表
        files = []
        if "data" in data and "files" in data["data"]:
            files = data["data"]["files"]
        elif "data" in data and "changed_files" in data["data"]:
            files = data["data"]["changed_files"]
        
        return files
        
    except Exception as e:
        return None

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(
        description="检测哪些文档的related_files包含已变更的代码",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--changed-files", help="逗号分隔的变更文件列表")
    parser.add_argument("--from-stdin", action="store_true", help="从stdin读取变更文件(JSON格式)")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录,默认{DEFAULT_DOC_DIR}")
    parser.add_argument("--recursive", action="store_true", help="递归扫描文档目录")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间(秒),默认{DEFAULT_TIMEOUT}秒")
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.changed_files and not args.from_stdin:
        parser.error("必须指定 --changed-files 或 --from-stdin")
    
    if args.changed_files and args.from_stdin:
        parser.error("--changed-files 和 --from-stdin 不能同时使用")
    
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
        # 获取变更文件列表
        changed_files = []
        
        if args.from_stdin:
            # 从stdin读取
            stdin_content = sys.stdin.read()
            parsed_files = parse_git_diff_output(stdin_content)
            
            if parsed_files is None:
                result["success"] = False
                result["error"] = "Failed to parse stdin input (expected JSON from git_diff_analyzer)"
            else:
                changed_files = parsed_files
        else:
            # 从参数读取
            changed_files = [f.strip() for f in args.changed_files.split(',')]
        
        if not changed_files:
            result["success"] = False
            result["error"] = "No changed files provided"
        else:
            # 检查文档目录是否存在
            if not os.path.isdir(args.doc_dir):
                result["success"] = False
                result["error"] = f"Document directory not found: {args.doc_dir}"
            else:
                # 执行检查
                check_result = check_affected_docs(changed_files, args.doc_dir, args.recursive)
                result["data"] = check_result
    
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
