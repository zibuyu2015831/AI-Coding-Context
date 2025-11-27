# AI 辅助开发文档体系框架 - 使用指南

> **面向人类开发者的完整介绍**  
> 如果你是 AI，请阅读 `AI_ENTRY_POINT.md`

---

## 📖 这个框架是什么？

一套帮助你为**任何项目**快速生成**结构化、AI 友好**的开发文档体系的完整解决方案。

### 核心特点

✅ **AI 自主决策** - AI 读取入口文件即可自动检测项目、选择策略  
✅ **方案优先** - 先生成可审核的方案，避免返工  
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

### 步骤 1: 复制框架

```bash
cp -r _documentation_framework your-project/
cd your-project/
```

### 步骤 2: 让 AI 自主执行

**📋 唯一需要的操作** - 发送给 AI:

```
请阅读 _documentation_framework/AI_ENTRY_POINT.md

然后为当前项目自动生成文档体系。
```

⚠️ **重要说明**:

- ✅ **只需发送** `AI_ENTRY_POINT.md` **给 AI**
- ✅ 其他文档（guides/、templates/等）AI 会自主决策是否读取
- ✅ 您无需阅读或理解框架内部文件
- ✅ `AI_ENTRY_POINT.md` 是您唯一需要关心的入口文档

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
   - Cursor: `.cursorrules`
   - Windsurf: Custom Rules

**配置后效果**: AI 每次交互自动遵守项目规范，无需重复提醒！

**就这么简单！** ✅

---

## 📂 框架文件结构

```
_documentation_framework/
├── AI_ENTRY_POINT.md          # 🤖 AI入口（AI读这个）
├── INTRODUCTION.md             # 👤 人类指南（你在读这个）
│
├── guides/                     # 📚 详细指导
│   ├── quick_start.md          # 快速开始
│   ├── project_types.md        # 项目类型适配（11种）
│   ├── language_support.md     # 语言支持（9种语言）
│   └── generation_workflow.md  # 详细生成流程
│
├── templates/                  # 📋 文档模板
│   ├── GENERATION_PLAN_TEMPLATE.md
│   ├── PROJECT_ANALYSIS_REPORT_TEMPLATE.md
│   ├── PROGRESS_TEMPLATE.md
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
    └── framework_spec.md       # 框架详细规范
```

---

## 🎁 核心价值

### 对个人开发者

- ⚡ **AI 效率提升 80%** - 减少重复解释
- 📈 **知识永久保存** - 难题解决方案沉淀
- 🚀 **换工具零成本** - 文档通用

### 对团队

- 🤝 **统一规范** - 文档即规范
- 🎯 **新人半天上手** - 文档完整清晰
- 💡 **知识传承** - 老员工经验系统化

### 对项目

- 📚 **文档完整** - 强制生成和维护
- 🔍 **发现隐患** - AI 自动检测问题
- 🛡️ **降低风险** - 关键信息不依赖个人

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

### 支持的语言（7 种）

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
请阅读 _documentation_framework/AI_ENTRY_POINT.md
然后为当前项目生成文档体系
```

AI 会自动完成所有检测和决策。

---

## ⚠️ 常见问题

**Q: 和自动文档生成工具有什么区别？**  
A: 自动工具通常只生成 API 文档，本框架生成完整的开发文档体系，包括规范、模式、知识库等，且具备 AI 自主决策能力。

**Q: 需要修改代码吗？**  
A: 不需要！仅生成文档。但建议修复 AI 发现的严重问题。

**Q: 大型项目（10 万行代码）能用吗？**  
A: 可以！框架有完整的分批执行和进度跟踪机制。

**Q: 支持我的小众框架吗？**  
A: AI 会自动识别和记录，即使框架不在预设列表中。

---

## 🎉 开始使用

```bash
# 1. 复制框架到你的项目
cp -r _documentation_framework your-project/

# 2. 发送给AI
"请阅读 _documentation_framework/AI_ENTRY_POINT.md
然后为当前项目生成文档体系"

# 3. 审核AI生成的方案
# 4. 确认后AI自动生成完整文档
# 5. 开始享受高效的AI辅助编程！
```

**就这么简单！** 🚀

---

## 📖 延伸阅读

- `guides/quick_start.md` - 详细的使用步骤
- `guides/project_types.md` - 了解支持的项目类型
- `reference/framework_spec.md` - 深入了解框架设计

---

**有任何问题欢迎反馈！**
