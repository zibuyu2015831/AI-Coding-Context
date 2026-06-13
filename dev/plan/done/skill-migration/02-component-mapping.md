---
title: AICC 组件 → Skill Plugin 映射表
summary: 将 AICC 现有的 workflows / agents / tools / templates / core / config / guides 等 7 大组件，逐一映射到目标 plugin 的 skills / agents / scripts / references 等位置；记录每个 skill 的职责、触发 description 草稿、依赖、规模估算与命名理由。
keywords: aicc | skill-mapping | component-migration | plugin-architecture
scope: dev/plan/done/skill-migration 子项目（组件映射阶段）
related_files: 01-feasibility-and-architecture.md | 03-implementation-roadmap.md | README.md
dependencies: 01-feasibility-and-architecture.md
verified_at: 2026-04-26
---

# 02 — 组件映射表

## 复检修订说明（2026-05-12）

本文件初版基于 brainstorm 阶段的组件心智模型编写。2026-05-12 复检时已对真实仓库目录抽样核对，发现 development agents、runtime agents、templates/prompts、review_standards 等映射与真实资产存在偏差。因此本文件在实施前必须先完成一次**真实资产清单驱动的再同步**：

1. 以 `find workflows agents tools core templates config guides -type f` 的真实输出生成 `plugin-manifest.generated.json` 草案。
2. 每个 skill 的 references/scripts/templates/agents 只能引用清单中存在的文件。
3. 原计划中的 `frontend_expert`、`backend_expert`、`devops_expert`、`architect`、`document_generator`、`auto_reviewer`、`test_generator`、`optimizer` 等名称不得直接作为实施依据，除非后续确认为新建资产。
4. Claude Code plugin 内 skill 目录使用短名（如 `skills/init/`），由 plugin namespace 形成 `/aicc:init`；面向无 namespace 平台的 `init` flat 包由构建产物生成。

## 一、映射总览

| AICC 现有组件（来自 `dev/FRAMEWORK_CONTEXT.md` §3.1） | 目标位置（plugin 内） | 映射比 | 主要约束 |
|---|---|---|---|
| `workflows/path_a-d_*.md` + `commit_guided_update.md` + `git_safety_workflow.md` + `complexity_alert_workflow.md` + `doc_error_fix_workflow.md` | `skills/<short-name>/SKILL.md` + `references/` | 多对多 | 500 行上限，需拆 step references |
| `workflows/document_health_check.md`、`maintenance_workflow.md`、`review_standards/*.md` | 分别进入 `health-check`、`incremental-update`、`mutual-review` references | 新增补漏 | 真实目录存在，初版未充分覆盖 |
| `agents/runtime/*.md` | `skills/<short-name>/references/agents/*.md`（嵌入对应 skill） | 1:1 嵌入 | 与 workflow 强耦合；以真实文件名为准 |
| `agents/development/*.md` | `agents/*.md`（plugin 顶级） | 选择性升格 | 只迁移真实存在且用户开发期高频的 subagent |
| `agents/language_specific/*.md`、`agents/workflows/*.md`、`agents/personas/*.md` | `skills/<short-name>/references/agents/*.md` 或 `references/agents/` | 1:1 嵌入/共享 | 使用频度低，避免污染 subagent 列表 |
| `tools/py/*.py`（**34 个**）、`tools/js/*.js`（**34 个 + 3 测试**） | `scripts/py/*.py`、`scripts/js/*.js` + `bin/aicc-*` 包装命令 | 1:1 平移 + 包装 | skill 正文优先调用 `bin/` 命令，降低路径依赖 |
| `tools/fallback/*.md` | `scripts/fallback/*.md` | 1:1 平移 | 罕用，但保留 |
| `tools/git-hooks/`（commit-guided 用 git hook 脚本） | `plugin/hooks/git-hooks/` 或 `scripts/hooks/` | 1:1 平移 | incremental-update / commit-guided 引用 |
| `tools/audit_complete_verification.sh`、`CHANGELOG.md`、`ROADMAP.md`、`README.md`、`__pycache__/`、测试缓存 | 仍留框架仓库 `tools/` 顶层 | 0:0（不进 plugin） | 元信息、开发产物、缓存不应进入 release artifact |
| 🆕（plugin 新增） | `plugin/tests/<skill>/eval-N.json` | 新增 | evaluation-driven development 体系（writing-skills 推荐） |
| `templates/*.md`、`templates/prompts/*`、`templates/review/*`、`templates/rules/*` | `skills/<short-name>/references/templates/*.md` 或 `references/templates/` | 1:N 拆分 | 初版漏掉 prompts/review/rules 子目录，需补齐 |
| `core/language_rules.md`、`security_rules.md`、`SUMMARY_FORMAT_SPEC.md`、`project_types/*.md` | `references/*.md`（plugin 顶级共享） | build-time copy | 避免每个 skill 重复；不用 symlink 作为发布机制 |
| `core/framework_spec.md`、`design_decisions.md` | 部分内化为 `plugin/CLAUDE.md`，部分留 `dev/` | 拆分 | 偏框架自身设计，剥离用户面 |
| `config/user_config.md`、`CONFIG_TEMPLATE.md` | 不再在 plugin 中维护；用户偏好走 Claude Code settings 或用户项目 `dev_docs/configuration.md` | 弃用框架级 config | 模式根本变化 |
| `guides/*.md` | 拆分：人类文档进 `plugin/README.md`；AI 决策内容内化到 skill body | 重组 | 不再独立成 guides/ 目录 |

---

## 二、workflows/ → skills 映射

### 2.1 总映射表

| 当前 AICC 文件 | 目标 skill | 复用关系 |
|---|---|---|
| `workflows/path_a_first_generation.md`（≈650 行） | `skills/init/` | 拆为 SKILL.md（~250 行）+ 8 个 step references |
| `workflows/path_b_health_check.md`（≈400 行）<br>`workflows/document_health_check.md` | `skills/health-check/` | SKILL.md（~250 行）+ 3 个 mode references |
| `workflows/path_c_incremental_update.md`（≈350 行）<br>`workflows/commit_guided_update.md`（≈480 行）<br>`workflows/git_safety_workflow.md`（≈520 行）<br>`workflows/maintenance_workflow.md` | `skills/incremental-update/` | 三者合并，SKILL.md（~300 行）+ commit_analysis、git_safety 等 references |
| `workflows/path_d_specific_tasks.md`（≈300 行） | **拆分到多个 skill** | 不独立成 skill；散到下面 |
| `workflows/path_d` 中的 `@think` | `skills/design-thinking/` | 取自 path_d，独立 |
| `workflows/path_d` 中的 `@review` | `skills/mutual-review/` | 取自 path_d，独立 |
| `workflows/complexity_alert_workflow.md` | `skills/complexity-dashboard/` | 独立 skill |
| `workflows/doc_error_fix_workflow.md` | `skills/doc-fallacy-fix/` | 独立 skill |
| `workflows/review-workflow.md`、`workflows/review_standards/*.md` | 整合进 `skills/mutual-review/` | 复审流程与分类型标准一起迁移 |
| `workflows/detection_workflow.md`、`decision_workflow.md`、`generation_workflow.md` | `skills/init/references/` | 已被 path_a 引用，作为 init 的 details |
| `workflows/monorepo_workflow.md` | `skills/init/references/special_scenarios/monorepo.md` | 作为 init 的特殊场景 |
| `workflows/create_custom_tool_workflow.md` | `plugin/CLAUDE.md` 或独立 dev 文档 | 偏框架开发，不直接面向用户 |
| `workflows/progress_tracking.md` | `skills/init/references/progress_tracking.md` | init 内部 |
| `workflows/shared/failure_handling.md`、`special_scenarios.md`、`ai_checklist.md` | `references/workflows/` | 跨 skill 共享 |

### 2.2 各 skill 详细规格

#### 2.2.1 `init`（Claude Code 显式调用：`/aicc:init`；flat 包名：`aicc-init`）

**职责**：在 dev_docs/ 不存在的项目里，从零生成完整 AI 辅助编程文档体系。

**触发 description（草稿）**：
> Use when a project lacks any AI coding documentation (no `dev_docs/AI_Coding_Context.md` exists) and the user wants to set up AI assistance, generate project docs, initialize codebase docs, or "make this project AI-friendly". NOT for projects that already have `dev_docs/`.

**触发关键词识别（应触发）**：
- "set up AI docs for this project"
- "generate AI coding context"
- "initialize AICC"
- "为这个项目生成 AI 辅助文档"

**触发关键词识别（不应触发）**：
- "update my docs"（应触发 incremental-update）
- "review my plan"（应触发 mutual-review）

**SKILL.md 主体结构**：
```
1. Overview（2 段）
2. When to Use / Not to Use
3. Required Tools（Python / Git）
4. Workflow Overview（8 步导航表，链到 step references）
5. Critical Decision Gates（人工审核节点）
6. Common Pitfalls（已知陷阱）
7. Related Skills
```

**references/ 目录**（≈ 14 个文件）：
```
references/
├── step_1_env_diagnosis.md           ← 来自 detection_workflow.md
├── step_2_project_scan.md
├── step_3_scale_decision.md          ← 来自 decision_workflow.md
├── step_4_subdoc_selection.md
├── step_5_design_thinking_handoff.md ← 委托给 design-thinking
├── step_6_plan_generation.md         ← 来自 generation_workflow.md
├── step_7_mutual_review_handoff.md   ← 委托给 mutual-review
├── step_8_doc_generation_loop.md
├── progress_tracking.md
├── special_scenarios/
│   ├── monorepo.md
│   ├── multi_language.md
│   └── existing_partial_docs.md
├── templates/
│   ├── AI_Coding_Context_TEMPLATE.md
│   ├── AI_RULES_TEMPLATE.md
│   ├── PROJECT_ANALYSIS_REPORT_TEMPLATE.md
│   ├── PROGRESS_TEMPLATE.md
│   ├── GENERATION_PLAN_TEMPLATE.md
│   ├── plans_README_TEMPLATE.md
│   ├── knowledge_README_TEMPLATE.md
│   └── PLAN_TEMPLATE.md
└── agents/
    ├── design_facilitator.md         ← 来自 agents/runtime/
    └── summary_generator.md
```

**依赖**：
- `scripts/py/env_diagnosis.py`、`project_scanner.py`、`summary_extractor.py`
- `references/language_rules.md`、`security_rules.md`、`project_types/*.md`、`summary_format_spec.md`
- 互调用：`design-thinking`（Step 5.5）、`mutual-review`（Step 7）

**估算规模**：SKILL.md ≈ 250 行，references 总量 ≈ 1500 行。

---

#### 2.2.2 `health-check`

**职责**：评估已有 dev_docs/ 体系的健康度，输出健康报告与修复建议。

**触发 description（草稿）**：
> Use when a project already has `dev_docs/AI_Coding_Context.md` and the user wants to assess doc quality, detect drift, run a doc audit, or check whether docs are still in sync with code. Triggers on phrases like "check my docs", "are my docs up to date", "audit AI context". NOT for first-time setup or for syncing after a specific commit.

**SKILL.md 主体结构**：
```
1. Overview
2. When to Use / Not to Use
3. Three Health Check Modes（mode 1/2/3）
4. Required Tools
5. Output Format（健康度评分 + 问题清单）
6. Common Findings（已知典型问题）
7. Handoff Conditions（什么时候应该触发 incremental-update 或 fallacy-fix）
```

**references/ 目录**：
```
references/
├── mode_1_quick_scan.md
├── mode_2_drift_detection.md
├── mode_3_full_audit.md
├── checklists/
│   ├── frontmatter_check.md
│   ├── link_integrity_check.md
│   └── code_example_check.md
└── output_templates/
    └── health_report.md
```

**依赖**：
- `scripts/py/doc_health_checker.py`、`summary_related_checker.py`、`doc_dependency_tracer.py`
- `references/summary_format_spec.md`

**估算规模**：SKILL.md ≈ 220 行，references ≈ 800 行。

---

#### 2.2.3 `incremental-update`

**职责**：围绕 Git 变更提供两类能力：提交前的结构化 commit 生成（commit-authoring / prepare-commit），以及提交后的 commit-guided 文档同步；包含 Git 安全防护。

**触发 description（草稿）**：
> Use when the user asks to create/prepare/review a git commit, generate a structured commit message, mentions @commit, asks to update docs after recent code changes, references specific commits, or wants to sync `dev_docs/` with the latest git state. Covers commit-authoring before commit and commit-guided documentation updates after commit. Includes git safety checks (no force push, branch protection). NOT for first-time setup or full audits.

**SKILL.md 主体结构**：
```
1. Overview
2. When to Use / Not to Use
3. Workflow A: Commit Authoring（状态检查 → diff 概览 → 选择 conventional/prompt 格式 → 生成 WHAT/WHY/HOW → 提交前确认）
4. Workflow B: Commit-Guided Doc Update（commit 分析 → 文档定位 → 安全检查 → 智能局部更新）
5. Git Safety Gates（关键不可逆操作前的人工确认）
6. Output Format
7. Edge Cases（merge commits、cherry-pick、revert、WIP/机械提交）
```

**references/ 目录**：
```
references/
├── workflow_a_commit_authoring.md
├── workflow_b_commit_guided_doc_update.md
├── step_1_commit_deep_analysis.md
├── step_2_doc_localization.md
├── step_3_git_safety_checks.md
├── step_4_smart_partial_update.md
├── structured_commit_format.md   ← prompt(type) + WHAT/WHY/HOW
├── git_safety_rules.md          ← 来自 git_safety_workflow.md
├── edge_cases/
│   ├── wip_and_mechanical_commits.md
│   ├── merge_commits.md
│   ├── cherry_pick.md
│   └── revert.md
└── agents/
    └── commit_analyst.md         ← 来自 agents/runtime/
```

**依赖**：
- `scripts/py/git_diff_analyzer.py`、`git_safety.py`、`manage_fix_with_git.py`
- `scripts/py/commit_template_cli.py`、`commit_quality_scorer.py`、`commit_parser.py`、`commit_integrity_validator.py`
- `references/security_rules.md`

**估算规模**：SKILL.md ≈ 320 行，references ≈ 1500 行。

---

#### 2.2.4 `design-thinking`

**职责**：5 Why 分析、多方案对比、风险评估、最终决策的引导式思维流程。

**触发 description（草稿）**：
> Use when the user wants 5-Why root-cause analysis, multi-option comparison, risk assessment, edge case enumeration, or any structured "think before coding" guidance for a feature/architecture decision. Triggers on @think, "let's design", "compare these options", "what could go wrong". Can also be invoked from inside init at Step 5.5.

**SKILL.md 主体结构**：
```
1. Overview（设计思维的价值：返工率从 50% → 20%）
2. When to Use / Not to Use
3. 5-Step Guided Process
4. Expert Team Mode（引导者 / 产品经理 / 架构师 / QA）
5. Hybrid Trigger（用户指令 + 自动复杂度评估）
6. Output Format（决策表 + 边界定义）
```

**references/ 目录**：
```
references/
├── step_1_5_why.md
├── step_2_multi_option.md
├── step_3_risk_assessment.md
├── step_4_reflection.md
├── step_5_final_decision.md
├── expert_team/
│   ├── facilitator.md
│   ├── product_manager.md
│   ├── architect.md
│   └── qa.md
└── examples/
    ├── architecture_decision_example.md
    └── feature_design_example.md
```

**依赖**：无脚本依赖；可被 `init` 与用户直接 invoke。

**估算规模**：SKILL.md ≈ 200 行，references ≈ 700 行。

---

#### 2.2.5 `mutual-review`

**职责**：分级 AI 互审（Trivial / Simple / Complex / Critical），对抗式编程：生成者 vs 审查者。

**触发 description（草稿）**：
> Use when the user wants AI cross-review of a generated plan, doc, or proposal—particularly for trivial/simple/complex/critical change reviews. Triggers on @review, "review this plan", "double-check before I run this", "have another AI look at this". Can also be invoked from inside init at Step 7.

**SKILL.md 主体结构**：
```
1. Overview（AI 互审的价值：问题发现率 +30-50%）
2. When to Use / Not to Use
3. Severity Classification（4 级判定）
4. Reviewer Persona（与生成者的人格对抗）
5. Standardized Checklist
6. Output Format（review report）
```

**references/ 目录**：
```
references/
├── severity_classification.md
├── reviewer_persona.md
├── checklists/
│   ├── plan_review.md
│   ├── doc_review.md
│   ├── code_review.md
│   └── critical_change_review.md
└── output_templates/
    └── review_report.md
```

**依赖**：无脚本依赖；可独立或被其他 skill invoke。

**估算规模**：SKILL.md ≈ 220 行，references ≈ 600 行。

---

#### 2.2.6 `adr`

**职责**：架构决策记录（ADR）的创建、查询、演进、断言验证。

**触发 description（草稿）**：
> Use when the user wants to create an architecture decision record (ADR), document a significant tech choice, query past architecture decisions, or validate code against existing ADR assertions. Triggers on "create ADR", "what was decided about X", "is this consistent with ADR-N", or @adr.

**SKILL.md 主体结构**：
```
1. Overview（ADR 系统价值：架构演进可追溯）
2. When to Use / Not to Use
3. ADR Lifecycle（Proposed → Accepted → Deprecated → Superseded）
4. Workflow（创建 / 查询 / 验证）
5. Why-Tool 与 AAC-Validator 使用
6. Output Format（ADR 文档结构）
```

**references/ 目录**：
```
references/
├── adr_lifecycle.md
├── adr_template.md             ← 来自 dev/architecture/adr-template.md
├── why_tool_usage.md
├── aac_validator_usage.md
└── examples/
    ├── adr_001_markdown.md
    └── adr_002_layered.md
```

**依赖**：
- `scripts/py/why_tool.py`、`aac_validator.py`

**估算规模**：SKILL.md ≈ 200 行，references ≈ 500 行。

---

#### 2.2.7 `complexity-dashboard`

**职责**：项目复杂度数据采集、报告渲染、阈值告警。

**触发 description（草稿）**：
> Use when the user wants to measure project complexity, generate a complexity report, set up alerts for complexity thresholds, or audit which modules are growing too complex. Triggers on @complexity, "show complexity", "is my code getting too complex".

**SKILL.md 主体结构**：
```
1. Overview
2. When to Use / Not to Use
3. Workflow（扫描 → 报告 → 告警）
4. Threshold Configuration
5. Output Format（HTML/Markdown report）
```

**references/ 目录**：
```
references/
├── scanner_usage.md
├── report_format.md
├── threshold_config.md
└── alert_rules.md
```

**依赖**：
- `scripts/py/complexity_scanner.py`、`report_generator.py`、`notifier.py`
- `scripts/js/complexity_scanner.js`、`report_generator.js`（降级）

**估算规模**：SKILL.md ≈ 180 行，references ≈ 500 行。

---

#### 2.2.8 `doc-fallacy-fix`

**职责**：识别并修复文档谬误、过期信息、依赖断裂。

**触发 description（草稿）**：
> Use when the user reports a documentation error, claims docs are wrong/outdated, or asks to find and fix doc inconsistencies. Triggers on "docs say X but actually Y", "this doc is wrong", "fix the docs about Z", @fix-docs.

**SKILL.md 主体结构**：
```
1. Overview
2. When to Use / Not to Use
3. Workflow（依赖追踪 → 影响面分析 → 批量修复 → 历史记录）
4. Git Branch Strategy（修复用独立分支）
5. Output Format
```

**references/ 目录**：
```
references/
├── dependency_tracing.md
├── impact_analysis.md
├── batch_fix.md
├── history_management.md
└── git_branch_strategy.md
```

**依赖**：
- `scripts/py/doc_dependency_tracer.py`、`semantic_related_detector.py`、`batch_fix_manager.py`、`fix_history_manager.py`、`manage_fix_with_git.py`

**估算规模**：SKILL.md ≈ 220 行，references ≈ 700 行。

---

#### 2.2.9 `systematic-review`

**职责**：多轮系统化文档审核（V3.0+ 019）：执行规程、原则、轮次归档。

**触发 description（草稿）**：
> Use when the user wants a comprehensive multi-round documentation audit, set up a recurring review cycle, or apply the AICC V3.0 systematic review framework (rounds-based with progress tracking). Triggers on "do a full doc audit", "set up systematic review", "let's do round N review", @sys-review.

**SKILL.md 主体结构**：
```
1. Overview（系统化审核 vs 一次性 health-check 的区别）
2. When to Use / Not to Use
3. Review Plan & Principles
4. Round Lifecycle（Plan → Execute → Archive → Next Round）
5. Output Format
```

**references/ 目录**：
```
references/
├── review_plan_template.md       ← 来自 dev/case_skillatlas_review/sys_review_plan.md
├── review_principles.md          ← 来自 sys_review_principles.md
├── round_lifecycle.md
├── progress_index_template.md
└── examples/
    └── case_skillatlas_overview.md
```

**依赖**：无脚本依赖；纯方法论 skill。

**估算规模**：SKILL.md ≈ 220 行，references ≈ 600 行。

---

#### 2.2.10 `doc-reading-habit`

**职责**：引导用户养成文档阅读习惯（V3.0 014），降低 AI 与人之间的理解偏差。

**触发 description（草稿）**：
> Use when the user is about to make decisions or write code without first reading relevant docs, or when the AI detects misalignment between user's stated understanding and existing documentation. Triggers proactively when user asks "how does X work" before any doc context is loaded.

**SKILL.md 主体结构**：
```
1. Overview（理解偏差检测的价值）
2. When to Use（含主动触发条件）
3. Detection Heuristics
4. Recommendation Workflow（智能文档推荐）
5. Output Format
```

**references/ 目录**：
```
references/
├── detection_heuristics.md
├── recommendation_workflow.md
└── agents/
    ├── document_recommender.md       ← 来自 agents/runtime/
    └── understanding_guardian.md     ← 来自 agents/runtime/
```

**依赖**：
- `scripts/py/summary_related_checker.py`、`summary_index_generator.py`

**估算规模**：SKILL.md ≈ 200 行，references ≈ 400 行。

---

#### 2.2.11 `knowledge-reuse`

**职责**：跨项目共享知识库（V3.0 010，进行中）。

**触发 description（草稿）**：
> Use when the user wants to share patterns/lessons across projects, install a shared knowledge base, query past troubleshooting/patterns/performance notes from other projects. Triggers on "use shared knowledge", "import patterns from X", @knowledge.

**SKILL.md 主体结构**：
```
1. Overview
2. When to Use / Not to Use
3. Knowledge Base Configuration
4. Reference Resolution
5. Output Format
```

**references/ 目录**：
```
references/
├── kb_config.md
├── reference_resolution.md
└── examples/
    └── multi_project_setup.md
```

**依赖**：
- `scripts/py/knowledge_cli.py`、`knowledge_matcher.py`

**估算规模**：SKILL.md ≈ 180 行，references ≈ 400 行。

> ⚠️ 010 在 V3.0 PROGRESS 中状态为"进行中（🟢）"，对应 skill 应等 010 落地后再启动；先在 plugin 中预留命名空间。

---

### 2.3 最终 skill 清单

Claude Code plugin 内 11 个短名 skill；面向 flat 平台的构建产物再加 `aicc-` 前缀：

```
skills/
├── init                  ← 首次生成（Phase 1）
├── health-check          ← 健康检查（Phase 1）
├── incremental-update    ← 增量更新 + commit-guided + git-safety（Phase 1.5）
├── design-thinking       ← 设计思维（Phase 2）
├── mutual-review         ← AI 互审（Phase 2）
├── adr                   ← ADR 系统（Phase 2）
├── complexity-dashboard  ← 复杂度仪表盘（Phase 3）
├── doc-fallacy-fix       ← 文档谬误修复（Phase 3）
├── systematic-review     ← 系统化文档审核（Phase 3）
├── doc-reading-habit     ← 文档阅读习惯（Phase 3）
└── knowledge-reuse       ← 跨项目知识复用（Phase 3 / 等 010 落地）
```

---

## 三、agents/ → 双层映射

### 3.1 runtime → embedded references

| AICC 文件 | 嵌入到的 skill | 位置 |
|---|---|---|
| `agents/runtime/commit_analyst.md` | `incremental-update` | `references/agents/commit_analyst.md` |
| `agents/runtime/design_facilitator.md` | `init`、`design-thinking` | 各放一份引用或上提到 `references/agents/` |
| `agents/runtime/summary_generator.md` | `init`、`incremental-update` | 同上，候选共享 reference |
| `agents/runtime/document_recommender.md` | `doc-reading-habit` | `references/agents/` |
| `agents/runtime/understanding_guardian.md` | `doc-reading-habit` | `references/agents/` |
| `agents/runtime/plan_reviewer.md` | `mutual-review` | `references/agents/` |
| `agents/runtime/code_reviewer.md` | `mutual-review` | `references/agents/` |
| `agents/runtime/security_auditor.md` | `mutual-review` 或 `systematic-review` | 待真实用途确认 |
| `agents/runtime/test_engineer.md` | `mutual-review` 或 `init` | 待真实用途确认 |
| `agents/runtime/performance_optimizer.md` | `complexity-dashboard` | 待真实用途确认 |

> ⚠️ 待确认条目记入 `05-open-questions.md` Q11。

### 3.2 development → plugin agents/

| AICC 文件 | 升格为 plugin subagent | 文件名 |
|---|---|---|
| `agents/development/api_designer.md` | `api-designer` | `agents/api-designer.md` |
| `agents/development/architecture_analyst.md` | `architecture-analyst` | `agents/architecture-analyst.md` |
| `agents/development/database_designer.md` | `database-designer` | `agents/database-designer.md` |
| `agents/development/product_manager.md` | `product-manager` | `agents/product-manager.md` |

格式要求（Claude Code subagent 标准）：
```yaml
---
name: api-designer
description: <Use when ...>
---
<expert prompt body>
```

> 说明：初版计划中的 frontend/backend/devops/security/test 等 development agents 不在当前真实 `agents/development/` 目录中。若后续确需这些角色，应先作为新资产立项，再进入 plugin 映射。

### 3.3 language_specific 与 workflows agents

| AICC 文件 | 处理方式 |
|---|---|
| `agents/language_specific/*.md` | 嵌入对应 skill 的 `references/agents/`（多数情况是 `init` 在分析特定语言时使用） |
| `agents/workflows/*.md` | 嵌入对应工作流 skill 的 `references/agents/` |

---

## 四、tools/ → plugin scripts/

### 4.1 完整脚本清单（来自实际 `tools/py/` 与 `tools/js/` 目录，**34 个 Python 脚本** / 34 个 JS 镜像 + 3 个测试）

> 注：AI_ENTRY_POINT.md §术语表只列出"用户可见"的核心脚本（约 20 个）；实际 tools/ 目录下还有 commit-guided / 通用文件 / 知识库管理等支持脚本。下表为完整清单，来自 `ls tools/py/` 实际枚举。

#### 4.1.1 用户可见的核心脚本（在 AI_ENTRY_POINT.md 术语表已登记）

| 脚本 | 用途 | 调用的 skill |
|---|---|---|
| `env_diagnosis.py/.js` | 环境诊断 | init, health-check |
| `project_scanner.py/.js` | 项目扫描 | init |
| `git_diff_analyzer.py/.js` | Git 变更分析 | incremental-update |
| `git_safety.py/.js` | Git 安全检查 | incremental-update |
| `summary_extractor.py/.js` | 摘要提取 | init, health-check |
| `summary_related_checker.py/.js` | 摘要关联检查 | health-check, doc-reading-habit |
| `summary_index_generator.py/.js` | 摘要索引生成 | init, doc-reading-habit |
| `why_tool.py/.js` | ADR 检索 | adr |
| `aac_validator.py/.js` | ADR 断言验证 | adr |
| `knowledge_cli.py/.js` | 知识库管理 | knowledge-reuse |
| `knowledge_matcher.py/.js` | 知识匹配解析 | knowledge-reuse |
| `doc_dependency_tracer.py/.js` | 文档依赖追踪 | health-check, doc-fallacy-fix |
| `manage_fix_with_git.py/.js` | Git 修复管理 | doc-fallacy-fix |
| `fix_history_manager.py/.js` | 修复历史管理 | doc-fallacy-fix |
| `semantic_related_detector.py/.js` | 语义关联检测 | doc-fallacy-fix, doc-reading-habit |
| `batch_fix_manager.py/.js` | 批量修复管理 | doc-fallacy-fix |
| `complexity_scanner.py/.js` | 复杂度扫描 | complexity-dashboard |
| `report_generator.py/.js` | 复杂度报告 | complexity-dashboard |
| `notifier.py/.js` | 复杂度通知 | complexity-dashboard |
| `doc_health_checker.py/.js` | 文档健康检查 | health-check |

#### 4.1.2 commit-guided 系列脚本（V3.0 018，被 incremental-update 整体引用）

| 脚本 | 用途 | 调用的 skill |
|---|---|---|
| `commit_aggregator.py/.js` | Commit 聚合 | incremental-update |
| `commit_integrity_validator.py/.js` | Commit 完整性校验 | incremental-update |
| `commit_parser.py/.js` | 结构化 Commit 解析 | incremental-update |
| `commit_quality_scorer.py/.js` | Commit 质量评分 | incremental-update |
| `commit_template_cli.py/.js` | Commit 模板 CLI；支持提交前生成结构化 message | incremental-update |
| `git_inspector.py/.js` | Git 状态检查 | incremental-update |
| `install_hooks.py/.js` | git-hooks 安装辅助 | plugin 顶级（hooks/） |

#### 4.1.3 通用文件 / 内容操作脚本（多 skill 共享）

| 脚本 | 用途 | 调用的 skill |
|---|---|---|
| `file_finder.py/.js` | 文件查找 | init, health-check, doc-fallacy-fix |
| `file_reader.py/.js` | 文件读取（带 frontmatter 感知） | init, health-check, doc-reading-habit |
| `content_searcher.py/.js` | 全文搜索 | init, health-check, doc-fallacy-fix |
| `summary_validator.py/.js` | 摘要格式校验 | init, health-check |
| `timestamp_analyzer.py/.js` | 时间戳分析（verified_at 等） | health-check, systematic-review |

#### 4.1.4 文档修复执行 / 知识库管理（专项 skill 用）

| 脚本 | 用途 | 调用的 skill |
|---|---|---|
| `doc_fix_executor.py/.js` | 文档修复执行器 | doc-fallacy-fix |
| `knowledge_repo_manager.py/.js` | 知识库仓库管理 | knowledge-reuse |

#### 4.1.5 测试用例（仅 JS 端）

| 测试文件 | 验证目标 |
|---|---|
| `commit_template_cli.test.js` | commit_template_cli 功能 |
| `install_hooks.test.js` | install_hooks 功能 |
| `integration.test.js` | 跨脚本集成 |

### 4.2 plugin 内调用约定

每个 skill 的 SKILL.md 优先调用 `bin/` 包装命令，包装命令再负责选择 Python / Node / fallback。只有在 `bin/` 机制实测不可用时，才回退到直接调用 `scripts/py/*.py`。

```markdown
## Required Tools

This skill requires Python 3.8+ available as `python` or `python3`.
Falls back to Node.js if Python unavailable.

Run via:
\`\`\`bash
aicc-project-scan --target . --output report.json
\`\`\`

If plugin `bin/` is unavailable after Phase 0a verification, use the direct script fallback:
\`\`\`bash
python "${AICC_PLUGIN_ROOT}/scripts/py/project_scanner.py" --target . --output report.json
\`\`\`
```

> ⚠️ Claude Code 是否提供稳定 plugin root 环境变量仍需验证；但主方案不再依赖 `${CLAUDE_PLUGIN_ROOT}`。详见 `05-open-questions.md` Q2。

### 4.3 fallback/

`scripts/fallback/linux_macos.md` 与 `windows_powershell.md` 保留，作为"无 Python/Node"环境的 Bash 速查手册。各 skill body 在 "Required Tools" 章节链向 fallback 文档作为最坏情况兜底。

---

## 五、templates/ → references/templates/

| AICC 模板 | 放进哪个 skill | 备注 |
|---|---|---|
| `GENERATION_PLAN_TEMPLATE.md` | `init/references/templates/` | 仅 init 用 |
| `generation_plan_trivial/simple/medium/complex/critical.md` | `init/references/templates/` + `mutual-review/references/templates/` | 分级方案与互审都要使用 |
| `PROJECT_ANALYSIS_REPORT_TEMPLATE.md` | `init/references/templates/` | |
| `PROGRESS_TEMPLATE.md`、`PROGRESS_TRACKING_TEMPLATE.md` | `init/references/templates/` | |
| `AI_RULES_TEMPLATE.md`、`templates/rules/*` | `init/references/templates/rules/` | AI_RULES 与规则示例 |
| `AI_Coding_Context_TEMPLATE.md` | `init/references/templates/` | |
| `testing_guide_TEMPLATE.md` | `init/references/templates/` | 子文档模板 |
| `deployment_guide_TEMPLATE.md` | `init/references/templates/` | 子文档模板 |
| `plans_README_TEMPLATE.md` | `init/references/templates/` | |
| `knowledge_README_TEMPLATE.md` | `init/references/templates/`、`knowledge-reuse/references/templates/` | |
| `templates/prompts/design_thinking/*.md` | `design-thinking/references/templates/prompts/` | 初版漏项，必须迁移 |
| `templates/review/*.md` | `systematic-review/references/templates/` 或 `mutual-review/references/templates/` | review plan/principles |
| `PLAN_TEMPLATE.md` | `references/templates/PLAN_TEMPLATE.md` | 多 skill 共用（设计思维、互审都可能用） |
| `dev/architecture/adr-template.md` | `adr/references/templates/` | |

---

## 六、core/ → references/

| AICC 文件 | 目标位置 | 理由 |
|---|---|---|
| `core/language_rules.md` | `references/language_rules.md` | 跨 init/health-check/incremental-update 共用 |
| `core/security_rules.md` | `references/security_rules.md` | 同上，多 skill 共用脱敏规则 |
| `core/SUMMARY_FORMAT_SPEC.md` | `references/summary_format_spec.md` | 摘要规范是底线，所有 skill 必读 |
| `core/project_types.md` + `core/project_types/*.md` | `references/project_types/` | 项目类型决策树 |
| `core/update_triggers.md` | `references/update_triggers.md` | health-check 与 incremental-update 都用 |
| `core/framework_spec.md` | `plugin/CLAUDE.md`（精简版）+ `dev/`（完整保留） | 偏框架自身规范，部分内化 |
| `core/design_decisions.md` | 留在 `dev/`（不进 plugin） | 框架团队设计文档，用户不需要 |

---

## 七、config/ → 演进与弃用

**当前 AICC**：`config/user_config.md` + `CONFIG_TEMPLATE.md` 控制框架行为（用户偏好、V3.0 功能开关等）。

**skill 模式下**：
1. **Claude Code 自身已有 settings**（settings.json）：用户偏好（model、theme 等）走原生体系，不要框架级 config 重复。
2. **项目级配置**（环境变量、.env）已由用户项目自身的 `dev_docs/configuration.md` 承载（init 会生成）。
3. **V3.0 功能开关**：在 skill 模式下不再需要"功能开关"——因为每个能力是独立 skill，用户不装就等于"关闭"。

**结论**：
- `config/` 目录**不进入 plugin**
- AICC 框架仓库（clone 模式）的 `config/` 保留，向后兼容
- 在 `plugin/README.md` 与 `01-feasibility-and-architecture.md §5.1` 明确声明"skill 模式不再有框架级 config"

---

## 八、guides/ → 拆分

| 当前 AICC 文件 | 目标位置 | 理由 |
|---|---|---|
| `guides/quick_start.md` | `plugin/README.md`（重写为面向新用户的安装与触发示例） | 人类入门 |
| `guides/project_types.md` | 已在 `references/project_types/` | 内容合并 |
| `guides/language_support.md` | `init/references/special_scenarios/multi_language.md` | 嵌入 init |
| `guides/ai_rules_maintenance.md` | `init/references/ai_rules_maintenance.md` | 嵌入 init |
| `guides/configuration_management.md` | `init/references/configuration_doc_template.md` | 嵌入 init（生成 dev_docs/configuration.md 时使用） |
| `guides/commit_guided_*.md` | `incremental-update/references/` | 嵌入 incremental-update |

---

## 九、本章小结

| 维度 | 数量 |
|---|---|
| 目标 skill 数 | **11 个短名 skill**（Phase 1 两个、Phase 1.5 一个、Phase 2 三个、Phase 3 五个） |
| development subagent 数 | **4 个真实现有 subagent 起步**（是否新增角色另行立项） |
| plugin scripts 数 | **34 Python + 34 JS（+ 3 测试）+ 2 fallback + git-hooks/ 子目录**，release 排除缓存和开发产物 |
| shared references 数 | **8 类**（language_rules、security_rules、summary_format_spec、project_types/、update_triggers、templates/PLAN_TEMPLATE 等） |
| 嵌入在 skill 内的 runtime agents | **以真实清单为准，当前 10 个 runtime 文件** |
| plugin 新增目录（无现有对应） | `tests/`（evaluation 体系）、`hooks/`（事件 hook）、`bin/`（包装命令）、`plugin-manifest.generated.json`（资产清单） |
| 待弃用的目录 | `config/`（plugin 不进） |

**关键判断**：每个 skill 的总规模（SKILL.md + references + templates）平均 ≈ 1000-2000 行；plugin 总规模 ≈ 15-25k 行 markdown + ≈ 5k 行 Python，与 document-skills 量级相当（document-skills 仅 pptx 一个 skill 就含 600+ 行 ooxml.md），可发布。

**下一文档**：[`03-implementation-roadmap.md`](./03-implementation-roadmap.md) —— 6 阶段实施路线图。
