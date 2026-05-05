---
title: Workflows 协作流程模板
summary: 介绍 AI 角色库中的协作流程模板目录，说明现有工作流、规划中的多角色协作模板及其在角色体系中的用途。
keywords: agents | workflows | collaboration | templates | guide | aicc
scope: AI 角色库协作流程模板目录说明
related_files: 无
dependencies: agents/README.md | agents/workflows/create_custom_agent_workflow.md
verified_at: 2026-05-05
---

# Workflows - 协作流程模板

## 📋 概述

本目录包含 AI 角色库的协作流程和工作流文档。

---

## 📁 工作流列表

### V3.1 功能工作流

| 工作流           | 文档                                                                 | 状态      | 说明                      |
| ---------------- | -------------------------------------------------------------------- | --------- | ------------------------- |
| 创建自定义 Agent | [create_custom_agent_workflow.md](./create_custom_agent_workflow.md) | ✅ 已完成 | AI 辅助创建项目专属 Agent |

### 协作流程模板 (待开发)

以下流程模板规划用于指导多角色协作：

- `new_feature_workflow.md` - 新功能开发流程
- `bug_fix_workflow.md` - Bug 修复流程
- `refactoring_workflow.md` - 代码重构流程

**状态**: ⏸️ P1 优先级，后续开发

---

## 使用说明

### 触发工作流

**方式 1: 自然语言**

```
"帮我创建一个自定义 Agent"
"@workflow:创建自定义Agent"
```

**方式 2: 框架自动检测**

AI 会根据用户意图自动建议合适的工作流。

---

## 贡献工作流

如果您有新的协作流程需求，欢迎参考现有工作流文档创建新的流程模板。

---

**版本**: v1.0  
**最后更新**: 2025-12-01
