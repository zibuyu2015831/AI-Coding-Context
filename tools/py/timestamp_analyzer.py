"""
时间戳分析工具 - 采集项目文件和文档的修改时间供 AI 分析文档健康度

用法:
    python tools/py/timestamp_analyzer.py [--project-root ./]

输出:
    {
      "data": {
        "project_files": [
          {"path": "src/api/user.ts", "modified_at": "2025-12-01T15:30:00"}
        ],
        "doc_files": [
          {"path": "dev_docs/api_layer.md", "modified_at": "2025-11-10T16:00:00"}
        ],
        "stats": {
          "total_project_files": 245,
          "total_doc_files": 8,
          "scan_time": "2025-12-02T14:00:00"
        }
      },
      "metadata": {
        "elapsed_seconds": 2.1,
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }
"""

import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

def load_gitignore_patterns(root_dir):
    """加载 .gitignore 模式"""
    patterns = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            pass
    return patterns

def should_ignore(rel_path, patterns):
    """检查文件是否应被忽略（简化的 gitignore 匹配）"""
    # 始终忽略这些目录
    ignored_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'venv'}
    
    parts = Path(rel_path).parts
    if any(part in ignored_dirs for part in parts):
        return True
    
    # 检查 gitignore 模式（简化匹配）
    for pattern in patterns:
        if pattern in rel_path or rel_path.startswith(pattern.rstrip('/')):
            return True
    
    return False

def get_file_timestamp(file_path):
    """获取文件修改时间（仅使用 st_mtime，跨平台一致）"""
    try:
        stat = os.stat(file_path)
        return datetime.fromtimestamp(stat.st_mtime).isoformat()
    except Exception:
        return None

def scan_directory(root_dir, patterns, max_files=5000):
    """扫描目录并采集时间戳"""
    project_files = []
    doc_files = []
    scanned_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # 排除被忽略的目录（in-place修改）
        dirs[:] = [d for d in dirs if not should_ignore(os.path.relpath(os.path.join(root, d), root_dir), patterns)]
        
        for file in files:
            if scanned_count >= max_files:
                break
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            
            if should_ignore(rel_path, patterns):
                continue
            
            modified_at = get_file_timestamp(file_path)
            if not modified_at:
                continue
            
            file_info = {
                "path": rel_path.replace(os.sep, '/'),  # 统一使用正斜杠
                "modified_at": modified_at
            }
            
# 判断是文档还是项目文件
            if rel_path.startswith('dev_docs' + os.sep) or file.endswith('.md'):
                doc_files.append(file_info)
            else:
                project_files.append(file_info)
            
            scanned_count += 1
        
        if scanned_count >= max_files:
            break
    
    return project_files, doc_files

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="采集文件时间戳供 AI 分析文档健康度")
    parser.add_argument("--project-root", default="./", help="项目根目录")
    parser.add_argument("--max-files", type=int, default=5000, help="最大扫描文件数")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.project_root)
    patterns = load_gitignore_patterns(root_dir)
    
    project_files, doc_files = scan_directory(root_dir, patterns, args.max_files)
    
    elapsed_time = round(time.time() - start_time, 2)
    
    result = {
        "data": {
            "project_files": project_files,
            "doc_files": doc_files,
            "stats": {
                "total_project_files": len(project_files),
                "total_doc_files": len(doc_files),
                "scan_time": datetime.now().isoformat()
            }
        },
        "metadata": {
            "elapsed_seconds": elapsed_time,
            "timeout_threshold": 10,
            "version": "1.1.0"
        }
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
