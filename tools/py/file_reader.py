"""
文件读取工具 - 安全地读取文件内容（支持大文件分页）

功能说明：
- 自动检测二进制文件并跳过
- 自动尝试多种编码（utf-8, gbk, latin-1）
- 支持按行分页读取大文件
- 统计总行数并标识是否截断

使用方法：
    python tools/py/file_reader.py --path "文件路径" [选项]

参数说明：
    --path PATH              要读取的文件路径（必需）
    --offset NUM             起始行号（0-indexed，默认：0）
    --limit NUM              最多读取行数（默认：1000）

输出格式：
    {
      "data": {
        "content": "文件内容（字符串）",
        "lines_read": 读取的行数,
        "total_lines": 文件总行数,
        "truncated": 是否被截断(bool),
        "is_binary": 是否为二进制文件(bool),
        "encoding": "使用的编码"
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 读取文件前 50 行
    python tools/py/file_reader.py --path ./README.md --limit 50

    # 读取第 100-200 行
    python tools/py/file_reader.py --path ./log.txt --offset 100 --limit 100

    # 读取整个文件
    python tools/py/file_reader.py --path ./config.json

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import os
import json
import argparse
import sys
import time

def is_binary_file(filepath, chunk_size=1024):
    """Check if file is binary by looking for null bytes in the first chunk."""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(chunk_size)
            if b'\0' in chunk:
                return True
    except Exception:
        pass
    return False

def count_lines(filepath, encoding):
    """Count total lines in file efficiently."""
    count = 0
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            for _ in f:
                count += 1
    except Exception:
        pass
    return count

def read_file(filepath, offset, limit):
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    
    if is_binary_file(filepath):
        return {
            "content": None,
            "lines_read": 0,
            "total_lines": 0,
            "truncated": False,
            "is_binary": True
        }

    encodings = ['utf-8', sys.getdefaultencoding(), 'latin-1']
    content = ""
    lines_read = 0
    total_lines = 0
    encoding_used = None
    
    # Try encodings
    for enc in encodings:
        try:
            total_lines = count_lines(filepath, enc)
            with open(filepath, 'r', encoding=enc) as f:
                # Skip to offset
                for _ in range(offset):
                    next(f, None)
                
                # Read limit lines
                lines = []
                for _ in range(limit):
                    line = next(f, None)
                    if line is None:
                        break
                    lines.append(line)
                
                content = "".join(lines)
                lines_read = len(lines)
                encoding_used = enc
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return {"error": str(e)}
            
    if encoding_used is None:
         return {
            "content": None,
            "lines_read": 0,
            "total_lines": 0,
            "truncated": False,
            "is_binary": True,
            "note": "Failed to decode text with common encodings"
        }

    truncated = (offset + lines_read) < total_lines

    return {
        "content": content,
        "lines_read": lines_read,
        "total_lines": total_lines,
        "truncated": truncated,
        "is_binary": False,
        "encoding": encoding_used
    }

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Safe File Reader")
    parser.add_argument("--path", required=True, help="File path to read")
    parser.add_argument("--offset", type=int, default=0, help="Start line (0-indexed)")
    parser.add_argument("--limit", type=int, default=1000, help="Max lines to read")
    
    args = parser.parse_args()
    
    result = read_file(args.path, args.offset, args.limit)
    
    elapsed_time = round(time.time() - start_time, 2)
    output = {
        "data": result,
        "metadata": {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
