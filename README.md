# AI Coding Context Framework (ACC)

> **AI 编程上下文框架** (AI Coding Context Framework)  
> **简称**: AI Coding Context / AICC  
> **宣传语**: 让 AI 深度理解你的项目，从"代码生成器"进化为"架构思考伙伴"  
> **面向人类开发者的完整介绍** | 如果你是 AI，请阅读 `AI_ENTRY_POINT.md`

## 📖 这个框架是什么？

一套帮助你为**任何项目**快速生成**结构化、AI 友好**的开发文档体系的完整解决方案。

### 核心特点

✅ **AI 自主决策** - AI 读取入口文件即可自动检测项目、选择策略
✅ **方案优先** - 先生成可审核的方案，避免返工
✅ **基于代码** - 一切分析以实际代码为依据，禁止臆测
✅ **问题发现** - AI 自动发现代码问题和隐患
✅ **多语言支持** - 9 种编程语言 + 11 种项目类型 + 25+主流框架
✅ **进度可控** - 大型项目分批执行，系统化完成
✅ **AI 角色库** - 标准化的专业 AI 角色库 (v3.0)
✅ **实用工具库** - 标准化的跨平台工具集 (v3.0)

## 🎯 它解决什么问题？

### 传统痛点

1. **AI 记不住项目规范** → 每次都要重新解释
2. **AI 无法站在全局角度思考问题** → 不会复用已有的设计
3. **跨会话信息丢失** → 换个 AI 工具又要从头开始
4. **新人上手慢** → 缺少系统化的项目文档
5. **文档容易过时** → 手动维护成本高

### 框架方案

1. **结构化文档** → AI 一次理解，永久记住
2. **标准化格式** → 所有 AI 工具通用
3. **知识沉淀** → 系统化存储在 knowledge/
4. **自动维护** → 有明确的更新触发器

## 📖 框架核心理念

### 现状：Vibe Coding 的陷阱

《软件设计哲学》这本书中提到一个观点：

软件开发是一个熵增的过程，在这个过程中每一次增量都会堆积复杂性，根源来自增加的依赖关系和多次迭代后的信息模糊。

复杂性很容易积累，却极难消除。

在生成式 AI 普及的今天，"Vibe Coding"（凭感觉编程）成为主流。

开发者习惯于抛出一个模糊的需求，让 AI 快速生成代码，更是加速了熵增的过程。

有过 Vibe Coding 经验的开发者一定**有**这种感受，在项目初期，AI 能极大增加效率，但随着项目进行，堆积的复杂度会达到一个自身难以承受的地步。

此时要么全面重构，重写**拿回**开发主动权，要么就只能完全盲信 AI，自己改动不了一点。

而对于已有的项目，进行新功能开发或 bug 修复，AI 辅助在很多时候显得力不从心。

Vibe Coding 速度虽快，但本质上是**向大模型借高利贷**：

1.  **变更放大 (Change Amplification)**: 简单的修改需要在多个层级同步，AI 经常漏改。
2.  **认知负荷 (Cognitive Load)**: 随着代码量激增，人类开发者逐渐失去对项目的掌控。
3.  **未知的未知 (Unknown Unknowns)**: 新的 AI 会话不知道之前的隐性约定，不断引入"雷区"。

最终结果：**速度越快，死得越快。项目迅速沦为不可维护的"屎山"。**

### 解决方案：战略式编程 (Strategic Programming)

**AI Coding Context (ACC)** 不仅仅是一个文档生成工具，它是一套强制执行**战略式编程**的系统。

所谓战略式编程，就是**慢下来，想清楚**，注重产出卓越的设计，并确保项目能长期、持续、高效工作。

我们通过以下机制，强迫 AI 和人类开发者"慢下来，想清楚"：

- **Plan First**: 强制 AI 在写代码前先生成方案，经过人工审核后才能执行。
- **Code-Based Truth**: 所有分析必须基于实际代码，禁止 AI 臆测。
- **Active Defense**: 主动拦截人类的危险指令（如"不管怎样先跑起来"）。
- **Adversarial Review**: 引入 AI 互审机制，让 AI 自己找自己的茬。
- **Document Priority**: 文档优先，鼓励 AI 生成结构化文档，鼓励开发者不断阅读、审核文档以了解整个项目。

## 🆚 方案对比

| 维度           | Vibe Coding (直接问 AI) | 传统文档工具 | **AI Coding Context V3.0** |
| :------------- | :---------------------- | :----------- | :------------------------- |
| **核心目标**   | 速度优先 (能跑就行)     | 记录信息     | **质量优先 (卓越设计)**    |
| **AI 角色**    | 代码生成器              | 记录员       | **思考伙伴 & 审查员**      |
| **复杂性管理** | 被动积累                | 无           | **主动预防 & 可视化**      |
| **知识传承**   | ❌ 极差                 | ⚠️ 依赖人工  | **✅ 系统化沉淀**          |
| **长期维护**   | ❌ 困难                 | ⚠️ 容易过时  | **✅ 自动触发更新**        |
| **Token 消耗** | 高 (重复解释)           | 中           | **低 (精准上下文)**        |

## 🚀 快速开始（3 步）

1. 完整阅读 `README.md（即本文档）` 了解框架
2. 复制框架到你的项目
3. 让 AI 读取 `AI_ENTRY_POINT.md`
4. AI 自动生成文档体系

### 步骤 1: 复制框架

```bash
cp -r ai_coding_context your-project/
cd your-project/
```

### 步骤 2: 让 AI 自主执行

**📋 唯一需要的操作** - 发送给 AI:

```
请阅读 ai_coding_context/AI_ENTRY_POINT.md

然后为当前项目自动生成文档体系。
```

⚠️ **重要说明**:

- ✅ **只需发送** `AI_ENTRY_POINT.md` **给 AI**
- ✅ 其他文档（guides/、templates/等）AI 会自主决策是否读取
- ✅ 您无需阅读或理解框架内部文件（除非您对框架原理感兴趣）
- ✅ `AI_ENTRY_POINT.md` 是您唯一需要关心的入口文档
- ✅ AI 会自主完成：项目检测 → 策略决策 → 生成方案 → 等待审核 → 执行生成

### 步骤 3: 审核确认

AI 会自动：

1. 检测项目语言、类型、规模
2. 决定生成策略
3. 生成分析方案和问题报告
4. **等待你审核**

审核通过后，AI 自动生成完整文档体系。

### 步骤 4: 配置 AI Rules（推荐）

文档生成后，AI 会提示：

```
📐 Rule文件已生成: dev_docs/rules/combined/AI_RULES.md
```

**配置到 IDE**（约 1 分钟）:

1. 打开`dev_docs/rules/combined/AI_RULES.md`
2. 删除文件开头的「使用说明」部分
3. 复制剩余内容到 IDE 的 rule 配置
   - Cursor: `.cursorrules` (直接复制内容即可,无需转换)
   - Windsurf: Custom Rules

**说明**: AI_RULES.md 生成的内容就是 IDE 的.cursorrules 文件格式,可以直接复制使用。

**配置后效果**: AI 每次交互自动遵守项目规范，无需重复提醒！

**就这么简单！** ✅

## 📂 框架文件结构

### 用户使用（生成项目文档）

```
ai_coding_context/
├── AI_ENTRY_POINT.md          # 🤖 AI入口（AI读这个）
├── INTRODUCTION.md             # 👤 人类指南（你在读这个）
│
├── core/                       # 🔧 核心规范
│   ├── language_rules.md       # 文档语言确认规范
│   ├── security_rules.md       # 敏感信息脱敏规范
│   ├── project_types.md        # 项目类型识别与处理
│   └── update_triggers.md      # 文档更新触发机制
│
├── config/                     # ⚙️ 配置系统 (v3.0)
│   ├── README.md               # 配置系统使用指南
│   ├── CONFIG_TEMPLATE.md      # 配置模板（框架默认值）
│   ├── user_config.md          # 用户个人配置（不提交到Git）
│   └── .gitignore              # 排除用户配置
│
├── workflows/                  # 📋 流程文档
│   ├── detection_workflow.md   # 项目检测详细流程
│   ├── decision_workflow.md    # 策略决策详细流程
│   ├── generation_workflow.md  # 文档生成详细流程
│   ├── progress_tracking.md    # 进度记录机制
│   ├── incremental_update_workflow.md # 增量更新流程
│   ├── monorepo_workflow.md    # Monorepo处理流程
│   └── document_health_check.md # 文档健康度检查
│
├── tools/                      # 🛠️ 实用工具库 (v3.0)
│   ├── py/                     # Python 实现
│   ├── js/                     # Node.js 实现
│   └── fallback/               # 降级命令
│
├── guides/                     # 📚 详细指导
│   ├── quick_start.md          # 快速开始
│   ├── project_types.md        # 项目类型适配（11种）
│   ├── language_support.md     # 语言支持（9种语言）
│   ├── documentation_maintenance.md # 文档维护指南
│   ├── ai_rules_maintenance.md # AI Rules维护指南
│   └── configuration_management.md # 配置管理最佳实践
│
└── templates/                  # 📋 文档模板
    ├── GENERATION_PLAN_TEMPLATE.md
    ├── PROJECT_ANALYSIS_REPORT_TEMPLATE.md
    ├── AI_RULES_TEMPLATE.md    # Rule总模板
    └── ... (其他模板)
```

### 框架开发和维护

```
ai_coding_context/
├── CONTRIBUTING.md             # 🤝 框架扩展指南
│
├── dev/                        # 🔧 版本规划和开发文档
│   ├── FRAMEWORK_CONTEXT.md    # 框架全局上下文
│   ├── VERSION_HISTORY.md      # 详细版本历史
│   └── V3.0/                   # V3.0版本规划
│       ├── README.md
│       ├── PROGRESS.md
│       ├── pending/            # 待讨论的优化点
│       └── confirmed/          # 已确认的优化点
│
├── quality/                    # ⭐ 质量保证体系（框架开发者工具）
│   ├── README.md               # 质量保证体系索引
│   ├── AUDIT_WORKFLOW.md       # 文档审查工作流
│   ├── HOW_TO_GENERATE_CONTEXTS.md # 批量生成审查上下文指南
│   ├── standards/              # 质量标准
│   │   ├── COMMON_STANDARDS.md # 通用质量标准（5大维度）
│   │   ├── QUALITY_CHECKLIST.md # 快速检查清单
│   │   └── BY_DOCUMENT_TYPE.md # 按文档类型的专项标准
│   ├── contexts/               # 审查上下文（每个框架文档一个）
│   │   └── _template.md        # 审查上下文模板
│   ├── reports/                # 审查报告归档
│   └── tools/                  # 审查辅助工具
│
└── reference/                  # 📖 参考规范
    ├── framework_spec.md       # 框架详细规范
    └── design_decisions.md     # 设计决策说明
```

> **说明**: `quality/` 目录是供框架开发者使用的质量保证工具，普通用户无需关心。  
> 如果你对框架的设计和原理感兴趣，可以阅读 `quality/README.md` 了解详情。

🎯 简要文档职责表

| 文档                          | 职责                      | 读者            |
| ----------------------------- | ------------------------- | --------------- |
| `AI_ENTRY_POINT.md`           | AI 入口，包含自主决策流程 | AI 必读         |
| `INTRODUCTION.md`             | 人类入门，介绍设计和用法  | 开发者阅读      |
| `guides/*.md`                 | 详细指导和参考            | AI/人类按需查阅 |
| `templates/*.md`              | 生成模板                  | AI 在生成时使用 |
| `reference/framework_spec.md` | 完整规范                  | 深入了解时查阅  |

## 🚀 V3.0 核心创新

V3.0 引入了质的飞跃：

### 1. 🛡️ 主动防御体系

不再被动等待指令，而是主动拦截风险。

- **危险指令拦截**: 识别并阻止可能导致技术债的"快餐式"指令。(规划中)
- **AI 互审机制** ✅: 引入独立的"审查员"角色，对生成的代码进行对抗性审查，分级审查机制。(已完成)

### 2. 🧠 智能思考引导

将 AI 从"执行者"提升为"思考者"。

- **设计思维引导** ✅: 强制进行 5 Why 分析，多方案对比，专家团队协作模式。(已完成)
- **强制文档摘要** ✅: 所有文档必须包含标准化 YAML 摘要，支持智能推荐，节省 Token 30-50%。(已完成)
- **架构决策记录 (ADR)**: 自动追踪和记录关键架构决策。(规划中)

### 3. 🏗️ 强大的基础设施

- **AI 角色库** ✅: 内置标准化的专业角色（架构师、QA、安全专家），降低 Prompt 门槛 90%。(已完成)
- **配置管理系统** ✅: 统一管理团队偏好和功能开关，Markdown + YAML 格式。(已完成)
- **实用工具库** ✅: 提供跨平台的代码分析工具(Python/Node.js)，消除 AI 的幻觉。(已完成)

---

## 🎁 核心价值

### 对个人开发者

- ⚡ **AI 效率提升 80%**: 减少重复解释，AI 一次理解永久记住。
- 📈 **知识永久保存**: 难题解决方案自动沉淀到知识库。
- 🚀 **换工具零成本**: 文档通用，不依赖特定 IDE。
- 💰 **节省 Token 99%**: 增量更新机制，无需每次重新读取全量代码。

### 对团队

- 🤝 **统一规范**: 文档即规范，AI 自动遵守团队约定。
- 🎯 **新人半天上手**: 结构化文档让新人快速理解项目全貌。
- 💡 **知识传承**: 老员工经验系统化，避免人员流动导致知识丢失。

### 对项目

- 📚 **文档完整**: 强制生成和维护，杜绝文档腐化。
- 🔍 **发现隐患**: AI 自动检测潜在问题和技术债。
- 🛡️ **降低风险**: 关键信息显性化，不依赖个人记忆。

---

## 🔧 技术细节

### 支持的语言（9 种）

Python / Java / Go / Rust / PHP / Ruby / C++ / JavaScript / TypeScript

### 支持的项目类型（11 种）

前端 / 后端 / 全栈 / CLI 工具 / 库/SDK / 脚本 / 移动应用 / 桌面应用 / Serverless / 容器化 / 数据科学

### 支持的框架（25+主流框架）

Vue / React / Angular / Express / FastAPI / Django / Spring Boot / Rails / Laravel / ... 等等

详见：`guides/project_types.md` 和 `guides/language_support.md`

---

## 🏗️ 框架开发与维护

### 如何贡献

我们欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与框架开发。

### 质量保证

本框架拥有完善的质量保证体系（位于 `quality/` 目录），确保框架自身的文档质量和逻辑严密性。

- **审查工作流**: 所有核心文档变更需经过 `AUDIT_WORKFLOW.md` 定义的审查流程。
- **质量标准**: 遵循 `quality/standards/` 中的严格标准。

---

## ⚠️ 常见问题

**Q: 和自动文档生成工具有什么区别？**
A: 自动工具只做"描述"，ACC 做"理解"和"规范"。ACC 生成的是 AI 辅助编程的上下文，而不仅仅是给人看的 API 文档。

**Q: 大型项目能用吗？**
A: 能。ACC 专为复杂项目设计，支持增量更新、分层文档和 Monorepo，能有效管理大型项目的复杂度。

**Q: v3.0 有什么新功能？**
A: 引入了 AI 角色库、配置系统、工具库，以及主动防御和设计思维引导等战略式编程特性。

👉 **查看完整解答**: [guides/faq.md](guides/faq.md)

---

## 📚 延伸阅读

- `guides/quick_start.md` - 详细的使用步骤
- `guides/project_types.md` - 了解支持的项目类型
- `reference/framework_spec.md` - 深入了解框架设计
- `reference/SUMMARY_FORMAT_SPEC.md` - 文档摘要规范 (V3.0)
