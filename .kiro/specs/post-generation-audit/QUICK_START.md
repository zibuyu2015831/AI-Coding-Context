---
title: 文档体系生成后自动审核机制 - 快速开始
summary: 为开发者提供快速开始指南，包括需求概述、核心功能、实施步骤和测试方法，帮助开发者快速理解并开始开发
keywords: 快速开始 | 开发指南 | 审核系统 | 实施步骤
scope: 开发指南
related_files: requirements.md
verified_at: 2025-12-19
---

# 文档体系生成后自动审核机制 - 快速开始

## 🎯 3分钟理解需求

### 要做什么？

在用户使用框架完成文档体系搭建后，**自动运行一个审核系统**，检查生成的文档是否符合框架标准，识别所有遗漏项和质量问题。

### 为什么需要？

002案例实践发现：
- **方案文档**: 8个遗漏项（进度记录、文档摘要、AI_RULES等）
- **主文档**: 3个缺失章节（文档维护触发器、AI编码禁忌、常见任务速查）
- **根本原因**: 依赖AI自觉性，缺少强制检查机制

### 核心价值

1. **质量保证的最后一道防线** - 自动发现遗漏
2. **提升用户信心** - 提供可信的审核报告
3. **持续改进的数据来源** - 收集常见问题数据

---

## 🏗️ 核心功能

### 5个审核器

1. **方案文档审核器** - 检查generation_plan.md（8个检查项）
2. **主文档审核器** - 检查AI_Coding_Context.md（13个章节）
3. **子文档审核器** - 检查所有子文档的摘要
4. **进度记录审核器** - 检查generation_progress.md
5. **AI_RULES审核器** - 检查ai_rules.md

### 3个核心组件

1. **审核引擎** - 执行所有检查
2. **报告生成器** - 生成结构化报告
3. **修复助手** - 引导用户修复问题

---

## 🚀 快速实施

### Step 1: 创建核心文件结构 (30分钟)

```bash
# 创建目录
mkdir -p tools/py/auditors
mkdir -p tools/py/tests

# 创建核心文件
touch tools/py/audit_system.py
touch tools/py/auditors/__init__.py
touch tools/py/auditors/plan_auditor.py
touch tools/py/auditors/main_doc_auditor.py
touch tools/py/auditors/sub_doc_auditor.py
touch tools/py/auditors/progress_auditor.py
touch tools/py/auditors/ai_rules_auditor.py
touch tools/py/report_generator.py
touch tools/py/fix_assistant.py

# 创建配置和模板
touch config/audit_config.yaml
touch templates/AUDIT_REPORT_TEMPLATE.md

# 创建测试
touch tools/py/tests/test_audit_system.py
```

### Step 2: 实现审核系统主入口 (1小时)

**文件**: `tools/py/audit_system.py`

**核心逻辑**:
```python
#!/usr/bin/env python3
"""文档体系审核系统"""

import argparse
from pathlib import Path
from auditors import (
    PlanAuditor,
    MainDocAuditor,
    SubDocAuditor,
    ProgressAuditor,
    AIRulesAuditor
)
from report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description='审核文档体系')
    parser.add_argument('--auto', action='store_true', help='自动模式')
    parser.add_argument('--path', default='.', help='项目路径')
    args = parser.parse_args()
    
    print("🔍 开始审核文档体系...")
    
    # 1. 运行所有审核器
    results = {}
    results['plan'] = PlanAuditor().audit(args.path)
    results['main_doc'] = MainDocAuditor().audit(args.path)
    results['sub_docs'] = SubDocAuditor().audit(args.path)
    results['progress'] = ProgressAuditor().audit(args.path)
    results['ai_rules'] = AIRulesAuditor().audit(args.path)
    
    # 2. 生成报告
    report = ReportGenerator().generate(results)
    
    # 3. 输出报告
    output_path = Path(args.path) / 'dev_docs/_analysis/audit_report.md'
    output_path.write_text(report, encoding='utf-8')
    
    print(f"✅ 审核完成！报告已生成: {output_path}")
    
    # 4. 显示摘要
    print_summary(results)

if __name__ == '__main__':
    main()
```

### Step 3: 实现方案文档审核器 (2小时)

**文件**: `tools/py/auditors/plan_auditor.py`

**检查项**:
```python
REQUIRED_SECTIONS = [
    "任务复杂度评估",
    "进度记录机制",
    "文档摘要规范",
    "AI_RULES 生成计划",
    "交互策略",
    "文档生成计划",
    "质量保证措施"
]

SECTION_CONTENT_CHECKS = {
    "进度记录机制": [
        "generation_progress.md",
        "PROGRESS_TEMPLATE.md"
    ],
    "文档摘要规范": [
        "YAML Frontmatter",
        "SUMMARY_FORMAT_SPEC.md"
    ],
    "AI_RULES 生成计划": [
        "dev_docs/rules/combined/AI_RULES.md",
        "AI_RULES_TEMPLATE.md"
    ]
}
```

### Step 4: 实现主文档审核器 (2小时)

**文件**: `tools/py/auditors/main_doc_auditor.py`

**检查项**: 对照 `templates/AI_Coding_Context_TEMPLATE.md`

### Step 5: 实现其他审核器 (2小时)

- 子文档审核器
- 进度记录审核器
- AI_RULES审核器

### Step 6: 实现报告生成器 (1小时)

**文件**: `tools/py/report_generator.py`

**使用模板**: `templates/AUDIT_REPORT_TEMPLATE.md`

### Step 7: 集成到工作流 (1小时)

修改相关工作流文件，添加审核步骤。

### Step 8: 测试验证 (2小时)

使用002案例作为测试用例，验证审核系统能发现所有11个遗漏项。

---

## 🧪 测试方法

### 测试用例: 002案例

**测试目标**: 验证审核系统能发现所有已知遗漏项

**测试步骤**:
```bash
# 1. 进入002案例目录
cd dev/real_case/002

# 2. 运行审核系统
python ../../tools/py/audit_system.py --auto

# 3. 查看审核报告
cat dev_docs/_analysis/audit_report.md
```

**预期结果**:
```markdown
# 文档体系审核报告

## 问题统计
- P0严重问题: 3个
  1. 进度记录机制遗漏
  2. AI_RULES文件缺失
  3. 主文档缺少3个必需章节

- P1重要问题: 5个
  ...

## 综合评分: 7.6/10
```

### 验收标准

- [ ] 检测到方案文档的8个遗漏项
- [ ] 检测到主文档的3个缺失章节
- [ ] 问题分类准确（P0/P1/P2）
- [ ] 综合评分准确（7.6/10）
- [ ] 改进建议具体可行

---

## 📖 开发指南

### 开发顺序

1. **先实现审核器** - 核心功能
2. **再实现报告生成** - 输出展示
3. **最后实现修复助手** - 增强功能
4. **集成到工作流** - 完整闭环

### 代码风格

- 使用Python 3.8+
- 遵循PEP 8规范
- 添加类型注解
- 编写单元测试

### 错误处理

- 文件不存在: 标记为P0问题
- 格式错误: 标记为P1问题
- 内容不完整: 标记为P1问题

---

## 🔗 相关文档

### 需求文档

- [requirements.md](./requirements.md) - 完整需求文档

### 参考案例

- 002 案例审核报告为历史外部案例，当前仓库未随附 `dev/real_case/002/quality_review/` 归档。
  - COMPREHENSIVE_AUDIT.md - 8个遗漏项
  - MAIN_DOC_AUDIT.md - 主文档评估
  - DEFECT_ANALYSIS.md - 根因分析

### 框架文档

- [workflows/path_a_first_generation.md](../../../workflows/path_a_first_generation.md)
- [workflows/shared/ai_checklist.md](../../../workflows/shared/ai_checklist.md)
- [templates/AI_Coding_Context_TEMPLATE.md](../../../templates/AI_Coding_Context_TEMPLATE.md)

---

**文档版本**: v1.0  
**创建日期**: 2025-12-19  
**预计开发时间**: 3-5天  
**优先级**: P0 (最高)
