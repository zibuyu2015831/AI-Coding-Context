"""
报告生成工具 - 用于将复杂度数据转换为 Markdown 和 HTML 报告
作为 005 优化点的核心实施工具

功能说明：
- 读取 complexity_scanner.py 输出的 JSON 数据
- 生成 Markdown 格式报告
- 基于模板生成 HTML 仪表盘
- 支持自定义模板
- 集成 Mermaid 图表

使用方法：
    python tools/py/report_generator.py [--data DATA] [--output OUTPUT] [--format FORMAT] [--template TEMPLATE]

参数说明：
    --data DATA              输入数据文件路径（JSON 格式）
    --output OUTPUT          输出文件路径
    --format FORMAT          输出格式（markdown/html，默认：markdown）
    --template TEMPLATE      HTML 模板文件路径（仅 HTML 格式需要）
    --date DATE              报告日期（默认：当前日期）

输出格式（Markdown）：
    # 项目复杂度报告
    ## 摘要
    ## 代码规模
    ## 依赖关系
    ## 代码质量
    ## 架构健康度
    ## 风险分析
    ## 行动建议

输出格式（HTML）：
    基于 dev_docs/complexity/dashboard/template.html 渲染的完整 HTML 页面

使用示例：
    # 生成 Markdown 报告
    python tools/py/report_generator.py --data data.json --output report.md --format markdown

    # 生成 HTML 仪表盘
    python tools/py/report_generator.py --data data.json --output dashboard.html --format html --template template.html

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
"""

import json
import time
import argparse
import os
from datetime import datetime


def load_data(data_path):
    """加载复杂度数据"""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def generate_markdown_report(data, report_date=None, include_review=True):
    """生成 Markdown 报告"""
    if report_date is None:
        report_date = datetime.now().strftime('%Y-%m-%d')

    complexity_data = data.get('data', {})
    code_size = complexity_data.get('code_size', {})
    dependencies = complexity_data.get('dependencies', {})
    code_quality = complexity_data.get('code_quality', {})
    architecture = complexity_data.get('architecture', {})
    risk_assessment = complexity_data.get('risk_assessment', {})
    review_data = complexity_data.get('review_data', {})

    # 风险等级颜色映射
    def risk_color(level):
        if level == 'high':
            return '🔴'
        elif level == 'medium':
            return '🟡'
        else:
            return '🟢'

    report = f"""# 📊 项目复杂度报告

**生成日期**: {report_date}
**工具版本**: {data.get('metadata', {}).get('version', '1.0.0')}
**扫描耗时**: {data.get('metadata', {}).get('elapsed_seconds', 0)}s

---

## 🎯 摘要

| 指标 | 当前值 | 状态 |
|------|---------|------|
| 整体风险评分 | {risk_assessment.get('overall_score', 0):.0f}/100 | {risk_color('low' if risk_assessment.get('overall_score', 0) > 70 else 'medium' if risk_assessment.get('overall_score', 0) > 50 else 'high')} |
| 代码质量评分 | {code_quality.get('quality_score', 0)}/100 | {risk_color('low' if code_quality.get('quality_score', 0) > 70 else 'medium' if code_quality.get('quality_score', 0) > 50 else 'high')} |
| 新增代码 | {code_size.get('new_lines', 0)} 行 | {risk_color('low' if code_size.get('new_lines', 0) < 200 else 'medium' if code_size.get('new_lines', 0) < 500 else 'high')} |

---

## 📈 代码规模

| 指标 | 数值 |
|------|------|
| 新增代码行数 | {code_size.get('new_lines', 0)} |
| 总代码量 | {code_size.get('total_lines', 0)} |
| 变更文件数 | {code_size.get('files', 0)} |
| 增长百分比 | {code_size.get('growth_percentage', 0):.1f}% |

```mermaid
graph TD
    A[代码规模] --> B[新增: {code_size.get('new_lines', 0)}行]
    A --> C[总数: {code_size.get('total_lines', 0)}行]
    A --> D[文件: {code_size.get('files', 0)}个]
    A --> E[增长: {code_size.get('growth_percentage', 0):.1f}%]
```

---

## 🔗 依赖关系

| 指标 | 数值 |
|------|------|
| 新增依赖 | {dependencies.get('new', 0)} |
| 重复依赖 | {dependencies.get('duplicate', 0)} |
| 依赖深度 | {dependencies.get('depth', 0)} |

---

## 📋 代码质量

| 指标 | 数值 | 建议 |
|------|------|------|
| TODO 标记 | {code_quality.get('todo_count', 0)} | < 10 |
| FIXME 标记 | {code_quality.get('fixme_count', 0)} | 0 |
| 重复代码 | {code_quality.get('duplicate_code', 0)} | 0 |
| 质量评分 | {code_quality.get('quality_score', 0)}/100 | > 70 |

---

## 🏗️ 架构健康度

| 指标 | 数值 | 建议 |
|------|------|------|
| 核心文件变更 | {architecture.get('core_files_changed', 0)} | 少 |
| 代码耦合度 | {architecture.get('coupling_score', 0)} | < 20 |
| 领域边界清晰度 | {architecture.get('domain_boundary_score', 0)}/10 | > 7 |

---

## ⚠️ 风险分析

### 整体评分
**{risk_assessment.get('overall_score', 0):.0f}/100**

### 风险项
"""

    # 添加风险项
    risks = risk_assessment.get('risks', [])
    if risks:
        for i, risk in enumerate(risks, 1):
            report += f"\n{risk_color(risk.get('level', 'low'))} **风险 {i}**\n"
            report += f"- **指标**: {risk.get('indicator', '')}\n"
            report += f"- **级别**: {risk.get('level', '')}\n"
            report += f"- **说明**: {risk.get('message', '')}\n"
    else:
        report += "\n🟢 无显著风险项\n"

    # 添加行动建议
    report += f"""
---

## 🛠️ 行动建议

"""

    # 根据风险生成建议
    has_suggestions = False

    if code_quality.get('todo_count', 0) > 10:
        report += f"1. 🔴 **清理 TODO 标记**：当前有 {code_quality.get('todo_count', 0)} 个，建议减少到 10 个以下\n"
        has_suggestions = True

    if code_quality.get('fixme_count', 0) > 0:
        report += f"2. 🔴 **立即处理 FIXME**：当前有 {code_quality.get('fixme_count', 0)} 个需要立即修复\n"
        has_suggestions = True

    if code_size.get('growth_percentage', 0) > 5:
        report += f"3. 🟡 **控制代码增长**：当前增长 {code_size.get('growth_percentage', 0):.1f}%，建议控制在 5% 以下\n"
        has_suggestions = True

    if dependencies.get('depth', 0) > 3:
        report += f"4. 🟡 **优化依赖关系**：当前依赖深度 {dependencies.get('depth', 0)}，建议减少到 3 层以下\n"
        has_suggestions = True

    if not has_suggestions:
        report += "🟢 当前状态良好，建议保持！\n"

    # 添加代码审查章节
    if include_review and review_data:
        report += f"""
---

## 📋 代码审查

### 📝 变更概述

| 指标 | 数值 | 状态 |
|------|------|------|
| 变更文件数 | {review_data.get('changes', {}).get('changed_files', 0)} | {risk_color('low' if review_data.get('changes', {}).get('changed_files', 0) < 5 else 'medium')} |
| 新增代码行数 | {review_data.get('changes', {}).get('added_lines', 0)} | {risk_color('low' if review_data.get('changes', {}).get('added_lines', 0) < 200 else 'medium' if review_data.get('changes', {}).get('added_lines', 0) < 500 else 'high')} |
| 核心文件变更 | {review_data.get('changes', {}).get('core_files_changed', 0)} | {risk_color('medium' if review_data.get('changes', {}).get('core_files_changed', 0) > 0 else 'low')} |

### 🚨 发现的问题

"""
        # 显示危险模式
        dangerous_patterns = review_data.get('dangerous_patterns', [])
        if dangerous_patterns:
            for pattern in dangerous_patterns:
                severity_color = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'low': '🟢'
                }.get(pattern.get('severity'), '🟢')

                report += f"""
{severity_color} **{pattern.get('type', 'unknown')}**
- 文件: {pattern.get('file', 'unknown')}
- 说明: {pattern.get('function', pattern.get('lines_changed', '未知'))}
"""

        # 显示 TODO 变化
        todo_changes = review_data.get('todo_changes', {})
        if todo_changes.get('added', 0) > 0:
            report += f"""
🟡 **新增 TODO 标记**
- 数量: {todo_changes.get('added', 0)} 个
- 建议: 及时处理新增的待办事项
"""

        # 显示审查风险级别
        review_risk_level = review_data.get('risk_level', 'low')
        report += f"""
### 🎯 审查风险
**级别**: {risk_color(review_risk_level)} {review_risk_level}
"""

    # 添加 Mermaid 图表
    report += f"""
---

## 📊 趋势图表

```mermaid
pie title 风险分布
    "高风险" : {len([r for r in risks if r.get('level') == 'high'])}
    "中风险" : {len([r for r in risks if r.get('level') == 'medium'])}
    "低风险" : {len([r for r in risks if r.get('level') == 'low' or r.get('level') not in ['high', 'medium']])}
```

```mermaid
stateDiagram-v2
    [*] --> 立即修复
    [*] --> 优先优化
    [*] --> 建议改进
    [*] --> 正常维护

    立即修复 --> TODO标记: {code_quality.get('todo_count', 0)}
    立即修复 --> FIXME标记: {code_quality.get('fixme_count', 0)}
    优先优化 --> 依赖深度: {dependencies.get('depth', 0)}
    建议改进 --> 代码增长: {code_size.get('growth_percentage', 0):.1f}%
    正常维护 --> [*]
```
"""

    return report


def generate_html_report(data, template_path, report_date=None):
    """基于模板生成 HTML 报告"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        complexity_data = data.get('data', {})
        code_size = complexity_data.get('code_size', {})
        dependencies = complexity_data.get('dependencies', {})
        code_quality = complexity_data.get('code_quality', {})
        architecture = complexity_data.get('architecture', {})
        risk_assessment = complexity_data.get('risk_assessment', {})

        # 简单的模板替换（生产环境可以使用更复杂的模板引擎）
        # 这里只做基本的格式化，复杂替换需要报告生成器后续迭代

        # 在模板中注入数据
        data_str = json.dumps(data, indent=2, ensure_ascii=False)

        html = template.replace('{{data}}', data_str)
        html = html.replace('{{report_date}}', report_date or datetime.now().strftime('%Y-%m-%d'))

        return html
    except Exception as e:
        print(f"Error generating HTML: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='报告生成工具')
    parser.add_argument('--data', required=True, help='输入数据文件路径（JSON 格式）')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='输出格式')
    parser.add_argument('--template', help='HTML 模板文件路径（仅 HTML 格式需要）')
    parser.add_argument('--date', help='报告日期（默认：当前日期）')

    args = parser.parse_args()

    # 加载数据
    data = load_data(args.data)
    if not data:
        return

    # 生成报告
    if args.format == 'markdown':
        report = generate_markdown_report(data, args.date)
        output_ext = '.md'
    elif args.format == 'html':
        if not args.template:
            print("Error: --template is required for HTML format")
            return
        report = generate_html_report(data, args.template, args.date)
        output_ext = '.html'

    # 输出报告
    if report:
        if args.output:
            # 确保输出目录存在
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        else:
            print(report)


if __name__ == '__main__':
    main()
