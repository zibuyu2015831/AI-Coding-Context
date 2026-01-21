"""
Commit 解析工具 - 解析 Git commit 信息

功能说明：
- 解析结构化 commit (prompt:格式)
- 解析传统 commit (降级处理)
- 聚合多个 commit
- 分析合并 commit
- 提取 WHAT/WHY/HOW 字段

使用方法：
    python tools/py/commit_parser.py [--mode MODE] [--max-count N] [--since DATE]

参数说明：
    --mode MODE              解析模式（默认：parse）
                            可选值：
                              parse           解析最近的commits
                              aggregate       聚合commits
                              analyze-merge   分析合并commit
    --max-count N           最多解析N个commit（默认：100）
    --since DATE            解析指定日期之后的commit（如：7.days.ago）
    --branch BRANCH         指定分支（默认：当前分支）
    --format FORMAT         输出格式（json/summary，默认：json）

输出格式：
    {
      "data": {
        "commits": [
          {
            "hash": "commit哈希",
            "type": "commit类型",
            "what": "做什么",
            "why": "为什么",
            "how": ["怎么做"],
            "is_structured": true/false,
            "author": "作者",
            "date": "日期"
          }
        ],
        "total": 总数,
        "structured_count": 结构化commit数量,
        "traditional_count": 传统commit数量
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "version": "1.0.0"
      }
    }

使用示例：
    # 解析最近100个commit
    python tools/py/commit_parser.py --mode parse --max-count 100
    
    # 解析最近7天的commit
    python tools/py/commit_parser.py --mode parse --since "7 days ago"
    
    # 聚合commits
    python tools/py/commit_parser.py --mode aggregate --max-count 50

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
from datetime import datetime
from typing import List, Dict, Optional, Tuple


# 结构化commit正则表达式
SUBJECT_PATTERN = r'^(prompt|ai|doc)\(([^)]+)\):\s*(.+)$'

# Conventional Commits 兼容模式
CONVENTIONAL_PATTERN = r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)\(([^)]*)\):\s*(.+)$'


def parse_prompt_commit(message: str) -> Optional[Dict]:
    """
    解析结构化 commit (prompt:格式)
    
    Args:
        message: commit message
        
    Returns:
        解析结果字典，如果不是结构化commit则返回None
    """
    lines = message.split('\n')
    
    # 解析主题行
    subject_match = re.match(SUBJECT_PATTERN, lines[0])
    if not subject_match:
        return None
    
    prefix, type_, what_short = subject_match.groups()
    
    # 初始化结果
    result = {
        'prefix': prefix,
        'type': type_,
        'what': what_short.strip(),
        'why': None,
        'how': [],
        'is_structured': True
    }
    
    # 解析 body
    if len(lines) > 1:
        body = '\n'.join(lines[1:]).strip()
        
        # 提取 WHAT
        what_match = re.search(r'WHAT:\s*(.+?)(?=\nWHY:|\nHOW:|$)', body, re.DOTALL)
        if what_match:
            result['what'] = what_match.group(1).strip()
        
        # 提取 WHY
        why_match = re.search(r'WHY:\s*(.+?)(?=\nHOW:|$)', body, re.DOTALL)
        if why_match:
            result['why'] = why_match.group(1).strip()
        
        # 提取 HOW
        how_match = re.search(r'HOW:\s*\n((?:[-*]\s*.+\n?)+)', body, re.MULTILINE)
        if how_match:
            how_text = how_match.group(1)
            result['how'] = [line.strip()[2:].strip() for line in how_text.split('\n') 
                           if line.strip() and line.strip().startswith(('-', '*'))]
    
    return result


def parse_conventional_commit(message: str) -> Optional[Dict]:
    """
    解析 Conventional Commits 格式
    
    Args:
        message: commit message
        
    Returns:
        解析结果字典，如果不匹配则返回None
    """
    lines = message.split('\n')
    
    match = re.match(CONVENTIONAL_PATTERN, lines[0])
    if not match:
        return None
    
    type_, scope, description = match.groups()
    
    body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
    
    return {
        'prefix': 'conventional',
        'type': type_,
        'what': description.strip(),
        'why': body if body else '(未提供)',
        'how': ['(需分析diff)'],
        'is_structured': False,
        'is_conventional': True
    }


def parse_traditional_commit(message: str) -> Dict:
    """
    解析传统 commit (降级处理)
    
    Args:
        message: commit message
        
    Returns:
        解析结果字典
    """
    lines = message.split('\n')
    subject = lines[0].strip()
    body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
    
    return {
        'prefix': 'traditional',
        'type': 'unknown',
        'what': subject,
        'why': body if body else '(未提供)',
        'how': ['(需分析diff)'],
        'is_structured': False,
        'is_conventional': False
    }


def parse_commit_message(message: str) -> Dict:
    """
    智能解析 commit message
    
    优先级: prompt: > conventional > traditional
    
    Args:
        message: commit message
        
    Returns:
        解析结果字典
    """
    # 尝试解析结构化commit
    result = parse_prompt_commit(message)
    if result:
        return result
    
    # 尝试解析 Conventional Commits
    result = parse_conventional_commit(message)
    if result:
        return result
    
    # 降级到传统commit
    return parse_traditional_commit(message)


def get_commits(max_count: int = 100, since: Optional[str] = None, 
                branch: Optional[str] = None) -> List[Dict]:
    """
    获取 Git commits
    
    Args:
        max_count: 最多获取的commit数量
        since: 起始日期
        branch: 分支名
        
    Returns:
        commit列表
    """
    try:
        # 构建git log命令
        cmd = ['git', 'log', f'--max-count={max_count}', 
               '--pretty=format:%H|%an|%ae|%ad|%s|%b', '--date=iso']
        
        if since:
            cmd.append(f'--since={since}')
        
        if branch:
            cmd.append(branch)
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        
        commits = []
        current_commit = []
        
        for line in result.stdout.split('\n'):
            if not line:
                continue
            
            # 检查是否是新的commit（以哈希开头）
            if '|' in line and len(line.split('|')) >= 5:
                # 处理上一个commit
                if current_commit:
                    commits.append(parse_commit_data('\n'.join(current_commit)))
                current_commit = [line]
            else:
                # 多行消息的一部分
                if current_commit:
                    current_commit.append(line)
        
        # 处理最后一个commit
        if current_commit:
            commits.append(parse_commit_data('\n'.join(current_commit)))
        
        return commits
        
    except subprocess.CalledProcessError as e:
        return []
    except FileNotFoundError:
        return []


def parse_commit_data(commit_text: str) -> Dict:
    """
    解析单个commit的完整数据
    
    Args:
        commit_text: commit文本
        
    Returns:
        commit数据字典
    """
    lines = commit_text.split('\n')
    first_line = lines[0]
    
    parts = first_line.split('|', 5)
    if len(parts) < 5:
        return {}
    
    hash_val, author, email, date, subject = parts[:5]
    body = parts[5] if len(parts) > 5 else ''
    
    # 重组完整消息
    full_message = subject
    if body:
        full_message += '\n' + body
    
    # 添加多行消息
    if len(lines) > 1:
        full_message += '\n' + '\n'.join(lines[1:])
    
    # 解析消息
    parsed = parse_commit_message(full_message)
    
    # 添加元数据
    parsed.update({
        'hash': hash_val,
        'author': author,
        'email': email,
        'date': date
    })
    
    return parsed


def aggregate_commits(commits: List[Dict]) -> Dict:
    """
    聚合多个commits
    
    Args:
        commits: commit列表
        
    Returns:
        聚合结果
    """
    if not commits:
        return {
            'summary': 'No commits to aggregate',
            'total': 0,
            'structured': [],
            'traditional': []
        }
    
    structured = [c for c in commits if c.get('is_structured')]
    traditional = [c for c in commits if not c.get('is_structured')]
    
    # 按类型分组
    by_type = {}
    for commit in structured:
        type_ = commit.get('type', 'unknown')
        if type_ not in by_type:
            by_type[type_] = []
        by_type[type_].append(commit)
    
    return {
        'summary': f'Aggregated {len(commits)} commits',
        'total': len(commits),
        'structured_count': len(structured),
        'traditional_count': len(traditional),
        'by_type': {k: len(v) for k, v in by_type.items()},
        'structured': structured,
        'traditional': traditional
    }


def analyze_merge_commits(source_branch: str, target_branch: str) -> Dict:
    """
    分析合并commits
    
    Args:
        source_branch: 源分支
        target_branch: 目标分支
        
    Returns:
        分析结果
    """
    try:
        # 获取两个分支之间的差异commits
        cmd = ['git', 'log', f'{target_branch}..{source_branch}', 
               '--pretty=format:%H|%s', '--no-merges']
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        
        if not result.stdout:
            return {
                'source': source_branch,
                'target': target_branch,
                'commits': [],
                'count': 0,
                'message': 'No commits to merge'
            }
        
        commits = []
        for line in result.stdout.split('\n'):
            if line:
                hash_val, subject = line.split('|', 1)
                commits.append({
                    'hash': hash_val,
                    'subject': subject
                })
        
        return {
            'source': source_branch,
            'target': target_branch,
            'commits': commits,
            'count': len(commits),
            'message': f'Found {len(commits)} commits to merge'
        }
        
    except subprocess.CalledProcessError:
        return {
            'error': f'Failed to analyze merge from {source_branch} to {target_branch}'
        }


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Commit Parser')
    parser.add_argument('--mode', default='parse',
                       choices=['parse', 'aggregate', 'analyze-merge'],
                       help='Parse mode')
    parser.add_argument('--max-count', type=int, default=100,
                       help='Maximum number of commits to parse')
    parser.add_argument('--since', help='Parse commits since date')
    parser.add_argument('--branch', help='Branch to parse')
    parser.add_argument('--source-branch', help='Source branch for merge analysis')
    parser.add_argument('--target-branch', help='Target branch for merge analysis')
    parser.add_argument('--format', default='json', choices=['json', 'summary'],
                       help='Output format')
    args = parser.parse_args()
    
    # 根据模式执行
    if args.mode == 'parse':
        commits = get_commits(args.max_count, args.since, args.branch)
        structured_count = sum(1 for c in commits if c.get('is_structured'))
        traditional_count = len(commits) - structured_count
        
        result_data = {
            'commits': commits,
            'total': len(commits),
            'structured_count': structured_count,
            'traditional_count': traditional_count
        }
        
    elif args.mode == 'aggregate':
        commits = get_commits(args.max_count, args.since, args.branch)
        result_data = aggregate_commits(commits)
        
    elif args.mode == 'analyze-merge':
        if not args.source_branch or not args.target_branch:
            result_data = {'error': 'Source and target branches required for merge analysis'}
        else:
            result_data = analyze_merge_commits(args.source_branch, args.target_branch)
    else:
        result_data = {'error': f'Unknown mode: {args.mode}'}
    
    elapsed_time = round(time.time() - start_time, 4)
    
    if args.format == 'summary':
        # 简化输出
        print(f"Total commits: {result_data.get('total', 0)}")
        print(f"Structured: {result_data.get('structured_count', 0)}")
        print(f"Traditional: {result_data.get('traditional_count', 0)}")
    else:
        # JSON输出
        result = {
            'data': result_data,
            'metadata': {
                'elapsed_seconds': elapsed_time,
                'version': '1.0.0'
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
