# 文档质量保证体系

> **用途**: 为框架文档提供系统化的质量保证工具和流程  
> **核心理念**: 人工阅读 + AI 互动的审查方式  
> **版本**: v1.0  
> **创建时间**: 2025-11-29

---

## 📋 体系概述

本目录提供框架文档的质量保证工具和流程，支持**人工阅读+AI 互动**的审查方式。

### 核心价值

- ✅ **标准化审查** - 统一的质量标准和流程
- ✅ **高效准备** - 预置审查上下文，减少重复劳动
- ✅ **质量可量化** - 明确的检查清单和评分标准
- ✅ **知识沉淀** - 审查报告归档，可追溯
- ✅ **支持演进** - 为框架持续改进提供基础设施

---

## 📁 目录结构

### standards/ - 质量标准

**用途**: 定义各类文档的质量标准

- [COMMON_STANDARDS.md](./standards/COMMON_STANDARDS.md) - 适用于所有文档的通用标准（准确性、完整性、一致性、可读性、可操作性）
- [BY_DOCUMENT_TYPE.md](./standards/BY_DOCUMENT_TYPE.md) - 按文档类型分类的专项标准（入口文档、核心规范、工作流、指导、模板）
- [QUALITY_CHECKLIST.md](./standards/QUALITY_CHECKLIST.md) - 快速检查清单（5 个维度）

### contexts/ - 单个文档审查上下文

**用途**: 为每个文档提供专门的审查上下文

每个文档的审查上下文，用于新建 AI 会话时提供背景信息。

**使用方式**:

```
【新建AI会话窗口】
1. 发送: dev/FRAMEWORK_CONTEXT.md （全局上下文）
2. 发送: quality/contexts/[文档名].md （单个文档上下文）
3. 发送: 实际文档内容
4. 开始审查讨论
```

**文件清单**: 见下方"文档索引"

### reports/ - 审查报告

**用途**: 归档历史审查报告，作为质量改进的记录

**命名规范**: `YYYY-MM-DD-vX.X-audit.md`

### tools/ - 审查辅助工具（可选）

**用途**: 提供自动化检查工具的说明文档

- [LINK_CHECKER.md](./tools/LINK_CHECKER.md) - 链接有效性检查工具说明
- [TERMINOLOGY_CHECKER.md](./tools/TERMINOLOGY_CHECKER.md) - 术语一致性检查工具说明

---

## 🔄 审查工作流

详见: [AUDIT_WORKFLOW.md](./AUDIT_WORKFLOW.md)

**简要流程**:

```
1. 选择要审查的文档
2. 新建AI会话窗口
3. 加载全局上下文（dev/FRAMEWORK_CONTEXT.md）
4. 加载文档审查上下文（quality/contexts/xxx.md）
5. 发送实际文档内容
6. AI分析并提供优化建议
7. 人工审核并决定是否采纳
8. 执行优化
9. （可选）记录审查报告
```

---

## 📊 文档索引

### 入口文档

- [ ] [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) → [审查上下文](../AI_ENTRY_POINT.md)
- [ ] [README.md](../README.md) → [审查上下文](../README.md)

### 核心规范文档 (core/)

- [ ] [language_rules.md](../core/language_rules.md) → [审查上下文](./contexts/core_language_rules.md)
- [ ] [security_rules.md](../core/security_rules.md) → [审查上下文](./contexts/core_security_rules.md)
- [ ] [project_types.md](../core/project_types.md) → [审查上下文](./contexts/core_project_types.md)
- [ ] [update_triggers.md](../core/update_triggers.md) → [审查上下文](./contexts/core_update_triggers.md)

### 工作流文档 (workflows/)

- [ ] [generation_workflow.md](../workflows/generation_workflow.md) → [审查上下文](./contexts/workflows_generation_workflow.md)
- [ ] [detection_workflow.md](../workflows/detection_workflow.md) → [审查上下文](./contexts/workflows_detection_workflow.md)
- [ ] [decision_workflow.md](../workflows/decision_workflow.md) → [审查上下文](./contexts/workflows_decision_workflow.md)
- [ ] [progress_tracking.md](../workflows/progress_tracking.md) → [审查上下文](./contexts/workflows_progress_tracking.md)
- [ ] [incremental_update_workflow.md](../workflows/incremental_update_workflow.md) → [审查上下文](./contexts/workflows_incremental_update_workflow.md)
- [ ] [monorepo_workflow.md](../workflows/monorepo_workflow.md) → [审查上下文](./contexts/workflows_monorepo_workflow.md)
- [ ] [document_health_check.md](../workflows/document_health_check.md) → [审查上下文](./contexts/workflows_document_health_check.md)

### 指导文档 (guides/)

- [ ] [quick_start.md](../guides/quick_start.md) → [审查上下文](./contexts/guides_quick_start.md)
- [ ] [project_types.md](../guides/project_types.md) → [审查上下文](./contexts/guides_project_types.md)
- [ ] [language_support.md](../guides/language_support.md) → [审查上下文](./contexts/guides_language_support.md)
- [ ] [documentation_maintenance.md](../guides/documentation_maintenance.md) → [审查上下文](./contexts/guides_documentation_maintenance.md)
- [ ] [ai_rules_maintenance.md](../guides/ai_rules_maintenance.md) → [审查上下文](./contexts/guides_ai_rules_maintenance.md)
- [ ] [configuration_management.md](../guides/configuration_management.md) → [审查上下文](./contexts/guides_configuration_management.md)

### 模板文档 (templates/)

- [ ] [GENERATION_PLAN_TEMPLATE.md](../templates/GENERATION_PLAN_TEMPLATE.md) → [审查上下文](./contexts/templates_GENERATION_PLAN_TEMPLATE.md)
- [ ] [PROJECT_ANALYSIS_REPORT_TEMPLATE.md](../templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md) → [审查上下文](./contexts/templates_PROJECT_ANALYSIS_REPORT_TEMPLATE.md)
- [ ] [PROGRESS_TEMPLATE.md](../templates/PROGRESS_TEMPLATE.md) → [审查上下文](./contexts/templates_PROGRESS_TEMPLATE.md)
- [ ] [AI_RULES_TEMPLATE.md](../templates/AI_RULES_TEMPLATE.md) → [审查上下文](./contexts/templates_AI_RULES_TEMPLATE.md)
- [ ] [AI_Coding_Context_TEMPLATE.md](../templates/AI_Coding_Context_TEMPLATE.md) → [审查上下文](./contexts/templates_AI_Coding_Context_TEMPLATE.md)

---

## 📈 审查进度跟踪

**当前版本**: V2.3  
**总文档数**: 30+  
**已审查**: 0  
**未审查**: 30+  
**V3.0 审查计划**: V3.0 完成后进行全面审查

---

## 💡 使用场景

### 场景 1: V3.0 完成后的全面审查

```
1. 为所有文档创建审查上下文（contexts/）
2. 按分类逐一审查（入口→核心→工作流→指导→模板）
3. 记录审查报告（reports/）
4. 汇总改进点并执行
```

### 场景 2: 单个文档的临时审查

```
1. 查阅该文档的审查上下文（contexts/xxx.md）
2. 新建AI会话
3. 加载全局上下文 + 文档上下文 + 文档内容
4. AI分析并提供建议
5. 执行优化
```

### 场景 3: 新文档创建后的质量验证

```
1. 为新文档创建审查上下文（基于模板）
2. 立即进行初次审查
3. 确保新文档符合质量标准
```

---

## 🔗 相关文档

- [workflows/document_health_check.md](../workflows/document_health_check.md) - 文档健康度检查（配合使用）

---

**版本**: v1.0  
**最后更新**: 2025-11-29  
**维护者**: Framework Team
