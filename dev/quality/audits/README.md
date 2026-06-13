# 审查归档目录 (audits/)

> **用途**：归档每次完整或专项审查的所有交付物
> **建立**：2026-04-25（v2.0 quality 体系补全时正式创建）

---

## 📁 目录结构与命名规范

审查归档支持**两种形式**，按本轮体量选择：

**形式 1 — 完整目录（Comprehensive / 多产物 round）**：每次审查对应一个独立子目录：

```
audits/
├── README.md                          ← 本文件（轮次索引）
├── YYYY-MM-DD_Version_Scope/          ← 完整审查目录
│   ├── Review_Plan.md                 ← 必需：本轮范围、视角、批次切分、退出条件
│   ├── Issue_Tracking.md              ← 必需：问题清单（PROJ-YYYYMMDD-XXX 编号）
│   ├── Progress_Tracking.md           ← 必需：阶段/任务进度
│   ├── Review_Log.md                  ← 必需：每日日志、关键决策
│   ├── Review_Checklist.md            ← 必需：复查清单
│   ├── Comprehensive_Review_Report.md ← 可选：完整审查报告
│   ├── Improvement_Roadmap.md         ← 可选：改进路线图
│   ├── Issue_Analysis.md              ← 可选：问题分类统计
│   └── [Topic]_Assessment_Report.md   ← 可选：专项评估报告
└── YYYY-MM-DD_<scope>.md              ← 形式 2：轻量单文档审查（loose-file）
```

**形式 2 — 轻量单文档（loose-file）**：单文档 / 单主题的轻量审查、健康检查、专项验证，**无需建目录**，直接落地为 `audits/YYYY-MM-DD_<scope>.md` 一个文件（自带 YAML frontmatter）。该文件即完整产物，不要求 5 件套。

### 命名规范

**完整目录**：`YYYY-MM-DD_Version_Scope`

| 字段 | 含义 | 示例 |
|---|---|---|
| YYYY-MM-DD | 审查启动日期 | 2026-04-25 |
| Version | 框架版本（含次要变体） | V3.0 / V3.x |
| Scope | 审查范围标签 | Comprehensive / Strategic / Component-tools / Security / Performance |

**轻量单文档**：`YYYY-MM-DD_<scope>.md`，其中 `<scope>` 用下划线连接的简明范围标签。

**示例**：
- `2026-04-25_V3.x_Comprehensive/` — 完整目录（全面审查）
- `2026-05-10_V3.0_Component-agents/` — 完整目录（agents 组件专项）
- `2026-05-18_dayflow_phase1_aicc_improvement_verification.md` — 轻量单文档（专项验证）

---

## 📋 创建新 round 的步骤

```bash
# 1. 创建目录
ROUND_DIR="dev/quality/audits/$(date +%Y-%m-%d)_V3.x_Comprehensive"
mkdir -p "$ROUND_DIR"

# 2. 初始化 5 件套（参考 Framework_Review_Guidelines.md §审查交付物清单）
touch "$ROUND_DIR"/Review_Plan.md
touch "$ROUND_DIR"/Issue_Tracking.md
touch "$ROUND_DIR"/Progress_Tracking.md
touch "$ROUND_DIR"/Review_Log.md
touch "$ROUND_DIR"/Review_Checklist.md
```

或使用 AICC 的 round 模板（位于 `templates/review/`，待后续生成）。

---

## 🗂️ 历史轮次索引

| 启动日期 | 范围 | 视角 | 形式 | 状态 | 链接 |
|---|---|---|---|---|---|
| 2026-04-25 | V3.x Comprehensive | A+B+C | 完整目录 | 已完成 | [`2026-04-25_V3.x_Comprehensive/`](./2026-04-25_V3.x_Comprehensive/) |
| 2026-05-05 | V3.x Followup Comprehensive | A+B+C | 完整目录 | 已完成 | [`2026-05-05_V3.x_Followup_Comprehensive/`](./2026-05-05_V3.x_Followup_Comprehensive/) |
| 2026-05-12 | Framework dogfood 健康检查 | B/C | 轻量单文档 | 已完成 | [`2026-05-12_framework_dogfood/health_check_report.md`](./2026-05-12_framework_dogfood/health_check_report.md) |
| 2026-05-18 | Dayflow Phase1 AICC 改进验证 | B | 轻量单文档 | 已完成 | [`2026-05-18_dayflow_phase1_aicc_improvement_verification.md`](./2026-05-18_dayflow_phase1_aicc_improvement_verification.md) |

**先前的非规范化审查档案（已归档，不在 internal 分支）**：

- V2.3 / V2.2 历史审查、`real_case/` 外部案例审查参考等档案，先于本规范化体系产生；其原 `dev/V2.3/`、`dev/V2.2/`、`dev/real_case/` 目录在 V3.0 交付后已归档/清理，**不在当前 internal 分支**，不强制迁移。

---

## 🔗 相关文档

- [`../README.md`](../README.md) — 质量体系总览与文档索引
- [`../Framework_Review_Guidelines.md`](../Framework_Review_Guidelines.md) — 审查方法论（含交付物完整清单与命名规范）
- [`../Start_Review.md`](../Start_Review.md) — 审查启动入口
- [`../Issue_Recording_Standard.md`](../Issue_Recording_Standard.md) — 问题记录格式
- [`../Progress_Tracking_Standard.md`](../Progress_Tracking_Standard.md) — 进度跟踪格式

---

**创建日期**：2026-04-25
**最后更新**：2026-06-13
**维护者**：Framework Team
**2026-06-13 变更**：补全四轮真实审查记录（04-25 / 05-05 / 05-12 / 05-18）并标记已完成；明确允许"轻量单文档 loose-file"归档形式；删除指向 dev/V2.3/V2.2/real_case 的失效引用（已归档，不在 internal 分支）。
