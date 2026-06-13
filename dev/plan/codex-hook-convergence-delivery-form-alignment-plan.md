---
title: Codex hook 机制收敛与交付形态对齐方案
summary: 记录 Codex v0.117 引入与 Claude Code 同构的 lifecycle hooks 后，对 AICC 已交付物的影响盘点与对齐实施。核心结论是把原"2 强制 + 1 顾问降级"的交付模型收敛为"2 强制（插件 + Codex/.codex）+ 1 源"，并完成代码、用户文档、规格矩阵、回归测试四处对齐。作为 plan-review 自审方案（Doc B）Codex 落点的前置基础。
keywords: aicc | codex | hooks | enforcement | delivery-form | convergence | projection
scope: AICC 框架交付形态（插件 / Codex 扁平包）的强制层一致性
related_files: plugin/build/codex_projection.py | plugin/build/test_codex_projection.py | plugin/README.md | plugin/hooks/hooks.json | dev/plan/done/plugin/03-execution-spec.md | dev/plan/done/plugin/01-plugin-architecture-and-enforcement.md | dev/plan/lingotrace-active-plan-self-review-absorption-plan.md
dependencies: dev/plan/done/plugin/01-plugin-architecture-and-enforcement.md | dev/plan/done/plugin/03-execution-spec.md
verified_at: 2026-06-13
status: done（交付形态对齐已实施并验证，2026-06-13；保留为 Doc B 前置基础，待 plan-review 落地后归档）
---

# Codex hook 机制收敛与交付形态对齐方案

状态：Done（代码 / 用户文档 / 回归测试已落地并验证；规格档案已加更正横幅）
创建日期：2026-06-13
最后更新日期：2026-06-13
来源：Codex v0.117.0 新增 lifecycle hooks 的官网查证

---

## 0. 文档定位

本文档是一次**已交付物的事实对齐**记录：Codex 在 v0.117.0 引入了与 Claude Code 同构的 lifecycle hooks，推翻了 AICC 插件改造期"Codex 无 hooks、强制层退化为建议级"的设计前提。本文盘点受影响的已交付物、给出"降级矩阵 → 收敛矩阵"的反转，并记录四处对齐的实施与验证。

它与 [LingoTrace 方案自审核协议吸收分析](./lingotrace-active-plan-self-review-absorption-plan.md)（下称 **Doc B**）是**两条有序工作流**：本文（**Doc A**）对齐已 shipped 的交付形态基础设施，是 Doc B 中 plan-review 自审门在 Codex 形态落地的**前置依赖**——只有当 Codex 的 `.codex/` 强制包为真且被规格承认，Doc B 的 `plan_done_without_review` 硬门才能"在 Codex 强制而非降级"。**实施顺序：先 A 后 B。**

本文档属于框架开发元数据，仅存在于 `internal` 分支 `dev/plan/`，不进入 `dev` / `master` 用户面分支。

---

## 1. 查证结论（官方文档）

Codex 自 **v0.117.0** 起支持 lifecycle hooks，与 Claude Code **逐字段同构**：

- **事件**：`SessionStart` / `PreToolUse` / `PermissionRequest` / `PostToolUse` / `UserPromptSubmit` / `Stop` 等，覆盖 AICC 在用的 `SessionStart` / `PreToolUse` / `PostToolUse`。
- **stdin**：`tool_name` / `tool_input.command` / `cwd` / `hook_event_name`——与 `_aicc_common.read_event()` 读取的字段完全一致。
- **deny 输出信封**：`hookSpecificOutput.permissionDecision(+Reason)`（或 exit 2 + stderr）——与 `common.pretooluse_decision()` 产出完全一致。
- **env**：提供 `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` **兼容别名**。
- **配置**：`hooks.json` 或 `config.toml` 内联 `[hooks]`，`~/.codex/`（用户级）或 `<repo>/.codex/`（项目级，需 `/hooks` 信任）。
- **关键限制**：官方自承 hook 拦截是 "a guardrail rather than a complete enforcement boundary"，且部分 shell 路径拦截有 gap——故 `git commit` 门不能宣称完全强制。

**推论**：AICC 的 hook 脚本在 I/O 层**本已 Codex 兼容**；原"无 hook → 全面降级"前提失效，且对齐成本低（脚本无须重写，只需投影 + 规格纠正 + 测试）。

来源：`developers.openai.com/codex/hooks`、`developers.openai.com/codex/config-advanced`、`github.com/openai/codex/issues/14882`。

---

## 2. 受影响已交付物盘点（A/B/C 分类）

| 落点 | 文件 | 类别 | 处置 |
|---|---|---|---|
| Codex 投影脚本 | `plugin/build/codex_projection.py` | C 代码 | **已改**：额外产出自包含 `.codex/` 强制包（commit `c8d3f46`，dev） |
| 用户面 README | `plugin/README.md` §Codex package | A 活文档（用户面） | **已改**：删除"degraded to advisory / Codex gets recommendations"，改为可安装强制包 + 顾问兜底（commit `b08638b`，dev） |
| 回归测试缺口 | （无） | C 测试 | **已补**：`plugin/build/test_codex_projection.py`——结构 + 措辞 + deny 强制（commit `b08638b`，dev） |
| 架构降级矩阵 | `dev/plan/done/plugin/01-...md` §3.4 | A 活规格（已归档） | **已加更正横幅**：降级矩阵 → 收敛矩阵；正文保留历史原貌 |
| 路线图 P4 + 风险行 | `dev/plan/done/plugin/02-...md` L54/L71 | A 活规格（已归档） | **已加更正横幅** |
| 执行蓝图 §7 + P4 验收 | `dev/plan/done/plugin/03-...md` L250-256/L283 | A 活规格（已归档） | **已加更正横幅** |
| 平台无关检查器/脚本 | `doc_health` / `git_safety` / hook 脚本 | C 代码 | **无须改**：契约同构，Codex 兼容（仅由投影搬运） |
| generation_plan 缺口记录、BUILD_NOTES | done 区 | B 历史档案 | **不改**：保留为当时状态 |

**对"是否需要更新已实现功能"的判定**：shipped **代码**仅 `codex_projection.py` 一处受影响且已修复并验证；其余功能代码平台无关、无须改。真正的"更新"是**用户文档 + 内部规格 + 测试**三类一致性对齐——属规格与测试对齐，非新功能开发。

---

## 3. 核心反转：降级矩阵 → 收敛矩阵

插件改造期（`01` §3.4）把交付能力刻成"主形态强制 / 次形态建议级"的**降级矩阵**。Codex 获得同构 hooks 后，该框架过时，应读作**收敛矩阵**：

| 能力 | Claude Code 插件 | Codex（安装 `.codex/` 包） | 退路 |
|---|---|---|---|
| commit 门禁 | `PreToolUse` deny（强制） | `PreToolUse` deny（**强制**，同脚本） | `bin/aicc-*` 顾问兜底（shell gap） |
| 危险 Git 拦截 | `PreToolUse` deny | `PreToolUse` deny（**强制**） | 同上 |
| 上下文注入 | `SessionStart` 自动 | `SessionStart` 自动（健康快照） | `AGENTS.md` 静态索引 |
| 审计遥测 | `PostToolUse` | `PostToolUse`（fail-open） | — |

即交付模型从"**2 强制 + 1 顾问降级**"收敛为"**2 强制（插件 + Codex/.codex）+ 1 源（SSOT）**"。顾问 CLI 从"Codex 的唯一手段"降为"任一形态在 hook 拦截 gap 处的兜底"。

---

## 4. 实施项与状态

- [x] **T1 代码**：`codex_projection.py` 产出自包含 `dist/codex/.codex/`（`hooks.json` + 原样 hook 脚本 + `scripts/py` 依赖 + `settings.json`）。dev `c8d3f46`。
- [x] **T2 用户文档**：`plugin/README.md` §Codex package 改写。dev `b08638b`。
- [x] **T3 回归测试**：`plugin/build/test_codex_projection.py`——断言 `.codex/` 结构、`hooks.json` 事件/匹配器、脚本与依赖齐全、`AGENTS.md` 不再含 "no hooks/advisory mode"，并以 `CLAUDE_PLUGIN_ROOT` 未设跑投影脚本验证 force-push/hard-reset 被 deny、green 静默。通过；lint clean。dev `b08638b`。
- [x] **T4 规格对齐**：对 `01`/`02`/`03` 三份已归档规格在 stale 断言处加**日期更正横幅**（降级 → 收敛），指向本文；不改写历史正文。internal（本提交）。
- [x] **T5 概念矩阵**：收敛矩阵记录于 §3，作为后续引用真源。

**验证**：`python3 plugin/build/test_codex_projection.py` 全绿；`python3 plugin/build/build.py --codex` lint clean、产物含 `.codex/` 包；手测 project-local 安装（env 未设）下 force-push / hard-reset / 提交非法 dev_docs 均被 deny。

---

## 5. 与 Doc B（plan-review 自审）的关系与顺序

- **依赖方向**：Doc B 的 §7.6.2 `plan_done_without_review` 硬门，其 Codex 落点是"扩展 `.codex/` 包内 `pre_commit_gate` 的判定"。该包由**本文 T1 落地**，强制语义由**本文 T4 在规格中确立**。故 **A 是 B 的前置**。
- **收益**：契约同构使 plan-review 的硬门**一次实现（扩展共享 `pre_commit_gate`）即同时服务插件与 Codex**，无须为 Codex 另写降级路径——Doc B §7.6.5 已据此更正。
- **顺序**：先完成 A（本文，已落地）→ 再实施 B（plan-review，§12 待办，精确到 §7 各落点 diff 与 Py/JS 双实现 + fixture）。

---

## 6. 边界（不做）

- 不为 Gemini / Copilot 等其它平台适配——平台仍收敛为 Claude Code + Codex（沿用 `01` D4）。
- 不重写已归档规格正文（仅加更正横幅），遵循归档纪律。
- 不在本文实施 plan-review 自审门本身——那是 Doc B 的范围。
- 不依赖 Codex hook 对所有 shell 路径的完全拦截——保留 `bin/aicc-*` 顾问兜底。

---

## 7. 下一步

- [x] 完成 T1–T5（本文）。
- [x] 在 `dev/plan/README.md` 索引登记本文档。
- [ ] 实施 Doc B（plan-review 自审）：以本文确立的 Codex `.codex/` 强制包为前置，落地 `plan_done_without_review` 等门（见 Doc B §12）。
