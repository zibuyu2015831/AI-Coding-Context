---
title: 方案文档索引模板
summary: 提供项目方案文档索引模板，用于按 active、done、archive 生命周期管理功能开发、Bug 修复和其他方案文档。
keywords: template | plans | index | bugfix | feature | aicc
scope: 方案文档索引模板
related_files: 无
dependencies: templates/PLAN_TEMPLATE.md | 无
verified_at: 2026-05-29
---

# plans/README.md 模板

> **用途**: 按生命周期管理所有功能开发、Bug 修复、重构和文档调整方案，作为开发前的必经规划步骤。

---

## 📋 使用规范

### **方案规范化说明**

为了便于状态流转、后续归档和提取关键要点到 `knowledge/`，所有方案文档应使用统一模板：

**模板位置**: `ai_coding_context/templates/PLAN_TEMPLATE.md`

**规范化优势**:

1. ✅ 方便后续归档和检索
2. ✅ 便于提取关键要点到 knowledge/
3. ✅ 统一沟通方式
4. ✅ 支持自动化处理

---

### **何时创建方案文档？**

**必须创建方案**的场景：

- ✅ 新增业务功能/模块
- ✅ 修改核心架构逻辑
- ✅ 涉及多个模块的 Bug 修复
- ✅ 性能优化改造
- ✅ 重构现有功能

**可选创建方案**的场景：

- 🟡 简单 UI 调整（如文案修改、样式微调）
- 🟡 单文件内的简单 Bug 修复

### **方案文档命名规范**

```
格式: YYYY-MM-DD_<type>_<short-name>.md
目录: 新方案统一创建到 dev_docs/plans/active/
类型: feature | bugfix | refactor | docs | perf

示例:
- active/2025-11-27_feature_user-export.md
- active/2025-11-26_bugfix_login-timeout.md
```

### **方案文档模板**

请使用统一模板 `ai_coding_context/templates/PLAN_TEMPLATE.md`

**核心章节**:

- 📋 方案元信息 - 类型、优先级、状态
- 📝 背景与问题 - 清晰描述问题
- 🎯 解决方案 - 技术选型、实施步骤、代码变更
- ✅ 验证计划 - 测试清单
- 🔑 **关键要点** - ⚠️ 用于 knowledge 提取
- 📚 参考资料
- 📅 执行记录

---

### **方案归档流程**

#### 何时归档到 knowledge/？

**触发条件**（需同时满足）:

1. 方案状态为"已完成"
2. "关键要点"部分非空
3. 符合以下任一条件:
   - 解决了耗时 > 2 小时的难题
   - 发现了框架/库的非常规用法
   - 总结了可复用的架构模式
   - 性能优化效果显著（提升 > 30%）

#### 归档步骤

1. **提取关键要点**

   - 从方案的"🔑 关键要点"章节提取内容
   - 整理为独立的知识文档

2. **创建 knowledge 文档**

   - 在`knowledge/`对应分类下创建文档
   - 使用知识库文档模板

3. **添加知识沉淀标记**

   - 在原方案末尾添加:
     ```markdown
     > ✅ 已归档到: `knowledge/[分类]/[文档名].md`
     ```

4. **移动方案到 done/**
   - 将原方案从 `active/` 移动到 `done/`
   - 将 frontmatter 或元信息中的状态改为 `done` / `已完成`

5. **更新索引**
   - 更新`knowledge/README.md`索引
   - 更新本文件的方案状态

---

## 📊 方案状态索引

### 🔵 Active

_暂无_

### ✅ Done

_暂无_

<!-- 示例:
- [2025-11-25_优化列表性能](./done/2025-11-25_perf_list-performance.md)
  - 已归档到: `knowledge/performance/list-virtualization.md`
-->

### 📦 Archive

> 废弃、搁置或被替代的方案移至此处。已完成方案继续保留在 `done/`。

_暂无_

---

## 🗂️ 生命周期目录

### Active (`active/`)

存放待审核、已确认或实施中的方案。新功能、Bug 修复、重构、文档调整都先进入这里。

### Done (`done/`)

存放已经实施、验证并完成必要文档同步的方案。

### Archive (`archive/`)

存放废弃、搁置或被替代的方案。不要把已完成方案移入这里。

---

## 🔄 维护规范

1. **创建方案**: AI 在开发功能/修复 Bug 前，先创建方案文档
2. **更新状态**: 状态变化时移动文件到 `active/`、`done/` 或 `archive/`，并更新本 README 索引
3. **归档规则**: 只有废弃、搁置或被替代的方案进入 `archive/`
4. **知识沉淀**: 有价值的方案完成后，提炼到 `knowledge/` 目录

---

## 💡 提示

- 方案文档是**人工审核点**，确保开发方向正确
- 方案文档是**AI 上下文传递载体**，跨会话开发时快速恢复上下文
- 方案文档是**可追溯性保障**，代码变更有据可查
