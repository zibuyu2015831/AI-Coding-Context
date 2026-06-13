---
title: LingoTrace 方案自审核协议吸收分析与决策记录
summary: 记录 LingoTrace 下游项目首创的「单个 active plan 自审核协议」与 AICC 现有评审子系统的对比分析，确认其真正增量在于引入「单个已落盘 active plan」这一全新审核对象，并给出复用既有互审引擎、按复杂度分级的吸收方案与决策依据。
keywords: aicc | plan-review | active-plan | review-object | self-review | lingotrace | absorption
scope: AI-Coding-Context 框架 plans/ 子系统的方案审核能力演进
related_files: core/framework_spec.md | workflows/review-workflow.md | workflows/review_standards | templates/PLAN_TEMPLATE.md | templates/plans_README_TEMPLATE.md | templates/review/review_plan_TEMPLATE.md | agents/runtime/plan_reviewer.md
dependencies: dev/plan/done/aicc-generation-plan-review-process-gap-plan.md | dev/plan/done/aicc-phase1-review-gate-implementation-plan.md | dev/plan/done/aicc-phase1-review-gate-followup-plan.md
verified_at: 2026-06-13
status: proposed（开放问题已定案，待转可执行实施计划，2026-06-13）
---

# LingoTrace 方案自审核协议吸收分析与决策记录

状态：Proposed（分析与决策已完成，待实现）
创建日期：2026-06-13
最后更新日期：2026-06-13
来源：LingoTrace 下游项目 `docs/plans/plan-review-protocol.md`

---

## 0. 文档定位

本文档记录一次完整的框架演进讨论：评估 LingoTrace 项目在采用 AICC 框架搭建文档体系后**首创的「active plan 自审核机制」**能否被 AICC 框架吸收。文档包含讨论过程、对比分析、关键洞察、吸收方案、决策依据与未吸收边界，作为后续实现的专项依据。

本文档属于框架开发元数据，仅存在于 `internal` 分支 `dev/plan/`，不进入 `dev` / `master` 用户面分支。

这是 AICC 设计意图中「下游项目创新 → 框架回收可泛化内核」反馈闭环的又一案例，与 `dayflow-phase1-aicc-improvement-plan.md`、`linguacafe-phase1-aicc-improvement-plan.md` 同属一类来源。

---

## 1. 触发与对象

LingoTrace 是采用 AICC 框架的下游 iOS / 本地优先应用项目。它在 `docs/plans/` 下首创了一份 `plan-review-protocol.md`（LangoTrace 方案自审核协议，状态 Accepted，2026-06-01），定义了 active plan 在进入实现前必须执行的严格自审核门禁：

- 适用于新功能、Bug 修复、重构、数据/迁移/同步、Provider/隐私/安全/发布、平台结构、文档治理等任务。
- 前置门禁：在 `docs/plans/active/` 创建/更新目标方案 → 核对事实来源 → 完成自审核 → 写回方案 → 将 `自审核状态` 由 `Not Reviewed` 改为 `Reviewed` → 等待用户确认。
- 默认双轮审查：第一轮系统架构师审查；第二轮测试/安全/落地性审查，且必须基于第一轮修订后的方案。
- 发现按 P0/P1/P2/P3 分级，每条含「问题 / 证据 / 影响 / 建议修改 / 是否阻塞」。
- 标准化「严格方案自审核记录」写回块；未来想法不得塞入当前实施步骤，须路由到非目标/剩余风险/`architecture/notes`，并在重新实现前重新提炼为新方案并重跑协议。
- 强调磁盘可恢复（不依赖聊天记忆）、隔离审查优先且可优雅降级、权威边界（让位于北极星/ADR/spec）。

核心问题：**这套机制能否、以及如何吸收进 AICC 框架。**

---

## 2. 现状盘点：AICC 已有的评审设施

吸收讨论的前提是认清 AICC **并非没有评审机制**，而是已有一套相当完整的评审设施：

| 资产 | 作用 |
|---|---|
| `workflows/review-workflow.md`（013 AI 互审工作流） | 方案生成后的互审：复杂度打分（静态40%+语义60%）→ 审查深度（skip/standard/deep/ultra）、可靠度自评与 auto-fix 逻辑、commit 质量 / Git 安全 / ADR 符合性三个审查维度 |
| `workflows/review_standards/*` | feature / bugfix / refactor / doc 分类审查标准 |
| `agents/runtime/plan_reviewer.md` + `agents/examples/plan_reviewer_examples.md` | 方案审查员角色与示例 |
| `templates/review/`（review_plan + review_principles） | 整个 `dev_docs/` 文档体系的事后一致性审查（多阶段、子代理、可恢复状态机、`_meta` + `REVIEW_LOG`） |
| `plans/` active→done→archive + frontmatter `status` | 方案生命周期状态机 |

结论：AICC 已有「评审引擎」（打分/维度/auto-fix）与「方案生命周期」，但二者**解耦**——评审是一次性决策流程，其产出（报告+元数据）**没有作为持久化门禁绑回方案文档本身**。

---

## 3. 关键洞察：审核对象的差异（本次讨论的核心结论）

最初的分析把 LingoTrace 的核心创新归为「把已审核状态持久化为门禁字段」。进一步推敲后修正为更根本的差异——**审核对象（review object）不同**。

### 3.1 三种现有审核对象

| 机制 | 审核对象 | 寻址方式 | 触发时机 | 产出落点 |
|---|---|---|---|---|
| 互审 workflow（013） | 当前回合**刚生成的方案**（in-flight） | 进程内隐式——「我刚产出的那份」 | 生成管线内，**与生成同回合** | 报告+元数据（回合内瞬时） |
| plan_reviewer persona | 用户**贴进对话的方案正文** | 对话消息内容 | 用户主动提交 | 对话回复 |
| 文档审查规程（templates/review） | **整个 `dev_docs/` 语料库** | 目录级 | 实现后 / 里程碑 | `_meta` + `REVIEW_LOG` |
| **LingoTrace 协议** | **`plans/active/` 下某个具名、已落盘的单个 active plan** | **文件路径 `<PLAN_PATH>`（可寻址）** | **任意时刻、可跨会话、与生成解耦** | **写回该 plan 自身**（状态字段 + 自审记录块） |

### 3.2 缺失的中间粒度

AICC 现有审核对象要么是「生成那一刻的产物」（互审 / persona），要么是「整个语料库」（文档审查）。**独缺「磁盘上某个具体、独立的 active plan」这个中间粒度**——而这正是 LingoTrace 协议的对象。

```
生成回合产物（互审，生成时）
   └─ 单个落盘 plan（可寻址 / 可重入，实现前按需）  ← LingoTrace 填补的空白
        └─ 整个语料库（文档审查，实现后）
```

### 3.3 这个对象选择带来的三个性质

1. **可寻址 + 可重入**：对准磁盘上一个具名实体，任何会话、任何工具都能「对准它」重跑审核与优化。互审做不到——它只在生成那一刻、对那一份刚生成的东西触发。
2. **解耦于创建时刻**：一份 active plan 可能是上周建的、被多次修订过、由另一个工具/会话写的、甚至人手写的。LingoTrace 能审这种「陈年 / 外来」方案；互审天然只覆盖「我刚生成的」。
3. **持久化是推论而非根因**：正因为审核对象是可寻址的落盘实体、且审核与生成解耦，「这份方案审没审过」无法靠会话流程隐式得知，**只能把 `自审核状态` 落盘**。是「对象」决定了「状态必须持久化」，不是反过来。

---

## 4. LingoTrace 协议的可泛化增量

剥离项目特定内容（Swift/Xcode/StoreKit/TTS/OCR/Keychain/本地优先北极星/AI Provider 契约）后，可泛化内核为：

1. **新审核对象**：单个已落盘 active plan，作为可寻址、可重入的独立审核与优化单元（§3）。
2. **持久化门禁状态**：`自审核状态: Not Reviewed → Reviewed` 写进方案 frontmatter，作为进入实现的硬前置。
3. **磁盘可恢复 / 不依赖聊天记忆**被提升为一等审查项。
4. **两门禁分离**：`Reviewed` ≠ 用户已批准实现，是两个独立持久状态。
5. **双轮硬约束**：第二轮必须基于第一轮修订后的方案，不得复述第一轮结论。
6. **未来想法路由纪律**：审查发现若属未来能力，分流到非目标 / 剩余风险 / `architecture/notes`，重新实现前须重新提炼为新方案并重跑协议——为 AICC 的 `memos/` 提供明确汇入口。
7. **标准化写回块** + **权威边界** + **隔离审查优雅降级**（后者已 framework-ready）。

---

## 5. 决策：吸收，但「提炼内核 + 复用引擎」，不照搬

**决策：吸收。** 它填补的是一个真实空白——AICC 现有评审机制没有一个以「磁盘上某个具体、独立的 active plan」为对象的、可寻址可重入的审核单元。

**方式：引入新审核对象 + 复用既有互审引擎 + 按复杂度分级，而非整本搬入 LingoTrace 的重型协议。**

吸收的本质不是「加一个 gate 字段」，而是给 AICC 引入一个新的一等审核对象——「单个已落盘 active plan 的独立审核与优化单元」，补上三种粒度里缺的中间格。落地上反而更干净：**复用互审引擎**（打分 / 维度 / auto-fix）做 machinery，**「对象、寻址、写回、可重入」这一层是全新增量**。

这也彻底化解「会不会变成两套评审系统」的顾虑：三种机制**审核对象不同，不竞争**，是三个粒度的互补：

1. 生成回合产物（互审，生成时）
2. 单个落盘 plan（实现前，按需，可重入）← 本次新增
3. 整个语料库（文档审查，实现后）

LingoTrace 协议 §8 已自洽地给出三段顺序（实现前方案自审 → 用户确认 → 实现 → 事后文档审查），可直接作为 AICC 三机制的衔接骨架。

---

## 6. 决策依据

- **真实空白**：现有审核对象在「单个落盘方案」粒度上缺位（§3.2），且该粒度恰是「实现前门禁」最自然的作用单元。
- **可寻址 / 可重入是刚需**：日常使用中用户常以短指令「审核 plans/active 下某方案、判断是否可进入实现」发起请求；这类请求今天无专门流程承接（与 `aicc-generation-plan-review-process-gap-plan.md` 记录的 `_analysis` 复查缺口同源同构，只是对象从 Phase 1 `_analysis` 产物换成了日常 `plans/active/` 方案）。
- **低重复成本**：打分、审查维度、auto-fix、分类审查标准、审查员角色均已存在，新增层很薄。
- **符合框架反馈闭环定位**：下游创新回收，与既有 dayflow / linguacafe 改进计划一脉相承。
- **可控风险**：通过「复用引擎 + 复杂度分级 + 域参数化」三条约束，规避照搬带来的哲学冲突（见 §8）。

---

## 7. 吸收方案（落地设计）

不新增竞争性评审系统，而是把可泛化内核分散嵌入现有资产：

### 7.1 新增审核对象语义层（核心）
- **新增 `core/plan_review_protocol.md`（Q2 已定案）**，定位为横跨 `plans/` 与 `_analysis/` 的**统一薄层**，**只定义**：审核对象（单个落盘方案产物——含日常 active plan 与 Phase 1 `_analysis` 三件套两个实例）、寻址（`<PLAN_PATH>`）、可重入语义、两门禁分离、写回要求、未来想法路由。
- 「怎么审」一律指向 `workflows/review-workflow.md`（打分 / 维度 / auto-fix）与 `workflows/review_standards/`，避免重复造引擎。
- `framework_spec.md` 的 plans/ 章节仅补**一行指针 + 一条硬规则**（`done` 方案 `review_status` 必须为 `reviewed|skipped(理由)`，见 §7.3 / Q4），不在该节展开协议正文，避免「目录规范」膨胀成「评审协议」。

### 7.2 方案模板
- `templates/PLAN_TEMPLATE.md` frontmatter 增字段：`review_status: not_reviewed | reviewed | skipped`、`review_rounds`、`review_reason`。
- 正文增标准「方案自审核记录」块（审核日期 / 方式 / 轮次 / 未隔离原因 / 发现摘要 / 写回修改 / 仍需确认 / 是否允许进入实现）。

### 7.3 框架规范
- `core/framework_spec.md` 的 `plans/` 章节增状态规则：「active 内方案进入实现前，`review_status` 必须为 `reviewed`，或带理由的 `skipped`」。
- **复杂度分级 + 高风险面叠加触发（Q1 已定案）**：**复杂度决定深度**——trivial / simple → 允许 `skipped`（记录理由）；medium → 单轮；complex / critical → 双轮。**高风险面清单**（auth / payment / data-schema / migration / external-API / privacy-secrets / concurrency / breaking-change，复用 §7.5）**决定开关**——任何复杂度只要触面即强制至少单轮，不得 `skipped`。
- **工具阻断分两层（Q4 已定案）**：`done` 方案 `review_status` 非 `reviewed|skipped(理由)` 由 `doc_health_checker`（Python/JS 双实现）**硬阻断**（新增 issue `plan_done_without_review`，severity=blocker）；「进入实现」无法被静态检查器拦截，改由入口/工作流路由**流程硬约束** + 检查器对事后可观测后果（已实现/已 done 却无复查记录）**软告警**。无 `review_status` 的历史方案给 info/warning（除非此刻被移入 done），复用 generation_plan 门已建的 severity 分层。
- 明确「`reviewed` ≠ 用户已批准实现」两门禁分离。

### 7.4 路由与索引
- 把「未来想法」路由编码为「评审发现 → `memos/` / `knowledge/`（architecture notes）」的明确汇入口。
- `templates/plans_README_TEMPLATE.md` 状态索引补充 `review_status` 维度。

### 7.5 域泛化
- 框架只提供**默认高风险面清单**：auth / payment / data-schema / migration / external-API / privacy-secrets / concurrency / breaking-change（恰好对应互审静态分析的「核心模块 + 破坏性变更」维度）。
- 具体高风险域交由项目分析阶段填充进 `project_analysis_report` / AI_RULES，**不**把 LingoTrace 的 iOS 形状硬编码进框架。

---

## 8. 未吸收 / 需改造的部分（边界）

- **不吸收** LingoTrace「默认双轮强审一切」的默认值——违背 AICC 分层轻量哲学（trivial/simple 应可跳过）。改造为复杂度分级触发。
- **不吸收** 任何硬编码域名词（StoreKit / Keychain / TTS / 本地优先北极星等）——改为项目分析阶段参数化。
- **不做成** 对所有项目类型强制生效的项——作为能力层，按项目复杂度分级开启（complex/critical 默认开，trivial/simple 默认关）。

---

## 9. 风险与张力

| 张力 | 说明 | 缓解 |
|---|---|---|
| 分层轻量 vs. 默认重型 | LingoTrace 默认近乎一切双轮强审；AICC 支持 trivial 项目并在低复杂度跳过审查 | 吸收持久化门禁机制，保留复杂度分级触发；trivial 自动 `skipped(理由)` |
| 两套评审系统的担忧 | 新增 plan 审核可能与互审重复 | 三机制审核对象不同、不竞争（§5）；新层复用互审引擎 |
| iOS 形状烙入框架 | 协议含大量项目特定高风险域 | 框架只给默认清单，具体域由项目分析填充（§7.5） |
| 状态轴增生 | `review_status` 与 active/done/archive 目录态正交 | 作为 active/ 内的 frontmatter 子状态，不新增目录，符合「类型/状态在 frontmatter 不在目录」原则 |

---

## 10. 与既有计划的关系

- `aicc-generation-plan-review-process-gap-plan.md`：同源同构——都是「用户短指令发起对既有落盘方案的复查」缺口；前者对象是 Phase 1 `_analysis` 产物，本方案对象是日常 `plans/active/` 方案。**Q3 已定案：共用抽象脊柱 + 对象 profile 参数化**——复用该门已落地的脊柱（寻址 → 机器检查 → 人工语义复查 → 持久化 `review_status` → 写回 → severity 阻断），以两个 profile（Phase 1 三件套 / daily-plan 单文件）参数化对象差异，共享路由词汇/写回格式/证据字段/severity/双实现纪律；daily-plan 门新增**平行 `plan_review_*` issue 家族**，靠对象探测（`_analysis/` vs `plans/active/`）分派，不重载 `phase1_*` 名字。即本方案作为该已落地门的**扩展**实现，而非平行再造，避免两套并行。
- `aicc-phase1-review-gate-implementation-plan.md` / `aicc-phase1-review-gate-followup-plan.md`：审核门落地与回写经验可直接复用到本方案的 `review_status` 门禁与写回块设计。

---

## 11. 关键决策（原开放问题，2026-06-13 已定案）

> 原四个开放问题已由用户**采纳架构师推荐方案**并定案。以下为决策结论，完整依据见 §11.1，落地点见 §7、§10。

1. **默认开启策略 → 复杂度分级 + 高风险面叠加触发**（不采用全局强制）。落入 PLAN_TEMPLATE 与 framework_spec 默认值（§7.3）。
2. **语义层落点 → 新增 `core/plan_review_protocol.md`**，定位为横跨 `plans/` 与 `_analysis/` 的统一薄层；framework_spec plans/ 章节仅补指针 + 硬规则（§7.1）。
3. **与 generation_plan 复查缺口 → 共用抽象脊柱 + 对象 profile 参数化**，作为已落地 Phase 1 门的扩展，新增平行 `plan_review_*` issue 家族（§10）。
4. **工具阻断 → 分两层**：`done` 方案 `review_status` 非 `reviewed|skipped(理由)` 由 `doc_health_checker` 硬阻断；「进入实现」走流程门 + 事后软告警（§7.3）。

## 11.1 决策依据（2026-06-13 采纳）

> 以下为站在 AICC 定位（「让 AI 在陌生代码库中稳定获得可验证上下文」的分层轻量框架）与既有事实（**generation_plan 复查门已落地并验证**，见 §10）之上对 §11 的决策依据。四问非并列：**Q1、Q3 为承重决策，Q2、Q4 由其收敛**；全部作为已发 Phase 1 门的**扩展**实现，而非另起一套。

**Q1 — 决策「复杂度分级 + 高风险面叠加触发」。** LingoTrace 默认全局强审，是因为它是单一高风险 App（隐私/支付/本地优先），整项目都在北极星射程内；AICC 服务多项目类型，全局强制违背分层轻量，且会让 `Reviewed` 退化为橡皮图章。细化方案 §7.3：**复杂度决定深度**（medium 单轮 / complex·critical 双轮），**高风险面清单**（auth / payment / data-schema / migration / external-API / privacy-secrets / concurrency / breaking-change）**决定开关**——任何复杂度只要触面即强制至少单轮；trivial/simple 不触面则默认 `skipped(理由)`。此举复现了 LingoTrace 全局强制背后的真实动机，又复用互审引擎既有的复杂度评分（0–30 skip / 31–65 standard / 66–100 deep）。

**Q2 — 决策新建 `core/plan_review_protocol.md`，定位为横跨 `plans/` 与 `_analysis/` 的统一薄层。** 折叠进 framework_spec plans/ 章节会让「目录规范」膨胀成「评审协议」（混轴）；折叠进 review-workflow 则与引擎正交。关键：新对象天然横跨两个子系统——日常 active plan 与 Phase 1 `_analysis` 三件套是**同一模式的两个实例**，故协议不应只住在 plans/ 章节。该文档**只定义**对象/寻址（`<PLAN_PATH>`）/重入/两门禁分离/写回/想法路由→`memos/`；「怎么审」一律指向 review-workflow.md。framework_spec plans/ 章节仅补一行指针 + 一条硬规则（done 必须 reviewed）。此选择顺手统一了 Q3 的落点。

**Q3 — 决策「共用抽象脊柱 + 对象 profile 参数化」，不各自独立、也不强压成一套字面流程。** generation_plan 门**已建成**（routing / 复查证据包 / run_record_contract 字段 / `phase1_*` issue 家族 / severity 分层），故新对象应复用其脊柱：寻址→机器检查（复用 doc_health/semantic checker）→人工语义复查→持久化 review_status→写回→severity 阻断。两个 profile：Phase 1（三件套一致性、三文件权责、已发 `phase1_*` 规则）与 daily-plan（单文件、`review_status` frontmatter、两门禁）。共享路由词汇/写回格式/证据字段命名/severity/双实现纪律。**实现要点**：daily-plan 门新增**平行 issue 家族**（如 `plan_review_*`），靠对象探测（`_analysis/` vs `plans/active/`）分派，**不重载 `phase1_*` 名字**。即把已发的 Phase 1 门当样板扩展，消除 §10「两套并行」之虑。

**Q4 — 决策「是，但分两层落点」。** 校正开放问题的隐含前提：检查器是对文档树的静态 linter，**拦不住「AI 开始写代码」这一运行时动作**，能可靠阻断的只有磁盘不变量。① **移入 done → 工具硬阻断**：新增 `plan_done_without_review`，`status: done` 而 `review_status` 非 `reviewed|skipped(理由)` → blocker，放进 `doc_health_checker`（已管 frontmatter/status 一致性），Python/JS 双实现。② **进入实现 → 流程硬约束 + 工具软告警**：硬门在入口/工作流路由，检查器只对事后可观测后果（已实现/已 done 却无复查记录）告警，预实现阶段最多 warning。③ **兼容层**复用 §G 已建的 severity 分层：无 `review_status` 的历史方案给 info/warning（除非此刻被移入 done），trivial `skipped(理由)` 放行，Py/Node 单运行时两实现结论须一致。

**一句话汇总**：Q1 分级+风险面触发；Q2 统一薄层协议文档；Q3 统一脊柱+双 profile；Q4 done 硬阻断、进入实现走流程门+软告警。承重次序：Q1、Q3 已承重定案 → Q2、Q4 随之收敛 → 全部作为已发 generation_plan 门的扩展落地（详见 §7 各落点）。

---

## 12. 下一步

- [x] 就 §11 开放问题与用户确认 —— 2026-06-13 用户采纳架构师推荐方案，四问全部定案（见 §11 / §11.1）。
- [ ] 将本分析转化为可执行实施计划（精确到 §7 各落点的 diff 设计与验证命令），作为已落地 generation_plan 门的**扩展**实现：`core/plan_review_protocol.md`（统一薄层）+ framework_spec plans/ 指针与硬规则 + PLAN_TEMPLATE/plans_README_TEMPLATE 增 `review_status` 字段 + `doc_health_checker` 新增 `plan_done_without_review`（Python/JS 双实现 + fixture）+ 入口/工作流路由的流程门。
- [x] 在 `dev/plan/README.md` 索引登记本文档。
