---
title: AICC Phase 1 审核门复测后续优化方案
summary: 记录完善后的 AICC 在 LinguaCafe 复测中暴露的检查器一致性、证据表结构、待确认项解释和维护者规则冲突问题，并提出下一轮可执行优化方案。
keywords: aicc | phase-1 | review-gate | follow-up | linguacafe | checker-consistency
scope: AI-Coding-Context Phase 1 审核门复测后的框架优化计划
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js
dependencies: dev/plan/done/aicc-generation-plan-review-process-gap-plan.md | dev/plan/done/aicc-phase1-review-gate-implementation-plan.md | dev/plan/linguacafe-phase1-aicc-improvement-plan.md
verified_at: 2026-05-18
status: done（已实施并验证，2026-06-13 归档）
---

# AICC Phase 1 审核门复测后续优化方案

> **状态：✅ 已实施并验证（done）** — 本方案提出的改进已落地到框架（契约 / 检查器 / 模板 / 工作流，Python+JS 一致并配有通过的测试），于 2026-06-13 经逐任务核验后归档至 `dev/plan/done/`。以下为当时的规划与问题记录，保留作开发档案，措辞中的“待办/暴露的问题”为历史状态。

## 1. 背景

在 `098c3bd feat: enforce Phase 1 plan review gate` 之后，使用以下接近日常使用的指令重新测试 LinguaCafe：

```text
请根据 AI-Coding-Context/AI_ENTRY_POINT.md，审核 dev_docs/_analysis 下当前 Phase 1 方案与分析结果，判断是否建议通过并等待我确认，还是需要先修正。若需要修正，请按框架流程直接更新相关 _analysis 文档；不要生成正式文档。
```

测试目录：

- `/Users/zibuyu/code/openSource/LinguaCafe/dev_docs/_analysis/generation_plan.md`
- `/Users/zibuyu/code/openSource/LinguaCafe/dev_docs/_analysis/project_analysis_report.md`
- `/Users/zibuyu/code/openSource/LinguaCafe/dev_docs/_analysis/generation_progress.md`

复测结果比上一轮明显改善：AI 已进入 Phase 1 方案复查流程，三件套均有新修改时间，`generation_progress.md` 写入了结构化 `Phase 1 方案复查记录`，并且不再直接写“可进入正式文档生成”。

但本次复测仍暴露出 AICC 框架层面的后续缺口，说明 Phase 1 Review Gate 已经开始生效，但检查器一致性、结构化语义检查和项目规则约束还需要继续完善。

## 2. 本次复测事实

### 2.1 运行产物状态

文件修改时间显示三件套均参与回写：

| 文件 | 修改时间 |
| --- | --- |
| `generation_plan.md` | 2026-05-18 17:39:36 |
| `project_analysis_report.md` | 2026-05-18 17:40:02 |
| `generation_progress.md` | 2026-05-18 17:40:18 |

`generation_progress.md` 中已经包含：

- `review_trigger`
- `review_started_at`
- `review_completed_at`
- `reviewed_files`
- `machine_checks`
- `manual_review_summary`
- `writeback_summary`
- `blocker_count`
- `warning_count`
- `waived_issue_count`
- `phase1_recommendation`
- `user_confirmation_status`

这说明 AICC 的入口路由和 progress 审核包要求已经对 AI 行为产生约束。

### 2.2 当前工具复跑结果

在 AICC 仓库中对 LinguaCafe 复测产物重新运行检查：

```bash
python3 tools/py/doc_health_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs
node tools/js/doc_health_checker.js --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs --repo-root /Users/zibuyu/code/openSource/LinguaCafe --format json
node tools/js/semantic_review_checker.js --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs --repo-root /Users/zibuyu/code/openSource/LinguaCafe --format json
```

结果：

| 工具 | 结果 | 说明 |
| --- | --- | --- |
| Python `doc_health_checker` | PASS，0 issues | 结构与运行记录检查通过 |
| JS `doc_health_checker` | PASS，0 issues | 与 Python 一致 |
| Python `semantic_review_checker` | PASS，0 issues | 未发现 Phase 1 gate 问题 |
| JS `semantic_review_checker` | FAIL，31 issues | 将 `AI-Coding-Context/` 框架目录纳入事实源和测试拓扑，产生大量误报 |

这说明当前最重要的问题不是 LinguaCafe 文档本身完全失败，而是 Python/JS 语义检查器的项目边界处理仍不一致。LinguaCafe 中的 `AI-Coding-Context/` 实际是指向 `/Users/zibuyu/code/zibuyu/AI-Coding-Context` 的符号链接；JS 版使用 `fs.statSync()` 递归进入符号链接目录，Python 版 `Path.rglob()` 当前没有同等方式跟随该符号链接。因此 Python PASS 不能证明边界规则已经正确，只说明两端默认遍历行为不同。

## 3. 暴露的问题

### 3.1 JS semantic_review_checker 未排除 AICC 框架目录

JS 版 `semantic_review_checker` 将 `/Users/zibuyu/code/openSource/LinguaCafe/AI-Coding-Context/` 符号链接作为项目事实源扫描，导致：

- `fact_conflicts` 将 AICC 框架文档与 LinguaCafe `_analysis` 文档互相比对。
- `test_topology` 将 AICC 自身测试夹具计入 LinguaCafe 测试目录。
- Python 与 JS 结果不一致，破坏“双实现一致”原则。

这是框架级 blocker。AICC 明确要求框架目录不得纳入项目分析，检查器自身不能违反该边界；同时，Python 与 JS 不应依赖各自运行时对符号链接的默认遍历差异来“偶然”得到不同结果。

### 3.2 证据表结构检查过弱

`generation_plan.md` 的 `证据与验证记录` 表仍是：

```markdown
| 结论 | 证据文件 | 验证方式 |
| --- | --- | --- |
```

缺少 `证据等级` 列。但同一文档后面的 Phase 1 复查清单勾选：

```markdown
- [x] `证据与验证记录` 表包含 `证据等级` 列，关键事实均能追溯来源文件或命令。
```

现有 checker 只检查全文是否出现“证据等级”，没有解析 `证据与验证记录` 章节下的表头。这会放行“自称满足、正文未满足”的方案。

### 3.3 待用户确认项缺少逐项不可判定说明

`generation_plan.md` 的“等待用户审核的问题”列出：

1. 是否接受全局文档策略。
2. 是否接受推荐子文档清单中的 16 个产物。
3. 是否需要把 `resources/vue3/` 当作正式迁移目标重点展开。

但没有逐项写明：

- 已检查哪些代码、配置或仓库文档。
- 为什么这些来源无法回答该问题。
- 该问题是否阻断 Phase 1。
- 用户不回答时默认采取何种保守策略。

这说明模板要求已经存在，但检查器尚未验证待确认项的逐项结构。

### 3.4 维护者规则未约束工程治理建议

LinguaCafe `CONTRIBUTING.md` 明确写明：

- 当前维护者不使用 JavaScript、Python 或 PHP 测试。
- 在维护者确定测试策略前，PR 不应直接添加测试。

但 `project_analysis_report.md` 仍提出“后续优先补核心 Service 与队列 Job 的回归测试”。这个建议从工程质量角度合理，但与当前维护者贡献规则存在冲突。AICC 应将其改写为：

- 首版文档记录测试缺口。
- 若要新增测试，先作为维护者策略确认项或内部治理建议。
- 不应作为普通 PR 或贡献者默认建议。

当前框架还没有把 `CONTRIBUTING.md`、维护规则、PR 规则、测试策略作为“治理约束事实源”用于校验建议。

### 3.5 progress 中 machine_checks 仍缺少机器可解析结构

`generation_progress.md` 已经记录了多轮工具结果，但形式仍是自然语言列表：

- 第 1 次运行。
- 第 2 次运行。
- 第 3 次运行。
- 工具名称与 issue 数量。
- 人工复核说明。

这对人可读，但不利于工具复核：

- 无法稳定解析 Python / JS 是否都运行。
- 无法确认每轮命令的退出码。
- 无法区分 machine PASS、人工 waived、误报修复后 PASS。
- 无法将“工具不可用”与“工具通过”严格区分。

下一轮应把 `machine_checks` 从自由文本升级为固定表格或 YAML-like 块。

## 4. 根因分析

### 4.1 排除规则散落在扫描器和工作流中

AICC 已在入口文档强调框架目录必须排除，但 `semantic_review_checker` 的权威文件扫描和测试拓扑扫描没有复用统一的排除规则，导致 JS 版与 Python 版行为漂移。当前差异的直接触发点是符号链接：JS 版跟随了 `AI-Coding-Context/` 符号链接，Python 版没有以同样方式进入该目录。

需要把“项目边界排除规则”抽成共享契约，并在 Python/JS 两边建立同名测试夹具。

### 4.2 当前语义检查仍偏关键词

证据等级检查目前主要判断全文是否出现关键词。Phase 1 gate 需要更结构化：

- 定位具体章节。
- 解析 Markdown 表头。
- 检查每行关键事实是否有证据等级。
- 对“复查清单自称完成”与“正文实际状态”做一致性检查。

### 4.3 用户确认项还没有 schema

模板要求“为什么代码或仓库文档无法回答”，但没有固定字段名、表格结构或列表格式，因此 checker 难以判断是否逐项满足。

需要定义待确认项结构，使 AI 生成时可执行，工具检查时可验证。

### 4.4 治理建议没有纳入项目规则约束

当前 AICC 会识别 `CONTRIBUTING.md` 存在，但没有将其中的规则作为建议约束。结果是 AI 能看到贡献指南，却仍可能生成与贡献指南冲突的测试、PR、分支或代码风格建议。

### 4.5 运行记录可读但不够可审计

自然语言记录适合人工阅读，但 Phase 1 gate 需要可审计、可恢复、可验证。`machine_checks` 应明确命令、实现语言、退出码、issue 数量、最终处置和是否豁免。

## 5. 优化目标

下一轮 AICC 优化目标是把 Phase 1 Review Gate 从“AI 已经会执行”提升到“工具能严格验证执行质量”：

1. Python/JS `semantic_review_checker` 在相同输入上给出一致结果。
2. AICC 框架目录、工具夹具、依赖目录不再污染目标项目事实源和测试拓扑。
3. `generation_plan.md` 的 `证据与验证记录` 表必须真实包含 `证据等级` 列。
4. 待用户确认项必须逐项说明不可由代码或仓库文档回答的原因。
5. 项目维护者规则必须约束测试、PR、分支、代码风格等建议。
6. `generation_progress.md` 的 `machine_checks` 可被工具解析和复核。

## 6. 具体改进任务

### Task A: 统一项目边界排除规则

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `core/framework_spec.md`

改进内容：

- 定义统一标准排除目录：
  - `AI-Coding-Context/`
  - `ai_coding_context/`
  - `.ai/`
  - `.git/`
  - `node_modules/`
  - `vendor/`
  - `storage/`
  - `bootstrap/cache/`
  - 框架目录内部的 `tools/testdata/`
- 使用真实路径判断框架目录，避免符号链接或不同大小写导致漏排。
- 不得全局排除用户项目自己的 `tools/testdata/`；只有当其真实路径位于已识别的 AICC 框架根目录下时才排除。
- `iter_authority_files()`、`scan_test_topology()` 和 project scanner 使用同一套排除判断。

验收：

- LinguaCafe 仓库中存在 `AI-Coding-Context/` 时，Python/JS `semantic_review_checker` 均不扫描该目录。
- JS 版不再报告 AICC 自身 `tools/py/tests/`、`tools/testdata/` 为 LinguaCafe 测试拓扑。

### Task B: 增加 Python/JS 一致性回归夹具

目标文件：

- `tools/testdata/semantic_review/linguacafe_with_embedded_aicc_case/`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/README.md`

夹具内容：

- 根目录包含 `AI-Coding-Context/AI_ENTRY_POINT.md`，并至少覆盖一个符号链接形态的 `AI-Coding-Context/`。
- `AI-Coding-Context/tools/py/tests/test_fake.py` 用于模拟框架测试目录。
- LinguaCafe-like `dev_docs/_analysis` 已通过 Phase 1 复查。
- 目标项目自身只包含 `tests/Feature/ExampleTest.php`。

验收：

- Python/JS `semantic_review_checker --full-check` 输出均为 PASS。
- `test_topology` 只看到目标项目 `tests/`，不看到 `AI-Coding-Context/tools/py/tests/`。

### Task C: 精确解析证据与验证记录表

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/evidence_table_missing_level_case/`
- `tools/testdata/semantic_review/evidence_table_valid_case/`

改进内容：

- 定位 `## 🧾 证据与验证记录` 到下一个同级标题之间的内容。
- 找到 `关键事实记录` 或首个 Markdown 表格。
- 解析表头，要求包含 `证据等级`。
- 检查每行关键事实的证据等级为 `E1`、`E2`、`E3` 或 `E4`，并沿用当前 AICC 模板语义：`E1` 为目录/文件名/数量，`E2` 为配置/锁文件/README/项目文件，`E3` 为源码片段/协议/调用链，`E4` 为构建/测试/工具运行结果。
- 若复查清单勾选“表包含证据等级列”，但实际表头缺失，报 `evidence_table_claim_mismatch`。

新增 issue type：

- `evidence_table_level_column_missing`
- `evidence_table_level_value_invalid`
- `evidence_table_claim_mismatch`

验收：

- LinguaCafe 当前复测文档应触发 `evidence_table_level_column_missing`。
- 修正后的表格应通过。

### Task D: 定义并检查待用户确认项结构

目标文件：

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/generation_plan_trivial.md`
- `templates/generation_plan_simple.md`
- `templates/generation_plan_medium.md`
- `templates/generation_plan_complex.md`
- `templates/generation_plan_critical.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`

建议结构：

```markdown
### 待确认项 1: [问题]

- **当前保守结论**: [用户未回答时文档采用的默认表述]
- **已检查证据**: `[path]`, `[path]`
- **为什么代码或仓库文档无法回答**: [具体说明]
- **blocks_phase1**: [true/false]
- **回写目标**: `[target.md]`
```

新增 issue type：

- `user_confirmation_rationale_missing`
- `user_confirmation_evidence_missing`
- `user_confirmation_default_missing`
- `user_confirmation_blocks_phase1_missing`

验收：

- 只列问题、不解释不可判定原因的方案失败。
- 每个待确认项都有保守结论、已检查证据、不可判定原因、阻断状态和回写目标时通过。

### Task E: 将维护者规则纳入语义约束

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/maintainer_rules_conflict_case/`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`

规则来源：

- `CONTRIBUTING.md`
- `DEVELOPMENT.md`
- `docs/contributing*`
- `README.md` 中的 contribution / testing / pull request / branch 章节

首批检测规则：

- 如果贡献文档明确“不使用测试”或“不要在 PR 中添加测试”，分析报告不得直接写“优先补测试”作为普通贡献建议。
- 如果贡献文档要求 PR 进入 `dev` 分支，文档不得建议默认向 `main` 分支提交。
- 如果贡献文档声明无严格格式化规则，文档不得强行引入格式化工具作为现有规范。

新增 issue type：

- `maintainer_rules_inconsistent`
- `test_recommendation_conflicts_with_contributing`
- `branch_policy_conflict`
- `formatting_policy_conflict`

验收：

- LinguaCafe-like fixture 中若直接建议“优先补测试”，应失败。
- 改写为“记录测试缺口；新增测试需先经维护者确认”时通过。

### Task F: 结构化 machine_checks

目标文件：

- `templates/PROGRESS_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/tests/test_doc_health_checker.py`
- `tools/js/doc_health_checker.test.js`

建议格式：

```markdown
### machine_checks

| round | tool | implementation | command | exit_code | issue_count | status | disposition |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | doc_health_checker | python | `python3 ...` | 1 | 3 | FAIL | fixed |
| 1 | semantic_review_checker | node | `node ...` | 1 | 31 | FAIL | framework_false_positive |
| 2 | semantic_review_checker | node | `node ...` | 0 | 0 | PASS | accepted |
```

新增 issue type：

- `machine_check_table_missing`
- `machine_check_required_tool_missing`
- `machine_check_exit_code_missing`
- `machine_check_issue_count_mismatch`
- `machine_check_unresolved_failure`

验收：

- progress 只用自然语言写工具结果时给 warning 或 blocker，取决于是否声明 Phase 1 建议通过。
- progress 声明建议通过时，必须至少记录 Python 或 JS 可用实现的最终 PASS；如果另一实现不可用或误报，必须写 disposition。

### Task G: 更新复测说明和操作指令

目标文件：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `dev/plan/README.md`

改进内容：

- 明确 Phase 1 复查时如果 Python/JS 结果不一致，默认不得直接建议通过，除非记录差异原因和人工复核结论。
- 明确如果检查器误报源于框架目录被纳入分析，应优先修复框架排除规则，而不是在项目文档中豁免。
- 在计划索引中登记本方案，作为 `098c3bd` 之后的 follow-up。

验收：

- 用户继续使用同一短指令时，AI 应能识别 Python/JS 分歧并记录为框架问题或阻断项。

## 7. 建议实施顺序

1. Task A + Task B：先修复 JS 语义检查器误扫 AICC 框架目录，并建立一致性 fixture。
2. Task C：补强证据表结构解析，堵住“清单自称完成但表头未改”的漏洞。
3. Task D：把待确认项 schema 化，避免 AI 只列问题不解释。
4. Task E：把 `CONTRIBUTING.md` 等维护者规则纳入建议约束。
5. Task F：结构化 progress 的 `machine_checks`，让工具结果可复核。
6. Task G：同步入口、工作流和复测说明。

## 8. 完成定义

完成后，AICC 应满足：

- LinguaCafe 复测目录在 Python/JS `semantic_review_checker` 上结果一致。
- AICC 框架目录不再污染被分析项目的事实源、测试拓扑和冲突检测。
- `generation_plan.md` 的证据表必须真实包含 `证据等级`，否则工具阻断。
- 待用户确认项必须逐项说明不可由仓库事实回答的原因。
- 与 `CONTRIBUTING.md` 冲突的测试、PR、分支和格式化建议会被检查器识别。
- `generation_progress.md` 的 machine checks 可由工具解析。
- 用户继续使用相同短指令时，AI 不需要额外 checklist 也能暴露并处理上述问题。

## 9. 风险与边界

- 本方案不要求 AICC 成为完整自然语言合规审计器，首轮只覆盖高确定性的维护者规则冲突。
- 证据表解析只需支持 AICC 模板生成的 Markdown 表格，不必支持所有 Markdown 变体。
- 对历史 `_analysis` 文档应保持兼容：未声明 Phase 1 建议通过时，缺少新结构可给 warning；声明建议通过时必须满足新 gate。
- Python/JS 结果不一致时，应优先修复工具差异；只有明确不可修复的误报才允许记录为 waived。

## 10. 自检结论

本次复测证明 `098c3bd` 的方向正确：AI 已经不再只更新 progress，也能按入口文档执行 Phase 1 复查并回写三件套。

但要达到 AICC 的定位，即“让 AI 在陌生代码库中稳定获得可验证上下文”，还必须继续加强工具层的可验证性。当前最优先的是 Python/JS 语义检查器一致性和框架目录排除规则；其次是证据表结构化检查、待确认项 schema、维护者规则约束和 machine checks 结构化。

## 11. 实施落地记录

实施时间：2026-05-18。

已完成内容：

- `semantic_review_checker` Python/JS 已统一项目边界排除规则，嵌入式或符号链接形式的 `AI-Coding-Context/` 不再污染目标项目事实源和测试拓扑。
- `project_scanner` Python/JS 的标准排除规则已补充 `AI-Coding-Context/` 常见目录名，避免首轮扫描把框架当成业务项目目录。
- `semantic_review_checker` 已解析 `generation_plan.md` 的 `证据与验证记录` 表，能识别缺少 `证据等级` 列、证据等级非法、复查清单与实际表头不一致。
- `semantic_review_checker` 已检查待确认项结构，要求 `当前保守结论`、`已检查证据`、`为什么代码或仓库文档无法回答`、`blocks_phase1` 和 `回写目标`。
- `semantic_review_checker` 已把 `CONTRIBUTING.md` 中的测试限制纳入高确定性治理约束，能阻断与维护者规则冲突的测试建议。
- `doc_health_checker` Python/JS 已要求 Phase 1 建议通过时使用结构化 `machine_checks` 表，并校验工具、命令、退出码、issue 数、状态和处置。
- `AI_ENTRY_POINT.md`、Path A 工作流、生成工作流、进度模板、方案模板、分析报告模板和运行记录契约已同步新 gate。

回归验证：

```bash
python3 -m unittest discover tools/py/tests
for test_file in tools/js/*.test.js; do node "$test_file" || exit 1; done
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
python3 tools/py/doc_health_checker.py --file dev/plan/done/aicc-phase1-review-gate-followup-plan.md --check-template-residue --check-file-paths --check-code-samples
python3 tools/py/doc_health_checker.py --file dev/plan/README.md --check-template-residue --check-file-paths
python3 tools/py/doc_health_checker.py --file AI_ENTRY_POINT.md --check-template-residue --check-code-samples
git diff --check
```

LinguaCafe 回归结果：

- Python/JS `doc_health_checker` 均识别 `generation_progress.md` 缺少结构化 `machine_checks` 表。
- Python/JS `semantic_review_checker` 均输出 17 个一致的 Phase 1 gate 问题。
- JS `semantic_review_checker` 已不再出现上一轮 31 个由 `AI-Coding-Context/` 符号链接引发的框架误扫问题。

剩余边界：

- 维护者规则冲突检查当前只覆盖高确定性的测试限制语句；分支、PR、格式化等规则后续可按真实样例继续扩展。
- 证据表解析面向 AICC 模板生成的标准 Markdown 表格；非标准表格仍应由人工复查兜底。
