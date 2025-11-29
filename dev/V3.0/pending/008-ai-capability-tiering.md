# 008 - AI 能力分级使用机制

**优先级**: P2  
**状态**: 🟡 待讨论  
**预估工作量**: 5 天  
**来源**: 《AI_PROGRAMMING_ANALYSIS_REVIEW.md》

---

## 📋 问题描述

**痛点**: 所有任务都用高级 AI，Token 成本高

---

## 💡 解决方案

### 分级策略

| 任务类型  | AI 级别 | 模型选择   | Token 成本 |
| --------- | ------- | ---------- | ---------- |
| 简单 CRUD | L1 基础 | GPT-3.5    | 低         |
| 业务逻辑  | L2 标准 | GPT-4      | 中         |
| 架构设计  | L3 高级 | Claude-3.5 | 高         |
| 代码审查  | L2 标准 | GPT-4      | 中         |

### 自动分级

```python
def select_ai_model(task_type, complexity):
    if task_type == "CRUD" and complexity < 3:
        return "gpt-3.5-turbo"  # 低成本
    elif task_type == "architecture":
        return "claude-3.5-sonnet"  # 高质量
    else:
        return "gpt-4"  # 标准
```

---

## 📊 价值评估

- Token 成本优化 30-50%
- 质量不降低

---

## ⚠️ 疑问

1. ❓ 如何自动判断任务复杂度?
2. ❓ 用户是否可手动指定模型?

---

**创建日期**: 2025-11-29
