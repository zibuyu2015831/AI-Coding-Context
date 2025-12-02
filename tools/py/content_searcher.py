"""
内容搜索工具 - 在项目文件中搜索文本（类似 grep）

功能说明：
- 优先使用 ripgrep (rg) 进行高速搜索
- 当 ripgrep 不可用时，自动降级到纯 Python 实现
- 支持正则表达式和固定字符串搜索
- 支持文件包含/排除模式
- 自动处理超时和编码问题

使用方法：
    python tools/py/content_searcher.py --query "搜索内容" [选项]

参数说明：
    --query QUERY            要搜索的文本（必需）
    --path PATH              搜索根目录（默认：当前目录）
    --include PATTERNS       逗号分隔的包含模式（如："*.py,*.js"）
    --exclude PATTERNS       逗号分隔的排除模式（如："node_modules,dist"）
    --regex                  将查询视为正则表达式（默认：否）
    --timeout SECONDS        搜索超时时间（默认：5秒）

输出格式：
    {
      "data": {
        "matches": [
          {"file": "文件路径", "line": 行号, "content": "匹配内容"},
          ...
        ]
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 搜索所有 TODO 注释
    python tools/py/content_searcher.py --query "TODO" --path ./src

    # 仅在 Python 文件中搜索
    python tools/py/content_searcher.py --query "import" --include "*.py"

    # 使用正则表达式搜索
    python tools/py/content_searcher.py --query "def\\s+\\w+" --regex

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import os
import json
import argparse
import subprocess
import re
import sys
import time
import fnmatch

def run_ripgrep(query, path, includes, excludes, is_regex, timeout):
    cmd = ["rg", "--json", "--line-number", "--heading", "--color=never"]
    
    if not is_regex:
        cmd.append("--fixed-strings")
    
    if includes:
        for inc in includes:
            cmd.extend(["--glob", inc])
            
    if excludes:
        for exc in excludes:
            cmd.extend(["--glob", f"!{exc}"])
            
    cmd.append(query)
    cmd.append(path)
    
    try:
        # Run rg with timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        matches = []
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                try:
                    data = json.loads(line)
                    if data["type"] == "match":
                        file_path = data["data"]["path"]["text"]
                        line_num = data["data"]["line_number"]
                        content = data["data"]["lines"]["text"].strip()
                        matches.append({
                            "file": file_path,
                            "line": line_num,
                            "content": content
                        })
                except json.JSONDecodeError:
                    continue
        return matches
    except FileNotFoundError:
        return None # rg not found
    except subprocess.TimeoutExpired:
        return {"error": "Search timed out (rg)"}
    except Exception as e:
        return {"error": str(e)}

def fallback_search(query, root_path, includes, excludes, is_regex, timeout):
    matches = []
    start_time = time.time()
    
    try:
        pattern = re.compile(query) if is_regex else None
    except re.error as e:
        return {"error": f"Invalid regex: {e}"}

    for root, dirs, files in os.walk(root_path):
        # Check timeout
        if time.time() - start_time > timeout:
             return {"error": "Search timed out (fallback)"}

        # Handle excludes for directories
        if excludes:
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, exc) for exc in excludes)]

        for file in files:
            if time.time() - start_time > timeout:
                return {"error": "Search timed out (fallback)"}
                
            # Handle includes/excludes for files
            if includes:
                if not any(fnmatch.fnmatch(file, inc) for inc in includes):
                    continue
            if excludes:
                if any(fnmatch.fnmatch(file, exc) for exc in excludes):
                    continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        line = line.strip()
                        found = False
                        if is_regex:
                            if pattern.search(line):
                                found = True
                        else:
                            if query in line:
                                found = True
                        
                        if found:
                            matches.append({
                                "file": file_path,
                                "line": i,
                                "content": line
                            })
            except Exception:
                continue # Skip unreadable files
                
    return matches

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Content Searcher")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--path", default=".", help="Root directory to search")
    parser.add_argument("--include", help="Comma-separated glob patterns to include")
    parser.add_argument("--exclude", help="Comma-separated glob patterns to exclude")
    parser.add_argument("--regex", action="store_true", help="Treat query as regex")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    includes = args.include.split(",") if args.include else []
    excludes = args.exclude.split(",") if args.exclude else []
    
    # Try rg first
    matches = run_ripgrep(args.query, args.path, includes, excludes, args.regex, args.timeout)
    
    if matches is None:
        # Fallback to python
        matches = fallback_search(args.query, args.path, includes, excludes, args.regex, args.timeout)
    
    elapsed_time = round(time.time() - start_time, 2)
    
    if isinstance(matches, dict) and "error" in matches:
         matches["metadata"] = {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
         print(json.dumps(matches, indent=2, ensure_ascii=False))
    else:
         result = {
             "data": {"matches": matches},
             "metadata": {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
         }
         print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
