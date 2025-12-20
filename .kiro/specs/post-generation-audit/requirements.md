---
title: 文档体系生成后自动审核机制
summary: 在用户使用框架完成文档体系搭建后，自动按照既定标准对生成的文档体系进行全面审核，识别遗漏项和质量问题，确保文档体系符合框架要求
keywords: 自动审核 | 质量保证 | 文档验证 | 后置检查 | 框架合规性
scope: 框架核心功能 - 文档生成后质量保证
related_files: workflows/path_a_first_generation.md | workflows/shared/ai_checklist.md
dependencies: dev/real_case/002/quality_review/COMPREHENSIVE_AUDIT.md
verified_at: 2025-12-19
---

# 文档体系生成后自动审核机制 - 需求文档

## 📋 需求概述

**优先级**: P0 (最高优先级)  
**需求来源**: 002案例质量审核实践  
**需求类型**: 新功能开发  
**预计工作量**: 3-5天

### 核心需求

在用户使用框架完成文档体系搭建后（Step 8执行完成），**自动触发**一个全面的审核流程，按照既定标准检查生成的文档体系，识别所有遗漏项和质量问题，生成详细的审核报告。

---

## 🎯 需求背景

### 问题陈述

通过002案例的实践，我们发现即使有完善的框架规范和检查清单，AI在生成文档体系时仍然会出现遗漏：

1. **方案文档遗漏**: 8个遗漏项（3个P0严重遗漏）
2. **主文档遗漏**: 3个必需章节缺失
3. **根本原因**: 依赖AI自觉性，缺少强制检查机制

### 为什么需要这个功能



#### 1. 质量保证的最后一道防线

- 方案生成阶段可能遗漏必需项
- 文档生成阶段可能偏离方案
- 需要一个**自动化的、全面的、标准化的**审核机制

#### 2. 提升用户信心

- 用户不知道生成的文档体系是否完整
- 用户不知道是否符合框架标准
- 需要一个**可信的、详细的**审核报告

#### 3. 持续改进的数据来源

- 收集常见遗漏项的数据
- 识别框架的薄弱环节
- 为框架改进提供依据

### 实践证明

002案例的手动审核发现了11个遗漏项：
- 方案文档: 8个遗漏（进度记录、文档摘要、AI_RULES等）
- 主文档: 3个缺失章节（文档维护触发器、AI编码禁忌、常见任务速查）

如果有自动审核机制，这些问题可以在生成完成后立即发现。

---

## 👥 用户故事

### 用户故事 1: 自动审核触发

**作为** 框架用户  
**我想要** 在文档生成完成后自动触发审核  
**以便** 立即知道文档体系是否完整和合规

#### 验收标准

1. WHEN 文档生成完成（Step 8完成）THEN 系统自动触发审核流程
2. WHEN 审核开始 THEN 系统显示审核进度和当前检查项
3. WHEN 审核完成 THEN 系统生成详细的审核报告
4. WHEN 发现问题 THEN 系统按优先级分类（P0/P1/P2）
5. WHEN 审核报告生成 THEN 系统提示用户查看并决定下一步

### 用户故事 2: 方案文档审核

**作为** 框架用户  
**我想要** 审核机制检查方案文档的完整性  
**以便** 确保方案包含所有必需项

#### 验收标准

1. WHEN 审核方案文档 THEN 系统检查所有必需章节是否存在
2. WHEN 检查必需章节 THEN 系统验证章节内容是否完整
3. WHEN 发现缺失章节 THEN 系统标记为P0问题并提供补充建议
4. WHEN 发现内容不完整 THEN 系统标记为P1问题并说明缺失内容
5. WHEN 所有检查完成 THEN 系统生成方案文档审核报告

### 用户故事 3: 主文档审核

**作为** 框架用户  
**我想要** 审核机制检查主文档的完整性  
**以便** 确保主文档符合模板要求

#### 验收标准

1. WHEN 审核主文档 THEN 系统对照模板检查所有必需章节
2. WHEN 检查YAML摘要 THEN 系统验证所有必需字段是否填写
3. WHEN 检查代码示例 THEN 系统验证是否有注释和说明
4. WHEN 发现缺失章节 THEN 系统标记为P0问题
5. WHEN 发现质量问题 THEN 系统标记为P1问题

### 用户故事 4: 子文档审核

**作为** 框架用户  
**我想要** 审核机制检查所有子文档  
**以便** 确保子文档都有标准化摘要和完整内容

#### 验收标准

1. WHEN 审核子文档 THEN 系统检查每个子文档的YAML摘要
2. WHEN 检查摘要 THEN 系统验证7个必需字段是否完整
3. WHEN 检查related_files THEN 系统验证文件路径是否存在
4. WHEN 发现摘要缺失 THEN 系统标记为P0问题
5. WHEN 发现字段不完整 THEN 系统标记为P1问题

### 用户故事 5: 进度记录审核

**作为** 框架用户  
**我想要** 审核机制检查进度记录文件  
**以便** 确保进度记录完整且状态正确

#### 验收标准

1. WHEN 审核进度记录 THEN 系统检查generation_progress.md是否存在
2. WHEN 检查进度状态 THEN 系统验证是否标记为"已完成"
3. WHEN 检查文档清单 THEN 系统验证所有文档是否都已标记完成
4. WHEN 发现进度文件缺失 THEN 系统标记为P0问题
5. WHEN 发现状态不一致 THEN 系统标记为P1问题

### 用户故事 6: AI_RULES文件审核

**作为** 框架用户  
**我想要** 审核机制检查AI_RULES文件  
**以便** 确保用户可以直接使用规则文件

#### 验收标准

1. WHEN 审核AI_RULES THEN 系统检查ai_rules.md是否存在
2. WHEN 检查文件内容 THEN 系统验证是否包含必需章节
3. WHEN 检查文档索引 THEN 系统验证是否链接到主文档
4. WHEN 发现文件缺失 THEN 系统标记为P0问题
5. WHEN 发现内容不完整 THEN 系统标记为P1问题

### 用户故事 7: 审核报告生成

**作为** 框架用户  
**我想要** 获得详细的审核报告  
**以便** 了解所有问题并决定如何处理

#### 验收标准

1. WHEN 审核完成 THEN 系统生成结构化的审核报告
2. WHEN 生成报告 THEN 系统按优先级分类所有问题
3. WHEN 列出问题 THEN 系统提供具体的改进建议
4. WHEN 报告完成 THEN 系统计算综合评分
5. WHEN 展示报告 THEN 系统提供下一步行动建议

### 用户故事 8: 问题修复引导

**作为** 框架用户  
**我想要** 系统引导我修复发现的问题  
**以便** 快速完善文档体系

#### 验收标准

1. WHEN 用户查看审核报告 THEN 系统提供"一键修复"选项（针对P0问题）
2. WHEN 用户选择修复 THEN 系统自动补充缺失的章节/文件
3. WHEN 自动修复完成 THEN 系统重新运行审核
4. WHEN 无法自动修复 THEN 系统提供详细的手动修复指南
5. WHEN 所有P0问题解决 THEN 系统标记文档体系为"合格"

---

## 📊 功能需求

### 功能1: 审核触发机制

**描述**: 在文档生成完成后自动触发审核

**触发条件**:
- Step 8（执行文档生成）完成
- 所有文档生成完毕
- generation_progress.md标记为"已完成"

**触发方式**:
- 自动触发（默认）
- 手动触发（用户命令：`@audit` 或 `@review:docs`）

**输出**:
- 审核开始提示
- 审核进度显示
- 审核完成通知

### 功能2: 方案文档审核器

**描述**: 检查generation_plan.md的完整性

**检查项**:
1. 必需章节检查
   - 任务复杂度评估 ✓
   - 进度记录机制 ✓
   - 文档摘要规范 ✓
   - AI_RULES生成计划 ✓
   - 交互策略 ✓
   - 文档生成计划 ✓
   - 质量保证措施 ✓

2. 章节内容检查
   - 进度记录机制: 是否提及generation_progress.md
   - 文档摘要规范: 是否说明YAML Frontmatter要求
   - AI_RULES生成计划: 是否说明生成时机

3. 数据验证检查
   - 统计数据是否有验证命令
   - 代码示例是否有文件路径

**输出**:
- 缺失章节列表（P0）
- 内容不完整列表（P1）
- 改进建议

### 功能3: 主文档审核器

**描述**: 检查AI_Coding_Context.md的完整性

**检查项**:
1. YAML Frontmatter检查
   - 所有必需字段是否填写
   - 格式是否符合规范

2. 必需章节检查（对照模板）
   - 文档定位 ✓
   - 项目概览 ✓
   - 关键目录速查 ✓
   - 场景快速导航 ✓
   - 文档索引 ✓
   - 设计思维引导 ✓
   - 开发流程规范 ✓
   - AI角色库 ✓
   - 核心代码模式 ✓
   - 命名规范 ✓
   - 业务模块映射 ✓
   - 文档维护触发器 ✓
   - AI编码禁忌 ✓
   - 常见任务速查 ✓

3. 内容质量检查
   - 代码示例是否有注释
   - 表格是否完整
   - 链接是否有效

**输出**:
- 缺失章节列表（P0）
- 质量问题列表（P1）
- 改进建议

### 功能4: 子文档审核器

**描述**: 检查所有子文档的摘要和内容

**检查项**:
1. 文档摘要检查
   - YAML Frontmatter是否存在
   - 7个必需字段是否完整
   - related_files路径是否存在

2. 文档内容检查
   - 是否符合对应的模板
   - 章节结构是否完整

**输出**:
- 摘要缺失/不完整的文档列表
- 内容问题列表
- 改进建议

### 功能5: 进度记录审核器

**描述**: 检查generation_progress.md的完整性

**检查项**:
1. 文件存在性检查
2. 进度状态检查（是否标记为"已完成"）
3. 文档清单检查（所有文档是否都已标记完成）
4. 时间记录检查（是否记录了完成时间）

**输出**:
- 进度记录问题列表
- 改进建议

### 功能6: AI_RULES审核器

**描述**: 检查ai_rules.md的完整性

**检查项**:
1. 文件存在性检查
2. 必需章节检查
   - 文档体系入口
   - 项目概述
   - 开发规范
   - 常见任务指引

3. 链接有效性检查

**输出**:
- AI_RULES问题列表
- 改进建议

### 功能7: 审核报告生成器

**描述**: 生成结构化的审核报告

**报告结构**:
```markdown
# 文档体系审核报告

## 审核概览
- 审核时间
- 审核范围
- 综合评分

## 问题统计
- P0严重问题: X个
- P1重要问题: X个
- P2可选问题: X个

## 详细问题清单

### P0严重问题
1. [问题描述]
   - 影响: [影响说明]
   - 改进建议: [具体建议]

### P1重要问题
...

### P2可选问题
...

## 改进建议
...

## 下一步行动
...
```

**输出位置**: `dev_docs/_analysis/audit_report.md`

### 功能8: 问题修复助手

**描述**: 引导用户修复发现的问题

**修复方式**:
1. 自动修复（针对简单问题）
   - 补充缺失的章节（使用模板）
   - 生成缺失的文件（使用模板）

2. 引导修复（针对复杂问题）
   - 提供详细的修复步骤
   - 提供代码/内容示例

3. 重新审核
   - 修复后自动重新运行审核
   - 验证问题是否解决

**输出**:
- 修复进度提示
- 修复结果报告
- 重新审核报告

---

## 🔧 技术需求

### 技术架构

```
审核系统
├── 审核触发器 (Audit Trigger)
├── 审核引擎 (Audit Engine)
│   ├── 方案文档审核器
│   ├── 主文档审核器
│   ├── 子文档审核器
│   ├── 进度记录审核器
│   └── AI_RULES审核器
├── 报告生成器 (Report Generator)
└── 修复助手 (Fix Assistant)
```

### 实现方式

**语言选择**: Python（与现有工具链一致）

**核心文件**:
- `tools/py/audit_system.py` - 审核系统主入口
- `tools/py/auditors/plan_auditor.py` - 方案文档审核器
- `tools/py/auditors/main_doc_auditor.py` - 主文档审核器
- `tools/py/auditors/sub_doc_auditor.py` - 子文档审核器
- `tools/py/auditors/progress_auditor.py` - 进度记录审核器
- `tools/py/auditors/ai_rules_auditor.py` - AI_RULES审核器
- `tools/py/report_generator.py` - 报告生成器
- `tools/py/fix_assistant.py` - 修复助手

**配置文件**:
- `config/audit_config.yaml` - 审核配置
  - 检查项定义
  - 评分权重
  - 问题优先级规则

**模板文件**:
- `templates/AUDIT_REPORT_TEMPLATE.md` - 审核报告模板

### 数据结构

```python
# 审核结果数据结构
class AuditResult:
    def __init__(self):
        self.timestamp = None
        self.scope = []
        self.score = 0.0
        self.issues = {
            'P0': [],
            'P1': [],
            'P2': []
        }
        self.statistics = {}
        self.recommendations = []

# 问题数据结构
class Issue:
    def __init__(self):
        self.id = None
        self.priority = None  # P0/P1/P2
        self.category = None  # 方案文档/主文档/子文档等
        self.title = None
        self.description = None
        self.impact = None
        self.suggestion = None
        self.auto_fixable = False
```

---

## 🔄 工作流集成

### 集成点1: Step 8完成后

**位置**: `workflows/path_a_first_generation.md` - Step 8末尾

**修改内容**:
```markdown
## Step 8: 执行文档生成（用户确认后）

...（现有内容）

### 8.5 自动审核文档体系 ⭐ 新增

**触发时机**: 所有文档生成完成后

**执行命令**:
```bash
python tools/py/audit_system.py --auto
```

**审核内容**:
1. 方案文档完整性
2. 主文档完整性
3. 子文档摘要规范
4. 进度记录完整性
5. AI_RULES文件完整性

**输出**:
- 审核报告: `dev_docs/_analysis/audit_report.md`
- 综合评分: X/10
- 问题统计: P0/P1/P2

**下一步**:
- 如果评分 ≥9.0: 文档体系合格，可以交付
- 如果评分 7.0-8.9: 建议修复P0问题
- 如果评分 <7.0: 必须修复P0和P1问题
```

### 集成点2: AI检查清单

**位置**: `workflows/shared/ai_checklist.md`

**修改内容**:
```markdown
## 📝 生成文档后的自检项

### 自动审核

- [ ] **运行审核系统**: 执行 `python tools/py/audit_system.py --auto`
- [ ] **查看审核报告**: 检查 `dev_docs/_analysis/audit_report.md`
- [ ] **修复P0问题**: 所有P0问题必须修复
- [ ] **重新审核**: 修复后重新运行审核
- [ ] **确认合格**: 综合评分 ≥9.0
```

### 集成点3: 主文档模板

**位置**: `templates/AI_Coding_Context_TEMPLATE.md`

**修改内容**: 确保模板包含所有必需章节（已在MAIN_DOC_AUDIT中识别）

---

## 📁 涉及的文件

### 需要创建的文件

1. `tools/py/audit_system.py` - 审核系统主入口
2. `tools/py/auditors/` - 审核器目录
   - `__init__.py`
   - `plan_auditor.py`
   - `main_doc_auditor.py`
   - `sub_doc_auditor.py`
   - `progress_auditor.py`
   - `ai_rules_auditor.py`
3. `tools/py/report_generator.py` - 报告生成器
4. `tools/py/fix_assistant.py` - 修复助手
5. `config/audit_config.yaml` - 审核配置
6. `templates/AUDIT_REPORT_TEMPLATE.md` - 审核报告模板
7. `tools/py/tests/test_audit_system.py` - 审核系统测试

### 需要修改的文件

1. `workflows/path_a_first_generation.md`
   - 添加 Step 8.5: 自动审核文档体系

2. `workflows/shared/ai_checklist.md`
   - 添加自动审核检查项

3. `templates/AI_Coding_Context_TEMPLATE.md`
   - 确保包含所有必需章节

4. `tools/README.md`
   - 添加审核系统工具说明

5. `AI_ENTRY_POINT.md`
   - 更新工作流说明，提及自动审核

---

## 🎯 验收标准

### 整体验收

- [ ] 审核系统可以自动触发
- [ ] 审核系统可以手动触发
- [ ] 审核报告结构清晰、内容完整
- [ ] 所有检查项都已实现
- [ ] 问题分类准确（P0/P1/P2）
- [ ] 改进建议具体可行
- [ ] 修复助手可以自动修复简单问题
- [ ] 使用002案例测试通过

### 功能验收

- [ ] 方案文档审核器: 可以检测所有8个遗漏项
- [ ] 主文档审核器: 可以检测所有3个缺失章节
- [ ] 子文档审核器: 可以检测摘要缺失/不完整
- [ ] 进度记录审核器: 可以检测进度文件问题
- [ ] AI_RULES审核器: 可以检测AI_RULES文件问题
- [ ] 报告生成器: 生成的报告符合模板要求
- [ ] 修复助手: 可以自动补充缺失章节

### 性能验收

- [ ] 审核时间 <30秒（小型项目）
- [ ] 审核时间 <60秒（中型项目）
- [ ] 审核时间 <120秒（大型项目）

---

## 📚 参考资料

### 核心参考

1. `dev/real_case/002/quality_review/COMPREHENSIVE_AUDIT.md`
   - 8个遗漏项的详细分析
   - 检查项定义
   - 改进建议

2. `dev/real_case/002/quality_review/MAIN_DOC_AUDIT.md`
   - 主文档的13个章节评估
   - 缺失章节分析
   - 改进建议

3. `dev/real_case/002/quality_review/DEFECT_ANALYSIS.md`
   - 根因分析
   - 薄弱环节识别
   - 改进方案

### 模板参考

1. `templates/AI_Coding_Context_TEMPLATE.md` - 主文档模板
2. `templates/GENERATION_PLAN_TEMPLATE.md` - 方案文档模板
3. `templates/PROGRESS_TEMPLATE.md` - 进度记录模板
4. `templates/AI_RULES_TEMPLATE.md` - AI_RULES模板

### 工作流参考

1. `workflows/path_a_first_generation.md` - 首次生成工作流
2. `workflows/shared/ai_checklist.md` - AI检查清单
3. `workflows/progress_tracking.md` - 进度追踪机制

---

## 🚀 实施计划

### Phase 1: 核心审核器开发 (2天)

**Day 1**:
- 创建审核系统框架
- 实现方案文档审核器
- 实现主文档审核器

**Day 2**:
- 实现子文档审核器
- 实现进度记录审核器
- 实现AI_RULES审核器

### Phase 2: 报告和修复 (1天)

**Day 3**:
- 实现报告生成器
- 实现修复助手（基础版）
- 创建审核报告模板

### Phase 3: 集成和测试 (1-2天)

**Day 4**:
- 集成到工作流
- 使用002案例测试
- 修复发现的问题

**Day 5** (可选):
- 性能优化
- 增强修复助手
- 完善文档

---

## 💡 未来扩展

### 扩展1: 智能修复

- 使用AI自动生成缺失的章节内容
- 根据项目特点定制内容

### 扩展2: 持续审核

- 定期审核文档健康度
- 检测文档是否过时

### 扩展3: 审核历史

- 记录每次审核结果
- 追踪问题修复进度
- 生成质量趋势报告

### 扩展4: 自定义检查项

- 允许用户添加自定义检查项
- 支持项目特定的质量标准

---

**需求文档版本**: v1.0  
**创建日期**: 2025-12-19  
**创建者**: Framework Quality Team  
**状态**: 待开发
