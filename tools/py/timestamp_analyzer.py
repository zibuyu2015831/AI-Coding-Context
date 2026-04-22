"""
时间戳分析工具 - 采集文件时间戳供 AI 分析文档健康度

功能说明:
    递归采集指定目录下文件的时间戳信息，
    为 AI 分析文档健康度、判断文档是否过期提供数据支持。
    - 采集文件最后修改时间 (mtime)
    - 计算文件年龄和相对新鲜度
    - 识别最旧和最新的文件
    - 生成时间戳统计信息
    - 支持按文件类型过滤

使用方法:
    # 分析当前目录
    python tools/py/timestamp_analyzer.py

    # 分析指定目录
    python tools/py/timestamp_analyzer.py --path docs/

    # 仅分析 Markdown 文件
    python tools/py/timestamp_analyzer.py --ext .md

    # 限制扫描深度
    python tools/py/timestamp_analyzer.py --max-depth 3

    # 输出 JSON 格式
    python tools/py/timestamp_analyzer.py --format json

    # 设置过期阈值（天数）
    python tools/py/timestamp_analyzer.py --threshold-days 30

参数说明:
    --path PATH            要分析的目录路径 (默认: 当前目录)
    --ext EXTENSION        仅分析指定扩展名的文件 (例如: .md, .txt)
    --max-depth DEPTH      最大扫描深度 (默认: 无限制)
    --format FORMAT        输出格式: text, json (默认: text)
    --threshold-days DAYS  文档过期阈值天数 (默认: 90 天)
    --include-hidden       包含隐藏文件和目录
    --exclude PATTERN      排除匹配模式的文件 (可多次使用)

输出格式:
    text 格式包含:
    - 扫描统计 (总文件数、总大小)
    - 时间戳统计 (最早、最新、平均年龄)
    - 过期文档列表 (超过阈值天数)
    - 最新修改的文档 Top 10

    json 格式包含:
    {
      "scan_info": {
        "path": "/path/to/docs",
        "total_files": 50,
        "total_size_bytes": 1024000,
        "scan_time": "2026-01-20T10:00:00"
      },
      "timestamp_stats": {
        "oldest_file": {"path": "...", "mtime": "...", "age_days": 365},
        "newest_file": {"path": "...", "mtime": "...", "age_days": 0},
        "average_age_days": 90
      },
      "expired_docs": [...],
      "recently_modified": [...]
    }

使用示例:
    # 示例 1: 分析文档目录并检查过期文档
    python tools/py/timestamp_analyzer.py --path docs/ --threshold-days 60

    # 示例 2: 导出 JSON 供其他工具处理
    python tools/py/timestamp_analyzer.py --format json > timestamp_report.json

    # 示例 3: 仅分析最近修改的 Markdown 文件
    python tools/py/timestamp_analyzer.py --path docs/ --ext .md --max-depth 2

    # 示例 4: 排除特定目录
    python tools/py/timestamp_analyzer.py --exclude "*.tmp" --exclude "*.log"

与其他工具集成:
    # 结合 git_diff_analyzer 使用
    python tools/py/git_diff_analyzer.py --staged --format json > diff.json
    python tools/py/timestamp_analyzer.py --format json > timestamp.json
    # 综合分析哪些文档需要更新

版本信息:
    版本: 1.0.0
    更新日期: 2026-01-20
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

VERSION = "1.0.0"


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="时间戳分析工具 - 采集文件时间戳供 AI 分析文档健康度"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="要分析的目录路径 (默认: 当前目录)"
    )
    parser.add_argument(
        "--ext",
        help="仅分析指定扩展名的文件 (例如: .md, .txt)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        help="最大扫描深度"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)"
    )
    parser.add_argument(
        "--threshold-days",
        type=int,
        default=90,
        help="文档过期阈值天数 (默认: 90 天)"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="包含隐藏文件和目录"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="排除匹配模式的文件 (可多次使用)"
    )

    return parser.parse_args()


def should_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
    """检查文件是否应该被排除"""
    for pattern in exclude_patterns:
        if pattern in str(file_path):
            return True
    return False


def collect_files(
    base_path: Path,
    ext: Optional[str] = None,
    max_depth: Optional[int] = None,
    include_hidden: bool = False,
    exclude_patterns: List[str] = []
) -> List[Path]:
    """递归收集文件"""
    files = []
    current_depth = 0

    def walk_directory(path: Path, depth: int):
        if max_depth is not None and depth > max_depth:
            return

        try:
            for item in path.iterdir():
                # 跳过隐藏文件/目录
                if not include_hidden and item.name.startswith('.'):
                    continue

                # 检查排除模式
                if should_exclude(item, exclude_patterns):
                    continue

                if item.is_file():
                    # 检查扩展名
                    if ext is None or item.suffix == ext:
                        files.append(item)
                elif item.is_dir():
                    walk_directory(item, depth + 1)
        except PermissionError:
            pass  # 跳过无权限访问的目录

    walk_directory(base_path, 0)
    return files


def analyze_timestamps(files: List[Path]) -> Dict[str, Any]:
    """分析文件时间戳"""
    if not files:
        return {
            "total_files": 0,
            "total_size_bytes": 0,
            "oldest_file": None,
            "newest_file": None,
            "average_age_days": 0,
            "files_by_age": []
        }

    now = datetime.now()
    file_data = []
    total_size = 0

    for file_path in files:
        try:
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            age_days = (now - mtime).days

            file_data.append({
                "path": str(file_path),
                "mtime": mtime.isoformat(),
                "age_days": age_days,
                "size_bytes": stat.st_size
            })
            total_size += stat.st_size
        except (OSError, IOError):
            continue

    if not file_data:
        return {
            "total_files": 0,
            "total_size_bytes": 0,
            "oldest_file": None,
            "newest_file": None,
            "average_age_days": 0,
            "files_by_age": []
        }

    # 按年龄排序
    file_data.sort(key=lambda x: x["age_days"], reverse=True)

    oldest = file_data[0]
    newest = file_data[-1]
    average_age = sum(f["age_days"] for f in file_data) / len(file_data)

    return {
        "total_files": len(file_data),
        "total_size_bytes": total_size,
        "oldest_file": oldest,
        "newest_file": newest,
        "average_age_days": average_age,
        "files_by_age": file_data
    }


def identify_expired_docs(stats: Dict[str, Any], threshold_days: int) -> List[Dict[str, Any]]:
    """识别过期文档"""
    if not stats["files_by_age"]:
        return []

    return [f for f in stats["files_by_age"] if f["age_days"] > threshold_days]


def get_recently_modified(stats: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
    """获取最近修改的文件"""
    if not stats["files_by_age"]:
        return []

    # 按修改时间排序（最新的在前）
    sorted_files = sorted(stats["files_by_age"], key=lambda x: x["mtime"], reverse=True)
    return sorted_files[:top_n]


def format_text_output(
    stats: Dict[str, Any],
    expired_docs: List[Dict[str, Any]],
    recently_modified: List[Dict[str, Any]],
    threshold_days: int,
    scan_path: str
) -> str:
    """格式化为文本输出"""
    lines = []

    lines.append("=" * 60)
    lines.append("时间戳分析报告")
    lines.append("=" * 60)
    lines.append("")

    # 扫描信息
    lines.append(f"扫描路径: {scan_path}")
    lines.append(f"扫描时间: {datetime.now().isoformat()}")
    lines.append("")

    # 统计概览
    lines.append("-" * 60)
    lines.append("统计概览")
    lines.append("-" * 60)
    lines.append(f"总文件数: {stats['total_files']}")
    lines.append(f"总大小: {stats['total_size_bytes'] / 1024:.2f} KB")
    lines.append("")

    # 时间戳统计
    if stats['oldest_file']:
        lines.append("-" * 60)
        lines.append("时间戳统计")
        lines.append("-" * 60)
        lines.append(f"最旧文件: {stats['oldest_file']['path']}")
        lines.append(f"  修改时间: {stats['oldest_file']['mtime']}")
        lines.append(f"  年龄: {stats['oldest_file']['age_days']} 天")
        lines.append("")
        lines.append(f"最新文件: {stats['newest_file']['path']}")
        lines.append(f"  修改时间: {stats['newest_file']['mtime']}")
        lines.append(f"  年龄: {stats['newest_file']['age_days']} 天")
        lines.append("")
        lines.append(f"平均年龄: {stats['average_age_days']:.1f} 天")
        lines.append("")

    # 过期文档
    if expired_docs:
        lines.append("-" * 60)
        lines.append(f"⚠️ 过期文档 (超过 {threshold_days} 天未更新)")
        lines.append("-" * 60)
        for doc in expired_docs[:10]:  # 只显示前 10 个
            lines.append(f"  {doc['path']} ({doc['age_days']} 天)")
        if len(expired_docs) > 10:
            lines.append(f"  ... 还有 {len(expired_docs) - 10} 个文件")
        lines.append("")

    # 最近修改
    if recently_modified:
        lines.append("-" * 60)
        lines.append("📄 最近修改的文件 (Top 10)")
        lines.append("-" * 60)
        for file_info in recently_modified:
            mtime_str = file_info['mtime'][:10]  # 只显示日期部分
            lines.append(f"  {mtime_str} - {file_info['path']}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("报告生成完成")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    args = parse_args()

    # 收集文件
    base_path = Path(args.path).resolve()
    if not base_path.exists():
        print(f"❌ 错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)

    if not base_path.is_dir():
        print(f"❌ 错误: 路径不是目录: {args.path}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 正在扫描目录: {base_path}")

    files = collect_files(
        base_path,
        ext=args.ext,
        max_depth=args.max_depth,
        include_hidden=args.include_hidden,
        exclude_patterns=args.exclude
    )

    print(f"📁 找到 {len(files)} 个文件")

    # 分析时间戳
    print("📊 正在分析时间戳...")
    stats = analyze_timestamps(files)

    # 识别过期文档
    expired_docs = identify_expired_docs(stats, args.threshold_days)

    # 获取最近修改的文件
    recently_modified = get_recently_modified(stats, top_n=10)

    # 输出结果
    if args.format == "json":
        output = {
            "scan_info": {
                "path": str(base_path),
                "total_files": len(files),
                "scan_time": datetime.now().isoformat()
            },
            "stats": stats,
            "expired_docs": expired_docs,
            "recently_modified": recently_modified,
            "threshold_days": args.threshold_days
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        output = format_text_output(
            stats,
            expired_docs,
            recently_modified,
            args.threshold_days,
            str(base_path)
        )
        print(output)

    # 返回退出码
    if expired_docs:
        sys.exit(2)  # 有过期文档
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
