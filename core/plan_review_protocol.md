---
title: 方案自审核协议 — 单个落盘方案的审核对象层
summary: 定义 AICC 框架中"单个已落盘方案产物"这一审核对象的统一薄层；规定审核对象、寻址、可重入语义、两门禁分离、写回要求、未来想法路由与复杂度/高风险面触发，"怎么审"一律委派给互审工作流。横跨 plans/ 与 _analysis/ 两个子系统。
keywords: plan-review | review-object | self-review | review_status | active-plan | aicc
scope: AICC 框架 plans/ 与 _analysis/ 子系统的方案审核对象语义层（"审什么/在哪寻址/状态怎么落盘"的真相源；"怎么审"指向 workflows/review-workflow.md）
related_files: core/framework_spec.md | workflows/review-workflow.md | templates/PLAN_TEMPLATE.md | templates/plans_README_TEMPLATE.md | tools/py/doc_health_checker.py
dependencies: workflows/review-workflow.md | workflows/review_standards/
verified_at: 2026-06-13
---

# 方案自审核协议 — 单个落盘方案的审核对象层

> **本文档只定义"审核对象"语义层**：审什么、在哪寻址、状态如何落盘、写回什么、想法去哪。
> **"怎么审"（打分 / 审查维度 / auto-fix / 深度分级）一律委派给 [互审工作流](../workflows/review-workflow.md) 与 [审查标准](../workflows/review_standards/)**，本文不复述引擎。

---

## 1. 为什么需要这一层

AICC 已有三种审核机制，但它们的**审核对象**各不相同：

| 机制 | 审核对象 | 触发时机 |
| --- | --- | --- |
| 互审工作流（`review-workflow.md`） | 当前回合**刚生成**的产物（in-flight） | 与生成同回合 |
| 文档审查规程（`templates/review/`） | **整个 `dev_docs/` 语料库** | 实现后 / 里程碑 |
| **本协议** | **磁盘上某个具名、独立的落盘方案**（可寻址 / 可重入） | **任意时刻、可跨会话、与生成解耦** |

独缺的中间粒度——"磁盘上某个具体、独立的方案"——正是"实现前门禁"最自然的作用单元。本协议补上它，**复用互审引擎做 machinery，只新增"对象 / 寻址 / 写回 / 可重入"这一薄层**，不新建竞争性评审系统。

---

## 2. 审核对象与两个实例

审核对象 = **单个已落盘的方案产物**。它有两个实例，共用同一套寻址 / 状态 / 写回模式：

1. **日常 active plan**：`dev_docs/plans/active/<YYYY-MM-DD>_<type>_<name>.md` 单文件。
2. **Phase 1 `_analysis` 三件套**：`dev_docs/_analysis/{generation_plan,generation_progress,health_check_report}.md`（由已落地的 `phase1_*` 门承接，本协议为其同构上位抽象，见 §7）。

两个实例的差异由"对象 profile"参数化，不各自另造流程。

---

## 3. 寻址与可重入

- **寻址**：审核对准一个明确的文件路径 `<PLAN_PATH>`（如 `dev_docs/plans/active/2026-06-13_feature_export.md`）。任何会话、任何工具都能"对准它"重跑审核与优化。
- **可重入**：方案可能是上周建的、被多次修订过、由另一工具 / 会话 / 人手写的。审核**不依赖聊天记忆**——审没审过、审到什么程度，只能落盘读取（见 §4）。这条"磁盘可恢复"被提升为一等审查项：审核记录必须写回方案自身，不得只留在对话里。

---

## 4. 持久化状态：`review_status`（两门禁分离）

方案 frontmatter 新增三字段：

| 字段 | 取值 | 含义 |
| --- | --- | --- |
| `review_status` | `not_reviewed` \| `reviewed` \| `skipped` | 自审核门禁状态 |
| `review_rounds` | 整数 | 已执行的审查轮次（0 / 1 / 2） |
| `review_reason` | 文本 | `skipped` 时**必填**的跳过理由；其它态可空 |

**两门禁分离（关键）**：`review_status: reviewed` **≠ 用户已批准进入实现**。它们是两个独立的持久状态——前者是"方案已被审核过"，后者是"用户已确认可以动手"。审核通过只解除"未审"这一门，是否进入实现仍需用户确认。

**与目录态正交**：方案的 `active / done / archive` 生命周期态由**目录位置**（`dev_docs/plans/{active,done,archive}/`）+ 正文 `**状态**` bullet 表示，**frontmatter 无 `status:` 字段**。`review_status` 是新增的 frontmatter 子状态，与目录态正交，不新增目录（符合"类型 / 状态在 frontmatter 不在目录"原则）。

---

## 5. 触发分级：复杂度决定深度，高风险面决定开关

不照搬"默认双轮强审一切"（违背 AICC 分层轻量）。触发规则两条叠加：

- **复杂度决定深度**（复用互审的复杂度评分 0–30 skip / 31–65 standard / 66–100 deep）：
  - `trivial` / `simple` → 允许 `skipped`（必须记 `review_reason`）。
  - `medium` → 单轮（`review_rounds ≥ 1`）。
  - `complex` / `critical` → 双轮（第二轮基于第一轮修订后的方案，不得复述第一轮结论）。
- **高风险面清单决定开关**：方案触及下列任一面，**任何复杂度都强制至少单轮，不得 `skipped`**：

  > `auth` / `payment` / `data-schema` / `migration` / `external-API` / `privacy-secrets` / `concurrency` / `breaking-change`

  框架只提供这份**默认清单**；项目特定高风险域由项目分析阶段填充进 `project_analysis_report` / `AI_RULES`，**不**把任何下游项目的领域形状硬编码进框架。

---

## 6. 写回块与想法路由

- **写回块**：审核完成后在方案正文追加标准"方案自审核记录"块（审核日期 / 方式 / 轮次 / 是否隔离审查及未隔离原因 / 发现摘要（按 P0/P1/P2/P3，每条含 问题·证据·影响·建议修改·是否阻塞）/ 写回修改 / 仍需用户确认项 / 是否允许进入实现）。模板见 [`templates/PLAN_TEMPLATE.md`](../templates/PLAN_TEMPLATE.md)。
- **想法路由纪律**：审核发现若属"未来能力"，**不得塞入当前实施步骤**，分流到方案的"非目标 / 剩余风险"或 [`memos/`](framework_spec.md)（备忘录）/ `knowledge/` architecture notes。重新实现前须把它重新提炼为新方案并**重跑本协议**。
- **权威边界**：审核结论让位于项目北极星 / ADR / spec；本协议不凌驾于既有架构决策之上。

---

## 7. 两层工具约束（静态检查器能做什么、不能做什么）

校正一个隐含前提：检查器是对文档树的**静态 linter**，**拦不住"AI 开始写代码"这一运行时动作**——能可靠阻断的只有磁盘不变量。故工具约束分两层：

1. **滞后硬阻断（commit 时，可强制）**：**位于 `dev_docs/plans/done/` 的方案**若 `review_status` 非 `reviewed | skipped(带理由)`，由 `doc_health_checker`（Python / JS 双实现）报 **blocker** 级 issue `plan_done_without_review`。done 态以**目录成员身份**判定（文件位于 / 被移入 `plans/done/`），不依赖任何 frontmatter `status`。该 issue 由插件 / Codex 形态的 `pre_commit_gate` hook 在 commit 时承接强制（见 §8）。
2. **流程软约束（进入实现前，顾问 / 流程级）**：「实现前先审」是运行时意图，静态门拦不住，改由入口 / 工作流路由**流程硬约束**（要求进入实现前先把对象审到 `reviewed | skipped`），检查器只对**事后可观测后果**（已实现 / 已 done 却无复查记录）出 info / warning 软告警。无 `review_status` 的历史 active 方案给 info / warning（除非此刻被移入 `done/`，则升为上述 blocker）。

> **强制范围界定**：只有第①层"done-without-review"在 commit 时被 hook 强制；第②层"实现前先审"在 SSOT / 插件 / Codex **三形态均为顾问 / 流程级，无平台差**。

---

## 8. 三种交付形态的落点

本协议是**框架 SSOT**层定义；其在三种交付形态的落点：

| 本层落点 | 框架 SSOT | 插件 | Codex 扁平包 |
| --- | --- | --- | --- |
| 对象语义层 | 本文档 | 技能 `skills/plan-review/`（委派 mutual-review 引擎） | `aicc-plan-review/`（顾问式） |
| done 硬阻断 | `doc_health_checker.plan_done_without_review`（Py/JS） | `pre_commit_gate` 调用 `doc_health.plan_done_without_review` | `.codex/` 包内同脚本 hook 强制 |
| `review_status` 字段 | `PLAN_TEMPLATE.md` frontmatter | init 脚手架模板投影 | 扁平模板 |
| 复杂度 / 高风险面配置 | 本文 §5 默认值 | `settings.json` `aicc.planReview` | settings 默认值 |
| 进入实现流程门 | 入口 / 工作流路由 | init / incremental-update 技能正文引用本协议 | 技能正文（顾问） |

---

## 9. 边界（不做）

- 不把"默认双轮强审一切"设为默认值（改为 §5 分级触发）。
- 不硬编码任何下游项目的领域名词（改为项目分析阶段参数化）。
- 不在本协议内重新实现互审引擎（一律委派 `review-workflow.md`）。
- 不新增目录轴（`review_status` 是 frontmatter 子状态）。
