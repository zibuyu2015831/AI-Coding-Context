---
title: AICC Phase 1 审核门落地实施计划
summary: 将 LinguaCafe 测试暴露出的 Phase 1 审核问题转化为 AICC 框架的具体实现任务、测试夹具和验收路径。
keywords: aicc | phase-1 | review-gate | implementation-plan | semantic-checker
scope: AI-Coding-Context 框架 Phase 1 审核机制实现计划
related_files: dev/plan/linguacafe-phase1-aicc-improvement-plan.md | AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md
dependencies: templates/PROGRESS_TEMPLATE.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md | core/contracts/run_record_contract.yaml | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js
verified_at: 2026-05-18
status: done（已实施并验证，2026-06-13 归档）
---

# AICC Phase 1 审核门落地实施计划

> **状态：✅ 已实施并验证（done）** — 本方案提出的改进已落地到框架（契约 / 检查器 / 模板 / 工作流，Python+JS 一致并配有通过的测试），于 2026-06-13 经逐任务核验后归档至 `dev/plan/done/`。以下为当时的规划与问题记录，保留作开发档案，措辞中的“待办/暴露的问题”为历史状态。（核验：13/14 任务落地；Task 3 的 `project_positioning_signals` 以 semantic_review_checker 等价实现，另有 2 个 project_types 指南为次要文档待补。）

## 1. 目标与边界

本实施计划用于落地 [AICC Phase 1 审核机制二次改进计划](./linguacafe-phase1-aicc-improvement-plan.md)，目标不是调整 LinguaCafe 项目文档，而是把 LinguaCafe 作为测试样本暴露出的框架缺口内化到 AICC。

从系统架构角度，Phase 1 的核心定位是“正式文档生成前的方案质量门”。它必须能回答三类问题：

1. 当前 `_analysis` 产物是否已经经过可复查的自审。
2. 方案中的强结论、风险、疑问和通过建议是否有证据等级支撑。
3. AI 是否可以在用户只给出短指令时，按框架默认规则完成复查、回写和进入下一阶段前的阻断判断。

本轮不生成或修复 LinguaCafe 的正式 `dev_docs` 文档，不把 Phase 1 变成完整代码审计系统，不要求用户同时安装 Python 和 Node 运行时。可用工具必须运行；不可用工具必须记录为明确降级状态。

## 2. 当前基础判断

仓库目前已经具备部分基础：

- `workflows/path_a_first_generation.md` 和 `workflows/generation_workflow.md` 已包含 Phase 1 自检门说明。
- `templates/generation_plan_*` 已开始引入证据等级与复查回写要求。
- `templates/PROGRESS_TEMPLATE.md` 已区分流程阶段进度、产物完成度、当前 gate 和下一步动作。
- `tools/py/semantic_review_checker.py` 与 `tools/js/semantic_review_checker.js` 已有 `review_consistency` 检查。
- `tools/py/project_scanner.py` 与 `tools/js/project_scanner.js` 已支持标准排除参数。
- `tools/py/framework_contract_checker.py` 与 `tools/js/framework_contract_checker.js` 已支持 self-check。

主要缺口是这些能力还没有被一个稳定的 Phase 1 审核契约串起来：入口路由不够强制，进度记录缺少审核包字段，证据等级没有覆盖所有关键结论，项目定位信号没有结构化输出，Python/JS 工具的排除规则和语义检查结果还需要做一致性约束。

## 3. 实施原则

- 契约先行：先定义状态机、必填字段和检查器错误类型，再改模板和工作流。
- 双实现一致：Python 和 JavaScript 工具必须保持字段名、issue type、阻断规则和退出语义一致。
- 可降级但不可静默：工具缺失、超时、误报豁免都必须写入 `generation_progress.md`，不能被表述为简单通过。
- 回写完整性优先：复查结论变化时，必须同步更新摘要、正文、表格、待确认清单、行动计划和进度记录。
- Phase 1 不越界：只判断方案是否可进入正式文档生成，不要求正式文档、AI Rules 或 `health_check_report.md` 已存在。

## 4. 任务分解

### Task 0: 定义 Phase 1 Review Contract 与状态机

目标：建立统一的 Phase 1 审核契约，消除“工具 PASS 但人工审核未完成”的状态歧义。

修改范围：

- `core/contracts/run_record_contract.yaml`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`
- `tools/py/tests/test_framework_contract_checker.py`
- `tools/js/framework_contract_checker.test.js`
- `tools/testdata/framework_contracts/`

实施要点：

- 在契约中定义 Phase 1 状态集合：`待审核`、`审核中`、`需修正`、`建议通过`、`用户已确认`、`正式生成中`、`首版验收中`、`已完成`。
- 明确阻断规则：`建议通过` 只能表示 AI 建议，不等同于 `用户已确认`；用户确认前不得开始正式文档生成。
- 在 self-check 中检测非法组合，例如 `phase1_verdict = PASS`、`当前状态 = 等待人工审核`、`下一步动作 = 生成正式文档` 同时出现时必须报错。
- 增加 issue type：`phase1_state_transition_invalid`、`phase1_user_confirmation_missing`、`phase1_formal_generation_before_confirmation`。

验收标准：

- Python/JS framework contract checker 均能识别合法与非法状态组合。
- 旧的“等待人工审核但工具 PASS”表达不会被误判为可直接生成正式文档。

### Task 1: 补齐 progress 审核包与自检证据

目标：让 `generation_progress.md` 成为 Phase 1 审核状态的可追溯记录，而不是只记录笼统进度。

修改范围：

- `templates/PROGRESS_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/tests/test_doc_health_checker.py`
- `tools/js/doc_health_checker.test.js`

新增字段：

- `review_started_at`
- `review_completed_at`
- `review_trigger`
- `machine_check_summary`
- `manual_review_summary`
- `blocker_count`
- `warning_count`
- `waived_issue_count`
- `phase1_recommendation`

实施要点：

- 在模板中新增“Phase 1 审核包”章节，要求记录命令、退出码、issue 数量、人工复核结论和剩余风险。
- 增加检查器 issue type：`phase1_self_check_record_missing`、`phase1_gate_without_self_check`、`checker_result_issue_count_mismatch`、`phase1_pass_without_required_review_evidence`、`phase1_progress_only_review`。
- 明确 `doc_health_checker` 只判断结构和运行记录完整性，不代替语义审核结论。

验收标准：

- 缺少审核包的 `generation_progress.md` 会失败。
- 只在进度文档写“已通过”，但没有修改 `generation_plan.md` 与 `project_analysis_report.md` 的案例会被标记为 `phase1_progress_only_review`。

### Task 2: 在模板和语义检查器中落地证据等级

目标：让 Phase 1 强结论、风险、疑问和通过建议都有证据等级，避免把目录猜测写成确定事实。

修改范围：

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/generation_plan_trivial.md`
- `templates/generation_plan_simple.md`
- `templates/generation_plan_medium.md`
- `templates/generation_plan_complex.md`
- `templates/generation_plan_critical.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

证据等级：

- `E1`: 直接代码或配置证据。
- `E2`: 项目文档、README、CONTRIBUTING、部署说明等证据。
- `E3`: 文件结构、目录命名、依赖拓扑等间接证据。
- `E4`: 推测、待确认或策略性判断。

实施要点：

- `generation_plan.md` 必须包含“Phase 1 证据等级与复查回写”表。
- `project_analysis_report.md` 中的风险、疑问、建议和阻断项必须带证据等级与状态。
- `semantic_review_checker` 增加 `evidence_level_completeness` 检查。
- 强结论使用 E3/E4 时必须降级为风险假设或待确认问题。

验收标准：

- 缺少证据等级的强结论会被识别。
- `E4` 项被写成“已确认事实”时会被识别。

### Task 3: 扩展项目定位信号扫描

目标：让框架能识别开源、自托管、用户手册、外部数据/API 等影响文档体系规划的项目定位信号。

修改范围：

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `tools/py/tests/test_project_scanner.py`
- `tools/js/project_scanner.test.js`
- `tools/testdata/semantic_review/linguacafe_phase1_review_case/`

新增输出字段：

```json
{
  "project_positioning_signals": {
    "open_source": true,
    "self_hosted": true,
    "user_manual": true,
    "external_data_or_api": true,
    "evidence": []
  }
}
```

实施要点：

- `open_source`: 识别 `LICENSE`、`CONTRIBUTING`、GitHub workflow、公开贡献说明。
- `self_hosted`: 识别 Docker Compose、安装脚本、默认账号、备份升级说明。
- `user_manual`: 识别 `manual`、`docs/user`、`README` 中的用户操作说明。
- `external_data_or_api`: 识别外部 API、导入源、第三方数据、爬取或同步任务。
- 证据必须包含路径和简短理由，不只输出布尔值。

验收标准：

- LinguaCafe-like fixture 能输出上述信号。
- Python/JS 输出字段结构一致。

### Task 4: 增强项目定位覆盖与维护者规则一致性检查

目标：把项目定位信号转化为 Phase 1 方案质量检查，避免文档规划遗漏核心用户场景。

修改范围：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

新增检查：

- `missing_project_positioning_doc`
- `missing_user_manual_boundary`
- `missing_external_data_or_api_boundary`
- `missing_self_hosting_boundary`
- `maintainer_rules_inconsistent`

实施要点：

- 当扫描到用户手册或明显用户操作说明，方案必须说明是否需要 `user_workflows.md`、`manual_mapping.md` 或等价文档。
- 当扫描到外部数据/API，方案必须说明数据来源、同步边界、失败处理、归因或授权风险是否进入文档计划。
- 当扫描到自托管部署，方案必须覆盖 Docker、环境变量、初始化账号、备份、升级、队列和生产/开发差异。
- 当项目存在 `CONTRIBUTING`、测试规则或 PR 规则，方案必须识别维护者工作流与测试命令。

验收标准：

- LinguaCafe-like 正例通过。
- 缺少项目定位文档规划的负例失败，并给出可回写目标。

### Task 4A: 标准排除规则与 Python/JS 一致性

目标：避免 AICC 框架自身、软链接或嵌套测试夹具污染被分析项目的扫描结果。

修改范围：

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_project_scanner.py`
- `tools/js/project_scanner.test.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`

实施要点：

- 统一标准排除项：`AI-Coding-Context`、`ai_coding_context`、`.ai`、`.git`、`node_modules`、`vendor`、工具测试数据和嵌套 fixtures。
- 对软链接使用 realpath 判断，避免只按显示路径过滤。
- 增加 LinguaCafe-like symlink fixture，模拟项目根目录中挂载 AICC 框架的情况。
- Python/JS 语义检查器的 verdict、issue type、默认排除行为必须一致。

验收标准：

- 标准排除规则不会吞掉业务目录。
- AICC 软链接不会被计入项目技术栈、测试拓扑或文档规划证据。

### Task 4B: 工具降级、误报豁免与性能边界

目标：让工具不可用、超时和误报豁免有统一表达，避免把未运行误写成通过。

修改范围：

- `templates/PROGRESS_TEMPLATE.md`
- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`

工具状态：

- `PASS`
- `FAIL`
- `NOT_RUN`
- `UNAVAILABLE`
- `TIMEOUT`
- `WAIVED_FALSE_POSITIVE`

实施要点：

- 进度模板要求记录替代检查、人工复核动作、剩余风险和豁免理由。
- 语义检查 issue 增加 `severity`、`blocks_phase1`、`suggested_writeback_target`。
- 大项目扫描需要保留 scope、timeout、skip reason，不允许静默裁剪。
- `UNAVAILABLE` 可以不阻断 Phase 1，但必须有替代检查或人工复核说明。

验收标准：

- 工具未运行或不可用不会被统计为 PASS。
- 被豁免的误报必须保留 issue 数和原因，并不影响真实 blocker 统计。

### Task 5: 更新入口、工作流与项目类型指南

目标：让用户只给出普通短指令时，AI 也能自动进入 Phase 1 审核门，而不是依赖详细提示词。

修改范围：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `workflows/path_d_specific_tasks.md`
- `core/project_types/fullstack.md`
- `core/project_types/web_frontend.md`
- `core/project_types/containerized.md`

实施要点：

- 在入口文档中增加短指令路由：当用户要求审核 `_analysis`、判断 Phase 1 是否通过、是否进入正式文档生成阶段时，必须进入 Phase 1 Review Gate。
- 明确 AI 的回复流程：读取三份 `_analysis` 文档、执行可用检查器、做代码/文档证据复核、回写三份分析文档、更新进度、给出“建议通过/需修正/等待用户确认”。
- 明确禁止项：用户确认前不得生成正式文档；不得只在聊天中给结论；不得只更新 `generation_progress.md`。
- 在项目类型指南中补充传统后端 + SPA、自托管部署、用户手册、外部数据/API、开源维护者规则的识别与文档规划要求。

验收标准：

- 用户输入“审核 dev_docs/_analysis 下已经生成的方案和分析结果”时，入口文档能明确指向 Phase 1 Review Gate。
- 项目类型指南能覆盖 LinguaCafe 暴露出的 Laravel + Vue 2 + Vue 3 子应用 + Docker + Redis/Horizon/Reverb + Python tokenizer 场景。

### Task 6: 框架自检与收尾验收

目标：确保契约、模板、工作流、工具和测试夹具形成闭环。

修改范围：

- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`
- `tools/testdata/framework_contracts/`
- `tools/testdata/semantic_review/README.md`
- `templates/README.md`
- 必要时更新 `dev/quality/` 下的质量记录或审计说明。

实施要点：

- self-check 必须覆盖入口、Path A、generation workflow、progress 模板、run record contract、generation plan 模板和 project analysis 模板之间的关键字段一致性。
- 为新增 issue type 建立正例和负例夹具。
- 最后运行 Python/JS 全量测试与核心命令。

验收命令：

```bash
python3 -m unittest discover tools/py/tests
for f in tools/js/*.test.js; do node "$f" || exit 1; done
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
python3 tools/py/doc_health_checker.py --full-check --doc-dir tools/testdata/semantic_review/linguacafe_phase1_review_case/dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir tools/testdata/semantic_review/linguacafe_phase1_review_case/dev_docs --repo-root tools/testdata/semantic_review/linguacafe_phase1_review_case
node tools/js/semantic_review_checker.js --full-check --doc-dir tools/testdata/semantic_review/linguacafe_phase1_review_case/dev_docs --repo-root tools/testdata/semantic_review/linguacafe_phase1_review_case
git diff --check
```

验收标准：

- Python/JS 测试均通过。
- framework contract self-check 通过。
- LinguaCafe-like 正例通过，负例按预期失败。
- 文档模板、入口和工作流没有出现字段漂移。

## 5. 执行顺序

推荐顺序：

1. Task 0：先固定状态机和契约。
2. Task 1：补齐进度记录审核包。
3. Task 2 与 Task 3：分别推进证据等级和项目定位扫描。
4. Task 4A 与 Task 4B：并行补齐工具一致性、排除规则和降级表达。
5. Task 4：基于 Task 2、Task 3、Task 4A 的结果增强语义检查。
6. Task 5：更新入口、工作流和项目类型指南。
7. Task 6：做框架级自检、夹具补齐和收尾验证。

若分批提交，建议按以下提交边界：

- 契约与模板提交：Task 0、Task 1。
- 语义与扫描能力提交：Task 2、Task 3、Task 4。
- 工具鲁棒性提交：Task 4A、Task 4B。
- 入口与项目类型指南提交：Task 5。
- 测试夹具与自检收尾提交：Task 6。

## 6. 验收矩阵

| 来源要求 | 落地任务 | 主要文件 | 验收方式 |
| --- | --- | --- | --- |
| Phase 1 审核通过不能等同用户确认 | Task 0 | `core/contracts/run_record_contract.yaml`、`templates/PROGRESS_TEMPLATE.md` | 非法状态夹具失败 |
| 自审必须可追溯 | Task 1 | `templates/PROGRESS_TEMPLATE.md`、`doc_health_checker` | 缺少审核包失败 |
| 强结论必须有证据等级 | Task 2 | `generation_plan_*`、`PROJECT_ANALYSIS_REPORT_TEMPLATE.md`、`semantic_review_checker` | `evidence_level_completeness` 检查 |
| 项目定位和愿景必须进入方案 | Task 3、Task 4 | `project_scanner`、`semantic_review_checker` | LinguaCafe-like fixture |
| 复查不能只改 progress | Task 1、Task 2、Task 5 | `doc_health_checker`、入口与工作流 | `phase1_progress_only_review` |
| AICC 软链接不能污染项目分析 | Task 4A | `project_scanner`、`semantic_review_checker` | symlink fixture |
| 工具不可用不能写成 PASS | Task 4B | progress 模板、检查器 | `UNAVAILABLE`/`TIMEOUT` 记录检查 |
| 用户短指令也应触发审核门 | Task 5 | `AI_ENTRY_POINT.md`、Path A、Path D | 入口路由文本检查 |
| Python/JS 工具结果一致 | Task 4A、Task 6 | py/js checkers 和 tests | 双实现测试 |
| 框架契约不漂移 | Task 6 | `framework_contract_checker` | self-check |

## 7. 测试夹具设计

新增或扩展以下夹具：

- `tools/testdata/semantic_review/linguacafe_phase1_review_case/`：正例，模拟 Laravel + Vue 2 主应用、Vue 3 子应用、Docker、Redis/Horizon/Reverb、Python tokenizer、用户手册、开源维护规则和 AICC 软链接排除。
- `tools/testdata/semantic_review/linguacafe_phase1_missing_evidence_case/`：负例，强结论缺少证据等级。
- `tools/testdata/semantic_review/linguacafe_phase1_progress_only_case/`：负例，只更新 `generation_progress.md`，未回写计划和分析报告。
- `tools/testdata/semantic_review/linguacafe_phase1_missing_positioning_case/`：负例，扫描到自托管和用户手册信号，但方案未规划对应文档。
- `tools/testdata/semantic_review/linguacafe_phase1_tool_degraded_case/`：负例或警告例，工具不可用但未记录替代检查。

每个夹具需要包含最小可读项目文件、`dev_docs/_analysis/` 三件套和预期 issue type 说明，避免测试依赖真实 LinguaCafe 仓库。

## 8. 风险与应对

- 风险：状态机过度复杂，增加 AI 执行负担。应对：状态只服务 Phase 1 到正式生成的门禁，不引入完整项目管理流。
- 风险：语义检查误报过多。应对：issue 采用 severity 与 `blocks_phase1` 分层，允许 `WAIVED_FALSE_POSITIVE` 但要求记录原因。
- 风险：Python/JS 双实现漂移。应对：共用夹具、统一 issue type、在 self-check 中检查关键文本和契约字段。
- 风险：项目定位扫描把间接证据当事实。应对：扫描器只输出信号和证据，是否构成结论由语义检查器和人工复核决定。
- 风险：大项目扫描性能不稳定。应对：保留 scope、timeout、skip reason，并在 progress 中记录降级路径。

## 9. 最终完成定义

本实施计划完成后，AICC 应满足以下条件：

- 用户携带 `AI_ENTRY_POINT.md` 并要求审核 `_analysis` 时，AI 能自动进入 Phase 1 Review Gate。
- AI 会读取并复查 `generation_plan.md`、`project_analysis_report.md`、`generation_progress.md`，并把修正完整回写到三份文档。
- 工具检查、人工复核、误报豁免和剩余风险都有结构化记录。
- 证据等级、项目定位、维护者规则、自托管边界和外部数据/API 边界都会影响 Phase 1 是否建议通过。
- 用户确认前，框架不会指挥 AI 生成正式文档。
- Python/JS 工具和框架自检能持续防止上述规则回退。
