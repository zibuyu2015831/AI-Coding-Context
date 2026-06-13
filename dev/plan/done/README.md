---
title: 已完成 / 已归档计划索引
summary: dev/plan/done 归档区索引。汇总已实施并验证（done）或已被取代（superseded）的开发计划；active plan 完成后迁入此处。
keywords: dev | plan | done | archive | superseded
scope: dev/plan/done 归档区索引
related_files: ../README.md
dependencies: 无
verified_at: 2026-06-13
---

# 已完成 / 已归档计划索引

本目录是 `dev/plan/` 的**归档区**。一份 active plan 一旦完成（已实施并验证）或被后续方案取代，即从 `dev/plan/` 迁入此处，并在 frontmatter 标注 `status: done | superseded`、在正文顶部加归档横幅。归档流程见上级 [`../README.md`](../README.md) 的「生命周期与归档约定」。

> 归档不改写历史结论：正文中的「暴露的问题 / 待办」均为当时状态，仅在顶部追加横幅说明已落地与归档时间。

## 已实施并验证 (done)

下列 6 份 Phase 1 / 首版验收改进方案均源自下游项目实测（LinguaCafe / Memex / Dayflow / EchoTalk），其改进已落地到框架的契约、检查器、模板与工作流（Python+JS 一致并配有通过的测试），于 2026-06-13 经逐任务核验后归档：

| 计划 | 来源 | 核验 |
| --- | --- | --- |
| [Phase 1 审核门落地实施计划](./aicc-phase1-review-gate-implementation-plan.md) | LinguaCafe | 13/14（Task 3 等价实现；2 个 project_types 指南待补） |
| [generation_plan 复查流程缺口记录与优化方案](./aicc-generation-plan-review-process-gap-plan.md) | LinguaCafe 第三轮 | 7/7 |
| [Phase 1 审核门复测后续优化方案](./aicc-phase1-review-gate-followup-plan.md) | LinguaCafe 复测 | 7/7（§11 落地记录已核实） |
| [首版验收门禁可信度优化方案](./aicc-first-release-acceptance-gate-improvement-plan.md) | LinguaCafe 首版 | 9/9 |
| [Memex 首次运行复测问题记录与优化方案](./aicc-memex-first-run-regression-plan.md) | Memex | 8/8 |
| [EchoTalk Phase 1 复查闭环优化方案](./aicc-echotalk-phase1-review-closure-plan.md) | EchoTalk 第二轮 | ~15/17（2 项次要后续） |
| [Dayflow 首次运行复盘与 AICC Phase 1 改进计划](./dayflow-phase1-aicc-improvement-plan.md) | Dayflow | 已实施（见 `dev/quality/audits/2026-05-18_dayflow_phase1_aicc_improvement_verification.md`） |

## 框架演进方案 (done)

下列方案为框架自身能力演进（非单个下游项目的 Phase 1 改进），均已实施并验证后归档：

| 计划 | 来源 | 核验 |
| --- | --- | --- |
| [LingoTrace 方案自审核协议吸收分析与决策记录](./lingotrace-active-plan-self-review-absorption-plan.md)（Doc B） | LingoTrace `plan-review-protocol.md` | plan-review 自审机制跨 SSOT/插件/Codex 三形态落地（dev `df7ab06`）：`core/plan_review_protocol.md` 薄层 + `plan_done_without_review`（Py/JS 双实现 + 测试，键于 `plans/done/` 目录成员）+ `skills/plan-review/` 委派 mutual-review + `pre_commit_gate` 调用同一判定 + `aicc.planReview` + Codex 投影。build/codex/doc_health 测试全绿 |
| [Codex hook 机制收敛与交付形态对齐方案](./codex-hook-convergence-delivery-form-alignment-plan.md)（Doc A） | Codex v0.117 官方文档查证 | Doc B 的前置基础：`.codex/` 强制包 + README 对齐 + `test_codex_projection.py` + 已归档规格更正横幅；前置使命随 Doc B 落地兑现 |

## 已被取代 / 子项目档案 (superseded / shipped)

| 计划 | 状态 | 说明 |
| --- | --- | --- |
| [AICC → Claude Code Plugin 改造方案](./plugin/README.md) | `done`（shipped） | 插件已合入 master（V3.0「conversion complete」P1.5→P5）；保留作规划档案 |
| [AICC Skill 化迁移规划](./skill-migration/README.md) | `superseded` | 已被 `plugin/` 方案整体吸收并更名 |

---

**最后更新**：2026-06-13 — 迁入框架演进方案 Doc B（plan-review 自审机制，dev `df7ab06`）+ Doc A（Codex hook 收敛，前置使命兑现）。此前：建立 `done/` 归档区，迁入 6 份已验证的 aicc-* 方案 + dayflow + plugin/ + skill-migration/。
