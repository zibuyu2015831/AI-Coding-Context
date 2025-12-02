"""
文件查找工具 - 根据文件名模式查找文件（类似 find）

功能说明：
- 递归遍历目录查找匹配的文件
- 支持通配符模式（如 *.py, config.*.js）
- 可限制返回结果数量
- 纯 Python 实现，无外部依赖

使用方法：
    python tools/py/file_finder.py --pattern "模式" [选项]

参数说明：
    --pattern PATTERN        文件名匹配模式（必need），支持 * 和 ? 通配符
    --path PATH              搜索根目录（默认：当前目录）
    --limit NUM              最大返回结果数（默认：无限制）

输出格式：
    {
      "data": {
        "files": ["文件路径1", "文件路径2", ...]
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 查找所有 Markdown 文件
    python tools/py/file_finder.py --pattern "*.md" --path ./docs

    # 查找配置文件（限制 10 个结果）
    python tools/py/file_finder.py --pattern "config.*" --limit 10

    # 查找 Python 测试文件
    python tools/py/file_finder.py --pattern "test_*.py"

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import os
import json
import argparse
import fnmatch
import time

def find_files(path, pattern, limit):
    matches = []
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, pattern):
            matches.append(os.path.join(root, filename))
            if limit and len(matches) >= limit:
                return matches
    return matches

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="File Finder")
    parser.add_argument("--pattern", required=True, help="Glob pattern")
    parser.add_argument("--path", default=".", help="Root directory to search")
    parser.add_argument("--limit", type=int, help="Max results")
    
    args = parser.parse_args()
    
    files = find_files(args.path, args.pattern, args.limit)
    
    elapsed_time = round(time.time() - start_time, 2)
    result = {
        "data": {"files": files},
        "metadata": {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
