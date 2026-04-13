"""
Git 集成修复管理器 - 使用 Git 版本控制管理文档修复流程

功能说明:
    - 检查 Git 工作区状态
    - 创建修复分支进行隔离修复
    - 执行修复操作并自动提交
    - 支持修复历史记录和回滚
    - 提供安全机制防止数据丢失

使用方法:
    # 检查 Git 状态
    python tools/py/manage_fix_with_git.py --check-status

    # 开始修复流程（创建分支并切换）
    python tools/py/manage_fix_with_git.py --start --branch-name "doc-fix-001"

    # 提交修复
    python tools/py/manage_fix_with_git.py --commit --message "修复 API 函数名错误"

    # 查看修复历史
    python tools/py/manage_fix_with_git.py --history

    # 查看特定提交详细信息
    python tools/py/manage_fix_with_git.py --show-commit "a1b2c3d"

    # 回滚到修复前状态
    python tools/py/manage_fix_with_git.py --rollback --commit "a1b2c3d"

    # 完成修复（合并到主分支）
    python tools/py/manage_fix_with_git.py --finish

参数说明:
    --check-status          检查 Git 工作区状态
    --start                 开始修复流程（创建分支）
    --branch-name NAME      修复分支名称（默认: doc-fix-YYYYMMDD）
    --commit                提交修复
    --message MSG           提交信息
    --history               查看修复历史
    --show-commit HASH      查看特定提交详细信息
    --rollback              回滚到指定提交
    --commit HASH           目标提交哈希
    --finish                完成修复（合并到主分支）
    --main-branch NAME      主分支名称（默认: main）
    --doc-dir PATH          文档目录（默认: dev_docs/）
    --verbose               输出详细信息

输出格式:
    {
      "success": true,
      "data": {
        "action": "check_status",
        "result": {
          "is_clean": true,
          "current_branch": "main",
          "status": "clean"
        }
      },
      "metadata": {
        "version": "1.0.0"
      }
    }

版本信息:
    Version: 1.0.0
    Created: 2026-04-13
    Purpose: Support 011-Document Error Fix Workflow
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime

VERSION = "1.0.0"
DEFAULT_DOC_DIR = "dev_docs"
DEFAULT_MAIN_BRANCH = "main"


def run_git_command(cmd, cwd=None):
    """
    执行 Git 命令

    Args:
        cmd: Git 命令列表
        cwd: 工作目录

    Returns:
        dict: 包含 success, output, error 的结果
    """
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip(),
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }


def check_git_status(cwd=None):
    """
    检查 Git 工作区状态

    Args:
        cwd: 工作目录

    Returns:
        dict: Git 状态信息
    """
    # 检查是否为 Git 仓库
    result = run_git_command(['rev-parse', '--is-inside-work-tree'], cwd)
    if not result['success']:
        return {
            'is_git_repo': False,
            'is_clean': False,
            'current_branch': None,
            'status': 'not_a_git_repo',
            'error': result['error']
        }

    # 获取当前分支
    branch_result = run_git_command(['branch', '--show-current'], cwd)
    current_branch = branch_result['output'] if branch_result['success'] else None

    # 检查工作区状态
    status_result = run_git_command(['status', '--porcelain'], cwd)
    is_clean = len(status_result['output'].strip()) == 0

    return {
        'is_git_repo': True,
        'is_clean': is_clean,
        'current_branch': current_branch,
        'status': 'clean' if is_clean else 'dirty',
        'status_output': status_result['output']
    }


def create_fix_branch(branch_name=None, cwd=None):
    """
    创建修复分支

    Args:
        branch_name: 分支名称
        cwd: 工作目录

    Returns:
        dict: 分支创建结果
    """
    if not branch_name:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        branch_name = f'doc-fix-{timestamp}'

    # 检查当前分支
    status = check_git_status(cwd)
    if not status['is_git_repo']:
        return {'success': False, 'error': 'Not a Git repository'}

    # 创建并切换到新分支
    result = run_git_command(['checkout', '-b', branch_name], cwd)

    if result['success']:
        return {
            'success': True,
            'branch_name': branch_name,
            'message': f'Created and switched to branch: {branch_name}'
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


def commit_fix(message, cwd=None):
    """
    提交修复

    Args:
        message: 提交信息
        cwd: 工作目录

    Returns:
        dict: 提交结果
    """
    # 添加所有变更
    add_result = run_git_command(['add', '.'], cwd)
    if not add_result['success']:
        return {'success': False, 'error': f'Failed to add files: {add_result["error"]}'}

    # 提交
    commit_result = run_git_command(['commit', '-m', message], cwd)

    if commit_result['success']:
        # 获取提交哈希
        hash_result = run_git_command(['rev-parse', 'HEAD'], cwd)
        commit_hash = hash_result['output'] if hash_result['success'] else None

        return {
            'success': True,
            'commit_hash': commit_hash,
            'message': message,
            'output': commit_result['output']
        }
    else:
        return {
            'success': False,
            'error': commit_result['error']
        }


def get_fix_history(limit=20, cwd=None):
    """
    获取修复历史

    Args:
        limit: 历史记录数量限制
        cwd: 工作目录

    Returns:
        dict: 修复历史
    """
    # 获取提交历史（只包含文档提交）
    cmd = ['log', f'-{limit}', '--pretty=format:%H|%an|%ae|%at|%s', '--', '*.md']
    result = run_git_command(cmd, cwd)

    if not result['success']:
        return {'success': False, 'error': result['error']}

    history = []
    for line in result['output'].split('\n'):
        if not line.strip():
            continue
        parts = line.split('|', 4)
        if len(parts) == 5:
            commit_hash, author_name, author_email, timestamp, subject = parts
            try:
                dt = datetime.fromtimestamp(int(timestamp))
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = timestamp

            history.append({
                'commit_hash': commit_hash,
                'author_name': author_name,
                'author_email': author_email,
                'date': date_str,
                'timestamp': int(timestamp) if timestamp else None,
                'subject': subject
            })

    return {
        'success': True,
        'history': history,
        'total': len(history)
    }


def show_commit(commit_hash, cwd=None):
    """
    显示特定提交的详细信息

    Args:
        commit_hash: 提交哈希
        cwd: 工作目录

    Returns:
        dict: 提交详细信息
    """
    # 获取提交信息
    info_result = run_git_command(['show', '--stat', commit_hash], cwd)
    if not info_result['success']:
        return {'success': False, 'error': info_result['error']}

    # 获取提交差异
    diff_result = run_git_command(['show', '--no-patch', commit_hash], cwd)

    return {
        'success': True,
        'commit_hash': commit_hash,
        'info': info_result['output'],
        'summary': diff_result['output'] if diff_result['success'] else None
    }


def rollback_to_commit(commit_hash, cwd=None, create_branch=True):
    """
    回滚到指定提交

    Args:
        commit_hash: 目标提交哈希
        cwd: 工作目录
        create_branch: 是否创建回滚分支

    Returns:
        dict: 回滚结果
    """
    # 验证提交是否有效
    result = run_git_command(['cat-file', '-e', commit_hash], cwd)
    if not result['success']:
        return {'success': False, 'error': f'Invalid commit: {commit_hash}'}

    if create_branch:
        # 创建回滚分支
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rollback_branch = f'rollback-{timestamp}'
        branch_result = run_git_command(['checkout', '-b', rollback_branch], cwd)
        if not branch_result['success']:
            return {'success': False, 'error': f'Failed to create rollback branch: {branch_result["error"]}'}

    # 执行回滚
    reset_result = run_git_command(['reset', '--hard', commit_hash], cwd)

    if reset_result['success']:
        return {
            'success': True,
            'commit_hash': commit_hash,
            'rollback_branch': rollback_branch if create_branch else None,
            'message': f'Successfully rolled back to commit: {commit_hash}'
        }
    else:
        return {
            'success': False,
            'error': reset_result['error']
        }


def finish_fix(main_branch=DEFAULT_MAIN_BRANCH, cwd=None):
    """
    完成修复，合并到主分支

    Args:
        main_branch: 主分支名称
        cwd: 工作目录

    Returns:
        dict: 完成结果
    """
    status = check_git_status(cwd)
    if not status['is_git_repo']:
        return {'success': False, 'error': 'Not a Git repository'}

    current_branch = status['current_branch']
    if current_branch == main_branch:
        return {'success': False, 'error': f'Already on {main_branch} branch'}

    # 切换到主分支
    checkout_result = run_git_command(['checkout', main_branch], cwd)
    if not checkout_result['success']:
        return {'success': False, 'error': f'Failed to checkout {main_branch}: {checkout_result["error"]}'}

    # 合并修复分支
    merge_result = run_git_command(['merge', '--no-ff', current_branch], cwd)

    if merge_result['success']:
        return {
            'success': True,
            'message': f'Successfully merged {current_branch} into {main_branch}',
            'source_branch': current_branch,
            'target_branch': main_branch
        }
    else:
        # 如果合并失败，尝试回退
        run_git_command(['merge', '--abort'], cwd)
        run_git_command(['checkout', current_branch], cwd)
        return {
            'success': False,
            'error': f'Merge failed: {merge_result["error"]}'
        }


def main():
    parser = argparse.ArgumentParser(
        description="Git 集成修复管理器 - 使用 Git 版本控制管理文档修复流程",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check-status", action="store_true", help="检查 Git 工作区状态")
    parser.add_argument("--start", action="store_true", help="开始修复流程（创建分支）")
    parser.add_argument("--branch-name", help="修复分支名称（默认: doc-fix-YYYYMMDD）")
    parser.add_argument("--commit", action="store_true", help="提交修复")
    parser.add_argument("--message", help="提交信息")
    parser.add_argument("--history", action="store_true", help="查看修复历史")
    parser.add_argument("--show-commit", help="查看特定提交详细信息")
    parser.add_argument("--rollback", action="store_true", help="回滚到指定提交")
    parser.add_argument("--commit-hash", dest="target_commit", help="目标提交哈希")
    parser.add_argument("--finish", action="store_true", help="完成修复（合并到主分支）")
    parser.add_argument("--main-branch", default=DEFAULT_MAIN_BRANCH, help=f"主分支名称（默认: {DEFAULT_MAIN_BRANCH}）")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录（默认: {DEFAULT_DOC_DIR}）")
    parser.add_argument("--verbose", action="store_true", help="输出详细信息")

    args = parser.parse_args()

    result = {
        "success": True,
        "data": {},
        "metadata": {
            "version": VERSION
        }
    }

    try:
        # 确定工作目录
        cwd = os.getcwd()

        if args.check_status:
            # 检查 Git 状态
            status = check_git_status(cwd)
            result["data"] = {
                "action": "check_status",
                "result": status
            }

        elif args.start:
            # 开始修复流程
            branch_result = create_fix_branch(args.branch_name, cwd)
            result["data"] = {
                "action": "start_fix",
                "result": branch_result
            }
            if not branch_result['success']:
                result["success"] = False
                result["error"] = branch_result['error']

        elif args.commit:
            # 提交修复
            if not args.message:
                result["success"] = False
                result["error"] = "提交信息不能为空，请使用 --message 参数"
            else:
                commit_result = commit_fix(args.message, cwd)
                result["data"] = {
                    "action": "commit_fix",
                    "result": commit_result
                }
                if not commit_result['success']:
                    result["success"] = False
                    result["error"] = commit_result['error']

        elif args.history:
            # 查看修复历史
            history_result = get_fix_history(20, cwd)
            result["data"] = {
                "action": "get_history",
                "result": history_result
            }
            if not history_result['success']:
                result["success"] = False
                result["error"] = history_result['error']

        elif args.show_commit:
            # 显示提交详情
            show_result = show_commit(args.show_commit, cwd)
            result["data"] = {
                "action": "show_commit",
                "result": show_result
            }
            if not show_result['success']:
                result["success"] = False
                result["error"] = show_result['error']

        elif args.rollback:
            # 回滚
            if not args.target_commit:
                result["success"] = False
                result["error"] = "请指定目标提交哈希，使用 --commit-hash 参数"
            else:
                rollback_result = rollback_to_commit(args.target_commit, cwd)
                result["data"] = {
                    "action": "rollback",
                    "result": rollback_result
                }
                if not rollback_result['success']:
                    result["success"] = False
                    result["error"] = rollback_result['error']

        elif args.finish:
            # 完成修复
            finish_result = finish_fix(args.main_branch, cwd)
            result["data"] = {
                "action": "finish_fix",
                "result": finish_result
            }
            if not finish_result['success']:
                result["success"] = False
                result["error"] = finish_result['error']

        else:
            # 无操作
            result["success"] = False
            result["error"] = "请指定操作: --check-status, --start, --commit, --history, --show-commit, --rollback, 或 --finish"

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    # 输出 JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
