"""
Commit 质量评分工具 - 评估 commit 质量

功能说明：
- 5维度评分（WHAT/WHY/HOW/粒度/可测试性）
- 生成改进建议
- 识别优质 commit

使用方法：
    python tools/py/commit_quality_scorer.py [--message MESSAGE] [--hash HASH]

参数说明：
    --message MESSAGE        Commit message文本
    --hash HASH             Commit哈希（自动获取message）
    --threshold SCORE       及格分数线（默认：60）

输出格式：
    {
      "data": {
        "total_score": 总分(0-100),
        "breakdown": {
          "what_clarity": WHAT清晰度(0-30),
          "why_depth": WHY深度(0-30),
          "how_completeness": HOW完整性(0-20),
          "granularity": 粒度合理性(0-10),
          "testability": 可测试性(0-10)
        },
        "grade": "优秀/良好/及格/不及格",
        "suggestions": ["建议1", "建议2"],
        "is_quality": true/false
      }
    }

版本信息：
    版本：1.0.0
    更新日期：2025-12-11
"""

import json
import subprocess
import argparse
import time
import re
from typing import Dict, List


def score_what_clarity(what_text: str) -> tuple[int, List[str]]:
    """
    评分WHAT清晰度 (满分30)
    
    Args:
        what_text: WHAT字段文本
        
    Returns:
        (分数, 建议列表)
    """
    if not what_text or what_text == '(未提供)':
        return 0, ["缺少WHAT字段,无法理解做了什么"]
    
    score = 0
    suggestions = []
    
    # 长度合理性 (10分)
    length = len(what_text)
    if 10 <= length <= 100:
        score += 10
    elif length < 10:
        score += 3
        suggestions.append("WHAT过于简短,建议补充更多细节")
    else:
        score += 7
        suggestions.append("WHAT过长,建议精简为一句话")
    
    # 动词开头 (10分)
    action_verbs = ['新增', '修复', '优化', '重构', '删除', '更新', '实现', '添加', 
                   '移除', '调整', 'add', 'fix', 'update', 'remove', 'refactor', 
                   'implement', 'optimize', 'delete', 'adjust']
    if any(what_text.startswith(verb) for verb in action_verbs):
        score += 10
    else:
        score += 5
        suggestions.append("建议以动词开头,如'新增'、'修复'、'优化'等")
    
    # 具体性 (10分)
    if re.search(r'[A-Z][a-z]+|[\u4e00-\u9fa5]{2,}', what_text):
        score += 10
    else:
        score += 5
        suggestions.append("建议包含具体的模块名或功能名")
    
    return score, suggestions


def score_why_depth(why_text: str) -> tuple[int, List[str]]:
    """
    评分WHY深度 (满分30)
    
    Args:
        why_text: WHY字段文本
        
    Returns:
        (分数, 建议列表)
    """
    if not why_text or why_text == '(未提供)':
        return 0, ["缺少WHY字段,无法理解为什么要做这个变更"]
    
    score = 0
    suggestions = []
    
    # 长度 (10分)
    length = len(why_text)
    if length >= 20:
        score += 10
    elif length >= 10:
        score += 7
    else:
        score += 3
        suggestions.append("WHY过于简短,建议详细说明动机")
    
    # 业务价值 (10分)
    business_keywords = ['需求', '用户', '业务', '提升', '优化', '解决', '问题', 
                        'requirement', 'user', 'business', 'improve', 'solve']
    if any(kw in why_text for kw in business_keywords):
        score += 10
    else:
        score += 3
        suggestions.append("建议说明业务价值或用户价值")
    
    # 避免空洞理由 (10分)
    empty_reasons = ['需求要求', '老板说', '产品要求', '必须做']
    if any(reason in why_text for reason in empty_reasons):
        score += 2
        suggestions.append("避免使用'需求要求'等空洞理由,说明真实动机")
    else:
        score += 10
    
    return score, suggestions


def score_how_completeness(how_text: List[str]) -> tuple[int, List[str]]:
    """
    评分HOW完整性 (满分20)
    
    Args:
        how_text: HOW字段列表
        
    Returns:
        (分数, 建议列表)
    """
    if not how_text or how_text == ['(需分析diff)']:
        return 0, ["缺少HOW字段,无法理解实现方式"]
    
    score = 0
    suggestions = []
    
    # 条目数量 (10分)
    count = len(how_text)
    if 2 <= count <= 5:
        score += 10
    elif count == 1:
        score += 6
        suggestions.append("HOW只有一条,建议补充更多实现细节")
    elif count > 5:
        score += 7
        suggestions.append("HOW条目过多,建议精简关键点")
    
    # 具体性 (10分)
    has_technical_detail = False
    for item in how_text:
        if re.search(r'[A-Z][a-z]+|[\u4e00-\u9fa5]{3,}', item):
            has_technical_detail = True
            break
    
    if has_technical_detail:
        score += 10
    else:
        score += 5
        suggestions.append("HOW缺少技术细节,建议说明具体实现方式")
    
    return score, suggestions


def score_granularity(what_text: str, how_text: List[str]) -> tuple[int, List[str]]:
    """
    评分粒度合理性 (满分10)
    
    Args:
        what_text: WHAT字段
        how_text: HOW字段列表
        
    Returns:
        (分数, 建议列表)
    """
    score = 10  # 默认满分
    suggestions = []
    
    # 检查是否过大
    if how_text and len(how_text) > 8:
        score = 5
        suggestions.append("commit粒度过大,建议拆分为多个commit")
    
    # 检查是否过小
    if '修改空格' in what_text or '调整缩进' in what_text or 'typo' in what_text.lower():
        score = 7
        suggestions.append("commit粒度过小,建议合并到相关功能commit中")
    
    return score, suggestions


def score_testability(how_text: List[str]) -> tuple[int, List[str]]:
    """
    评分可测试性 (满分10)
    
    Args:
        how_text: HOW字段列表
        
    Returns:
        (分数, 建议列表)
    """
    score = 0
    suggestions = []
    
    if not how_text or how_text == ['(需分析diff)']:
        return 5, ["未说明如何验证,建议补充测试方法"]
    
    # 检查是否提到测试
    test_keywords = ['测试', '验证', '检查', 'test', 'verify', 'check', '单元测试', '集成测试']
    has_test_mention = any(any(kw in item for kw in test_keywords) for item in how_text)
    
    if has_test_mention:
        score = 10
    else:
        score = 5
        suggestions.append("建议说明如何测试或验证这个变更")
    
    return score, suggestions


def calculate_commit_score(commit_data: Dict) -> Dict:
    """
    计算commit总分
    
    Args:
        commit_data: commit数据（包含what/why/how字段）
        
    Returns:
        评分结果
    """
    what = commit_data.get('what', '')
    why = commit_data.get('why', '')
    how = commit_data.get('how', [])
    
    # 各维度评分
    what_score, what_suggestions = score_what_clarity(what)
    why_score, why_suggestions = score_why_depth(why)
    how_score, how_suggestions = score_how_completeness(how)
    granularity_score, granularity_suggestions = score_granularity(what, how)
    testability_score, testability_suggestions = score_testability(how)
    
    # 总分
    total = what_score + why_score + how_score + granularity_score + testability_score
    
    # 等级
    if total >= 80:
        grade = "优秀"
    elif total >= 60:
        grade = "良好"
    elif total >= 40:
        grade = "及格"
    else:
        grade = "不及格"
    
    # 合并建议
    all_suggestions = (what_suggestions + why_suggestions + how_suggestions + 
                      granularity_suggestions + testability_suggestions)
    
    return {
        'total_score': total,
        'breakdown': {
            'what_clarity': what_score,
            'why_depth': why_score,
            'how_completeness': how_score,
            'granularity': granularity_score,
            'testability': testability_score
        },
        'grade': grade,
        'suggestions': all_suggestions,
        'is_quality': total >= 80
    }


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Commit Quality Scorer')
    parser.add_argument('--message', help='Commit message text')
    parser.add_argument('--hash', help='Commit hash')
    parser.add_argument('--threshold', type=int, default=60, help='Pass threshold')
    args = parser.parse_args()
    
    # 获取commit message
    if args.hash:
        try:
            result = subprocess.run(
                ['git', 'show', '--no-patch', '--format=%s%n%b', args.hash],
                capture_output=True, text=True, encoding='utf-8', check=True
            )
            message = result.stdout.strip()
        except:
            message = None
    else:
        message = args.message
    
    if not message:
        result_data = {'error': 'No commit message provided'}
    else:
        # 解析commit (使用commit_parser的逻辑)
        from commit_parser import parse_commit_message
        commit_data = parse_commit_message(message)
        
        # 评分
        result_data = calculate_commit_score(commit_data)
        result_data['commit_data'] = commit_data
    
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
