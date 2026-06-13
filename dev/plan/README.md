---
title: 开发计划索引
summary: 汇总框架演进、迁移和专题实施计划，作为 dev/plan 目录入口。active plan 完成后迁入 done/ 归档区。
keywords: dev | plan | roadmap | index | lifecycle | done
scope: 开发计划目录索引
related_files: dev/FRAMEWORK_CONTEXT.md | ./done/README.md
dependencies: 无
verified_at: 2026-06-13
---

# 开发计划索引

本目录存放**进行中 / 待决策**的框架开发计划与方案。已完成或已被取代的计划迁入 [`done/`](./done/README.md) 归档区。

## 状态约定

每份计划的 `status` 字段采用以下枚举（链接标签与各文档 `title:` frontmatter 保持一致）：

| 状态 | 含义 | 归属目录 |
| --- | --- | --- |
| `proposed` | 已提案/分析完成，待立项或待审核，尚未实施 | `dev/plan/`（active） |
| `in-progress` | 已立项，正在实施中 | `dev/plan/`（active） |
| `done` | 已实施并落地（含已合入 master / 已交付并验证） | `dev/plan/done/` |
| `superseded` | 已被后续方案取代，仅作历史档案 | `dev/plan/done/` |

## 生命周期与归档约定

> **active plan 完成后必须归档**：一旦一份方案 `status` 转为 `done` 或 `superseded`，按以下步骤迁入 `done/`，保持 active 区只剩真正在途的工作。

1. **迁移文件**：`git mv dev/plan/<plan> dev/plan/done/<plan>`（子项目目录整体迁移）。
2. **标注状态**：在 frontmatter 写入 `status: done | superseded`（附简要落地/取代说明与归档日期）。
3. **加归档横幅**：在正文首个标题下追加一行横幅，说明已落地、归档时间与（如有）核验结论；**不改写正文历史结论**，正文中的「暴露的问题 / 待办」保留为当时状态。
4. **修复引用**：更新指向该文件的链接与 `dependencies:`/`related_files:` 路径（`dev/plan/<plan>` → `dev/plan/done/<plan>`），并将子项目内的根向相对链接补一层 `../`。
5. **更新索引**：本文件移除该条目，[`done/README.md`](./done/README.md) 增加对应条目。

## 进行中 / 提案 (active)

- [LingoTrace 方案自审核协议吸收分析与决策记录](./lingotrace-active-plan-self-review-absorption-plan.md) — `proposed`（§11 开放问题已定案 + §7.6 插件/Codex 落地映射已设计，待转可执行实施计划）
- [AICC Phase 1 审核机制二次改进计划](./linguacafe-phase1-aicc-improvement-plan.md) — `proposed`（待审核）

## 已完成 / 已归档 (done/superseded)

→ 见 [`done/README.md`](./done/README.md)（已迁入 6 份已验证的 aicc-* 方案、dayflow，以及 plugin/、skill-migration/ 两个子项目档案）。
