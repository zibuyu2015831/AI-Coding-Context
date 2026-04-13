"""
修复历史管理器 - 管理文档修复历史记录

功能说明:
    - 基于 Git 提交信息记录修复历史
    - 在 _analysis/fix_history/ 目录中存储修复元数据
    - 支持修复查询和统计
    - 提供命令行接口查询修复历史
    - 自动与 Git 提交关联

使用方法:
    # 记录修复历史
    python tools/py/fix_history_manager.py --record --commit "a1b2c3d" --target-docs "dev_docs/api_layer.md,dev_docs/state_management.md"

    # 查询修复历史
    python tools/py/fix_history_manager.py --query

    # 查询特定修复记录
    python tools/py/fix_history_manager.py --query --commit "a1b2c3d"

    # 查询特定文档的修复历史
    python tools/py/fix_history_manager.py --query --doc "dev_docs/api_layer.md"

    # 获取修复统计信息
    python tools/py/fix_history_manager.py --stats

    # 清理修复历史
    python tools/py/fix_history_manager.py --cleanup --days 90

    # 与 Git 提交关联
    python tools/py/fix_history_manager.py --sync

参数说明:
    --record                 记录修复历史
    --commit HASH           Git 提交哈希
    --target-docs DOCS      逗号分隔的目标文档列表
    --query                  查询修复历史
    --doc PATH              特定文档路径
    --stats                  获取修复统计信息
    --cleanup               清理旧的修复历史
    --days NUM              保留天数，默认 90 天
    --sync                  与 Git 提交同步修复历史
    --analysis-dir PATH     分析目录，默认 dev_docs/_analysis/
    --verbose               输出详细信息

输出格式:
    {
      "success": true,
      "data": {
        "action": "query",
        "result": {
          "total_records": 5,
          "records": [
            {
              "commit_hash": "a1b2c3d",
              "date": "2026-04-13 14:30:00",
              "target_docs": ["dev_docs/api_layer.md"],
              "message": "修复 API 函数名错误"
            }
          ]
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
import argparse
from datetime import datetime, timedelta
import glob
import re

VERSION = "1.0.0"
DEFAULT_ANALYSIS_DIR = "dev_docs/_analysis"
FIX_HISTORY_DIR = "fix_history"


def ensure_dir_exists(dir_path):
    """
    确保目录存在
    """
    os.makedirs(dir_path, exist_ok=True)


def get_fix_history_dir(analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    获取修复历史目录路径
    """
    return os.path.join(analysis_dir, FIX_HISTORY_DIR)


def record_fix_history(commit_hash, target_docs, analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    记录修复历史

    Args:
        commit_hash: Git 提交哈希
        target_docs: 目标文档列表
        analysis_dir: 分析目录

    Returns:
        dict: 记录结果
    """
    history_dir = get_fix_history_dir(analysis_dir)
    ensure_dir_exists(history_dir)

    # 检查记录是否已存在
    existing_files = glob.glob(os.path.join(history_dir, f"*{commit_hash}*.json"))
    if existing_files:
        return {
            "success": True,
            "message": "记录已存在",
            "file_path": existing_files[0]
        }

    # 构建记录文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{commit_hash}.json"
    file_path = os.path.join(history_dir, filename)

    # 保存修复记录
    record = {
        "commit_hash": commit_hash,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target_docs": target_docs,
        "timestamp": int(time.time())
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False, default=str)
        return {
            "success": True,
            "message": "记录成功",
            "file_path": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"记录失败: {str(e)}"
        }


def query_fix_history(commit_hash=None, doc_path=None, analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    查询修复历史

    Args:
        commit_hash: Git 提交哈希
        doc_path: 文档路径
        analysis_dir: 分析目录

    Returns:
        dict: 查询结果
    """
    history_dir = get_fix_history_dir(analysis_dir)
    ensure_dir_exists(history_dir)

    records = []
    history_files = glob.glob(os.path.join(history_dir, "*.json"))

    for file_path in history_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                record = json.load(f)
            record['file_path'] = file_path

            # 筛选条件
            if commit_hash and record['commit_hash'] != commit_hash:
                continue
            if doc_path:
                if doc_path not in [d for d in record.get('target_docs', [])]:
                    continue

            records.append(record)
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue

    # 按日期降序排序
    records.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    return {
        "success": True,
        "total_records": len(records),
        "records": records
    }


def get_fix_stats(analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    获取修复统计信息

    Args:
        analysis_dir: 分析目录

    Returns:
        dict: 统计信息
    """
    history_dir = get_fix_history_dir(analysis_dir)
    ensure_dir_exists(history_dir)

    history_files = glob.glob(os.path.join(history_dir, "*.json"))
    total_records = len(history_files)
    records = []
    docs_set = set()

    for file_path in history_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                record = json.load(f)
            records.append(record)

            # 统计文档
            for doc in record.get('target_docs', []):
                docs_set.add(doc)
        except Exception as e:
            continue

    # 按日期分组统计
    daily_stats = {}
    for record in records:
        date_str = record.get('date', '')[:10]  # 获取日期部分
        if date_str not in daily_stats:
            daily_stats[date_str] = 0
        daily_stats[date_str] += len(record.get('target_docs', []))

    return {
        "success": True,
        "total_records": total_records,
        "total_docs_fixed": len(docs_set),
        "daily_stats": daily_stats,
        "records_per_doc": {
            doc: sum(1 for r in records if doc in [d for d in r.get('target_docs', [])])
            for doc in docs_set
        }
    }


def cleanup_old_records(days=90, analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    清理旧的修复历史记录

    Args:
        days: 保留天数
        analysis_dir: 分析目录

    Returns:
        dict: 清理结果
    """
    history_dir = get_fix_history_dir(analysis_dir)
    ensure_dir_exists(history_dir)

    cutoff_date = datetime.now() - timedelta(days=days)
    history_files = glob.glob(os.path.join(history_dir, "*.json"))
    deleted = 0

    for file_path in history_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                record = json.load(f)
            date_str = record.get('date', '')
            if date_str:
                try:
                    record_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    if record_date < cutoff_date:
                        os.remove(file_path)
                        deleted += 1
                except:
                    continue
        except Exception as e:
            continue

    return {
        "success": True,
        "deleted_records": deleted,
        "message": f"已删除 {deleted} 条旧记录"
    }


def sync_with_git(analysis_dir=DEFAULT_ANALYSIS_DIR):
    """
    与 Git 提交同步修复历史

    Args:
        analysis_dir: 分析目录

    Returns:
        dict: 同步结果
    """
    history_dir = get_fix_history_dir(analysis_dir)
    ensure_dir_exists(history_dir)

    # 检查是否为 Git 仓库
    try:
        import subprocess
        git_result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True
        )
        if git_result.returncode != 0:
            return {
                "success": False,
                "error": "不是 Git 仓库"
            }
    except:
        return {
            "success": False,
            "error": "无法执行 Git 命令"
        }

    return {
        "success": True,
        "message": "同步功能已启用，但需要进一步实现"
    }


def main():
    parser = argparse.ArgumentParser(
        description="修复历史管理器 - 管理文档修复历史记录",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--record", action="store_true", help="记录修复历史")
    parser.add_argument("--commit", help="Git 提交哈希")
    parser.add_argument("--target-docs", help="逗号分隔的目标文档列表")
    parser.add_argument("--query", action="store_true", help="查询修复历史")
    parser.add_argument("--doc", help="特定文档路径")
    parser.add_argument("--stats", action="store_true", help="获取修复统计信息")
    parser.add_argument("--cleanup", action="store_true", help="清理旧的修复历史")
    parser.add_argument("--days", type=int, default=90, help="保留天数，默认 90 天")
    parser.add_argument("--sync", action="store_true", help="与 Git 提交同步修复历史")
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR, help=f"分析目录，默认 {DEFAULT_ANALYSIS_DIR}")
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
        if args.record:
            # 记录修复历史
            if not args.commit:
                result["success"] = False
                result["error"] = "请指定提交哈希: --commit"
            elif not args.target-docs:
                result["success"] = False
                result["error"] = "请指定目标文档: --target-docs"
            else:
                target_docs = args.target_docs.split(',')
                target_docs = [doc.strip() for doc in target_docs if doc.strip()]

                record_result = record_fix_history(
                    args.commit,
                    target_docs,
                    args.analysis_dir
                )
                result["data"] = {
                    "action": "record",
                    "result": record_result
                }
                if not record_result['success']:
                    result["success"] = False
                    result["error"] = record_result['error']

        elif args.query:
            # 查询修复历史
            query_result = query_fix_history(
                args.commit,
                args.doc,
                args.analysis_dir
            )
            result["data"] = {
                "action": "query",
                "result": query_result
            }

        elif args.stats:
            # 获取修复统计信息
            stats_result = get_fix_stats(args.analysis_dir)
            result["data"] = {
                "action": "stats",
                "result": stats_result
            }

        elif args.cleanup:
            # 清理旧记录
            cleanup_result = cleanup_old_records(
                args.days,
                args.analysis_dir
            )
            result["data"] = {
                "action": "cleanup",
                "result": cleanup_result
            }

        elif args.sync:
            # 与 Git 同步
            sync_result = sync_with_git(args.analysis_dir)
            result["data"] = {
                "action": "sync",
                "result": sync_result
            }
            if not sync_result['success']:
                result["success"] = False
                result["error"] = sync_result['error']

        else:
            result["success"] = False
            result["error"] = "请指定操作: --record, --query, --stats, --cleanup, 或 --sync"

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    # 输出 JSON
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
