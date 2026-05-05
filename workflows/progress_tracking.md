---
title: 进度记录机制
summary: 说明 AI 在文档生成和维护过程中为何需要持续记录进度、如何组织进度信息，以及这些记录如何支持中断恢复与用户审核。
keywords: progress | tracking | workflow | recovery | review | aicc
scope: 文档生成与维护过程中的进度记录机制
related_files: 无
dependencies: AI_ENTRY_POINT.md | templates/PROGRESS_TRACKING_TEMPLATE.md | workflows/path_a_first_generation.md
verified_at: 2026-05-05
---

# 进度记录机制

> **上级文档**: [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md)  
> **版本**: v2.2  
> **最后更新**: 2025-11-27

---

## 📝 为什么需要进度记录?

### 价值 1: 会话中断恢复 ⭐⭐⭐

**场景**: AI 会话可能随时中断(网络问题、超时、手动刷新等)

**好处**: 记录进度后,可从上次位置继续,避免重复劳动

### 价值 2: 便于用户审核 ⭐⭐⭐

**好处**:

- 用户可随时查看当前进度
- 清晰知道已完成哪些文档、正在生成哪些
- 预估剩余工作量和完成时间

### 价值 3: 质量保证 ⭐⭐

**好处**:

- 强制 AI 按顺序完成,避免遗漏
- 每个文档都有明确的状态标记
- 便于发现和修复生成过程中的问题

### 价值 4: 协作友好 ⭐

**好处**:

- 多人可通过进度文件了解生成状态
- 接手他人工作时快速了解进度

---

## 📋 进度记录方式

### 位置

**统一路径**: `dev_docs/_analysis/generation_progress.md`

### 模板

**使用模板**: `templates/PROGRESS_TEMPLATE.md`

---

## 🔄 AI 生成时的行为

### 1. 开始生成前

```markdown
✅ 创建进度记录: dev_docs/\_analysis/generation_progress.md
```

### 2. 每完成一个文档后

```markdown
✅ 更新进度记录: 标记 XX 文档为已完成
```

### 3. 所有文档生成完毕

```markdown
✅ 更新进度记录: 当前状态 = 已完成
✅ 生成完成报告
```

### 4. 会话中断恢复

**用户**: "继续生成文档"

**AI 操作**:

1. 读取`dev_docs/_analysis/generation_progress.md`
2. 识别未完成的部分
3. 输出: "检测到进度记录,上次完成到 XX,现在从 YY 继续"
4. 继续生成未完成的部分

---

## ⚠️ 重要原则

**无论项目规模大小,都必须使用进度记录！**

即使是小型项目,也应该记录进度,因为:

- 防止意外中断
- 提供透明度
- 养成良好习惯

---

## 🔗 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 主流程
- [生成流程](./generation_workflow.md) - 文档生成详情
- [PROGRESS_TEMPLATE.md](../templates/PROGRESS_TEMPLATE.md) - 进度模板

---

**版本**: v2.2  
**路径**: `workflows/progress_tracking.md`
