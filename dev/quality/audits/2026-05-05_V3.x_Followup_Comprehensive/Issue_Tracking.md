---
title: AICC V3.x Follow-up Comprehensive Review — Issue Tracking
summary: 本轮跟进复审发现的问题、回归失败项和需重判项汇总表，统一使用 AICC-20260505-XXX 编号。
keywords: issue-tracking | followup-review | regression | delta
scope: 2026-05-05 跟进复审的问题跟踪
verified_at: 2026-05-05
dependencies: dev/quality/Issue_Recording_Standard.md | dev/quality/audits/2026-04-25_V3.x_Comprehensive/Issue_Tracking.md | dev/quality/audits/2026-04-25_V3.x_Comprehensive/Review_Checklist.md
---

# AICC V3.x Follow-up Comprehensive Review — Issue Tracking

> 编号前缀：`AICC-20260505-NNN`
>
> 状态：`🔴 未闭合` / `🟡 验证中` / `🟢 已闭合` / `⚪ 需重判` / `🟣 转长期`

## 统计概览

| 维度 | 数量 |
|---|---|
| 总问题数 | 3 |
| 回归失败 | 1 |
| 新增问题 | 2 |
| 需重判 | 0 |
| 已闭合确认 | 34 |
| 转长期 | 0 |

## 使用规则

1. 本轮只记录三类事项：
   - 上轮问题在本轮复核中判定未闭合
   - 本轮发现的新问题
   - 上轮结论需要重判的问题
2. 如果上轮问题验证通过，必须登记到本文件的“已闭合确认”区域，不得只留在日志中。
3. 每条问题必须标注归属视角和来源批次。

## 已闭合确认

用于登记上轮问题的验证通过项，至少包含：`历史问题 ID`、`闭合日期`、`验证批次`、`验证命令/证据路径`、`验证人`。

| 历史问题 ID | 闭合日期 | 验证批次 | 验证命令/证据 | 验证人 | 备注 |
|---|---|---|---|---|---|
| `AICC-20260425-002` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；Public 层 `dev/` markdown 死链 grep 为空 | Codex | 未回归 |
| `AICC-20260425-003` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`audit_metadata.py` 不存在 | Codex | 未回归 |
| `AICC-20260425-010` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`010-cross-project-knowledge/senior_review_report.md` 存在 | Codex | 未回归 |
| `AICC-20260425-016` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；AI_RULES 标准路径抽检通过 | Codex | 未回归 |
| `AICC-20260425-022` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；confirmed 目录命名抽检通过 | Codex | 未回归 |
| `AICC-20260425-029` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；Public 层主流路径仍统一 | Codex | 未回归 |
| `AICC-20260425-032` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；主文档标准路径抽检通过 | Codex | 未回归 |
| `AICC-20260425-001` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`FRAMEWORK_CONTEXT` / `PROGRESS` 编号集合 diff 为空 | Codex | 未回归 |
| `AICC-20260425-011` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；V3.0 进度摘要与 SSOT 未漂移 | Codex | 未回归 |
| `AICC-20260425-012` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`PROGRESS` 自身未见集合矛盾 | Codex | 未回归 |
| `AICC-20260425-014` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；规划/已完成语义未回退 | Codex | 未回归 |
| `AICC-20260425-015` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`019` 单文件实体仍在 | Codex | 未回归 |
| `AICC-20260425-017` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`doc_health_checker` 双脚本与引用均存在 | Codex | 未回归 |
| `AICC-20260425-019` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；复杂度告警工作流与路由仍在 | Codex | 未回归 |
| `AICC-20260425-020` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；phantom 参数未回归 | Codex | 未回归 |
| `AICC-20260425-018` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；doc_error_fix 工作流测试路径与现状说明仍一致 | Codex | 未回归 |
| `AICC-20260425-021` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；complexity_scanner fallback 与直接运行验证通过 | Codex | 未回归 |
| `AICC-20260425-023` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；dev/quality README 索引口径抽检通过 | Codex | 未回归 |
| `AICC-20260425-024` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；过度承诺交付物条目未回归 | Codex | 未回归 |
| `AICC-20260425-025` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；contexts 按需生成措辞与目录现状一致 | Codex | 未回归 |
| `AICC-20260425-026` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；Phase 4 / 候选优化点诚实化仍在 | Codex | 未回归 |
| `AICC-20260425-028` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；quick_start 步骤结构与 frontmatter 校验通过 | Codex | 未回归 |
| `AICC-20260425-030` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；Public 层旧框架名 grep 为空 | Codex | 未回归 |
| `AICC-20260425-031` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；README 仍为 4 步入口 | Codex | 未回归 |
| `AICC-20260425-033` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；project_scanner 仍为 quick_start 主推荐 | Codex | 未回归 |
| `AICC-20260425-035` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；`aac_validator.js` JSDoc 头部仍在 | Codex | 未回归 |
| `AICC-20260425-004` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；两份标准文档末尾无乱码 | Codex | 未回归 |
| `AICC-20260425-005` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；Guidelines 三视角结构仍在 | Codex | 未回归 |
| `AICC-20260425-006` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；audits/、BY_DOCUMENT_TYPE、5 件套口径仍完整 | Codex | 未回归 |
| `AICC-20260425-007` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；BY_DOCUMENT_TYPE 相关引用仍正确 | Codex | 未回归 |
| `AICC-20260425-008` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；PROGRESS 末尾整洁无乱码 | Codex | 未回归 |
| `AICC-20260425-009` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；pending/018 悬空引用未回归 | Codex | 未回归 |
| `AICC-20260425-013` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；FRAMEWORK_CONTEXT 错路径未回归 | Codex | 未回归 |
| `AICC-20260425-027` | 2026-05-05 | B1 | `reports/B1_historical_issue_verification.md`；复杂度工作流 Public 提升仍在 | Codex | 未回归 |

## 转长期

用于登记经本轮确认后不在当前修复轮处理、但必须保留追踪的问题。

| 历史问题 ID / 新问题 ID | 原因 | 裁定依据 | 后续入口 |
|---|---|---|---|

## 待填模板

## 问题 ID: AICC-20260505-001

- **类型**: 设计问题（历史未闭合项持续存在）
- **严重级别**: 严重
- **优先级**: 高
- **关联任务**: 012-强制文档摘要机制
- **关联 ADR/Commit**: AICC-20260425-034
- **归属视角**: A+B
- **来源批次**: B1
- **关联历史问题**: AICC-20260425-034
- **状态**: ✅ 已修复

### 问题描述

上一轮 `AICC-20260425-034` 的未闭合问题已在本轮修复阶段完成闭合。此前存在的三类缺口均已收口：

- 轨道 A：Public 非模板文档缺少 frontmatter
- 轨道 B：已有 frontmatter 但字段不完整（如 `workflows/complexity_alert_workflow.md`）
- 轨道 C：模板文件与 `summary_validator --strict` 的口径冲突

当前按同口径复算（排除 `*_TEMPLATE*` 文件），Public 层 frontmatter 覆盖率已达到 `139 / 139 = 100%`。同时，`workflows/`、`guides/`、`agents/`、`templates/` 与 `config/CONFIG_TEMPLATE.md` 的 strict 校验均已通过。

### 影响范围

- `012-强制文档摘要机制` 已完成 dogfood 闭环
- `014`、`018` 等依赖 frontmatter 的能力已可在框架自身上应用
- 当前问题已从“系统性缺口”转为“修复完成后的维持与回归防御”

### 主要文件路径

- `workflows/`
- `guides/`
- `agents/`
- `config/`
- `templates/`

### 相关文件路径

- `AI_ENTRY_POINT.md`
- `README.md`
- `CONTRIBUTING.md`
- `core/SUMMARY_FORMAT_SPEC.md`
- `tools/py/summary_validator.py`
- `dev/quality/audits/2026-05-05_V3.x_Followup_Comprehensive/reports/B1_historical_issue_verification.md`

### 具体位置

- `workflows/path_a_first_generation.md:1`
- `guides/ai_rules_maintenance.md:1`
- `agents/README.md:1`
- `templates/AI_Coding_Context_TEMPLATE.md:1`
- `config/CONFIG_TEMPLATE.md:1`

### 复现步骤

1. 运行 Public 层 frontmatter 覆盖率统计脚本，确认当前覆盖率。
2. 运行 `python3 tools/py/summary_validator.py --dir workflows --recursive --strict`。
3. 运行 `python3 tools/py/summary_validator.py --dir guides --recursive --strict`。
4. 运行 `python3 tools/py/summary_validator.py --dir agents --recursive --strict`。
5. 运行 `python3 tools/py/summary_validator.py --dir templates --recursive --strict`。

### 证据

- `reports/B1_historical_issue_verification.md`
- `reports/B8_repair_verification.md`
- 同口径 Public 覆盖率：`139 / 139 = 100%`（排除 `*_TEMPLATE*`）
- `workflows/` 严格校验：`27 / 27` valid
- `guides/` 严格校验：`15 / 15` valid
- `agents/` 严格校验：`59 / 59` valid
- `templates/` 严格校验：`29 / 29` valid
- `config/CONFIG_TEMPLATE.md`：strict 校验通过

### 建议修复方案

- 修复已完成，后续重点转为防回归：
- 保持 `summary_validator.py --strict` 在 Public 层全目录的周期性复查
- 新增或修改 Public 文档时保持 frontmatter 与字段完整性
- 若未来调整模板语义，应同步校验规则与模板头部结构，避免再次漂移

### 审查阶段

B8 修复完成验证

## 问题 ID: AICC-20260505-003

- **类型**: 文档问题（入口链结构示意与实体不一致）
- **严重级别**: 次要
- **优先级**: 低
- **关联任务**: 无
- **关联 ADR/Commit**: 无
- **归属视角**: A+B
- **来源批次**: B3
- **关联历史问题**: 无
- **状态**: ✅ 已修复

### 问题描述

`README.md` 现已将 `config/user_config.md` 标注为“首次运行创建”，与 `config/README.md` 的运行时语义一致。本问题已修复。

### 影响范围

- 当前入口层描述与仓库实体/运行时语义一致
- 新用户不会再误判 `user_config.md` 是否随仓库分发

### 主要文件路径

- `README.md`

### 相关文件路径

- `config/README.md`
- `config/CONFIG_TEMPLATE.md`
- `config/.gitignore`
- `dev/quality/audits/2026-05-05_V3.x_Followup_Comprehensive/reports/B3_entry_route_replay.md`

### 具体位置

- `README.md:210-214`
- `config/README.md:25-48`

### 复现步骤

1. 查看 `README.md` 的 `config/` 目录结构示意。
2. 列出仓库中的 `config/` 实际文件。
3. 对照 `config/README.md` 中关于 `user_config.md` 的生成语义。

### 证据

- `reports/B3_entry_route_replay.md`
- `reports/B8_repair_verification.md`
- `find config -maxdepth 1 -type f | sort`
- `README.md:210-214`
- `config/README.md:25-48`

### 建议修复方案

- 已完成：README 结构示意中的 `user_config.md` 已改为“首次运行创建，不提交到 Git”

### 审查阶段

B8 修复完成验证

## 问题 ID: AICC-20260505-002

- **类型**: 文档问题（残留编码乱码）
- **严重级别**: 次要
- **优先级**: 低
- **关联任务**: 无
- **关联 ADR/Commit**: 无
- **归属视角**: C
- **来源批次**: B1
- **关联历史问题**: 无
- **状态**: ✅ 已修复

### 问题描述

`dev/quality/HOW_TO_GENERATE_CONTEXTS.md` 中的两处乱码标题已恢复为正常标题文本，本问题已修复。

### 影响范围

- `dev/quality` 文档卫生度已恢复
- 当前未发现 `HOW_TO_GENERATE_CONTEXTS.md` 残留 `U+FFFD`

### 主要文件路径

- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md`

### 相关文件路径

- `dev/quality/Issue_Recording_Standard.md`
- `dev/quality/Progress_Tracking_Standard.md`
- `dev/quality/audits/2026-05-05_V3.x_Followup_Comprehensive/reports/B1_historical_issue_verification.md`

### 具体位置

- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md:33`
- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md:260`

### 复现步骤

1. 执行 `rg -n "�" dev/quality --glob '*.md' -g '!dev/quality/audits/**'`。
2. 确认结果为空；历史审计目录中的旧证据引用不计入本问题验收范围。

### 证据

- `reports/B1_historical_issue_verification.md`
- `reports/B8_repair_verification.md`
- `rg -n "�" dev/quality --glob '*.md' -g '!dev/quality/audits/**'` 结果为空
- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md:33`：`## 🤖 AI 使用指南`
- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md:260`：`## 🔄 批量生成工作流`

### 建议修复方案

- 已完成：乱码标题恢复为正常 Markdown 标题文本，且 `dev/quality/*.md` 重新扫描未见新的 `U+FFFD`

### 审查阶段

B8 修复完成验证

## 待填模板

## 问题 ID: AICC-20260505-XXX

- **类型**: [文档问题/设计问题/集成问题/安全问题/...]
- **严重级别**: [严重/主要/次要/建议]
- **优先级**: [高/中/低]
- **关联任务**: [任务编号，如不适用则填 无]
- **关联 ADR/Commit**: [ADR 编号或 Commit Hash，如不适用则填 无]
- **归属视角**: [A/B/C]
- **来源批次**: [B1/B2/B3/B4/B5]
- **关联历史问题**: [如 AICC-20260425-028；无则填 无]
- **状态**: [🔴/🟡/🟢/⚪/🟣]

### 问题描述

[描述当前问题或重判原因]

### 影响范围

[描述受影响的用户路径、文档、脚本或边界]

### 主要文件路径

- `[path]`

### 相关文件路径

- `[path]`

### 具体位置

- `[文件:行号/章节]`

### 复现步骤

1. [步骤一]
2. [步骤二]

### 证据

- [命令输出 / 文件引用 / 对照依据]

### 建议修复方案

[建议如何闭合]

### 审查阶段

[本轮批次]
