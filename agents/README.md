# AI 角色库 (AI Agent Library)

**版本**: v3.0  
**创建**: 2025-11-29  
**状态**: 🚧 建设中

---

## 📋 简介

AI 角色库是 AI Coding Context 框架 V3.0 的核心特性，提供专业化的 AI 角色定义，帮助 AI 在不同场景下提供更精准、更专业的辅助。

**核心价值**:

- 🎯 **专业性**: 每个角色都有明确的专业定位和行为准则
- 🔄 **可复用**: 标准化的角色定义，跨项目复用
- 🎭 **灵活调用**: 支持 IDE 集成、框架 Rules、自然语言三种调用方式
- 📊 **质量保证**: 内置评估标准和检查清单

---

## 📁 目录结构

```
ai_agents/
├── README.md                     # 本文档 - 角色库索引和使用指南
├── _templates/                   # 角色模板
│   └── agent_template.md         # 标准角色模板
├── runtime/                      # 框架运行时角色（自动调用）
├── development/                  # 开发时角色（通用能力）
├── language_specific/            # 语言专属角色
│   ├── base/                     # 通用基础
│   ├── typescript/               # TypeScript 专属
│   ├── python/                   # Python 专属
│   └── java/                     # Java 专属
├── workflows/                    # 协作流程模板
└── examples/                     # 示例库（集中管理）
    └── README.md                 # 示例库索引
```

---

## 🎭 角色分类

### Runtime 角色（框架运行时）

框架在特定场景下自动调用的角色：

| 角色 ID                         | 中文名称     | 职责                         | 状态      |
| ------------------------------- | ------------ | ---------------------------- | --------- |
| `runtime.plan_reviewer`         | 方案审查员   | 审查技术方案的完整性和合理性 | ✅ 已完成 |
| `runtime.code_reviewer`         | 代码审查员   | 审查代码质量和规范符合性     | ✅ 已完成 |
| `runtime.test_engineer`         | 测试工程师   | 设计和生成测试用例           | ✅ 已完成 |
| `runtime.performance_optimizer` | 性能优化专家 | 识别和优化性能瓶颈           | ✅ 已完成 |
| `runtime.security_auditor`      | 安全审计员   | 审查代码安全隐患             | ✅ 已完成 |

### Development 角色（开发时）

用户在开发过程中按需调用的通用角色：

| 角色 ID                            | 中文名称     | 职责                   | 状态      |
| ---------------------------------- | ------------ | ---------------------- | --------- |
| `development.architecture_analyst` | 架构分析师   | 分析系统架构和设计模式 | ✅ 已完成 |
| `development.database_designer`    | 数据库设计师 | 设计数据库模型和表结构 | ✅ 已完成 |
| `development.api_designer`         | API 设计师   | 设计 RESTful API 接口  | ✅ 已完成 |

### Language Specific 角色（语言专属）

特定编程语言或技术栈的专业角色：

| 角色 ID                                | 中文名称         | 技术栈                  | 状态      |
| -------------------------------------- | ---------------- | ----------------------- | --------- |
| `language_specific.vue3_expert`        | Vue 3 专家       | Vue 3 + Composition API | ✅ 已完成 |
| `language_specific.vue3_state_manager` | Vue 3 状态管理师 | Vue 3 + Pinia           | ✅ 已完成 |

---

## 🔧 使用方式

### 方式 1: IDE 集成调用 ⭐ 推荐

将角色定义复制到 AI IDE 的 agent 配置中，通过 IDE 原生功能切换角色：

```bash
# 1. 打开角色文件，例如 runtime/plan_reviewer.md
# 2. 复制整个内容
# 3. 在 AI IDE（如 Claude Desktop）中创建新 agent
# 4. 粘贴内容并保存
# 5. 切换到该 agent 使用
```

### 方式 2: 框架 Rules 调用

框架会在适当场景下主动提示可用角色：

```markdown
AI 检测到你正在设计技术方案...
💡 建议使用专业角色: @角色:方案审查员
```

### 方式 3: 自然语言调用

直接用自然语言请求使用特定角色：

```
用户: "请使用代码审查员角色审查这段代码"
AI: [加载 code_reviewer 角色并执行审查]
```

---

## 📚 贡献新角色

如需为项目添加新的自定义角色：

1. **使用模板**: 复制 `_templates/agent_template.md`
2. **填写内容**: 按照模板填写角色定义
3. **质量检查**: 使用 `_templates/quality_checklist.md` 自检
4. **放置位置**:
   - 通用角色 → `development/`
   - 语言专属 → `language_specific/[语言]/`
5. **更新索引**: 在本 README 中添加角色信息

---

## 🔗 典型协作流程

### 新功能开发流程

```
1. architecture_analyst (架构分析师)
   ↓ 设计系统架构
2. database_designer (数据库设计师)
   ↓ 设计数据模型
3. api_designer (API 设计师)
   ↓ 设计接口规范
4. plan_reviewer (方案审查员) ← 自动调用
   ↓ 审查技术方案
5. [开发者实现代码]
6. code_reviewer (代码审查员)
   ↓ 审查代码质量
7. test_engineer (测试工程师)
   ↓ 生成测试用例
```

### Bug 修复流程

```
1. code_reviewer (代码审查员)
   ↓ 分析问题代码
2. [开发者修复 Bug]
3. test_engineer (测试工程师)
   ↓ 生成回归测试
4. security_auditor (安全审计员)
   ↓ 检查安全隐患（如适用）
```

---

## 📊 当前状态

**实施进度**: ✅ P0 角色全部完成

- [x] 创建目录结构
- [x] 创建角色模板
- [x] 创建检查清单
- [x] 开发 P0 角色（10/10）✅

**详细进度**: 参见 [implementation_progress.md](./_progress/implementation_progress.md)

---

## 📖 相关文档

- [实施方案](../../dev/V3.0/confirmed/013-ai-agent-library-implementation.md)
- [需求定义](../../dev/V3.0/pending/013-ai-agent-library.md)
- [吸收方案](../../AI_AGENT_LIBRARY_ABSORPTION_PLAN.md)
- [角色模板](./_templates/agent_template.md)
- [质量检查清单](./_templates/quality_checklist.md)
- [示例库](./examples/README.md)

---

**维护者**: AI Coding Context Framework Team  
**反馈渠道**: 项目 Issues
