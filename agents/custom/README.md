# Custom - 项目自定义 Agent

## 📋 概述

**Custom** 目录用于存放项目专属的自定义 Agent,满足框架标准角色无法覆盖的特定需求。

框架提供 22 个通用角色,但每个项目都有其独特性。通过自定义 Agent,您可以为项目量身定制专业的 AI 助手。

---

## 🎯 核心价值

### 为什么需要自定义 Agent?

框架提供的标准角色无法覆盖所有项目特定需求:

| 场景类型       | 示例               | 框架角色                | 自定义 Agent                 |
| -------------- | ------------------ | ----------------------- | ---------------------------- |
| **技术栈差异** | GraphQL vs RESTful | api_designer (RESTful)  | custom.graphql_designer ✅   |
| **框架差异**   | Svelte vs Vue      | vue3_expert             | custom.svelte_expert ✅      |
| **业务领域**   | 金融合规审查       | security_auditor (通用) | custom.finance_compliance ✅ |
| **项目特定**   | 项目特定编码规范   | code_reviewer (通用)    | custom.project_reviewer ✅   |

### 价值量化

- 从 **22 个通用场景** → **无限项目个性化场景**
- 用户满意度预计提升 **40-60%**
- 框架竞争力显著超越静态 Prompt 库

---

## 📁 目录说明

```
agents/custom/
├── README.md              # 本文档
├── _template.md           # 快速模板
├── graphql_designer.md    # 示例:GraphQL API设计师
├── tailwind_expert.md     # 示例:Tailwind CSS专家
└── finance_compliance.md  # 示例:金融合规审查员
```

**说明**:

- 框架是项目级 copy,每个项目的 `custom/` 都是该项目专属
- 无需 team 子目录,项目本身就是边界

---

## 🆔 ID 命名规范

### 格式

```
custom.{角色英文名}
```

### 示例

- `custom.graphql_designer` - GraphQL API 设计师
- `custom.tailwind_expert` - Tailwind CSS 专家
- `custom.finance_compliance` - 金融合规审查员
- `custom.project_code_reviewer` - 项目特定代码审查员

### 命名规则

- ✅ 使用小写字母和下划线
- ✅ 英文名称简洁明确
- ✅ 反映角色核心职责
- ❌ 避免与框架角色重名

---

## 🛠️ 创建方式

### 方式 1: AI 辅助创建 (推荐)

**触发命令**:

```
@workflow:创建自定义Agent
```

**AI 将引导您完成 5 个 Phase**:

1. **需求收集**: AI 询问角色职责、技术栈、输入输出等
2. **深度分析**: AI 自动查重、评估必要性、分析边界
3. **生成草稿**: AI 生成完整的角色文档
4. **迭代优化**: 根据您的反馈调整(最多 3 轮)
5. **保存注册**: 自动保存并更新索引

**优势**:

- ✅ 自动查重,避免重复
- ✅ 自动填充元数据
- ✅ 质量检查机制
- ✅ 成功率 >90%

---

### 方式 2: 手动创建

**步骤**:

1. 复制 `_template.md` 为新文件
2. 按照模板填写内容
3. 保存到 `custom/` 目录
4. 更新本 README 的索引

**AI 辅助检查**:

- AI 会检测到您手动创建的文件
- 自动提供质量检查报告
- 帮助您改进文档

---

## 📊 元数据规范

自定义 Agent 的元数据示例:

```markdown
<!-- AGENT_META_START -->

ID: custom.graphql_designer
名称: GraphQL API 设计师
类型: development
版本: v1.0
创建: 2025-12-01
更新: 2025-12-01
来源: user # 用户创建
改造状态: 已通用化
语言支持: 通用
标签: [GraphQL, API 设计, Schema]
依赖: [database_designer]
被依赖: []
可编辑性: editable # 用户完全控制

<!-- AGENT_META_END -->
```

**关键字段**:

- `来源: user` - 标识为用户创建
- `可编辑性: editable` - 用户完全控制,可任意修改

---

## 📚 自定义 Agent 索引

### 当前项目自定义 Agent

> 暂无自定义 Agent,使用 `@workflow:创建自定义Agent` 创建第一个!

---

## 💡 最佳实践

### 1. 何时创建自定义 Agent?

✅ **推荐创建**:

- 框架角色无法满足项目特定需求
- 需要项目特定的编码规范或业务规则
- 使用框架未覆盖的技术栈或工具

❌ **不推荐创建**:

- 框架已有类似角色,只需微调
- 一次性需求,不值得创建角色
- 可以通过自然语言描述解决

### 2. 如何设计高质量的自定义 Agent?

**职责明确**:

- 单一职责原则
- 避免与现有角色重叠

**输入输出清晰**:

- 明确需要哪些输入
- 明确应该输出什么

**提供示例**:

- 至少 1 个快速示例
- 示例真实可用

**定义评估标准**:

- 不少于 3 条评估标准
- 标准具体可验证

### 3. 维护建议

**定期审查**:

- 检查是否还在使用
- 评估是否需要更新

**版本管理**:

- 重大变更时更新版本号
- 记录变更历史

**团队协作**:

- 与团队成员分享
- 收集使用反馈

---

## 🔗 相关文档

- [AI 角色库总览](../README.md)
- [自定义 Agent 模板](./_template.md)
- [AI 辅助创建工作流](../workflows/create_custom_agent_workflow.md)
- [Personas 人格型 Agent](../personas/README.md)

---

## 🆘 常见问题

### Q: 自定义 Agent 和框架角色有什么区别?

**A**:

- **框架角色**: 通用、稳定、locked/customizable,由框架维护
- **自定义 Agent**: 项目专属、editable,由用户完全控制

### Q: 可以修改框架角色吗?

**A**:

- **runtime 角色** (locked): 不可修改,保证框架稳定性
- **development/language_specific 角色** (customizable): 可基于此创建自定义版本
- **custom 角色** (editable): 完全可修改

### Q: 自定义 Agent 会影响其他项目吗?

**A**: 不会。框架是项目级 copy,每个项目的 `custom/` 目录独立。

### Q: 如何删除不再使用的自定义 Agent?

**A**:

1. 删除对应的 `.md` 文件
2. 从本 README 的索引中移除
3. 检查是否有其他角色依赖它

---

**版本**: v1.0  
**最后更新**: 2025-12-01
