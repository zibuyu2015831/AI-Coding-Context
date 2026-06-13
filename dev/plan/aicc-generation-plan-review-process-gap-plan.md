---
title: AICC generation_plan 复查流程缺口记录与优化方案
summary: 记录 LinguaCafe 第三次运行后发现的 generation_plan.md 复查机制缺口，并提出可执行、可记录、可验证的框架完善方案。
keywords: aicc | generation-plan | phase-1 | review-process | progress-record
scope: AI-Coding-Context 框架首次生成 Phase 1 方案复查流程
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | tools/py/doc_health_checker.py | tools/py/semantic_review_checker.py
dependencies: dev/plan/aicc-phase1-review-gate-implementation-plan.md | dev/plan/linguacafe-phase1-aicc-improvement-plan.md
verified_at: 2026-05-18
---

# AICC generation_plan 复查流程缺口记录与优化方案

## 1. 背景

LinguaCafe 第三次 AICC 运行使用了接近日常使用的短指令：

```text
请根据 AI-Coding-Context/AI_ENTRY_POINT.md，审核 dev_docs/_analysis 下当前 Phase 1 方案与分析结果，判断是否建议通过并等待我确认，还是需要先修正。若需要修正，请按框架流程直接更新相关 _analysis 文档；不要生成正式文档。
```

运行结果显示，AI 能识别“需要审核 `_analysis`”，也能更新 `generation_progress.md`，但没有真正完成 `generation_plan.md` 与 `project_analysis_report.md` 的结构化复查和全文回写。当前 AICC 框架已有 Phase 1 自检、AI 互审、复查回写要求等文字说明，但还没有形成一个专门针对 `generation_plan.md` 的可执行流程、进度记录格式和工具阻断规则。

本方案用于补充记录这个具体缺口，并作为后续实现时的专项依据。

## 1.1 架构定位判断

AICC 的定位不是普通文档生成脚本，而是“让 AI 在陌生代码库中稳定获得可验证上下文”的框架。因此，`generation_plan.md` 不是普通计划文档，而是首次建立上下文体系前的执行契约；`generation_progress.md` 也不是普通进度条，而是 AI 运行过程的可恢复、可审计状态记录。

从这个定位看，Phase 1 方案复查必须满足三个架构要求：

- **可执行**：入口文档能把用户自然语言审核请求路由到明确流程，AI 不需要用户复述内部 checklist。
- **可追溯**：复查证据、工具结果、人工语义判断和回写范围必须落到 `_analysis` 文档中。
- **可阻断**：当方案事实、证据等级、用户确认边界或三件套一致性不满足要求时，框架必须阻止“建议通过”或“进入正式生成”。

这也是本方案与一般文档润色方案的区别：目标不是把 LinguaCafe 的方案写得更完整，而是让 AICC 形成稳定的 Phase 1 审核能力。

## 2. 当前框架事实

### 2.1 已有机制

AICC 目前已经有以下相关机制：

- `workflows/path_a_first_generation.md` Step 7 定义了“AI 互审”，要求生成方案后按复杂度执行 0-3 轮审查。
- `workflows/path_a_first_generation.md` Step 7.4 定义了“Phase 1 自检门”，要求 `_analysis` 方案产物可审核。
- `workflows/generation_workflow.md` 步骤 3.1B 定义了 Phase 1 方案自检 gate 的最小要求。
- `templates/GENERATION_PLAN_TEMPLATE.md` 包含“复查回写要求”，要求复查改变事实状态时同步更新摘要、正文、表格、待确认清单、行动计划、证据记录和 `generation_progress.md`。
- `templates/PROGRESS_TEMPLATE.md` 能记录当前状态、流程阶段进度、产物完成度、当前 gate、下一步动作和状态变更记录。
- `tools/py/doc_health_checker.py` 与 `tools/py/semantic_review_checker.py` 能执行结构与部分语义检查。

### 2.2 尚未形成的能力

上述机制仍然缺少以下能力：

- 没有独立的 `generation_plan.md` 复查流程入口。
- 没有规定用户短指令“审核 `_analysis` / 判断 Phase 1 是否通过”必须路由到哪个专门流程。
- 没有可填写的 `generation_plan.md` 复查清单。
- 没有 `generation_progress.md` 的复查证据包字段。
- 没有工具检查“progress 写 PASS，但 plan/report 没有回写”的矛盾。
- 没有状态机区分“AI 建议通过”“等待用户确认”“用户已确认”“正式生成中”。

因此，当前框架是“有复查要求”，但不是“有专门复查流程”。

### 2.3 当前开发进度约束

本方案必须尊重 AICC 当前实际开发进度：

- 现有 `run_record_contract.yaml` 只约束 `generation_plan` 必需标题和 `generation_progress` 必需字段，还没有 Phase 1 状态机或审核包 schema。
- 现有 `doc_health_checker` 更适合结构、模板残留、路径和运行记录完整性检查，不应突然承担深度语义判断。
- 现有 `semantic_review_checker` 已有少量 Phase 1 强结论检查，但还没有完整的三件套一致性模型。
- Python/JS 工具双实现并存，任何新增规则都必须考虑 issue type、字段名、退出码和 fixture 的一致性。
- 现有路径 A 已经在文档中插入 Step 7.4，但入口路径图和用户短指令路由尚未同步，这会导致 AI 实际运行时跳过该 gate。

因此，实施时不能只修改模板文字；必须同步修改入口路由、契约、模板、检查器和测试夹具，否则 AI 仍可能像 LinguaCafe 第三次运行一样只更新 `generation_progress.md`。

## 3. LinguaCafe 第三次运行暴露的问题

### 3.1 progress 记录了 PASS，但不能证明复查完成

`generation_progress.md` 记录了：

- `doc_health_checker` 已执行。
- `semantic_review_checker` 已执行。
- `Phase 1 verdict = PASS，可进入正式文档生成`。

但它没有记录：

- 复查触发来源。
- 复查开始与完成时间。
- 检查器命令、退出码、issue 数量。
- 人工语义复查结论。
- blocker、warning、waived issue 统计。
- 是否已回写 `generation_plan.md`。
- 是否已回写 `project_analysis_report.md`。
- 是否仍等待用户确认。

因此，`generation_progress.md` 当前只能表达“AI 声称做过复查”，不能证明“复查已完整完成”。

### 3.2 generation_plan 没有完成专项复查

`generation_plan.md` 仍存在以下问题：

- “证据与验证记录”仍是 `结论 / 证据文件 / 验证方式` 三列，没有 `证据等级`。
- 待用户确认项仍包含“是否加入更完整的开源贡献者指南”，但仓库内已有 `CONTRIBUTING.md`，应自动纳入贡献者/维护者文档规划，而不是作为是否存在的确认项。
- 项目定位信号没有完整驱动子文档清单，例如开源维护、用户手册、自托管运维、外部数据/API 与授权边界。
- 状态表述仍容易让 AI 把 `PASS` 理解为“可直接进入正式生成”，而不是“建议通过，等待用户确认”。

### 3.3 project_analysis_report 没有同步回写

`project_analysis_report.md` 没有同步补齐：

- 警告、疑问、建议的证据等级。
- 当前状态字段。
- 是否阻塞 Phase 1。
- 建议回写目标。
- 项目定位触发项。

文件修改时间也显示它没有参与第三轮复查回写。这说明 AI 把审核结果主要写进了 `generation_progress.md`，没有执行三件套同步修正。

### 3.4 当前工具没有发现问题

对 LinguaCafe 第三次结果运行当前工具：

```bash
python3 tools/py/doc_health_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs --repo-root /Users/zibuyu/code/openSource/LinguaCafe
```

结果均为 PASS，0 issues。

这说明现有检查器还没有覆盖：

- `phase1_progress_only_review`
- `phase1_pass_without_required_review_evidence`
- `evidence_level_completeness`
- `phase1_user_confirmation_missing`
- `missing_project_positioning_doc`

## 4. 根因分析

### 4.1 入口路由不够明确

`AI_ENTRY_POINT.md` 的路径图目前表现为：

```text
Step 6: 生成分析方案与问题报告
Step 7: AI 内部互审
Step 7.5: 等待人工审核
```

Step 7.4 “Phase 1 自检门”存在于 Path A 文档中，但没有成为入口路径图中的显式节点。用户后续要求“审核 `_analysis`”时，AI 容易把它当作普通健康检查，而不是进入专项 Phase 1 Review Gate。

### 4.2 互审和复查的边界混合

当前框架同时存在：

- AI 互审。
- Phase 1 自检。
- 结构健康检查。
- 语义复查。
- 人工审核等待。

这些概念没有统一成一个明确流程：谁负责复查 `generation_plan.md`，谁负责复查 `project_analysis_report.md`，谁负责记录结果，谁负责判断是否阻断。

### 4.3 progress 缺少可审计结构

`generation_progress.md` 当前更像进度看板，不是审核证据记录。它缺少固定字段来证明：

- 哪个复查流程已执行。
- 复查发现了什么。
- 修改了哪些 `_analysis` 文件。
- 为什么仍然可以建议通过。

### 4.4 checker 没有把三件套作为一致性整体

当前工具更多检查单文件结构、模板残留、部分语义冲突。它们没有建立以下跨文件规则：

- progress 声明 Phase 1 PASS 时，plan 必须具备证据等级。
- progress 声明 Phase 1 PASS 时，report 的警告/疑问/建议必须具备证据等级与状态。
- progress 的最后更新时间晚于 plan/report 时，必须证明主体文档已被复查或无需修改。
- plan/report 未回写时，progress 不得写 PASS。

### 4.5 generation_plan 的权责边界不够清晰

如果只强调“复查 `generation_plan.md`”，AI 可能再次把所有结论都塞进方案文档，导致三件套权责混乱。正确边界应是：

- `generation_plan.md` 负责当前正式文档体系生成策略、子文档清单、批次计划、质量门禁和进入下一阶段的准入条件。
- `project_analysis_report.md` 负责风险、疑问、警告、建议、用户确认项和项目定位触发项。
- `generation_progress.md` 负责流程状态、复查记录、工具结果、回写摘要、用户确认状态和恢复入口。

专项复查流程必须检查三者一致，而不是把 `generation_plan.md` 变成唯一事实源。

### 4.6 首次生成自检与后续审核请求没有分层

Phase 1 方案复查存在两个场景：

- 首次生成后，AI 在输出给用户前主动执行自检。
- 用户随后要求“审核 `_analysis` / 判断 Phase 1 是否通过”时，AI 对已经存在的三件套执行复查和必要回写。

这两个场景共享同一套 gate 条件，但触发方式、进度记录和输出措辞不同。当前框架没有明确区分，容易让 AI 在后续审核请求中只跑检查器，不回写 plan/report。

### 4.7 小项目、历史文档和部分工具不可用的边界未定义

新增复查规则如果过硬，可能误伤：

- 简单项目的轻量方案。
- 老版本 AICC 生成的历史 `_analysis` 文档。
- 只具备 Python 或只具备 Node 运行时的环境。
- 缺少 `CONTRIBUTING.md`、`manual/`、Docker 或外部 API 的普通项目。

因此，规则需要区分 blocker、warning 和可豁免项。只有会导致 Phase 1 错误通过、事实误判、用户确认边界失效或正式生成提前开始的问题，才应阻断。

## 5. 优化目标

### 5.1 建立 generation_plan 专项复查流程

AICC 应新增明确流程：`Phase 1 generation_plan Review Gate`。

该流程用于用户已经拥有 `_analysis` 三件套，并要求 AI 判断 Phase 1 是否可通过的场景。

触发语义包括：

- “审核 dev_docs/_analysis”
- “判断 Phase 1 是否通过”
- “检查方案是否可以进入正式文档生成”
- “复查 generation_plan.md”
- “根据 AI_ENTRY_POINT.md 审核方案和分析结果”

### 5.2 让 progress 记录复查证据

`generation_progress.md` 应新增“Phase 1 方案复查记录”章节，至少包含：

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

### 5.3 让 generation_plan 复查清单显式化

`generation_plan.md` 复查至少检查：

- 项目类型判断是否有代码或文档证据。
- 子文档清单是否覆盖项目定位信号。
- 关键事实表是否包含证据等级。
- 待用户确认项是否仅包含代码和仓库文档无法判断的问题。
- 风险与注意事项是否有证据来源。
- 质量保证措施是否与项目真实技术栈匹配。
- 下一步动作是否保持在“等待用户确认”。

### 5.4 让 project_analysis_report 成为风险事实源

`project_analysis_report.md` 复查至少检查：

- 每个警告、疑问、建议是否有证据等级。
- 每个问题是否有当前状态。
- 每个问题是否标注 `blocks_phase1`。
- 每个问题是否有建议回写目标。
- 可由代码确认的事实是否被错误放入用户确认项。

### 5.5 让 checker 阻断 progress-only PASS

检查器应能识别：

- progress 写 PASS 但缺少复查记录。
- progress 写 PASS 但 plan 缺证据等级。
- progress 写 PASS 但 report 缺证据等级。
- progress 写 PASS 但用户尚未确认却把下一步写成正式生成。
- progress 更新时间晚于 plan/report，但没有记录“无需回写”的理由。

### 5.6 明确三件套权责与回写规则

复查流程应规定：

- 修改子文档清单、批次计划、质量门禁时，必须回写 `generation_plan.md`。
- 修改风险、疑问、建议、证据等级、项目定位触发项时，必须回写 `project_analysis_report.md`。
- 修改状态、工具结果、复查结论、回写摘要、用户确认状态时，必须回写 `generation_progress.md`。
- 如果某个文件无需修改，必须在 `generation_progress.md` 的 `writeback_summary` 中说明“已检查，无需回写”的原因。

### 5.7 支持轻量项目和历史产物的兼容策略

新增规则应采用分层判定：

- **Blocker**：progress-only PASS、用户确认前进入正式生成、关键事实无证据等级、可由代码确认的事实被放入用户确认项。
- **Warning**：项目定位触发项可能遗漏，但现有子文档有合并覆盖说明。
- **Info**：历史产物缺少新字段，但没有写 Phase 1 PASS，也没有请求进入正式生成。

这样可以保证框架在提升严格度的同时，不把所有旧文档和轻量项目都判定为不可用。

## 6. 具体改进方案

### Task A: 更新入口路由

目标文件：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`

改进内容：

- 在入口文档中新增“Phase 1 方案复查请求”触发条件。
- 将 Step 7.4 Phase 1 自检门加入 Path A 主路径图。
- 明确用户请求审核 `_analysis` 时，不进入正式生成，不只跑健康检查，而是执行 `generation_plan.md` 专项复查流程。

验收：

- 用户只输入“审核 dev_docs/_analysis 下当前 Phase 1 方案与分析结果”时，入口文档能明确指向 Phase 1 generation_plan Review Gate。

### Task B: 新增 generation_plan 复查清单

目标文件：

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/generation_plan_trivial.md`
- `templates/generation_plan_simple.md`
- `templates/generation_plan_medium.md`
- `templates/generation_plan_complex.md`
- `templates/generation_plan_critical.md`

改进内容：

- 新增“Phase 1 方案复查清单”章节。
- 强制 `证据与验证记录` 包含 `证据等级` 列。
- 强制待确认事项包含“为什么代码或仓库文档无法回答”。
- 强制项目定位触发项影响子文档规划，或说明合并覆盖位置。

验收：

- 生成方案模板中存在可执行复查清单。
- 缺少证据等级的方案不能被标记为建议通过。

### Task C: 新增 progress 复查记录结构

目标文件：

- `templates/PROGRESS_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

改进内容：

- 在 progress 模板中新增“Phase 1 方案复查记录”。
- 在 run record contract 中加入必填字段。
- `doc_health_checker` 增加结构检查，确保复查记录存在且字段完整。

新增 issue type：

- `phase1_plan_review_record_missing`
- `phase1_plan_review_writeback_missing`
- `phase1_pass_without_plan_review_record`
- `phase1_pass_before_user_confirmation`

验收：

- progress 写 `Phase 1 verdict = PASS` 但缺少复查记录时，检查器失败。
- progress 写“进入正式文档生成”但用户未确认时，检查器失败或 blocker。

### Task D: 增强 semantic_review_checker 的三件套一致性检查

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

改进内容：

- 检查 `generation_plan.md` 的证据等级完整性。
- 检查 `project_analysis_report.md` 的警告、疑问、建议是否有证据等级与状态。
- 检查 progress-only PASS。
- 检查用户确认项是否包含可由代码确认的事实。
- 检查项目定位触发项是否进入子文档规划。

新增 issue type：

- `evidence_level_completeness`
- `project_analysis_issue_status_missing`
- `phase1_progress_only_review`
- `confirmable_fact_misclassified`
- `project_positioning_coverage_missing`

验收：

- LinguaCafe 第三次结果应被当前新增规则判定为不通过。
- 修正后的 LinguaCafe-like fixture 应通过。

### Task E: 建立 LinguaCafe 第三轮负例夹具

目标文件：

- `tools/testdata/semantic_review/linguacafe_phase1_progress_only_case/`
- `tools/testdata/semantic_review/README.md`

夹具内容：

- `dev_docs/_analysis/generation_plan.md`: 证据表缺少证据等级，项目定位覆盖不足。
- `dev_docs/_analysis/project_analysis_report.md`: 警告、疑问、建议缺少证据等级与状态。
- `dev_docs/_analysis/generation_progress.md`: 声明 Phase 1 PASS，但缺少复查证据包。
- 最小项目文件：`README.md`、`CONTRIBUTING.md`、`manual/Home.md`、`manual/Setup.md`、`docker-compose.yml`、`composer.json`、`package.json`。

验收：

- Python/JS semantic checker 对该 fixture 的 issue type 集合一致。
- 该 fixture 必须稳定复现 LinguaCafe 第三次运行暴露的问题。

### Task F: 明确三件套权责与复查输出协议

目标文件：

- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`

改进内容：

- 新增 `_analysis` 三件套权责表。
- 新增复查输出协议：`建议通过，等待用户确认`、`需修正，已回写 _analysis`、`需人工确认，禁止正式生成`。
- 要求 AI 在最终回复中列出已回写文件、未回写但已检查文件、剩余 blocker/warning 数量。
- 禁止出现“Phase 1 PASS，可进入正式文档生成”这类绕过用户确认的表达；应写为“Phase 1 建议通过，等待用户确认后再进入正式生成”。

验收：

- 工作流文档能区分三件套各自职责。
- 输出示例不再把 checker PASS、AI 建议通过和用户确认通过混为一谈。

### Task G: 增加兼容与降级规则

目标文件：

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `templates/PROGRESS_TEMPLATE.md`

改进内容：

- 新增 severity 分层：`blocker`、`warning`、`info`。
- 对历史 `_analysis` 文档，如果没有声明 Phase 1 PASS，也没有请求进入正式生成，可以给 warning 而不是 blocker。
- 对工具不可用场景，允许 `UNAVAILABLE`，但必须记录替代检查或人工复核。
- 对小项目，不强制新增额外项目定位文档；只要求说明“不适用”或“已合并覆盖”。

验收：

- 缺少新字段的历史 fixture 不会被误判为必须修复，除非它声明 Phase 1 PASS。
- 工具不可用但有替代复核记录时不阻断；工具不可用且无记录时阻断。

## 7. 与既有 Phase 1 审核门计划的关系

本方案不是替代 [AICC Phase 1 审核门落地实施计划](./aicc-phase1-review-gate-implementation-plan.md)，而是它的专项补充。

对应关系：

| 本方案问题 | 对应既有任务 | 补充价值 |
| --- | --- | --- |
| generation_plan 没有专项复查流程 | Task 0、Task 5 | 明确入口路由和专门流程名称 |
| progress 不能证明复查完成 | Task 1 | 补充复查证据包字段 |
| plan/report 未全文回写 | Task 1、Task 2 | 补充三件套一致性规则 |
| checker 漏检 progress-only PASS | Task 4、Task 6 | 补充 LinguaCafe 第三轮负例夹具 |
| 用户确认前状态混乱 | Task 0 | 强化 `建议通过` 与 `用户已确认` 的边界 |

## 8. 建议实施顺序

1. 先更新 `AI_ENTRY_POINT.md` 和 Path A 路由，让短指令能稳定进入专项复查流程。
2. 再更新 `GENERATION_PLAN_TEMPLATE.md` 和各复杂度模板，明确复查清单。
3. 然后更新 `PROGRESS_TEMPLATE.md` 与 run record contract，加入复查证据包。
4. 接着增强 `doc_health_checker`，阻断缺少复查记录的 PASS。
5. 再增强 `semantic_review_checker`，阻断证据等级缺失、progress-only PASS、项目定位漏项。
6. 补充三件套权责与复查输出协议，修正用户确认前的措辞边界。
7. 增加兼容与降级规则，避免误伤轻量项目和历史产物。
8. 最后建立 LinguaCafe 第三轮负例和修正后正例，保证 Python/JS 双实现一致。

## 8.1 验收矩阵

| 发现的问题 | 必须落地的能力 | 对应任务 | 验收方式 |
| --- | --- | --- | --- |
| 用户短指令没有进入专门流程 | 入口路由到 Phase 1 generation_plan Review Gate | Task A | 入口文档含触发语义和流程跳转 |
| plan 缺证据等级仍 PASS | 方案证据等级完整性检查 | Task B、Task D | 负例 fixture 触发 `evidence_level_completeness` |
| progress 声称 PASS 但无复查证据 | progress 审核包与结构检查 | Task C | 负例 fixture 触发 `phase1_pass_without_plan_review_record` |
| report 未同步回写 | 三件套一致性检查 | Task D、Task F | 负例 fixture 触发 `phase1_progress_only_review` |
| 用户确认前写进入正式生成 | 状态机和输出协议 | Task A、Task F | 输出示例只允许“建议通过，等待用户确认” |
| 项目定位触发项漏入规划 | 项目定位覆盖检查 | Task D | LinguaCafe-like fixture 覆盖 manual、CONTRIBUTING、Docker、外部 API |
| 新规则误伤历史产物 | severity 与兼容策略 | Task G | 历史 fixture 只给 warning 或 info |

## 9. 完成定义

完成后，AICC 应满足：

- 用户只要求“审核 `_analysis` / 判断 Phase 1 是否通过”时，AI 会执行专门的 `generation_plan.md` 复查流程。
- `generation_progress.md` 不再只记录“已执行检查”，而能证明复查过程、结果、回写范围和剩余风险。
- `generation_plan.md` 的关键事实、子文档规划、待确认事项和下一步动作都经过结构化复查。
- `project_analysis_report.md` 的警告、疑问、建议都能追溯到证据等级和当前状态。
- progress-only PASS 会被工具阻断。
- 用户确认前，AI 只能给出“建议通过，等待用户确认”，不能进入正式生成。
- 三件套权责清晰，AI 不会把所有复查结论堆进单一文件。
- 小项目、历史产物和工具不可用场景有明确兼容与降级策略。

## 10. 自检结论

从系统架构角度，本方案当前是必要且方向正确的。它补足了总 Phase 1 审核门计划中最容易被实现时忽略的一点：`generation_plan.md` 复查必须成为一个独立可执行流程，而不是散落在 AI 互审、健康检查和人工审核等待之间的文字要求。

本次补充后，方案已经覆盖：

- 项目定位与愿景：AICC 作为可验证上下文框架，需要把方案复查从“文本建议”升级为“运行时 gate”。
- 当前开发进度：承认现有工具和契约仍处在基础阶段，要求按入口、模板、契约、检查器、fixture 逐层落地。
- 关键边界：三件套权责、首次自检与后续审核、用户确认前阻断、轻量项目兼容、历史产物兼容、工具降级。
- 可扩展点：severity 分层、issue type 稳定化、Python/JS 双实现一致、LinguaCafe 第三轮负例和修正后正例。
