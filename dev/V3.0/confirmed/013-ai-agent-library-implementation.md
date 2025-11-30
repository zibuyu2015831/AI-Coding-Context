# 013 - AI 角色库实施方案

**优先级**: P0 ⭐ (基础设施)  
**状态**: 🟢 已确认  
**确认日期**: 2025-11-29  
**预估工作量**: 8-12 天  
**来源**: 用户洞察 + ai-coding-prompt-java-main 项目分析

---

## 📋 执行摘要

本方案是基于以下两份文档的综合实施指南：

1. `dev/V3.0/pending/013-ai-agent-library.md` - 需求定义和讨论结果
2. `AI_AGENT_LIBRARY_ABSORPTION_PLAN.md` - 参考项目分析和吸收方案

**核心目标**: 建立标准化的专业 AI 角色定义库，支持框架运行时和用户开发时双重用途

**关键成果**:

- ✅ 解答了全部 10 个核心疑问
- ✅ 基于成熟项目（AI 编码率 89.2%）制定吸收策略
- ✅ 明确了 22 个初始角色和实施优先级
- ✅ 建立了完整的质量保证机制

---

## 🎯 第一部分：讨论结果汇总

### 1.1 核心设计决策

#### 决策 1: 角色粒度 - 三级粒度模型

```
分类层 (runtime/development/language_specific)
  └── 角色层 (如 plan_reviewer, code_reviewer)
      └── 清单层 (功能完整性检查、技术方案符合性检查...)
```

**初始角色数量**:

- P0: 10 个（核心场景）
- P1: 8 个（扩展场景）
- P2: 4 个（特殊场景）
- **总计**: 22 个（与参考项目一致，经过验证）

#### 决策 2: 角色调用机制 - 三种方式并存

| 调用方式       | 场景                        | 用户体验                |
| -------------- | --------------------------- | ----------------------- |
| **IDE 集成**   | 复制到 AI IDE 的 agent 配置 | 最佳，利用 IDE 原生功能 |
| **框架 Rules** | AI 主动提示可用角色         | 智能，降低认知负荷      |
| **自然语言**   | "请使用 xxx 角色"           | 最灵活，无需特殊语法    |

#### 决策 3: 角色元数据

**V3.1 核心字段示例** (13 个字段):

```markdown
<!-- AGENT_META_START -->

ID: runtime.plan_reviewer # 1. 必需 - 唯一标识符 {类型}.{英文名}
名称: 方案审查员 # 2. 必需 - 中文名称
类型: runtime # 3. 必需 - runtime/development/language_specific
版本: v1.0 # 4. 必需 - 版本号
创建: 2025-11-29 # 5. 必需 - 创建日期 YYYY-MM-DD
更新: 2025-11-29 # 6. 必需 - 最后更新日期 YYYY-MM-DD
来源: 框架内置 # 7. 推荐 - 参考来源/统一为框架内置，以后可能扩展为社区或用户自定义
改造状态: 已通用化 # 8. 推荐 - 已通用化/待改造
语言支持: 通用 # 9. 推荐 - 通用/TypeScript/Python 等
标签: [审查, 方案, 质量保证] # 10. 可选 - 标签列表
依赖: [] # 11. 推荐 - 依赖的其他角色 ID 列表
被依赖: [001-ai-mutual-review] # 12. 推荐 - 被哪些功能/角色依赖
可编辑性: locked # 13. 是否可编辑 - locked/customizable/editable

<!-- AGENT_META_END -->
```

**完整字段说明表**:

| 序号 | 字段            | 必需性 | 说明           | 可选值                                    | V3.0 |
| ---- | --------------- | ------ | -------------- | ----------------------------------------- | ---- |
| 1    | **ID**          | 必需   | 唯一标识符     | `{类型}.{英文名}`                         | ✅   |
| 2    | **名称**        | 必需   | 中文名称       | -                                         | ✅   |
| 3    | **类型**        | 必需   | 角色分类       | runtime / development / language_specific | ✅   |
| 4    | **版本**        | 必需   | 版本号         | v1.0, v1.1, ...                           | ✅   |
| 5    | **创建**        | 必需   | 创建日期       | YYYY-MM-DD                                | ✅   |
| 6    | **更新**        | 必需   | 最后更新日期   | YYYY-MM-DD                                | ✅   |
| 7    | **来源**        | 推荐   | 参考来源       | 框架内置 / user (自定义角色)              | ✅   |
| 8    | **改造状态**    | 推荐   | 通用化状态     | 已通用化 / 待改造                         | ✅   |
| 9    | **语言支持**    | 推荐   | 语言适用性     | 通用 / TypeScript / Python / ...          | ✅   |
| 10   | **标签**        | 可选   | 标签列表       | [标签 1, 标签 2, ...]                     | ✅   |
| 11   | **依赖**        | 推荐   | 依赖的其他角色 | [角色 ID 列表]                            | ✅   |
| 12   | **被依赖**      | 推荐   | 被哪些功能依赖 | [功能/角色列表]                           | ✅   |
| 13   | **可编辑性** 🆕 | V3.1+  | 是否可编辑     | locked / customizable / editable          | 🔮   |

**"可编辑性"字段说明** 🆕:

| 取值             | 含义           | 适用角色                      | 说明                    |
| ---------------- | -------------- | ----------------------------- | ----------------------- |
| **locked**       | 锁定,不可编辑  | runtime 角色                  | 框架核心角色,保护稳定性 |
| **customizable** | 可作为基础定制 | development/language_specific | 可基于此创建自定义版本  |
| **editable**     | 完全可编辑     | custom 自定义角色             | 用户完全控制,可任意修改 |

**注意**:

- V3.0 实现前 12 个字段
- "可编辑性"为 V3.1+自定义 Agent 功能预留

#### 决策 4: 质量保证 - 5 级机制

1. **改造检查清单** - 格式/内容/质量三维检查
2. **角色自评估标准** - 每个角色定义输出质量标准
3. **三级评审流程** - 自检 → 同行评审 → 实战验证
4. **版本管理和迭代** - v1.0 → v1.1 → v1.2
5. **使用反馈机制** - 调用次数、评分、改进建议

#### 决策 5: 语言特定性 - "通用基础 + 语言增强"

```
language_specific/
├── base/                    # 通用基础角色
│   ├── backend_engineer.md
│   └── frontend_engineer.md
├── typescript/               # TypeScript专属
│   ├── extends: _base/frontend_engineer.md
│   └── vue3_expert.md
└── python/                   # Python专属
    ├── extends: _base/backend_engineer.md
    └── django_expert.md
```

#### 决策 6: 更新机制 - 框架作者主导

```
更新流程: 用户反馈 → 框架作者评估 → 角色更新 → 框架版本发布

- 角色定义稳定，用户可微调但不推荐自定义
- 框架作者负责角色更新，保证质量和一致性
- 通过版本号追踪演进
```

#### 决策 7: Token 消耗 - 按需加载，影响可控

| 项目              | Token 消耗          | 评估   |
| ----------------- | ------------------- | ------ |
| 单个角色定义      | ~1,200 tokens       | 可接受 |
| 角色清单（22 个） | ~1,500 tokens       | 可接受 |
| 对比：主文档      | ~5,000-8,000 tokens | 参考   |

**结论**: Token 消耗不大，ROI 高

#### 决策 8: 测试验证 - 信任大模型 + 用户反馈

```
质量保障: 信任大模型能力 + 用户反馈迭代
暂不建立: 自动化测试、A/B测试、量化指标体系（成本高，ROI低）
```

### 1.2 初始角色集规划

#### P0 优先级（10 个，必须实现）

**运行时角色** (runtime/)

1. **plan_reviewer** - 方案审查员 ← 支持 001 (AI 互审)
2. **code_reviewer** - 代码审查员
3. **test_engineer** - 测试工程师
4. **performance_optimizer** - 性能优化专家
5. **security_auditor** - 安全审计员

**开发时角色** (development/) 6. **architecture_analyst** - 架构分析师 7. **database_designer** - 数据库设计师 8. **api_designer** - API 设计师

**语言专属角色** (language_specific/) 9. **vue3_expert** - Vue 3 专家 10. **vue3_state_manager** - Vue 3 状态管理师

#### P1 优先级（8 个，推荐实现）

11. doc_fixer - 文档修复助手 ← 支持 011
12. summary_generator - 摘要生成助手 ← 支持 012
13. business_logic_engineer - 业务逻辑工程师
14. api_implementer - API 实现工程师
15. frontend_api_manager - 前端 API 管理师
16. project_scaffold_generator - 项目脚手架生成器
17. cross_platform_expert - 跨端适配专家
18. refactoring_expert - 重构专家

#### P2 优先级（4 个，可选实现）

19. data_persistence_engineer - 持久化工程师
20. microservice_dependency_manager - 微服务依赖管理师
21. api_doc_generator - API 文档生成器
22. mobile_component_engineer - 移动端组件工程师

### 1.3 参考项目分析总结

**项目**: ai-coding-prompt-java-main

- **成果**: AI 编码率从 9.6%提升至 89.2%
- **架构**: 8 层 22+角色
- **特点**: 统一的 prompt 模板结构
- **许可**: MIT 许可证，可合法借鉴

**6 大优秀设计模式**:

1. 角色身份明确化 ⭐⭐⭐⭐⭐
2. 检查清单化 ⭐⭐⭐⭐⭐
3. 代码模板提供 ⭐⭐⭐⭐
4. 输入输出明确化 ⭐⭐⭐⭐⭐
5. 质量检查清单 ⭐⭐⭐⭐⭐
6. 分层架构映射 ⭐⭐⭐⭐

### 1.4 角色文件映射表 ⭐

**说明**: 以下表格记录了我们规划的每个角色在 ai-coding-prompt 项目中的对应文件位置，**强烈建议**在创建角色时先参考对应文件。

**注意**: ai-coding-prompt 项目中部分角色带有 Java 语言背景，在参考时需要去除，将之通用化。

#### P0 运行时角色映射

| 我们的角色                                  | 参考文件位置                                                                                     | 改造重点                                            |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| **plan_reviewer**<br>(方案审查员)           | `other_project/ai-coding-prompt-java-main/`<br>`rules/Review需求实现检查prompt.md`               | ✅ 直接可用<br>⚠️ 去 Java 特定术语<br>⚠️ 添加元数据 |
| **code_reviewer**<br>(代码审查员)           | `other_project/ai-coding-prompt-java-main/`<br>`rules/Review需求实现检查prompt.md`<br>(部分内容) | ✅ 提取代码质量检查部分<br>⚠️ 通用化编码规范        |
| **test_engineer**<br>(测试工程师)           | `other_project/ai-coding-prompt-java-main/`<br>`rules/测试用例生成prompt.md`                     | ✅ 高度可用<br>⚠️ 支持多种测试框架                  |
| **performance_optimizer**<br>(性能优化专家) | `other_project/ai-coding-prompt-java-main/`<br>`rules/性能优化prompt.md`                         | ✅ 可用<br>⚠️ 去 Java 特定优化手段                  |
| **security_auditor**<br>(安全审计员)        | `other_project/ai-coding-prompt-java-main/`<br>`rules/安全检查prompt.md`                         | ✅ 可用<br>⚠️ 通用化安全检查项                      |

#### P0 开发时角色映射

| 我们的角色                               | 参考文件位置                                                                  | 改造重点                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **architecture_analyst**<br>(架构分析师) | `other_project/ai-coding-prompt-java-main/`<br>`技术方案/新增类需求prompt.md` | ✅ 高度可用<br>⚠️ 去 Spring Boot 架构特定内容<br>⚠️ 支持多种架构模式 |
| **database_designer**<br>(数据库设计师)  | `other_project/ai-coding-prompt-java-main/`<br>`数据层/建表prompt.md`         | ✅ 可用<br>⚠️ 支持多种数据库<br>⚠️ 去 MySQL 特定语法                 |
| **api_designer**<br>(API 设计师)         | `other_project/ai-coding-prompt-java-main/`<br>`应用层/接口定义prompt.md`     | ✅ 可用<br>⚠️ 保持 RESTful 通用性                                    |

#### P0 语言专属角色映射

| 我们的角色                                   | 参考文件位置                                                                | 改造重点                                                        |
| -------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **vue3_expert**<br>(Vue 3 专家)              | `other_project/ai-coding-prompt-java-main/`<br>`前端/前端组件开发prompt.md` | ✅ 直接可用<br>✅ 已经是 Vue 3 Composition API<br>⚠️ 添加元数据 |
| **vue3_state_manager**<br>(Vue 3 状态管理师) | `other_project/ai-coding-prompt-java-main/`<br>`前端/前端状态管理prompt.md` | ✅ 直接可用<br>✅ 已经是 Pinia<br>⚠️ 添加元数据                 |

#### P1 角色映射（按需参考）

| 我们的角色                                           | 参考文件位置                                                                  | 改造重点                                                   |
| ---------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **doc_fixer**<br>(文档修复助手)                      | ❌ 无对应文件<br>需要新创建                                                   | 🆕 新创建<br>参考 review 需求检查模式                      |
| **summary_generator**<br>(摘要生成助手)              | ❌ 无对应文件<br>需要新创建                                                   | 🆕 新创建<br>参考文档规范                                  |
| **business_logic_engineer**<br>(业务逻辑工程师)      | `other_project/ai-coding-prompt-java-main/`<br>`业务层/业务层prompt.md`       | ✅ 可用<br>⚠️ 去 DDD Java 特定实现<br>⚠️ 保留 DDD 通用原则 |
| **api_implementer**<br>(API 实现工程师)              | `other_project/ai-coding-prompt-java-main/`<br>`应用层/接口实现prompt.md`     | ✅ 可用<br>⚠️ 去 Spring Boot 注解<br>⚠️ 通用化控制器模式   |
| **frontend_api_manager**<br>(前端 API 管理师)        | `other_project/ai-coding-prompt-java-main/`<br>`前端/前端API服务prompt.md`    | ✅ 高度可用<br>✅ 已经是 Axios<br>⚠️ 添加元数据            |
| **project_scaffold_generator**<br>(项目脚手架生成器) | `other_project/ai-coding-prompt-java-main/`<br>`工程结构/工程结构prompt.md`   | ✅ 可用<br>⚠️ 去 Java 项目结构<br>⚠️ 支持多语言脚手架      |
| **cross_platform_expert**<br>(跨端适配专家)          | `other_project/ai-coding-prompt-java-main/`<br>`移动端/跨端适配prompt.md`     | ✅ 高度可用<br>✅ 已经是 uni-app<br>⚠️ 添加元数据          |
| **refactoring_expert**<br>(重构专家)                 | `other_project/ai-coding-prompt-java-main/`<br>`技术方案/修改类需求prompt.md` | ✅ 可用<br>⚠️ 通用化重构策略                               |

**映射表使用说明**:

- ✅ = 高度可用，改造工作量小
- ⚠️ = 需要注意的改造点
- ❌ = 无对应文件，需新创建
- 🆕 = 全新创建的角色

### 1.5 优秀设计模式详解 ⭐

基于对 ai-coding-prompt 项目的分析，识别出以下 6 个优秀设计模式，**必须**在我们的角色定义中复用。

#### 模式 1: 角色身份明确化 ⭐⭐⭐⭐⭐

**原理**: 通过明确的"你是 xxx 专家"身份定义，赋予 AI 专业视角和标准

**参考示例** (来自`Review需求实现检查prompt.md`):

```markdown
## 角色定义

你是一位经验丰富的代码审查专家，专注于检查 AI 生成的代码是否符合
需求规格和技术方案要求。
```

**吸收要点**:

- ✅ 使用"你是一位经验丰富的 xxx 专家"模板
- ✅ 明确专注领域，限定职责范围
- ✅ 设定专业身份，避免通用 AI 视角

**我们的标准格式**:

```markdown
## 🎯 角色设定 (System Prompt)

### 身份定义

你是一位经验丰富的[专业领域]专家，专注于[核心职责]。
你的核心职责是[具体职责描述]。
```

#### 模式 2: 检查清单化 ⭐⭐⭐⭐⭐

**原理**: 使用结构化的 checkbox 清单，确保审查/检查的完整性

**参考示例** (来自`Review需求实现检查prompt.md`):

```markdown
## 检查清单

### 1. 功能完整性检查

- [ ] 是否实现了需求规格中所有列出的功能点
- [ ] 每个功能点的业务逻辑是否正确
- [ ] 异常场景和边界条件是否处理

### 2. 技术方案符合性检查

- [ ] 是否按照技术方案中的架构设计实现
- [ ] 模块划分是否符合设计原则
      ...
```

**吸收要点**:

- ✅ 使用`- [ ]` checkbox 格式
- ✅ 分类清晰（功能/技术/质量/安全）
- ✅ 每项可独立验证

**我们的标准格式**:

```markdown
## 📊 评估标准

评估[角色名]输出质量的标准:

### [维度 1]: [名称]

- [ ] [具体检查项 1]
- [ ] [具体检查项 2]

### [维度 2]: [名称]

- [ ] [具体检查项 1]
      ...
```

#### 模式 3: 代码模板提供 ⭐⭐⭐⭐

**原理**: 提供具体的代码框架，降低 AI 理解成本，确保输出格式统一

**参考示例** (来自`业务层prompt.md`):

```java
/**
 * [领域服务名称] - [业务功能描述]
 *
 * 业务规则:
 * 1. [规则1描述]
 */
@DomainService
public class [业务领域]Service {
    // 实现细节
}
```

**吸收要点**:

- ✅ 提供完整的代码框架
- ✅ 包含注释说明的最佳实践
- ✅ 使用占位符`[xxx]`标注可替换部分

**我们的改造**:

- ⚠️ 去除语言特定的语法（如 Java 注解）
- ✅ 使用伪代码或通用描述
- ✅ 提供多语言示例（可选）

**我们的标准格式**:

```markdown
### 输出规范

**[输出类型]格式**:
\`\`\`[语言/伪代码]
[模板内容，使用[占位符]标注]
\`\`\`

**多语言参考**:

- TypeScript: [简要说明]
- Python: [简要说明]
```

#### 模式 4: 输入输出明确化 ⭐⭐⭐⭐⭐

**原理**: 明确告知 AI 需要哪些输入，应该输出什么

**参考示例** (来自`业务层prompt.md`):

```markdown
## 输入要求

1. 技术方案文档中的领域服务功能描述
2. 数据模型定义
3. 业务规则和约束条件

## 输出要求

1. 完整的业务逻辑层代码
2. 符合 DDD 设计原则的领域模型
3. 包含详细业务注释的代码
```

**吸收要点**:

- ✅ 输入输出分别列举要求
- ✅ 具体、可验证
- ✅ 降低沟通成本

**我们的标准格式**:

```markdown
## 💡 输入要求

1. [具体的输入项 1]
2. [具体的输入项 2]
3. [具体的输入项 3]

## 📤 输出要求

1. [具体的输出项 1]
2. [具体的输出项 2]
   - 子项或细节说明
3. [具体的输出项 3]

## 📚 参考示例

**何时参考**:

- [场景 1：任务较复杂，你需要更清晰的理解时]
- [场景 2：不确定输出格式时]

**示例文档**: [角色名\_examples.md](../examples/角色名_examples.md)

**快速示例**: [一句话说明典型的输入和输出]
```

**设计优势**:

- ✅ **Token 高效**: 角色定义简洁，示例按需加载（节省 60-70% Token）
- ✅ **易于维护**: 示例集中在 examples/目录，更新不影响角色定义
- ✅ **用户友好**: 明确告知何时需要参考，降低认知负荷

#### 模式 5: 质量检查清单 ⭐⭐⭐⭐⭐

**原理**: 角色自带质量检查项，确保输出质量

**参考示例** (来自`业务层prompt.md`):

```markdown
## 质量检查

- [ ] 所有业务规则都在领域层实现
- [ ] 代码符合单一职责原则
- [ ] 领域模型表达业务概念清晰
- [ ] 业务逻辑可测试性强
```

**吸收要点**:

- ✅ 作为角色输出的自检机制
- ✅ 可作为人工审查参考
- ✅ 确保质量标准明确

**我们的标准格式**:

```markdown
## 📊 评估标准

评估[角色名]输出质量的标准:

- [ ] [质量标准 1]
- [ ] [质量标准 2]
- [ ] [质量标准 3]
      ...
```

#### 模式 6: 分层架构映射 ⭐⭐⭐⭐

**原理**: 角色与开发流程/架构层次对应，职责清晰

**参考项目的架构映射**:

```
规则层 (Rules) → 质量保障角色
  ├── Review需求实现检查 → plan_reviewer/code_reviewer
  ├── 测试用例生成 → test_engineer
  ├── 性能优化 → performance_optimizer
  └── 安全检查 → security_auditor

业务层 (Business) → 业务逻辑角色
  └── 业务层prompt → business_logic_engineer

应用层 (Application) → 接口角色
  ├── 接口定义 → api_designer
  ├── 接口实现 → api_implementer
  └── 接口文档 → api_doc_generator

技术方案层 (Technical) → 设计角色
  ├── 新增类需求 → architecture_analyst
  └── 修改类需求 → refactoring_expert

数据层 (Data) → 数据角色
  ├── 建表 → database_designer
  ├── 持久化 → data_persistence_engineer
  └── 服务依赖 → microservice_dependency_manager
```

**吸收要点**:

- ✅ 角色职责与实际工作对应
- ✅ 避免职责重叠
- ✅ 保持单一职责原则

**我们的分类**:

```
runtime/ → 框架运行时角色（自动调用）
development/ → 开发时角色（通用能力）
language_specific/ → 语言专属角色（特定技术栈）
workflows/ → 协作流程（多角色编排）
```

---

## 🛠️ 第二部分：实施流程和具体步骤

### 阶段 1: 基础设施建设（2-3 天）✅ **已完成**

**完成情况**:

- ✅ agents/目录结构已创建并核查
- ✅ agent_template.md 已创建
- ✅ quality_checklist.md 已创建
- ✅ agents/README.md 已创建
- ✅ examples/README.md 已创建
- ✅ \_progress/目录已创建

**⚠️ 需要调整** (基于新增的元数据字段):

- [ ] 更新 agent_template.md: 增加"可编辑性"字段
- [ ] 确认"来源"字段统一为`框架内置`

---

#### 步骤 1.1: 创建目录结构 ✅ **已完成**

**注意**: 【该项已由用户手动完成】

```bash
agents/                        # 🆕 AI角色库
    ├── README.md                     # 角色库索引和使用指南
    ├── _templates/                   # 角色模板
    │   └── agent_template.md
    ├── runtime/                      # 框架运行时角色
    ├── development/                  # 开发时角色（通用）
    ├── language_specific/            # 语言专属角色
    │   ├── base/                    # 通用基础
    │   ├── typescript/
    │   ├── python/
    │   └── java/
    ├── workflows/                    # 协作流程模板
    │   ├── new_feature_workflow.md
    │   ├── bug_fix_workflow.md
    │   └── refactoring_workflow.md
    └── examples/                     # 🆕 示例库（集中管理）
        ├── README.md                 # 示例库索引和使用指南
        └── [角色名]_examples.md      # 各角色的详细示例
    ├── personas/                     # 🆕 V3.1+ 人格型Agent
    │   ├── README.md
    │   ├── linus_torvalds.md        # Linux创始人人格
    │   ├── martin_fowler.md         # 重构大师人格
    │   ├── uncle_bob.md             # 整洁代码倡导者人格
    └── custom/                       # 🆕 V3.1+ 项目自定义角色
        ├── README.md                # 项目级自定义说明
        ├── _template.md             # 快速模板
        └── (用户创建的角色文件)
```

**验收标准**:

- [ ] 所有目录创建完成
- [ ] 目录结构符合设计
- [ ] README.md 框架已建立

#### 步骤 1.2: 创建角色模板

**文件**: `agents/_templates/agent_template.md`

**模板内容**:

```markdown
# 角色名称 (Agent Name)

<!-- AGENT_META_START -->

ID: [类型].[英文名称]
名称: [中文名称]
类型: [runtime/development/language_specific]
版本: v1.0
创建: [日期]
更新: [日期]
来源: 框架内置 # 🔄 统一为"框架内置"
改造状态: [已通用化/待改造]
语言支持: [通用/特定语言]
标签: [标签列表]
依赖: []
被依赖: []
可编辑性: [locked/customizable/editable] # 🆕 新增字段

<!-- AGENT_META_END -->

---

## 📋 角色概述

> **📌 快速说明**
>
> - **职责**: [一句话职责]
> - **适用场景**: [2-3 个典型场景]
> - **专长领域**: [3-5 个专长]
> - **协作角色**: [相关角色]

---

## 🎯 角色设定 (System Prompt)

### 身份定义

[详细的角色身份定义]

### 行为准则

**✅ 你应该**:

1. [行为规范 1]
2. [行为规范 2]

**❌ 你不应该**:

1. [禁止行为 1]
2. [禁止行为 2]

### 输出规范

[格式要求和质量标准]

---

## � 输入要求

1. [输入项 1]
2. [输入项 2]
3. [输入项 3]

## 📤 输出要求

1. [输出项 1]
2. [输出项 2]
3. [输出项 3]

## 📚 参考示例

**何时参考**:

- 首次使用此角色时，建议查看示例了解输出格式
- 不确定如何组织输出时

**示例文档**: [角色名\_examples.md](../examples/角色名_examples.md)

**快速示例**: [一句话说明输入输出]

---

## 🔗 协作角色

- **上游角色**: [角色](./xxx.md) - 说明
- **下游角色**: [角色](./xxx.md) - 说明
- **配合角色**: [角色](./xxx.md) - 说明

---

## 📊 评估标准

评估角色输出质量的标准:

- [ ] [评估标准 1]
- [ ] [评估标准 2]
```

**验收标准**:

- [ ] 模板文件创建完成
- [ ] 包含所有必要章节
- [ ] 格式规范，可直接复用

#### 步骤 1.3: 创建改造检查清单

**文件**: `agents/_templates/quality_checklist.md`

**内容**: 参考吸收方案中的检查清单

**验收标准**:

- [ ] 检查清单文件创建
- [ ] 包含格式/内容/质量三维检查
- [ ] 可作为质量验收标准

#### 步骤 1.4: 创建角色库 README

**文件**: `agents/README.md`

**核心内容**:

1. 角色库简介
2. 角色分类说明
3. 使用方式（三种调用方式）
4. 角色索引（按分类列举）
5. 贡献新角色的指南
6. 典型协作流程

**验收标准**:

- [ ] README 文件创建
- [ ] 包含完整的使用指南
- [ ] 角色索引框架建立

#### 步骤 1.5: 创建示例库结构 🆕

**文件**: `agents/examples/README.md`

**目的**: 集中管理所有角色的详细使用示例，保持角色定义简洁

**核心内容**:

1. 示例库使用说明
2. 示例文档命名规范：`[角色名]_examples.md`
3. 示例编写指南
4. 示例索引（按角色分类）

**示例文档模板**: `examples/[角色名]_examples.md`

```markdown
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

\`\`\`[语言]
[具体的输入代码或内容]
\`\`\`

### 角色响应

\`\`\`[语言]
[具体的输出代码或内容]
\`\`\`

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
```

**验收标准**:

- [ ] examples/目录创建完成
- [ ] README.md 包含使用说明和索引
- [ ] 示例文档模板可直接复用
- [ ] 说明何时需要参考示例

---

### 阶段 2: P0 角色开发（3-4 天）✅ **已完成**

**完成情况**:

- ✅ 5 个 runtime 角色已创建
- ✅ 3 个 development 角色已创建
- ✅ 3 个 language_specific 角色已创建（含 base/frontend_engineer）
- ✅ 所有角色已通过 quality_checklist
- ✅ role_conversion_log.md 和 implementation_progress.md 已修复

**⚠️ 需要调整** (基于新增的元数据字段):

- [ ] 为 10 个 P0 角色补充"可编辑性"字段
  - runtime 角色: `可编辑性: locked`
  - development 角色: `可编辑性: customizable`
  - language_specific 角色: `可编辑性: customizable`
- [ ] 统一"来源"字段为`框架内置`

---

#### 步骤 2.1: 改造运行时角色（2 天）✅ **已完成**

**角色列表**:

1. plan_reviewer (方案审查员)
2. code_reviewer (代码审查员)
3. test_engineer (测试工程师)
4. performance_optimizer (性能优化专家)
5. security_auditor (安全审计员)

**改造流程**:

```
1. 从ai-coding-prompt提取原始内容
2. 按照agent_template.md格式改造
3. 去Java化、通用化
4. 添加元数据和协作关系
5. 使用quality_checklist.md自检
6. 提交同行评审
```

**单个角色验收标准**:

- [ ] 通过格式检查清单
- [ ] 通过内容检查清单
- [ ] 通过质量检查清单
- [ ] 提供至少 1 个使用示例
- [ ] 明确协作关系
- [ ] 定义评估标准

**阶段验收标准**:

- [ ] 5 个运行时角色全部完成
- [ ] 每个角色通过 quality_checklist
- [ ] README 中的索引已更新

#### 步骤 2.2: 改造开发时角色（1 天）✅ **已完成**

**角色列表**: 6. architecture_analyst (架构分析师) 7. database_designer (数据库设计师) 8. api_designer (API 设计师)

**改造流程**: 同步骤 2.1

**阶段验收标准**:

- [ ] 3 个开发时角色全部完成
- [ ] 每个角色通过 quality_checklist
- [ ] README 中的索引已更新

#### 步骤 2.3: 改造语言专属角色（1 天）✅ **已完成**

**角色列表**: 9. vue3_expert (Vue 3 专家) 10. vue3_state_manager (Vue 3 状态管理师)

**特殊注意**:

- 先创建 `language_specific/_base/frontend_engineer.md` 通用基础
- Vue 3 专属角色继承通用基础并增强

**阶段验收标准**:

- [ ] 通用基础角色创建
- [ ] 2 个 Vue 3 专属角色完成
- [ ] 验证"通用基础+语言增强"模式可行
- [ ] README 中的索引已更新

---

### 阶段 2.5: 元数据字段补充（0.5 天）⏳ **待执行**

**背景**: Phase 1 和 Phase 2 已 100%完成，但元数据定义新增了"可编辑性"字段，需要补充到已创建的角色中。

#### 步骤 2.5.1: 更新角色模板

**文件**: [agents/\_templates/agent_template.md](cci:7://file:///d:/zibuyu_code/ai_coding_context/agents/_templates/agent_template.md:0:0-0:0)

**需要调整**:

- [ ] 增加"可编辑性"字段到元数据区
- [ ] 统一"来源"字段说明为`框架内置`
- [ ] 更新字段说明和示例

**验收标准**:

- [ ] agent_template.md 包含 13 个字段
- [ ] 字段说明清晰
- [ ] 格式规范

#### 步骤 2.5.2: 补充 P0 角色元数据

**任务**: 为 10 个已创建的 P0 角色补充"可编辑性"字段

**文件清单**:

1. agents/runtime/plan_reviewer.md - 补充 `可编辑性: locked`
2. agents/runtime/code_reviewer.md - 补充 `可编辑性: locked`
3. agents/runtime/test_engineer.md - 补充 `可编辑性: locked`
4. agents/runtime/performance_optimizer.md - 补充 `可编辑性: locked`
5. agents/runtime/security_auditor.md - 补充 `可编辑性: locked`
6. agents/development/architecture_analyst.md - 补充 `可编辑性: customizable`
7. agents/development/database_designer.md - 补充 `可编辑性: customizable`
8. agents/development/api_designer.md - 补充 `可编辑性: customizable`
9. agents/language_specific/vue3_expert.md - 补充 `可编辑性: customizable`
10. agents/language_specific/vue3_state_manager.md - 补充 `可编辑性: customizable`

**同时调整**:

- [ ] 统一"来源"字段为`框架内置`（目前可能是`ai-coding-prompt-java-main`）

**验收标准**:

- [ ] 10 个 P0 角色全部补充"可编辑性"字段
- [ ] 元数据格式统一
- [ ] runtime 角色均为`locked`
- [ ] development 和 language_specific 角色均为`customizable`
- [ ] 所有角色"来源"字段统一为`框架内置`

#### 步骤 2.5.3: 重新验证质量

**任务**: 使用 quality_checklist.md 重新验证 10 个角色

**验收标准**:

- [ ] 所有角色通过格式检查（含新字段）
- [ ] 元数据完整性验证通过
- [ ] 更新 implementation_progress.md 记录调整

### 2.6 用户自定义 Agent 功能 (V3.1+) 🔮

#### 2.6.1 核心价值

**为什么需要用户自定义 Agent?**

| 场景类型       | 示例               | 框架角色                | 用户自定义                   |
| -------------- | ------------------ | ----------------------- | ---------------------------- |
| **技术栈差异** | GraphQL vs RESTful | api_designer (RESTful)  | custom.graphql_designer ✅   |
| **框架差异**   | Svelte vs Vue      | vue3_expert             | custom.svelte_expert ✅      |
| **业务领域**   | 金融合规审查       | security_auditor (通用) | custom.finance_compliance ✅ |
| **项目特定**   | 项目特定编码规范   | code_reviewer (通用)    | custom.project_reviewer ✅   |

**价值量化**:

- 从 **22 个通用场景** → **无限项目个性化场景**
- 用户满意度预计提升 **40-60%**
- 框架竞争力显著超越静态 Prompt 库

#### 2.6.2 目录结构

```

agents/custom/
├── README.md # 项目级自定义 Agent 说明
├── \_template.md # 快速模板
├── graphql_designer.md # 示例：GraphQL API 设计师
├── tailwind_expert.md # 示例：Tailwind CSS 专家
└── finance_compliance.md # 示例：金融合规审查员

```

**说明**:

- 框架是项目级 copy，每个项目的`custom/`都是该项目专属
- 无需 team 子目录，项目本身就是边界

#### 2.6.3 ID 命名规范

**格式**: `custom.{角色英文名}`

**示例**:

- `custom.graphql_designer` - GraphQL API 设计师
- `custom.tailwind_expert` - Tailwind CSS 专家
- `custom.finance_compliance` - 金融合规审查员

#### 2.6.4 AI 辅助创建工作流 (5 个 Phase)

**触发方式**: `@workflow:创建自定义Agent`

**Phase 1: 需求收集** (3-5 轮提问)

```

AI 提问:

1. Agent 核心职责是什么?
2. 适用的技术栈/场景?
3. 主要输入和输出是什么?
4. 与哪些角色协作?
5. 项目特定规范?

```

**Phase 2: 深度分析** (AI 自主完成)

```

✅ 查重检查: 搜索是否已有类似角色
✅ 必要性评估: 是否可直接使用现有角色
✅ 扩展点分析: 头脑风暴特有功能
✅ 边界分析: 与现有角色的职责划分
✅ 依赖识别: 自动识别协作关系

```

**Phase 3: 生成草稿** (按标准格式)

```

AI 生成完整的自包含文档:

- 元数据自动填充 (custom.{name})
- 基于基础角色复制通用内容 (如适用)
- 增强特定内容
- 快速示例
- 协作角色自动识别

```

**Phase 4: 迭代优化** (用户审查)

```

用户提出修改意见, AI 实时调整
最多迭代 3 轮

```

**Phase 5: 保存和注册**

```

1. 保存到 agents/custom/{name}.md
2. 更新 agents/custom/README.md (索引)
3. 生成使用示例

```

#### 2.6.5 质量保证机制

**AI 生成时的自动检查**:

```yaml
格式检查:
  - [ ] 元数据区完整 (AGENT_META_START/END)
  - [ ] ID格式正确 (custom.{name})
  - [ ] 必需字段无遗漏

内容检查:
  - [ ] 角色概述清晰
  - [ ] 输入输出要求明确
  - [ ] 至少有1个快速示例
  - [ ] 评估标准不少于3条

唯一性检查:
  - [ ] ID不与现有角色冲突
  - [ ] 职责无显著重叠(语义搜索)
```

#### 2.6.6 元数据扩展

**自定义 Agent 的元数据**:

```
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

### 2.7 Personas 人格型 Agent 功能 (V3.1+) 🔮

#### 2.7.1 核心概念

**职责型 Agent vs 人格型 Agent**:

```

职责型 Agent (Role-based):
设计理念: 单一职责原则 (What to do)
特征: 专业、精准、高效
示例: code_reviewer, api_designer
Token: ~1,200 tokens
使用场景: 明确的单一任务

人格型 Agent (Persona-based):
设计理念: 人格导向 + 多职责 (How to think)
特征: 导师式、全流程、一致思维
示例: linus_torvalds, martin_fowler
Token: ~2,500 tokens
使用场景: 需要全流程指导、复杂技术决策

```

**为什么需要人格型 Agent?**

| 用户需求                   | 职责型解决方案      | 人格型解决方案                |
| -------------------------- | ------------------- | ----------------------------- |
| 方案讨论+代码审查+Bug 分析 | 切换 3 个 Agent     | 1 个 Linus 人格,全流程参与 ✅ |
| 保持一致的技术视角         | 每个 Agent 独立视角 | 统一的人格思维方式 ✅         |
| 自然的导师式指导           | 专业但较机械        | 像真实导师对话 ✅             |

#### 2.7.2 初始 Persona 清单

**P1 优先级 (3 个核心人格)**:

**1. linus_torvalds** - Linux 创始人人格

```yaml
人格原型: Linus Torvalds (Linux创始人)
思维方式: 实用主义、性能至上、直率批评
专业领域: [系统架构, 代码审查, 性能优化, Bug分析, 技术决策]
风格特点: [直言不讳, 重视质量, 反对过度工程]
能力范围:
  - 方案讨论和架构设计
  - 代码审查(严格标准)
  - Bug诊断和分析
  - 性能优化建议
  - 技术决策咨询
Token消耗: ~2,500
```

**2. martin_fowler** - 重构大师人格

```yaml
人格原型: Martin Fowler (重构大师)
思维方式: 渐进式改进、持续重构、注重可读性
专业领域: [架构设计, 代码重构, 设计模式, 企业应用架构]
风格特点: [温和, 注重可读性, 强调测试, 渐进式改进]
能力范围:
  - 架构设计和演进
  - 代码重构指导
  - 设计模式应用
  - 企业应用架构咨询
  - 持续集成和测试
Token消耗: ~2,500
```

**3. uncle_bob** - 整洁代码倡导者人格

```yaml
人格原型: Robert C. Martin (Uncle Bob)
思维方式: 原则至上、长期可维护性、专业主义
专业领域: [整洁代码, SOLID原则, TDD, 敏捷开发]
风格特点: [严格, 强调规范, 教育性强, 注重原则]
能力范围:
  - 整洁代码实践
  - SOLID原则应用
  - TDD测试驱动开发
  - 代码质量标准
  - 专业主义培养
Token消耗: ~2,500
```

#### 2.7.3 Persona 元数据设计

```
<!-- AGENT_META_START -->

ID: personas.linus_torvalds
名称: Linus Torvalds
类型: persona # 新类型
版本: v1.0
创建: 2025-12-01
更新: 2025-12-01
来源: 框架内置
改造状态: 已通用化
语言支持: 通用
标签: [系统架构, 性能优化, 代码审查]
依赖: []
被依赖: []
可编辑性: customizable # 可基于此创建自定义版本

# Persona 专属字段

人格原型: Linus Torvalds (Linux 创始人)
思维方式: 实用主义、性能至上、直率批评
专业领域: [系统架构, 代码审查, 性能优化, Bug 分析, 技术决策]
风格特点: [直言不讳, 重视质量, 反对过度工程]

<!-- AGENT_META_END -->
```

#### 2.7.4 使用场景

**场景 1: 全流程技术指导**

```
用户: "@角色:Linus 我想设计一个分布式缓存系统"
Linus: "别搞那些花里胡哨的,先说需求..."
[从架构→数据→接口→代码,全程同一视角]
```

**场景 2: 复杂技术决策**

```
用户: "@角色:Martin 这个架构该不该重构?"
Martin: "让我们先看看代码异味..."
[渐进式分析,给出重构建议]
```

**场景 3: 代码质量提升**

```
用户: "@角色:Uncle Bob 审查这段代码"
Uncle Bob: "违反了单一职责原则..."
[严格的质量标准,教育式指导]
```

#### 2.7.5 何时用 Persona vs Role?

| 场景                 | 推荐类型        | 理由                       |
| -------------------- | --------------- | -------------------------- |
| **明确单一任务**     | Role ✅         | 效率高(Token 少)、专业度高 |
| **需要全流程指导**   | Persona ✅      | 上下文连贯、思维一致       |
| **追求效率和专业度** | Role ✅         | Token 更少、响应更快       |
| **重视交互体验**     | Persona ✅      | 自然、像真实导师           |
| **复杂技术决策讨论** | Persona ✅      | 统一视角、深度思考         |
| **项目特定功能**     | Role(custom) ✅ | 精准专业                   |

**最佳实践: Persona + Role 混合**:

```
用户: "@角色:Linus 我要设计API"
Linus: "说需求,别搞RESTful教条..."
[讨论方向]
Linus: "方向对了,细节让API设计师来"
AI: [切换到 api_designer,完成详细设计]
```

#### 2.7.6 Token 消耗对比与 ROI

| 项目           | Token 消耗 | 使用场景   | ROI 评估  |
| -------------- | ---------- | ---------- | --------- |
| 职责型 Role    | ~1,200     | 单一任务   | 高效率 ✅ |
| 人格型 Persona | ~2,500     | 全流程指导 | 高体验 ✅ |
| 混合使用       | 按需       | 灵活切换   | 最优 ⭐   |

**结论**: Token 消耗增加约 2 倍,但用户体验和指导质量显著提升,ROI 高 ✅

### 阶段 3: 集成与验证（1-2 天）

#### 步骤 3.1: 与 001 (AI 互审)集成测试

**测试内容**:

1. 加载 plan_reviewer 角色
2. 使用 plan_reviewer 审查一个技术方案
3. 验证输出格式符合预期
4. 验证审查质量

**验收标准**:

- [ ] plan_reviewer 成功加载
- [ ] 输出符合定义的格式
- [ ] 审查清单完整
- [ ] 问题识别准确

#### 步骤 3.2: 测试三种调用方式

**测试 1: IDE 集成调用**

```
1. 将plan_reviewer复制到Claude Desktop的agent配置
2. 通过IDE切换到该agent
3. 测试审查功能
```

**测试 2: 框架 Rules 调用**

```
1. 在AI_RULES.md中添加角色清单
2. 测试AI是否能主动提示可用角色
```

**测试 3: 自然语言调用**

```
1. 在AI_Coding_Context.md中添加角色索引
2. 用户自然语言："请使用代码审查员角色审查代码"
3. 验证AI能正确加载角色
```

**验收标准**:

- [ ] 三种调用方式都能成功
- [ ] 用户体验符合预期
- [ ] 调用文档已补充

#### 步骤 3.3: Token 消耗验证

**测试内容**:

1. 测量单个角色的实际 Token 消耗
2. 测量角色清单的 Token 消耗
3. 验证按需加载策略有效

**验收标准**:

- [ ] 单个角色 Token 消耗 ≤ 1,500 tokens
- [ ] 角色清单 Token 消耗 ≤ 2,000 tokens
- [ ] 按需加载机制有效

#### 步骤 3.4: 向后兼容性验证

**测试内容**:

1. 验证现有 AI_Coding_Context.md 不受影响
2. 验证现有子文档不受影响
3. 验证角色库可选启用

**验收标准**:

- [ ] 现有文档正常工作
- [ ] 不使用角色库时无影响
- [ ] 角色库是增强功能

---

### 阶段 4: 文档更新（1 天）

#### 步骤 4.1: 更新 AI_ENTRY_POINT.md

**更新内容**:

```markdown
## 🎭 AI 角色库 (V3.0 新增)

本框架提供了专业的 AI 角色库，可以提供更专业的辅助。

### 可用角色分类

**框架角色** (22 个标准角色):

**运行时角色** (框架自动调用):

- plan_reviewer - 方案审查员 (用于 AI 互审机制)
- code_reviewer - 代码审查员
- test_engineer - 测试工程师
- performance_optimizer - 性能优化专家
- security_auditor - 安全审计员

**开发时角色** (用户按需调用):

- architecture_analyst - 架构分析师
- database_designer - 数据库设计师
- api_designer - API 设计师
- ...

**语言专属角色**:

- vue3_expert - Vue 3 专家
- vue3_state_manager - Vue 3 状态管理师
- ...

**扩展能力** (V3.1+ 规划中) 🔮:

- 支持用户创建项目专属自定义角色
- 支持人格型导师式 Agent (如 Linus 人格)
- 详见未来版本路线图

### 使用方式

详见: agents/README.md
```

**验收标准**:

- [ ] AI_ENTRY_POINT.md 已更新
- [ ] 添加角色库说明章节
- [ ] 保持向后兼容

#### 步骤 4.2: 更新 AI_Coding_Context.md

**更新内容**:

```markdown
## 🎭 专业 AI 角色（可选）

本项目配置了专业的 AI 角色库，提供 22 个标准角色:

### 框架标准角色

| 角色         | 使用场景      | 调用方式           |
| ------------ | ------------- | ------------------ |
| 方案审查员   | 审查技术方案  | @角色:方案审查员   |
| 代码审查员   | 审查代码质量  | @角色:代码审查员   |
| 架构分析师   | 分析系统架构  | @角色:架构分析师   |
| 数据库设计师 | 设计数据库    | @角色:数据库设计师 |
| API 设计师   | 设计 API 接口 | @角色:API 设计师   |
| Vue3 专家    | Vue3 开发     | @角色:Vue3 专家    |

...

### 扩展说明 🔮

未来版本(V3.1+)将支持:

- **自定义角色**: 为项目创建专属 Agent (如 GraphQL 设计师、Tailwind 专家)
- **人格型 Agent**: 导师式全流程指导 (如 Linus 人格、Martin Fowler 人格)

详细信息: [agents/README.md](agents/README.md)
```

**验收标准**:

- [ ] AI_Coding_Context.md 已更新
- [ ] 添加角色索引章节
- [ ] 提供清晰的使用指引

#### 步骤 4.3: 更新 AI_RULES.md

**更新内容**:

```markdown
## AI 角色库使用规范

### 可用专业角色

以下专业角色可在适当场景下使用：

**运行时角色** (框架自动调用):

- plan_reviewer: 在生成技术方案后自动调用审查
- code_reviewer: 代码质量审查
- test_engineer: 测试用例生成
- performance_optimizer: 性能优化建议
- security_auditor: 安全检查

**开发时角色** (用户按需调用):

- 当检测到架构设计需求时,提示: "建议使用 @角色:架构分析师"
- 当检测到数据库设计需求时,提示: "建议使用 @角色:数据库设计师"
- 当检测到 API 设计需求时,提示: "建议使用 @角色:API 设计师"
- 当检测到代码审查需求时,提示: "建议使用 @角色:代码审查员"

**语言专属角色**:

- 当用户使用 Vue 3 时,提示: "建议使用 @角色:Vue3 专家"
- 当讨论 Vue 3 状态管理时,提示: "建议使用 @角色:Vue3 状态管理师"

### 主动提示时机

**框架角色**:

- 生成技术方案后 → 提示使用 plan_reviewer
- 讨论架构设计时 → 提示使用 architecture_analyst
- 设计数据库时 → 提示使用 database_designer
- 设计 API 时 → 提示使用 api_designer
- 代码实现完成后 → 提示使用 code_reviewer
- 讨论 Vue 3 开发时 → 提示使用 vue3_expert

**未来扩展** (V3.1+ 规划中) 🔮:

- 当检测到项目使用 GraphQL 等框架角色未覆盖的技术时
  → 提示: "当前框架角色库暂不包含{技术}专家,未来版本将支持自定义角色"
- 当用户需要全流程技术指导时
  → 提示: "未来版本将支持人格型导师 Agent,提供一致的全流程指导"
```

**验收标准**:

- [ ] AI_RULES.md 已更新
- [ ] 定义了主动提示规则
- [ ] 明确了角色使用时机

### 阶段 5: V3.1 自定义 Agent 功能开发 (2-3 天) 🔮 **V3.1+规划**

#### 步骤 5.1: 创建 custom/目录和文档

**任务**: 建立用户自定义 Agent 的基础设施

**文件清单**:

1. `agents/custom/README.md` - 自定义 Agent 使用指南
2. `agents/custom/_template.md` - 快速模板
3. `agents/workflows/create_custom_agent.md` - AI 辅助创建工作流

**README.md 核心内容**:

- 项目级自定义 Agent 简介
- 与框架角色的关系
- 创建方式(AI 辅助 vs 手动)
- ID 命名规范 (`custom.{name}`)
- 最佳实践

**\_template.md 内容**:

- 基于 agent_template.md
- 预填充`来源: user`
- 预填充`可编辑性: editable`
- 简化版,更易上手

**验收标准**:

- [ ] custom/目录创建
- [ ] README.md 说明清晰
- [ ] \_template.md 可用
- [ ] 命名规范正确

#### 步骤 5.2: 创建 AI 辅助创建工作流

**文件**: `agents/workflows/create_custom_agent.md`

**工作流内容** (5 个 Phase):

**Phase 1: 需求收集**

```markdown
## Phase 1: 需求收集

AI 执行步骤:

1. 询问 Agent 核心职责
2. 询问适用技术栈/场景
3. 询问主要输入输出
4. 询问协作角色
5. 询问项目特定规范

提问模板:
"请告诉我这个自定义 Agent 的核心职责是什么?"
"它主要应用在哪些技术栈或场景?"
...
```

**Phase 2: 深度分析**

```markdown
## Phase 2: 深度分析 (AI 自主)

AI 执行步骤:

1. 查重检查

   - 搜索 agents/目录下所有角色
   - 语义相似度分析
   - 如发现相似角色,询问用户是否继续

2. 必要性评估

   - 分析是否可直接使用现有角色
   - 评估自定义的必要性

3. 扩展点分析

   - 头脑风暴特有功能
   - 识别与现有角色的差异点

4. 边界分析

   - 明确职责范围
   - 避免与现有角色重叠

5. 依赖识别
   - 自动识别可能的协作角色
   - 建议依赖关系
```

**Phase 3: 生成草稿**

```markdown
## Phase 3: 生成草稿

AI 执行步骤:

1. 创建文档结构
2. 填充元数据(ID: custom.{name})
3. 生成角色概述
4. 编写 System Prompt
5. 定义输入输出要求
6. 创建快速示例
7. 列出协作角色
8. 定义评估标准
```

**Phase 4: 迭代优化**

```markdown
## Phase 4: 迭代优化

AI 执行步骤:

1. 展示生成的文档给用户
2. 询问是否需要修改
3. 根据反馈调整
4. 最多迭代 3 轮
```

**Phase 5: 保存和注册**

```markdown
## Phase 5: 保存和注册

AI 执行步骤:

1. 保存到 agents/custom/{name}.md
2. 更新 agents/custom/README.md 索引
3. 生成使用示例
4. 提示用户如何使用
```

**验收标准**:

- [ ] workflow 文件创建
- [ ] 包含所有 5 个 Phase
- [ ] 可被 AI 执行
- [ ] 质量检查机制完善

#### 步骤 5.3: 测试自定义 Agent 创建流程

**测试场景 1**: 创建 GraphQL 设计师

```
用户: "@workflow:创建自定义Agent"
AI: [执行5个Phase]
结果: agents/custom/graphql_designer.md
验证:
  - ID为custom.graphql_designer
  - 元数据完整
  - 可编辑性为editable
```

**测试场景 2**: 创建 Tailwind 专家

```
用户: "@workflow:创建自定义Agent"
AI: [执行5个Phase]
结果: agents/custom/tailwind_expert.md
验证:
  - 查重检查正常工作
  - 质量检查通过
```

**测试场景 3**: 手动创建+AI 质量检查

```
用户: [手动创建custom/finance_compliance.md]
AI: "检测到你手动创建了Agent,我来帮你检查质量..."
结果: 输出质量检查报告
```

**验收标准**:

- [ ] AI 辅助创建成功率>90%
- [ ] 查重机制有效
- [ ] 质量检查准确
- [ ] 手动创建也能获得 AI 检查

### 阶段 6: V3.1 Personas 功能开发 (2-3 天) 🔮 **V3.1+规划**

#### 步骤 6.1: 创建 personas/目录

**任务**: 建立 Personas 人格型 Agent 基础设施

**文件清单**:

1. `agents/personas/README.md` - Personas 使用指南
2. `agents/personas/linus_torvalds.md` - Linux 创始人人格
3. `agents/personas/martin_fowler.md` - 重构大师人格
4. `agents/personas/uncle_bob.md` - 整洁代码倡导者人格

**README.md 核心内容**:

- Personas 概念说明(职责型 vs 人格型)
- 3 个初始 Persona 介绍
- 使用场景和最佳实践
- 何时用 Persona vs Role
- Token 消耗说明

**验收标准**:

- [ ] personas/目录创建
- [ ] README.md 说明清晰
- [ ] 概念解释准确

#### 步骤 6.2: 创建 3 个核心 Persona

**任务**: 创建 Linus、Martin Fowler、Uncle Bob 三个人格

**单个 Persona 文件结构**:

```markdown
# Linus Torvalds 人格

<!-- AGENT_META_START -->

[完整元数据,包含人格专属字段]

<!-- AGENT_META_END -->

## 📋 人格概述

[人格特征、思维方式、专业领域]

## 🎯 角色设定

[身份定义、行为准则、输出规范]

## 💡 典型对话示例

[3-5 个真实对话场景]

## 📊 适用场景

[何时使用这个人格]

## 🔗 协作建议

[与其他角色/Persona 的配合]
```

**Linus Torvalds 人格要点**:

- 思维方式: 实用主义、性能至上
- 风格: 直言不讳、反对过度工程
- 典型语句: "别搞那些花里胡哨的..."
- Token: ~2,500

**Martin Fowler 人格要点**:

- 思维方式: 渐进式改进、持续重构
- 风格: 温和、注重可读性
- 典型语句: "让我们先看看代码异味..."
- Token: ~2,500

**Uncle Bob 人格要点**:

- 思维方式: 原则至上、长期可维护性
- 风格: 严格、强调规范
- 典型语句: "违反了单一职责原则..."
- Token: ~2,500

**验收标准**:

- [ ] 3 个 Persona 文件创建完成
- [ ] 元数据包含人格专属字段
- [ ] 典型对话示例真实
- [ ] Token 消耗 ≈2,500 tokens/个
- [ ] 人格特征鲜明

#### 步骤 6.3: 测试 Persona 使用场景

**测试场景 1**: 全流程技术指导

```
用户: "@角色:Linus 我想设计分布式缓存系统"
验证:
  - Linus人格正确加载
  - 对话风格符合人格特征
  - 能够进行全流程指导
  - 思维方式一致
```

**测试场景 2**: Persona + Role 混合

```
用户: "@角色:Martin 这个架构该不该重构?"
Martin: [分析后] "方向对了,细节让架构分析师来"
AI: [切换到architecture_analyst]
验证:
  - Persona和Role切换流畅
  - 上下文保持连贯
```

**测试场景 3**: Token 消耗验证

```
测试:
  - 加载单个Persona
  - 测量实际Token消耗
验证:
  - Token消耗≈2,500 tokens
  - 在可接受范围内
```

**测试场景 4**: 对比测试

```
同一任务分别使用:
  - 职责型Role (code_reviewer)
  - 人格型Persona (Linus)
对比:
  - 响应质量
  - 用户体验
  - Token消耗
  - ROI评估
```

**验收标准**:

- [ ] Persona 正确加载
- [ ] 对话风格符合人格
- [ ] 全流程指导有效
- [ ] Persona+Role 混合流畅
- [ ] Token 消耗符合预期
- [ ] 用户体验显著提升

## 📊 第三部分：过程记录机制

### 3.1 进度跟踪表

**文件**: `agents/_progress/implementation_progress.md`

```markdown
# AI 角色库实施进度

## 整体进度

- 开始日期: [YYYY-MM-DD]
- 预计完成: [YYYY-MM-DD]
- 当前状态: [进行中/已完成]
- 完成百分比: [X%]

## 阶段性进度

### 阶段 1: 基础设施 (2-3 天)

- [ ] 创建目录结构
- [ ] 创建角色模板
- [ ] 创建检查清单
- [ ] 创建 README 框架

### 阶段 2: P0 角色开发 (3-4 天)

- [ ] plan_reviewer (1/10)
- [ ] code_reviewer (2/10)
- [ ] test_engineer (3/10)
- [ ] performance_optimizer (4/10)
- [ ] security_auditor (5/10)
- [ ] architecture_analyst (6/10)
- [ ] database_designer (7/10)
- [ ] api_designer (8/10)
- [ ] vue3_expert (9/10)
- [ ] vue3_state_manager (10/10)

### 阶段 3: 集成与验证 (1-2 天)

- [ ] 001 集成测试
- [ ] 三种调用方式测试
- [ ] Token 消耗验证
- [ ] 向后兼容性验证

### 阶段 4: 文档更新 (1 天)

- [ ] AI_ENTRY_POINT.md
- [ ] AI_Coding_Context.md
- [ ] AI_RULES.md

## 问题和风险记录

### 已解决问题

- 无

### 待解决问题

- 无

### 风险项

- 无

## 变更记录

| 日期 | 变更内容 | 理由 |
| ---- | -------- | ---- |
| -    | -        | -    |
```

### 3.2 角色改造记录

**文件**: `agents/_progress/role_conversion_log.md`

```markdown
# 角色改造日志

## plan_reviewer (方案审查员)

**改造日期**: [YYYY-MM-DD]
**来源**: ai-coding-prompt-java-main/rules/Review 需求实现检查 prompt.md
**改造人**: [名称]

**主要变更**:

- 去 Java 特定内容
- 添加元数据
- 格式标准化
- 添加协作关系

**自检结果**: ✅ 通过
**同行评审**: ✅ 通过 (@reviewer)
**测试状态**: ✅ 通过

---

## code_reviewer (代码审查员)

...
```

### 3.3 问题收集表

**文件**: `agents/_progress/issues_and_feedback.md`

```markdown
# 问题和反馈收集

## 实施过程中的问题

### 问题 1: [问题标题]

- **发现日期**: [YYYY-MM-DD]
- **影响范围**: [描述]
- **解决方案**: [描述]
- **状态**: [待解决/已解决]

## 用户反馈

### 反馈 1: [反馈标题]

- **反馈日期**: [YYYY-MM-DD]
- **反馈内容**: [描述]
- **处理方案**: [描述]
- **状态**: [待处理/已处理]
```

---

## ✅ 第四部分:最终核查标准

### 4.1 基础设施核查

- [ ] **目录结构完整**

  - [ ] runtime/ development/ language_specific/ workflows/ 目录存在
  - [ ] \_templates/ \_progress/ 目录存在
  - [ ] README.md 创建完成

- [ ] **模板文件完整**

  - [ ] agent_template.md 包含所有必要章节
  - [ ] quality_checklist.md 包含三维检查标准
  - [ ] 模板可直接复用

- [ ] **文档质量**
  - [ ] README.md 提供清晰的使用指南
  - [ ] README.md 包含完整的角色索引
  - [ ] README.md 说明三种调用方式

### 4.2 P0 角色核查

#### 角色完整性检查

- [ ] **10 个 P0 角色全部完成**
  - [ ] 5 个运行时角色
  - [ ] 3 个开发时角色
  - [ ] 2 个语言专属角色

#### 单个角色质量检查（对所有 10 个角色）

**格式检查**:

- [ ] 包含完整的 AGENT_META 元数据
- [ ] 包含角色概述（快速说明）
- [ ] 包含角色设定（身份/行为/输出规范）
- [ ] 包含使用示例（至少 1 个）
- [ ] 包含协作角色
- [ ] 包含评估标准

**内容检查**:

- [ ] 角色定位明确
- [ ] 行为准则清晰（应该/不应该）
- [ ] 输出规范具体
- [ ] 示例真实可用
- [ ] 无语言/框架特定内容（或已标注）

**质量检查**:

- [ ] 语言通顺，无歧义
- [ ] 结构清晰，易于理解
- [ ] 实用性强，可直接使用
- [ ] 与其他角色无冲突
- [ ] 元数据准确完整

#### 特殊角色验证

- [ ] **plan_reviewer**: 成功支持 001 (AI 互审机制)
- [ ] **vue3_expert**: "通用基础+语言增强"模式可行

### 4.3 集成测试核查

- [ ] **001 集成测试通过**

  - [ ] plan_reviewer 成功加载
  - [ ] 审查输出格式正确
  - [ ] 审查质量符合预期

- [ ] **三种调用方式验证**

  - [ ] IDE 集成调用测试通过
  - [ ] 框架 Rules 调用测试通过
  - [ ] 自然语言调用测试通过

- [ ] **Token 消耗验证**

  - [ ] 单个角色 ≤ 1,500 tokens
  - [ ] 角色清单 ≤ 2,000 tokens
  - [ ] 按需加载策略有效

- [ ] **向后兼容性验证**
  - [ ] 现有文档不受影响
  - [ ] 角色库可选启用
  - [ ] 不使用时无影响

### 4.4 文档更新核查

- [ ] **AI_ENTRY_POINT.md**

  - [ ] 添加了角色库说明章节
  - [ ] 说明清晰易懂
  - [ ] 保持向后兼容

- [ ] **AI_Coding_Context.md**

  - [ ] 添加了角色索引章节
  - [ ] 提供使用指引
  - [ ] 格式规范

- [ ] **AI_RULES.md**
  - [ ] 添加了主动提示规则
  - [ ] 定义了使用时机
  - [ ] 规则明确

### 4.5 过程记录核查

- [ ] **进度跟踪表完整**

  - [ ] 所有阶段状态记录
  - [ ] 完成百分比准确
  - [ ] 问题和风险有记录

- [ ] **角色改造日志完整**

  - [ ] 每个角色都有改造记录
  - [ ] 记录包含来源、变更、自检、评审
  - [ ] 日志格式统一

- [ ] **问题收集表维护**
  - [ ] 实施问题有记录
  - [ ] 用户反馈有记录
  - [ ] 处理状态明确

### 4.6 最终验收清单

#### 功能性验收

- [ ] ✅ 10 个 P0 角色全部可用
- [ ] ✅ 三种调用方式都工作正常
- [ ] ✅ 支持 001 (AI 互审机制)
- [ ] ✅ Token 消耗在可接受范围

#### 质量性验收

- [ ] ✅ 所有角色通过 quality_checklist
- [ ] ✅ 同行评审全部通过
- [ ] ✅ 集成测试全部通过
- [ ] ✅ 向后兼容性验证通过

#### 文档性验收

- [ ] ✅ 角色库 README 完整
- [ ] ✅ 框架核心文档已更新
- [ ] ✅ 使用指南清晰
- [ ] ✅ 进度记录完整

#### 可维护性验收

- [ ] ✅ 角色模板可复用
- [ ] ✅ 检查清单可执行
- [ ] ✅ 质量保证机制建立
- [ ] ✅ 反馈渠道明确

---

## 📈 第五部分：成功指标

### 5.1 短期指标（实施完成后 1 周）

| 指标           | 目标值 | 测量方法                       |
| -------------- | ------ | ------------------------------ |
| P0 角色完成率  | 100%   | 10 个角色全部通过验收          |
| 质量检查通过率 | 100%   | 每个角色通过 quality_checklist |
| 集成测试通过率 | 100%   | 所有集成测试通过               |
| 文档更新完成率 | 100%   | 3 个核心文档全部更新           |

### 5.2 中期指标（使用 1 个月后）

| 指标           | 目标值   | 测量方法           |
| -------------- | -------- | ------------------ |
| 角色调用成功率 | >95%     | 用户反馈和日志分析 |
| 用户满意度     | >4.0/5.0 | 用户反馈调查       |
| Token 消耗增长 | <20%     | 对比角色库启用前后 |
| 发现的问题数   | <5 个    | 问题收集表统计     |

### 5.3 长期指标（使用 3 个月后）

| 指标            | 目标值 | 测量方法           |
| --------------- | ------ | ------------------ |
| AI 编码质量提升 | >20%   | 代码审查通过率对比 |
| 开发效率提升    | >15%   | 需求交付周期对比   |
| 角色复用率      | >80%   | 角色调用频率统计   |
| P1/P2 角色需求  | 明确   | 用户反馈分析       |

---

## 🎯 第六部分：版本路线图

### 6.1 V3.0 (当前版本) - 基础框架角色库

- ✅ 22 个框架标准角色
- ✅ 完整的质量保证机制
- ✅ 三种调用方式

### 6.2 V3.1 (规划中) - 扩展功能

- 🔮 用户自定义 Agent 功能
- 🔮 Personas 人格型 Agent
- 🔮 AI 辅助创建工作流

### 6.3 V3.2+ (未来) - 生态建设

- 社区 Agent 分享
- 角色评级系统
- 跨项目复用

---

## 📚 附录：参考文档

1. `dev/V3.0/pending/013-ai-agent-library.md` - 需求定义
2. `AI_AGENT_LIBRARY_ABSORPTION_PLAN.md` - 吸收方案
3. `dev/V3.0/pending/001-ai-mutual-review.md` - AI 互审机制
4. `other_project/ai-coding-prompt-java-main/` - 参考项目

---

**方案版本**: v1.0
**最后更新**: 2025-11-29
