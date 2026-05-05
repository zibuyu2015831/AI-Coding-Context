---
title: AICC V3.x Follow-up Comprehensive Review — Round Plan
summary: 基于 2026-04-25 综合审查结果的跟进复审方案，补齐证据链目录、差异基线、关键工作流回归、用户门禁与三视角复核要求。
keywords: followup-review | comprehensive | three-views | remediation | delta-audit
scope: 整个 AICC 框架的跟进复审（Public + dev/）
verified_at: 2026-05-05
dependencies: dev/quality/README.md | dev/quality/Framework_Review_Guidelines.md | dev/quality/Issue_Recording_Standard.md | dev/quality/Progress_Tracking_Standard.md | dev/quality/standards/COMMON_STANDARDS.md | dev/quality/standards/QUALITY_CHECKLIST.md | dev/quality/standards/BY_DOCUMENT_TYPE.md | dev/quality/audits/2026-04-25_V3.x_Comprehensive/Review_Plan.md | dev/quality/audits/2026-04-25_V3.x_Comprehensive/Issue_Tracking.md | dev/quality/audits/2026-04-25_V3.x_Comprehensive/Review_Checklist.md
---

# AICC V3.x Follow-up Comprehensive Review — Round Plan

## 元信息

| 字段 | 值 |
|---|---|
| 启动日期 | 2026-05-05 |
| 审查轮次 | `2026-05-05_V3.x_Followup_Comprehensive` |
| 审查类型 | Follow-up Comprehensive |
| 审核视角 | A 用户视角 + B 完整性视角 + C dev/ 卫生视角 |
| 基线轮次 | `2026-04-25_V3.x_Comprehensive` |
| 代码快照 | `19bd9ea7c117af8bf038d9a3a726b39cbbeda7c1` |
| 差异基线 | `2026-04-25` 轮次工件 + 当前 `HEAD` + 当前工作区未提交变更 |
| 当前工作区状态 | 存在未跟踪目录 `dev/plan/`，视为本轮增量差异的一部分进行分类 |
| SSOT 提示 | V3.0 功能状态以 `dev/V3.0/PROGRESS.md` 为准；本计划不写死完成项数量 |

## 审查目标

1. 复核上一轮综合审查全部问题，形成完整的闭合状态表；`严重/主要` 优先，`次要/建议` 不遗漏。
2. 核查 2026-04-25 之后的增量变化，避免“旧报告已过时”。
3. 重新演练关键用户路径和关键工作流，确认高风险问题是否真正影响当前版本。
4. 用三视角重新验证 Public/dev 边界、文档一致性和 dev/ 自身卫生。
5. 产出带证据链和用户裁决门禁的闭环工件，而不是重复生成一份静态大报告。

## 审查策略

本轮不是从零开始的首轮全量审查，而是“上一轮问题闭合验证 + 增量差异审查 + 高风险路径回归”三合一方案。

优先级顺序：

1. 上一轮 `严重` 和 `主要` 问题
2. 用户主路径和关键工作流
3. Public → dev/ 边界与 SSOT 漂移
4. 批量合规扫描
5. dev/ 卫生与新增内容分类
6. 上一轮 `次要/建议` 问题的闭合归档

## 证据链目录

除 5 件套外，本轮还使用以下目录和文件作为证据锚点：

```text
2026-05-05_V3.x_Followup_Comprehensive/
├── _meta.md
├── _round_decisions.md
├── reports/
├── questions/
├── clarifications/
└── fix_plans/
```

规则：

- `reports/`：子代理或主会话生成的批次审查报告。
- `questions/`：待澄清问题与合并问题单。
- `clarifications/`：用户裁决或补充说明。
- `_round_decisions.md`：本轮统一裁定，作为是否启动修复轮的共识锚点。
- `fix_plans/`：只有确认进入修复执行轮时才创建具体计划。

## 视角矩阵

| 检查对象 | A 用户 | B 完整性 | C dev 卫生 |
|---|:-:|:-:|:-:|
| `README.md` / `AI_ENTRY_POINT.md` / `CONTRIBUTING.md` | ✅ | ✅ | ⏭️ |
| `core/` 顶层规范 | ✅ | ✅ | ⏭️ |
| `guides/` / `templates/` / `workflows/` 关键文档 | ✅ | ✅ | ⏭️ |
| `tools/README.md` 与工具对外承诺 | ✅ | ✅ | ⏭️ |
| `tools/py/` / `tools/js/` 脚本合规 | ✅ | ✅ | ⏭️ |
| `dev/FRAMEWORK_CONTEXT.md` / `dev/V3.0/PROGRESS.md` | ⏭️ | ✅ | ✅ |
| `dev/quality/` 与 `dev/architecture/` | ⏭️ | ✅ | ✅ |
| `dev/plan/` 与其他新增 dev-only 内容 | ⏭️ | ✅ | ✅ |

## 风险维度

| 风险 ID | 内容 | 主要视角 | 验证方式 |
|---|---|:-:|---|
| F1 | 上轮高优先级问题假闭合或未闭合 | A+B | 对照 `2026-04-25` Issue + Checklist 逐条复核 |
| F2 | 用户入口路径仍存在断链、错名、步骤漂移 | A | README → AI_ENTRY_POINT → quick_start 实走 |
| F3 | SSOT 文档再次漂移 | B+C | 交叉比对 `FRAMEWORK_CONTEXT`、`PROGRESS`、实体文件 |
| F4 | 工作流描述可读但不可执行 | A+B | 选定 3 条关键剧本做端到端推演 |
| F5 | 批量合规性退化 | A+B | frontmatter / 双脚本 / 零依赖扫描 |
| F6 | dev/ 新增内容无归属或污染边界 | B+C | 新增目录分类、引用边界与归档策略检查 |

## 批次切分

### B0：基线快照

- 读取本轮所需规范与上轮归档
- 记录当前 `git rev-parse HEAD`
- 记录当前 `git status --short`
- 记录顶层目录文件分布
- 建立本轮 5 件套工件和证据链目录
- 生成 `_meta.md` 初始状态
- 记录上一轮作为差异基线的来源文件与命令

退出条件：
- `Progress_Tracking.md` 已写入基线状态
- `Review_Log.md` 已记录启动事实
- `_meta.md` 已记录 `HEAD`、工作区状态、差异基线和目标范围

### B1：上轮问题闭合验证

目标：
- 全量复核 `2026-04-25` 轮次问题，按优先级分层推进
- 使用上轮 `Review_Checklist.md` 的复查命令作为基线，必要时补充当前命令
- 为每条问题形成闭合状态：`已闭合 / 未闭合 / 需重判 / 转长期`

范围：
- `AICC-20260425-028`
- `AICC-20260425-034`
- 其余所有 `主要` 级问题
- 所有 `次要/建议` 级问题的状态归档

产出：
- `reports/B1_historical_issue_verification.md`
- `questions/B1_merged.questions.md`（若存在裁决争议）
- 在本轮 `Issue_Tracking.md` 中登记 `回归失败`、`需重判`、`转长期`
- 在 `Issue_Tracking.md` 的“已闭合确认”区域登记验证通过项
- 在本轮 `Review_Checklist.md` 记录对应验证动作

### B2：增量差异分类

目标：
- 识别 2026-04-25 之后新增或变化的内容
- 判断是“正常演进”还是“新风险入口”

差异基线：

- 基线审计资产：`2026-04-25_V3.x_Comprehensive/`
- 基线代码事实：当前仓库 `HEAD`
- 当前工作区事实：`git status --short`
- 当前文件盘点：顶层与重点目录文件清单

验证方法：

- `git diff --name-status <baseline_commit>..HEAD`，若无可用基线 commit，则退化为“上轮问题涉及路径 + 当前工作区差异 + 新增目录清单”
- `find` / `rg --files` 生成目录快照

重点：
- `dev/plan/`
- `dev/quality/` 与 `dev/V3.0/` 下新文件
- 关键 Public 文档是否发生结构性修改

产出：
- 一份增量清单
- 每项增量的归属视角和处理建议
- `reports/B2_delta_inventory.md`

### B3：入口与主路径复演

目标：
- 从终端用户视角重新走一遍上手路径

剧本：
- `README.md`
- `AI_ENTRY_POINT.md`
- `guides/quick_start.md`

判定：
- 是否存在错名、跳步、互相矛盾、引用失效、不可执行步骤
- 是否仍需借助 `dev/` 知识才能跑通
- 是否满足 `COMMON_STANDARDS` 与入口类文档专项标准

产出：
- `reports/B3_user_journey.md`
- 必要时 `questions/B3_user_journey.questions.md`

### B4：关键工作流回归

目标：
- 对高风险工作流做轻量回归，而不是对全部工作流重跑

剧本：
- 首次生成：`path_a_first_generation.md`
- 文档健康检查：`path_b_health_check.md`
- 增量更新：`path_c_incremental_update.md`
- 特定任务分流：`path_d_specific_tasks.md`
- 生成主工作流：`generation_workflow.md`
- Commit-Guided：`commit_guided_update.md`
- Git 安全：`git_safety_workflow.md`
- 文档谬误修复：`doc_error_fix_workflow.md`
- 增量更新总工作流：`incremental_update_workflow.md`
- 文档健康检查总工作流：`document_health_check.md`

判定：
- 文档描述是否仍可走通
- 关键引用的工具、模板、规则文件是否存在
- Public 承诺和 dev 设计是否一致
- 关键工作流是否符合 `BY_DOCUMENT_TYPE.md` 的 workflows 标准

产出：
- `reports/B4_workflow_regression.md`
- `questions/B4_workflow.questions.md`（若需用户裁定）

### B5：批量合规扫描

目标：
- 快速扫出“上轮修了但本轮又退化”的系统性问题

扫描项：
- Markdown frontmatter 覆盖率
- `tools/py/` 与 `tools/js/` 文件对称性
- 零依赖红线
- Public 层 `dev/` 泄漏
- 关键目录引用断链
- 新增内容是否破坏双版本/零依赖/边界封闭

产出：
- 聚合发现
- 若无问题，也要记录“正面结论”
- `reports/B5_compliance_scan.md`

### B6：总结与收口

目标：
- 输出本轮结论，并在需要时形成修复轮输入

产出：
- 问题清单状态归档
- 下一轮执行建议
- 是否需要单独开修复轮次
- `_round_decisions.md`
- `clarifications/B6_final_clarifications.md`（如用户有最终裁决）

## 子代理委派策略

本轮允许使用子代理，但只委派并行、界限清晰的任务。

| 批次 | 是否委派 | 建议角色 | 任务 |
|---|---|---|---|
| B1 | 适合 | `explorer` | 对照上轮 Checklist 批量验证命令与状态 |
| B2 | 适合 | `explorer` | 枚举增量目录和文件变化 |
| B3 | 不建议 | 主会话 | 用户旅程需要连续判断，不适合切碎 |
| B4 | 适合 | `explorer` | 清点工作流依赖文件、模板和规则文件是否存在 |
| B5 | 适合 | `explorer` | 批量合规扫描 |
| B6 | 不建议 | 主会话 | 需要统一裁决 |

委派约束：

- 子代理只返回结果，不直接修改审计结论文件。
- 子代理默认只读；只有创建 `reports/`、`questions/` 这类本轮证据文件时才允许写入。
- 主会话负责把发现归并到 `Issue_Tracking.md` 和 `Progress_Tracking.md`。
- 如果子代理与上轮结论冲突，以当前代码与文档为准重判。
- 存在争议时，必须进入 `questions/` 与 `clarifications/`，不得在主会话口头跳过。

## 用户门禁

以下节点需要用户明确批准：

1. B1 结束后：确认“历史问题闭合口径”。
2. B2/B4 出现重判项时：确认是否接受新的事实结论。
3. B6 结束时：确认 `_round_decisions.md`，决定是否启动修复轮。

## 时间估算

| 批次 | 预估 |
|---|---|
| B0 基线快照 | 0.5 小时 |
| B1 上轮问题闭合验证 | 1.5-2.5 小时 |
| B2 增量差异分类 | 0.5-1 小时 |
| B3 入口与主路径复演 | 1-1.5 小时 |
| B4 关键工作流回归 | 1-2 小时 |
| B5 批量合规扫描 | 0.5-1 小时 |
| B6 总结与收口 | 0.5-1 小时 |
| 合计 | 4.5-9.5 小时 |

## 退出条件

1. `B0-B6` 全部有明确状态。
2. 上轮全部问题都已归类为 `已闭合 / 未闭合 / 需重判 / 转长期` 之一。
3. 本轮所有新增问题都已写入 `Issue_Tracking.md`。
4. `reports/`、`questions/`、`clarifications/`、`_round_decisions.md` 已形成最小证据链。
5. 本轮 `Review_Checklist.md` 已具备可执行复查项。
6. 已给出是否启动“修复执行轮”的明确建议。

## 已知限制

- 本轮是 follow-up round，不以重新穷尽全仓所有文档为目标。
- 新用户旅程模拟仍受现有上下文污染，只能尽量约束视角。
- 当前工作区存在未跟踪目录 `dev/plan/`，若其内容在审查中变化，结论可能受影响。
- 未运行需要外部依赖或网络的验证动作。

## 相关文档

- [dev/quality/README.md](../../README.md)
- [dev/quality/Framework_Review_Guidelines.md](../../Framework_Review_Guidelines.md)
- [dev/quality/Issue_Recording_Standard.md](../../Issue_Recording_Standard.md)
- [dev/quality/Progress_Tracking_Standard.md](../../Progress_Tracking_Standard.md)
- [2026-04-25 Review Plan](../2026-04-25_V3.x_Comprehensive/Review_Plan.md)
- [2026-04-25 Issue Tracking](../2026-04-25_V3.x_Comprehensive/Issue_Tracking.md)
- [2026-04-25 Verification Checklist](../2026-04-25_V3.x_Comprehensive/Review_Checklist.md)
