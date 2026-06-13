---
title: 开发计划索引
summary: 汇总框架演进、迁移和专题实施计划，作为 dev/plan 目录入口。
keywords: dev | plan | roadmap | index
scope: 开发计划目录索引
related_files: dev/FRAMEWORK_CONTEXT.md
dependencies: 无
verified_at: 2026-06-13
---

# 开发计划索引

本目录用于存放框架开发计划、迁移方案和实施路线图。

## 状态约定

每份计划的 `status` 字段采用以下枚举（链接标签与各文档 `title:` frontmatter 保持一致）：

| 状态 | 含义 |
| --- | --- |
| `proposed` | 已提案/分析完成，待立项或待审核，尚未实施 |
| `in-progress` | 已立项，正在实施中 |
| `done` | 已实施并落地（含已合入 master / 已交付） |
| `superseded` | 已被后续方案取代，仅作历史档案 |

> 注：部分早期改进记录未在 frontmatter 显式登记状态，下方以 `(status: ?)` 标注，归入 active 组待逐一确认，不臆测。

## 进行中 / 提案 (active)

- [LingoTrace 方案自审核协议吸收分析与决策记录](./lingotrace-active-plan-self-review-absorption-plan.md) — `proposed`
- [AICC Phase 1 审核机制二次改进计划](./linguacafe-phase1-aicc-improvement-plan.md) — `proposed`（待审核）
- [AICC Phase 1 审核门落地实施计划](./aicc-phase1-review-gate-implementation-plan.md) — (status: ?)
- [AICC generation_plan 复查流程缺口记录与优化方案](./aicc-generation-plan-review-process-gap-plan.md) — (status: ?)
- [AICC Phase 1 审核门复测后续优化方案](./aicc-phase1-review-gate-followup-plan.md) — (status: ?)
- [AICC 首版验收门禁可信度优化方案](./aicc-first-release-acceptance-gate-improvement-plan.md) — (status: ?)
- [AICC Memex 首次运行复测问题记录与优化方案](./aicc-memex-first-run-regression-plan.md) — (status: ?)
- [AICC EchoTalk Phase 1 复查闭环优化方案](./aicc-echotalk-phase1-review-closure-plan.md) — (status: ?)

## 已完成 / 已归档 (done/superseded)

- [AICC → Claude Code Plugin 改造方案 — 总索引与决策](./plugin/README.md) — `done`（插件已合入 master，V3.0「conversion complete」）
- [Dayflow 首次运行复盘与 AICC Phase 1 改进计划](./dayflow-phase1-aicc-improvement-plan.md) — `done`（已实施）
- [AICC Skill 化迁移规划 — 总索引](./skill-migration/README.md) — `superseded`（已被 plugin 方案取代）
