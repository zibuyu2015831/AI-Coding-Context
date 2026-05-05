---
title: AI Rules 维护指南
summary: 指导维护者识别何时需要更新 AI Rules 文件、如何同步规则变更以及更新后的验证方式，确保 IDE 中的 AI 行为与框架规范持续一致。
keywords: ai-rules | maintenance | guide | rules | ide | aicc
scope: AI Rules 文件的维护与验证实践
related_files: 无
dependencies: AI_ENTRY_POINT.md | templates/AI_RULES_TEMPLATE.md | workflows/commit_guided_update.md
verified_at: 2026-05-05
---

# AI Rules 维护指南

> **版本**: v2.3  
> **创建日期**: 2025-11-28  
> **用途**: 指导开发者何时及如何维护 AI Rules 文件

---

## 📋 概述

AI Rules 文件(`dev_docs/rules/combined/AI_RULES.md`)是配置到 IDE 中让 AI 遵守的规则集。

本指南说明:

- 何时需要更新 Rules
- 如何更新 Rules
- 更新后如何验证

---

## 🕐 更新时机

### 必须更新（关键变更）⭐⭐⭐

以下情况**必须**立即更新 AI Rules:

#### 1. 架构重构

**场景示例**:

- 从单体应用迁移到微服务
- 从 MVC 迁移到 DDD 架构
- 引入新的架构层（如 CQRS）

**需要更新的 rules**:

- 架构概述部分
- 模块组织规范
- 依赖注入方式

**示例**:

```markdown
# 更新前

## 架构

单体应用，MVC 三层架构

# 更新后

## 架构

微服务架构，每个服务独立部署

- API Gateway: api-gateway/
- User Service: services/user/
- Order Service: services/order/
```

---

#### 2. 技术栈升级

**场景示例**:

- Vue 2 → Vue 3 (Composition API)
- React 16 → React 18 (Concurrent Features)
- Python 2 → Python 3 (语法变化)

**需要更新的 rules**:

- 组件编写规范
- API 使用方式
- 生命周期钩子

**示例**:

```markdown
# 更新前 (Vue 2)

## 组件定义

使用 Options API:
export default {
data() { return {...} },
methods: {...}
}

# 更新后 (Vue 3)

## 组件定义

优先使用 Composition API:

<script setup lang="ts">
import { ref, computed } from 'vue'
const count = ref(0)
</script>
```

---

#### 3. 新增核心模块

**场景示例**:

- 新增支付模块
- 新增权限系统
- 新增消息队列集成

**需要更新的 rules**:

- 模块清单
- 该模块的开发规范
- 相关 API 调用约定

**示例**:

````markdown
## 新增模块规范

### 支付模块 (新增 2025-11-28)

**位置**: `src/modules/payment/`

**规范**:

- 所有金额使用整数（分为单位）
- 支付回调必须验证签名
- 订单状态使用枚举类型

**示例**:

```python
# ✅ 正确
amount = 10000  # 100.00元
status = PaymentStatus.PENDING

# ❌ 错误
amount = 100.00  # 使用浮点数
status = "pending"  # 使用字符串
```

````

---

#### 4. 编码规范变更

**场景示例**:
- 采用新的命名规范
- 变更注释规范
- 变更文件组织方式

**需要更新的rules**:
- 命名约定章节
- 代码风格要求

**示例**:
```markdown
# 更新前
## 命名规范
组件文件: PascalCase (UserCard.vue)

# 更新后
## 命名规范
组件文件: kebab-case (user-card.vue)
- 理由: 与HTML标签保持一致
- 变更日期: 2025-11-28
````

---

### 建议更新（重要变更）⭐⭐

以下情况**建议**在方便时更新:

#### 1. 新功能上线（影响 > 3 个文件）

**场景**: 添加用户积分系统

**更新内容**:

```markdown
## 积分系统规范 (新增)

### 数据模型

- 用户积分: `user.points` (整数)
- 积分记录: `PointLog` 模型

### 业务规则

- 积分只能增加，不能直接减少
- 使用积分时创建冻结记录
- 积分有效期: 1 年
```

---

#### 2. 依赖项重大升级

**场景**: React 17 → 18, Django 3 → 4

**更新内容**:

- 新特性使用建议
- 废弃 API 的替代方案
- 破坏性变更说明

---

#### 3. API 设计变更

**场景**: RESTful → GraphQL

**更新内容**:

- API 调用方式
- 数据获取规范
- 错误处理机制

---

#### 4. 数据库 Schema 重大调整

**场景**: 用户表拆分、添加软删除

**更新内容**:

- 模型定义更新
- 查询规范调整
- 数据迁移注意事项

---

### 可选更新（次要变更）⭐

以下情况可以不更新或批量更新:

- 小 bug 修复（1-2 个文件）
- 文案调整
- 样式微调
- 配置参数调整

---

## 🔄 更新流程

### 方式 1: 让 AI 重新生成（推荐）⭐⭐⭐

**适用**: 大规模重构或多处变更

**步骤**:

```markdown
1. 发送给 AI:
```

请按照最新的项目代码，重新生成 dev_docs/rules/combined/AI_RULES.md

请注意以下重大变更：

- [变更 1]: Vue 2 升级到 Vue 3
- [变更2]: 新增支付模块
- [变更3]: API从RESTful改为GraphQL

```

2. AI会:
- 分析最新代码
- 检测框架和技术栈
- 重新生成完整Rules

3. 你需要:
- 审核生成的Rules
- 确认关键规范正确
- 复制到IDE配置
```

**优点**: 全面、准确  
**缺点**: 耗时较长（5-10 分钟）

---

### 方式 2: 手动增量更新

**适用**: 小范围更新，明确知道改动点

**步骤**:

```markdown
1. 打开 dev_docs/rules/combined/AI_RULES.md

2. 定位需要修改的 section
   例如: "## 组件开发规范"

3. 更新具体规则
   例如: 更新 Vue 3 Composition API 用法

4. 保持格式一致

   - 使用 ✅ ❌ 标记
   - 包含代码示例
   - 添加更新日期

5. 测试 AI 是否理解新规则
   - 让 AI 写一段新代码
   - 检查是否遵守新规范
```

**优点**: 快速、精准  
**缺点**: 可能遗漏相关部分

---

### 方式 3: 模块化更新（v2.2+）

**适用**: 独立规范变更

**步骤**:

```markdown
1. 更新独立 rule 文件
   例如: dev_docs/rules/core/api_design.md

2. 发送给 AI:
```

请更新 dev_docs/rules/core/api_design.md
新要求: 所有 API 改为 GraphQL

然后重新组合生成 dev_docs/rules/combined/AI_RULES.md

```

3. AI会:
- 更新指定的rule文件
- 重新组合生成combined版本
```

**优点**: 模块化、清晰  
**缺点**: 需要框架支持模块化 rules（v2.2+）

---

## ✅ 更新检查清单

更新完成后，必须检查以下内容:

### 内容检查

- [ ] **无冲突**: 新规则不与现有规则冲突
- [ ] **有示例**: 关键规则包含实际代码示例（不是占位符）
- [ ] **有标注**: 重要规则用加粗或 emoji 强调
- [ ] **有依据**: 规范有明确的理由说明

### 示例检查

````markdown
# ❌ 不好的规则（无示例）

## API 调用

所有 API 调用必须处理错误

# ✅ 好的规则（有示例）

## API 调用

所有 API 调用必须处理错误:

**✅ 正确**:

```javascript
try {
  const data = await api.getUser(id);
  return data;
} catch (error) {
  logger.error("获取用户失败", error);
  showErrorMessage("获取用户信息失败");
}
```
````

**❌ 错误**:

```javascript
const data = await api.getUser(id); // 未处理错误
return data;
```

````

### 格式检查

- [ ] **文件大小**: < 2000行（过大影响AI性能）
- [ ] **章节完整**: 所有章节有明确标题
- [ ] **代码块**: 所有代码块有语言标注
- [ ] **链接有效**: 所有内部链接可访问

### 功能检查

- [ ] **IDE配置**: 已复制到IDE的rules配置
- [ ] **AI理解**: 测试AI是否理解新规则
- [ ] **实际应用**: 让AI生成代码，检查是否符合新规范

---

## 🧪 更新验证

### 验证方法

**1. AI代码生成测试**

```markdown
测试1: 让AI生成一个新组件

发送给AI:
"请创建一个用户列表组件"

检查:
- [ ] 是否使用了新的组件定义方式（如Vue 3 Composition API）
- [ ] 是否遵守命名规范
- [ ] 是否包含错误处理
- [ ] 是否符合文件组织规范
````

**2. 规范一致性检查**

```markdown
测试 2: 让 AI 审查现有代码

发送给 AI:
"请审查 src/components/UserCard.vue 是否符合规范"

检查:

- [ ] AI 能否识别不符合规范的地方
- [ ] AI 的建议是否符合新规范
- [ ] AI 是否引用了正确的规范条目
```

**3. 边缘情况测试**

```markdown
测试 3: 测试复杂场景

发送给 AI:
"如何在 Vue 3 中实现一个带权限控制的表单组件？"

检查:

- [ ] AI 是否综合应用多条规范
- [ ] AI 是否提供符合规范的解决方案
- [ ] AI 是否主动说明规范依据
```

---

## 📅 维护周期建议

### 按项目活跃度

| 项目活跃度   | 检查频率 | 更新频率 | 说明                           |
| ------------ | -------- | -------- | ------------------------------ |
| **高频开发** | 每月     | 按需     | 活跃开发中，技术栈可能快速演进 |
| **中频开发** | 每季度   | 每季度   | 稳定开发，定期检查规范有效性   |
| **维护模式** | 每半年   | 年度     | 基本稳定，仅在重大变更时更新   |

### 定期检查事项

**月度检查** (高频项目):

- [ ] 新增的核心模块是否有规范
- [ ] 最近的技术债务是否需要规范化
- [ ] 团队是否有新的编码约定

**季度检查** (中频项目):

- [ ] 依赖包是否有重大更新
- [ ] 规范是否仍然有效
- [ ] 是否有过时的规范需要移除

**年度检查** (维护项目):

- [ ] 技术栈是否需要升级
- [ ] Rules 文件是否需要重构
- [ ] 是否有新的最佳实践

---

## 💡 最佳实践

### 1. 在重大变更后立即更新

**❌ 不好的做法**:

```
完成架构重构，但拖延1个月才更新Rules
→ 结果: AI继续按旧规范生成代码，需要大量手动修正
```

**✅ 好的做法**:

```
完成架构重构后，当天更新Rules
→ 结果: AI立即按新规范生成代码，减少返工
```

---

### 2. 记录更新原因

**在 Rules 文件头部维护变更日志**:

```markdown
# AI Rules - 变更日志

## v2.3 (2025-11-28)

**变更**:

- 升级到 Vue 3，更新组件定义规范
- 新增支付模块规范
- 统一错误处理方式

**原因**:

- 技术栈升级
- 业务扩展
- 代码质量提升

**影响**:

- 所有新组件必须使用 Composition API
- 支付相关代码必须遵守金额处理规范

## v2.2 (2025-11-27)

...
```

---

### 3. 保留变更历史

**使用 Git 管理 Rules 文件**:

```bash
# 每次更新时提交
git add dev_docs/rules/combined/AI_RULES.md
git commit -m "docs(rules): 更新Vue 3组件规范"

# 需要回滚时
git log dev_docs/rules/combined/AI_RULES.md
git checkout <commit-hash> -- dev_docs/rules/combined/AI_RULES.md
```

---

### 4. 定期审查有效性

**每季度审查**:

```markdown
检查清单:

- [ ] 哪些规范 3 个月内从未被引用？（可能需要删除）
- [ ] 哪些规范经常被违反？（可能需要调整）
- [ ] 哪些新的编码模式需要规范化？
- [ ] 团队成员对现有规范有什么反馈？
```

---

### 5. 移除过时规范

**示例**:

```markdown
# ❌ 应该删除的过时规范

## jQuery 使用规范

项目已迁移到 Vue 3，不再使用 jQuery

# ✅ 保留历史但标记废弃

## jQuery 使用规范 [已废弃 2025-11-28]

**注意**: 项目已迁移到 Vue 3，新代码请使用 Vue 组件
此规范仅供维护旧代码参考

详见: Vue 3 组件开发规范
```

---

## 🔗 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 了解 Rules 在整个框架中的角色
- [templates/AI_RULES_TEMPLATE.md](../templates/AI_RULES_TEMPLATE.md) - Rules 文件模板
- [core/update_triggers.md](../core/update_triggers.md) - 文档更新触发机制

---

## 📝 快速参考卡

### 更新决策树

```
遇到代码变更 → 是否影响架构/技术栈/核心模块？
  ├─ 是 → 必须立即更新Rules ⭐⭐⭐
  └─ 否 → 是否影响 > 3个文件？
       ├─ 是 → 建议更新Rules ⭐⭐
       └─ 否 → 可选更新，可批量处理 ⭐
```

### 更新方式选择

```
变更范围大、技术栈变化 → 方式1: AI重新生成
明确知道改动点 → 方式2: 手动增量更新
独立模块规范变更 → 方式3: 模块化更新
```

---

**版本**: v2.3  
**最后更新**: 2025-11-28  
**路径**: `guides/ai_rules_maintenance.md`
