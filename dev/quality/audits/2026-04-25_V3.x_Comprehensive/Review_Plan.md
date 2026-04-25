---
title: AICC V3.x Comprehensive Review — Round Plan
summary: 本轮全面审查的范围、视角、风险维度、批次切分、退出条件与时间估算；以三视角分层与五大风险维度为骨架
keywords: comprehensive-review | three-views | risk-dimensions | batches | v3.x
scope: 整个 AICC 框架（Public + dev/）的一次完整审查
verified_at: 2026-04-25
---

# AICC V3.x Comprehensive Review — Round Plan

## 📌 元信息

| 字段 | 值 |
|---|---|
| 启动日期 | 2026-04-25 |
| 框架版本 | V2.3 稳定 + V3.0（P0 完成 11 项 / P1 进行中 / P2 部分启动） |
| 审查范围 | Comprehensive（全框架，含 Public + dev/） |
| 视角集合 | A（用户）+ B（完整性）+ C（dev/ 卫生）三视角全开 |
| 主审 AI | Claude Opus 4.7 (1M context) |
| 维护者 | Framework Team |
| 预期退出 | 完成 R1-R5 五大风险维度的全部一级核查 + 报告产出 + 改进路线图 |

---

## 🎯 审查目标

1. **整体完整性** — 验证 386 文件的结构完整性、模块职责边界、版本演进一致性
2. **架构一致性** — 实现 ↔ ADR ↔ FRAMEWORK_CONTEXT ↔ PROGRESS 是否对齐
3. **问题全面检测** — 识别技术缺陷、文档不一致、引用断链、性能瓶颈、安全风险
4. **质量综合评估** — 按 `standards/COMMON_STANDARDS.md` 五维度逐文档/逐目录打分
5. **价值实现分析** — V3.0 已完成的 11 项功能是否真的落地、是否产生预期价值
6. **未来发展建议** — 基于发现产出 Improvement_Roadmap

---

## 🔭 视角矩阵

| 文件类别 | 视角 A | 视角 B | 视角 C |
|---|:-:|:-:|:-:|
| 入口（AI_ENTRY_POINT, README, CONTRIBUTING） | ✅ | ✅ | ⏭️ |
| core/ 顶层 + project_types/ | ✅ | ✅ | ⏭️ |
| agents/ 全部 | ✅ | ✅ | ⏭️ |
| workflows/ 全部 | ✅ | ✅ | ⏭️ |
| guides/ 全部 | ✅ | ⏭️ | ⏭️ |
| templates/ 全部 | ✅ | ✅ | ⏭️ |
| config/ | ✅ | ⏭️ | ⏭️ |
| tools/ 脚本 | ✅ | ✅ | ⏭️ |
| dev/FRAMEWORK_CONTEXT.md | ⏭️ | ✅ | ✅ |
| dev/architecture/ | ⏭️ | ✅ | ✅ |
| dev/V3.0/ (PROGRESS, README, confirmed/) | ⏭️ | ✅ | ✅ |
| dev/quality/ 自指 | ⏭️ | ✅ | ✅ |
| dev/complexity/ | ⏭️ | ✅ | ✅ |
| dev/V2.3, V2.2, reference/, real_case/ | ⏭️ | ⏭️ | ✅（卫生） |

✅ = 该视角下必检；⏭️ = 该视角下不适用或暂不审

---

## ⚠️ 五大风险维度

| 维度 | 内容 | 主要视角 | 检测方法 |
|---|---|:-:|---|
| **R1** | **工作流闭环** — generation/commit_guided/git_safety/quality/ADR/doc_error_fix 等工作流之间的衔接是否真的可走通；端到端剧本是否能跑 | A+B | 端到端剧本演练 + 逐 workflow 审查 |
| **R2** | **V3.0 落地一致性** — 11 项已完成功能是否每一项都有对应的 agents/tools/workflows/templates 实体支撑；FRAMEWORK_CONTEXT 与 PROGRESS 是否一致 | B | 对照 PROGRESS 逐项核查实体存在与可调用性 |
| **R3** | **引用与边界** — A 视角下 Public→dev/ 的死链；B 视角下交叉引用一致性；C 视角下 dev/ 内部悬空引用 | A+B+C | 全仓库 grep + 链接有效性扫描 |
| **R4** | **新用户上手路径** — 从零项目能否 30 分钟内产出第一份 AI_Coding_Context.md；README→AI_ENTRY_POINT→quick_start 路径是否闭环 | A | 端到端用户旅程模拟 + quick_start 跑通 |
| **R5** | **自指一致性** — AICC 用自己的 quality/ 审自己时，规程是否真的能用；BY_DOCUMENT_TYPE 等被引用的标准是否存在 | B+C | 审查过程本身就是验证 |

---

## 📦 批次切分

按 `quality/README.md` 的 🔴/🟡/⚪ 优先级与五大风险维度的交叉，分 7 个批次：

### 批次 B0：基线快照（已完成）
- ✅ 已读取 quality/ 所有方法论文档
- ✅ 已生成 386 文件全量盘点
- ✅ Phase 0 体系补全已 commit + push
- ✅ 已识别 F-1 ~ F-8 基线问题（见 Issue_Tracking.md）

### 批次 B1：R3 引用与边界（视角 A 优先）
**目标**：穷尽 Public→dev/ 的所有死链，区分真泄漏 vs 故意保留
- 全仓库 grep `dev/` 路径引用，过滤 shell `/dev/null` 假阳性
- 分类：(a) 真泄漏（必须修复或 dev-only 标注）、(b) CONTRIBUTING.md 等故意（需明确说明）
- 同步检查 dev/ 内部对已删文件的悬空引用（C 视角）
- **预计**：1 批次，产出 ~10-30 条 Issue
- **委派**：Explore agent（thorough）做扫描，主代理裁决

### 批次 B2：R2 V3.0 落地一致性
**目标**：核对 11 项已完成功能的实体存在与文档一致性
- 对照 `dev/V3.0/PROGRESS.md` 已完成清单（001/003/004/005/006/012/013/014/016/017/018）
- 每项检查：agents/、tools/、workflows/、templates/、config/ 是否有对应实体
- 检查 `FRAMEWORK_CONTEXT.md` 与 PROGRESS 一致（已知 F-1：FRAMEWORK_CONTEXT 漏列 011/014）
- **预计**：1 批次，产出 ~5-15 条 Issue
- **委派**：Explore agent 做实体存在性扫描

### 批次 B3：R1 工作流端到端闭环
**目标**：模拟用户跑通核心工作流剧本
- 剧本 1：新项目首次生成（path_a → generation_workflow → AI_RULES 生成）
- 剧本 2：commit-guided 文档同步（commit → commit_guided_update → git_safety → review）
- 剧本 3：文档谬误修复（detection → doc_error_fix → 011 ADR 流程）
- 剧本 4：复杂度告警（complexity_scanner → 报告 → 决策）
- 验证：每剧本所需的 workflow / agent / tool / template 是否齐全可用
- **预计**：2 批次（每剧本约 0.5 批次）
- **委派**：主代理深度演练，code_reviewer 复审

### 批次 B4：R5 自指一致性 + quality/ 体系自审
**目标**：用 v2.0 的 quality 体系审 quality 体系自身
- README 索引覆盖率（已完成 v2.0 重写，应通过）
- Guidelines 内部一致性（已修订 v1.2，应通过）
- 被引用标准都存在（BY_DOCUMENT_TYPE.md 已补，应通过）
- contexts/ 实际数量 vs README 标注（当前为 0，是已知缺口）
- audits/ 物理存在（已创建）
- sub-agent 名称对齐 agents/runtime/（已修订）
- **预计**：1 批次，产出 ~3-8 条 Issue
- **委派**：understanding_guardian 角色

### 批次 B5：R4 新用户旅程
**目标**：模拟"我是新用户"路径
- 仅看 Public 层：README → AI_ENTRY_POINT → quick_start → 第一份 AI_Coding_Context.md
- 记录每个停顿点、歧义点、断链点
- 检查 30 分钟时间预算
- **预计**：1 批次，产出 ~5-15 条 Issue
- **委派**：主代理切换"用户视角"，禁用 dev/ 知识

### 批次 B6：批量合规性扫描（⚪ 仅合规级文件）
**目标**：对 tools/ 70+ 脚本与所有 .md 做合规扫描
- 双版本对称性（py vs js）
- Python 零依赖红线（grep import）
- JS 零依赖红线（grep require）
- YAML Frontmatter 摘要合规率（按 SUMMARY_FORMAT_SPEC）
- 文档头部 docstring 完整性
- **预计**：1 批次，产出聚合报告
- **委派**：通用 Explore agent 做批量扫描

### 批次 B7：报告整合 + 改进路线图
- 汇总 Issue_Tracking 全部条目，按视角/严重级别/类型统计
- 产出 Comprehensive_Review_Report.md
- 产出 Improvement_Roadmap.md（短期/中期/长期）
- 产出 Issue_Analysis.md
- 更新 quality/README.md 的"历史轮次索引"

---

## 🤖 子代理委派策略（本轮）

| 批次 | 推荐角色 |
|---|---|
| B1 R3 引用扫描 | 通用 Explore agent（thorough） |
| B2 V3.0 实体核查 | 通用 Explore agent + understanding_guardian |
| B3 端到端剧本 | 主代理 + code_reviewer 复审关键决策 |
| B4 自指审查 | understanding_guardian |
| B5 新用户旅程 | 主代理（带用户视角约束） |
| B6 批量合规扫描 | 通用 Explore agent + 自动化脚本 |
| B7 报告整合 | 主代理 |

---

## ⏱️ 时间估算

| 批次 | 估算 |
|---|---|
| B0 已完成 | 0 |
| B1 R3 引用边界 | 1-2 小时 |
| B2 V3.0 一致性 | 1-2 小时 |
| B3 工作流闭环（4 剧本） | 3-4 小时 |
| B4 自指审查 | 0.5-1 小时 |
| B5 新用户旅程 | 1-2 小时 |
| B6 批量合规扫描 | 1-2 小时 |
| B7 报告整合 | 2-3 小时 |
| **总计** | **9.5 - 16 小时**（可分多次会话执行） |

---

## 🚪 退出条件

本轮 round 视为完成，需满足：

1. ✅ 所有 7 个批次状态为 completed
2. ✅ Issue_Tracking.md 中的每条问题都有：归属视角、严重级别、修复建议
3. ✅ Comprehensive_Review_Report.md 已产出且包含 §1-§10 全部章节（按 Guidelines.md 大纲）
4. ✅ Improvement_Roadmap.md 已产出且短期项有明确责任人/期限
5. ✅ quality/README.md "历史轮次索引"已更新
6. ✅ 关键修复（严重级别）已分派为后续 PR/任务

---

## 🚧 已知限制

- **没有自动化测试基础**：AICC 主要是文档与脚本，缺少真正的"运行测试"机制
- **新用户旅程模拟有偏差**：主代理已知所有上下文，无法 100% 模拟新用户
- **跨平台覆盖不全**：仅在 Linux 测试，macOS/Windows 行为未独立验证
- **真实案例样本少**：dev/real_case/ 只有 2 个案例，外推性有限

这些限制不影响本轮启动，但应在最终报告中说明。

---

## 🔗 相关文档

- [Framework_Review_Guidelines.md](../../Framework_Review_Guidelines.md) — 方法论
- [Start_Review.md](../../Start_Review.md) — 启动入口
- [README.md](../README.md) — audits/ 目录说明
- [`../../README.md`](../../README.md) — quality 体系总览（含完整文件索引）
- [`../../standards/BY_DOCUMENT_TYPE.md`](../../standards/BY_DOCUMENT_TYPE.md) — 按类型专项标准

---

**版本**：v1.0
**创建日期**：2026-04-25
**维护者**：本轮主审（Claude Opus 4.7）
