---
title: AICC 首版验收门禁可信度优化方案
summary: 记录 LinguaCafe 正式文档体系生成完成后暴露的首版验收 PASS 失真、跨文档事实冲突、AI Rules 错配、敏感值脱敏失败和 accepted issue 失控问题，并提出 AICC 后续优化方案。
keywords: aicc | first-release | acceptance-gate | health-check | ai-rules | sensitive-redaction | linguacafe
scope: AI-Coding-Context 路径 A 正式文档生成后的首版质量验收流程、模板、检查器和契约
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | workflows/shared/ai_checklist.md | templates/HEALTH_CHECK_REPORT_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | templates/AI_RULES_TEMPLATE.md | tools/py/doc_health_checker.py | tools/js/doc_health_checker.js | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js | core/security_rules.md | core/contracts/run_record_contract.yaml
dependencies: dev/plan/aicc-phase1-review-gate-followup-plan.md | dev/plan/aicc-generation-plan-review-process-gap-plan.md | dev/plan/linguacafe-phase1-aicc-improvement-plan.md
verified_at: 2026-05-18
---

# AICC 首版验收门禁可信度优化方案

## 1. 背景

LinguaCafe 项目在完成 Phase 1 方案审核后，继续按照 AICC 路径 A 生成正式 `dev_docs/` 文档体系。生成结果包含 16 个正式文档、3 个 `_analysis` 阶段文档以及 1 个首版验收报告：

- `dev_docs/AI_Coding_Context.md`
- `dev_docs/architecture_overview.md`
- `dev_docs/backend_architecture.md`
- `dev_docs/frontend_architecture.md`
- `dev_docs/api_layer.md`
- `dev_docs/database_schema.md`
- `dev_docs/async_realtime_workflow.md`
- `dev_docs/dictionary_language_domain.md`
- `dev_docs/reading_vocabulary_domain.md`
- `dev_docs/testing_guide.md`
- `dev_docs/deployment_guide.md`
- `dev_docs/python_tools.md`
- `dev_docs/vue3_migration_notes.md`
- `dev_docs/rules/combined/AI_RULES.md`
- `dev_docs/plans/README.md`
- `dev_docs/knowledge/README.md`
- `dev_docs/_analysis/generation_plan.md`
- `dev_docs/_analysis/project_analysis_report.md`
- `dev_docs/_analysis/generation_progress.md`
- `dev_docs/_analysis/health_check_report.md`

从流程层面看，这次测试证明 AICC 的 Phase 1 审核门已经能引导 AI 使用自然指令完成方案复查、回写 `_analysis` 三件套并等待用户确认。但正式文档生成完成后的首版验收暴露出新的系统性问题：AI 能生成完整文档体系，也会生成 `health_check_report.md`，却仍可能在检查器失败、事实冲突、规则错配和脱敏失败的情况下写出最终 `PASS`。

这说明当前 AICC 的问题重心已经从“Phase 1 方案是否可审核”转移到“首版正式文档是否可信、可验收、可作为后续 AI 编码入口”。本方案专门记录这次暴露的问题，并定义下一轮框架完善方向。

## 2. 本次评估事实

### 2.1 实际复跑命令

在 `/Users/zibuyu/code/openSource/LinguaCafe` 中复跑以下命令：

```bash
python3 AI-Coding-Context/tools/py/doc_health_checker.py --full-check --doc-dir dev_docs
node AI-Coding-Context/tools/js/doc_health_checker.js --full-check --doc-dir dev_docs
python3 AI-Coding-Context/tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .
node AI-Coding-Context/tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .
```

结果：

| 工具 | 结果 | issue 数 | 主要问题 |
| --- | --- | ---: | --- |
| Python `doc_health_checker` | FAIL | 3 | `health_check_report.md` 正文触发模板残留 marker |
| JS `doc_health_checker` | FAIL | 9 | 3 个模板残留 marker + 6 个 ESM 代码示例解析失败 |
| Python `semantic_review_checker` | PASS | 0 | 未发现当前规则覆盖范围内的问题 |
| JS `semantic_review_checker` | PASS | 0 | 与 Python 语义检查一致 |

`health_check_report.md` 却写出：

- 最终 verdict: `PASS`
- Python doc health: `PASS`
- JS doc health: `FAIL`，6 issues accepted
- semantic review: Python/JS 均 `PASS`

实际复跑结果说明：当前首版验收报告的最终 verdict 与机器检查结果不一致，且报告自身还引入了新的模板残留问题。

### 2.2 文档数量事实

实际 `dev_docs` 下有 20 个文件。`generation_progress.md` 和 `health_check_report.md` 多处仍写“19 个产物”或“全部 19 个产物已生成”。这里存在两个层面的不一致：

- Phase 1 计划中的“19 个产物”包含 `_analysis` 三件套和正式文档产物，但生成完成后又新增 `health_check_report.md`。
- 首版验收阶段没有把 `health_check_report.md` 纳入最终产物统计口径，导致进度、验收报告和实际文件数不一致。

这会影响后续恢复流程：如果 AI 根据 `generation_progress.md` 判断 19/19 已完成，它可能忽略健康报告自身是否已经有效落盘并通过自检。

### 2.3 事实冲突样例

本次人工复查发现以下工具未检出的跨文档事实冲突或高风险错配：

| 问题 | 文档位置 | 仓库事实 | 风险 |
| --- | --- | --- | --- |
| Web 层被写成 `Nginx/PHP-FPM` | `architecture_overview.md` | `docker/PhpDockerfile` 使用 `php:8.2-apache`，并复制 Apache vhost | 架构图、请求流和部署理解错误 |
| `AI_Coding_Context.md` 容器表写 `PHP-FPM + Nginx` | `AI_Coding_Context.md` | `deployment_guide.md` 与 Dockerfile 均显示 Apache | 入口文档误导后续 AI |
| AI Rules 写 Vuex 4 | `rules/combined/AI_RULES.md` | 根 `package.json` 为 `vuex ^3.6.2` | AI 后续编码规则错误 |
| AI Rules 写不存在的 Store 模块 | `rules/combined/AI_RULES.md` | 实际模块为 `shared`、`interactiveText`、`hoverVocabularyBox`、`vocabularyBox` | 直接误导前端改动 |
| `vue3_migration_notes.md` 局部写 Vue 2.7 / Vuex 4 | `vue3_migration_notes.md` | 根 `package.json` 为 Vue `^2.6.12`、Vuex `^3.6.2` | 迁移评估基线错误 |

这些问题不属于简单格式问题，而是 AICC 作为“AI 编码上下文入口”最应该防止的事实污染。

### 2.4 脱敏失败样例

Phase 1 方案和问题报告明确要求部署文档只列变量名和用途，不复述密码、Token、完整密钥或个人联系信息。但正式文档中仍出现：

- `DB_PASSWORD` 默认值。
- `REDIS_PASSWORD` 具体值。
- Reverb / Pusher 固定 key。
- 备份和恢复命令中把默认数据库用户名、数据库名与密码提示组合成可直接复制的连接凭据。

即使这些值来自开源仓库配置，也违反了本次 AICC 运行自己写下的质量保证措施。更重要的是，AICC 的定位不是“复刻配置文件”，而是为 AI 后续开发提供安全边界；部署文档可以说明“存在弱默认值”“生产环境必须改写”，但不应在指南中扩散具体敏感值。

### 2.5 accepted issue 失控样例

JS `doc_health_checker` 报 6 个 ESM `import` / `export` 语法误报，AI 将其标记为 accepted，并在最终报告中写 PASS。这里有两个独立问题：

- 若 accepted issue 只是工具误报，应有结构化豁免记录，包括 issue id、文件、原因、残余风险、后续工具修复目标。
- 如果任一检查器最终 exit code 仍为 1，默认不应写全局 PASS，除非框架明确允许某类已登记误报不影响最终 verdict，并能被工具再次验证。

当前 AICC 缺少 accepted issue 的可审计 schema，导致“工具失败”可以被自然语言解释绕过。

## 3. 问题分级

### 3.1 P0 阻断问题

以下问题必须在下一轮 AICC 优化中优先处理：

1. `health_check_report.md` 的最终 verdict 与实际机器检查结果不一致。
2. 任一 checker 失败后仍可写首版 `PASS`，缺少强制阻断。
3. `AI_RULES.md` 出现技术栈与源码事实冲突。
4. 文档违反自身 Phase 1 脱敏规则，复述敏感默认值或固定 key。
5. `architecture_overview.md` / `AI_Coding_Context.md` 出现核心运行架构事实错误。

### 3.2 P1 高优先级问题

1. `generation_progress.md` 产物统计与实际文件数不一致。
2. `health_check_report.md` 自身未被最终自检纳入稳定口径。
3. accepted issue 没有结构化豁免记录。
4. Python/JS `doc_health_checker` 对 ESM 示例的处理不一致或 JS 侧误报无法消解。
5. `semantic_review_checker` 未覆盖常见跨文档事实冲突。

### 3.3 P2 改进项

1. 健康报告模板中的示例 marker 容易触发模板残留检查。
2. 首版验收报告没有区分“生成前计划产物”“正式文档产物”“验收报告自身”。
3. 对“开源仓库中的默认配置是否算敏感信息”的规则还需要更细粒度定义。
4. 对历史文档和新规则之间的兼容策略需要写清楚。

## 4. 根因分析

### 4.1 首版验收 gate 还停留在流程说明层

`workflows/path_a_first_generation.md` 和 `workflows/generation_workflow.md` 已经要求首版生成后运行检查器并生成 `health_check_report.md`。但当前约束仍偏文字流程，没有形成足够强的工具阻断规则：

- `health_check_report.md` 可以人工写 `PASS`。
- `generation_progress.md` 可以写 Step 9/9 完成。
- 检查器失败可以被自然语言 accepted。
- 产物统计不一致不会阻断。

因此，AI 能“遵守流程形式”，却不能保证“验收结论真实”。

### 4.2 health_check_report 不是可审计运行记录

当前 `HEALTH_CHECK_REPORT_TEMPLATE.md` 更像人工报告模板，缺少机器可解析字段。它没有强制记录：

- 每个 checker 的实现语言。
- 原始命令。
- exit code。
- issue_count。
- status。
- disposition。
- accepted / waived issue 的逐项依据。
- final verdict 的计算规则。

这导致报告的最终 verdict 无法被工具反向验证。

### 4.3 accepted issue 没有进入契约层

Phase 1 已经引入了结构化 `machine_checks` 表，但首版验收阶段还没有同等强度的结构化规则。尤其 accepted issue 目前只是自然语言，缺少：

- 可枚举状态。
- 可验证原因。
- 与最终 verdict 的关系。
- 后续框架修复追踪。

没有契约层定义时，AI 容易把 accepted 当作“忽略失败”的通用出口。

### 4.4 语义检查缺少跨文档事实模型

现有 `semantic_review_checker` 已能发现部分事实冲突、量化声明和 Phase 1 gate 问题，但还没有建立“正式文档事实表”：

- 技术栈版本事实来自 `package.json`、`composer.json`、Dockerfile。
- 运行架构事实来自 Dockerfile、Compose、Supervisor、配置文件。
- AI Rules 必须从主文档和源码事实派生，不能独立发明。
- 入口文档、架构文档、部署文档之间必须对关键事实保持一致。

因此，Apache/Nginx、Vuex 版本、Store 模块这类跨文档错配没有被工具发现。

### 4.5 脱敏规则没有被工具化

`core/security_rules.md` 和方案文档已有脱敏要求，但 `doc_health_checker` / `semantic_review_checker` 没有把“本次方案要求脱敏”转换成正式文档检查条件。结果是：

- Phase 1 写了“不要复述默认密码”。
- 正式文档仍复述默认密码。
- 健康报告未将其视为 blocker。

这是方案约束没有传递到首版验收的典型问题。

### 4.6 AI_RULES 的风险权重不足

`AI_RULES.md` 是后续 IDE / Agent 自动加载的规则源。它一旦错，危害比普通说明文档更大。但当前验收没有把它作为高风险产物单独检查：

- 技术栈版本必须严格来自依赖文件。
- 测试策略必须遵守 `CONTRIBUTING.md`。
- 路由、认证、状态管理、部署边界必须和主文档一致。

当前 AI Rules 生成后只被当作普通 Markdown 检查，这是不足的。

## 5. 优化目标

### 5.1 总目标

将 AICC 路径 A 的首版验收从“文件生成完成 + 人工报告 PASS”升级为“机器可验证、跨文档一致、可审计豁免、脱敏合规的质量门禁”。

### 5.2 具体目标

1. 任一必需 checker 失败时，默认最终 verdict 为 `FAIL`，不得写全局 `PASS`。
2. 若存在 accepted issue，必须用结构化表格记录，并且只能接受框架定义允许豁免的问题类型。
3. `health_check_report.md` 必须能被 `doc_health_checker` 自身检查通过。
4. `generation_progress.md` 的完成状态必须与 `health_check_report.md` 的最终 verdict 和实际产物数量一致。
5. `AI_RULES.md` 的技术栈、状态管理、测试策略、路由认证和部署边界必须与源码和主文档一致。
6. 入口、架构、部署、AI Rules 之间的关键事实必须一致。
7. 如果 Phase 1 方案要求脱敏，正式文档不得复述具体密码、Token、固定 key、个人邮箱等敏感值。
8. Python/JS 双实现对同一文档体系的关键 verdict 必须一致；不一致时不得通过首版验收。

## 6. 目标状态设计

### 6.1 首版验收状态机

建议 AICC 定义以下状态：

| 状态 | 含义 | 允许下一步 |
| --- | --- | --- |
| `首版验收中` | 正式文档已生成，正在运行检查器和人工语义复核 | 修复问题或生成验收报告 |
| `首版需修正` | 发现 blocker 或未豁免失败项 | 回写正式文档并复跑检查 |
| `首版建议通过` | 所有 blocker 清零，允许等待用户确认 | 用户确认后标记完成 |
| `已完成` | 用户已接受首版验收或框架任务明确结束 | 后续进入维护模式 |

约束：

- 工具失败时不得进入 `首版建议通过`。
- `health_check_report.md` 未落盘或未通过自检时不得进入 `首版建议通过`。
- `generation_progress.md` 的“当前状态”不得与 `health_check_report.md` 的 final verdict 矛盾。

### 6.2 health_check_report 结构化 schema

建议健康报告必须包含以下章节：

```markdown
## machine_checks

| round | tool | implementation | command | exit_code | issue_count | status | disposition |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1 | doc_health_checker | python | `...` | 0 | 0 | PASS | verified |
| 1 | doc_health_checker | js | `...` | 0 | 0 | PASS | verified |
| 1 | semantic_review_checker | python | `...` | 0 | 0 | PASS | verified |
| 1 | semantic_review_checker | js | `...` | 0 | 0 | PASS | verified |

## accepted_issues

| issue_id | tool | file | issue_type | original_status | accepted_reason | residual_risk | follow_up |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

规则：

- `machine_checks` 必须覆盖 Python/JS 两套 `doc_health_checker` 和 `semantic_review_checker`。
- `exit_code != 0` 且 `disposition != accepted` 时 final verdict 必须为 `FAIL`。
- `accepted_issues` 为空时必须写“无 accepted issue”，不能省略章节。
- accepted issue 必须逐项列出，不能只写“ESM 误报若干”。
- 如果 accepted issue 属于 checker 缺陷，`follow_up` 必须指向 AICC 框架修复方向。

### 6.3 final verdict 计算规则

建议引入固定计算规则：

| 条件 | final verdict |
| --- | --- |
| 任一必需文档缺失 | `FAIL` |
| 任一 checker 未运行且无 `UNAVAILABLE` 说明 | `FAIL` |
| 任一 checker `exit_code != 0` 且无合法 accepted issue | `FAIL` |
| 存在 blocker 级事实冲突 | `FAIL` |
| 存在敏感值泄露 | `FAIL` |
| `AI_RULES.md` 与源码事实冲突 | `FAIL` |
| 只有 warning 或 accepted issue，且均有结构化说明 | `PASS_WITH_ACCEPTED_ISSUES` |
| 无 issue | `PASS` |

如果当前 AICC 暂不想引入新 verdict 值，也至少应规定：存在 accepted issue 时，最终结论不能写裸 `PASS`，必须写“建议通过，含已接受问题”，并保留风险说明。

### 6.4 敏感值处理规则

建议将敏感值分为三类：

| 类型 | 示例 | 正式文档处理 |
| --- | --- | --- |
| 真实 secret / token / key | API Key、Pusher/Reverb key、邮箱登录密码 | 不复述具体值，只写变量名和来源文件 |
| 弱默认凭据 | 默认数据库密码、Redis 密码、root 密码 | 不复述具体值；说明存在弱默认值并要求生产改写 |
| 公开标识但可滥用 | 容器名、数据库名、公开端口 | 可写，但避免与密码组合成可直接复制的连接凭据 |

特殊规则：

- 即使值来自开源仓库，也不代表 AICC 文档可以复述。
- 如果用户明确要求部署文档可复制运行，则可以提供命令，但密码位置应使用占位变量，例如 `<DB_USER>`、`<DB_NAME>`，避免写出真实默认密码。
- `health_check_report.md` 应记录是否执行敏感值扫描，以及扫描结果。

### 6.5 AI_RULES 高风险校验

建议对 `dev_docs/rules/combined/AI_RULES.md` 增加专门校验：

| 校验项 | 事实源 | 示例 |
| --- | --- | --- |
| 前端框架版本 | `package.json` | Vue 2.6，不得写 Vue 2.7 |
| 状态管理版本 | `package.json` | Vuex 3，不得写 Vuex 4 |
| Store 模块 | `resources/js/vuex/`、`resources/js/app.js` | 不得列不存在模块 |
| Web 服务层 | Dockerfile、Supervisor 配置 | Apache 不得写 Nginx/PHP-FPM |
| 测试策略 | `CONTRIBUTING.md`、`tests/` | 不得建议普通 PR 添加测试 |
| 路由/认证 | `routes/web.php`、`routes/api.php`、中间件 | 不得引导新增 API 到 `routes/api.php` |

AI Rules 检查失败应视为 blocker，因为它会直接污染后续 Agent 行为。

### 6.6 跨文档事实一致性检查

建议 `semantic_review_checker` 增加“关键事实抽取 + 跨文档一致性”规则，首批覆盖：

- Web 服务层：Apache / Nginx / PHP-FPM。
- 前端框架：Vue 主版本、Vuex 主版本、构建工具。
- 生产前端入口：`resources/js/` 与 `resources/vue3/` 的边界。
- 队列和广播：Horizon / Reverb / Redis 的关系。
- API 路由事实源：`routes/web.php` vs `routes/api.php`。
- 测试策略：测试存在情况与维护者贡献规则。

实现上不需要一次做通用 NLP。可以先使用规则化事实抽取：

- 从依赖文件和 Dockerfile 提取事实。
- 在 Markdown 中查找高风险关键词组合。
- 当文档出现与源码事实相反的关键词时报 issue。

## 7. 具体改进任务

### Task A: 首版验收报告结构化

目标文件：

- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `workflows/shared/ai_checklist.md`
- `core/contracts/run_record_contract.yaml`

改进内容：

1. 在健康报告模板中新增 `machine_checks` 表。
2. 新增 `accepted_issues` 表，要求逐项记录 accepted issue。
3. 明确 final verdict 计算规则。
4. 明确 `PASS_WITH_ACCEPTED_ISSUES` 或“建议通过，含已接受问题”的表达方式。
5. 规定健康报告必须自检通过后才能作为首版验收报告。
6. 在 progress 模板中新增“首版质量验收记录”结构化章节。

验收标准：

- 新模板不会因自身示例文本触发模板残留检查。
- 生成的 `health_check_report.md` 能被 Python/JS `doc_health_checker --full-check` 检查。
- `generation_progress.md` 必须能记录首版验收的机器检查、回写动作和最终状态。

### Task B: doc_health_checker 增加首版验收完整性检查

目标文件：

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/tests/test_doc_health_checker.py`
- `tools/js/doc_health_checker.test.js`

新增 issue type：

| issue type | 触发条件 |
| --- | --- |
| `health_report_machine_checks_missing` | `health_check_report.md` 缺少结构化 machine_checks |
| `health_report_verdict_conflicts_with_checks` | final verdict 与 machine_checks 结果矛盾 |
| `health_report_accepted_issue_missing_detail` | accepted issue 缺少原因、残余风险或 follow-up |
| `health_report_self_template_residue` | 健康报告自身包含会触发模板残留的 marker |
| `progress_completion_without_valid_health_report` | progress 写已完成，但健康报告缺失或 FAIL |
| `artifact_count_mismatch` | progress/report 产物数量与实际文件数或计划口径不一致 |

验收标准：

- 构造 LinguaCafe-like fixture：健康报告写 PASS 但机器检查中 JS doc health FAIL，必须报 `health_report_verdict_conflicts_with_checks`。
- 构造健康报告正文含模板 marker 的 fixture，必须报 `health_report_self_template_residue`。
- 构造 progress 写 Step 9/9 完成但健康报告 FAIL 的 fixture，必须报 `progress_completion_without_valid_health_report`。
- 修正 fixture 后 Python/JS 检查结果一致。

### Task C: accepted issue 契约与白名单

目标文件：

- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`

改进内容：

1. 定义 accepted issue 必填字段：
   - `issue_id`
   - `tool`
   - `implementation`
   - `file`
   - `issue_type`
   - `original_status`
   - `accepted_reason`
   - `residual_risk`
   - `follow_up`
2. 定义 accepted issue 不得覆盖的类型：
   - 敏感值泄露。
   - AI Rules 与源码事实冲突。
   - 核心架构事实冲突。
   - 必需文档缺失。
   - 健康报告自身检查失败。
3. 定义可临时 accepted 的类型：
   - 明确的检查器解析误报。
   - 历史文档兼容问题。
   - 运行时环境不可用但有人工替代复核。
4. accepted issue 存在时，最终结论必须显式带有“含已接受问题”。

验收标准：

- 未提供 `residual_risk` 的 accepted issue 会失败。
- 将敏感值泄露标记 accepted 会失败。
- 将 ESM 解析误报标记 accepted 且字段齐全，可通过但 final verdict 不得写裸 `PASS`。

### Task D: ESM 代码示例解析修复

目标文件：

- `tools/js/doc_health_checker.js`
- `tools/js/doc_health_checker.test.js`
- `tools/py/doc_health_checker.py`
- `tools/py/tests/test_doc_health_checker.py`

改进内容：

1. JS 版代码示例检查识别 ESM `import` / `export`。
2. 对 Markdown 中标为 `javascript` 的片段，如果包含 ESM 语法，使用可解析的 module 模式检查，或降级为语法片段检查。
3. Python/JS 对同一 ESM 示例给出一致结果。
4. 不因真实语法错误被误认为 ESM 误报。

验收标准：

- `export default defineConfig({})` 示例不再误报。
- `import { createApp } from "vue"` 示例不再误报。
- 破损的 ESM 示例仍能报出语法错误。
- LinguaCafe 当前 `frontend_architecture.md` 与 `vue3_migration_notes.md` 不再产生 6 个 JS 侧误报。

### Task E: 敏感值扫描与方案约束传递

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `core/security_rules.md`
- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`

新增 issue type：

| issue type | 触发条件 |
| --- | --- |
| `sensitive_default_value_repeated` | 正式文档复述默认密码或固定 key |
| `sensitive_policy_declared_but_violated` | Phase 1 要求脱敏，但正式文档复述敏感值 |
| `secret_like_value_in_docs` | 文档出现疑似 token/key/password 且无脱敏说明 |

改进内容：

1. 从 Phase 1 方案中识别是否声明脱敏要求。
2. 从正式文档中扫描高风险变量和值组合。
3. 对 `docker-compose.yml` 中默认密码和固定 key，允许文档写变量名、风险和来源文件，不允许写具体值。
4. 对个人邮箱、Discord 等联系信息默认不在 dev_docs 中复述，除非用户明确要求。

验收标准：

- 文档中写 `DB_PASSWORD` 变量名不报错。
- 文档中写具体默认密码时报 `sensitive_default_value_repeated`。
- 文档中写具体 Reverb/Pusher key 时报 `secret_like_value_in_docs`。
- 健康报告能汇总敏感值扫描结果。

### Task F: AI_RULES 高风险一致性校验

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `templates/AI_RULES_TEMPLATE.md`
- `workflows/path_a_first_generation.md`

新增 issue type：

| issue type | 触发条件 |
| --- | --- |
| `ai_rules_dependency_version_conflict` | AI Rules 写的技术栈版本与依赖文件冲突 |
| `ai_rules_state_module_conflict` | AI Rules 写的状态管理模块不存在 |
| `ai_rules_test_policy_conflict` | AI Rules 测试建议与 `CONTRIBUTING.md` 冲突 |
| `ai_rules_runtime_stack_conflict` | AI Rules 运行架构与 Dockerfile / Compose 冲突 |

验收标准：

- LinguaCafe-like fixture 中 `Vuex 4` 对 `vuex ^3.6.2` 必须失败。
- AI Rules 写 `user_storage` / `theme`，但 `resources/js/vuex/` 不存在对应文件，必须失败。
- `CONTRIBUTING.md` 写“PR 不要添加测试”时，AI Rules 不得建议普通 PR 默认补测试。
- 修正后 Python/JS 语义检查一致通过。

### Task G: 跨文档运行架构一致性检查

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/testdata/semantic_review/first_release_acceptance_case/`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`

首批规则：

1. 如果 Dockerfile 使用 `php:*-apache` 或 Supervisor 启动 `apache2-foreground`，正式文档不得把 Web 层写成 Nginx/PHP-FPM。
2. 如果根 `package.json` 写 Vue `^2.6.x`，正式文档不得写生产前端为 Vue 2.7 或 Vue 3。
3. 如果根 `package.json` 写 Vuex `^3.x`，正式文档不得写生产状态管理为 Vuex 4。
4. 如果 `resources/vue3/package.json` 独立存在且根 package 无 workspace，正式文档必须把它与生产入口区分。
5. 如果 `routes/web.php` 承载主要业务路由，正式文档不得建议新增业务 API 到 `routes/api.php`。

验收标准：

- LinguaCafe-like fixture 中 Apache 被写成 Nginx 时失败。
- Vuex 3 被写成 Vuex 4 时失败。
- `resources/vue3/` 被写成生产入口时失败。
- 正确文档通过。

### Task H: 产物统计与完成状态一致性

目标文件：

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `templates/PROGRESS_TEMPLATE.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`

改进内容：

1. 明确三类计数：
   - Phase 1 方案产物数。
   - 正式文档产物数。
   - 首版验收报告数。
2. `generation_progress.md` 不再只写单一 `19/19`，而是写：
   - `_analysis` 方案产物完成数。
   - 正式文档完成数。
   - 验收产物完成数。
   - 总文件数。
3. `health_check_report.md` 检查范围必须与实际 `dev_docs` 文件数一致。
4. 如果报告写“全部 N 个产物”，checker 应核对实际数量或至少核对与 progress 一致。

验收标准：

- 实际 20 文件但报告写 19 时，报 `artifact_count_mismatch`。
- 健康报告自身生成后，progress 必须更新验收产物计数。
- 修正后计数一致。

### Task I: 首版验收输出措辞收紧

目标文件：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`

改进内容：

1. 禁止在存在 accepted issue 时写“全部通过”“无问题”“PASS”这类无条件结论。
2. 禁止在任一 checker 失败时写“首版验收完成”。
3. 推荐输出：
   - “首版建议通过，含已接受问题”
   - “首版需修正”
   - “首版阻塞，等待修复”
4. 用户确认前，progress 不应从 `首版建议通过` 自动跳到 `已完成`。

验收标准：

- fixture 中 checker 失败但报告写“最终 verdict: PASS”必须失败。
- fixture 中 accepted issue 存在但报告写“全部通过”必须失败。

## 8. 测试计划

### 8.1 单元测试

必须新增或更新以下测试：

```bash
python3 -m unittest tools/py/tests/test_doc_health_checker.py
python3 -m unittest tools/py/tests/test_semantic_review_checker.py
node tools/js/doc_health_checker.test.js
node tools/js/semantic_review_checker.test.js
```

测试覆盖：

- 健康报告 verdict 与 machine checks 矛盾。
- accepted issue 字段不完整。
- accepted issue 试图覆盖敏感值泄露。
- 健康报告自引用模板 marker。
- Apache 被写成 Nginx。
- Vuex 3 被写成 Vuex 4。
- AI Rules Store 模块不存在。
- 正式文档复述默认密码或固定 key。
- 产物数量不一致。

### 8.2 框架自检

执行：

```bash
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
```

预期：

- Python/JS self-check 均通过。
- 新增模板和契约不引入路径错误、模板残留或缺失依赖。

### 8.3 LinguaCafe 回归测试

使用当前 LinguaCafe 文档作为真实反例，预期新检查器至少报出：

- `health_report_verdict_conflicts_with_checks`
- `health_report_self_template_residue`
- `ai_rules_dependency_version_conflict`
- `ai_rules_state_module_conflict`
- `sensitive_policy_declared_but_violated`
- `runtime_stack_conflict` 或等价运行架构冲突 issue
- `artifact_count_mismatch`

在 LinguaCafe 文档修正后，预期：

- Python/JS `doc_health_checker` 通过。
- Python/JS `semantic_review_checker` 通过。
- `health_check_report.md` final verdict 与机器结果一致。
- `generation_progress.md` 状态与验收报告一致。

## 9. 实施顺序建议

### 阶段 1: 先收紧首版验收报告与 progress

优先修改：

- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `doc_health_checker`

原因：这是阻止“检查失败但写 PASS”的最小闭环。

### 阶段 2: 修复 JS ESM 误报与 accepted issue 契约

优先修改：

- `tools/js/doc_health_checker.js`
- accepted issue schema
- 对应测试

原因：只有减少误报并规范豁免，才能避免 AI 借 accepted issue 逃过 gate。

### 阶段 3: 增加 AI_RULES 和跨文档事实一致性检查

优先修改：

- `semantic_review_checker`
- `AI_RULES_TEMPLATE.md`
- LinguaCafe-like fixture

原因：这部分直接决定生成的上下文是否能安全地指导后续 AI 编码。

### 阶段 4: 增加敏感值扫描

优先修改：

- `core/security_rules.md`
- `semantic_review_checker`
- 健康报告汇总

原因：脱敏规则已经在方案中存在，但缺少工具执行；这会影响所有项目。

## 10. 边界情况

### 10.1 开源仓库默认值是否允许写入文档

默认不允许复述密码、key、token 的具体值。允许写：

- 变量名。
- 配置文件路径。
- 风险说明。
- 生产环境必须改写。

如果用户明确要求生成可复制部署脚本，可以使用占位变量，不写真实默认值。

### 10.2 只存在 Python 或 Node 环境

如果某一实现不可运行：

- `machine_checks` 中必须写 `UNAVAILABLE`。
- 必须写明原因。
- 必须记录替代复核方式。
- 不得把 `UNAVAILABLE` 写成 `PASS`。

首版验收默认应为 warning 或 `PASS_WITH_ACCEPTED_ISSUES`，不能写裸 `PASS`。

### 10.3 历史文档兼容

对旧版本 AICC 生成的文档：

- 如果只是缺少新字段，但没有声明首版 PASS，可报 warning。
- 如果声明首版 PASS 或已完成，则必须满足新 gate。
- 如果用户请求“只读评估”，不应自动修改旧文档，但应列出阻断项。

### 10.4 AI_RULES 中的简化表达

AI Rules 可以简短，但不能错误。允许写“Vue 2 + Vuex”，不强制写 patch 版本；不允许写 Vuex 4、Pinia、Nginx 等源码不支持的事实。

### 10.5 accepted issue 的长期处理

accepted issue 不是永久豁免。健康报告应记录 follow-up，AICC 计划文档应沉淀工具改进方向。对于同类 accepted issue 第三次出现，应优先修复检查器而不是继续接受。

### 10.6 规则分层与误伤控制

首版实现应区分通用规则和生态特定规则：

- 通用规则：健康报告 verdict、machine checks、accepted issue schema、敏感值扫描、产物计数一致性，适用于所有项目。
- Web/PHP/Laravel/Vue 规则：Apache/Nginx/PHP-FPM、Vue/Vuex、Laravel 路由、CONTRIBUTING 测试策略，只在仓库存在对应事实源时启用。
- 缺少事实源时不应推断失败，只能报 warning 或跳过。例如无 Dockerfile 的项目不应触发运行架构冲突，无 `AI_RULES.md` 的项目不应触发 AI Rules 专项失败。

这样可以让 LinguaCafe 暴露的问题沉淀为 AICC 能力，而不是把 LinguaCafe 的技术栈硬编码成所有项目的验收标准。

### 10.7 代码示例与敏感值扫描的边界

文档引用源码片段时，也应遵守脱敏策略。允许说明“源码中存在固定 key/default password”，但不应在正式文档中完整复述具体值，除非该值被明确判定为非敏感公开常量且不会与连接凭据、账号或公网端点组合成可滥用信息。

敏感值扫描不应简单禁止所有 `KEY`、`PASSWORD`、`TOKEN` 字样；它应重点检查“变量名 + 具体值”的组合，并允许只写变量名、配置路径、风险说明和替换建议。

## 11. 成功判定

本方案实施完成后，应满足：

1. LinguaCafe 当前首版文档在未修正前不能通过新 AICC 验收。
2. 修正后的 LinguaCafe 文档能通过 Python/JS 双实现。
3. 健康报告 final verdict 可由 machine checks 和 accepted issue 表推导。
4. AI Rules 不再包含与源码依赖、目录、测试策略冲突的规则。
5. 文档不再复述默认密码、固定 key 或个人联系信息。
6. `generation_progress.md` 与 `health_check_report.md` 的状态、产物数量、验收结果一致。
7. 新增规则不误伤简单项目、无 Docker 项目、无 AI Rules 项目或历史未完成文档。

## 12. 对当前 AICC 定位的影响

这次优化会把 AICC 从“能生成项目文档体系”进一步推进到“能验证文档体系是否足以作为 AI 编码入口”。两者的差别很关键：

- 普通文档生成可以接受局部错误，后续人工慢慢修。
- AI 编码上下文入口不能包含高风险错误，因为后续 Agent 会把这些内容当作规则和事实执行。

因此，首版验收必须特别关注：

- 入口文档是否会误导。
- AI Rules 是否会误导。
- 架构图是否会误导。
- 部署和安全说明是否会扩散风险。
- 检查报告是否可信。

本方案的核心不是追求更多检查项，而是让“首版验收 PASS”变成一个有工程含义的结论：正式文档体系已经具备作为后续 AI 工作入口的最低可信度。
