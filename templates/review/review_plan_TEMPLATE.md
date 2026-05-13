---
title: 文档审核规程（{PROJECT_NAME}）
summary: 定义 {PROJECT_NAME} 项目文档体系系统化审核的完整执行规程，包括多阶段协议、三套子代理 Prompt 模板、触发机制、文档分层策略、可恢复状态机、写入权限、_meta.md 与 REVIEW_LOG.md 维护规范，是启动每轮审核的操作手册。
keywords: 文档审核 | 执行规程 | 子代理 | 审核流程 | 模板
scope: {PROJECT_NAME} 项目 dev_docs/ 文档体系的审核执行规程
related_files: 无
dependencies: 无
verified_at: 2026-05-12
---

# 文档审核规程（{PROJECT_NAME}）

> **版本**: v1.0
> **生成日期**: {GENERATION_DATE}
> **项目**: {PROJECT_NAME}
> **配套文档**: `sys_review_principles.md`
> **执行模型**: 多阶段并行子代理 + 主会话编排 + 轮次目录持久化

---

## 0. 使用方法

将本文档与 `sys_review_principles.md` 一起发给 AI，即可启动一轮文档审核。

**启动指令**：
```
我需要对 {PROJECT_NAME} 的文档体系进行一轮[基线全审/事件触发/手动]审核。
请阅读已附上的 sys_review_plan.md 和 sys_review_principles.md，
然后从阶段 0 开始执行。
```

---

## 1. 审核目标（摘要）

- **准确性**：每条事实性断言必须与代码一致（能定位到 `文件:行号`）
- **完整性**：文档覆盖模块关键行为，新会话 AI 仅凭文档即可完成典型任务
- **终极验收**：随机抽 1 份文档，新开会话让 AI 不追问用户完成典型变更任务

**落盘优先**：任何需要用户确认、跨会话恢复或作为后续子代理输入的内容，必须先写入 `rounds/<round-id>/` 中的明确文件，再通过消息通知用户。

详细原则见 `sys_review_principles.md`。

---

## 2. 审核范围

### 2.1 目标文档分层

<!-- AICC 在生成时根据项目实际文档填写以下分层表 -->

| # | 文档 | 层级 | 说明 |
|---|------|------|------|
| 1 | `AI_Coding_Context.md` | L1 核心入口 | 项目全景索引，必须最准确 |
| 2 | {L1_DOC_2} | L1 核心架构 | {L1_DOC_2_DESC} |
| 3 | {L2_DOC_1} | L2 关键功能 | {L2_DOC_1_DESC} |
| 4 | {L2_DOC_2} | L2 关键功能 | {L2_DOC_2_DESC} |
| 5 | {L3_DOC_1} | L3 支撑功能 | {L3_DOC_1_DESC} |

> **并行度建议**：L1 文档（{L1_COUNT} 份）单独一批先做；L2/{L3_RANGE} 文档分批，每批 ≤4 个子代理并行

### 2.2 严格排除的目录

`_analysis/`、`knowledge/`、`plans/`、`review/`、`thinking/` — 这些是过程产物，不是真相源文档。
子代理可读取它们作为辅助上下文，但不得作为审核目标，不得修改其中内容（除追加 bugfix 记录和进度记录）。

---

## 3. 多阶段执行协议

### 阶段总览

```
阶段 0   → 准备与快照
阶段 1   → 并行深审（深审子代理，严格只读）
阶段 1.5 → 疑问汇集与去重（主会话）
阶段 2   → 多轮澄清循环（主会话 ↔ 用户，直到无空白条目）
阶段 2.5 → 多轮裁定快照生成（AI 起草 ↔ 用户修订，对齐为止）
阶段 3a  → 逐文档修复计划生成（计划子代理）
阶段 3b  → 用户审核修复计划（多轮，用户拍板）
阶段 3c  → 并行执行修复（执行子代理，严格遵循计划）
阶段 4   → 轻量复审（对照复查方法清单验证）
阶段 5   → 副产物归档 + 用户 git 合并
```

**角色分工**：

| 阶段 | 负责方 | 理由 |
|------|--------|------|
| 0 准备 | 主会话 | 唯一的全局初始化入口 |
| 1 深审 | **深审子代理**（每文档一个）| 上下文隔离 |
| 1.5 疑问汇集 | 主会话 | 跨文档视角合并同质疑问 |
| 2 澄清循环 | 主会话 ↔ 用户 | 子代理无法实时对话 |
| 2.5 裁定快照 | 主会话起草 ↔ 用户审批 | 需全局视角；用户最终拍板 |
| 3a 修复计划 | **计划子代理**（每文档一个）| 隔离上下文；携带三件套+裁定 |
| 3b 审核计划 | 用户 | 执行前最终人工门禁 |
| 3c 执行修复 | **执行子代理**（每文档一个）| 严格按计划执行，不越权 |
| 4 复审 | 主会话 | 跨文档视角最终一致性扫描 |
| 5 归档 + 合并 | 主会话 + 用户 | AI 归档，用户决定 git 提交 |

---

### 阶段 0：准备

```bash
# 主会话执行以下操作：
ROUND_TYPE="baseline"  # baseline | event-triggered | manual
ROUND_ID="$(date +%Y)-Q$(( ($(date +%-m)+2)/3 ))-baseline"
# 事件触发格式：ROUND_ID="$(date +%Y-%m-%d)_<slug>"

ROUND_DIR="dev_docs/review/rounds/${ROUND_ID}"
mkdir -p "${ROUND_DIR}"/{reports,questions,clarifications,fix_plans}
```

1. 确认工作目录为仓库根
2. 加载 `dev_docs/AI_Coding_Context.md` 作为项目全景 primer
3. 执行 `git rev-parse HEAD` → 写入 `_meta.md`（代码快照锚点）
4. 创建本轮轮次目录骨架（见上方命令）
5. 写入 `_meta.md`（参考本文档 §6 的模板）
6. 在 `dev_docs/review/REVIEW_LOG.md` 中追加一条启动记录
7. 后续所有阶段只以轮次目录中的文件作为状态依据；主会话消息不能替代 `_meta.md`、`questions/`、`clarifications/`、`_round_decisions.md` 或 `fix_plans/`

---

### 阶段 1：并行深审（深审子代理，严格只读）

**原则**：每份目标文档分配一个独立子代理，上下文完全隔离。

**子代理输出**（必须写入磁盘，不得返回主会话内存）：
- `rounds/<round>/reports/<doc>.report.md`
- `rounds/<round>/questions/<doc>.questions.md`

**子代理返回给主会话**：仅限"产物路径 + 一句摘要 + 异常（若有）"

**降级方案（无子代理工具时）**：
> 提示用户：请为每份文档手动新开一个会话窗口，在新窗口中粘贴下方 Pass 1 Prompt
> 并指定目标文档路径。执行完成后将产物文件复制到 `rounds/<round>/reports/` 和
> `questions/` 目录，再回到本会话继续。

#### Pass 1 深审 Prompt 模板

```
你是 {PROJECT_NAME} 项目的资深文档审核员。请对一份开发文档进行**只读模式**的深度审核，
目标是让这份文档成为"AI 辅助编程时的可信真相源"。

【项目上下文】
你必须首先 Read dev_docs/AI_Coding_Context.md 作为项目全景 primer。

【本轮审核目录（由主会话注入）】
ROUND_DIR = dev_docs/review/rounds/<round-id>/
REPORT_PATH    = ROUND_DIR/reports/<doc-basename>.report.md
QUESTIONS_PATH = ROUND_DIR/questions/<doc-basename>.questions.md

【目标文档】
TARGET_DOC = <此处填入目标文档完整路径>

【审核目标】
1) 准确性：文档中每一条事实性断言（路径、端口、字段、API、配置、行为）
   必须能在源码中定位到具体的"文件:行号"；
2) 完整性：文档必须覆盖该模块的关键行为、隐性约束与历史坑点。
   判断完整性的唯一标准是——一个新会话的 AI 仅凭这份文档能否完成一次典型变更任务。

【硬性约束】
- 本次为只读审核：不得修改 TARGET_DOC，不得修改任何代码；
- 除了 REPORT_PATH 和 QUESTIONS_PATH 两个产物文件，不得写入任何其他文件；
- 允许读取 dev_docs/plans/bugfixes/ 与 dev_docs/thinking/ 作为上下文辅助；
- 不得把 dev_docs/_analysis / knowledge / plans / review / thinking 列为"目标文档"；
- 任何无法在代码中直接验证的断言，必须写入 QUESTIONS_PATH 而不是凭直觉填写；
- 你返回给调用方的消息只能包含：产物文件路径 + 一句话摘要 + 异常（如有）。
  报告正文必须写到 REPORT_PATH，疑问必须写到 QUESTIONS_PATH。

【REPORT_PATH 文件结构】（使用 Write 工具写入）
---
doc: <TARGET_DOC>
round: <round-id>
reviewer: pass1-subagent
git_head: <由主会话注入>
written_at: <今日 ISO 日期>
---

# 审核报告：<目标文档文件名>

## A. 文档问题清单（准确性）
- 问题 A1
  - 文档原文：...
  - 实际代码：`<文件:行号>` ...
  - 严重程度：严重/中等/轻微
  - 修复方向：...

## B. 建议补全的章节（完整性）
- 补全建议 B1
  - 当前缺口：...
  - 建议新增内容（草稿）：...
  - 依据的源码位置：`<文件:行号>`

## C. 疑问索引
（仅列出编号和标题，完整内容见 QUESTIONS_PATH）
- Q1 - <疑问标题>

## D. 代码问题观察（仅记录，不修复）
- 代码问题 D1
  - 代码位置：`<文件:行号>`
  - 现象：...
  - 可能影响：...
  - 建议归档文件名草稿：plans/bugfixes/<date>_<slug>.md

## E. 证据索引
- 本次审核访问过的主要源码文件列表
- git HEAD: <由主会话注入>

【QUESTIONS_PATH 文件结构】（使用 Write 工具写入，采用"可打勾"格式）
---
doc: <TARGET_DOC>
round: <round-id>
status: pending
total: <疑问总数>
answered: 0
---

# 审核疑问：<目标文档文件名>

> 请在每条疑问下方的"答复"区填写答案，并把 [ ] 改为 [x]、[~] 或 [?]。
> 空白 [ ] 条目会阻塞本文档进入阶段 2.5。

## Q1 - <一句话标题>

**触发条目**：A<编号> / B<编号>

**上下文**：
- 文档现写：...
- 代码现状：`<文件:行号>` ...
- 已查阅的历史资料：...

**具体问题**：...

**可能假设**：
- A) ...
- B) ...

**[ ] 已答复**（三态：[x] 已答复 / [~] 搁置 / [?] 不确定）

**答复**：
<留空，等待用户>

---
```

---

### 阶段 1.5：疑问汇集与去重（主会话）

1. 读取所有 `questions/*.questions.md`
2. 按话题聚类，识别跨文档同质疑问
3. 生成 `questions/_merged.questions.md`（合并视图 + 反向链接到原始文件）
4. 更新 `_meta.md` 文档状态表

---

### 阶段 2：多轮澄清循环（主会话 ↔ 用户）

**用户操作**：在 `_merged.questions.md` 或各 `*.questions.md` 中直接填写答复。

**每条疑问三态**：
- `[x]` 已答复 → 纳入修复范围
- `[~]` 搁置 → 本轮跳过，记录到 REVIEW_LOG 遗留项
- `[?]` 用户也不确定 → 保留原文，文档中加 `⚠️ 待确认` 标注

**循环退出条件**：所有条目均已脱离 `[ ]` 空白状态。

**用户答复重点**：解释"为什么"（设计意图、历史决策），而非"是什么"（"是什么"可从代码读出）。

**循环结束后——主会话整理答复**：
当所有疑问条目脱离 `[ ]` 后，主会话必须执行以下步骤，为阶段 3a 计划子代理备好输入：
1. 逐一读取每份文档对应的 `questions/<doc>.questions.md`（含用户已填写的答复）
2. 将该文档的所有已答复条目整理为结构化格式，写入 `clarifications/<doc>.answers.md`
3. `clarifications/<doc>.answers.md` 是阶段 3a **计划子代理的唯一答复读入源**，必须包含：
   - 映射关系：Q<N> → 对应的 A<N>/B<N> 问题
   - 用户答复原文
   - 疑问最终状态（[x]/[~]/[?]）

---

### 阶段 2.5：多轮裁定快照生成（主会话 ↔ 用户）

**目的**：生成 `_round_decisions.md`，作为阶段 3 所有修复子代理的全局共识锚点，从源头解决跨文档不一致。

**多轮对齐流程**：
```
AI 基于所有 report.md + answers.md 起草 _round_decisions_draft.md
       ↓
用户审查：直接在草稿上标注异议、修改内容、补充说明
       ↓
AI 响应：解释每条裁定的代码依据，或接受用户修正并更新草稿
       ↓
循环直到用户在 _meta.md 中显式批准 → 定稿为 _round_decisions.md
```

**`_round_decisions.md` 结构**：
```markdown
---
round: <round-id>
status: approved          # draft / under-review / approved
version: v1
approved_by: <user>
approved_at: <date>
---

## Part A：跨文档统一裁定（所有修复子代理必须遵守）
| 裁定 ID | 类型 | 裁定结论 | 代码证据 | 影响的文档 |
|--------|------|---------|---------|-----------|

## Part B：各文档修复摘要（子代理行动范围指引）
| 文档 | 修复项数 | 关键修复描述 | 关联裁定 |
|------|---------|------------|---------|

## Part C：遗留问题（本轮不修改）
| 来源 | 状态 | 原因 | 本轮处理方式 |
|------|------|------|------------|
```

---

### 阶段 3a：逐文档修复计划生成（计划子代理）

每份文档分配一个计划子代理，并行生成 `fix_plans/<doc>.fix_plan.md`。

**子代理输入（三件套 + 全局裁定）**：
| 输入文件 | 用途 | 由谁写入 |
|---------|------|---------|
| 目标文档本身 | 了解当前内容 | 项目原始文档 |
| `reports/<doc>.report.md` | 知道要改什么 | 阶段 1 深审子代理 |
| `clarifications/<doc>.answers.md` | 知道为什么这样改 | 阶段 2 结束后由主会话整理 |
| `_round_decisions.md` | 知道跨文档改动时用哪个说法 | 阶段 2.5 用户批准后主会话写入 |

#### Fix Plan Prompt 模板

```
你是 {PROJECT_NAME} 项目的文档方案评估员。请基于 Pass 1 报告与用户的澄清答复，
为一份目标文档生成详细的"修复计划"，供用户在阶段 3c 执行前 review 与批准。

【本轮审核目录（由主会话注入）】
ROUND_DIR     = dev_docs/review/rounds/<round-id>/
REPORT_PATH   = ROUND_DIR/reports/<doc-basename>.report.md
ANSWERS_PATH  = ROUND_DIR/clarifications/<doc-basename>.answers.md
DECISIONS_PATH = ROUND_DIR/_round_decisions.md
FIX_PLAN_PATH = ROUND_DIR/fix_plans/<doc-basename>.fix_plan.md

【目标文档】
TARGET_DOC = <文件路径>

【任务】
1. Read REPORT_PATH 获取问题清单
2. Read ANSWERS_PATH 获取用户回答
3. Read DECISIONS_PATH 获取跨文档裁定（所有修复必须遵守裁定）
4. Read TARGET_DOC 获取原文
5. 必要时 Read 相关源码二次核对证据
6. 对每一条（A 问题 / B 补全建议）给出裁定：
   - 采纳（有证据且用户未反对）→ 生成详细修复方案
   - 放弃（缺证据或用户澄清后不成立）→ 记录在放弃项
   - 延后（用户答复为"待后续"或"不确定"）→ 记录在延后项
7. 生成 FIX_PLAN_PATH

【FIX_PLAN_PATH 文件结构】（使用 Write 工具写入）
---
doc: <TARGET_DOC>
round: <round-id>
status: pending_approval   # pending_approval / approved / rejected
planner: plan-subagent
planned_at: <今日 ISO 日期>
fix_count: <修复条目数>
estimated_churn: <low/medium/high>
---

# 修复计划：<目标文档文件名>

## 计划概要
- 修复条目数：N（准确性 A 条 + 完整性补全 B 条）
- 不修复/遗留：M 条（含原因）
- 预估改动规模：小/中/大（约 N 行）
- 依赖裁定：D-X、D-Y（来自 _round_decisions.md）

---

## FP-1：<一句话标题>
**来源**：report.md A<N> | **关联裁定**：D-<N>（若有）

### 问题描述
<当前文档中的错误或缺失内容，以及其对 AI 理解的影响>

### 决策依据
- 代码证据：`<文件:行号>` 中写道 "..."
- 用户答复（Q<N>）："..."
- 关联裁定 D-X：...

### 修复方案（前/后对比）
**修改前（第 X-Y 行）：**
```
<原文内容>
```

**修改后：**
```
<新内容（含源码证据注释）>
```

### 复查方法
修复后，执行以下核查：
- [ ] 在文档中搜索"<旧值>"确认已替换
- [ ] 对照 `<文件:行号>` 确认文档与代码逐字一致
- [ ] 若涉及跨文档裁定，确认与 _round_decisions.md D-X 一致

---

## FP-2：...（同结构）

---

## 不修复项
| 来源 | 原因 | 本轮处理 |
|------|------|---------|
| A5 | 用户澄清后判定不成立 | 不做修改 |
| B7 | 用户标注 [~] 搁置 | 原章节加注 `<!-- TODO: 待重构后完善 -->` |
| Q3 | 用户标注 [?] 不确定 | 对应段落加 `⚠️ 此处设计意图待确认` |

## 代码问题归档建议
- D1 → 建议新建 plans/bugfixes/<date>_<slug>.md，标题草稿：...

【约束】
- Write 权限仅限 FIX_PLAN_PATH
- 不得修改 TARGET_DOC、reports/、questions/、clarifications/
- 不得修改任何代码文件
- 每一条采纳项必须附"证据（文件:行号）"；若无证据则强制降级为"放弃"或"延后"
- 返回给调用方的消息：只包含 FIX_PLAN_PATH 与一句摘要
```

---

### 阶段 3b：用户审核修复计划

用户对每份 `fix_plan.md` 的操作：
- `[x]` 在每个 FP-N 的"复查方法"第一行打勾 → 批准该修复项
- ✏️ 直接修改"修复方案"内容 → 执行子代理按修改后的版本执行
- ❌ 在 FP-N 旁标注"删除"或"本轮放弃" → 执行子代理跳过
- 💬 在文件中提问 → 返回澄清循环

**门禁**：所有 `fix_plan.md` 全部状态为 `approved`（由用户在 `_meta.md` 审批记录中标注），方可进入阶段 3c。

---

### 阶段 3c：并行执行修复（执行子代理）

**执行子代理的唯一权威输入**：对应的 `fix_plan.md`（只执行 `approved` 的 FP-N）。

#### Pass 2 执行 Prompt 模板

```
你是 {PROJECT_NAME} 项目的文档作者。请对一份开发文档进行**写入模式**的修复，
本次唯一的修改指令源是 fix_plan.md，任何偏离计划的改动都是越权。

【本轮审核目录（由主会话注入）】
ROUND_DIR     = dev_docs/review/rounds/<round-id>/
FIX_PLAN_PATH = ROUND_DIR/fix_plans/<doc-basename>.fix_plan.md
META_PATH     = ROUND_DIR/_meta.md

【目标文档】
TARGET_DOC = <文件路径>

【执行步骤】
1. Read FIX_PLAN_PATH —— 这是你本次修改的唯一权威指令源；
2. Read TARGET_DOC 获取原文；
3. 对 TARGET_DOC 按 fix_plan.md 中每一条"FP-N 采纳项"落地修改；
4. 更新 front matter 的 verified_at 为今日日期；
5. 返回："已按计划更新 TARGET_DOC；采纳 N 条、跳过 M 条、异常 K 条"。

【硬性约束】
- 只能修改 TARGET_DOC，禁止写入任何其他文件；
- 禁止修改任何代码文件；
- 禁止执行 git 命令；
- 每一条新增/修改的事实性断言必须附带源码证据（文件:行号）；
  若 plan 某条采纳项缺证据，应拒绝落地并进入"异常"路径；
- 保留 front matter 其他字段，只更新 verified_at；
- 保留原文档中 plan 未提及的正确内容，不做多余改动；
- 不要删除章节标题，除非 plan 明确要求；

【异常路径】
若执行中发现 fix_plan 与代码现状不符（例如 plan 要求写 X = 42，但源码里 X = 43），
立即停止修改并返回冲突描述："阶段 3c 异常，请主会话记录到 META_PATH"。
不得擅自按代码现状修正计划，也不得直接修改 META_PATH；由主会话写入 `_meta.md` 的"执行异常"区。
```

**降级方案**：若无子代理工具，主会话按 fix_plan.md 逐篇串行执行修复。

---

### 阶段 4：轻量复审（主会话）

1. **逐条执行复查 checklist**：逐条执行各 `fix_plans/*.fix_plan.md` 中的"复查方法"清单
2. **一致性扫描验证**：扫描 `_round_decisions.md` 中所有裁定，确认已在涉及文档中落地；将结果写入 `rounds/<round-id>/consistency_check.md`（裁定 ID → 检查结果 ✅/❌/⚠️，❌ 项需指明冲突并立即修复）
3. **终极验收**：随机抽 1 份文档，在全新会话中让 AI 仅凭此文档完成典型变更任务

---

### 阶段 5：副产物归档 + 用户合并

1. 代码问题（report.md D 章节）→ 归档到 `plans/bugfixes/<date>_<slug>.md`，在相关文档中以"参见 BUG-N"交叉引用
2. 所有目标文档的 `verified_at` 更新为审核当日日期
3. 在 `REVIEW_LOG.md` 中追加本轮摘要与指向 `rounds/<round-id>/` 的链接
4. `rounds/<round-id>/` 目录作为中间产物**永久归档保留**（不要删除）
5. **用户手动 `git add / commit / push`**（禁止 AI 自动提交）

---

## 4. 审核触发机制

### 4.1 时间触发（周期化）

| 频率 | 范围 | 说明 |
|------|------|------|
| **每季度一次** | 全量（所有目标文档）| 基线审核，跑完完整多阶段流程 |
| **每月一次** | 抽样（随机 3 份 L2/L3）| 验证腐化速度，仅做阶段 0-1 |

### 4.2 事件触发（必须做，至少跑阶段 0-1）

<!-- AICC 在生成时根据项目实际架构填写以下触发表 -->

| 触发事件 | 必须重审的文档 |
|---------|--------------|
| 新增/删除服务或模块 | 入口文档、拓扑文档、API 文档 |
| 修改数据库模型文件 | 数据模型文档 + 对应服务文档 |
| 修改 API 路由定义 | API 文档 + 对应服务文档 |
| 修改核心配置文件 | 部署文档、拓扑文档 |
| {PROJECT_SPECIFIC_TRIGGER_1} | {DOCS_TO_REVIEW_1} |
| AI 辅助编程中反复出现"文档与代码不符" | 被投诉的相关文档 |

### 4.3 手动触发

- 重要版本发布前
- 新成员 onboard 遇到文档歧义时

所有重审事件记录到 `REVIEW_LOG.md` 的"重审触发日志"章节。

---

## 5. 退出条件（一轮完整审核）

- [ ] `rounds/<round-id>/` 目录结构完整，`_meta.md` 已写入启动元信息
- [ ] 所有目标文档均有对应的 `reports/*.report.md`
- [ ] 所有目标文档均有对应的 `questions/*.questions.md`
- [ ] `_merged.questions.md` 已生成并覆盖全部疑问
- [ ] 所有疑问条目均已脱离 `[ ]` 空白状态（已答复/搁置/不确定）
- [ ] `_round_decisions.md` 已被用户显式批准（`_meta.md` 中有记录）
- [ ] 所有需修订文档均有对应的 `fix_plans/*.fix_plan.md` 且已被用户批准
- [ ] 所有执行子代理均以"正常完成"或"异常已裁定"收尾，`_meta.md` 异常区为空或均已处理
- [ ] `consistency_check.md` 已生成且所有冲突均已修复
- [ ] 所有"代码问题观察"均已归档到 `plans/bugfixes/`
- [ ] 所有目标文档的 `verified_at` 已更新为审核当日
- [ ] `REVIEW_LOG.md` 已追加本轮摘要
- [ ] **终极验收**：随机抽 1 份文档，新会话 AI 仅凭此文档可完成典型变更任务，不追问用户

---

## 6. 可恢复状态机与 `_meta.md`

### 6.1 状态判定规则

中断后恢复审核时，主会话必须先读取 `_meta.md`，再扫描 `rounds/<round-id>/` 下的实际文件，并按以下规则反推每份文档的状态。若 `_meta.md` 与文件系统不一致，以文件系统为事实依据，修正 `_meta.md` 后再继续。

| 状态 | 判定依据 | 下一步 |
|------|---------|--------|
| 未开始 | 不存在 `reports/<doc>.report.md` | 派发阶段 1 深审 |
| Pass1进行中 | `_meta.md` 已记录派发，但报告或疑问文件缺失 | 检查子代理状态；必要时重新派发 |
| Pass1完成 | 同时存在 `reports/<doc>.report.md` 与 `questions/<doc>.questions.md` | 进入阶段 1.5 或等待疑问合并 |
| 疑问待答复 | `questions/<doc>.questions.md` 或 `_merged.questions.md` 仍有 `[ ]` 空白条目 | 等待用户答复 |
| 裁定对齐中 | 疑问已答复，但 `_round_decisions.md` 不存在或状态不是 `approved` | 起草或继续修订裁定快照 |
| 修复计划生成中 | `_round_decisions.md` 已批准，但 `fix_plans/<doc>.fix_plan.md` 缺失 | 派发阶段 3a 计划子代理 |
| 修复计划待审批 | 存在 `fix_plans/<doc>.fix_plan.md`，但 frontmatter 或 `_meta.md` 未标注 approved | 等待用户审批 |
| 执行修复中 | 修复计划已批准，执行子代理已派发但目标文档未完成复查 | 检查执行结果或异常区 |
| 已完成 | 目标文档已更新，相关 fix plan 复查项通过，一致性检查无冲突 | 保持归档，等待下一轮 |
| 已延后 | `_meta.md` 显式标注本轮延后，且记录原因 | 本轮跳过，写入 REVIEW_LOG 遗留项 |
| 异常 | `_meta.md` 执行异常区存在未处理条目 | 暂停该文档，等待用户裁定 |

恢复流程：
1. 读取 `_meta.md` 的轮次信息、审批记录和异常区。
2. 扫描 `reports/`、`questions/`、`clarifications/`、`fix_plans/`、`_round_decisions.md`、`consistency_check.md`。
3. 根据上表更新文档状态表，从最早的非终态继续执行。

### 6.2 `_meta.md` 模板

```markdown
---
round_id: <round-id>
round_type: baseline | event-triggered | manual
started_at: <date>
finished_at: <null>
git_head_at_start: <git rev-parse HEAD 输出>
git_head_at_finish: <null>
executor_version: sys_review_plan_v1.0
status: in_progress | completed | paused
---

# 轮次元信息：<round_id>

## 文档状态表

| 文档 | 状态 | Pass1 | 疑问答复 | 裁定对齐 | 修复计划 | 执行修复 | 备注 |
|------|------|-------|---------|---------|---------|---------|------|
| AI_Coding_Context.md | 未开始 | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | - |

状态枚举（按顺序）：
未开始 → Pass1进行中 → Pass1完成 → 疑问待答复 → 裁定对齐中 →
修复计划生成中 → 修复计划待审批 → 执行修复中 → 已完成 | 已延后 | 异常

## 裁定快照审批记录
（待写入）

## 修复计划审批记录
（待写入）

## 执行异常区
> 由执行子代理在发现 fix_plan 与代码冲突时追加；需用户裁定后清空

（空）

## 副产物索引
- bugfixes: （待写入）
- 一致性验证: rounds/<round-id>/consistency_check.md
```

---

## 7. 审核检查清单

本清单用于阶段 1 深审、阶段 3a 修复计划和阶段 4 复审。子代理可按目标文档类型选择相关项，但 P0 项不得跳过。

### 7.1 维度优先级矩阵

| 维度 | 验证点 | 优先级 |
|------|--------|--------|
| 准确性 | API 路径、端口号、配置参数是否与代码一致 | P0 |
| 准确性 | 数据模型、字段类型、约束是否与代码一致 | P0 |
| 准确性 | 代码示例是否来自真实代码并带源码位置 | P0 |
| 完整性 | 核心服务、模块、关键入口是否有文档覆盖 | P0 |
| 完整性 | 关键业务流程是否端到端描述 | P0 |
| 完整性 | 启动依赖、健康检查、容错策略是否记录 | P1 |
| 完整性 | 历史坑点是否引用 `plans/bugfixes/` 或相关记录 | P1 |
| 一致性 | 服务名、端口、字段名、术语跨文档统一 | P1 |
| 时效性 | `verified_at` 是否在 3 个月以内 | P2 |
| 时效性 | 新功能、删除功能、废弃功能是否反映到文档 | P2 |

### 7.2 每份文档必检项

- [ ] Frontmatter 中 `title`、`summary`、`keywords`、`scope` 与正文一致
- [ ] `related_files` 指向的文件真实存在，且覆盖关键源码
- [ ] `dependencies` 引用的文档真实存在
- [ ] 文档中提及的文件路径真实存在
- [ ] 事实性断言均有源码证据或明确标注为待确认
- [ ] 代码块语言标识正确，示例来自真实代码或明确标注为伪代码
- [ ] 文档内部链接、相对链接、Mermaid 图表可被验证

### 7.3 代码验证项

- [ ] API 路径与路由定义一致
- [ ] 端口号与启动配置、部署配置一致
- [ ] 环境变量名与实际读取位置一致
- [ ] 数据库字段名、类型、默认值、索引、约束与模型或迁移文件一致
- [ ] 关键函数、类名、模块名与源码一致
- [ ] 错误码、状态流转、重试、幂等、权限判断等边界行为有代码依据
- [ ] 已删除或废弃的功能未继续作为现状描述

### 7.4 跨文档一致性项

- [ ] 同一服务、模块、队列、表、字段、API 在所有文档中的名称一致
- [ ] 端口、协议、部署拓扑在入口文档、部署文档和模块文档中一致
- [ ] 主文档索引与实际子文档列表一致
- [ ] `_round_decisions.md` 中的裁定已落地到所有受影响文档
- [ ] `plans/bugfixes/` 中本轮新增问题已在相关文档交叉引用

### 7.5 常见问题模式速查

| # | 模式 | 典型验证方法 |
|---|------|-------------|
| 1 | 文件路径错误 | 用文件搜索验证路径是否存在 |
| 2 | 行号或代码片段过时 | 读取源码并逐字比对 |
| 3 | 端口号错误 | 对比启动脚本、Compose/K8s、配置文件 |
| 4 | API 路径不一致 | 搜索路由注册、控制器、网关配置 |
| 5 | 数据模型不一致 | 对比模型、迁移、Schema 定义 |
| 6 | 配置项缺失 | 对比 `.env.example`、配置类、读取点 |
| 7 | 术语混用 | 全仓搜索核心术语并在 `_round_decisions.md` 裁定 |
| 8 | 链接失效 | 验证相对路径、锚点、外部链接可达性 |
| 9 | 过程产物误当真相源 | 检查是否把 `_analysis/`、`plans/`、`thinking/` 当成当前事实 |
| 10 | 完整性不足 | 用“新会话 AI 能否完成典型变更”反向检查缺口 |

---

## 8. 写入权限总表

| 文件 / 目录 | 谁写入 | 何时 | 约束 |
|-------------|--------|------|------|
| `REVIEW_LOG.md` | 主会话 | 阶段 0 启动、阶段 5 完成 | 只追加轮次摘要和触发日志 |
| `rounds/<round>/_meta.md` | 主会话 | 阶段 0 创建，各阶段更新 | 子代理不得直接改，异常由主会话记录 |
| `rounds/<round>/reports/*.report.md` | 深审子代理 | 阶段 1 | 每个子代理只写自己的报告 |
| `rounds/<round>/questions/*.questions.md` | 深审子代理 | 阶段 1 | 每个子代理只写自己的疑问文件 |
| `rounds/<round>/questions/_merged.questions.md` | 主会话或合并子代理 | 阶段 1.5 | 只读原始 questions，不改原文件 |
| `rounds/<round>/clarifications/*.answers.md` | 主会话整理用户答复 | 阶段 2 | 必须保留用户答复原文和三态 |
| `rounds/<round>/_round_decisions.md` | 主会话 | 阶段 2.5 | 需用户批准后才能作为权威输入 |
| `rounds/<round>/fix_plans/*.fix_plan.md` | 计划子代理 | 阶段 3a | 只能写对应目标文档的修复计划 |
| `dev_docs/<target>.md` | 执行子代理 | 阶段 3c | 只能按已批准 fix plan 修改指定目标文档 |
| `rounds/<round>/consistency_check.md` | 主会话 | 阶段 4 | 记录裁定落地和冲突结果 |
| `dev_docs/plans/bugfixes/*.md` | 主会话 | 阶段 5 | 只归档代码问题，不修改代码 |
| 代码文件 | 无人 | 全阶段禁止 | 审核流程只读代码，不修代码 |

---

## 9. `REVIEW_LOG.md` 维护规范

```markdown
# 文档审核进度记录

> 本文件是所有审核轮次的总索引。单轮详情进入对应的
> `dev_docs/review/rounds/<round-id>/_meta.md`。

## 最新状态摘要
- 最近基线轮次：<round-id>（进行中/已完成）
- 已审文档数 / 总数：N / M
- 待用户确认的疑问数：N（跨 M 份文档）

## 轮次索引（按时间倒序）
| 轮次 ID | 类型 | 启动时间 | 完成时间 | 状态 |
|--------|------|---------|---------|------|

## 重审触发日志
| 日期 | 触发原因 | 触发的轮次 | 涉及文档 |
|------|---------|----------|---------|

## 长期健康度追踪
| 基线轮次 | 发现问题总数 | 代码问题记录 | 终极验收通过率 |
|---------|----------|------------|-------------|
```
