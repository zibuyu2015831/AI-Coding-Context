---
title: 备忘目录索引模板
summary: 提供 memos 目录索引模板，用于记录开发过程中暂不进入正式计划的延后想法、外部依赖、阻塞项和待验证假设。
keywords: template | memos | deferred | backlog | aicc
scope: 备忘目录索引模板
related_files: core/framework_spec.md | templates/PLAN_TEMPLATE.md
dependencies: 无
verified_at: 2026-05-29
---

# memos/README.md 模板

> **中文名称**: 备忘录

> **用途**: 记录开发过程中出现、但暂时不进入正式方案的想法、依赖、阻塞项、后续优化点和待验证假设。

---

## 使用边界

- `memos/` 不是承诺排期；只有迁入 `dev_docs/plans/active/` 的事项才进入方案驱动开发流程。
- 备忘事项应保持短小、可追踪，避免替代正式方案文档。
- 与用户讨论需求、Bug、架构调整或后续优化时，AI 必须主动阅读本文件和相关备忘录，关联已有记录，避免重复讨论或重复规划。
- 讨论中出现暂不实现的想法、外部依赖、延后优化点、待验证假设或用户明确要求稍后处理的事项时，AI 应主动将合适的内容沉淀为备忘录。
- 当事项被确认推进时，创建 `dev_docs/plans/active/YYYY-MM-DD_<type>_<short-name>.md`，并在原 memo 中追加迁移链接。
- 当事项失效时，将 `status` 标记为 `closed`，说明关闭原因。

---

## 命名规范

```text
YYYY-MM-DD_deferred_short-name.md
YYYY-MM-DD_dependency_short-name.md
YYYY-MM-DD_idea_short-name.md
YYYY-MM-DD_blocker_short-name.md
```

---

## 备忘模板

```markdown
---
type: deferred
status: open
created_at: YYYY-MM-DD
related_plan: 无
---

# [简短标题]

## 背景

[为什么记录这条备忘]

## 当前无法推进的原因

- [缺少的信息、外部依赖、优先级不足或实现条件不成熟]

## 触发条件

- [什么条件满足后应重新评估]

## 后续处理记录

- YYYY-MM-DD: 创建备忘。
```

---

## 当前备忘索引

### Open

_暂无_

### Closed

_暂无_
