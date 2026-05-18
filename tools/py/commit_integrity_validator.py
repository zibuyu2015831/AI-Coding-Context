"""
Commit 诚信验证工具 - 对比 Commit Message 与物理代码变更的一致性

功能说明：
- 解析擬提交的 Commit Message (WHAT/WHY/HOW 结构)
- 获取当前 Git 暂存区 (staged) 或未暂存 (unstaged) 的文件变更
- 对比 HOW 字段中提到的文件与实际变更文件是否匹配
- 识别遗漏的文件或未在 HOW 中说明的变更文件
- 输出诚信分 (Integrity Score) 和改进建议

使用方法：
    python tools/py/commit_integrity_validator.py --message "COMMIT_MESSAGE" [--staged]

参数说明：
    --message TEXT      要验证的 Commit Message（必需）
    --staged            检查已暂存(staged)的变更（默认）
    --unstaged          检查未暂存(unstaged)的变更
    --format FORMAT     输出格式：text, json（默认：text）

输出格式：
    text 格式：
    - Commit 诚信审计报告
    - 得分：[分数] [状态]
    - 匹配文件数：N
    - 建议列表（如有）

    json 格式：
    {
      "score": 85,
      "status": "EXCELLENT",
      "matched_count": 3,
      "under_reported": [...],
      "over_reported": [...],
      "suggestions": [...]
    }

版本信息：
    版本：1.0.0
    更新日期：2026-04-07
"""

import re
import json
import subprocess
import argparse
from typing import List, Dict, Set

def parse_how_files(message: str) -> Set[str]:
    """
    从 Commit Message 的 HOW 字段中提取提到的文件路径 (生产级解析器 v3)
    
    解析逻辑:
    1. 提取 HOW: 之后的所有文本
    2. 忽略括号 (...) 中的内容，防止误将描述文字识别为路径
    3. 使用更精准的正则匹配完整路径
    """
    how_section = ""
    # 查找 HOW: 之后的所有内容, 直到下一个大写关键字 (如 WHY, WHAT) 或结束
    how_match = re.search(r'HOW:\s*(.*?)(?=\s*[A-Z]{3,}:|$)', message, re.DOTALL)
    if how_match:
        how_section = how_match.group(1)
    
    # 核心优化：移除所有括号及其内容，防止误读描述 (如 "Node.js", "AI")
    clean_how = re.sub(r'\(.*?\)', '', how_section)
    
    # 路径匹配正则: 匹配包含斜杠的文件名, 或者带常见扩展名的文件名
    # 使用 \b 单词边界防止匹配到类似 v1.4 的版本号
    patterns = [
        r'\b[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]{1,10}\b', # 标准路径或带扩展名文件
        r'(?<![a-zA-Z0-9_\-/])\.[a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)?\b'  # 隐藏文件如 .gitignore
    ]
    
    found_paths = set()
    for pattern in patterns:
        matches = re.findall(pattern, clean_how)
        for m in matches:
            # 清理标点
            p = m.strip(' "\'').rstrip('.,:;')
            # 统一处理 ./ 前缀
            if p.startswith('./'):
                p = p[2:]
            if p:
                found_paths.add(p)
    
    return found_paths

def get_git_diff_files(staged: bool = True) -> Set[str]:
    """获取 Git 变更的文件列表 (包含超时保护)"""
    cmd = ["git", "diff", "--name-only"]
    if staged:
        cmd.append("--staged")
    
    try:
        # 增加 5 秒超时保护, 防止在巨型仓库中挂死
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return set()

def calculate_integrity(msg_files: Set[str], actual_files: Set[str]) -> Dict:
    """计算诚信分并生成报告"""
    # 1. 匹配到的文件
    matched = msg_files.intersection(actual_files)
    
    # 2. Commit 提到了但实际没改的文件 (虚报)
    over_reported = msg_files - actual_files
    
    # 3. 实际改了但 Commit 没提的文件 (漏报)
    under_reported = actual_files - msg_files
    
    # 计算分数 (基础分 100)
    score = 100
    
    # 惩罚项
    under_reported_penalty = len(under_reported) * 15 # 漏报严重，扣分多
    over_reported_penalty = len(over_reported) * 5    # 虚报较轻，可能只是路径写错
    
    score -= (under_reported_penalty + over_reported_penalty)
    score = max(0, score) # 不低于0分
    
    # 生成建议
    suggestions = []
    if under_reported:
        suggestions.append(f"⚠️ 以下文件已修改但未在 HOW 中说明: {', '.join(under_reported)}")
    if over_reported:
        suggestions.append(f"ℹ️ HOW 中提到的以下文件似乎未发生变更: {', '.join(over_reported)}")
    
    if score >= 90:
        status = "EXCELLENT"
    elif score >= 80:
        status = "GOOD"
    else:
        status = "NEEDS_IMPROVEMENT"
        
    return {
        "score": score,
        "status": status,
        "matched_count": len(matched),
        "under_reported": list(under_reported),
        "over_reported": list(over_reported),
        "suggestions": suggestions
    }

def main():
    parser = argparse.ArgumentParser(description='Commit Integrity Validator')
    parser.add_argument('--message', required=True, help='Commit message to validate')
    parser.add_argument('--staged', action='store_true', default=True, help='Check staged changes (default)')
    parser.add_argument('--unstaged', action='store_false', dest='staged', help='Check unstaged changes')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    actual_files = get_git_diff_files(args.staged)
    msg_files = parse_how_files(args.message)
    
    report = calculate_integrity(msg_files, actual_files)
    
    if args.format == 'json':
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"--- Commit 诚信审计报告 ---")
        print(f"得分: {report['score']} [{report['status']}]")
        print(f"匹配文件数: {report['matched_count']}")
        
        if report['suggestions']:
            print("\n建议:")
            for s in report['suggestions']:
                print(f"  {s}")
        else:
            print("\n✅ 意图与物理变更完美匹配！")

if __name__ == "__main__":
    main()
