---
title: 文档质量保证体系
summary: 说明 AICC 框架自身质量保证体系的目录结构、审查视角、归档方式、上下文分级和测试项目复测记录入口。
keywords: quality | audit | review | test-runs | aicc
scope: AICC 框架自身质量审查与复测归档体系
related_files: dev/quality/test-runs/README.md | dev/quality/Framework_Review_Guidelines.md
dependencies: dev/FRAMEWORK_CONTEXT.md | dev/quality/standards/QUALITY_CHECKLIST.md
verified_at: 2026-06-13
---

# 文档质量保证体系

> **用途**: 为 AICC 框架自身提供系统化的质量保证工具与流程
> **核心理念**: AI 辅助下的多视角审查 + 人工裁决
> **版本**: v2.1（2026-06-13 三分支模型对齐；v2.0 2026-04-25 全面重写：完整文件索引 + 三视角分层 + context 优先级分级）

---

## 📋 体系概述

本目录承载 AICC 框架对**自身**进行质量审查的全部工具、规程与档案。审查的根本特点是 dogfood —— **用 AICC 自带的方法论（设计思维、互审、ADR、Commit-Guided）来审 AICC 自己**。

### 核心价值

- ✅ **三视角分层** —— 用户视角 / 完整性视角 / dev 卫生视角，避免混淆问题归属
- ✅ **标准化审查** —— 统一的质量标准、问题记录格式、进度跟踪规范
- ✅ **可中断恢复** —— 进度跟踪支持长时间审查在多次会话间接续
- ✅ **分级 context** —— 不要求每个文件都有独立 context，按优先级分配审查粒度
- ✅ **历史可追溯** —— `audits/` 下按轮次归档，支持跨版本对比

---

## 📁 目录结构

### 顶层文件（方法论与规程）

| 文件 | 角色 |
|---|---|
| [Start_Review.md](./Start_Review.md) | 启动审查的入口与指令模板 |
| [Framework_Review_Guidelines.md](./Framework_Review_Guidelines.md) | 全框架审查方法论（含三视角分层、范围、清单、报告大纲、成熟度评级） |
| [AUDIT_WORKFLOW.md](./AUDIT_WORKFLOW.md) | 单文档审查 9 步流程 |
| [HOW_TO_GENERATE_CONTEXTS.md](./HOW_TO_GENERATE_CONTEXTS.md) | context 批量/单个生成 SOP |
| [Issue_Recording_Standard.md](./Issue_Recording_Standard.md) | 问题记录标准（ID、模板、分类、严重级别） |
| [Progress_Tracking_Standard.md](./Progress_Tracking_Standard.md) | 进度跟踪标准（含中断恢复机制） |

### standards/ — 质量标准

| 文件 | 角色 |
|---|---|
| [COMMON_STANDARDS.md](./standards/COMMON_STANDARDS.md) | 五维度通用标准（准确性 / 完整性 / 一致性 / 可读性 / 可操作性） |
| [QUALITY_CHECKLIST.md](./standards/QUALITY_CHECKLIST.md) | 快速核对清单 |
| [BY_DOCUMENT_TYPE.md](./standards/BY_DOCUMENT_TYPE.md) | 按文档类型的专项标准（入口 / core / workflows / agents / tools / templates / guides / config） |

### contexts/ — 单文档审查上下文（按需生成）

采用**按需生成**策略：仅在审查 🔴 优先级文档时，按 [HOW_TO_GENERATE_CONTEXTS.md](./HOW_TO_GENERATE_CONTEXTS.md) 现场生成对应 context。目录通常仅含 `_template.md` 模板，**不预先落地全部文档的 context**（成本过高且易过时）。

**使用方式**：

```
【新建 AI 会话】
1. 发送: dev/FRAMEWORK_CONTEXT.md            （全局心智模型）
2. 若审查 🔴 文档：现场按 HOW_TO_GENERATE_CONTEXTS.md 生成对应 context 并发送
3. 发送: 实际文档内容
4. 开始审查讨论
```

详细的"何时需要 context / 何时批审 / 何时仅合规扫描"分级策略，见下方"🎚️ Context 优先级分级（v2.0 引入）"。

### audits/ — 审查归档

完整审查（round）对应 `audits/YYYY-MM-DD_Version_Scope/` 一个子目录，含 5 件套；轻量单文档审查可直接落地为 `audits/YYYY-MM-DD_<scope>.md` 单文件（loose-file 形式，无需建目录）。完整目录 5 件套：

```
Review_Plan.md          - 本轮范围、视角、批次切分、退出条件
Issue_Tracking.md       - 问题清单（按 PROJ-YYYYMMDD-XXX 编号）
Progress_Tracking.md    - 阶段/任务进度，支持中断恢复
Review_Log.md           - 每日日志、关键决策、临时观察
Review_Checklist.md     - 复查清单（用于修复后验证）
```

可选附加：`Comprehensive_Review_Report.md`、`Improvement_Roadmap.md`、`Issue_Analysis.md`、专项报告等。

详见 [Framework_Review_Guidelines.md §审查交付物清单](./Framework_Review_Guidelines.md#审查交付物清单模板)。

### test-runs/ — 真实项目复测归档

`test-runs/` 保存 Dayflow、LinguaCafe、Memex 等真实项目运行 AICC 后的原始复盘记录、复跑命令、检查结果和 fixture 提炼说明。优化方案仍放在 `dev/plan/`，本目录保留可回放证据。

入口：[test-runs/README.md](./test-runs/README.md)

---

## 🔭 审核视角分层

任何一次审查都必须先选择视角集合：

| 视角 | 可见范围 | 审核什么 |
|---|---|---|
| **A. 用户视角** | master/dev 用户可见树 | 模拟终端用户能否照着 README → AI_ENTRY_POINT 跑通；用户可见树中任何对 dev/ 的引用都视为缺陷 |
| **B. 完整性视角** | 用户可见树 + internal/dev/ | 实现 ↔ ADR ↔ FRAMEWORK_CONTEXT ↔ dev/plan 一致性 |
| **C. internal/dev/ 卫生视角** | internal 分支的 dev/ 树 | dev/ 仅存在于 internal 分支、master/dev 结构一致、用户可见树无 dev/ 泄漏 |

**Comprehensive round 应执行 A+B+C 全部三视角**。详见 Framework_Review_Guidelines.md §审核视角分层。

---

## 🔄 审查工作流（简）

```
1. 选择文档
2. 新建 AI 会话
3. 加载全局上下文 (dev/FRAMEWORK_CONTEXT.md)
4. 加载文档审查上下文 (quality/contexts/xxx.md，若有)
5. 发送实际文档
6. AI 分析并提供建议
7. 人工审核并裁决
8. 执行优化
9. （可选）记录审查报告到 audits/
```

详见 [AUDIT_WORKFLOW.md](./AUDIT_WORKFLOW.md)。

---

## 🎚️ Context 优先级分级（v2.0 引入）

实测 AICC 公共层有 **200+ 个 .md + 70+ 个工具脚本**，远超原 README 索引的 30 项。给每个文件单独写 context 不现实，因此按以下三级分配：

| 级别 | 含义 | 处理方式 |
|---|---|---|
| 🔴 **独立 context** | 入口、核心规范、关键工作流、关键模板等结构性文档 | 在 `contexts/` 下有独立 context 文件，单独深度审查 |
| 🟡 **同类批审** | 同目录/同类型的批量文档（如 12 个 project_types、24 个非关键模板、各类 examples） | 共享一份"目录级 context"，集中按统一标准批量审查 |
| ⚪ **仅合规扫描** | 工具脚本、JSON/YAML/CSS、配置实例等非叙事性文件 | 不写 context，由子代理做合规性自动扫描（双版本对称、零依赖、字段完整等） |

---

## 📊 完整文档索引

> **状态图例**：⚪ 未开始 / 🔵 进行中 / ✅ 已完成 / ⏭️ 跳过（不在本视角内）
> **优先级图例**：🔴 独立 context / 🟡 同类批审 / ⚪ 仅合规扫描

### 入口层（公共，🔴 全部独立 context）

| 优先级 | 文档 | 视角 | 备注 |
|:-:|---|:-:|---|
| 🔴 | [`AI_ENTRY_POINT.md`](../../AI_ENTRY_POINT.md) | A+B | AI 唯一入口 |
| 🔴 | [`README.md`](../../README.md) | A | GitHub 首页/人类入门 |
| 🔴 | [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | A+B | 含对 dev/quality 的引用，三视角交叉点 |

### core/ — 核心规范（🔴 顶层独立，🟡 project_types 批审）

**顶层规范文档（🔴 独立 context）**：

| 文档 | 视角 |
|---|:-:|
| [`core/framework_spec.md`](../../core/framework_spec.md) | A+B |
| [`core/design_decisions.md`](../../core/design_decisions.md) | A+B |
| [`core/SUMMARY_FORMAT_SPEC.md`](../../core/SUMMARY_FORMAT_SPEC.md) | A+B |
| [`core/language_rules.md`](../../core/language_rules.md) | A |
| [`core/security_rules.md`](../../core/security_rules.md) | A |
| [`core/project_types.md`](../../core/project_types.md) | A |
| [`core/update_triggers.md`](../../core/update_triggers.md) | A |

**项目类型子目录（🟡 批审，共享 context `core_project_types_collection.md`）**：

`core/project_types/` 下 12 个文件（ai_llm / backend_api / cli_tool / containerized / data_science / desktop / fullstack / library_sdk / microservices / mobile / web_frontend / script）。批审重点：结构对称性、技术栈准确性、与 `core/project_types.md` 索引一致性。

### agents/ — AI 角色库（🟡 主要批审）

**runtime/（10 个，🟡 批审 + 关键角色 🔴 独立）**：

🔴 独立 context：`code_reviewer.md`、`security_auditor.md`、`understanding_guardian.md`（这三者是 quality 体系本身要委派的角色，必须深度审）

🟡 批审：`commit_analyst.md`、`design_facilitator.md`、`document_recommender.md`、`performance_optimizer.md`、`plan_reviewer.md`、`summary_generator.md`、`test_engineer.md`

**development/（4 个，🟡 批审）**：`api_designer.md`、`architecture_analyst.md`、`database_designer.md`、`product_manager.md`

**language_specific/（6 个，🟡 批审）**：`base/`（含 backend_engineer / frontend_engineer）、`java/`、`python/`、`typescript/`、`vue3_expert.md`、`vue3_state_manager.md`

**personas/（3 个角色 + 1 个 README，🟡 批审，重点：人格定义边界与"是否仍合规"）**：`linus_torvalds.md`、`martin_fowler.md`、`uncle_bob.md`

**workflows/（7 个，🟡 批审）**：`create_custom_agent_workflow.md`、`document_fix_coordinator.md`、`document_recommender.md`、`error_detector.md`、`knowledge_librarian.md`、`knowledge_matcher.md`、`understanding_guardian.md`

**custom/（1 个，⚪ 仅合规）**：`_template.md`

**_templates/（2 个，⚪ 仅合规）**：`agent_template.md`、`quality_checklist.md`

**examples/（18 个，🟡 批审，含 1 个 design_thinking/ 子目录与 1 个 README，重点：示例与角色定义一致性）**

**_progress/（3 个，视角 B 专属）**：`implementation_progress.md`、`issues_and_feedback.md`、`role_conversion_log.md` —— 视角 A 下应不存在引用泄漏（用户可见树中任何指回 `dev/` 的引用均为泄漏缺陷）

### workflows/ — 工作流（🔴 关键路径独立，🟡 其他批审）

**🔴 独立 context（关键路径）**：

| 文档 | 视角 |
|---|:-:|
| [`workflows/path_a_first_generation.md`](../../workflows/path_a_first_generation.md) | A+B |
| [`workflows/path_b_health_check.md`](../../workflows/path_b_health_check.md) | A+B |
| [`workflows/path_c_incremental_update.md`](../../workflows/path_c_incremental_update.md) | A+B |
| [`workflows/path_d_specific_tasks.md`](../../workflows/path_d_specific_tasks.md) | A+B |
| [`workflows/generation_workflow.md`](../../workflows/generation_workflow.md) | A+B |
| [`workflows/commit_guided_update.md`](../../workflows/commit_guided_update.md) | A+B |
| [`workflows/git_safety_workflow.md`](../../workflows/git_safety_workflow.md) | A+B |
| [`workflows/doc_error_fix_workflow.md`](../../workflows/doc_error_fix_workflow.md) | A+B |
| [`workflows/incremental_update_workflow.md`](../../workflows/incremental_update_workflow.md) | A+B |
| [`workflows/document_health_check.md`](../../workflows/document_health_check.md) | A+B |

**🟡 批审**：`detection_workflow.md`、`decision_workflow.md`、`monorepo_workflow.md`、`maintenance_workflow.md`、`progress_tracking.md`、`create_custom_tool_workflow.md`、`create_custom_agent_workflow.md`

**🟡 批审子目录**：

- `workflows/review_standards/`（4 个：bugfix / doc / feature / refactor 的审查标准）
- `workflows/shared/`（4 个：ai_checklist / failure_handling / special_scenarios 等共享工具）

### guides/ — 指南（🔴 入门关键，🟡 其他批审）

**🔴 独立 context**：

| 文档 | 视角 |
|---|:-:|
| [`guides/quick_start.md`](../../guides/quick_start.md) | A |
| [`guides/commit_guided_quick_start.md`](../../guides/commit_guided_quick_start.md) | A |
| [`guides/configuration_management.md`](../../guides/configuration_management.md) | A |
| [`guides/faq.md`](../../guides/faq.md) | A |

**🟡 批审**：`generation_workflow.md`、`commit_guided_migration.md`、`ai_rules_maintenance.md`、`documentation_maintenance.md`、`language_support.md`、`project_types.md`

**🟡 批审子目录**：

- `guides/examples/`（5 个真实摘要示例：API / architecture / config / tool / workflow）

### templates/ — 模板（🔴 关键模板，🟡 其他批审）

**🔴 独立 context**：

| 文档 | 视角 |
|---|:-:|
| [`templates/AI_Coding_Context_TEMPLATE.md`](../../templates/AI_Coding_Context_TEMPLATE.md) | A+B |
| [`templates/AI_RULES_TEMPLATE.md`](../../templates/AI_RULES_TEMPLATE.md) | A+B |
| [`templates/GENERATION_PLAN_TEMPLATE.md`](../../templates/GENERATION_PLAN_TEMPLATE.md) | A+B |
| [`templates/HEALTH_CHECK_REPORT_TEMPLATE.md`](../../templates/HEALTH_CHECK_REPORT_TEMPLATE.md) | A+B |
| [`templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`](../../templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md) | A+B |

**🟡 批审**：复杂度变体（trivial/simple/medium/complex/critical 5 个）、PLAN_TEMPLATE / PROGRESS_TEMPLATE / PROGRESS_TRACKING_TEMPLATE / RULE_TEMPLATE / TESTING_GUIDE_TEMPLATE / DEPLOYMENT_GUIDE_TEMPLATE 等

**🟡 批审子目录**：

- `templates/prompts/`（5 个设计思维步骤模板：why / how / risk / reflection / decision）
- `templates/rules/`（含 core 与 triggers 子目录）
- `templates/review/`（审查计划模板）

### config/ — 配置（🔴 1 个独立 + 🟡 1 个批审 + ⚪ 实例）

| 优先级 | 文档 |
|:-:|---|
| 🔴 | [`config/CONFIG_TEMPLATE.md`](../../config/CONFIG_TEMPLATE.md) |
| 🟡 | [`config/MIGRATION_GUIDE.md`](../../config/MIGRATION_GUIDE.md) |
| ⚪ | `config/README.md`（合规扫描）、`config/.gitignore`（不审） |

### tools/ — 工具脚本（⚪ 全部合规扫描）

`tools/py/` 与 `tools/js/` 各 35 脚本，加上 `tools/fallback/`、git hooks 等，共 70+ 个文件。**不写 context**，统一由子代理做合规性扫描：

| 扫描项 | 工具/方法 |
|---|---|
| Py/JS 双版本对称 | grep `tools/py/*.py` 与 `tools/js/*.js` 文件名对应 |
| 零依赖红线 | 静态扫描 `import`（Python）/ `require`（JS）语句，仅允许标准库 |
| 头部文档注释 | 每个脚本头部需有 docstring + 用法说明 |
| 跨平台兼容 | python/python3 双兼容、Windows/Unix 路径处理 |

**🔴 1 个独立 context**：[`tools/README.md`](../../tools/README.md)（工具库总览，对外承诺的能力清单）

### internal/dev/ 树（视角 B/C 专属）

视角 B/C 下需审查（`dev/` 仅存在于 internal 分支，当前子目录如下）：

- `dev/FRAMEWORK_CONTEXT.md`（🔴 独立 context，全局心智模型源头）
- `dev/architecture/`（ADR 系统，含 `decisions/`、`evolution.md`、`adr-template.md`）
- `dev/quality/` —— **本目录**自指审查（v2.0 起明确纳入）
- `dev/plan/`（规划与进度源头，视角 B 一致性轴）
- `dev/complexity/`（complexity 仪表盘运行时）
- `dev/reference/`（开发参考资料，🟡 批审）
- `dev/case_skillatlas_review/`（真实案例素材，🟡 批审）

（注：V3.0/V2.3/V2.2/real_case/discussions 等历史目录已归档/清理，不在当前 internal 分支。）

### 仓库根孤儿文件（视角 C 关注）

- `audit_metadata.py`（位于仓库根，疑似应迁入 `tools/` —— F-3 缺陷）

---

## 📈 审查进度跟踪

**当前状态**：多轮审查已完成并归档于 `audits/`（详见下表）。注：2026-04-25 轮曾记录"待修 31 项 Issue 进入 P0/P1/P2"——此为该轮历史快照，后续轮次已对其复查/修复，最新状态以各轮归档为准。

**历史轮次**：

| 日期 | 范围 | 报告路径 | 主要发现 |
|---|---|---|---|
| 2026-04-25 | V3.0+ Comprehensive | `audits/2026-04-25_V3.x_Comprehensive/` | 35 项 Issue（严重 2 / 主要 11 / 次要 14 / 建议 8）；V3.0 12 项实体 ✅ 真实落地；frontmatter 14% 自指失败；30 分钟用户旅程不达标；详见该轮 Comprehensive_Review_Report.md |
| 2026-05-05 | V3.x Followup Comprehensive | `audits/2026-05-05_V3.x_Followup_Comprehensive/` | 历史 Issue 复验 + delta 分类 + 入口路径回放 + 工作流回归 + 合规扫描 + 修复验证（reports/B1–B8）|
| 2026-05-12 | Framework dogfood 健康检查 | `audits/2026-05-12_framework_dogfood/health_check_report.md` | 单文档健康检查（loose-file 形式）|
| 2026-05-18 | Dayflow Phase1 AICC 改进验证 | `audits/2026-05-18_dayflow_phase1_aicc_improvement_verification.md` | Dayflow 真实项目 Phase1 改进项验证（loose-file 形式）|

---

## 💡 典型使用场景

### 场景 1：全框架 Comprehensive 审查（如本次 V3.0+）

1. 在 `audits/` 下创建本轮目录与 5 件套
2. 选择视角集合（推荐 A+B+C）
3. 按 🔴 → 🟡 → ⚪ 优先级分批，每批可独立委派子代理
4. 持续记录到 `Issue_Tracking.md`，按视角与严重级别分类
5. 完成后产出 `Comprehensive_Review_Report.md` 与 `Improvement_Roadmap.md`

### 场景 2：单文档临时审查

1. 查阅或现场生成该文档的 context（按 [HOW_TO_GENERATE_CONTEXTS.md](./HOW_TO_GENERATE_CONTEXTS.md) §单个新文档生成工作流）
2. 新建 AI 会话，按 [AUDIT_WORKFLOW.md](./AUDIT_WORKFLOW.md) 9 步执行
3. 视情况记录到 `audits/` 或仅本地修改

### 场景 3：新文档加入框架后的初次质量验证

1. 为新文档生成 context
2. 立即进行初次审查（视角 A 必检）
3. 通过后将 context 提交到 `contexts/`，更新本 README 索引

### 场景 4：组件专项审查（如仅审 tools/ 双版本对称）

1. 在 `audits/` 下创建 `YYYY-MM-DD_V3.0_Component-tools/`
2. 仅声明视角 A，仅扫描 ⚪ 合规项
3. 子代理批量扫描，主代理整合

---

## 🔗 相关文档

- [`workflows/document_health_check.md`](../../workflows/document_health_check.md) — 文档健康度检查（与质量审查互补）
- [`dev/FRAMEWORK_CONTEXT.md`](../FRAMEWORK_CONTEXT.md) — 全局心智模型，每次审查必须先加载
- [`core/SUMMARY_FORMAT_SPEC.md`](../../core/SUMMARY_FORMAT_SPEC.md) — 文档摘要格式规范

---

**版本**: v2.1
**最后更新**: 2026-06-13
**维护者**: Framework Team
**v2.0 变更要点**:
- 完整索引 200+ 公共文档（v1.0 仅列 30+）
- 引入 🔴/🟡/⚪ 三级 context 优先级
- 引入"审核视角分层"与 Guidelines.md 呼应
- 新增 dev/ 层审查范围说明（与三视角对应）
- 新增 audits/ 5 件套规范说明
**v2.1 变更要点（2026-06-13）**:
- 改写为三分支模型（master/dev/internal），视角表与 dev/ 树范围对齐当前 internal 分支
- 删除 export-ignore / V3.0/V2.3/V2.2/real_case 等失效路径
- 审查历史补齐 2026-05-05 / 05-12 / 05-18 三轮，刷新当前状态口径
