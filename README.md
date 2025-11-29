# AI Coding Context - 使用指南

> **AI 编程上下文框架** (AI Coding Context Framework)  
> **简称**: AI Coding Context / ACC  
> **宣传语**: 让 AI 深度理解你的项目  
> **面向人类开发者的完整介绍** | 如果你是 AI，请阅读 `AI_ENTRY_POINT.md`

---

## 📖 这个框架是什么？

一套帮助你为**任何项目**快速生成**结构化、AI 友好**的开发文档体系的完整解决方案。

### 核心特点

✅ **AI 自主决策** - AI 读取入口文件即可自动检测项目、选择策略
✅ **方案优先** - 先生成可审核的方案，避免返工
✅ **基于代码** - 一切分析以实际代码为依据，禁止臆测
✅ **问题发现** - AI 自动发现代码问题和隐患
✅ **多语言支持** - 9 种编程语言 + 11 种项目类型 + 25+主流框架
✅ **进度可控** - 大型项目分批执行，系统化完成

---

## 🎯 它解决什么问题？

### 传统痛点

1. **AI 记不住项目规范** → 每次都要重新解释
2. **跨会话信息丢失** → 换个 AI 工具又要从头开始
3. **新人上手慢** → 缺少系统化的项目文档
4. **文档容易过时** → 手动维护成本高

### 框架方案

1. **结构化文档** → AI 一次理解，永久记住
2. **标准化格式** → 所有 AI 工具通用
3. **知识沉淀** → 系统化存储在 knowledge/
4. **自动维护** → 有明确的更新触发器

---

## 🚀 快速开始（3 步）

1. 完整阅读 `INTRODUCTION.md（即本文档）` 了解框架
2. 复制框架到你的项目
3. 让 AI 读取 `AI_ENTRY_POINT.md`
4. AI 自动生成文档体系

### 步骤 1: 复制框架

```bash
cp -r ai_documentation_framework your-project/
cd your-project/
```

### 步骤 2: 让 AI 自主执行

**📋 唯一需要的操作** - 发送给 AI:

```
请阅读 ai_documentation_framework/AI_ENTRY_POINT.md

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

---

## 📂 框架文件结构

```
ai_documentation_framework/
├── AI_ENTRY_POINT.md          # 🤖 AI入口（AI读这个）
├── INTRODUCTION.md             # 👤 人类指南（你在读这个）
├── CONTRIBUTING.md             # 🤝 框架扩展指南 (v2.3新增)
│
├── core/                       # 🔧 核心规范 (v2.2新增)
│   ├── language_rules.md       # 文档语言确认规范
│   ├── security_rules.md       # 敏感信息脱敏规范
│   ├── project_types.md        # 项目类型识别与处理
│   └── update_triggers.md      # 文档更新触发机制
│
├── workflows/                  # 📋 流程文档 (v2.2新增)
│   ├── detection_workflow.md   # 项目检测详细流程
│   ├── decision_workflow.md    # 策略决策详细流程
│   ├── generation_workflow.md  # 文档生成详细流程
│   ├── progress_tracking.md    # 进度记录机制
│   ├── incremental_update_workflow.md # 增量更新流程 (v2.3新增)
│   ├── monorepo_workflow.md    # Monorepo处理流程 (v2.3新增)
│   └── document_health_check.md # 文档健康度检查 (v2.3新增)
│
├── guides/                     # 📚 详细指导
│   ├── quick_start.md          # 快速开始
│   ├── project_types.md        # 项目类型适配（11种）
│   ├── language_support.md     # 语言支持（9种语言）
│   ├── generation_workflow.md  # 详细生成流程
│   ├── ai_rules_maintenance.md # AI Rules维护指南 (v2.3新增)
│   └── configuration_management.md # 配置管理最佳实践 (v2.3新增)
│
├── templates/                  # 📋 文档模板
│   ├── GENERATION_PLAN_TEMPLATE.md
│   ├── PROJECT_ANALYSIS_REPORT_TEMPLATE.md
│   ├── PROGRESS_TEMPLATE.md
│   ├── HEALTH_CHECK_REPORT_TEMPLATE.md # 健康度报告模板 (v2.3新增)
│   ├── AI_RULES_TEMPLATE.md    # ⭐ Rule总模板
│   ├── RULE_TEMPLATE.md        # ⭐ 独立Rule模板
│   ├── PLAN_TEMPLATE.md
│   ├── rules/                  # ⭐ Rule示例
│   │   ├── core/               # 核心规范示例
│   │   ├── triggers/           # 触发器示例
│   │   └── AI_RULES_STANDARD_TEMPLATE.md
│   ├── rules_README_TEMPLATE.md
│   └── ...
│
└── reference/                  # 📖 参考规范
    ├── framework_spec.md       # 框架详细规范
    └── design_decisions.md     # 设计决策说明 (v2.2新增)
```

🎯 简要文档职责表

| 文档                          | 职责                      | 读者            |
| ----------------------------- | ------------------------- | --------------- |
| `AI_ENTRY_POINT.md`           | AI 入口，包含自主决策流程 | AI 必读         |
| `INTRODUCTION.md`             | 人类入门，介绍设计和用法  | 开发者阅读      |
| `guides/*.md`                 | 详细指导和参考            | AI/人类按需查阅 |
| `templates/*.md`              | 生成模板                  | AI 在生成时使用 |
| `reference/framework_spec.md` | 完整规范                  | 深入了解时查阅  |

---

## 🎁 核心价值

### 对个人开发者

- ⚡ **AI 效率提升 80%** - 减少重复解释
- 📈 **知识永久保存** - 难题解决方案沉淀
- 🚀 **换工具零成本** - 文档通用
- 💰 **节省 Token 99%** - 文档健康度检查 vs 重新生成 (v2.3)

### 对团队

- 🤝 **统一规范** - 文档即规范
- 🎯 **新人半天上手** - 文档完整清晰
- 💡 **知识传承** - 老员工经验系统化

### 对项目

- 📚 **文档完整** - 强制生成和维护
- 🔍 **发现隐患** - AI 自动检测问题
- 🛡️ **降低风险** - 关键信息不依赖个人
- 🔄 **生命周期管理** - 智能评估文档健康度 (v2.3)

---

## 💡 设计原理

### 1. AI 自主决策机制

- 使用 AI 辅助编程的项目
- 团队协作项目（需要统一规范）
- 中长期维护项目（>3 个月）
- 复杂架构项目（微服务、Monorepo 等）

### ⚠️ 可选

- 一次性脚本（生命周期<1 周）
- 纯个人项目且不使用 AI
- 极小项目（<10 个文件）

---

## 🆚 对比其他方案

| 方案             | 上手成本 | AI 效率 | 质量 | 维护成本 |
| ---------------- | -------- | ------- | ---- | -------- |
| **口头解释**     | 低       | 差      | 差   | 高       |
| **手写 README**  | 中       | 一般    | 一般 | 高       |
| **自动生成工具** | 低       | 好      | 差   | 中       |
| **本框架**       | 中       | 优秀    | 优秀 | 低       |

**本框架的优势**：

- AI 自主决策、自动检测
- 方案优先、质量保障
- 问题发现、提前修复
- 进度可控、适合大项目

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

## 📚 文档使用指南

### 作为开发者

1. **首次使用** - 阅读本文档（INTRODUCTION.md）
2. **快速上手** - 查看 `guides/quick_start.md`
3. **了解功能** - 浏览 `guides/` 目录下的其他文档
4. **深入理解** - 阅读 `reference/framework_spec.md`

### 让 AI 使用

**只需一句话**：

```
请阅读 ai_documentation_framework/AI_ENTRY_POINT.md
然后为当前项目生成文档体系
```

AI 会自动完成所有检测和决策。

---

## ⚠️ 常见问题

**Q: 和自动文档生成工具有什么区别？**  
A: 自动工具通常只生成 API 文档，本框架生成完整的开发文档体系，包括规范、模式、知识库等，且具备 AI 自主决策能力。

**Q: 需要修改代码吗？**  
A: 不需要！仅生成文档。但建议修复 AI 发现的严重问题（如果有的话）。

**Q: 大型项目（10 万行代码）能用吗？**  
A: 可以！框架有完整的分批执行和进度跟踪机制。

**Q: 支持我的小众框架吗？**  
A: AI 会自动识别和记录，即使框架不在预设列表中。

**Q: 为什么选择 Markdown 而不是 JSON/YAML?**  
A: Markdown 具有三大优势:

- 便于开发者直接阅读和理解
- 便于人工审核和修改
- AI 解析友好,语义清晰,支持代码示例和格式化
- 版本控制友好(可读的 diff)

**Q: 生成的文档與其他工具的关系?**  
A: 本框架作为独立文档体系使用,不与 Swagger/TypeDoc 等 API 文档工具整合。各工具解决不同层面的问题,可以并行使用。

**Q: v2.2 版本相比之前有什么改进？**  
A: v2.2 版本主要进行了以下优化:

1. **模块化结构** - 创建了 `core/` 和 `workflows/` 目录,将核心规范和流程文档模块化
2. **精简入口** - `AI_ENTRY_POINT.md` 更加简洁(从 1100+ 行精简到 500- 行),详细内容通过引用访问
3. **增强规范** - 新增语言规范、安全规范、更新触发等核心规范
4. **流程清晰** - 独立的流程文档使执行步骤更清晰,便于 AI 查阅
5. **易于维护** - 模块化设计提升了框架的可扩展性和可维护性

**Q: v2.3 版本有什么新功能？** ⭐ **最新**  
A: v2.3 版本实现了文档生命周期管理:

1. **智能工作流分流** - AI 自动检测项目是否已有文档,智能选择生成或检查流程
2. **文档健康度检查** - 3 种检查模式(快速/标准/深度),科学评估文档是否过时
3. **Token 优化显著** - 文档过时评估仅需~50 tokens(vs 重新生成的~5000 tokens),节省 99%
4. **智能降级策略** - 4 级降级策略,包含双向时间对比,识别历史项目
5. **Monorepo 增强** - 完善的 Monorepo 项目处理流程

这些改进使框架从"纯生成工具"进化为"完整文档生命周期管理工具"。

---

## 📖 延伸阅读

- `guides/quick_start.md` - 详细的使用步骤
- `guides/project_types.md` - 了解支持的项目类型
- `reference/framework_spec.md` - 深入了解框架设计

---

**有任何问题欢迎反馈！**
