"""
Commit 聚合工具 - 批量聚合和Token优化

功能说明：
- 同类 commit 聚合
- Token 优化
- 智能过滤

使用方法：
    python tools/py/commit_aggregator.py [--max-count N] [--since DATE]

参数说明：
    --max-count N           最多聚合N个commit（默认：50）
    --since DATE            聚合指定日期之后的commit
    --optimize-token        启用Token优化

版本信息：
    版本：1.0.0
    更新日期：2025-12-11
"""

import json
import argparse
import time
from typing import List, Dict


def aggregate_by_type(commits: List[Dict]) -> Dict:
    """按类型聚合commits"""
    by_type = {}
    
    for commit in commits:
        commit_type = commit.get('type', 'unknown')
        if commit_type not in by_type:
            by_type[commit_type] = []
        by_type[commit_type].append(commit)
    
    return by_type


def optimize_tokens(commits: List[Dict]) -> Dict:
    """优化Token消耗"""
    # 统计原始Token
    original_tokens = sum(
        len(c.get('what', '')) + len(c.get('why', '')) + 
        sum(len(h) for h in c.get('how', []))
        for c in commits
    )
    
    # 聚合同类型
    by_type = aggregate_by_type(commits)
    
    # 生成摘要
    summaries = []
    for commit_type, type_commits in by_type.items():
        summary = {
            'type': commit_type,
            'count': len(type_commits),
            'changes': [c.get('what', '') for c in type_commits[:5]]  # 只保留前5个
        }
        summaries.append(summary)
    
    # 统计优化后Token
    optimized_tokens = sum(
        len(s['type']) + sum(len(c) for c in s['changes'])
        for s in summaries
    )
    
    reduction = ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0
    
    return {
        'summaries': summaries,
        'original_tokens': original_tokens,
        'optimized_tokens': optimized_tokens,
        'reduction_percent': round(reduction, 2)
    }


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Commit Aggregator')
    parser.add_argument('--max-count', type=int, default=50)
    parser.add_argument('--since', help='Since date')
    parser.add_argument('--optimize-token', action='store_true')
    args = parser.parse_args()
    
    # 获取commits
    from commit_parser import get_commits
    commits = get_commits(args.max_count, args.since)
    
    if args.optimize_token:
        result_data = optimize_tokens(commits)
    else:
        result_data = aggregate_by_type(commits)
    
    elapsed_time = round(time.time() - start_time, 4)
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
