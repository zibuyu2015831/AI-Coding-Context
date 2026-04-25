---
title: V3.x Comprehensive Review — Issue Tracking
summary: 本轮审查发现的全部问题清单，按 PROJ-YYYYMMDD-XXX 编号；含 Phase 0 基线快照阶段已识别的 F-1~F-8 与后续批次新增问题
keywords: issue-tracking | aicc | v3.x-review | findings
scope: 整轮审查的问题汇总单
verified_at: 2026-04-25
---

# V3.x Comprehensive Review — Issue Tracking

> **格式规范**：见 [`../../Issue_Recording_Standard.md`](../../Issue_Recording_Standard.md)
> **编号规则**：PROJ-YYYYMMDD-XXX；本轮统一前缀 `AICC-20260425-NNN`
> **状态**：🔴 待修复 / 🟡 修复中 / 🟢 已修复 / ⚪ 已确认非问题 / 🟣 已转化为长期改进

---

## 📊 统计概览

| 严重级别 | 数量 |
|---|---|
| 严重 | 0 |
| 主要 | 3 |
| 次要 | 5 |
| 建议 | 2 |
| **合计** | **10**（B0 基线 8 + B1 新增 2；后续批次将追加） |

| 视角分布 | 数量 |
|---|---|
| 视角 A（用户） | 2 |
| 视角 B（完整性） | 4 |
| 视角 C（dev 卫生） | 4 |

| 修复状态 | 数量 |
|---|---|
| 🟢 已修复（Phase 0 顺手处理） | 4 |
| 🔴 待修复 | 6 |

---

## 问题 ID: AICC-20260425-001

- **类型**: 文档问题（漂移）
- **严重级别**: 主要
- **优先级**: 中
- **归属视角**: B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/FRAMEWORK_CONTEXT.md` L17-L23 列出 V3.0 已完成功能为 11 项（001/003/012/013/016/017/018/019/004/005/006），但 `dev/V3.0/PROGRESS.md` L18 实际记录已完成为 11 项含 014（001/003/004/005/006/012/013/014/016/017/018），且 011（文档谬误修复工作流）也已标记 ✅。两份文档对"已完成"的定义和清单不一致。

### 影响范围

- 任何按 FRAMEWORK_CONTEXT 评估 V3.0 进度的 AI 或人类会得到错误结论
- 影响"V3.0 落地一致性"判断（R2 风险维度）

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`
- `dev/V3.0/PROGRESS.md`

### 具体位置

- 文件: `dev/FRAMEWORK_CONTEXT.md`, L11-L29 与 L702-L716（已完成清单）
- 文件: `dev/V3.0/PROGRESS.md`, L18-L41 与 L82-L88

### 建议修复方案

- 以 `PROGRESS.md` 为权威源
- 将 FRAMEWORK_CONTEXT 中的"已完成"清单更新为含 011/014
- 长期：约定 PROGRESS.md 为单一真相源（single source of truth），FRAMEWORK_CONTEXT 仅做"快照引用"

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-002

- **类型**: 文档问题（边界泄漏）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

Public 层文件中存在指向 `dev/` 路径的相对引用，违反 `.gitattributes export-ignore` 边界约束。这些引用在 GitHub release tarball / `git archive` 中将变为死链，对终端用户表现为"无法点击的链接"。

确认的真泄漏（视角 A 缺陷）：

1. `core/design_decisions.md` L256：`**V3.0 规划中** (详见 `dev/V3.0/`)`
2. `core/design_decisions.md` L492：`(设计记录详见框架开发分支中的 dev/V3.0/ 目录)`
3. `core/SUMMARY_FORMAT_SPEC.md` L403：`**反馈**: 如有疑问请在 dev/discussions/ 提出`
4. `agents/_progress/implementation_progress.md` L5：`(../../dev/V3.0/confirmed/001-ai-agent-library/implementation.md)` ← **相对路径直链 dev/，发布版必死**
5. `workflows/doc_error_fix_workflow.md` L507-509：3 处直链 `(../dev/V3.0/confirmed/011-doc-error-fix-workflow/...)` ← **同上，必死**

确认的故意保留（不算缺陷，但应明确标注）：

6. `CONTRIBUTING.md` L1202-1208 整段引用 dev/quality/ —— 因 CONTRIBUTING 面向贡献者（贡献者必然在 dev 分支工作），是合理的，但建议在该段开头明确标注"以下路径仅在 dev 分支可见"
7. `CONTRIBUTING.md` L904：`(详见开发分支中的 dev/V3.0/ 目录)` —— 与 #6 同性质

非引用类（shell `/dev/null`、`'dev/staging/prod'` 字符串等共 11 处）：均为假阳性，不计

### 影响范围

- 视角 A 下用户体验严重受损（链接断裂）
- agents/_progress/ 与 workflows/doc_error_fix_workflow.md 中的相对链接是最严重的，因为是 markdown 链接语法 `[text](path)`

### 主要文件路径

- `core/design_decisions.md`
- `core/SUMMARY_FORMAT_SPEC.md`
- `agents/_progress/implementation_progress.md`
- `workflows/doc_error_fix_workflow.md`

### 建议修复方案

**对于真泄漏 #4 #5（必死链接）**：

- 选项 A：改为指向 ADR 或工作流自身（如指向 `dev/architecture/decisions/004-...md` 的设计意图，但这仍在 dev/ 下，不彻底）
- 选项 B：移除链接，改为纯文字描述（"详见 dev 分支中的 011 设计文档"）
- 选项 C：将 011/001 等关键文档的"用户可见摘要"提取到 Public 层（如 `core/v3-features.md`），并指向该摘要
- **推荐 B**：成本最低，与 `core/design_decisions.md` 已采用的措辞一致

**对于 #1 #2 #3**：

- 已是文字描述非链接，影响小，但建议补充"（仅 dev 分支可见）"明示

**对于 #6 #7**：

- 在该段开头一次性声明"本节涉及框架开发流程，以下 dev/ 路径仅在 dev 分支可见"

### 审查阶段

B0 基线快照（B1 时将做穷尽性扫描确认完整性）

---

## 问题 ID: AICC-20260425-003

- **类型**: 设计问题（孤儿文件）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）+ A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

仓库根目录存在 `audit_metadata.py`（9KB），从命名看应属于 `tools/` 或 `dev/quality/` 下的审查辅助工具，但孤立在仓库根目录。视角 A 用户克隆仓库时会看到一个用途不明的 .py 文件。

### 主要文件路径

- `audit_metadata.py`（仓库根）

### 建议修复方案

- 阅读其内容判断真实用途
- 选项 A：迁入 `tools/py/`（若是通用工具）
- 选项 B：迁入 `dev/quality/`（若仅服务于审查工作流）
- 若无明确用途且无引用 → 删除

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-004

- **类型**: 文档问题（编码乱码）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/Issue_Recording_Standard.md` 末尾出现 `2025-12-18�更新`（U+FFFD 替换字符）；`dev/quality/Progress_Tracking_Standard.md` 末尾同类乱码 + 出现重复段落（恢复粘贴痕迹）。

### 修复

Phase 0 commit `3edfbe2` 中已直接修复。无遗留。

### 教训

- 编辑时如有断电/崩溃恢复，需检查文件末尾完整性
- 建议加入预提交 hook 检查 U+FFFD 字符

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-005

- **类型**: 设计问题（自相矛盾）
- **严重级别**: 主要
- **优先级**: 中
- **归属视角**: B（完整性）
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/Framework_Review_Guidelines.md` 在多处（L24-26 / L107 / L489-509）声明"跳过 dev/ 目录"，但同时在审查范围中包含 `dev/quality/audits/`、ADR 系统（位于 `dev/architecture/`）、复杂度仪表盘（位于 `dev/complexity/`）等 dev/ 下内容。政策与实际审查范围矛盾。

### 修复

Phase 0 commit `3edfbe2` 中重写为"审核视角分层"机制（A/B/C），统一三视角并存而非二元排除。

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-006

- **类型**: 设计问题（基础设施长期缺失）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: B+C
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/` 体系建立以来：

- `contexts/` 目录除 `_template.md` 外**实际为空**，但方法论文档反复声明应有 30+ 文档的 context
- `audits/` 目录在多处 SOP 中被引用为唯一归档位置，**物理上从未创建**
- 这两项使整套审查体系长期处于"理论可用、实操不可用"状态

### 修复

Phase 0 commit `3edfbe2` 中：

- 创建 `audits/` 目录及 README（命名规范、5 件套结构）
- 创建本轮 round 目录 `2026-04-25_V3.x_Comprehensive/`
- contexts/ 改为 v2.0 的"按需生成"策略（🔴 优先级独立 context、🟡 同类批审、⚪ 仅合规扫描），不再要求每个文件都有

### 教训

- 长期未创建的目录暗示"sop 写完就没人真的用"——应配合 dogfood 机制周期性触发使用

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-007

- **类型**: 文档问题（被引用但缺失）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/standards/BY_DOCUMENT_TYPE.md` 在多处被引用：

- `HOW_TO_GENERATE_CONTEXTS.md` L725、L282
- `standards/COMMON_STANDARDS.md` L268
- `standards/QUALITY_CHECKLIST.md` L171

但实际**文件不存在**。属于"标准被宣告但未实现"的设计漏洞。

### 修复

Phase 0 commit `3edfbe2` 中创建该文件，覆盖入口/core/workflows/agents/tools/templates/guides/config/ADR/quality 自身共 10 类专项标准。

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-008

- **类型**: 文档问题（编码乱码 + 末尾重复）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/PROGRESS.md` L290-L312 末尾存在数据损坏：

```
**最后更新**: 2026-04-22
发布
```
（"发布"是孤字，紧接一个未闭合的 ``` 代码块）

随后 L294-L312 整段重复了 `## 🔗 相关链接` / `## 状态图例` / `**最后更新**` 三个块。与 AICC-20260425-004 同性质（编辑事故残留）。

### 主要文件路径

- `dev/V3.0/PROGRESS.md`

### 具体位置

- L289-L312（含未闭合代码块和重复段落）

### 建议修复方案

- 删除 L290-L312 中的重复段落与孤字"发布"
- 保留单份"状态图例 / 最后更新"

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-009

- **类型**: 文档问题（dev/ 内部悬空引用）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/reference/commit_as_prompt_analysis.md` L699 引用 `dev/V3.0/pending/018-commit-guided-documentation.md`，但 `pending/` 目录已不存在（018 已迁移至 `dev/V3.0/confirmed/018-commit-guided-documentation/`）。属于历史迁移残留的悬空引用。

### 主要文件路径

- `dev/V3.0/reference/commit_as_prompt_analysis.md`

### 具体位置

- L699: `1. **创建优化点文档**: \`dev/V3.0/pending/018-commit-guided-documentation.md\``

### 建议修复方案

- 改为：`dev/V3.0/confirmed/018-commit-guided-documentation/`
- 或加注："（注：本文档为历史分析，018 已 confirmed，详见 confirmed/018-...）"

### 审查阶段

B1 R3 引用与边界扫描

---

## 问题 ID: AICC-20260425-010

- **类型**: 设计问题（文件位置疑似错误）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/archived/advanced-audit-report.md` 不符合该目录命名规范 `NNN-name.md`（其他归档项均为 `002-...md` / `007-...md` 等优化点编号）。`PROGRESS.md` 中列出的归档优化点为 5 项（002 / 007 / 008 / 009 / 015），不含 advanced-audit-report，说明这不是被归档的优化点，可能是一份审查报告被错放。

### 主要文件路径

- `dev/V3.0/archived/advanced-audit-report.md`

### 建议修复方案

- 阅读其内容判断真实属性
- 选项 A：迁入 `dev/V3.0/reference/`（若是分析报告）
- 选项 B：迁入 `dev/quality/audits/` 历史归档区（若是审查报告）
- 不应留在 archived/

### 审查阶段

B1 R3 引用与边界扫描（附带观察）

---

## 📈 后续批次将追加的问题段落

每个批次（B2-B7）执行后将在此追加问题，编号继续：AICC-20260425-011 起。

---

**版本**：v1.0
**创建日期**：2026-04-25
**最后更新**：2026-04-25（B0 基线快照完成）
