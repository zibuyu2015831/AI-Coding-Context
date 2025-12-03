"""
文档摘要索引生成器 - 生成文档摘要索引页

⚠️ 状态说明:
    此工具暂不启用,后续根据需要决定是否使用。
    原因: 索引页生成可能导致冗余信息,且不确定实际使用价值。
    如需启用,请移除此注释并在implementation_plan中更新状态。

功能说明:
    - 遍历所有文档
    - 批量提取摘要
    - 生成Markdown格式索引页
    - 支持按分类组织索引

使用方法:
    # 生成索引页
    python tools/py/summary_index_generator.py --doc-dir dev_docs/ --output dev_docs/_index.md
    
    # 递归扫描
    python tools/py/summary_index_generator.py --doc-dir dev_docs/ --output dev_docs/_index.md --recursive
    
    # 按分类组织
    python tools/py/summary_index_generator.py --doc-dir dev_docs/ --output dev_docs/_index.md --group-by-dir

参数说明:
    --doc-dir PATH      文档目录,默认dev_docs/
    --output PATH       输出索引文件路径
    --recursive         递归扫描子目录
    --group-by-dir      按目录分组索引
    --timeout SECONDS   超时时间,默认10秒

输出格式:
    生成的索引页为Markdown格式,包含所有文档的摘要信息

版本信息:
    Version: 1.0.0
    Created: 2025-12-03
    Purpose: Support 012-Mandatory Document Summary mechanism
    Status: DISABLED - 暂不启用
"""

import os
import re
import json
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

def extract_summary_from_file(file_path):
    """从单个文件提取摘要"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = extract_frontmatter(content)
        
        return {
            "file": file_path,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "file": file_path,
            "summary": None,
            "error": str(e)
        }

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

def generate_index_markdown(summaries, group_by_dir=False):
    """生成索引页Markdown内容"""
    lines = []
    
    lines.append("# 文档索引")
    lines.append("")
    lines.append("> 📋 本文档由工具自动生成,包含所有文档的摘要信息")
    lines.append("")
    lines.append(f"> 🕐 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if group_by_dir:
        # 按目录分组
        grouped = defaultdict(list)
        for item in summaries:
            if item.get("summary"):
                dir_name = os.path.dirname(item["file"])
                if not dir_name:
                    dir_name = "根目录"
                grouped[dir_name].append(item)
        
        for dir_name in sorted(grouped.keys()):
            lines.append(f"## {dir_name}")
            lines.append("")
            
            for item in grouped[dir_name]:
                summary = item["summary"]
                file_name = os.path.basename(item["file"])
                
                lines.append(f"### [{summary.get('title', file_name)}]({item['file']})")
                lines.append("")
                lines.append(f"**摘要**: {summary.get('summary', '无')}")
                lines.append("")
                
                if summary.get('keywords'):
                    keywords = summary['keywords'] if isinstance(summary['keywords'], list) else [summary['keywords']]
                    lines.append(f"**关键词**: {', '.join(keywords)}")
                    lines.append("")
                
                if summary.get('scope'):
                    lines.append(f"**范围**: {summary['scope']}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
    else:
        # 不分组,按文件名排序
        sorted_summaries = sorted(summaries, key=lambda x: x["file"])
        
        for item in sorted_summaries:
            if not item.get("summary"):
                continue
            
            summary = item["summary"]
            file_name = os.path.basename(item["file"])
            
            lines.append(f"## [{summary.get('title', file_name)}]({item['file']})")
            lines.append("")
            lines.append(f"**文件**: `{item['file']}`")
            lines.append("")
            lines.append(f"**摘要**: {summary.get('summary', '无')}")
            lines.append("")
            
            if summary.get('keywords'):
                keywords = summary['keywords'] if isinstance(summary['keywords'], list) else [summary['keywords']]
                lines.append(f"**关键词**: {', '.join(keywords)}")
                lines.append("")
            
            if summary.get('scope'):
                lines.append(f"**范围**: {summary['scope']}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    return '\n'.join(lines)

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(
        description="生成文档摘要索引页 (当前暂不启用)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录,默认{DEFAULT_DOC_DIR}")
    parser.add_argument("--output", required=True, help="输出索引文件路径")
    parser.add_argument("--recursive", action="store_true", help="递归扫描子目录")
    parser.add_argument("--group-by-dir", action="store_true", help="按目录分组索引")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间(秒),默认{DEFAULT_TIMEOUT}秒")
    
    args = parser.parse_args()
    
    result = {
        "success": True,
        "data": {},
        "metadata": {
            "elapsed_seconds": 0,
            "timeout_threshold": args.timeout,
            "version": VERSION,
            "status": "DISABLED - 此工具暂不启用"
        }
    }
    
    try:
        # 检查文档目录
        if not os.path.isdir(args.doc_dir):
            result["success"] = False
            result["error"] = f"Document directory not found: {args.doc_dir}"
        else:
            # 查找所有文档
            md_files = find_markdown_files(args.doc_dir, args.recursive)
            
            # 提取摘要
            summaries = []
            for md_file in md_files:
                # 检查超时
                if time.time() - start_time > args.timeout:
                    result["warning"] = "Timeout reached, partial results returned"
                    break
                
                extraction = extract_summary_from_file(md_file)
                summaries.append(extraction)
            
            # 生成索引
            index_content = generate_index_markdown(summaries, args.group_by_dir)
            
            # 写入文件
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            result["data"] = {
                "output_file": args.output,
                "total_files": len(md_files),
                "processed": len(summaries),
                "has_summary": sum(1 for s in summaries if s.get("summary"))
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
