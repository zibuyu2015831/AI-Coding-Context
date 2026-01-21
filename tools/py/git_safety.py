"""
Git 安全检查工具 - 检查 Git 操作的安全性

功能说明：
- 检查当前分支是否为保护分支
- 验证 Git 命令是否安全
- 建议符合规范的分支名
- 支持自定义保护分支配置

使用方法：
    python tools/py/git_safety.py [--mode MODE] [--command COMMAND] [--branch-name NAME]

参数说明：
    --mode MODE              检查模式（默认：check-branch）
                            可选值：
                              check-branch    检查当前分支是否安全
                              validate-command 验证Git命令是否安全
                              suggest-branch   建议分支名
    --command COMMAND        要验证的Git命令（仅在validate-command模式下使用）
    --branch-name NAME       要生成的分支名（仅在suggest-branch模式下使用）
    --protected-branches     自定义保护分支列表（逗号分隔）

输出格式：
    {
      "data": {
        "safe": 是否安全(bool),
        "current_branch": "当前分支名",
        "reason": "原因说明",
        "suggestion": "建议"
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }

使用示例：
    # 检查当前分支
    python tools/py/git_safety.py --mode check-branch
    
    # 验证Git命令
    python tools/py/git_safety.py --mode validate-command --command "git push --force"
    
    # 建议分支名
    python tools/py/git_safety.py --mode suggest-branch --branch-name "user points"

版本信息：
    版本：1.0.0
    更新日期：2025-12-11
    所属：018-Commit-Guided Documentation
"""

import json
import subprocess
import argparse
import time
import re

# 默认保护分支列表
DEFAULT_PROTECTED_BRANCHES = ['main', 'master', 'production', 'release', 'develop']

# 危险命令列表（RED ZONE）
DANGEROUS_COMMANDS = [
    r'git\s+reset\s+--hard',
    r'git\s+push\s+--force',
    r'git\s+push\s+-f\b',
    r'git\s+rebase',
    r'git\s+merge\b(?!.*--abort)',  # 允许 git merge --abort
    r'git\s+branch\s+-D',
    r'git\s+tag\s+-d',
    r'git\s+tag\s+--delete',
]

# 受限命令列表（YELLOW ZONE）
RESTRICTED_COMMANDS = [
    r'git\s+checkout\s+-b',
    r'git\s+commit',
    r'git\s+push\s+origin',
]


def get_current_branch():
    """获取当前分支名"""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None


def check_current_branch(protected_branches=None):
    """
    检查当前分支是否为保护分支
    
    Args:
        protected_branches: 自定义保护分支列表
        
    Returns:
        dict: 检查结果
    """
    if protected_branches is None:
        protected_branches = DEFAULT_PROTECTED_BRANCHES
    
    current_branch = get_current_branch()
    
    if current_branch is None:
        return {
            'safe': False,
            'current_branch': None,
            'reason': 'Not a git repository or git not found',
            'suggestion': 'Ensure you are in a git repository and git is installed'
        }
    
    # 检查是否为保护分支
    is_protected = current_branch in protected_branches
    
    # 检查是否匹配保护分支模式（如 release/*）
    for pattern in protected_branches:
        if '*' in pattern:
            regex_pattern = pattern.replace('*', '.*')
            if re.match(f'^{regex_pattern}$', current_branch):
                is_protected = True
                break
    
    if is_protected:
        return {
            'safe': False,
            'current_branch': current_branch,
            'reason': f'Current branch "{current_branch}" is a protected branch',
            'suggestion': f'Create a feature branch: git checkout -b feature/your-feature-name'
        }
    else:
        return {
            'safe': True,
            'current_branch': current_branch,
            'reason': f'Current branch "{current_branch}" is safe to work on',
            'suggestion': None
        }


def validate_git_command(command):
    """
    验证 Git 命令是否安全
    
    Args:
        command: Git 命令字符串
        
    Returns:
        dict: 验证结果
    """
    if not command:
        return {
            'safe': False,
            'command': command,
            'reason': 'No command provided',
            'suggestion': 'Provide a git command to validate'
        }
    
    # 检查危险命令
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return {
                'safe': False,
                'command': command,
                'reason': f'Command matches dangerous pattern: {pattern}',
                'suggestion': 'This command is in the RED ZONE and should never be executed by AI',
                'zone': 'RED'
            }
    
    # 检查受限命令
    for pattern in RESTRICTED_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return {
                'safe': False,
                'command': command,
                'reason': f'Command matches restricted pattern: {pattern}',
                'suggestion': 'This command requires explicit user authorization',
                'zone': 'YELLOW'
            }
    
    # 命令安全
    return {
        'safe': True,
        'command': command,
        'reason': 'Command is safe to execute',
        'suggestion': None,
        'zone': 'GREEN'
    }


def suggest_safe_branch_name(description):
    """
    根据描述建议符合规范的分支名
    
    Args:
        description: 分支描述（如 "user points"）
        
    Returns:
        dict: 建议结果
    """
    if not description:
        return {
            'safe': True,
            'original': description,
            'suggested': None,
            'reason': 'No description provided',
            'suggestion': 'Provide a description for branch name suggestion'
        }
    
    # 转换为小写
    name = description.lower()
    
    # 替换空格和特殊字符为连字符
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s_]+', '-', name)
    
    # 移除首尾连字符
    name = name.strip('-')
    
    # 根据描述推断分支类型
    if any(keyword in description.lower() for keyword in ['fix', 'bug', 'issue']):
        prefix = 'bugfix'
    elif any(keyword in description.lower() for keyword in ['refactor', 'cleanup', 'improve']):
        prefix = 'refactor'
    elif any(keyword in description.lower() for keyword in ['doc', 'documentation']):
        prefix = 'docs'
    else:
        prefix = 'feature'
    
    suggested_name = f'{prefix}/{name}'
    
    return {
        'safe': True,
        'original': description,
        'suggested': suggested_name,
        'reason': f'Generated branch name based on description',
        'suggestion': f'Use: git checkout -b {suggested_name}'
    }


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Git Safety Checker')
    parser.add_argument('--mode', default='check-branch',
                       choices=['check-branch', 'validate-command', 'suggest-branch'],
                       help='Check mode')
    parser.add_argument('--command', help='Git command to validate')
    parser.add_argument('--branch-name', help='Branch name description')
    parser.add_argument('--protected-branches', help='Custom protected branches (comma-separated)')
    args = parser.parse_args()
    
    # 解析自定义保护分支
    protected_branches = None
    if args.protected_branches:
        protected_branches = [b.strip() for b in args.protected_branches.split(',')]
    
    # 根据模式执行检查
    if args.mode == 'check-branch':
        result_data = check_current_branch(protected_branches)
    elif args.mode == 'validate-command':
        result_data = validate_git_command(args.command)
    elif args.mode == 'suggest-branch':
        result_data = suggest_safe_branch_name(args.branch_name)
    else:
        result_data = {'error': f'Unknown mode: {args.mode}'}
    
    elapsed_time = round(time.time() - start_time, 4)
    result = {
        'data': result_data,
        'metadata': {
            'elapsed_seconds': elapsed_time,
            'timeout_threshold': 10,
            'version': '1.0.0'
        }
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
