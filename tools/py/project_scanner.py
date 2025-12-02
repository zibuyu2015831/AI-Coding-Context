"""
项目结构扫描工具 - 生成项目目录树的 JSON 或文本表示

功能说明：
- 扫描指定目录，生成完整的目录树结构
- 自动读取并尊重 .gitignore 规则
- 支持限制扫描深度和每目录文件数
- 支持输出 JSON 格式（供 AI 解析）或树形文本格式（供人类阅读）

使用方法：
    python tools/py/project_scanner.py [--path 路径] [选项]

参数说明：
    --path PATH              要扫描的根目录路径（默认：当前目录）
    --ignore PATTERNS        逗号分隔的忽略模式（会自动叠加 .gitignore）
    --follow-symlinks        跟随符号链接（默认：否）
    --max-files NUM          每个目录最多显示的文件数（默认：1000）
    --depth NUM              最大扫描深度（默认：无限制）
    --format FORMAT          输出格式：json 或 tree（默认：json）

输出格式（JSON模式）：
    {
      "data": {
        "structure": {目录树对象},
        "stats": {"files": 文件数, "dirs": 目录数}
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 扫描当前项目（JSON 格式）
    python tools/py/project_scanner.py --path . --max-files 100

    # 扫描 src 目录（限制深度为 3）
    python tools/py/project_scanner.py --path ./src --depth 3

    # 生成人类可读的树形结构
    python tools/py/project_scanner.py --format tree

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import os
import json
import argparse
import fnmatch
import sys
import time
from collections import deque

def load_gitignore_patterns(root_dir):
    patterns = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    patterns.append(line)
        except Exception as e:
            sys.stderr.write(f"Warning: Could not read .gitignore: {e}\n")
    return patterns

def is_ignored(path, patterns, root_dir):
    rel_path = os.path.relpath(path, root_dir)
    if rel_path == '.':
        return False
    
    # Normalize path separators to /
    rel_path = rel_path.replace(os.sep, '/')
    name = os.path.basename(path)
    
    for pattern in patterns:
        # Handle directory-specific patterns (ending with /)
        if pattern.endswith('/'):
            if fnmatch.fnmatch(rel_path + '/', pattern) or fnmatch.fnmatch(name + '/', pattern):
                return True
        # Handle standard patterns
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False

def generate_tree(structure, prefix=""):
    lines = []
    keys = sorted(structure.keys())
    for i, key in enumerate(keys):
        is_last = (i == len(keys) - 1)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{key}")
        
        if isinstance(structure[key], dict):
            extension = "    " if is_last else "│   "
            lines.extend(generate_tree(structure[key], prefix + extension))
    return lines

def scan_project(root_dir, ignore_patterns, follow_symlinks, max_files_per_dir, max_depth):
    structure = {}
    stats = {"files": 0, "dirs": 0}
    
    # Queue for BFS: (current_path, current_depth, parent_structure_dict)
    queue = deque([(root_dir, 0, structure)])
    
    # Base ignore patterns (always ignore .git)
    all_patterns = ignore_patterns + ['.git']
    gitignore_patterns = load_gitignore_patterns(root_dir)
    all_patterns.extend(gitignore_patterns)

    processed_dirs = set()

    while queue:
        current_path, depth, parent_dict = queue.popleft()
        
        if max_depth is not None and depth > max_depth:
            continue
            
        if not follow_symlinks and os.path.islink(current_path):
            continue
            
        real_path = os.path.realpath(current_path)
        if real_path in processed_dirs:
            continue
        processed_dirs.add(real_path)

        try:
            # Sort for consistent output
            entries = sorted(os.listdir(current_path))
        except PermissionError:
            sys.stderr.write(f"Warning: Permission denied accessing {current_path}\n")
            continue
        except Exception as e:
            sys.stderr.write(f"Warning: Error accessing {current_path}: {e}\n")
            continue

        file_count = 0
        dir_count = 0
        
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            
            if is_ignored(full_path, all_patterns, root_dir):
                continue
                
            if os.path.isdir(full_path):
                if not follow_symlinks and os.path.islink(full_path):
                     # Treat symlink to dir as file in structure if not following
                     parent_dict[entry] = "[Symlink Dir]"
                     stats["files"] += 1
                else:
                    new_dict = {}
                    parent_dict[entry] = new_dict
                    stats["dirs"] += 1
                    queue.append((full_path, depth + 1, new_dict))
            else:
                if file_count < max_files_per_dir:
                    parent_dict[entry] = None # Leaf node
                    stats["files"] += 1
                    file_count += 1
                elif file_count == max_files_per_dir:
                    parent_dict["..."] = f"(truncated, >{max_files_per_dir} files)"
                    file_count += 1 # Increment to ensure we don't add "..." multiple times

    return structure, stats

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Project Structure Scanner")
    parser.add_argument("--path", default=".", help="Root directory to scan")
    parser.add_argument("--ignore", help="Comma-separated glob patterns to ignore")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    parser.add_argument("--max-files", type=int, default=1000, help="Max files per directory")
    parser.add_argument("--depth", type=int, help="Max scan depth")
    parser.add_argument("--format", choices=["json", "tree"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.path)
    ignore_patterns = args.ignore.split(",") if args.ignore else []
    
    structure, stats = scan_project(
        root_dir, 
        ignore_patterns, 
        args.follow_symlinks, 
        args.max_files, 
        args.depth
    )
    
    elapsed_time = round(time.time() - start_time, 2)
    
    if args.format == "json":
        result = {
            "data": {"structure": structure, "stats": stats},
            "metadata": {
                "elapsed_seconds": elapsed_time,
                "timeout_threshold": 10,
                "version": "1.1.0"
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        tree_lines = generate_tree(structure)
        print("\n".join(tree_lines))
        print(f"\nStats: {stats['files']} files, {stats['dirs']} directories")
        print(f"Elapsed: {elapsed_time}s")

if __name__ == "__main__":
    main()
