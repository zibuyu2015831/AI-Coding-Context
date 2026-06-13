---
title: AICC Skill 化 — 开放问题清单
summary: 记录在 brainstorm 与设计阶段未能解决、或需要外部验证才能闭环的所有问题。每条包含问题描述、提出背景、影响面、决策方、解决路径、紧迫度与状态。本文档将持续维护到所有问题闭环。
keywords: aicc | skill | open-questions | uncertainties | decision-log
scope: dev/plan/done/skill-migration 子项目（持续维护）
related_files: 01-feasibility-and-architecture.md | 02-component-mapping.md | 03-implementation-roadmap.md | 04-edge-cases-and-risks.md | README.md
dependencies: README.md
verified_at: 2026-04-26
---

# 05 — 开放问题清单

> **使用方法**：本清单是 brainstorm 阶段的"留白账本"。每条问题在闭环前都不可作为已确定决策使用。维护流程：
>
> 1. **新增**：发现新问题 → 在合适分组下追加，编号顺延（QXX）
> 2. **更新**：状态变化 → 修改 `状态` 字段，附决议日期
> 3. **闭环**：问题已解决 → 移到 §"已闭环问题"区，保留历史
> 4. **变更通知**：高紧迫度（H）问题状态变化时，需同步更新 `01-04` 文档对应条目

---

## 一、统计概览

| 紧迫度 | 数量 | 阻塞 Phase |
|---|---|---|
| **H 高** | 6 | Phase 0a-0b |
| **M 中** | 5 | Phase 0b-2 |
| **L 低** | 4 | Phase 3-5 |
| **合计** | 15 | — |

---

## 二、高紧迫度（H）—— Phase 0a 启动后、Phase 0b 前必须有结论

### Q1：plugin.json schema 与 Anthropic 当前版本约束

**问题**：当前查到的 `document-skills` 使用 `.claude-plugin/plugin.json`，但缺少官方 schema 文档。需明确所有必需 + 可选字段（name / version / description / author / homepage / dependencies / hooks_format / ...）。

**提出背景**：Phase 0 必须先建立 plugin.json，否则 plugin 无法被加载。

**影响面**：阻塞 Phase 0；如 schema 与本规划假设不一致，可能要重做骨架。

**决策方**：维护者 / Anthropic 官方文档调研

**解决路径**：
1. 阅读 Anthropic Claude Code plugin 官方文档（如有）
2. 反向工程 `document-skills/.claude-plugin/plugin.json` 与 superpowers 的 `package.json`
3. 直接试装一个最小 plugin.json，看 Claude Code 报错信息

**紧迫度**：H

**状态**：🔴 未解决（待 Phase 0 第 1 周）

---

### Q2：plugin 脚本调用主路径：`bin/` 是否可用，是否仍需 plugin root 环境变量

**问题**：每个 skill 需要调用 `scripts/py/*.py`。2026-05-12 复检后主方案调整为 `bin/` 包装命令（如 `aicc-project-scan`）优先，避免直接依赖 `${CLAUDE_PLUGIN_ROOT}`。但仍需验证 Claude Code plugin 的 `bin/` 是否稳定加入 Bash PATH；如果不可用，才需要确定 plugin root 环境变量或自定义 `AICC_PLUGIN_ROOT`。

**提出背景**：Phase 0b 的 `scripts-call-convention.md` 必须明确主路径与 fallback。

**影响面**：所有 11 个 skill 的脚本调用语法。

**决策方**：维护者 / 实测 Claude Code

**解决路径**：
1. 在测试 plugin 中创建 `bin/aicc-smoke-test`，确认 Bash 是否可直接执行
2. 若 `bin/` 可用，SKILL.md 统一调用包装命令
3. 若 `bin/` 不可用，再测试是否存在稳定 plugin root ENV
4. 兜底方案：要求用户/安装脚本设置 `AICC_PLUGIN_ROOT`

**紧迫度**：H

**状态**：🔴 未解决

---

### Q3：plugin 内 skill 跨目录引用是否允许（skill references → plugin 顶级 references）

**问题**：本规划假设每个 skill 可引用 plugin 顶级 `references/`（例如共享的 `references/security_rules.md`）。但 Anthropic 官方说"references 1 层深"——这是指目录深度，还是引用链深度？

**提出背景**：如果 Anthropic 禁止跨 skill 目录引用，plugin 顶级共享 references 就不可行，必须每个 skill 内部复制一份共享文件。

**影响面**：
- 影响 02-component-mapping §六（core/ → references/）
- 影响所有 skill 的 references/ 组织

**决策方**：维护者 / 实测

**解决路径**：
1. 看 document-skills 是否有跨 skill 引用案例（superpowers 的 brainstorming 的 `@graphviz-conventions.dot` 是同 skill 内引用，无参考价值）
2. 直接试装一个跨引用 plugin，观察 Claude 是否能 Read 到
3. 兜底方案：放弃顶级共享 references，每个 skill 内部复制（增加维护成本）

**紧迫度**：H

**状态**：🔴 未解决

---

### Q4：plugin 发布渠道选择

**问题**：plugin 装到用户机器有几种方式：
- (a) Anthropic 官方 marketplace（如 anthropic-agent-skills）
- (b) git URL 直接安装（`/plugin install https://github.com/.../aicc.git`）
- (c) 第三方 marketplace（如 superpowers 走的 claude-plugins-official）
- (d) 本地 path 安装（`/plugin install /path/to/aicc`）

**提出背景**：Phase 0 必须选定主分发渠道。

**影响面**：
- 用户安装体验
- CI/CD 流程
- 版本发布频率
- 是否需要 Anthropic 审核

**决策方**：维护者 + 业务方

**解决路径**：
1. 调研每种渠道的接入门槛与受众规模
2. MVP 阶段建议 (b) git URL（最灵活，无审核）+ (d) 本地 path（开发期）
3. 长期视用户量加入 (a) 或 (c)

**紧迫度**：H

**状态**：🔴 未解决

---

### Q5：skill 之间的互调用机制

**问题**：`init` Step 5.5 想委托给 `design-thinking`。三种实现：
- (a) 在 SKILL.md 内显式引导加载 `/aicc:design-thinking`
- (b) 调用 Subagent（development agent）
- (c) 内嵌简版

**提出背景**：本规划假设 (a) 可行，但未验证。如不行需走 (b) 或 (c)。

**影响面**：
- 决定 init 与 design-thinking、mutual-review 的关系
- 决定 systematic-review 与 mutual-review、doc-fallacy-fix 的关系
- 整体 skill 生态的可组合性

**决策方**：维护者 / 实测

**解决路径**：
1. Phase 0 第 1 周用 superpowers skills（如 brainstorming → writing-plans → executing-plans）观察是否实际链式调用
2. 直接在测试 skill 中尝试 invoke 另一个 skill
3. 如不可行，准备好 (b) (c) 回退方案文档

**紧迫度**：H

**状态**：🔴 未解决

---

## 三、中紧迫度（M）—— Phase 1-2 前需要解决

### Q6：plugin marketplace 政策与命名占用

**问题**：如未来选 marketplace 发布，`aicc` 这个 plugin 名是否已被占用？

**提出背景**：影响 plugin.json 的 name 字段。

**影响面**：如被占用，可能要改成 `aicc-framework` 或 `ai-coding-context`。

**决策方**：维护者

**解决路径**：
- MVP 不上 marketplace，先用 git URL 安装（git URL 不存在命名冲突）
- marketplace 上线时查重；如冲突，**plugin 名按以下优先级回退**：
  1. `aicc`（首选）
  2. `ai-coding-context`（保底）
  3. `aicc-framework`（次保底）
- **skill 前缀 `aicc-` 始终不变**（与 plugin name 解耦）
- 如最终选择非 `aicc` 的 plugin name，需更新 README §三决策表（# 5）+ 01 §4.1 plugin 目录名 + 02 §一映射表

**紧迫度**：M

**状态**：🟡 待 Phase 4

---

### Q7：plugin 自带 Python `requirements.txt` 是否被 Claude Code 自动安装

**问题**：复杂脚本（complexity_scanner、aac_validator）依赖第三方包。plugin 是否能在安装时自动 `pip install -r requirements.txt`？

**提出背景**：影响 4.4 风险（EC-4.4）。

**影响面**：用户首次使用某些 skill 时的体验。

**决策方**：维护者 / 实测

**解决路径**：
1. 调研 Anthropic plugin 的依赖管理机制
2. 兜底：在 SKILL.md 给出 `pip install xxx yyy` 提示用户手动装

**紧迫度**：M

**状态**：🟡 未解决

---

### Q8：skill 内调用 Subagent 时的命名冲突

**问题**：plugin 的 `agents/aicc-frontend-expert.md` 与用户已安装的其他 plugin 的 frontend-expert 是否会冲突？

**提出背景**：subagent 命名空间是否与 plugin 隔离尚不明确。

**影响面**：所有 development subagent 的命名。

**决策方**：维护者 / 实测

**解决路径**：用 `aicc-` 前缀（已在规划中），与其他 plugin 不冲突；如发现仍冲突，再加 namespace 标记。

**紧迫度**：M

**状态**：🟡 已部分缓解（前缀策略）

---

### Q9：core/workflows/templates/agents/tools → plugin 发布层同步策略

**问题**：clone 模式下 `core/`、`workflows/`、`templates/`、`agents/`、`tools/` 是源码；plugin 模式下 `plugin/references/`、`plugin/skills/*/references/`、`plugin/scripts/` 是发布层副本。如何避免漂移？

**提出背景**：双轨模式下 single source of truth 问题。2026-05-12 复检后不再推荐 symlink 作为 release 机制，改为 build-time copy。

**影响面**：
- 维护成本
- Windows / zip artifact / marketplace 兼容（symlink 不可靠）
- 引用完整性（skill 引用的文件必须存在）

**决策方**：维护者

**解决路径**：
- 本地开发可选 symlink，但不得进入 release artifact
- Phase 0b 准备 build 脚本，从真实源码目录 copy 到 `plugin/`
- 生成 `plugin-manifest.generated.json`，记录每个 skill 的 references/scripts/templates/agents 来源
- CI 校验 manifest 中所有目标存在，且 release artifact 不包含 `__pycache__/`、开发审计文件、测试缓存

**紧迫度**：M

**状态**：🟡 待 Phase 0b 设计

---

### Q10：SKILL.md 的 frontmatter 是否支持 keywords / scope 等扩展字段

**问题**：AICC 现有所有文档 frontmatter 都有 keywords / scope / dependencies 等字段（来自 SUMMARY_FORMAT_SPEC）。skill frontmatter 是否兼容？

**提出背景**：Anthropic 官方说 frontmatter 只要求 `name` + `description`，但**不禁止**额外字段。是否会影响 skill 加载？

**影响面**：
- skill metadata 的 token 占用
- 与 AICC 摘要规范的统一

**决策方**：维护者 / 实测

**解决路径**：
1. 试装一个 SKILL.md 带额外字段，观察加载行为
2. 如被忽略：保留 AICC 风格不影响
3. 如冲突：在 plugin 中省略额外字段，保留在 references 文件中

**紧迫度**：M

**状态**：🟡 未解决

---

### Q11：agents 真实资产归属待确认条目

**问题**：02-component-mapping 初版中部分 agent 名称与真实仓库不一致。当前真实 runtime agents 包括 `code_reviewer.md`、`security_auditor.md`、`test_engineer.md`、`performance_optimizer.md` 等；development agents 当前真实存在 4 个：`api_designer.md`、`architecture_analyst.md`、`database_designer.md`、`product_manager.md`。

**提出背景**：需查看现有 agent 内容才能精确归类，避免按计划虚构不存在的角色。

**影响面**：02 文档准确性。

**决策方**：维护者

**解决路径**：
1. Phase 0b 生成真实 agents 清单
2. 逐个 agent 阅读 frontmatter/正文，决定进入 plugin `agents/` 还是 skill references
3. 不存在的角色如确需补齐，另行立项为新增资产，不能作为迁移默认项

**紧迫度**：H

**状态**：🔴 待 Phase 0b 决定

---

## 四、低紧迫度（L）—— Phase 3+ 解决

### Q12：是否需要保留一个 `aicc-overview` skill 作为"显示菜单"用途

**问题**：用户装了 plugin 但不知道有什么能力。是否需要一个 skill 触发条件为"用户问 AICC 有什么功能"？

**提出背景**：EC-6.1（用户认知）。

**影响面**：plugin 总 skill 数；可能与其他 skill 抢触发权。

**决策方**：维护者（Phase 1 验收后基于用户反馈）

**解决路径**：
- MVP 不做
- Phase 3 末期评估：如用户反馈"找不到能力"频次高，则补
- description 写得极窄：`Use ONLY when the user explicitly asks "what AICC capabilities are available" or "show me the AICC menu"`

**紧迫度**：L

**状态**：🟢 待 Phase 3+ 评估

---

### Q13：clone 模式的最终弃用时间表

**问题**：clone 模式何时正式 deprecate？长期保留还是 N 个月后转 read-only？

**提出背景**：Phase 5 交付物之一。

**影响面**：用户预期 / 维护成本。

**决策方**：维护者 + 业务方

**解决路径**：
- Phase 5 启动前根据 plugin 模式覆盖率决定
- 当前默认值：长期保留（与"双轨"策略一致）

**紧迫度**：L

**状态**：🟢 待 Phase 5

---

### Q14：skill 国际化（中英双语）策略

**问题**：AICC 用户群体中文为主，但 Anthropic 官方推荐英文 description。是否同时维护两套 description？

**提出背景**：影响触发率（参考 EC-6.4）。

**影响面**：
- 维护成本翻倍
- description 字符限制（1024）可能不够双语

**决策方**：维护者

**解决路径**：
- description 用英文为主，关键词列表中混入中文核心词（"健康检查"、"互审"等）
- skill body 内提示用户用中文/英文都可
- baseline eval 必须有中英双语样本

**紧迫度**：L

**状态**：🟢 待 Phase 1 测试反馈

---

### Q15：plugin 测试方法（evaluation 体系）

**问题**：writing-skills 推荐 evaluation-driven development，但没给出具体工具。AICC 维护者用什么方式跑 baseline eval？

**提出背景**：Phase 1 起每个 skill 都需要 eval。

**影响面**：
- 测试工程化
- CI 集成

**决策方**：维护者

**解决路径**：
- Phase 0 调研现有方案：是否有 Anthropic 官方 eval runner？superpowers 是否有 testing-skills-with-subagents？
- 兜底：手工跑 eval 场景，记录在 `tests/<skill>/results.md`

**紧迫度**：L

**状态**：🟢 待 Phase 0 末期决定

---

## 五、已闭环问题区（保留历史）

> 此区放已经解决并移除追踪的问题。当前为空，所有问题待 Phase 0 启动后逐步解决。

_暂无_

---

## 六、问题维护流程

### 6.1 何时新增问题

- 实施过程中发现新的不确定性
- 复审发现规划中的隐含假设
- 用户反馈引出新边界条件

### 6.2 何时更新状态

| 旧状态 | 触发条件 | 新状态 |
|---|---|---|
| 🔴 未解决 | 决策方完成调研 | 🟡 已部分缓解 / 🟢 已确认方向 |
| 🟡 已部分缓解 | 决策落定 + 已写入 01-04 文档 | ✅ 已闭环（迁移到 §五） |
| 🟢 已确认方向 | 实施期落地完毕 | ✅ 已闭环 |

### 6.3 何时通知

- H 级问题状态变化 → 同步更新 README §三决策表 + 01-04 对应章节
- M 级问题状态变化 → 仅更新本文件
- L 级问题状态变化 → 仅更新本文件

---

## 七、本章小结

| 维度 | 数值 |
|---|---|
| 高紧迫度问题 | 5（Q1-Q5） |
| 中紧迫度问题 | 6（Q6-Q11） |
| 低紧迫度问题 | 4（Q12-Q15） |
| 已闭环 | 0 |
| 阻塞 Phase 0 启动的问题 | 5 个高紧迫度全部 |

**关键判断**：5 个高紧迫度问题（Q1-Q5）必须在 Phase 0 第 1 周完成调研，否则整个路线图无法启动。这是规划风险的核心所在；**建议 Phase 0 实际是 1 周调研 + 2 周搭建**，而非纯搭建。

---

**下一步**：
- 维护者复审本规划全部 6 份文档
- 决定是否启动 Phase 0
- 如启动，将 Q1-Q5 列为 Phase 0 第 1 周必交付项
