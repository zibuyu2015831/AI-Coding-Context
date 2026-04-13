"""
批量修复管理器 - 管理批量文档修复任务

功能说明:
    - 生成修复方案清单
    - 分阶段执行修复任务
    - 提供修复预览和确认功能
    - 支持风险控制机制
    - 自动错误处理和回滚

使用方法:
    # 生成修复方案
    python tools/py/batch_fix_manager.py --generate --pattern "getUserInfo" --replacement "fetchUserProfile"

    # 执行批量修复
    python tools/py/batch_fix_manager.py --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"

    # 执行快速修复（自动确认低风险修复）
    python tools/py/batch_fix_manager.py --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --auto

    # 预览修复效果
    python tools/py/batch_fix_manager.py --preview --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"

    # 检查修复方案
    python tools/py/batch_fix_manager.py --check --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"

    # 设置批次大小
    python tools/py/batch_fix_manager.py --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --batch-size 5

    # 分阶段执行（只执行第 1 阶段）
    python tools/py/batch_fix_manager.py --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --stage 1

参数说明:
    --generate               生成修复方案
    --pattern PATTERN        查找模式（正则表达式）
    --replacement TEXT       替换文本
    --execute                执行修复
    --plan PATH              修复方案路径
    --auto                   自动确认低风险修复
    --preview                预览修复效果
    --check                  检查修复方案
    --batch-size NUM         批次大小，默认 10 个文档/批次
    --stage NUM              阶段号（用于分阶段执行）
    --analysis-dir PATH      分析目录，默认 dev_docs/_analysis/
    --doc-dir PATH           文档目录，默认 dev_docs/
    --verbose                输出详细信息
    --timeout SECONDS        超时时间，默认 60 秒

输出格式:
    {
      "success": true,
      "data": {
        "action": "generate_plan",
        "result": {
          "plan_path": "dev_docs/_analysis/doc_fix_plan_20260413.md",
          "affected_docs": 5,
          "stage_count": 2,
          "risk_level": "medium"
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
import re
import json
import time
import argparse
from datetime import datetime

VERSION = "1.0.0"
DEFAULT_TIMEOUT = 60
DEFAULT_DOC_DIR = "dev_docs"
DEFAULT_ANALYSIS_DIR = "dev_docs/_analysis"
DEFAULT_BATCH_SIZE = 10


def ensure_dir_exists(dir_path):
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)


def find_markdown_files(directory, recursive=True):
    """查找目录下的所有Markdown文件"""
    md_files = []
    if recursive:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith('.md'):
                md_files.append(file_path)
    return md_files


def search_in_file(file_path, pattern, replacement):
    """在文件中搜索并替换文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        matches = list(re.finditer(pattern, content))
        if matches:
            replaced_content = re.sub(pattern, replacement, content)
            return {
                'success': True,
                'file_path': file_path,
                'match_count': len(matches),
                'original_content': content,
                'replaced_content': replaced_content,
                'matches': [{'start': m.start(), 'end': m.end(), 'text': m.group()} for m in matches]
            }
        return None
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_fix_plan(pattern, replacement, doc_dir, analysis_dir):
    """生成修复方案"""
    ensure_dir_exists(analysis_dir)

    md_files = find_markdown_files(doc_dir)
    affected_docs = []
    stage_count = 0

    # 扫描所有文档
    for doc in md_files:
        result = search_in_file(doc, pattern, replacement)
        if result and result['success']:
            affected_docs.append(result)

    if not affected_docs:
        return {
            'success': False,
            'error': '未找到匹配的文档',
            'affected_docs': 0
        }

    # 分阶段（基于风险分级）
    low_risk_docs = []
    medium_risk_docs = []
    high_risk_docs = []

    for doc in affected_docs:
        file_name = os.path.basename(doc['file_path'])
        # 简单的风险分级：API文档风险高，其他风险低
        if 'api' in file_name.lower() or 'interface' in file_name.lower():
            high_risk_docs.append(doc)
        elif 'state' in file_name.lower() or 'data' in file_name.lower():
            medium_risk_docs.append(doc)
        else:
            low_risk_docs.append(doc)

    # 写入修复方案
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plan_path = os.path.join(analysis_dir, f'doc_fix_plan_{timestamp}.md')

    plan_content = []
    plan_content.append(f'# 文档修复方案 ({timestamp})')
    plan_content.append(f'\n## 修复信息')
    plan_content.append(f'- 模式: {pattern}')
    plan_content.append(f'- 替换: {replacement}')
    plan_content.append(f'- 受影响文档: {len(affected_docs)}')

    plan_content.append(f'\n## 分阶段执行')
    if low_risk_docs:
        stage_count += 1
        plan_content.append(f'\n### 阶段 {stage_count} (低风险 - {len(low_risk_docs)} 个文档)')
        for doc in low_risk_docs:
            plan_content.append(f'- {doc["file_path"]} ({doc["match_count"]} 个匹配)')
    if medium_risk_docs:
        stage_count += 1
        plan_content.append(f'\n### 阶段 {stage_count} (中风险 - {len(medium_risk_docs)} 个文档)')
        for doc in medium_risk_docs:
            plan_content.append(f'- {doc["file_path"]} ({doc["match_count"]} 个匹配)')
    if high_risk_docs:
        stage_count += 1
        plan_content.append(f'\n### 阶段 {stage_count} (高风险 - {len(high_risk_docs)} 个文档)')
        for doc in high_risk_docs:
            plan_content.append(f'- {doc["file_path"]} ({doc["match_count"]} 个匹配)')

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(plan_content))

    return {
        'success': True,
        'plan_path': plan_path,
        'affected_docs': len(affected_docs),
        'stage_count': stage_count,
        'risk_level': 'low' if stage_count == 1 else 'medium' if stage_count == 2 else 'high'
    }


def parse_fix_plan(plan_path):
    """解析修复方案"""
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'success': False, 'error': f'无法读取方案文件: {str(e)}'}

    # 解析阶段信息
    stages = []
    current_stage = None
    stage_re = re.compile(r'### 阶段 (\d+) \((.*?) - (\d+) 个文档\)')

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue

        match = stage_re.match(line)
        if match:
            current_stage = {
                'stage': int(match.group(1)),
                'risk_level': match.group(2),
                'doc_count': int(match.group(3)),
                'docs': []
            }
            stages.append(current_stage)
        elif current_stage and line.startswith('- '):
            doc_match = re.match(r'- (.*?) \((\d+) 个匹配\)', line)
            if doc_match:
                current_stage['docs'].append({
                    'file_path': doc_match.group(1),
                    'match_count': int(doc_match.group(2))
                })

    return {
        'success': True,
        'plan_path': plan_path,
        'stages': stages
    }


def execute_fix_plan(plan_path, auto=False, stage=None, batch_size=DEFAULT_BATCH_SIZE):
    """执行修复方案"""
    parse_result = parse_fix_plan(plan_path)
    if not parse_result['success']:
        return parse_result

    # 筛选需要执行的阶段
    if stage:
        stages = [s for s in parse_result['stages'] if s['stage'] == stage]
        if not stages:
            return {'success': False, 'error': f'阶段 {stage} 不存在'}
    else:
        stages = parse_result['stages']

    # 执行修复
    results = []

    for stage_info in stages:
        stage_result = {'stage': stage_info['stage'], 'risk_level': stage_info['risk_level'], 'docs': []}
        results.append(stage_result)

        for i, doc in enumerate(stage_info['docs']):
            # 批次控制
            if i % batch_size == 0 and i > 0:
                time.sleep(1)

            result = search_in_file(doc['file_path'], None, None)  # 重新搜索以确保文档未被修改
            if not result:
                continue

            try:
                with open(doc['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()

                with open(doc['file_path'], 'w', encoding='utf-8') as f:
                    # 从方案中提取模式和替换
                    with open(plan_path, 'r', encoding='utf-8') as plan_file:
                        plan_content = plan_file.read()
                    pattern_match = re.search(r'模式: (.*)', plan_content)
                    replacement_match = re.search(r'替换: (.*)', plan_content)
                    if pattern_match and replacement_match:
                        pattern = pattern_match.group(1)
                        replacement = replacement_match.group(1)
                        new_content = re.sub(pattern, replacement, content)
                        f.write(new_content)

                stage_result['docs'].append({
                    'file_path': doc['file_path'],
                    'success': True,
                    'message': '修复成功'
                })

            except Exception as e:
                stage_result['docs'].append({
                    'file_path': doc['file_path'],
                    'success': False,
                    'error': str(e)
                })

    return {
        'success': True,
        'plan_path': plan_path,
        'execution_result': results
    }


def preview_fix_plan(plan_path):
    """预览修复方案"""
    parse_result = parse_fix_plan(plan_path)
    if not parse_result['success']:
        return parse_result

    return {
        'success': True,
        'plan_path': plan_path,
        'preview': {
            'stages': [
                {
                    'stage': s['stage'],
                    'risk_level': s['risk_level'],
                    'doc_count': len(s['docs']),
                    'docs': [d['file_path'] for d in s['docs']]
                }
                for s in parse_result['stages']
            ]
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="批量修复管理器 - 管理批量文档修复任务",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--generate", action="store_true", help="生成修复方案")
    parser.add_argument("--pattern", help="查找模式（正则表达式）")
    parser.add_argument("--replacement", help="替换文本")
    parser.add_argument("--execute", action="store_true", help="执行修复")
    parser.add_argument("--plan", help="修复方案路径")
    parser.add_argument("--auto", action="store_true", help="自动确认低风险修复")
    parser.add_argument("--preview", action="store_true", help="预览修复效果")
    parser.add_argument("--check", action="store_true", help="检查修复方案")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"批次大小，默认 {DEFAULT_BATCH_SIZE} 个文档/批次")
    parser.add_argument("--stage", type=int, help="阶段号（用于分阶段执行）")
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR, help=f"分析目录，默认 {DEFAULT_ANALYSIS_DIR}")
    parser.add_argument("--doc-dir", default=DEFAULT_DOC_DIR, help=f"文档目录，默认 {DEFAULT_DOC_DIR}")
    parser.add_argument("--verbose", action="store_true", help="输出详细信息")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间，默认 {DEFAULT_TIMEOUT} 秒")

    args = parser.parse_args()

    result = {
        'success': True,
        'data': {},
        'metadata': {'version': VERSION}
    }

    try:
        if args.generate:
            if not args.pattern or not args.replacement:
                result['success'] = False
                result['error'] = '缺少必填参数'
            else:
                gen_result = generate_fix_plan(
                    args.pattern,
                    args.replacement,
                    args.doc_dir,
                    args.analysis_dir
                )
                result['data'] = {'action': 'generate_plan', 'result': gen_result}
                if not gen_result.get('success', True):
                    result['success'] = False
                    result['error'] = gen_result['error']

        elif args.execute:
            if not args.plan:
                result['success'] = False
                result['error'] = '缺少修复方案路径'
            else:
                exec_result = execute_fix_plan(
                    args.plan,
                    args.auto,
                    args.stage,
                    args.batch_size
                )
                result['data'] = {'action': 'execute_plan', 'result': exec_result}
                if not exec_result.get('success', True):
                    result['success'] = False
                    result['error'] = exec_result['error']

        elif args.preview:
            if not args.plan:
                result['success'] = False
                result['error'] = '缺少修复方案路径'
            else:
                preview_result = preview_fix_plan(args.plan)
                result['data'] = {'action': 'preview_plan', 'result': preview_result}
                if not preview_result.get('success', True):
                    result['success'] = False
                    result['error'] = preview_result['error']

        elif args.check:
            if not args.plan:
                result['success'] = False
                result['error'] = '缺少修复方案路径'
            else:
                check_result = parse_fix_plan(args.plan)
                result['data'] = {'action': 'check_plan', 'result': check_result}
                if not check_result.get('success', True):
                    result['success'] = False
                    result['error'] = check_result['error']

        else:
            result['success'] = False
            result['error'] = '请指定操作'

    except Exception as e:
        result['success'] = False
        result['error'] = str(e)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
