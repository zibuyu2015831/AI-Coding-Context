# 审查归档目录 (audits/)

> **用途**：归档每次完整或专项审查的所有交付物
> **建立**：2026-04-25（v2.0 quality 体系补全时正式创建）

---

## 📁 目录结构与命名规范

每次审查（round）对应一个独立子目录：

```
audits/
├── README.md                          ← 本文件（轮次索引）
└── YYYY-MM-DD_Version_Scope/          ← 单轮审查目录
    ├── Review_Plan.md                 ← 必需：本轮范围、视角、批次切分、退出条件
    ├── Issue_Tracking.md              ← 必需：问题清单（PROJ-YYYYMMDD-XXX 编号）
    ├── Progress_Tracking.md           ← 必需：阶段/任务进度
    ├── Review_Log.md                  ← 必需：每日日志、关键决策
    ├── Review_Checklist.md            ← 必需：复查清单
    ├── Comprehensive_Review_Report.md ← 可选：完整审查报告
    ├── Improvement_Roadmap.md         ← 可选：改进路线图
    ├── Issue_Analysis.md              ← 可选：问题分类统计
    └── [Topic]_Assessment_Report.md   ← 可选：专项评估报告
```

### 命名规范

格式：`YYYY-MM-DD_Version_Scope`

| 字段 | 含义 | 示例 |
|---|---|---|
| YYYY-MM-DD | 审查启动日期 | 2026-04-25 |
| Version | 框架版本（含次要变体） | V3.0 / V3.x |
| Scope | 审查范围标签 | Comprehensive / Strategic / Component-tools / Security / Performance |

**示例**：
- `2026-04-25_V3.x_Comprehensive/` — 全面审查
- `2026-05-10_V3.0_Component-agents/` — agents 组件专项
- `2026-06-01_V3.0_Security/` — 安全专项

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

| 启动日期 | 范围 | 视角 | 状态 | 主要发现 | 链接 |
|---|---|---|---|---|---|
| 2026-04-25 | V3.x Comprehensive | A+B+C | 准备中 | (待启动) | (待创建) |

**先前的非规范化审查档案**：

- V2.3 历史审查：位于 `dev/V2.3/`（双 AI 评估 / Monorepo / 入口文档 / 智能工作流等专项）
- V2.2 历史审查：位于 `dev/V2.2/`（V2.2 综合审查）
- 真实案例审查：位于 `dev/real_case/case_002/quality_review/`（外部案例审查参考）

这些档案先于本规范化体系产生，未来不强制迁移，但应在 `quality/README.md` 中保留入口。

---

## 🔗 相关文档

- [`../README.md`](../README.md) — 质量体系总览与文档索引
- [`../Framework_Review_Guidelines.md`](../Framework_Review_Guidelines.md) — 审查方法论（含交付物完整清单与命名规范）
- [`../Start_Review.md`](../Start_Review.md) — 审查启动入口
- [`../Issue_Recording_Standard.md`](../Issue_Recording_Standard.md) — 问题记录格式
- [`../Progress_Tracking_Standard.md`](../Progress_Tracking_Standard.md) — 进度跟踪格式

---

**创建日期**：2026-04-25
**维护者**：Framework Team
