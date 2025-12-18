"""
Commit 模板 CLI 工具 - 交互式生成结构化 commit

功能说明：
- 交互式引导生成 commit
- 实时质量评分
- 快速模式支持

使用方法：
    python tools/py/commit_template_cli.py [--quick] [--type TYPE]

参数说明：
    --quick                 快速模式（跳过交互）
    --type TYPE            Commit类型
    --what WHAT            做什么
    --why WHY              为什么
    --how HOW              怎么做（逗号分隔）

版本信息：
    版本：1.0.0
    更新日期：2025-12-11
"""

import argparse
import sys


def interactive_mode():
    """交互式模式"""
    print("📝 Commit-as-Prompt 向导\\n")
    
    # 选择类型
    print("[1/4] 变更类型:")
    print("  1. 新功能 (feature)")
    print("  2. Bug修复 (fix)")
    print("  3. 架构调整 (architecture)")
    print("  4. 其他\\n")
    
    type_choice = input("选择: ").strip()
    type_map = {'1': 'feature', '2': 'fix', '3': 'architecture', '4': 'other'}
    commit_type = type_map.get(type_choice, 'feature')
    
    # WHAT
    print("\\n[2/4] WHAT - 做什么? (一句话描述)")
    what = input("> ").strip()
    
    # WHY
    print("\\n[3/4] WHY - 为什么做? (业务动机、需求编号)")
    why = input("> ").strip()
    
    # HOW
    print("\\n[4/4] HOW - 怎么做? (实现策略、风险点，每行一条，空行结束)")
    how_items = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        how_items.append(line)
    
    return commit_type, what, why, how_items


def generate_commit_message(commit_type, what, why, how_items):
    """生成commit message"""
    message = f"prompt({commit_type}): {what}\\n\\n"
    message += f"WHAT: {what}\\n"
    message += f"WHY: {why}\\n"
    message += "HOW:\\n"
    for item in how_items:
        message += f"- {item}\\n"
    
    return message


def main():
    parser = argparse.ArgumentParser(description='Commit Template CLI')
    parser.add_argument('--quick', action='store_true', help='Quick mode')
    parser.add_argument('--type', default='feature', help='Commit type')
    parser.add_argument('--what', help='What')
    parser.add_argument('--why', help='Why')
    parser.add_argument('--how', help='How (comma-separated)')
    args = parser.parse_args()
    
    if args.quick:
        # 快速模式
        commit_type = args.type
        what = args.what or "未指定"
        why = args.why or "未指定"
        how_items = args.how.split(',') if args.how else []
    else:
        # 交互模式
        commit_type, what, why, how_items = interactive_mode()
    
    # 生成commit
    message = generate_commit_message(commit_type, what, why, how_items)
    
    print("\\n✅ 生成的commit:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    # 质量评分
    try:
        from commit_quality_scorer import calculate_commit_score
        from commit_parser import parse_commit_message
        
        commit_data = parse_commit_message(message)
        score_result = calculate_commit_score(commit_data)
        
        print(f"\\n💯 质量评分: {score_result['total_score']}/100 {score_result['grade']}")
        print(f"  - WHAT清晰度: {score_result['breakdown']['what_clarity']}/30")
        print(f"  - WHY深度: {score_result['breakdown']['why_depth']}/30")
        print(f"  - HOW完整性: {score_result['breakdown']['how_completeness']}/20")
        
        if score_result['suggestions']:
            print("\\n建议:")
            for suggestion in score_result['suggestions'][:3]:
                print(f"  - {suggestion}")
    except:
        pass
    
    # 询问是否执行
    if not args.quick:
        confirm = input("\\n执行? (Y/n): ").strip().lower()
        if confirm in ['y', 'yes', '']:
            print("\\n提示: 请手动执行: git commit -m \"<message>\"")
        else:
            print("\\n已取消")


if __name__ == '__main__':
    main()
