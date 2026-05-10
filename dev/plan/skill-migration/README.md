---
title: AICC Skill 化迁移规划 — 总索引
summary: 将 AICC 框架的能力沉淀为 Claude Code plugin / skill 体系的整体规划入口；记录决策共识、文档导航与状态。本文件仅做总索引，所有展开内容请进入 01-04 子文档。
keywords: aicc | skill-migration | plugin | claude-code | planning
scope: dev/plan/skill-migration 子项目根（规划阶段）
related_files: 01-feasibility-and-architecture.md | 02-component-mapping.md | 03-implementation-roadmap.md | 04-edge-cases-and-risks.md | 05-open-questions.md | ../../FRAMEWORK_CONTEXT.md
dependencies: ../../FRAMEWORK_CONTEXT.md
verified_at: 2026-04-26
status: 规划中（brainstorm 完成 → 待复审 → 待立项）
---

# AICC Skill 化迁移规划

> **当前阶段**：头脑风暴产出已落档，等待人工复审。**尚未进入实施**。
> **分支**：`skill`（后续所有相关工作均在此分支推进）。
> **触发原因**：业界主流 AI 编程工具（Claude Code、Copilot CLI、Gemini CLI、Codex）均已原生支持 skill 机制。AICC 当前的 "clone 仓库 + 发送 AI_ENTRY_POINT.md" 模式相对市场成熟实践显得笨重。本规划探讨"将 AICC 优秀设计沉淀为 skill"的可行性、架构与实施路线。

---

## 一、本规划是什么

本规划是一次**架构级迁移**的设计阶段产物，不是实施清单。它回答以下问题：

1. **可行吗？** —— skill 机制能承载 AICC 框架的全部核心能力吗？
2. **怎么做？** —— 推荐的打包形态、命名规则、内部结构是什么？
3. **从哪些组件开始？** —— AICC 现有的 7 大组件（workflows / agents / tools / templates / core / config / guides）如何分别映射到 plugin？
4. **分几步？** —— 从 0 到 1 的实施路线图与阶段验收标准。
5. **会踩什么坑？** —— 已识别的边界条件、风险与开放问题。

**本规划不做的事**：
- 不写任何 SKILL.md 实际内容（属于实施阶段产物）
- 不创建 plugin 目录骨架（属于 Phase 0 的事）
- 不修改 AICC 现有的 dev/ 目录结构（保持稳定，新增不动旧）

---

## 二、为什么需要 skill 化（一句话动机）

**clone 模式让"AICC 的能力"和"用户项目"物理耦合，每个用户都要把 ~200 个文件拷进自己仓库。skill 化可让能力以 plugin 形式发布、按描述自动触发、零污染用户项目。**

详细问题陈述与业界调研见 [`01-feasibility-and-architecture.md` §一、二](./01-feasibility-and-architecture.md)。

---

## 三、核心决策共识（已锁定）

下表为 brainstorm 阶段与维护者达成的 10 项核心决策。任何后续设计、实施、复审都以此为基准；如需变更须走"决策变更"流程并在本表登记修订日期。

| # | 决策项 | 锁定值 | 决策依据（精简） |
|---|---|---|---|
| 1 | 整体走向 | **C：skill-first，clone 兜底** | 兼顾"主推方式 = skill"与"老用户/无 skill 工具不被抛弃" |
| 2 | 打包形态 | **单 plugin × 多扁平 skill** | Anthropic 官方 `document-skills` 与 superpowers 的双重实证 |
| 3 | 总入口 skill | **❌ 不设** | description 字段已承担路由职责；总入口会让 Claude 跳过实际 skill 内容（writing-skills 警示） |
| 4 | skill 前缀 | **`aicc-` 固定前缀** | 跨 plugin 不冲突；用户搜 `aicc` 一目了然 |
| 5 | plugin 名 | **`aicc`** | 与项目内部缩写、skill 前缀对齐；短、好记 |
| 6 | 多平台 | **Claude Code 优先 → Gemini 二期 → Codex/Copilot CLI 列 backlog** | 控制测试矩阵；保留 AICC 跨工具 DNA |
| 7 | tools 打包 | **plugin 级 `scripts/`，Python 主、JS 降级** | 多 skill 共用脚本应提到 plugin 层；保留 fallback/ 的无运行时方案 |
| 8 | runtime agents | **嵌入对应 skill 的 references/agents/** | 与 workflow 强耦合，分散更合理 |
| 9 | development agents | **升格为 plugin `agents/` subagent** | 用户开发期使用，Claude Code 原生体验最好 |
| 10 | 仓库布局 | **`dev/` 不动；新增 `plugin/` 目录承载 skill 源码** | 框架开发与 plugin 产物清晰分离；release 仅发 plugin/ |

> 注：上表的"决策依据"是浓缩版；完整推理过程见 `01-feasibility-and-architecture.md` 第四章。

---

## 四、文档导航

| 文档 | 主题 | 阅读优先级 |
|---|---|---|
| **README.md**（本文） | 总索引 + 决策共识 | ⭐⭐⭐ 必读 |
| [`01-feasibility-and-architecture.md`](./01-feasibility-and-architecture.md) | 问题陈述、业界调研、可行性论证、整体架构设计、备选方案对比 | ⭐⭐⭐ 必读 |
| [`02-component-mapping.md`](./02-component-mapping.md) | AICC 7 大组件 → plugin 映射表，含每个 skill 的职责、依赖、规模估算 | ⭐⭐⭐ 必读 |
| [`03-implementation-roadmap.md`](./03-implementation-roadmap.md) | 6 个阶段（Phase 0-5）的目标、交付物、验收标准、依赖与风险 | ⭐⭐ 实施前必读 |
| [`04-edge-cases-and-risks.md`](./04-edge-cases-and-risks.md) | 边界条件、已识别风险与缓解措施（按 8 个类别归并） | ⭐⭐ 实施前必读 |
| [`05-open-questions.md`](./05-open-questions.md) | 当前未决问题清单（15+ 项），含决策方、提问背景、影响面 | ⭐⭐ 持续维护 |

---

## 五、状态与时间戳

| 字段 | 值 |
|---|---|
| 当前阶段 | brainstorm 完成 → **待复审** |
| 提案人 | Framework Team（与 AI 协作产出） |
| 复审人 | _待指定_ |
| 实施负责人 | _待指定_ |
| 复审目标日期 | _待定_ |
| 立项决策日期 | _待定_ |
| 关联分支 | `skill` |
| 关联 PROGRESS 条目 | _尚未登记到 V3.0/PROGRESS.md_ |

**修订记录**：

| 日期 | 修订内容 | 修订人 |
|---|---|---|
| 2026-04-26 | 初版产出（含 6 份文档） | Framework Team |

---

## 六、术语与缩写

为后续文档行文统一，本规划使用以下术语：

| 术语 | 含义 |
|---|---|
| **AICC** | AI Coding Context 框架，本仓库的项目代号 |
| **clone 模式** | 当前主流使用方式：用户把整个 AICC 仓库 clone 到自己项目里、发送 AI_ENTRY_POINT.md 给 AI |
| **skill-first** | 本规划目标方式：用户安装 plugin、由 skill description 自动触发，不再 clone 仓库 |
| **plugin** | Claude Code 插件（包含 skills/、agents/、commands/、hooks/、scripts/ 的发布单元） |
| **skill** | 单个 SKILL.md + 可选 references/scripts 的功能单元，由 description 触发 |
| **subagent** | Claude Code 的专项 Agent（plugin 的 agents/ 目录），可被 Agent tool 调用 |
| **progressive disclosure** | Anthropic 官方 skill 设计原则：SKILL.md 当目录、details 按需 Read 加载 |
| **CSO** | Claude Search Optimization：让 description 字段更易被 Claude 找到的优化方法 |

---

**下一步行动**：

1. 维护者（你）阅读 6 份文档，记录任何反对意见或补充
2. 召开/约定一次 review 节点，确认所有锁定决策仍然成立
3. 决定是否将本规划登记到 `dev/V3.0/PROGRESS.md`（若立项后归类为 V3.1 或 V4.0 工作项）
4. 立项后进入 Phase 0：搭建 `plugin/` 骨架、起草第一个 skill MVP（推荐 `aicc-init`）
