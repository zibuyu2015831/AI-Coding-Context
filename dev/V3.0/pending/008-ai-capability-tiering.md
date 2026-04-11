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

## 🧠 深度思考：必要性与边界问题

### 必要性分析：为什么需要分级使用？

#### 问题本质
目前的"全 GPT-4"策略导致：
- Token 成本高（32k 上下文每 1k 成本约 $0.03）
- 简单任务的资源浪费（杀鸡用牛刀）
- 速率限制（API 调用限制导致等待）

#### 分级使用的价值

| 指标 | 全 GPT-4 | 分级使用 | 提升幅度 |
|------|----------|----------|----------|
| Token 成本 | $100/周 | $30-$50/周 | -50% to -70% |
| API 调用速度 | 受限制 | 优化后 | +200% |
| 任务完成时间 | 20 分钟 | 15 分钟 | -25% |

#### 与 V3.0 战略的契合点
1. **可持续发展**：优化成本，支持长期使用
2. **数据驱动决策**：量化不同任务的成本效益
3. **风险分散**：避免单一模型的风险

---

### 边界问题 1：如何自动判断任务复杂度？

#### 复杂度评估方法

**任务复杂度 = 需求规模 + 技术难度 + 创新程度**

```python
def assess_complexity(prompt):
    """
    评估任务复杂度的简化方法
    """
    score = 0

    # 1. 需求规模
    if len(prompt) > 500: score += 3
    elif len(prompt) > 200: score += 2
    else: score += 1

    # 2. 技术难度
    if any(keyword in prompt for keyword in ["架构", "系统设计"]): score += 3
    elif any(keyword in prompt for keyword in ["重构", "性能"]): score += 2
    else: score += 1

    # 3. 创新程度
    if any(keyword in prompt for keyword in ["新功能", "全新"]): score += 3
    elif any(keyword in prompt for keyword in ["优化", "改进"]): score += 2
    else: score += 1

    return score

def select_ai_model(prompt, user_preference=None):
    complexity = assess_complexity(prompt)

    if user_preference:
        return user_preference

    if complexity <= 4:
        return "gpt-3.5-turbo"  # 低复杂度

    elif complexity <= 7:
        return "gpt-4"  # 中等复杂度

    else:
        return "claude-3.5-sonnet"  # 高复杂度
```

---

### 边界问题 2：用户是否可手动指定模型？

#### 权限控制策略

**应该允许，但需要引导**

```python
def handle_model_override(user_input, suggested_model):
    if user_specified_model := extract_model_from_input(user_input):
        # 用户明确指定了模型
        log_override(suggested_model, user_specified_model)
        return user_specified_model

    # 询问用户是否接受建议的模型
    if should_ask_confirmation():
        return ask_user_confirmation(suggested_model)

    return suggested_model
```

---

### 扩展点与风险

#### 阶段 1 (MVP，2026-Q2)
- 基础复杂度评估
- 固定模型分级
- 手动指定支持

#### 阶段 2 (P1，2026-Q3)
- 学习用户模式
- 模型性能监控
- 自动调整策略
- 与 014-文档阅读习惯引导集成：根据任务复杂度推荐模型

#### 风险与缓解
- 质量下降风险：需要建立反馈机制
- 实现复杂：分阶段实现，先简单后复杂

---

## ⚠️ 疑问

1. ❓ 如何自动判断任务复杂度?
2. ❓ 用户是否可手动指定模型?
3. ❓ 如何平衡质量与成本的关系?

---

**创建日期**: 2025-11-29
