"""
Git 仓库检查工具 - 获取 Git 仓库状态信息

功能说明：
- 检测当前目录是否为 Git 仓库
- 获取当前分支名称
- 列出所有未提交的变更文件
- 检测仓库是否干净（无变更）

使用方法：
    python tools/py/git_inspector.py [--mode MODE]

参数说明：
    --mode MODE              检查模式（默认：status）
                            可选值：status（仓库状态）

输出格式：
    {
      "data": {
        "branch": "分支名",
        "changes": [
          {"status": "状态码", "file": "文件路径"},
          ...
        ],
        "clean": 是否干净(bool)
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 检查仓库状态
    python tools/py/git_inspector.py --mode status

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import json
import subprocess
import argparse
import time

def get_git_status():
    try:
        # Check if git exists
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        
        # Get status
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": "Not a git repository or git error"}
            
        lines = result.stdout.splitlines()
        changes = []
        for line in lines:
            if len(line) > 3:
                status = line[:2]
                file = line[3:]
                changes.append({"status": status, "file": file})
                
        # Get branch
        branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        branch = branch_res.stdout.strip()
        
        return {
            "branch": branch,
            "changes": changes,
            "clean": len(changes) == 0
        }
    except FileNotFoundError:
        return {"error": "Git not found"}
    except Exception as e:
        return {"error": str(e)}

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Git Inspector")
    parser.add_argument("--mode", default="status", help="Inspection mode")
    args = parser.parse_args()
    
    git_data = get_git_status() if args.mode == "status" else {"error": f"Unknown mode: {args.mode}"}
    
    elapsed_time = round(time.time() - start_time, 2)
    result = {
        "data": git_data,
        "metadata": {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
