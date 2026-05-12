---
title: 复杂度告警工作流（剧本 4）
summary: AI 代理执行项目复杂度扫描、阈值判定、告警与决策建议的端到端 SOP；面向 005-complexity-dashboard 优化点的运行时调用入口
keywords: complexity | alert | scenario-4 | path-d | dogfood | aicc-v3
scope: AI 在用户项目中执行复杂度告警剧本时调用本工作流；亦适用于框架仓库自审（dogfood）
related_files: tools/py/complexity_scanner.py | tools/js/complexity_scanner.js | tools/py/report_generator.py | tools/js/report_generator.js
dependencies: workflows/path_d_specific_tasks.md | tools/README.md
verified_at: 2026-04-26
---

# 复杂度告警工作流（剧本 4）

> **路径分类**：path_d 特定任务 / 剧本 4
>
> **来源**：本工作流由 `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` 中的"实施产出 + 验证场景 A/B/C/D"提炼而来，转写为面向 AI 的运行时 SOP（去除"开发完成验证"语境）。

## 🎯 触发条件

满足以下之一时，AI 应启动本工作流：

- 用户显式调用：`@complexity` 或"扫描项目复杂度"、"生成复杂度报告"等指令
- `path_d_specific_tasks.md` 路由命中 `@complexity`
- 周期性自动触发：例如 pre-commit/post-commit Git Hook、CI 定时任务
- 用户在多次 commit 后询问"代码增长是否健康"

## 🛠️ 工具链调用顺序

本工作流依赖 V3.0 双脚本对称工具集（`tools/py/*.py` + `tools/js/*.js` 镜像）：

| 阶段 | 工具 | 职责 |
|---|---|---|
| 1. 数据采集 | `tools/py/complexity_scanner.py` 或 `.js` | 扫描代码、调用 git_diff_analyzer 与 git_inspector |
| 2. 报告产出 | `tools/py/report_generator.py` 或 `.js` | 把 JSON 数据渲染为 Markdown / HTML |
| 3. 通知发送 | `tools/py/notifier.py`（可选） | Slack / Email 告警 |

> **未实现**：原 005 设计提到的 `architecture_analyzer` 工具尚未实体化（见 AICC-20260425-026），本工作流不依赖它；后续若实施再追加。

## ⚙️ 配置文件查找规则

`complexity_scanner` 按以下 fallback 顺序探测配置（B3#021 引入）：

1. CLI 显式 `--config <path>` 指定（最高优先级）
2. `dev_docs/complexity/config.yaml`（**用户项目场景**：本工作流的默认目标位置）
3. `dev/complexity/config.yaml`（**框架自审 / dogfood 场景**）
4. 工具内置默认（`warning_threshold` / `critical_threshold` / `crisis_threshold`）

用户项目首次运行前应在 `dev_docs/complexity/config.yaml` 中定义阈值；若不存在，工具会以内置默认运行不会失败。

## 📋 标准操作流程

### 步骤 1 — 基础数据采集

```bash
# Python 优先（与 V3.0 默认）
python tools/py/complexity_scanner.py \
  --since "1 day ago" \
  --output dev_docs/complexity/data/$(date +%Y-%m-%d).json

# 或 Node.js 镜像
node tools/js/complexity_scanner.js \
  --since "1 day ago" \
  --output dev_docs/complexity/data/$(date +%Y-%m-%d).json
```

**产出**：JSON 数据，含五个分组：

- `code_size`：新增行数、总代码量、文件数、增长百分比
- `dependencies`：新增依赖、重复依赖、依赖深度
- `code_quality`：TODO/FIXME 计数、重复代码、质量评分
- `architecture`：核心文件变更、耦合度、领域边界评分
- `risk_assessment`：综合评分 + 风险列表

### 步骤 2 — 阈值与告警判定

`complexity_scanner` 内部已实现风险评级（`calculate_review_risk`）。AI 应读取 JSON 中 `risk_assessment.risks[]`，按严重级别归类：

| 级别 | 触发条件 | AI 响应 |
|---|---|---|
| 🟢 low | 无风险或仅 medium 风险 | 报告生成即可，不打扰用户 |
| 🟡 warning | TODO 增加超阈值、单文件大改 | 标注于报告，建议优化 |
| 🔴 critical | 危险函数（eval/exec/Function）出现 | 报告 + 立即提示用户 + 触发通知 |

### 步骤 3 — 报告产出

```bash
# Markdown 报告（必须）
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/$(date +%Y-%m-%d).json \
  --output dev_docs/complexity/reports/$(date +%Y-%m-%d).md \
  --format markdown

# HTML 仪表盘（可选，供人查看）
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/$(date +%Y-%m-%d).json \
  --template dev_docs/complexity/template.html \
  --output dev_docs/complexity/dashboard/dashboard.html \
  --format html
```

### 步骤 4 — 通知与决策建议

- 若级别 ≥ warning：调用 `tools/py/notifier.py`（按 config 中的 `review.notification.channels`）
- AI 应在对话中给出**具体行动建议**：
  - daily_growth 超标 → 建议拆分本次 commit 为多次小 commit
  - dependency_depth 超标 → 建议引入抽象层或重构
  - quality_score 走低 → 建议清 TODO / 减小文件
  - 危险函数出现 → 阻断流程，请用户人工确认

## 🚦 回归验证（修复后/部署后核对）

```bash
# 工具链能跑通端到端
python tools/py/complexity_scanner.py --since "1 day ago" --output /tmp/c.json && \
python tools/py/report_generator.py --data /tmp/c.json --output /tmp/c.md --format markdown && \
test -s /tmp/c.md && echo "✅ 剧本 4 端到端可演练"

# JS 镜像同样可跑通
node tools/js/complexity_scanner.js --since "1 day ago" --output /tmp/c2.json && \
node tools/js/report_generator.js --data /tmp/c2.json --output /tmp/c2.md --format markdown && \
test -s /tmp/c2.md && echo "✅ 双脚本对称通过"
```

## 🔗 相关文档

- 设计源：`dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md`（开发档案 / 验证记录）
- 优化点登记：`dev/V3.0/confirmed/005-complexity-dashboard.md`
- 路由入口：`workflows/path_d_specific_tasks.md` `@complexity` 章节
- 工具索引：`AI_ENTRY_POINT.md` "工具脚本标准" 段
- 框架自审 dogfood：`core/framework_spec.md` "标准产物路径（SSOT）" 章节

## 📌 设计与历史

- 来源：B3#027 修复（005 walkthrough → workflows/ Public 提升）
- 同步关闭：B3#019 端到端工作流缺失（剧本 4）
- frontmatter 角色：本文件作为 workflows/ 目录第 2 个带 frontmatter 的样板（与 B3#034 P1 联动）
