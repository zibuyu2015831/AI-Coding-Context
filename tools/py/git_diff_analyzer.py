"""
Git 差异分析工具 - 分析 Git 变更供 AI 判断文档更新需求

功能说明:
    分析 Git 差异，识别受影响的文件和代码变更范围，
    为 AI 判断哪些文档需要更新提供数据支持。
    - 获取 Git diff 统计信息
    - 识别变更的文件列表
    - 分析代码变更量 (新增/删除行数)
    - 识别文件重命名和模式变更
    - 支持多种 diff 格式输出

使用方法:
    # 分析最近一次提交
    python tools/py/git_diff_analyzer.py

    # 分析指定提交范围
    python tools/py/git_diff_analyzer.py --commit-range HEAD~3..HEAD

    # 分析特定文件的变更
    python tools/py/git_diff_analyzer.py --files src/main.py,src/utils.py

    # 输出 JSON 格式
    python tools/py/git_diff_analyzer.py --format json

    # 分析工作区未暂存的变更
    python tools/py/git_diff_analyzer.py --unstaged

    # 分析已暂存但未提交的变更
    python tools/py/git_diff_analyzer.py --staged

参数说明:
    --commit-range RANGE    分析的提交范围 (例如: HEAD~3..HEAD)
    --files FILES          仅分析指定文件 (逗号分隔)
    --format FORMAT        输出格式: text, json (默认: text)
    --unstaged             分析工作区未暂存的变更
    --staged               分析已暂存但未提交的变更
    --short-stat           仅显示简短统计

输出格式:
    支持 text 和 json 两种输出格式:

    text 格式包含:
    - 提交范围信息
    - 变更文件统计
    - 每个文件的变更详情 (新增/删除行数)
    - 总体统计信息

    json 格式包含:
    {
      "commit_range": "HEAD~3..HEAD",
      "total_files_changed": 5,
      "total_insertions": 120,
      "total_deletions": 45,
      "files": [
        {
          "path": "src/main.py",
          "status": "modified",
          "insertions": 30,
          "deletions": 10
        }
      ]
    }

使用示例:
    # 示例 1: 分析最近 3 次提交
    python tools/py/git_diff_analyzer.py --commit-range HEAD~3..HEAD --format json

    # 示例 2: 检查工作区未暂存的变更
    python tools/py/git_diff_analyzer.py --unstaged

    # 示例 3: 仅查看简短统计
    python tools/py/git_diff_analyzer.py --short-stat

    # 示例 4: 分析特定文件的变更历史
    python tools/py/git_diff_analyzer.py --files src/core.py --commit-range HEAD~10..HEAD

与其他工具集成:
    # 配合 summary_related_checker 使用
    CHANGED_FILES=$(python tools/py/git_diff_analyzer.py --format json | jq -r '.files[].path')
    python tools/py/summary_related_checker.py --files "$CHANGED_FILES"

版本信息:
    版本: 1.0.0
    更新日期: 2026-01-20
"""

import os
import re
import subprocess
import json
import argparse
import sys
from typing import List, Dict, Any, Optional

VERSION = "1.0.0"


def run_git_command(args: List[str]) -> subprocess.CompletedProcess:
    """执行 Git 命令"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except FileNotFoundError:
        print("❌ 错误: 未找到 git 命令", file=sys.stderr)
        sys.exit(1)


def parse_diff_stats(diff_output: str) -> Dict[str, Any]:
    """解析 diff 统计信息"""
    stats = {
        "files": [],
        "total_insertions": 0,
        "total_deletions": 0,
        "total_files_changed": 0
    }

    # 解析统计行，格式: "1 file changed, 10 insertions(+), 5 deletions(-)"
    stat_pattern = r'(\d+)\s+files?\s+changed(?:,\s+(\d+)\s+insertions?\(\+\))?(?:,\s+(\d+)\s+deletions?\(-\))?'

    for line in diff_output.split('\n'):
        match = re.search(stat_pattern, line)
        if match:
            stats["total_files_changed"] = int(match.group(1))
            if match.group(2):
                stats["total_insertions"] = int(match.group(2))
            if match.group(3):
                stats["total_deletions"] = int(match.group(3))

    return stats


def get_file_diff(file_path: str, commit_range: str = "") -> Dict[str, Any]:
    """获取单个文件的 diff 信息"""
    args = ["diff"]
    if commit_range:
        args.extend(commit_range.split(".."))
    args.extend(["--", file_path])

    result = run_git_command(args)

    if result.returncode != 0:
        return None

    diff_text = result.stdout
    insertions = len(re.findall(r'^\+[^+]', diff_text, re.MULTILINE))
    deletions = len(re.findall(r'^-[^-]', diff_text, re.MULTILINE))

    return {
        "path": file_path,
        "insertions": insertions,
        "deletions": deletions,
        "status": "modified"
    }


def analyze_diff(
    commit_range: str = "",
    files: List[str] = None,
    unstaged: bool = False,
    staged: bool = False
) -> Dict[str, Any]:
    """分析 Git diff"""
    result = {
        "commit_range": commit_range or "HEAD",
        "files": [],
        "total_insertions": 0,
        "total_deletions": 0,
        "total_files_changed": 0
    }

    # 构建 git diff 命令
    if unstaged:
        diff_args = ["diff"]
    elif staged:
        diff_args = ["diff", "--cached"]
    elif commit_range:
        diff_args = ["diff", "--stat"] + commit_range.split("..")
    else:
        diff_args = ["diff", "HEAD~1", "HEAD", "--stat"]

    # 获取统计信息
    stat_result = run_git_command(diff_args)

    if stat_result.returncode == 0:
        stats = parse_diff_stats(stat_result.stdout)
        result["total_insertions"] = stats["total_insertions"]
        result["total_deletions"] = stats["total_deletions"]
        result["total_files_changed"] = stats["total_files_changed"]

    # 获取文件列表
    if files:
        for file_path in files:
            file_diff = get_file_diff(file_path, commit_range)
            if file_diff:
                result["files"].append(file_diff)
    else:
        # 获取所有变更的文件
        name_only_args = ["diff", "--name-only"]
        if commit_range:
            name_only_args.extend(commit_range.split(".."))
        elif staged:
            name_only_args = ["diff", "--cached", "--name-only"]
        elif unstaged:
            name_only_args = ["diff", "--name-only"]

        name_result = run_git_command(name_only_args)

        if name_result.returncode == 0:
            for file_path in name_result.stdout.strip().split('\n'):
                if file_path:
                    file_diff = get_file_diff(file_path, commit_range)
                    if file_diff:
                        result["files"].append(file_diff)

    return result


def format_text_output(result: Dict[str, Any], short_stat: bool = False) -> str:
    """格式化为文本输出"""
    lines = []

    lines.append(f"Commit Range: {result['commit_range']}")
    lines.append("")

    if short_stat:
        lines.append(f"{result['total_files_changed']} files changed, "
                    f"{result['total_insertions']} insertions(+), "
                    f"{result['total_deletions']} deletions(-)")
        return "\n".join(lines)

    lines.append(f"Total files changed: {result['total_files_changed']}")
    lines.append(f"Total insertions: {result['total_insertions']}")
    lines.append(f"Total deletions: {result['total_deletions']}")
    lines.append("")

    if result['files']:
        lines.append("Changed files:")
        for file_info in result['files']:
            lines.append(f"  {file_info['path']} (+{file_info['insertions']}/-{file_info['deletions']})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Git 差异分析工具 - 分析 Git 变更供 AI 判断文档更新需求",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--commit-range",
        help="分析的提交范围 (例如: HEAD~3..HEAD)"
    )
    parser.add_argument(
        "--files",
        help="仅分析指定文件 (逗号分隔)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)"
    )
    parser.add_argument(
        "--unstaged",
        action="store_true",
        help="分析工作区未暂存的变更"
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="分析已暂存但未提交的变更"
    )
    parser.add_argument(
        "--short-stat",
        action="store_true",
        help="仅显示简短统计"
    )

    args = parser.parse_args()

    # 解析文件列表
    file_list = None
    if args.files:
        file_list = [f.strip() for f in args.files.split(",")]

    # 分析 diff
    result = analyze_diff(
        commit_range=args.commit_range,
        files=file_list,
        unstaged=args.unstaged,
        staged=args.staged
    )

    # 输出结果
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result, short_stat=args.short_stat))


if __name__ == "__main__":
    main()
