---
title: AICC Memex 首次运行复测问题记录与优化方案
summary: 记录 Memex 作为新测试项目首次运行 AICC 后暴露的首版生成绕过审核、健康报告缺失、运行记录不完整、测试拓扑漏记和检查器误报问题，并沉淀下一轮 AICC 框架优化方向。
keywords: aicc | memex | first-run | path-a | first-release | health-check | testing-topology | semantic-review
scope: AI-Coding-Context 路径 A 首次运行、正式文档生成后首版验收、运行记录契约、检查器语义质量和测试项目复测闭环
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | templates/HEALTH_CHECK_REPORT_TEMPLATE.md | tools/py/doc_health_checker.py | tools/py/semantic_review_checker.py | tools/py/summary_validator.py | tools/js/doc_health_checker.js | tools/js/semantic_review_checker.js | core/contracts/run_record_contract.yaml
dependencies: dev/plan/done/aicc-first-release-acceptance-gate-improvement-plan.md | dev/plan/done/aicc-phase1-review-gate-followup-plan.md | dev/plan/done/aicc-generation-plan-review-process-gap-plan.md | dev/plan/linguacafe-phase1-aicc-improvement-plan.md
verified_at: 2026-05-18
status: done（已实施并验证，2026-06-13 归档）
---

# AICC Memex 首次运行复测问题记录与优化方案

> **状态：✅ 已实施并验证（done）** — 本方案提出的改进已落地到框架（契约 / 检查器 / 模板 / 工作流，Python+JS 一致并配有通过的测试），于 2026-06-13 经逐任务核验后归档至 `dev/plan/done/`。以下为当时的规划与问题记录，保留作开发档案，措辞中的“待办/暴露的问题”为历史状态。

## 1. 背景

Memex 是本轮 AICC 的新测试项目，路径为：

- 项目根目录：`/Users/zibuyu/code/openSource/memex`
- 首次运行产物目录：`/Users/zibuyu/code/openSource/memex/dev_docs`
- AICC 框架目录：`/Users/zibuyu/code/zibuyu/AI-Coding-Context`

本次测试的输入场景是“用户携带 AICC 入口文档，在一个没有既有 `dev_docs/` 的真实开源项目中执行路径 A 首次生成”。终端输出显示 AI 已完成中文开发文档体系生成，入口为 `dev_docs/AI_Coding_Context.md`，并新增 13 个 Markdown 文档：

- `dev_docs/AI_Coding_Context.md`
- `dev_docs/README.md`
- `dev_docs/_analysis/generation_plan.md`
- `dev_docs/_analysis/project_analysis_report.md`
- `dev_docs/_analysis/generation_progress.md`
- `dev_docs/architecture/overview.md`
- `dev_docs/architecture/data_storage.md`
- `dev_docs/architecture/event_task_agent_pipeline.md`
- `dev_docs/modules/agent_system.md`
- `dev_docs/modules/ui_navigation.md`
- `dev_docs/platform/build_release.md`
- `dev_docs/testing/testing_guide.md`
- `dev_docs/rules/combined/AI_RULES.md`

终端输出还声明以下检查已经通过：

- `env_diagnosis.py`
- `project_scanner.py --exclude-standard --mode summary`
- `summary_validator.py --dir dev_docs --recursive --strict`
- 敏感词扫描只命中安全规则说明，没有真实密钥或 token

但是，基于当前 AICC 已强化的 Phase 1 方案审核门和首版验收门禁重新复核后，本次运行不能视为完整通过。它证明 AI 可以快速生成一套可读的首版文档，但也暴露出 AICC 仍允许“格式通过、流程跳过、语义未验收”的系统性缺口。

## 2. 本次复核结论

### 2.1 总体判断

本次 Memex 首次运行结果应判定为：

| 维度 | 结论 | 说明 |
| --- | --- | --- |
| 文档生成完整性 | 部分通过 | 已生成 13 个文档，覆盖主入口、分析三件套、架构、模块、平台、测试和 AI Rules。 |
| 基础格式检查 | 通过 | `summary_validator --strict` 显示 13/13 valid。 |
| 当前 AICC 结构健康检查 | 不通过 | `doc_health_checker --full-check` 发现 28 个 issue。 |
| 当前 AICC 语义检查 | 不通过 | `semantic_review_checker --full-check` 发现 7 个 issue。 |
| Phase 1 审核流程 | 不通过 | 直接进入正式文档生成，没有停在方案审核和用户确认门。 |
| 首版验收记录 | 不通过 | 缺少 `dev_docs/_analysis/health_check_report.md`。 |
| 可作为后续 AI 编码入口 | 有条件可用 | 核心架构方向基本正确，但运行记录、测试拓扑和验收可信度不足。 |

### 2.2 复核命令与结果

在 AICC 仓库中复跑：

```bash
python3 tools/py/summary_validator.py --dir /Users/zibuyu/code/openSource/memex/dev_docs --recursive --strict
```

结果：

| 指标 | 值 |
| --- | ---: |
| total_files | 13 |
| processed | 13 |
| valid | 13 |
| invalid | 0 |
| total_warnings | 0 |

这与终端输出一致，说明 13 个文档的 frontmatter 和 summary 格式是合格的。

继续复跑：

```bash
python3 tools/py/doc_health_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/memex/dev_docs
```

结果：

| 指标 | 值 |
| --- | ---: |
| passed | false |
| total_issues | 28 |
| targets_count | 13 |

继续复跑：

```bash
python3 tools/py/semantic_review_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/memex/dev_docs --repo-root /Users/zibuyu/code/openSource/memex
```

结果：

| 指标 | 值 |
| --- | ---: |
| passed | false |
| issues | 7 |

因此，终端输出中的“验证已完成”不能等同于“当前 AICC 首版验收通过”。这次测试再次证明 AICC 必须强制 AI 区分不同检查器的职责边界：

- `summary_validator`：只证明摘要/frontmatter 格式。
- `doc_health_checker`：证明结构、运行记录、模板残留、主入口章节和首版验收契约。
- `semantic_review_checker`：证明事实一致性、测试拓扑、审核门状态和首版语义风险。
- `health_check_report.md`：证明首版验收结果可审计、可恢复、可复核。

## 3. 暴露的问题

### 3.1 P0：路径 A 首次运行绕过 Phase 1 方案审核门

#### 现象

Memex 本次运行没有停在 `_analysis` 三件套生成后的人工审核阶段，而是直接生成了正式文档体系：

- `dev_docs/AI_Coding_Context.md`
- `dev_docs/README.md`
- `dev_docs/architecture/*`
- `dev_docs/modules/*`
- `dev_docs/platform/*`
- `dev_docs/testing/*`
- `dev_docs/rules/combined/AI_RULES.md`

`generation_progress.md` 中写明：

```text
当前 gate：首批正式文档生成与自检。
```

这说明 AI 将首次运行理解为“一次性完成正式文档体系生成”，而不是当前 AICC 期望的路径 A 分阶段流程。

#### 为什么这是框架问题

AICC 当前路径 A 的核心定位是：

1. 先分析项目并生成 `dev_docs/_analysis/generation_plan.md`。
2. 回写 `project_analysis_report.md` 和 `generation_progress.md`。
3. 执行 Phase 1 方案复查。
4. 等待用户确认或明确授权。
5. 再进入正式文档生成。
6. 正式文档生成后进入首版验收。

Memex 的结果说明：即使 LinguaCafe 复测后 AICC 已强化 Phase 1 审核门，AI 在新的真实项目中仍可能走回“一次性生成全部文档”的旧行为。根因可能是入口文档、工作流和模板中的执行路径仍不足以在用户普通首次生成指令下强制“先停门、后生成”。

#### 风险

- 用户没有机会先审核方案清单和风险判断。
- `generation_plan.md` 变成事后记录，而不是正式文档生成前的决策依据。
- 后续文档若基于错误方案批量生成，修复成本显著增加。
- AICC 的 Phase 1 gate 变成可被绕过的建议流程，而不是强约束流程。

#### 优化方向

1. `AI_ENTRY_POINT.md` 中应明确：路径 A 首次生成默认不得一次性完成正式文档，除非用户明确说“跳过审核、直接生成正式文档”。
2. `workflows/path_a_first_generation.md` 应把 Phase 1 停门定义为硬步骤，而不是推荐步骤。
3. `generation_progress.md` 模板应要求记录：
   - `phase1_plan_created`
   - `phase1_review_completed`
   - `user_confirmed_formal_generation`
   - `formal_docs_generation_started`
   - `first_release_acceptance_completed`
4. `doc_health_checker` 应检查：如果正式文档已经存在，但 `_analysis` 中没有用户确认或授权记录，应报 `formal_docs_generated_without_phase1_confirmation`。

### 3.2 P0：正式文档已生成但缺少首版验收报告

#### 现象

`dev_docs/_analysis` 下只有：

- `generation_plan.md`
- `project_analysis_report.md`
- `generation_progress.md`

不存在：

- `dev_docs/_analysis/health_check_report.md`

但终端输出称“已完成 AICC 首次运行的中文开发文档体系生成”，并列出验证已完成。

#### 为什么这是框架问题

当前 AICC 已将首版正式文档生成后的验收独立建模为 first-release acceptance gate。正式文档生成完成后，AI 应生成结构化 `health_check_report.md`，记录：

- 实际文档清单。
- 机器检查命令、实现语言、退出码、issue 数、状态、处置。
- accepted issue 的逐项说明。
- 敏感信息扫描结果。
- 最终 verdict 的计算依据。
- 是否允许将 `dev_docs/AI_Coding_Context.md` 作为后续 AI 编码入口。

Memex 运行没有生成该报告，说明首版验收门禁仍没有在路径 A 正式生成完成后稳定触发。

#### 风险

- 用户只能看到“终端说通过”，无法复查机器检查原始依据。
- 后续 AI 无法知道首版文档是否已经通过验收，还是仅完成了格式检查。
- `generation_progress.md` 无法承担健康报告职责，恢复流程缺少可信锚点。

#### 优化方向

1. Path A workflow 明确：只要正式文档区出现 `AI_Coding_Context.md` 或 `rules/combined/AI_RULES.md`，就必须生成 `health_check_report.md`。
2. `generation_progress.md` 不能把首版生成标为完成，除非 `health_check_report.md` 存在且 verdict 非阻塞。
3. `doc_health_checker` 应新增检查：
   - `formal_docs_without_health_report`
   - `progress_completion_without_health_report`
   - `health_report_missing_after_ai_rules_generated`
4. 终端总结模板必须区分：
   - “正式文档已生成”
   - “首版验收报告已生成”
   - “首版验收通过”
   - “仍待用户审核/修正”

### 3.3 P0：`summary_validator` 被误用为最终质量依据

#### 现象

终端输出把 `summary_validator.py --dir dev_docs --recursive --strict` 通过作为主要验证依据之一，并写明：

```text
13/13 valid，0 warning
```

当前复跑证实这是真实结果。但同一产物在更完整检查下失败：

- `doc_health_checker`：28 issues。
- `semantic_review_checker`：7 issues。

#### 为什么这是框架问题

`summary_validator` 的职责是校验 summary/frontmatter 元数据，不负责：

- Phase 1 是否被绕过。
- health report 是否存在。
- 运行记录是否符合契约。
- 主入口章节是否完整。
- 测试拓扑是否覆盖。
- 跨文档事实是否一致。
- 敏感信息是否符合项目级约束。

如果 AI 在终端总结中把 `summary_validator` 通过表述为“验证已通过”，用户很容易误解为“文档体系质量通过”。

#### 风险

- 弱检查结果被包装成强结论。
- AICC 的检查器分层失效。
- 用户无法判断问题出在格式、结构、语义还是流程。

#### 优化方向

1. `AI_ENTRY_POINT.md` 和工作流中明确禁止将 `summary_validator` 单独作为最终通过依据。
2. 终端输出模板应固定使用分层表述：
   - 元数据检查：通过/失败。
   - 结构健康检查：通过/失败/未运行。
   - 语义复查：通过/失败/未运行。
   - 首版验收：通过/失败/未运行。
3. 检查器可增加 `summary_only_validation_misrepresented` 检查：当 progress 或 health report 写“验证通过”但只记录了 `summary_validator`，应报 warning 或 blocker。

### 3.4 P1：`generation_progress.md` 不符合当前运行记录契约

#### 现象

`doc_health_checker` 对 `generation_progress.md` 报出运行记录缺失项，包括：

- `开始时间`
- `最后更新`
- `当前状态`
- `总体步骤进度`
- `流程阶段进度`
- `产物完成度`
- `逐文档完成状态`
- `总任务数`
- `已完成数`
- `下一步动作`

当前 `generation_progress.md` 只有：

- 当前阶段。
- `machine_checks` 表。
- 已生成清单。
- `writeback_summary`。
- 下一步。

这些内容对人工阅读足够，但对 AICC 的可恢复运行记录不够。

#### 为什么这是框架问题

`generation_progress.md` 的定位不是普通日志，而是 AICC 运行状态机的恢复入口。它必须支持：

- 中断后恢复。
- 用户审核时定位当前 gate。
- 检查器验证是否已完成必要步骤。
- AI 判断是否允许进入下一阶段。

Memex 结果说明：AI 仍可能生成简化版 progress，缺少当前契约字段。

#### 优化方向

1. `PROGRESS_TEMPLATE.md` 中将运行记录字段做成不可省略表格或 YAML-like 块。
2. `doc_health_checker` 继续保持对 progress 必需项的严格检查。
3. Path A 终端总结中应提示：如果 progress 记录不完整，即使文档已生成，也不能声明完整通过。
4. 提供一段“最小合法 progress 结构”给 AI 复制使用，避免自由发挥。

### 3.5 P1：`generation_plan.md` 仍是简版事后方案

#### 现象

`doc_health_checker` 对 `generation_plan.md` 报出缺失项，包括：

- `🎯 任务复杂度评估 (Complexity Assessment)`
- `⚠️ 风险点与注意事项`
- `🤝 交互策略 (Interaction Strategy)`
- `📚 第三阶段：子文档规划（待审核）`
- `📊 质量保证措施`
- `🧾 证据与验证记录`
- `🔎 Phase 1 方案复查清单`

当前 `generation_plan.md` 记录了项目检测结果、子文档清单、批次计划和质量门禁，但没有体现完整 Phase 1 方案复查流程。

#### 为什么这是框架问题

这说明 AI 把 `generation_plan.md` 当作“生成后摘要”，而不是“正式文档生成前必须审核的方案”。它缺少：

- 复杂度与规模判断依据。
- 用户交互策略。
- 分批生成边界。
- 证据等级和验证记录。
- Phase 1 复查清单。
- 哪些事项必须等待用户确认。

#### 优化方向

1. `GENERATION_PLAN_TEMPLATE.md` 中的必需章节要与 checker 保持一致。
2. `doc_health_checker` 的 required section 检查应继续阻断声明已通过的简版方案。
3. Path A 首次生成时，如果用户未明确要求直接生成正式文档，AI 应只生成 `_analysis` 三件套，不生成正式文档。
4. 若用户明确要求一次性生成，仍必须把 `generation_plan.md` 写成完整方案，并在 `generation_progress.md` 记录用户授权。

### 3.6 P1：主入口文档与当前 AICC 必需章节不一致

#### 现象

`doc_health_checker` 对 `dev_docs/AI_Coding_Context.md` 报出 10 个缺失必需章节：

- `📊 项目概览`
- `📂 关键目录速查`
- `🎯 场景快速导航`
- `🚀 文档索引`
- `💻 核心代码模式`
- `🛠️ 开发流程规范`
- `📋 命名规范`
- `🏢 业务模块映射`
- `⚠️ AI 编码禁忌`
- `🔧 常见任务速查`

当前 Memex 主入口文档有以下章节：

- 项目定位。
- 先读顺序。
- 代码边界速览。
- 常见任务路由。
- 验证基线。

内容本身可读，但不满足当前主入口模板。

#### 为什么这是框架问题

这里有两个可能问题：

1. AI 没有使用当前模板生成主入口文档。
2. AICC checker 对主入口章节要求过于固定，未允许新模板风格。

从框架定位看，主入口必须稳定，因为它是后续 AI 编码时最可能被首先加载的文档。章节可以优化，但模板和检查器必须一致，不能出现“AI 生成一套结构，checker 要另一套结构”的漂移。

#### 优化方向

1. 明确 `AI_Coding_Context.md` 的必需章节是否仍保留 emoji 章节名。
2. 如果主入口模板已演进，应同步更新 `doc_health_checker` 的 required sections。
3. 如果 required sections 仍是标准，则 Path A workflow 应强制使用主入口模板，不允许自由写作替代。
4. 允许项目定制章节，但不能缺少等价语义块。可设计“章节别名表”，例如：
   - `项目定位` 可等价于 `📊 项目概览` 的部分内容。
   - `代码边界速览` 可等价于 `📂 关键目录速查` 与 `💻 核心代码模式` 的组合。
   但在首版验收中必须能被工具识别。

### 3.7 P1：测试拓扑文档低估了真实项目测试结构

#### 现象

`semantic_review_checker` 报出测试拓扑未覆盖：

- `ios/RunnerTests/`
- `tests/`

人工复核还发现 Memex 实际测试远不止 `testing_guide.md` 中提到的少量 domain model 测试。真实项目包含：

- `ios/RunnerTests/RunnerTests.swift`
- `tests/tools/test_compare_flutter_analyze.py`
- `tests/tools/test_compare_flutter_test_failures.py`
- `tests/tools/test_pr_policy_check.py`
- `tests/tools/test_pr_preflight_summary_comment.py`
- `test/agent/*`
- `test/data/repositories/*`
- `test/data/services/*`
- `test/db/*`
- `test/domain/models/*`
- `test/integration/*`
- `test/ui/*`
- `test/utils/*`

但 `dev_docs/testing/testing_guide.md` 写的是：

```text
当前测试主要位于 test/，已有 domain model 测试覆盖系统事件、LLM config、日程聚合和位置上下文配置。
```

#### 为什么这是框架问题

测试策略文档是 AI 后续修改代码时决定“该跑什么、该补什么测试”的关键入口。低估测试拓扑会导致：

- AI 忽略已有 agent/service/ui/integration 测试。
- AI 不知道 Python 工具测试存在。
- iOS 原生测试被遗漏。
- 变更验证基线过弱。

Memex 是 Flutter + iOS + Python tools 混合项目，AICC 需要更强的测试拓扑发现和回写机制。

#### 优化方向

1. `project_scanner` 或 `semantic_review_checker` 的 test topology 结果必须回写到 `testing_guide.md`。
2. 测试文档模板应包含：
   - 已发现测试目录表。
   - 每个目录的测试语言/框架推断。
   - 文件数量。
   - 适用验证命令。
   - 是否纳入默认验证基线。
3. 当实际存在多个测试根目录，而 testing 文档只覆盖一个目录时，应报 `test_topology_under_documented`。
4. 对 Flutter 项目，应默认扫描：
   - `test/`
   - `integration_test/`
   - `ios/*Tests/`
   - `androidTest/`
   - `tests/` 工具测试目录

### 3.8 P1：检查器存在“同义规则被误判为事实冲突”的风险

#### 现象

`semantic_review_checker` 的 `fact_conflicts` 包含部分可疑误报，例如：

- `MemexRouter`：文档写“优先补 Repository 或 Service，再通过 MemexRouter 暴露给 ViewModel”，权威文件写“MemexRouter is a thin routing/facade; do not put complex business logic in MemexRouter”。二者语义基本一致。
- `*.g.dart`：文档写“不要手改 `*.g.dart`”，权威文件写“Generated output should not be edited by hand”。二者语义一致。
- `GlobalEventBus`：权威文件只是 PR policy 中的 sensitive keyword 提醒，检查器却把它当作事实冲突对比对象。

#### 为什么这是框架问题

语义检查器的价值是发现真实事实冲突，而不是把同义改写或审查关键词都升级为 blocker。误报过多会导致：

- AI 或用户降低对 checker 的信任。
- 真实问题被噪声淹没。
- accepted issue 增加，反而削弱门禁。

#### 优化方向

1. `semantic_review_checker` 区分三类结果：
   - `hard_fact_conflict`：版本、技术栈、运行架构、文件存在性等客观冲突。
   - `rule_rephrasing_similarity`：同义规则改写，默认 info。
   - `sensitive_keyword_attention`：PR policy 或安全关键词提示，默认 warning/info。
2. 对 `AGENTS.md`、`CONTRIBUTING.md`、PR policy 文档建立不同权威类型，而不是统一按事实冲突处理。
3. 对“不要手改生成文件”“薄门面”“不要放业务逻辑”等规则类句子，允许同义表达，只在文档表达相反时才报 blocker。
4. 增加 Memex-like fixture，覆盖 `MemexRouter` 和 `*.g.dart` 的同义规则案例。

### 3.9 P2：敏感词扫描命令自身触发模板残留/关键词误报

#### 现象

`generation_progress.md` 的 `machine_checks` 表记录了敏感词扫描命令：

```bash
rg -n "<marker:T-B-D>|<marker:T-O-D-O>|待补充|真实 API|sk-|eyJ|password|token|密钥" dev_docs
```

`doc_health_checker` 报出：

```text
template_residue: marker <marker:T-O-D-O> line 27
```

这里的 `<marker:T-O-D-O>` 是扫描命令中的模式，不是文档模板残留。

#### 为什么这是框架问题

AICC 鼓励记录检查命令，但 checker 又把命令中的扫描模式当作模板残留。这会形成自我冲突：AI 越完整记录扫描命令，越容易触发误报。

#### 优化方向

1. 模板残留检查应识别 Markdown 表格中的 `command` 列或 fenced code block 中的扫描模式。
2. 对 `rg -n "...<marker:T-O-D-O>..."` 这类命令上下文豁免模板残留。
3. 如果文档正文出现模板占位 marker 仍应报 issue；如果出现在命令字符串中，应记录为 `ignored_marker_in_checker_command` 或不报。

### 3.10 P2：AICC 对“新测试项目结果如何沉淀”缺少统一归档结构

#### 现象

Dayflow、LinguaCafe、Memex 都作为 AICC 测试项目暴露问题，但当前 `dev/plan` 中的文档命名和层级仍偏单次复盘：

- `dayflow-phase1-aicc-improvement-plan.md`
- `linguacafe-phase1-aicc-improvement-plan.md`
- `aicc-phase1-review-gate-followup-plan.md`
- `aicc-first-release-acceptance-gate-improvement-plan.md`
- 本文档新增 `aicc-memex-first-run-regression-plan.md`

随着测试项目增多，AICC 需要更清晰地区分：

- 测试项目运行结果。
- 暴露的问题。
- 已实施的框架修复。
- 未实施的后续计划。
- 可回放的 fixture。

#### 优化方向

1. 后续可建立 `dev/quality/test-runs/<project>/<date>/` 保存原始运行摘要、复跑命令和检查结果。
2. `dev/plan` 保留可执行优化方案，不承载所有原始日志。
3. 每个测试项目复盘文档应有统一字段：
   - 测试项目。
   - AICC 版本/commit。
   - 用户指令。
   - 生成产物。
   - 复跑命令。
   - 失败点。
   - 框架根因。
   - 是否已有修复。
   - 后续验证方式。

## 4. 系统架构视角的根因分析

### 4.1 AICC 状态机仍不够硬

前几轮 LinguaCafe 测试主要修复了“用户要求审核 `_analysis` 时，AI 必须进入 Phase 1 Review Gate”的问题。Memex 暴露的是更早的一步：用户首次要求生成文档时，AI 仍可能直接跑完整路径 A。

这说明 AICC 需要把路径 A 拆成两个不同的默认模式：

| 模式 | 默认行为 | 进入条件 |
| --- | --- | --- |
| 保守首次生成 | 只生成 `_analysis` 三件套并停门 | 用户没有明确授权跳过审核 |
| 一次性首版生成 | 生成正式文档并执行首版验收 | 用户明确要求直接生成完整文档体系 |

如果不区分，AI 会根据“创建开发文档体系”的自然语言倾向一次性完成全部工作。

### 4.2 检查器分层没有被终端总结内化

当前工具层已经有多种 checker，但 AI 终端总结仍可能只列成功项，省略未运行项。例如 Memex 输出中没有 `doc_health_checker`、`semantic_review_checker` 和 `health_check_report.md`，但语气接近“已完成”。

这不是单个 checker 能解决的问题，需要在 AICC 响应模板中强制列出所有必需检查的运行状态：

- `PASS`
- `FAIL`
- `NOT_RUN`
- `UNAVAILABLE`
- `WAIVED_WITH_REASON`

任何 `NOT_RUN` 或 `FAIL` 都不能被自然语言“验证已完成”覆盖。

### 4.3 文档模板、检查器和 AI 行为仍存在版本漂移

Memex 主入口文档的章节结构可读但不符合 checker required sections。这说明至少存在一种漂移：

- AI 没有使用当前模板。
- 当前模板没有被入口文档强制引用。
- checker 仍要求旧模板。
- 或者模板允许自由结构但 checker 不识别等价章节。

AICC 作为框架，必须保证“AI 应生成什么”和“checker 要求什么”是同一契约。

### 4.4 项目定位识别成功，但验收机制没有跟上项目复杂度

Memex 的核心事实识别总体是成功的：

- Flutter 移动应用。
- iOS/Android。
- 本地优先。
- Provider + GoRouter。
- Drift SQLite。
- 文件系统工作区。
- `dart_agent_core`。
- Agent / Skill / 事件总线 / 持久任务。

但项目复杂度较高，真实测试拓扑、平台能力、Agent 安全边界和数据存储边界都需要更强验收。AICC 不能只因为核心定位抓对，就认为首版文档体系可通过。

### 4.5 首版文档质量应按风险区域加权

对 Memex 这类本地优先 AI 移动应用，以下区域的文档错误风险更高：

- 本地数据位置和迁移。
- LLM provider 与用户配置。
- Agent 文件权限。
- 后台任务与崩溃恢复。
- iOS/Android 权限。
- 测试和验证基线。

当前首版验收没有根据项目类型加权，只做通用 Markdown 检查。后续 AICC 应根据项目类型动态增加验收关注点。

### 4.6 初步根因排查：不是单点回归，而是高层路由与局部门禁不一致

本轮进一步排查了当前 AICC 的入口文档、Path A 工作流、通用生成工作流和最近相关提交。初步结论是：Memex 没有停在 Phase 1，不像是某个最近提交直接删除了等待审核步骤，而是既有“完整执行路径 A”的高层表达与近期新增的 Phase 1 / 首版验收 gate 没有完全对齐。

#### 当前文档中的矛盾证据

| 位置 | 当前表达 | 对 AI 的潜在影响 |
| --- | --- | --- |
| `AI_ENTRY_POINT.md` 路由决策表 | `dev_docs/` 不存在 → 路径 A，说明为“执行 Step 2-8” | 暗示首次生成应从扫描一路执行到正式文档生成，而不是默认停在 Step 7.5。 |
| `AI_ENTRY_POINT.md` 路由索引 | 路径 A 的读取时机为“立即读取 - 执行首次生成流程” | 没有在路由层强调“默认只到 Phase 1 审核门”。 |
| `workflows/path_a_first_generation.md` frontmatter summary | 描述为“配置读取、项目检测、策略决策、方案生成、人工审核等待与正式生成的完整首轮流程” | “完整首轮流程”容易被理解为一次性完成全生命周期。 |
| `workflows/path_a_first_generation.md` Step 4 策略表 | 小型项目策略写“一次性完成”，中大型写分批 | 这里的一次性/分批本意应是用户确认后的正式生成方式，但没有明确排除 Phase 1 前置停门。 |
| `workflows/path_a_first_generation.md` Step 7.5 | 明确“暂停执行，等待用户确认” | 局部门禁是正确的，但与高层“执行 Step 2-8”冲突。 |
| `AI_ENTRY_POINT.md` Phase 1 方案复查请求路由 | 只覆盖用户后续要求“审核 `_analysis` / 判断 Phase 1 是否通过”的场景 | 对“首次创建文档体系”这个入口场景缺少同等强度的默认停门规则。 |
| `AI_ENTRY_POINT.md` 首版正式文档验收请求路由 | 只覆盖正式文档已经生成后用户要求验收的场景 | 没有规定“正式文档一旦生成，AI 必须主动进入首版验收并产出 health report”。 |

#### 最近提交排查结果

| 提交 | 相关变化 | 与本问题的关系 |
| --- | --- | --- |
| `f2d0321 prompt(fix): harden Phase 1 AICC review gates` | 引入或强化 Phase 1 自检、证据等级、项目定位和测试拓扑检查。 | 之前已有“等待人工审核”，该提交强化了局部门禁，但没有消除入口层“路径 A 执行 Step 2-8”的表达。 |
| `098c3bd feat: enforce Phase 1 plan review gate` | 在 `AI_ENTRY_POINT.md` 增加 Phase 1 方案复查请求路由，并在流程图中加入 Step 7.4。 | 修复的是“用户要求审核 `_analysis` 时如何处理”，不是“首次生成默认必须停在 Phase 1”。 |
| `081a5f9 feat: harden AICC first-release acceptance gate` | 增加首版正式文档验收请求路由、health report 契约、accepted issue 和敏感值规则。 | 修复的是“正式文档已生成后如何验收”，但没有检查“正式文档生成时是否缺少 health report”。 |

因此，Memex 暴露的问题更准确地说是“近期 gate 改动落地不完整”，不是“最近改动引入了反向规则”。当前 AICC 同时存在：

- 局部正确规则：Step 7.5 必须等待人工审核；用户确认后才能执行 Step 8。
- 高层歧义规则：路径 A 路由表仍写执行 Step 2-8；Path A 摘要仍描述完整首轮流程。
- 工具缺口：即使正式文档已经生成且没有 `health_check_report.md`，当前 checker 还没有把它作为显式 blocker。

#### 对后续修复的直接启示

1. 入口路由层必须先修：`dev_docs/` 不存在时，默认路由应写成“执行 Step 2-7.5，等待用户确认”，而不是“执行 Step 2-8”。
2. Path A 文档标题和摘要需要区分“全生命周期说明”和“单次默认执行边界”。
3. Step 4 的“一次性完成/分批”必须改写为“用户确认后的正式生成策略”，避免被理解成 Phase 1 前就可一次性生成。
4. Phase 1 方案复查请求路由应扩展为“首次生成默认停门规则”，而不只覆盖后续审核请求。
5. 首版验收门禁应由请求触发和状态触发两种方式驱动：只要正式文档存在且 progress 声明生成完成，就必须要求 `health_check_report.md`。

## 5. 后续 AICC 优化方案

### Task 0：修正 Path A 高层路由口径

**目标**：消除入口层“执行 Step 2-8”与 Step 7.5 “等待人工审核”之间的冲突。

**涉及文件**：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`

**要求**：

1. 将 `AI_ENTRY_POINT.md` 路由决策表中 `dev_docs/` 不存在的说明改为“执行 Step 2-7.5，等待用户确认”。
2. 将路径 A 路由索引中的“执行首次生成流程”补充为“默认只到 Phase 1 审核门”。
3. 将 `workflows/path_a_first_generation.md` summary 改写为“定义完整生命周期；默认单次执行在 Step 7.5 停止”。
4. 将 Step 4 策略表中的“一次性完成/分批”明确限定为“用户确认后正式生成阶段的执行方式”。
5. 在 `generation_workflow.md` 的 Phase 1 gate 前增加同样约束，避免通用生成工作流绕过 Path A 细则。

**验收**：

- 搜索 `执行 Step 2-8` 不再命中入口路由。
- 搜索 `一次性完成` 的上下文明确限定为用户确认后的正式生成阶段。
- 入口文档、Path A 工作流和通用生成工作流都明确“首次生成默认停在 Phase 1 人工审核门”。

### Task 1：强化路径 A 默认停门规则

**目标**：防止首次运行直接跳过 Phase 1 方案审核。

**涉及文件**：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `templates/PROGRESS_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

**要求**：

1. 默认路径 A 首次运行只生成 `_analysis` 三件套。
2. 正式文档生成需要用户明确确认或明确授权跳过审核。
3. 如果正式文档已生成但缺少确认记录，checker 报 blocker。
4. 如果用户明确要求一次性生成，progress 必须记录授权来源和授权文本摘要。

**验收**：

- 构造 fixture：有正式文档、无 Phase 1 确认记录，`doc_health_checker` 必须失败。
- 构造 fixture：有正式文档、有用户授权记录、有 health report，`doc_health_checker` 可继续进入后续检查。

### Task 2：正式文档生成后强制首版验收报告

**目标**：确保生成正式文档后一定有可审计的 `health_check_report.md`。

**涉及文件**：

- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

**要求**：

1. 检测到 `dev_docs/AI_Coding_Context.md`、`dev_docs/rules/combined/AI_RULES.md` 或正式子文档时，必须要求 `dev_docs/_analysis/health_check_report.md`。
2. `generation_progress.md` 的完成状态必须引用 health report verdict。
3. health report 本身必须通过模板残留、machine checks 和 accepted issues schema 检查。

**验收**：

- Memex-like fixture 当前应失败，错误包括 `formal_docs_without_health_report`。
- 补充合法 health report 后，错误转移到真实语义/结构问题，而不是缺失报告。

### Task 3：终端总结和 progress 强制区分检查器层级

**目标**：防止 `summary_validator` 通过被误解为整体通过。

**涉及文件**：

- `AI_ENTRY_POINT.md`
- `workflows/shared/ai_checklist.md`
- `workflows/path_a_first_generation.md`
- `templates/PROGRESS_TEMPLATE.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`

**要求**：

1. 终端总结必须列出：
   - `summary_validator`
   - `doc_health_checker`
   - `semantic_review_checker`
   - `health_check_report`
2. 每项状态只能是 `PASS`、`FAIL`、`NOT_RUN`、`UNAVAILABLE`、`WAIVED_WITH_REASON`。
3. 如果任一首版必需项为 `NOT_RUN` 或 `FAIL`，不得写“首版验收通过”。
4. `summary_validator` 只能被描述为“元数据/摘要格式检查”。

**验收**：

- 构造 progress 只记录 `summary_validator PASS` 却写“验证通过”，checker 报 `summary_only_validation_misrepresented`。

### Task 4：测试拓扑发现必须回写测试文档

**目标**：让测试策略文档真实反映项目测试结构。

**涉及文件**：

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `templates` 中 testing guide 相关模板

**要求**：

1. 扫描测试目录时覆盖常见命名：
   - `test/`
   - `tests/`
   - `integration_test/`
   - `ios/*Tests/`
   - `androidTest/`
   - `__tests__/`
   - `spec/`
2. testing 文档必须列出所有非空测试根目录。
3. 对每个测试根目录记录：
   - 路径。
   - 文件数量。
   - 推断语言/框架。
   - 推荐运行命令。
4. 若实际测试目录未被 testing 文档覆盖，报 `test_topology_under_documented`。

**验收**：

- Memex-like fixture 中 `test/`、`tests/`、`ios/RunnerTests/` 均需被检测并要求文档覆盖。

### Task 5：修正模板残留检查对扫描命令的误报

**目标**：避免 `rg "...<marker:T-O-D-O>..."` 这种检查命令自身触发模板残留。

**涉及文件**：

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- 对应测试文件

**要求**：

1. Markdown 表格 `command` 列中的 `<marker:T-O-D-O>`、`<marker:T-B-D>`、`<marker:fill>` 等扫描模式不作为模板残留。
2. fenced code block 中若上下文是检查命令，也可豁免。
3. 正文段落、列表项、标题中的 marker 仍必须报 issue。

**验收**：

- `rg -n "<marker:T-B-D>|<marker:T-O-D-O>|待补充" dev_docs` 不触发 template residue。
- 正文段落中的待办占位语句仍触发 template residue。

### Task 6：语义检查器区分真实事实冲突与同义规则表达

**目标**：降低 `MemexRouter`、`*.g.dart` 这类同义规则误报。

**涉及文件**：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- 对应测试文件

**要求**：

1. 将语义检查结果分为：
   - `hard_fact_conflict`
   - `rule_conflict`
   - `rule_rephrasing_similarity`
   - `sensitive_keyword_attention`
2. 对 PR policy 中的“敏感关键词提示”不再直接作为事实冲突 authority。
3. 对生成文件不可手改、薄门面、分层边界等规则类内容，只在表达相反时阻断。

**验收**：

- 文档写“不要手改 `*.g.dart`”与权威文档写“Generated output should not be edited by hand”不报 blocker。
- 文档写“可以直接编辑 `*.g.dart`”必须报 blocker。

### Task 7：建立测试项目复盘归档规范

**目标**：让 Dayflow、LinguaCafe、Memex 等测试项目结果可持续沉淀。

**涉及文件**：

- `dev/plan/README.md`
- 可新增 `dev/quality/test-runs/README.md`
- 可新增测试运行记录模板

**要求**：

1. 每次测试项目复盘都记录：
   - 测试项目路径。
   - AICC commit。
   - 用户指令。
   - 生成产物。
   - 复跑命令。
   - 失败点。
   - 框架根因。
   - 后续优化任务。
2. 原始日志和复跑结果建议进入 `dev/quality/test-runs/`，`dev/plan` 只保留转化后的优化方案。
3. 后续可把 Memex 这类真实项目结果提炼成 checker fixture。

**验收**：

- 新增复盘模板。
- `dev/plan/README.md` 能索引所有已沉淀的测试项目问题文档。

## 6. 与既有计划的关系

### 6.1 与 LinguaCafe Phase 1 计划的关系

LinguaCafe 暴露的是 Phase 1 审核门本身的问题：用户要求审核 `_analysis` 时，AI 是否会进入专门复查流程、是否回写三件套、是否等待用户确认。

Memex 暴露的是更完整路径上的问题：

- 首次运行是否默认停在 Phase 1。
- 正式文档生成后是否强制首版验收。
- AI 是否把 `summary_validator` 误当总验收。
- 测试拓扑和主入口模板是否被真实项目复杂度检验。

因此，本文档不是替代 LinguaCafe 计划，而是对路径 A “从首次生成到首版验收”的下一层补充。

### 6.2 与 first-release acceptance gate 计划的关系

`aicc-first-release-acceptance-gate-improvement-plan.md` 已经处理了 LinguaCafe 正式文档生成后出现的 PASS 失真、AI Rules 错配、敏感值脱敏等问题。

Memex 复测说明：即使这些能力已经在框架中加强，新的首次运行仍可能因为没有生成 `health_check_report.md` 而完全绕过首版验收。这意味着下一轮优化重点应包括：

- 不只是“health report 写错时如何阻断”。
- 还要“正式文档已生成但 health report 不存在时如何阻断”。

### 6.3 与 generation_plan 复查流程计划的关系

`aicc-generation-plan-review-process-gap-plan.md` 关注的是 `generation_plan.md` 复查机制。Memex 结果证明该问题仍然存在新的变体：`generation_plan.md` 可以作为事后简版摘要出现，并不承担正式文档生成前的 gate 作用。

因此，后续实现应把 `generation_plan.md` 的完整性检查与“是否已经生成正式文档”联动：如果正式文档已经存在，`generation_plan.md` 更不能是简版或缺少复查记录。

## 7. 边界问题与设计取舍

### 7.1 是否允许用户一次性生成正式文档

允许，但必须显式记录授权。AICC 不应阻止高级用户一次性生成完整文档体系，但默认路径应保守。合理策略是：

- 默认：先生成 `_analysis`，等待审核。
- 用户明确要求“一次性生成完整文档体系”：允许，但必须同步生成完整方案、progress 和 health report。
- 用户只说“开始创建开发文档体系”：按默认保守路径解释，不应自动跳过 Phase 1。

### 7.2 历史产物是否全部按新规则失败

不应对所有历史产物无差别 blocker。建议兼容策略：

- 如果只存在 `_analysis` 且未声明 PASS：缺少新字段可 warning。
- 如果声明 Phase 1 建议通过：必须满足 Phase 1 gate。
- 如果正式文档已生成：必须满足首版验收 gate。
- 如果正式文档已生成且 progress 声明完成：缺少 health report 应 blocker。

### 7.3 主入口章节是否必须固定 emoji 标题

需要进一步确认。固定标题便于工具检查，但可能降低项目适配性。建议方案：

- 保留必需语义块，不强依赖 emoji 标题。
- checker 支持章节别名和语义等价映射。
- 模板仍提供标准标题，降低 AI 自由发挥。

### 7.4 检查器误报是否应阻断

真实误报不应无限阻断，但必须结构化 accepted。当前 Memex 的 `MemexRouter` / `*.g.dart` 语义误报提示我们：检查器需要降低误报，同时 accepted issue 仍要可审计。

建议策略：

- 明确误报类型，降级为 info/warning。
- 对真正 blocker 不允许自然语言 waived。
- accepted issue 必须有 issue id、原因、残余风险、后续修复目标。

### 7.5 是否需要立即修复 Memex 的 dev_docs

本文档目标不是修复 Memex 项目文档，而是记录 AICC 框架问题。Memex 可作为后续复测样本，建议先完善 AICC，再用同一项目重新运行或要求 AI 按新框架复查。

## 8. 建议下一步

优先级建议：

1. 先实现 Task 1 和 Task 2：阻断“跳过 Phase 1”和“正式文档无 health report”。
2. 再实现 Task 3：统一终端总结和 progress 的检查器状态表达。
3. 随后实现 Task 4：修测试拓扑发现和回写，因为这是 Memex 当前最真实的内容缺陷。
4. 并行修 Task 5 和 Task 6：降低 checker 自身误报，避免后续门禁噪声过高。
5. 最后实现 Task 7：建立测试项目复盘归档规范。

### 8.1 本轮实施结果

已按本文档完成首轮 AICC 框架修复，实施范围覆盖 Task 0 至 Task 7 的核心要求：

| 任务 | 实施状态 | 已落地内容 | 验证方式 |
| --- | --- | --- | --- |
| Task 0 | 已完成 | `AI_ENTRY_POINT.md`、Path A 和通用生成 workflow 均明确首次运行默认停在 Step 7.5 Phase 1 人工审核门。 | `rg "执行 Step 2-8"` 不再命中入口路由；流程文档包含默认停门说明。 |
| Task 1 | 已完成 | `doc_health_checker` 新增正式文档缺 Phase 1 确认记录 blocker；progress 模板和运行记录契约新增正式生成授权字段。 | Python/JS doc health checker 回归测试覆盖 `formal_docs_generated_without_phase1_confirmation`。 |
| Task 2 | 已完成 | `doc_health_checker` 新增正式文档缺 `health_check_report.md` blocker；health report 模板补充分层 checker 记录。 | Python/JS doc health checker 回归测试覆盖 `formal_docs_without_health_report`。 |
| Task 3 | 已完成 | progress 模板新增 checker status matrix；checker 新增 `summary_only_validation_misrepresented`，阻断只用 `summary_validator` 声称整体验证通过。 | Python/JS doc health checker 回归测试覆盖 summary-only 误表述。 |
| Task 4 | 已完成 | `semantic_review_checker` 测试拓扑扫描扩展到 `test/`、`tests/`、`integration_test/`、`ios/*Tests/`、`androidTest/`、`__tests__/`、`spec/`，并忽略空测试根。 | Python/JS semantic checker 回归测试覆盖 Memex 风格 `test/`、`tests/`、`ios/RunnerTests/`。 |
| Task 5 | 已完成 | 模板残留检查新增对扫描命令中 `<marker:T-O-D-O>`、`<marker:T-B-D>` 和中文待填标记的上下文豁免，同时正文占位仍阻断。 | Python/JS doc health checker 回归测试覆盖扫描命令豁免和正文残留阻断。 |
| Task 6 | 已完成 | 语义检查器将规则类冲突标记为 `rule_conflict`，并把 “should not be edited by hand” 与“不要手改”识别为同向规则，避免同义表达误报。 | Python/JS semantic checker 回归测试覆盖 `*.g.dart` 同义规则和反向规则。 |
| Task 7 | 已完成 | 新增 `dev/quality/test-runs/README.md` 与 `templates/test_run_report_TEMPLATE.md`，明确真实项目复测归档规范。 | 文档健康检查与 `git diff --check` 作为最终复检项。 |

### 8.2 剩余注意事项

- 当前实现对“只有 `AI_Coding_Context.md`、没有其他正式子文档、也没有 health report”的极简历史产物保持兼容，不直接按正式文档缺 health report 阻断；一旦出现正式子文档、AI Rules 或 health report，即进入首版验收契约。
- `summary_validator` 已纳入 health report 模板和契约，但它仍只代表元数据/摘要格式检查，不能替代 `doc_health_checker` 和 `semantic_review_checker`。
- 后续用 Memex 或 LinguaCafe 再测时，应优先观察 AI 是否在首次运行默认停在 `_analysis` 三件套和 Phase 1 审核门。

## 9. 当前结论

Memex 首次运行说明 AICC 已能帮助 AI 快速抓住真实项目的核心定位，并生成一套可读的中文首版文档。但从框架愿景看，这次运行仍不能算通过：

- 它绕过了 Phase 1 默认审核门。
- 它生成正式文档后没有生成首版验收报告。
- 它把 `summary_validator` 通过包装成较强的验证结论。
- 它没有满足当前 progress 和 generation plan 契约。
- 它遗漏了真实测试拓扑。
- 它暴露了 semantic checker 的同义规则误报。

因此，下一轮 AICC 优化不应只补单个文档模板，而应强化路径 A 状态机：首次生成、方案审核、用户确认、正式生成、首版验收必须成为可检查的连续链路。只有这样，AICC 才能在 Dayflow、LinguaCafe、Memex 这类不同技术栈项目中稳定产出可信的 AI 编码上下文。
