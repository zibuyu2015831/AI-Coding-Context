---
title: AICC → Claude Code Plugin 改造方案 — 总索引与决策
summary: 将 AICC 框架改造为单个 Claude Code Plugin（内含多 skill + subagents + hooks + tools）的完整方案。已吸收并取代 dev/plan/done/skill-migration。核心四原则：单 plugin 多 skill、hooks 强制执行层、迁移即收敛、所有 plugin 交付物使用英文。目标平台仅 Claude Code（主，全能力）与 Codex（次，退化为建议级）。已实施并交付：插件已合入 master（V3.0「conversion complete」P1.5→P5），master 同时保留 clone 用法；临时 plugin 分支完成后已删除。
keywords: aicc | plugin | claude-code | codex | skills | hooks | enforcement | convergence | english
scope: dev/plan/done/plugin 子项目根（已实施并交付，保留作规划档案）
related_files: ./01-plugin-architecture-and-enforcement.md | ./02-implementation-roadmap.md | ./03-execution-spec.md | ../skill-migration/README.md | ../../../../FRAMEWORK_REVIEW.md | ../../../../FRAMEWORK_REVIEW_II.md | ../../../../PLUGIN_BUILD_KICKOFF.md
dependencies: ../skill-migration/02-component-mapping.md
verified_at: 2026-06-13
status: done（已实施）
supersedes: dev/plan/done/skill-migration（整体吸收并更名）
---

# AICC → Claude Code Plugin 改造方案

> **状态：✅ 已实施并交付（shipped）** — 插件转换已于 V3.0 完成并合入 master（提交 P1.5→P5「conversion complete」），见 master 分支 `plugin/` 与 `plugin/MIGRATION.md`。以下为当时的规划记录，保留作开发档案；其“待执行”措辞为历史状态。

> **状态（历史）**：方案已定稿，等待在新会话中以 Claude Code `/goal` 一次性执行。
> **执行分支**：`plugin`（长期维护，与 `master` 并行；`master` 保留现有 clone 用法）。
> **启动指令**：根目录 [`PLUGIN_BUILD_KICKOFF.md`](../../../../PLUGIN_BUILD_KICKOFF.md)（复制到新会话即可启动）。

---

## 一、已锁定的决策（本轮用户确认）

| # | 决策 | 锁定值 | 来源 |
| --- | --- | --- | --- |
| D1 | 打包形态 | **单 plugin × 多 skill**（plugin 是容器，skill 是组件，非二选一） | 官方机制核验 + skill-migration 决策 #2 |
| D2 | 强制执行层 | **hooks 作为一等强制层**（合理且必要，用户确认） | 两份审查第一缺口 |
| D3 | 迁移策略 | **迁移即收敛**（用户确认）：未收敛的资产不进 plugin | FRAMEWORK_REVIEW_II §6 |
| D4 | 目标平台 | **仅 Claude Code（主，全能力）+ Codex（次，退化为建议级）**；不考虑 Gemini/Copilot 等其它平台 | 用户确认 |
| D5 | 文档语言 | **所有 plugin 交付物一律使用英文**（SKILL.md / description / references / hooks 注释 / plugin README 等），以获得最佳触发与执行效果 | 用户确认 |
| D6 | 分支策略 | 改造在 **`plugin` 分支**进行，长期维护；`master` 维持现有 clone 用法（即便效果略差） | 用户确认 |
| D7 | 与 skill-migration 关系 | **整体更名吸收**：本目录为单一真相源，skill-migration 标注 superseded | 用户确认 |

> 注：本方案为 D1–D7 的展开。skill-migration 已锁定的 12 项底层决策（短名 skill、无总入口、build-time copy、Python 主 JS 降级、真实资产为准等）仍然有效，见 `../skill-migration/README.md` §三，不重复。

---

## 二、为什么是 plugin（不是 skill，也不是继续 clone）

“skill vs plugin” 是伪二选一：**plugin 是分发容器，skill 是其中一种组件，一个 plugin 可打包任意多 skill + agents + hooks。**

```
能力载体        能否承载 AICC 全貌
单个 skill   ❌ 11 类工作流 + 20 角色 + 80 工具 + Git 安全，违反 500 行上限、丢失渐进披露与角色隔离
继续 clone   ❌ 200 文件污染用户仓库、手动粘贴入口、无强制层（两份审查批评的现状）
Plugin       ✅ 多 skill（渐进披露）+ subagents（角色）+ hooks（强制）+ bin（工具）+ settings（配置）
```

**体量越大，plugin 越占优**：渐进式披露让 SKILL.md 主体仅 200–300 行，把 6.3 万行散文降级为按需 Read 的 references，取代当前 811 行必读入口。这正是对审查“体量失控”根因的官方解法。

---

## 三、plugin 如何同时根治两份审查的全部根因

```
根因①「无反熵/无强制」 ─► hooks: PreToolUse commit 门禁（可 deny）+ 危险 Git 拦截
根因②「体量失控」      ─► 多 skill + 渐进披露 + 迁移即收敛（references 总量 ≤ 现状 50%）
根因③「规格-实现鸿沟」 ─► config → settings.json（真正生效）+ hook（真正执行）
根因④「手动注入摩擦」  ─► /plugin install 一次 + SessionStart 自动注入上下文
根因⑤「无遥测」        ─► PostToolUse 审计日志，为量化宣称补真实数据
```

> 一句话：plugin 是把 AICC 从“靠人读、靠 AI 自觉的文档系统”升级为“自动加载、系统强制的工程系统”的载体——落地两份审查 §7 的共同结论“把‘AI 应当遵守’变成‘系统保证执行’”。

---

## 四、目标平台与退化矩阵（D4）

| 能力 | Claude Code（主形态，全能力） | Codex（次形态，退化为建议级） |
| --- | --- | --- |
| skill 自动触发 | ✅ description 自动触发 + `/aicc:*` | ⚠️ flat 包：`aicc-*` 前缀，靠提示词/AGENTS.md 引导 |
| commit 强制门禁 | ✅ `PreToolUse` deny | ❌ 无 hooks → skill body 内“请先运行校验”（建议） |
| 上下文自动注入 | ✅ `SessionStart` | ❌ 用户手动触发入口 skill |
| 遥测审计 | ✅ `PostToolUse` | ❌ 无 |

**原则**：强制执行层是 Claude Code 主形态的差异化优势，**主设计不被 Codex 的能力上限拉低**；Codex 形态由 build-time 从同一套源生成 flat 包，明确标注“退化为建议级”。不为 Gemini/Copilot 等做任何适配。

---

## 五、文档导航

| 文档 | 主题 | 语言 | 优先级 |
| --- | --- | --- | --- |
| **README.md**（本文） | 决策、定位、退化矩阵、索引 | 中（规划） | ⭐⭐⭐ |
| [`01-plugin-architecture-and-enforcement.md`](./01-plugin-architecture-and-enforcement.md) | plugin 骨架、hooks 强制层设计、组件映射增量、配置重构 | 中（规划） | ⭐⭐⭐ |
| [`02-implementation-roadmap.md`](./02-implementation-roadmap.md) | 迁移即收敛路线、阶段门禁、收敛指标、风险回退 | 中（规划） | ⭐⭐ |
| [`03-execution-spec.md`](./03-execution-spec.md) | **一次性 goal 执行的逐文件蓝图**：skill 清单+英文 description、hooks.json、bin、收敛动作、验收清单 | **英（蓝图＝交付物语言）** | ⭐⭐⭐ |

> **语言约定**：规划/理由类文档（README/01/02）用中文便于人审；**执行蓝图（03）及一切 plugin 产物用英文（D5）**。执行者无论读到何种语言的规划，**产出物一律英文**。

---

## 六、状态与执行入口

| 字段 | 值 |
| --- | --- |
| 方向决策 | Plugin（D1–D7 已锁定） |
| 执行方式 | Claude Code `/goal`，一次性完成 |
| 启动指令 | 根目录 `PLUGIN_BUILD_KICKOFF.md`（复制即用） |
| 执行分支 | `plugin`（从 dev 谱系派生，含 dev/plan；长期维护） |
| master | ✅ 插件已合入 master（V3.0「conversion complete」）；上一行"维持现有 clone 用法"为规划期历史设想，已被实际交付取代 |
| 前置输入 | `FRAMEWORK_REVIEW.md`、`FRAMEWORK_REVIEW_II.md`、`skill-migration/*` |

**修订记录**

| 日期 | 内容 | 修订人 |
| --- | --- | --- |
| 2026-06-11 | 初版（plugin-conversion）：定向 plugin + hooks + 迁移即收敛 | 架构审查（AI 协作） |
| 2026-06-11 | 用户确认后定稿并更名为 `plugin`：锁定 D1–D7、平台收敛为 Claude Code+Codex、新增英文强制(D5)、新增 03 执行蓝图、产出 `/goal` 启动指令 | 架构审查（AI 协作） |
