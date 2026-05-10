---
title: AICC Skill 化 — 可行性与架构设计
summary: 完整记录 AICC 迁移到 skill 模式的问题陈述、业界 skill 机制深度调研、可行性论证、4 个备选架构方案对比，以及最终选定方案的详细设计（plugin 顶层结构、skill 内部结构、路由机制、与 AICC 现有体系的关系）。
keywords: aicc | skill | feasibility | architecture | plugin-design | progressive-disclosure
scope: dev/plan/skill-migration 子项目（架构论证阶段）
related_files: README.md | 02-component-mapping.md | 03-implementation-roadmap.md | 04-edge-cases-and-risks.md
dependencies: README.md | ../../FRAMEWORK_CONTEXT.md
verified_at: 2026-04-26
---

# 01 — 可行性与架构设计

## 一、问题陈述

### 1.1 当前 AICC 的使用模式（clone 模式）

AICC 目前发布形态是一个 Git 仓库（约 200+ 文件），用户需要：

1. `git clone https://.../ai_coding_context.git` 到自己项目里（或全局目录）
2. 阅读 README，确认操作系统与运行时
3. 主动把 `AI_ENTRY_POINT.md` 文件路径发给 AI（手动注入入口）
4. AI 读取 AI_ENTRY_POINT.md → 路由到路径 A/B/C/D → 进一步按需读取 core/、workflows/、templates/、agents/、tools/ 中的子文档
5. 生成的产物（`dev_docs/`、`AI_RULES.md`）落到用户项目里
6. 更新框架时：用户需要 `git pull` 同步框架仓库

### 1.2 痛点清单

| # | 痛点 | 严重程度 | 频率 | 用户感受 |
|---|---|---|---|---|
| 1 | clone 仓库导致用户工作区被框架文件污染 | 高 | 一次性，但永久存在 | "我的项目里凭空多了一堆不相关文件" |
| 2 | 每个新项目都要重复 clone | 中 | 每个新项目 | "刚开新坑就要先把框架搬过来" |
| 3 | 必须手动发送 AI_ENTRY_POINT.md 路径才能触发 | 高 | 每次新会话 | "我得先教 AI 找到入口" |
| 4 | 框架升级要手动 pull，老项目可能被锁在旧版本 | 中 | 每次框架版本更新 | "升级很麻烦，干脆不升了" |
| 5 | AI 必须先读完 AI_ENTRY_POINT（约 750 行）才能开始干活 | 中 | 每次新会话 | "刚开始就吃掉一堆 token" |
| 6 | 同一台机器开 N 个项目就有 N 份 AICC 副本 | 低 | 多项目用户 | "硬盘空间浪费" |
| 7 | 跨工具复用难（Cursor/Copilot/Claude Code 各自手动配） | 高 | 每次切换工具 | "在 IDE 里又要重新接入一次" |
| 8 | 用户没法用自然语言触发能力（必须显式说"按 AICC 框架来"） | 中 | 日常使用 | "AI 不知道我在用 AICC" |

### 1.3 业界趋势倒逼

**2024-2026 期间，主流 AI 编程工具相继支持 skill 机制**：

- Anthropic Claude Code：Agent Skills 系统，plugin 形式分发，描述驱动自动触发
- Anthropic 官方 marketplace：`anthropic-agent-skills`（含 `document-skills`）
- GitHub Copilot CLI：`.github/copilot/skills/` 体系
- Google Gemini CLI：extension 机制（`gemini-extension.json`）
- OpenAI Codex：`~/.agents/skills/` 体系

**业界共识**：能力以"具名、自描述、按需加载、可独立触发"的 skill 单元发布，已成为 AI 工具能力扩展的标准做法。AICC 若不跟进，其优秀的工程化思想（方案优先、设计思维、AI 互审、ADR、复杂度仪表盘等）将逐渐被业界绕过。

### 1.4 不迁移的代价

如果继续维持纯 clone 模式：
- 新用户首次使用门槛 = 阅读 AI_ENTRY_POINT.md（750 行）≈ 30 分钟
- 新用户配置门槛 = clone + 路径设置 + IDE 集成 ≈ 15-30 分钟
- 累计学习成本（按 5 年 1000 用户估算）≈ 750-1500 工时
- AICC 最有价值的 V3.0 设计能力（设计思维、ADR、互审）被锁在 clone 用户群体内，无法被自然语言触发

迁移的价值：单次工程投入，把上述累计成本压到接近 0。

---

## 二、业界 skill 机制深度调研

### 2.1 skill 是什么？运行时如何工作？

**skill 的物理结构**（Anthropic 官方定义）：

```
<plugin>/skills/<skill-name>/
├── SKILL.md          # 必需：包含 frontmatter + 主体说明
├── references/        # 可选：进一步细节按需加载
│   └── *.md
└── scripts/           # 可选：可执行脚本（执行而非读取）
    └── *.py
```

**SKILL.md 的 YAML frontmatter（强制）**：

```yaml
---
name: <skill-name>           # 必需，64 字符内
description: <一句话>         # 必需，1024 字符内，第三人称，"Use when..."
---
```

**运行时三阶段**：

1. **会话启动 (cold start)**：所有 plugin 内 skill 的 `name + description` 被汇总注入系统提示。用户尚未触发任何 skill 时，每个 skill 的成本仅为 metadata（约 100 token）。
2. **触发 (trigger)**：用户输入或对话状态命中某个 skill 的 description 时，Claude 自动 invoke `Skill` 工具，加载该 skill 的 `SKILL.md` 完整内容（最多 500 行）。
3. **按需展开 (progressive disclosure)**：SKILL.md 中如有 `[详见 references/foo.md](references/foo.md)` 形式的引用，Claude 只在需要时调用 Read 工具加载 references 文件。scripts/ 中的脚本永远是 Bash 执行，不读入上下文。

**关键认知**：skill 是一个"按需展开的金字塔"，与 AICC 当前 AI_ENTRY_POINT 的"按需读子文档"思路高度一致 —— 这是**根本可行性的来源**。

### 2.2 两个权威实现的对比

| 维度 | Anthropic 官方 `document-skills` | superpowers (Tools-and-Skills) |
|---|---|---|
| plugin 总 skill 数 | 18 个 | 14 个 |
| 命名风格 | 名词为主：`pdf`, `docx`, `pptx`, `xlsx`, `mcp-builder`, `skill-creator`, `frontend-design`... | 动词-ing：`brainstorming`, `writing-plans`, `executing-plans`, `test-driven-development`... |
| 是否有总入口 skill | ❌ 没有 | ❌ 没有 |
| skill 之间互调用 | 极少（pdf 不会调用 docx） | 频繁（brainstorming → writing-plans → executing-plans 链式） |
| references 形态 | 大量使用，单 skill 可达数十文件（`pptx/` 含 ooxml/ 子目录） | 较少使用，一个 skill 1-3 个 reference |
| scripts 使用 | 重度使用（PDF/PPTX 操作） | 轻度使用（render-graphs.js） |
| 触发机制 | 强类型驱动（用户提到 .pdf 必触发 pdf skill） | 流程语义驱动（"开始一个新功能" → brainstorming） |

**对 AICC 的启示**：
- AICC 的能力既有"流程语义"型（`init`、`health-check`），也有"任务型"（`adr`、`mutual-review`），更接近**两者的混合**。
- 命名风格选择 `aicc-init` / `aicc-health-check` 这样的"前缀 + 名词/动词"，介于两者之间，更稳。
- references 用量预计中等（templates、role 定义、长 workflow 都需要拆出去）。

### 2.3 Anthropic 官方最佳实践要点（精选）

来源：`anthropic-best-practices.md`（已纳入仓库 `superpowers/skills/writing-skills/anthropic-best-practices.md` 缓存）。

| # | 要求 | 量化指标 | 对 AICC 的影响 |
|---|---|---|---|
| 1 | SKILL.md body < 500 行 | 硬性建议 | AICC 现有 path_a_first_generation.md 约 600+ 行，**必须拆 references** |
| 2 | description ≤ 1024 字符 | 硬性 | 容易满足 |
| 3 | description 写"Use when..."、第三人称、不总结 workflow | 风格规范 | 需重写 AICC 入口的"职责说明"风格 |
| 4 | references 只能 1 层深（禁止 ref → ref） | 硬性 | AICC 现有 workflows/shared/ 嵌套引用需拍平 |
| 5 | 跨平台 forward slash 路径 | 硬性 | AICC 已遵守 |
| 6 | scripts 优先执行而非读入 | 强烈推荐 | AICC tools/py/ 全部脚本均可走此路 |
| 7 | 不假设依赖已装 | 硬性 | AICC 当前隐含假设 Python 已装，需补显式声明 |
| 8 | 避免时间敏感信息（"After August 2025..."） | 风格 | AICC FRAMEWORK_CONTEXT.md 大量时间戳需重新审视 |
| 9 | 一致术语（一个概念只用一种叫法） | 强烈推荐 | AICC 当前混用"主文档/Coding Context 文档/AI_Coding_Context.md"，需标准化 |
| 10 | 至少 3 个 evaluation 测试 | 强烈推荐 | AICC 需建立 plugin 级 eval 体系（V3.0+） |
| 11 | CSO（Claude Search Optimization） | 风格规范 | description 必须用 Claude 真实会搜索的关键词（错误信息、症状、同义词），帮助 100+ skills 中胜出。AICC 现有 frontmatter 多偏"职责描述"，需重写为搜索优化版 |

> *CSO（Claude Search Optimization）= 让 description 字段更易被 Claude 在 100+ skills 中找到的优化技巧。详见 superpowers `writing-skills/SKILL.md` §"Claude Search Optimization"。本规划在 Phase 0 standards 文档 `description-style-guide.md` 中给出具体范式。*

### 2.4 平台兼容现状

| 平台 | skill 加载方式 | plugin 概念 | 关键差异 |
|---|---|---|---|
| Claude Code | `Skill` tool + 自动 description 匹配 | ✅ 完整 plugin（skills/agents/commands/hooks） | AICC 主战场 |
| Gemini CLI | `gemini-extension.json` + `activate_skill` tool | ⚠️ 部分（无 commands/hooks） | tool name 不同；MCP 调用差异 |
| Codex | `~/.agents/skills/` flat 加载 | ❌ 无 plugin 概念 | 全局命名空间，命名冲突风险高 |
| Copilot CLI | `.github/copilot/skills/` repo-级 | ❌ 无 plugin 概念 | 仅在 repo 上下文激活 |

**对 AICC 的策略**：Claude Code 是 MVP 主战场（plugin 体系最完整），Gemini 二期补 `gemini-extension.json` 即可，Codex/Copilot 列 backlog（生态较小，等用户呼声）。

### 2.5 Anthropic skill 的元-skill：writing-skills

`superpowers/skills/writing-skills/SKILL.md` 提出 skill 编写的"铁律"：

- **NO SKILL WITHOUT A FAILING TEST FIRST**：先写 pressure scenario（baseline 失败场景），再写 SKILL.md，再验证 Claude 在 skill 加持下不再失败。
- **description 只描述触发条件，不描述工作流**：实证表明，description 总结 workflow 会让 Claude 跟着 description 走、跳过 SKILL.md 内容。
- **Red Flags 清单**：把"agent 会用什么借口跳过 skill"列出来，明确驳斥。

**对 AICC 的影响**：
- AICC 现有 workflows/*.md 普遍是"详细工作流"风格，迁移到 skill 时**头部 description 必须只写触发条件**，工作流内容放进 SKILL.md body。
- 必须为每个 skill 设计 baseline 测试场景（在 03 路线图的 Phase 1-3 各阶段都要纳入）。

---

## 三、可行性分析

### 3.1 AICC 现有能力 → skill 模式的可映射性矩阵

| AICC 组件 | 可映射性 | 风险 | 备注 |
|---|---|---|---|
| **workflows/path_a_first_generation.md**（首次生成全流程） | 🟢 高 | 文件超 500 行，需拆 references | 自然映射为 `aicc-init` skill |
| **workflows/path_b_health_check.md** | 🟢 高 | 健康检查模式 1/2/3 拆 references | 自然映射为 `aicc-health-check` |
| **workflows/path_c_incremental_update.md + commit_guided_update.md + git_safety_workflow.md** | 🟢 高 | 三者合并为一个 skill；Git 操作要走 plugin 安全规范 | `aicc-incremental-update` |
| **workflows/path_d_specific_tasks.md** | 🟡 中 | 是 D 路径的"散装入口"，应拆为多个 skill | 拆为 `aicc-design-thinking`、`aicc-mutual-review`、`aicc-doc-fallacy-fix` 等 |
| **agents/runtime/\*.md**（commit_analyst、design_facilitator 等） | 🟢 高 | embed 到对应 skill 的 references/agents/ | 与 workflow 强耦合 |
| **agents/development/\*.md**（frontend_expert 等） | 🟢 高 | 升格为 plugin agents/，作为 Claude Code subagent | 用户开发时使用 |
| **tools/py/\*.py**（34 个 Python 脚本，含 commit / file / knowledge / content / summary / timestamp 等系列） | 🟢 高 | 全部移入 plugin scripts/，由 skill body 显式调用 | scripts 不进上下文，token 友好 |
| **tools/js/\*.js**（34 个 Node.js 镜像 + 3 个 \*.test.js 回归测试） | 🟢 高 | 同样移入 plugin scripts/js/，作为 Python 不可用时的降级；测试文件用于 plugin 自检 | 保持 AICC 现有降级策略 |
| **tools/fallback/\*.md** | 🟡 中 | 无运行时环境时使用，作为 plugin 一份独立 reference | 罕用，但保留 |
| **tools/git-hooks/**（commit-guided 用 git hook 脚本） | 🟢 高 | 平移到 `plugin/hooks/git-hooks/` 或独立 scripts/hooks/ | aicc-incremental-update 引用 |
| **tools/audit_complete_verification.sh**、**tools/CHANGELOG.md**、**tools/ROADMAP.md**、**tools/README.md** | ⚪ 不迁移 | 保留在框架仓库 tools/ 顶层，不进 plugin | 这些是 tools 自身的元信息/审计工具，与 plugin 用户场景无关 |
| **templates/\*.md**（10+ 模板） | 🟢 高 | 按使用频度就近放进各 skill 的 references/templates/ | 主文档模板放 `aicc-init`；ADR 模板放 `aicc-adr` |
| **core/language_rules.md, security_rules.md, project_types.md** | 🟢 高 | 高频共享 → 提到 plugin 顶级 references/，由各 skill 引用 | 跨 skill 共享，不重复 |
| **core/SUMMARY_FORMAT_SPEC.md** | 🟢 高 | 同上，作为顶级 reference | 摘要规范是底线规则 |
| **core/framework_spec.md, design_decisions.md** | 🟡 中 | 偏框架自身设计文档，部分内容应内化到 plugin CLAUDE.md，部分留在框架仓库 dev/ | 见后文 §五 |
| **config/user_config.md, CONFIG_TEMPLATE.md** | 🟡 中 | skill 模式下，框架级 config 已无意义；用户偏好走 Claude Code 自身 settings 或 dev_docs/configuration.md | 见 02-component-mapping §七 |
| **guides/\*.md**（quick_start, language_support, ai_rules_maintenance 等） | 🟢 高 | 拆为：人类用户文档（plugin README.md）+ skill 内嵌内容 | 不再独立成 guides/ 目录 |
| **dev/quality/**（V3.0+ 系统化文档审核） | 🟡 中 | 框架自身 dev 工具，继续留在 dev/，但其能力可 mirror 一份给用户作为 `aicc-systematic-review` | dogfood 边界，见 §五.3 |

**结论**：AICC 90% 以上能力可以 1:1 或 1:N 映射到 skill 体系；剩余 10% 是框架自身开发工作流（dev/），保持原样不动即可。

### 3.2 关键约束与挑战

#### 约束 1：500 行 SKILL.md 上限

AICC 现有 workflows 文件多数超过 500 行：
- `path_a_first_generation.md` ≈ 650 行
- `commit_guided_update.md` ≈ 480 行
- `git_safety_workflow.md` ≈ 520 行

**应对**：每个 skill 的 SKILL.md 只保留**导航与决策框架**（约 200-300 行），具体步骤、模板、变量表全部下沉到 references/{step1.md, step2.md, ...}。这与 Anthropic 的 progressive disclosure 模式一致。

#### 约束 2：description 1024 字符 + "Use when..." 风格

AICC 现有路径文档头部常以"职责"、"目的"开头（如"路径 A：首次生成流程"），不是 trigger-style。**需重写**。例：

```yaml
# ❌ AICC 现有风格
description: AI Coding Context 框架的首次生成流程，按 8 步执行项目检测、规模决策、方案生成、AI 互审、人工审核、文档生成、进度记录。

# ✅ skill 化目标风格
description: Use when a project does not yet have a dev_docs/AI_Coding_Context.md (or any existing AI coding documentation), and the user asks to set up AI assistance for the codebase. Triggers full project analysis, plan generation with human approval gate, and incremental doc generation with progress tracking.
```

#### 约束 3：references 只能 1 层深

AICC 现有 `workflows/path_a_*.md` → `workflows/shared/failure_handling.md` → `core/security_rules.md` 是 3 层引用链。**必须拍平**：每个 skill 的 references 都直接由 SKILL.md 引用，不能 ref → ref。

**应对**：plugin 顶级建立 `shared-references/` 区域承载跨 skill 共享内容（language_rules、security_rules、SUMMARY_FORMAT_SPEC），各 skill 的 SKILL.md 直接 `[详见 ../shared-references/security_rules.md](../shared-references/security_rules.md)`。

> ⚠️ 待验证：Claude Code 是否允许 skill 跨目录引用 `../shared-references/`。若不允许，回退方案是每个 skill 内部复制一份；详见 `05-open-questions.md` Q3。

#### 约束 4：AICC 当前 AI_ENTRY_POINT 的"路由代码"如何分布

AI_ENTRY_POINT.md 中有 100+ 行的路由决策表（`dev_docs/` 是否存在 → 路径 A/B；@commit → 路径 C；等）。skill 模式下：
- **不再有总路由器**
- 每个 skill 的 description 字段写清"什么情况下应该选我"
- 由 Claude 模型基于 description 自动匹配（实证：document-skills 18 个 skill 工作良好）

**应对**：在 02-component-mapping 中为每个 skill 拟定 description 草稿，并在 Phase 1 的 baseline 测试中验证路由准确率。

### 3.3 价值评估（量化）

**收益**：

| 维度 | clone 模式 | skill 模式 | 改善 |
|---|---|---|---|
| 首次接入耗时 | 30-60 分钟 | 5 分钟（`/plugin install aicc`） | -85% |
| 每次新会话 token 开销 | 全量 AI_ENTRY_POINT (~10k token) | 仅触发的 skill (~2k token) | -80% |
| 新项目接入耗时 | 15-30 分钟（重复 clone + 配置） | 0（plugin 全局可用） | -100% |
| 框架升级摩擦 | git pull + 兼容验证 | plugin 自动更新 | -90% |
| 用户工作区污染 | ~200 文件 | 0 文件 | -100% |
| 跨 IDE 复用 | 每 IDE 单独配置 | plugin 自动 | 质变 |
| 自然语言触发率 | 0%（必须显式说"按 AICC 来"） | 90%+（description 自动匹配） | 质变 |

**成本**：

| 项 | 估算（人月） | 说明 |
|---|---|---|
| Phase 0：plugin 骨架 + 发布机制 | 0.5 | plugin.json、CI、releases 流程 |
| Phase 1：3 个核心 skill MVP | 2.0 | aicc-init / health-check / incremental-update |
| Phase 2：3 个 V3.0 高价值 skill | 1.5 | design-thinking / mutual-review / adr |
| Phase 3：5 个剩余 V3.0 skill | 2.0 | complexity / fallacy-fix / systematic-review / doc-reading-habit / knowledge-reuse |
| Phase 4：多平台扩展 | 0.5 | gemini-extension.json + 翻译 |
| Phase 5：迁移指南 + clone 模式归档 | 0.5 | 文档 + 兼容测试 |
| **合计** | **7.0 人月** | 约 6 个月并行推进 |

**ROI**：单次 7 人月投入 vs 每年节省的累计用户成本 ≈ 第二年回本（按 100 新用户/年估算）。

### 3.4 风险（高层）

| # | 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|---|
| 1 | description 误触发率高 | 中 | 中 | Phase 1 baseline 测试 + 持续 eval |
| 2 | skill 互调用机制不支持，导致复杂工作流断裂 | 低 | 高 | 早期验证（Phase 0），降级为单 skill 内整套流程 |
| 3 | Claude Code plugin 体系本身仍在演进，API 不稳 | 中 | 中 | 紧跟 Anthropic 官方版本，避免使用未文档化特性 |
| 4 | 用户已有 dev_docs/ 不兼容新 skill | 低 | 高 | Phase 5 兼容测试 + 提供修复脚本 |
| 5 | 工作量超估 | 中 | 中 | 严格 Phase Gate，每个 Phase 独立可发布 |

详见 `04-edge-cases-and-risks.md`。

---

## 四、整体架构设计

### 4.1 选定方案：单 plugin × 多扁平 skill × 无总入口

```
aicc/                                 ← Claude Code plugin 根目录
├── .claude-plugin/
│   └── plugin.json                   ← plugin 元信息（Anthropic 标准）
├── README.md                         ← 人类用户的入门文档
├── CLAUDE.md                         ← AI 默认上下文（可选，承载 AICC 跨 skill 共识）
├── shared-references/                ← 跨 skill 共享（language_rules、security_rules、SUMMARY_FORMAT_SPEC 等）
│   ├── language_rules.md
│   ├── security_rules.md
│   ├── summary_format_spec.md
│   └── project_types/
│       ├── frontend.md
│       ├── backend.md
│       └── ...
├── skills/                           ← 扁平 skill 命名空间，全部独立触发
│   ├── aicc-init/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── step_1_env_diagnosis.md
│   │       ├── step_2_project_scan.md
│   │       ├── step_3_scale_decision.md
│   │       ├── step_4_subdoc_selection.md
│   │       ├── step_5_design_thinking_handoff.md
│   │       ├── step_6_plan_generation.md
│   │       ├── step_7_mutual_review_handoff.md
│   │       ├── step_8_doc_generation_loop.md
│   │       ├── templates/
│   │       │   ├── AI_Coding_Context_TEMPLATE.md
│   │       │   ├── AI_RULES_TEMPLATE.md
│   │       │   └── ...
│   │       └── agents/
│   │           ├── design_facilitator.md
│   │           └── summary_generator.md
│   ├── aicc-health-check/
│   ├── aicc-incremental-update/      ← 含 commit-guided + git-safety
│   ├── aicc-design-thinking/
│   ├── aicc-mutual-review/
│   ├── aicc-adr/
│   ├── aicc-complexity-dashboard/
│   ├── aicc-doc-fallacy-fix/
│   ├── aicc-systematic-review/
│   ├── aicc-doc-reading-habit/
│   └── aicc-knowledge-reuse/
├── agents/                           ← Claude Code subagent（development 角色）
│   ├── aicc-frontend-expert.md
│   ├── aicc-backend-expert.md
│   ├── aicc-devops-expert.md
│   ├── aicc-architect.md
│   └── ...
├── commands/                         ← 显式 slash 命令，对应主要 skill
│   ├── aicc-init.md
│   ├── aicc-health.md
│   ├── aicc-update.md
│   └── ...
├── scripts/                          ← 脚本工具（执行而非读取）
│   ├── py/
│   │   ├── env_diagnosis.py
│   │   ├── project_scanner.py
│   │   ├── git_diff_analyzer.py
│   │   ├── git_safety.py
│   │   ├── summary_extractor.py
│   │   ├── summary_related_checker.py
│   │   ├── summary_index_generator.py
│   │   ├── why_tool.py
│   │   ├── aac_validator.py
│   │   ├── knowledge_cli.py
│   │   ├── knowledge_matcher.py
│   │   ├── doc_dependency_tracer.py
│   │   ├── manage_fix_with_git.py
│   │   ├── fix_history_manager.py
│   │   ├── semantic_related_detector.py
│   │   ├── batch_fix_manager.py
│   │   ├── complexity_scanner.py
│   │   ├── report_generator.py
│   │   ├── notifier.py
│   │   └── doc_health_checker.py
│   ├── js/                           ← Node.js 降级镜像
│   │   ├── env_diagnosis.js
│   │   ├── project_scanner.js
│   │   ├── git_diff_analyzer.js
│   │   ├── complexity_scanner.js
│   │   ├── report_generator.js
│   │   └── doc_health_checker.js
│   └── fallback/                     ← 无运行时环境时的 Bash/PowerShell 速查
│       ├── linux_macos.md
│       └── windows_powershell.md
├── hooks/                            ← Claude Code 事件 hook（可选）
│   └── on-session-start.json         ← 例如：在新项目自动 health-check
└── gemini-extension.json             ← Gemini CLI 兼容清单（Phase 4 添加）
```

### 4.2 备选方案对比与决策依据

| 方案 | 形态 | 优点 | 缺点 | 决策 |
|---|---|---|---|---|
| **A. 单 plugin × 多扁平 skill** | 所有 skill 平铺在 plugin 内 | ✅ 与 document-skills/superpowers 一致<br>✅ 单次安装即获全部能力<br>✅ 每个 skill 独立触发 | plugin 体量大；发布更新粒度粗 | **✅ 选定** |
| B. 多 plugin 拆分 | aicc-core / aicc-quality / aicc-architecture 三个 plugin | 用户按需装；发布粒度细 | plugin 间依赖复杂；用户认知成本高（要装哪几个？） | ❌ |
| C. 单 skill `aicc` + 内部 references | 一个 skill 做"门面"，内部引用所有详细 workflow | 与现有 AI_ENTRY_POINT 心智模型一致；改动最小 | 放弃 skill 体系最有价值的"按描述自动触发多入口"；用户必须显式说"用 aicc" | ❌ |
| D. 混合：单 plugin + 总入口 + 专项 skill | 既有 `aicc` 总入口 skill，也有专项 skill | 兼顾单入口便捷与多触发点 | writing-skills 警示"description 总结 workflow 会让 Claude 跳过实际 skill 内容"；总入口 description 写不好就成了陷阱 | ❌ |

**为什么不要总入口 skill（详细论证）**：

1. **设计哲学冲突**：skill 系统的核心机制是"每个 skill 用自己的 description 争夺 Claude 的注意力"。总入口 skill 一旦存在，其 description 必须涵盖"所有 AICC 场景"，这会与下游具体 skill 的 description 高度重叠 → Claude 无法清晰区分该用谁。
2. **实证证据**：document-skills（18 skill）和 superpowers（14 skill）都没有总入口，运行良好。
3. **writing-skills 元-skill 警告**：description 总结 workflow 会创建"快捷方式"让 Claude 跳过 skill 内容。总入口 skill 必然要总结全流程 → 触发这个反模式。
4. **路由本就该是 description 的责任**：AICC 现在的路由决策表（"无 dev_docs/ → 路径 A"）正好可以分散写进每个 skill 的 description 第一句话。

**唯一保留可能**：未来如果用户反馈"我不知道用哪个 aicc skill"频次很高，可以补一个 `aicc-overview` skill，描述为 `Use ONLY when the user explicitly asks "what AICC capabilities are available" or "show me the AICC menu"` —— 此时 description 是"显示菜单"而不是"路由"，不会与其他 skill 抢触发权。这个保留方案记入 `05-open-questions.md` Q5。

### 4.3 SKILL.md 内部结构规范（约束 + 模板）

**硬性约束**：
- body < 500 行（含示例代码）
- frontmatter `name` 与目录名一致
- frontmatter `description` < 1024 字符，第三人称，"Use when..." 起头，**不总结 workflow**
- 内部引用只能指向同 skill 的 `references/`，或 plugin 顶级 `shared-references/`
- 引用都必须用 forward slash
- 不假设 Python/Node 已装，必须显式声明依赖与降级

**推荐结构**：

```markdown
---
name: aicc-init
description: Use when ... (1-3 sentences of trigger conditions only)
---

# AICC Init

## Overview
（2-4 句：这个 skill 解决什么问题）

## When to Use
- 触发条件 1
- 触发条件 2
- ❌ Not for: ...（防误触发）

## Workflow
（核心步骤的导航表，每步链到 references/step_N.md）

## Required Tools / Dependencies
（声明 Python/Node 依赖与版本）

## Quick Reference
（高频参数、决策矩阵）

## Common Mistakes
（已知陷阱）

## Detailed Steps
- [Step 1: ...](references/step_1_env_diagnosis.md)
- [Step 2: ...](references/step_2_project_scan.md)
- ...

## Related Skills
- aicc-design-thinking（在 Step 5.5 调用）
- aicc-mutual-review（在 Step 7 调用）
```

### 4.4 路由机制：description 字段如何替代 AI_ENTRY_POINT

**当前 AI_ENTRY_POINT.md 的路由决策表**（750 行文档中约 100 行）：

```
| dev_docs/ 不存在                  | 路径 A: 首次生成流程     |
| dev_docs/ 存在 + 主文档存在       | 路径 B: 文档健康检查     |
| 检测到 @commit 或 Git 上下文     | 路径 C: 增量更新流程     |
| 检测到显式指令 (@think, @review) | 路径 D: 特定任务         |
```

**skill 化后的 description 草稿**（每条独立）：

```yaml
# aicc-init
description: Use when a project lacks any AI coding documentation (no dev_docs/AI_Coding_Context.md exists) and the user wants to set up AI assistance, generate project docs, or "initialize" their codebase for AI-assisted development. NOT for projects that already have dev_docs/.

# aicc-health-check
description: Use when a project already has dev_docs/AI_Coding_Context.md and the user wants to assess doc quality, detect drift, run a doc audit, or check whether docs are still in sync with code. NOT for first-time setup.

# aicc-incremental-update
description: Use when the user mentions @commit, references recent git commits, or asks to update docs after code changes. Also triggers on phrases like "sync the docs with my latest changes". NOT for first-time setup or full audits.

# aicc-design-thinking
description: Use when the user wants 5-Why analysis, multi-option comparison, risk assessment, or any structured "think before coding" guidance for a feature/architecture decision. Triggers on @think, "let's design", "compare options". Can also be invoked from inside aicc-init at Step 5.5.

# aicc-mutual-review
description: Use when the user wants AI cross-review of a generated plan, doc, or proposal—particularly for trivial/simple/complex/critical change reviews. Triggers on @review, "review this plan", "double-check". Can also be invoked from inside aicc-init at Step 7.
```

**路由准确性的验证策略**：见 `03-implementation-roadmap.md` 的 Phase 1 baseline 测试。

### 4.5 跨 skill 协作：当一个 skill 需要另一个 skill 的能力时

**场景**：`aicc-init` Step 5.5 需要 design-thinking 引导。

**三种实现策略**：

| 策略 | 实现方式 | 优点 | 缺点 |
|---|---|---|---|
| **(a) Skill 互调用**（推荐） | aicc-init 的 SKILL.md 在 Step 5.5 处写"`Skill('aicc-design-thinking')`" 显式调用 | 复用充分，单一真理来源 | 待验证 Claude Code 是否允许 skill 内部直接调用 `Skill` 工具 |
| (b) Subagent 调度 | aicc-init 在 Step 5.5 调用 `Agent({subagent_type: 'aicc-design-facilitator'})` | 已有 superpowers:subagent-driven-development 的成熟模式可参考 | 需要 development agent 而非 runtime；行为略不同 |
| (c) 内嵌副本 | aicc-init 内部复制一份精简版 design-thinking 流程 | 简单可靠 | 重复维护；与独立的 aicc-design-thinking 可能漂移 |

**推荐**：MVP 阶段先用 (a)，验证可行；不行则降级 (b)；最差才用 (c)。详见 `05-open-questions.md` Q5。

---

## 五、与 AICC 现有体系的关系

### 5.1 框架仓库布局演进（保留 dev/，新增 plugin/）

```
ai_coding_context/                          ← 框架仓库
├── [main 分支可见]
│   ├── README.md                           ← 人类用户：介绍 + 安装方式（clone OR plugin）
│   ├── CONTRIBUTING.md                     ← 贡献指南，保留
│   ├── AI_ENTRY_POINT.md                   ← 保留，用于 clone 模式兜底
│   ├── core/                               ← clone 模式必需文件，保留
│   ├── workflows/
│   ├── templates/
│   ├── agents/
│   ├── tools/                              ← 含 py/, js/, fallback/, git-hooks/,
│   │                                       ←  audit_complete_verification.sh,
│   │                                       ←  CHANGELOG.md, ROADMAP.md, README.md
│   ├── guides/
│   ├── config/
│   └── plugin/                             ← 🆕 skill plugin 源码（同步发布到 marketplace）
│       ├── .claude-plugin/plugin.json
│       ├── shared-references/              ← 跨 skill 共享（language_rules / security_rules / SUMMARY_FORMAT_SPEC / project_types/ ...）
│       ├── skills/                         ← 11 个 aicc-* skill
│       ├── agents/                         ← 7 个 development subagent
│       ├── commands/                       ← 显式 slash 命令（可选）
│       ├── scripts/                        ← 平移自上层 tools/（py/ + js/ + fallback/ + git-hooks/）
│       ├── hooks/                          ← Claude Code 事件 hook（on-session-start 等）
│       ├── tests/                          ← evaluation 体系（baseline eval JSON）
│       ├── CLAUDE.md                       ← 跨 skill 共识（精简版 framework_spec）
│       ├── GEMINI.md                       ← Gemini CLI 兼容（Phase 4 添加）
│       ├── gemini-extension.json           ← 同上
│       └── README.md                       ← plugin 用户文档
└── [dev 分支可见，main 自动剔除]
    └── dev/                                ← 框架自身开发工作区，**保持不变**
        ├── FRAMEWORK_CONTEXT.md
        ├── README.md                       ← dev/ 区索引
        ├── architecture/                   ← 框架自身 ADR（与 aicc-adr 双轨独立）
        ├── case_skillatlas_review/         ← 案例素材
        ├── complexity/                     ← 复杂度仪表盘运行时（与 aicc-complexity-* 双轨）
        ├── plan/
        │   └── skill-migration/            ← 本规划目录
        ├── quality/                        ← 框架自审复审体系
        ├── real_case/                      ← 真实案例素材
        ├── reference/                      ← 理论分析、外部研究
        ├── V2.2/、V2.3/、V3.0/             ← 历版本审查与规划
        └── ...
```

**关键原则**：
- `plugin/` 是 main 分支可见的产物（与 release 一同发布）
- 框架仓库内 `core/` `workflows/` `templates/` `agents/` `tools/` 是 clone 模式必需文件，**不删除**（双轨保留）
- 但需要建立"single source of truth"：避免同样的内容在 `core/language_rules.md` 和 `plugin/shared-references/language_rules.md` 各维护一份漂移
- **解决方案**：plugin/shared-references/ 内的文件用 symlink 指向上层 core/ 等（Linux/Mac）；Windows 用脚本同步。详见 `05-open-questions.md` Q9。

### 5.2 双轨并存策略

| 用户类型 | 推荐路径 | 维护承诺 |
|---|---|---|
| 新用户（首次接触 AICC） | skill-first（`/plugin install aicc`） | 一等公民，全力维护 |
| 现有 clone 用户 | 渐进迁移：保留 clone，叠加 plugin 测试 | 二等公民，但兼容性维护到 V4.0 |
| 不支持 plugin 的环境（旧版 Cursor、本地 Ollama 等） | clone 模式 + AI_RULES.md | 三等公民，仅修复 P0 bug |

**clone 模式的退役时间表**：暂不设定。视 plugin 模式覆盖率而定；至少保留到 plugin 模式占比 > 80%。

### 5.3 dogfood：框架自身的开发工作流

**问题**：AICC 框架团队自己开发 AICC 时，使用的是 `dev/quality/` 和 `dev/V3.0/PROGRESS.md` 体系（不是 dev_docs/）。skill 化是否影响这部分？

**答案**：不影响，但需要明确边界：
- `dev/quality/` 是**框架自身**的复审工作流，目标是审查 `AI_ENTRY_POINT.md`、`README.md` 等顶层文档。这个工作流面向的"项目"是 AICC 框架仓库本身。
- `aicc-systematic-review` skill 是**用户项目**的复审工作流，目标是审查用户项目的 `dev_docs/`。两者是同一种方法的两次实例化，不冲突。
- AICC 团队可以选择 dogfood：用 `aicc-systematic-review` skill（在 plugin 装好后）来复审框架自身。但这是可选行为，不强制。

**dogfood 的边界声明**：
- 框架仓库根目录的 `AI_ENTRY_POINT.md` 入口（clone 模式）始终保留
- 框架团队的 dev/ 工作流不依赖 plugin（avoid 鸡生蛋问题）
- plugin 的开发与发布走独立 CI（与 dev/ 工作流松耦合）

---

## 六、本章小结

| 论证项 | 结论 |
|---|---|
| skill 机制能承载 AICC 全部核心能力？ | ✅ 90%+ 可 1:1 或 1:N 映射；剩余 10% 为框架自身 dev/ 工作流，保持原样 |
| 该选哪种打包形态？ | 单 plugin × 多扁平 skill × 无总入口（与 document-skills、superpowers 双重实证一致） |
| 主要技术约束？ | 500 行 SKILL.md 上限（拆 references）；description 风格（重写）；reference 1 层深（拍平） |
| 主要价值？ | 接入耗时 -85%；token 开销 -80%；用户工作区污染 -100%；自然语言触发率 0% → 90%+ |
| 主要风险？ | description 误触发；skill 互调用机制不确定；Claude Code plugin API 演进 |
| 投入预估？ | ≈ 7 人月，6 个月并行推进，分 6 个 Phase |

**下一文档**：[`02-component-mapping.md`](./02-component-mapping.md) —— AICC 7 大组件 → plugin 的细粒度映射表。
