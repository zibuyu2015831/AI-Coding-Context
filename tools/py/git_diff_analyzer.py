"""
Git 差异分析工具 - 分析代码变更供 AI 判断文档更新需求

用法:
    python tools/py/git_diff_analyzer.py [--since "2025-11-10" | --since "7 days ago"]

输出:
    {
      "data": {
        "reference_point": "2025-11-10T16:00:00",
        "changed_files": [
          {"path": "src/api/user.ts", "change_type": "modified", "lines_changed": 45}
        ],
        "summary": {
          "total_files_changed": 2,
          "files_by_type": {"modified": 1, "added": 1, "deleted": 0}
        }
      },
      "metadata": {
        "git_available": true,
        "elapsed_seconds": 0.8,
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }
"""

import subprocess
import json
import time
import argparse
from datetime import datetime

def check_git_available():
    """检查 git 是否可用"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True, timeout=2)
        return True
    except:
        return False

def get_reference_commit(since):
    """获取参考时间点的 commit 哈希"""
    try:
        if "ago" in since or "days" in since or "hours" in since:
            # git log 支持相对时间
            cmd = ["git", "log", f"--since={since}", "--max-count=1", "--format=%H"]
        else:
            # 具体日期格式
            cmd = ["git", "log", f"--since={since}", "--max-count=1", "--format=%H"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
        return result.stdout.strip()
    except:
        return "HEAD~10"  # 默认对比最近 10 个提交

def analyze_changes(since_commit="HEAD~10"):
    """分析自指定提交以来的变更"""
    try:
        # 获取变更文件列表（带统计）
        cmd = ["git", "diff", "--numstat", f"{since_commit}..HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        
        changes = []
        files_by_type = {"modified": 0, "added": 0, "deleted": 0}
        
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            
            parts = line.split('\t')
            if len(parts) != 3:
                continue
            
            added, deleted, filepath = parts
            
            # 判断变更类型
            if added == '0' and deleted != '0':
                change_type = "deleted"
                lines_changed = int(deleted) if deleted.isdigit() else 0
            elif deleted == '0' and added != '0':
                change_type = "added"
                lines_changed = int(added) if added.isdigit() else 0
            else:
                change_type = "modified"
                lines_changed = (int(added) if added.isdigit() else 0) + (int(deleted) if deleted.isdigit() else 0)
            
            files_by_type[change_type] += 1
            
            changes.append({
                "path": filepath,
                "change_type": change_type,
                "lines_changed": lines_changed
            })
        
        return changes, files_by_type
    
    except subprocess.TimeoutExpired:
        return None, {"error": "timeout"}
    except Exception as e:
        return None, {"error": str(e)}

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Git 差异分析供 AI 判断文档更新需求")
    parser.add_argument("--since", default="7 days ago", help="对比起点（如 '2025-11-10' 或 '7 days ago'）")
    args = parser.parse_args()
    
    # 检查 git 可用性
    if not check_git_available():
        elapsed_time = round(time.time() - start_time, 2)
        result = {
            "success": False,
            "error": "git_not_available",
            "suggestion": "使用 timestamp_analyzer.py 作为替代",
            "metadata": {
                "git_available": False,
                "elapsed_seconds": elapsed_time,
                "timeout_threshold": 10,
                "version": "1.1.0"
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    # 获取参考提交
    reference_commit = get_reference_commit(args.since)
    
    # 分析变更
    changed_files, files_by_type = analyze_changes(reference_commit)
    
    elapsed_time = round(time.time() - start_time, 2)
    
    if changed_files is None:
        # 发生错误
        result = {
            "success": False,
            "error": files_by_type.get("error", "unknown"),
            "suggestion": "检查 git 仓库状态或使用 timestamp_analyzer.py",
            "metadata": {
                "git_available": True,
                "elapsed_seconds": elapsed_time,
                "timeout_threshold": 10,
                "version": "1.1.0"
            }
        }
    else:
        # 成功
        result = {
            "data": {
                "reference_commit": reference_commit,
                "changed_files": changed_files,
                "summary": {
                    "total_files_changed": len(changed_files),
                    "files_by_type": files_by_type
                }
            },
            "metadata": {
                "git_available": True,
                "elapsed_seconds": elapsed_time,
                "timeout_threshold": 10,
                "version": "1.1.0"
            }
        }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
