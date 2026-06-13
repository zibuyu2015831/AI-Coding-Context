---
title: LingoTrace 方案自审核协议吸收分析与决策记录
summary: 记录 LingoTrace 下游项目首创的「单个 active plan 自审核协议」与 AICC 现有评审子系统的对比分析，确认其真正增量在于引入「单个已落盘 active plan」这一全新审核对象，并给出复用既有互审引擎、按复杂度分级的吸收方案与决策依据。
keywords: aicc | plan-review | active-plan | review-object | self-review | lingotrace | absorption
scope: AI-Coding-Context 框架 plans/ 子系统的方案审核能力演进
related_files: core/framework_spec.md | workflows/review-workflow.md | workflows/review_standards | templates/PLAN_TEMPLATE.md | templates/plans_README_TEMPLATE.md | templates/review/review_plan_TEMPLATE.md | agents/runtime/plan_reviewer.md
dependencies: dev/plan/done/aicc-generation-plan-review-process-gap-plan.md | dev/plan/done/aicc-phase1-review-gate-implementation-plan.md | dev/plan/done/aicc-phase1-review-gate-followup-plan.md
verified_at: 2026-06-13
status: proposed（提案，待决策）
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
- 可选新增 `core/plan_review_protocol.md`，**只定义**：审核对象（单个落盘 active plan）、寻址（`<PLAN_PATH>`）、可重入语义、两门禁分离、写回要求、未来想法路由。
- 「怎么审」一律指向 `workflows/review-workflow.md`（打分 / 维度 / auto-fix）与 `workflows/review_standards/`，避免重复造引擎。

### 7.2 方案模板
- `templates/PLAN_TEMPLATE.md` frontmatter 增字段：`review_status: not_reviewed | reviewed | skipped`、`review_rounds`、`review_reason`。
- 正文增标准「方案自审核记录」块（审核日期 / 方式 / 轮次 / 未隔离原因 / 发现摘要 / 写回修改 / 仍需确认 / 是否允许进入实现）。

### 7.3 框架规范
- `core/framework_spec.md` 的 `plans/` 章节增状态规则：「active 内方案进入实现前，`review_status` 必须为 `reviewed`，或带理由的 `skipped`」。
- **绑定复杂度层级**（复用既有复杂度评估）：trivial / simple → 允许 `skipped`（记录理由）；medium → 单轮；complex / critical → 双轮。
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

- `aicc-generation-plan-review-process-gap-plan.md`：同源同构——都是「用户短指令发起对既有落盘方案的复查」缺口；前者对象是 Phase 1 `_analysis` 产物，本方案对象是日常 `plans/active/` 方案。实现时应统一路由与回写格式，避免两套并行。
- `aicc-phase1-review-gate-implementation-plan.md` / `aicc-phase1-review-gate-followup-plan.md`：审核门落地与回写经验可直接复用到本方案的 `review_status` 门禁与写回块设计。

---

## 11. 开放问题（待决策）

1. **默认开启策略**：是「按复杂度分级开启」（推荐）还是「全局强制」？直接决定 PLAN_TEMPLATE 与 framework_spec 的默认值。
2. **是否新增 `core/plan_review_protocol.md`**，还是把语义层折叠进 `framework_spec.md` plans/ 章节 + review-workflow.md？
3. **与 generation_plan 复查缺口的合并程度**：共用一套「落盘方案复查」流程，还是各自独立、仅共享回写格式？
4. **工具阻断**：`review_status != reviewed` 时是否由 `tools/py/*` 检查器阻断「进入实现 / 移入 done」？

---

## 12. 下一步

- [ ] 就 §11 开放问题（尤其问题 1、3）与用户确认。
- [ ] 确认后，将本分析转化为可执行实施计划（精确到 §7 各落点的 diff 设计与验证命令）。
- [ ] 在 `dev/plan/README.md` 索引登记本文档（随本次提交完成）。
