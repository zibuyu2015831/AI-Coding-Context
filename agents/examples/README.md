# AI 角色示例库 (Agent Examples Library)

**版本**: v1.0  
**创建**: 2025-11-29  
**目的**: 集中管理所有 AI 角色的详细使用示例

---

## 📋 简介

本目录集中存放所有 AI 角色的详细使用示例，保持角色定义文件简洁的同时，为用户提供充分的参考资料。

**设计优势**:

- ✅ **Token 高效**: 角色定义简洁，示例按需加载（节省 60-70% Token）
- ✅ **易于维护**: 示例集中管理，更新不影响角色定义
- ✅ **用户友好**: 明确告知何时需要参考，降低认知负荷

---

## 📁 命名规范

示例文档统一采用以下命名格式：

```
[角色名]_examples.md
```

**示例**:

- `plan_reviewer_examples.md` - 方案审查员示例
- `code_reviewer_examples.md` - 代码审查员示例
- `vue3_expert_examples.md` - Vue 3 专家示例

---

## 📝 示例文档模板

创建新的示例文档时，请遵循以下结构：

````markdown
# [角色名] 角色使用示例

**角色**: [角色中文名]  
**文档**: [角色定义链接](../runtime/角色名.md)

---

## 📋 目录

- [示例 1: 场景描述](#示例1)
- [示例 2: 场景描述](#示例2)
- [示例 3: 场景描述](#示例3)

---

## 示例 1: [场景名称]

### 场景说明

[简要说明这个示例的应用场景]

### 用户输入

\```[语言]
[具体的输入代码或内容]
\```

### 角色响应

\```[语言]
[具体的输出代码或内容]
\```

### 关键点说明

- ✅ [关键点 1]
- ✅ [关键点 2]
- ✅ [关键点 3]

---

## 示例 2: [场景名称]

...

---

## 📝 使用建议

1. **首次使用**: 建议先查看示例 1 和示例 2
2. **特定场景**: 根据实际需求选择对应示例
3. **自定义扩展**: 可以基于示例调整
````

---

## 📚 示例索引

### Runtime 角色示例

| 角色         | 示例文档                                                                 | 状态      |
| ------------ | ------------------------------------------------------------------------ | --------- |
| 方案审查员   | [plan_reviewer_examples.md](./plan_reviewer_examples.md)                 | ✅ 已完成 |
| 代码审查员   | [code_reviewer_examples.md](./code_reviewer_examples.md)                 | ✅ 已完成 |
| 测试工程师   | [test_engineer_examples.md](./test_engineer_examples.md)                 | ✅ 已完成 |
| 性能优化专家 | [performance_optimizer_examples.md](./performance_optimizer_examples.md) | ✅ 已完成 |
| 安全审计员   | [security_auditor_examples.md](./security_auditor_examples.md)           | ✅ 已完成 |

### Development 角色示例

| 角色         | 示例文档                                                               | 状态      |
| ------------ | ---------------------------------------------------------------------- | --------- |
| 架构分析师   | [architecture_analyst_examples.md](./architecture_analyst_examples.md) | ✅ 已完成 |
| 数据库设计师 | [database_designer_examples.md](./database_designer_examples.md)       | ✅ 已完成 |
| API 设计师   | [api_designer_examples.md](./api_designer_examples.md)                 | ✅ 已完成 |

### Base 角色示例

| 角色       | 示例文档                                                         | 状态        |
| ---------- | ---------------------------------------------------------------- | ----------- |
| 前端工程师 | [frontend_engineer_examples.md](./frontend_engineer_examples.md) | ✅ 已完成 |
| 后端工程师 | [backend_engineer_examples.md](./backend_engineer_examples.md)   | ✅ 已完成   |

### Language Expert 角色示例

| 角色            | 示例文档                                                         | 状态      |
| --------------- | ---------------------------------------------------------------- | --------- |
| Java 专家       | [java_expert_examples.md](./java_expert_examples.md)             | ✅ 已完成 |
| Python 专家     | [python_expert_examples.md](./python_expert_examples.md)         | ✅ 已完成 |
| TypeScript 专家 | [typescript_expert_examples.md](./typescript_expert_examples.md) | ✅ 已完成 |

### 其他 Language Specific 角色示例

| 角色             | 示例文档                                                           | 状态      |
| ---------------- | ------------------------------------------------------------------ | --------- |
| Vue 3 专家       | [vue3_expert_examples.md](./vue3_expert_examples.md)               | ✅ 已完成 |
| Vue 3 状态管理师 | [vue3_state_manager_examples.md](./vue3_state_manager_examples.md) | ✅ 已完成 |

---

## ✍️ 编写示例指南

### 1. 选择典型场景

选择 2-3 个最具代表性的使用场景，覆盖：

- ✅ 最常见的用例（80%用户会遇到）
- ✅ 中等复杂度的场景
- ✅ 一个稍复杂的高级场景（可选）

### 2. 提供真实示例

- ✅ 使用真实的代码片段（非伪代码）
- ✅ 输入输出完整可运行
- ✅ 注释关键点说明

### 3. 标注关键点

每个示例后添加"关键点说明"：

- ✅ 角色的专业判断体现在哪里
- ✅ 输出的哪些部分最有价值
- ✅ 用户应该注意什么

### 4. 何时参考说明

在示例文档开头明确说明：

- 📌 首次使用此角色时
- 📌 不确定输出格式时
- 📌 需要了解最佳实践时

---

## 🔗 与角色定义的配合

角色定义文件（如 `runtime/plan_reviewer.md`）应包含以下章节链接到示例：

```markdown
## 📚 参考示例

**何时参考**:

- 首次使用此角色时，建议查看示例了解输出格式
- 不确定如何组织输出时

**示例文档**: [plan_reviewer_examples.md](../examples/plan_reviewer_examples.md)

**快速示例**: 输入技术方案文档 → 输出结构化的审查报告（包含问题清单、改进建议、风险评估）
```

---

## 📊 当前状态

**示例覆盖率**: 10/10 (100%) ✅

**已完成示例**:

- ✅ plan_reviewer_examples.md
- ✅ code_reviewer_examples.md
- ✅ test_engineer_examples.md
- ✅ performance_optimizer_examples.md
- ✅ security_auditor_examples.md
- ✅ architecture_analyst_examples.md
- ✅ database_designer_examples.md
- ✅ api_designer_examples.md
- ✅ vue3_expert_examples.md
- ✅ vue3_state_manager_examples.md
- ✅ backend_engineer_examples.md
- ✅ java_expert_examples.md
- ✅ python_expert_examples.md
- ✅ typescript_expert_examples.md

---

**维护者**: AI Coding Context Framework Team  
**反馈渠道**: 项目 Issues
