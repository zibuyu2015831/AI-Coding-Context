---
title: 文档引用审查报告
summary: 全项目 305 个 Markdown 文档的跨文档引用审查记录。已修复的 20 处确定性失效引用见"已修复清单"；本文档主体记录所有需用户拍板的不确定项。
scope: 全项目（含 dev/）
audit_date: 2026-04-25
auditor: AI（6 个并行子代理扫描 + 主线程汇总核验）
---

# 文档引用审查报告

## 审查方法

- **范围**：项目内全部 305 个 `.md` 文件，含 `dev/` 目录（按用户指示，`.gitattributes` 中排除 `dev/` 仅用于 merge 时不污染 main，审查时纳入）。
- **引用定义**：仅文档间的相互引用（`[text](path)`、`[text][id]` + `[id]: path`、纯文本中的内部路径）；外部 URL 不在范围。
- **修复边界**：链接失效 **且** 新位置唯一明确才直接修复；目标不存在或多个候选则记录待决策。
- **已剔除范围**：
  - `dev/reference/ai-coding-prompt-java-main/` 内部互引（vendored sub-project，非本项目维护）。
  - `.py` 等非文档文件的引用（如 `tools/py/git_diff_analyzer.py`）。

---

## 已修复清单（CERTAIN_FIX，共 20 处 / 11 个文件）

| # | 文件 | 行 | 修复内容 |
|---|---|---|---|
| 1 | `.kiro/specs/post-generation-audit/QUICK_START.md` | 274 | `../../workflows/path_a_first_generation.md` → `../../../workflows/path_a_first_generation.md`（路径深度差 1） |
| 2 | 同上 | 275 | `../../workflows/shared/ai_checklist.md` → `../../../workflows/shared/ai_checklist.md` |
| 3 | 同上 | 276 | `../../templates/AI_Coding_Context_TEMPLATE.md` → `../../../templates/AI_Coding_Context_TEMPLATE.md` |
| 4 | `dev/FRAMEWORK_CONTEXT.md` | 746 | `../quality/README.md` → `./quality/README.md`（原路径解析到 repo 根，应留在 dev/ 内） |
| 5 | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` | 777 | `[001-ai-mutual-review.md](./001-ai-mutual-review.md)` → `[013-ai-mutual-review.md](../013-ai-mutual-review/013-ai-mutual-review.md)`（编号笔误 001→013，路径同目录→兄弟目录） |
| 6 | 同上 | 778 | `./011-doc-error-fix-workflow.md` → `../011-doc-error-fix-workflow/011-doc-error-fix-workflow.md` |
| 7 | 同上 | 779 | `./012-mandatory-doc-summary.md` → `../012-mandatory-doc-summary/012-mandatory-doc-summary.md` |
| 8 | `dev/V3.0/confirmed/012-mandatory-doc-summary/012-mandatory-doc-summary.md` | 746 | `./confirmed/016-...` → `../016-unified-config-system/016-unified-config-system.md`（路径双重错误：confirmed/ 内引用又写了 confirmed/） |
| 9 | 同上 | 747 | `./confirmed/017-...` → `../017-utility-script-library/017-utility-script-library.md` |
| 10 | 同上 | 748 | `../../workflows/generation_workflow.md` → `../../../../workflows/generation_workflow.md`（路径深度差 2） |
| 11 | 同上 | 749 | `../../workflows/incremental_update_workflow.md` → `../../../../workflows/incremental_update_workflow.md` |
| 12 | 同上 | 750 | `../../workflows/document_health_check.md` → `../../../../workflows/document_health_check.md` |
| 13 | `dev/V3.0/confirmed/011-doc-error-fix-workflow/011-doc-error-fix-workflow.md` | 941 | `../../workflows/incremental_update_workflow.md` → `../../../../workflows/incremental_update_workflow.md` |
| 14 | 同上 | 942 | `../../workflows/document_health_check.md` → `../../../../workflows/document_health_check.md` |
| 15 | 同上 | 943 | `../../core/update_triggers.md` → `../../../../core/update_triggers.md` |
| 16 | `dev/V3.0/confirmed/013-ai-mutual-review/013-ai-mutual-review.md` | 1245 | `../../reference/AI编程的现状.md` → `../../../reference/AI编程的现状.md`（dev/ 内 reference/，深度差 1） |
| 17 | 同上 | 1246 | `../../reference/AI_PROGRAMMING_ANALYSIS.md` → `../../../reference/AI_PROGRAMMING_ANALYSIS.md` |
| 18 | `dev/real_case/002/quality_review/COMPREHENSIVE_AUDIT.md` | 539-540 | `../../workflows/...` → `../../../../workflows/...`（深度差 2） |
| 19 | `dev/real_case/002/quality_review/MAIN_DOC_AUDIT.md` | 655 | `../../templates/AI_Coding_Context_TEMPLATE.md` → `../../../../templates/AI_Coding_Context_TEMPLATE.md` |
| 20 | `dev/real_case/002/quality_review/README.md` | 132 | `../../FRAMEWORK_CONTEXT.md` → `../../../FRAMEWORK_CONTEXT.md` |
| 21 | `workflows/generation_workflow.md` | 1089, 1091 | `./README.md` → `../README.md`、`./templates/` → `../templates/`（"参考资源"块路径全偏 1 级） |
| 22 | `guides/generation_workflow.md` | 594, 596 | 同上（重复块） |

> 注：序号 21、22 各含 2 处更改。

---

## 待用户拍板的不确定项

### P1：目标文件不存在（核心阻断）

#### U1. `agents/development/product_manager.md:129` — `product_manager_examples.md` 缺失

- **原文**：`**详细示例**: [\`product_manager_examples.md\`](../examples/product_manager_examples.md)`
- **目标解析**：`agents/examples/product_manager_examples.md` —— 不存在
- **同类对照**：`agents/development/` 下其他角色文档（api_designer、architecture_analyst、database_designer）的 `_examples.md` 文件**都存在**于 `agents/examples/` 内，唯独 product_manager 缺失。`agents/runtime/` 的 5 个角色 + `agents/examples/design_thinking/user_login_flow.md` 也都齐全。
- **可能影响**：用户阅读 product_manager 角色卡时，"详细示例"链接 404；其他角色卡有示例，造成体验不一致。
- **修复方案**（请选一）：
  - **A**：补全文件 `agents/examples/product_manager_examples.md`（推荐，与同类一致）
  - **B**：删除 product_manager.md:129 这一行链接
  - **C**：将链接改为指向已有的 `design_thinking/user_login_flow.md`（PM 相关示例）

#### U2. `agents/_progress/implementation_progress.md:5` — 编号与目录名严重错位

- **原文**：
  - 第 3 行：`**项目**: 013 - AI 角色库实施`
  - 第 5 行：`**实施方案**: [013-ai-agent-library-implementation.md](../../../dev/V3.0/confirmed/013-ai-agent-library-implementation.md)`
- **目标解析**：`dev/V3.0/confirmed/013-ai-agent-library-implementation.md` —— 不存在
- **现状对比**：
  - 实际"AI 角色库"项目目录是 `dev/V3.0/confirmed/001-ai-agent-library/`，含 `001-ai-agent-library.md`、`implementation.md`、`progress.md`
  - 编号 013 实际对应 `dev/V3.0/confirmed/013-ai-mutual-review/`（AI 互审，不是角色库）
- **可能影响**：进度文档与规划文档完全脱钩；同时折射出更深的命名冲突（项目 ID 在不同位置不一致）。
- **修复方案**（请选一）：
  - **A**：将 progress 文件改写指向 `001-ai-agent-library/`：第 3 行改为 `**项目**: 001 - AI 角色库`，第 5 行链接改为 `../../../dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md`，并考虑链接到 `implementation.md` / `progress.md`
  - **B**：把整份 `agents/_progress/implementation_progress.md` 移除（如果 `001-ai-agent-library/progress.md` 已经覆盖该职能，本文档冗余）
  - **C**：保留并仅修字面错（最低成本，但留下编号不一致的债）

#### U3. `dev/FRAMEWORK_CONTEXT.md:744-745` — `reference/{design_decisions,SUMMARY_FORMAT_SPEC}.md` 找不到

- **原文**：
  ```
  - [reference/design_decisions.md](../reference/design_decisions.md) - 框架设计决策说明
  - [reference/SUMMARY_FORMAT_SPEC.md](../reference/SUMMARY_FORMAT_SPEC.md) - 文档摘要格式规范
  ```
- **目标解析**：从 `dev/FRAMEWORK_CONTEXT.md` 出发，`../reference/` 指向 repo 根 `reference/`，该目录不存在；`dev/reference/` 也无这两个文件。
- **强候选**：`core/design_decisions.md` 与 `core/SUMMARY_FORMAT_SPEC.md` **都存在**且文件名完全匹配。极可能是文档曾经规划放在 `reference/`（或 `dev/reference/`），实际落到 `core/` 后忘记同步引用。
- **可能影响**：FRAMEWORK_CONTEXT 是 dev 区入口文档，"参考文档"段落两个核心链接死链，影响新人上手。
- **修复方案**（请选一）：
  - **A**（推荐）：链接文本与 href 同步改为 `core/`：`[core/design_decisions.md](../core/design_decisions.md)`、`[core/SUMMARY_FORMAT_SPEC.md](../core/SUMMARY_FORMAT_SPEC.md)`
  - **B**：在 `dev/reference/` 下新建两个同名占位文件，内部 redirect 到 `core/...`
  - **C**：删除两行（如果这些信息不再属于"参考"列表）

#### U4. `dev/V3.0/confirmed/014-doc-reading-habit-guide/014-doc-reading-habit-guide.md:476` — 同 U3

- **原文**：`- [design_decisions.md](../../reference/design_decisions.md) - 已补充相关设计理念`
- **目标解析**：`dev/V3.0/reference/design_decisions.md` 不存在；`dev/reference/design_decisions.md` 也不存在。
- **强候选**：同 U3，应是 `core/design_decisions.md`，正确路径 `../../../../core/design_decisions.md`。
- **可能影响**：014 是 V3.0 已确认计划，相关引用断裂。
- **修复方案**：与 U3 联动决策；推荐 **A**（改为 `core/`）。

#### U5. `workflows/generation_workflow.md:1090` + `guides/generation_workflow.md:595` — `STRUCTURE_SPEC.md` 全仓不存在

- **原文（两文件）**：`- [结构规范](./STRUCTURE_SPEC.md)`
- **目标解析**：`workflows/STRUCTURE_SPEC.md` 与 `guides/STRUCTURE_SPEC.md` 都不存在；全仓 grep 没有 `STRUCTURE_SPEC.md` 同名文件。
- **可能影响**：两份"参考资源"列表都包含一个不存在的"结构规范"链接。考虑到所在块的另两条已被批准修复为指向 repo 根的 `README.md` 与 `templates/`，本条形态相同但目标确实空白。
- **可能候选**（推测）：`core/framework_spec.md`（"框架规范"）或 `core/project_types.md`（项目类型/结构规范），但语义都不完全匹配"结构规范"。
- **修复方案**（请选一）：
  - **A**：删除两行
  - **B**：替换为 `[框架规范](../core/framework_spec.md)` 或 `[项目类型](../core/project_types.md)`
  - **C**：新建 `STRUCTURE_SPEC.md`（位置与内容待定）

#### U6. `guides/project_types.md:275` — `api_reference.md` 全仓不存在

- **原文**：`详见 [API Reference](./api_reference.md)`
- **目标解析**：`guides/api_reference.md` 不存在；全仓也无 `api_reference.md` 同名文件（仅在 `core/project_types/library_sdk.md` 与本身有作为"建议生成的文件名"出现）。
- **上下文**：本条出现在"library_sdk"章节末尾，明显是引导用户跳到详细 API 参考。
- **可能影响**：library_sdk 章节末尾断链。
- **修复方案**（请选一）：
  - **A**：删除该行
  - **B**：将链接改为 `core/project_types/library_sdk.md` 自身（但语义有点重复）
  - **C**：明示这是"待用户项目自行生成"的文档，加上备注说明

#### U7. `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md:270` — `_templates/agent_template.md`

- **原文**：`参考 [\_templates/agent_template.md](./_templates/agent_template.md)`（"贡献新角色"小节）
- **目标解析**：`dev/V3.0/confirmed/001-ai-agent-library/_templates/agent_template.md` —— 不存在。
- **强候选**：`agents/_templates/agent_template.md` 存在（全仓唯一同名文件），路径应为 `../../../../agents/_templates/agent_template.md`。
- **可能影响**：贡献新角色的指引找不到模板。
- **修复方案**（请选一）：
  - **A**（推荐）：改为 `../../../../agents/_templates/agent_template.md`
  - **B**：在该计划目录内新建 `_templates/` 子目录并放置模板（更贴近"自包含计划"的理念，但与现有结构不一致）
  - **C**：删除该提示

---

### P2：历史/快照文档中的失效引用（修不修都有道理）

#### U8. `dev/V2.3/*` 中对 `workflows/`、`core/` 的失效引用（多处）

- **涉及文件**：
  - `dev/V2.3/入口文档优化_review.md:455`
  - `dev/V2.3/智能工作流_plan.md:513,549,591,786,1098,2202`
- **典型原文**：`[文档](./workflows/monorepo_workflow.md)`、`[文档](./core/update_triggers.md)` 等
- **目标解析**：从 `dev/V2.3/` 出发，`./workflows/...` 指向 `dev/V2.3/workflows/...`，不存在。这些工作流/触发器文件**今天确实存在**于 repo 根的 `workflows/` 和 `core/` 下，正确路径应为 `../../workflows/...` 与 `../../core/...`。
- **特殊考虑**：V2.3 是**历史规划文档**（"v2.3 整体优化方案"），内容定格在那个时间点。修改其引用相当于"事后改写历史"。
- **可能影响**：
  - 现状：链接指向不存在的位置
  - 不修：阅读时跳转失败，但保留历史原貌
  - 修：链接生效，但历史文档被修改
- **修复方案**（请选一）：
  - **A**：把所有 `./workflows/`、`./core/` 类引用统一修正为 `../../workflows/`、`../../core/`（约 7 处批量替换）
  - **B**：保留原状，在 `dev/V2.3/README.md`（如有则新建）顶部加一条"本目录为历史规划，引用路径未跟随后续重构更新"的说明
  - **C**：在每个失效链接后加 `<!-- TODO: V2.3 历史路径 -->` 注释提醒

#### U9. `dev/V3.0/archived/015-quality-assurance-system.md:317-319` — archived 内的失效引用

- **原文**：
  ```
  - [document_health_check](../../workflows/document_health_check.md)
  - [011-doc-error-fix-workflow.md](./011-doc-error-fix-workflow.md)
  - [012-mandatory-doc-summary.md](./012-mandatory-doc-summary.md)
  ```
- **目标解析**：路径深度错（同 U8 类问题）；后两条同目录引用对应实际 `../confirmed/{011,012}-.../`。
- **特殊考虑**：本文件位于 `archived/`，定位为"已归档/未采纳的方案"，断链可能是有意保留的"历史快照"。
- **修复方案**（请选一）：
  - **A**：保留原状（archived 即是历史，断链合理）
  - **B**：与 U8 一并批量修正

#### U10. `dev/real_case/002/AI_Coding_Context.md` — 整文件大量"对外项目"引用

- **现象**：本文件是为 **Claude Code（Anthropic 项目）** 生成的 AI 编码上下文示例（标题"Claude Code AI 编码上下文"），其中所有 `architecture.md`、`api_reference.md`、`development_guide.md`、`testing_guide.md`、`deployment_guide.md`、`project_overview.md`、`project_analysis.md`、`tools/cli_reference.md`、`architecture/framework_overview.md`、`architecture/plugin_development_guide.md`、`ai_coding_context/agents/README.md`、`ai_coding_context/agents/examples/...`、`./plans/README.md` 等链接都指向那个项目假设的目录结构（`dev_docs/...`、`ai_coding_context/...`），并不指向我们的仓库。
- **统计**：约 17+ 处引用，集中在第 56-91、121-202、342-343 行。
- **可能影响**：
  - 本质：作为案例样本，引用本应在那个项目的语境内才有效；放在我们仓库里链接全断
  - 用户体验：在 GitHub/IDE 中浏览该 case study 时，链接全 404
- **修复方案**（请选一）：
  - **A**（推荐）：保留原文，但在文件顶部 frontmatter 下方加一段醒目说明，例如 `> ⚠️ 本文件为生成示例样本，所有链接是面向 Claude Code 项目假设结构的，在本仓库中无法跳转。`
  - **B**：将所有 markdown 链接降级为 inline code（去掉 `[](...)` 包装），让它们不再是可点击的死链
  - **C**：对每个链接添加 `<!-- 案例样本：链接面向 Claude Code 项目，非本仓库路径 -->` 注释
  - **D**：保持现状（接受死链是 case study 的固有特征）

---

### P3：模板/示例性引用（设计上就不指向真实文件）

> 这一类引用出现在模板文件、规范示例、Mock 输出中，**本质就是占位符或示意**，不是真实失效。一般无需修改，但若需要"零死链"洁癖可考虑标注。

#### U11. `core/framework_spec.md:196-208` — 规范示例

- 4 处形如 `[2025-11-27_新增导出功能](./features/2025-11-27_export-feature.md)` 的示例引用，演示 plan 文档的命名/路径规范。
- **建议**：保留，可在该段开头加一行 `> 以下为示例文件名，无需真实存在`。

#### U12. `templates/AI_Coding_Context_TEMPLATE.md:110, 192, 215, 231, 258` — 模板内占位

- 5 处指向 `./tools/README.md`、`./plans/README.md`、`./agents/README.md`、`./knowledge/README.md` 的链接。
- 模板文件被复制到目标项目的 `dev_docs/` 下后，这些相对路径才能正确指向用户项目内的对应位置。
- **建议**：保留，但可在模板顶部说明"路径是相对于生成位置（通常是 `dev_docs/AI_Coding_Context.md`）"。

#### U13. `templates/{generation_plan_complex,generation_plan_critical,generation_plan_trivial,GENERATION_PLAN_TEMPLATE}.md:143` 与 `dev/real_case/001/generation_plan.md:140`、`dev/reference/生产级Vue3文档体系方案.md:104` — 引用规则示例

- 形如 `[文档名](./other_doc.md)` 的指导性示例，告诉用户"如何写跨文档引用"。
- **建议**：保留（已在 inline code 中，并不会被读者点击）。

#### U14. `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md:495-496`、`templates/plans_README_TEMPLATE.md:129` — 模板示例

- 类似 U11，模板内列出"可能的产物文件名"。
- **建议**：保留。

#### U15. `agents/_templates/agent_template.md:114, 128, 132, 136` — 模板占位符

- `[角色名]_examples.md`、`xxx.md` 等明显的占位符。
- **建议**：保留。

#### U16. `agents/workflows/understanding_guardian.md:117, 138, 164, 185` — Agent 提示词内的"示例输出"

- 4 处 `dev_docs/api_layer.md`、`dev_docs/architecture.md`、`dev_docs/state_management.md`、`dev_docs/security.md#密码处理` 等链接，出现在 agent 的"标准回复样板"中，演示当 agent 发现问题时怎样引用项目文档。
- **特殊考虑**：这些不是文档间引用，而是 prompt 中的示例输出，属于 agent 的输出格式样本。
- **建议**：保留。

#### U17. `workflows/path_b_health_check.md:339, 343` — Mock 健康检查输出示例

- `[数据库设计](./database_design.md)`、`[样式指南](./styling_guide.md)` 出现在演示"健康检查输出格式"的代码块附近，是 mock 数据。
- **建议**：保留。

#### U18. `workflows/monorepo_workflow.md:230, 237, 244, 279, 280, 281` — Monorepo 用法示例

- 6 处 `../packages/{web-app,api-server,worker}/dev_docs/AI_Coding_Context.md`，演示 monorepo 项目的目录结构。
- **建议**：保留。

#### U19. `dev/V3.0/confirmed/001-ai-agent-library/implementation.md:440, 676` 等 — `角色名_examples.md` 占位

- 模板/示例性引用。
- **建议**：保留。

#### U20. `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md:230-248` — 结构定义示例

- 一组 `./runtime/*`、`./development/*`、`./language_specific/*` 引用，描述"AI 角色库应有的目录结构"，是规范定义而非实际链接。
- **建议**：保留。

---

## 出范围说明

以下情形未纳入审查：
- **外部 URL**（http/https/mailto） —— 用户明确不要求验证
- **`.py` / `.js` 等代码文件**的引用（如 `dev/V3.0/confirmed/012-mandatory-doc-summary/012-mandatory-doc-summary.md:751` 引用 `git_diff_analyzer.py`）
- **`dev/reference/ai-coding-prompt-java-main/` 内部互引** —— 是 vendored sub-project，不是本项目维护范围
- **代码块（fenced code）内的"看起来像引用"的字符串** —— 多为示例代码或 prompt 模板

---

## 决策模板

请逐条对 U1–U7（P1，必须决策）、U8–U10（P2，建议决策）做出选择。U11–U20（P3）若无意见可整体保留。

格式建议：
```
U1: 选 A（补全文件）
U2: 选 B（删除冗余）
U3: 选 A（改 core/）
U4: 选 A（同 U3）
U5: 选 A（删除）
U6: 选 A（删除）
U7: 选 A（改路径）
U8: 选 B（保留 + 加说明）
U9: 选 A（保留）
U10: 选 A（加顶部说明）
P3 全部保留
```

收到决策后我会执行第二批修复并补充 audit doc 的"二次修复记录"段。
