---
title: AICC Plugin 化改造方案 — 总索引与决策
summary: 在“审查发现 + Claude Code 官方能力核验 + 既有 skill-migration 规划”三者基础上，确定将 AICC 改造为单个 Claude Code Plugin（内含多 skill + subagents + hooks + tools）。本目录是对 skill-migration 规划的演进与超集：保留其已锁定的“单 plugin × 多 skill”架构，新增其缺失的【强制执行层（hooks）】与【迁移即收敛】两条主线。
keywords: aicc | plugin | claude-code | skills | hooks | enforcement | migration
scope: dev/plan/plugin-conversion 子项目根（规划阶段，分支 plugin-conversion）
related_files: ./01-plugin-architecture-and-enforcement.md | ./02-implementation-roadmap.md | ../skill-migration/README.md | ../../../FRAMEWORK_REVIEW.md | ../../../FRAMEWORK_REVIEW_II.md
dependencies: ../skill-migration/01-feasibility-and-architecture.md | ../skill-migration/02-component-mapping.md
verified_at: 2026-06-11
status: 规划中（决策已定向 plugin → 待复审立项）
supersedes: dev/plan/skill-migration（架构决策吸收并扩展，非推翻）
---

# AICC Plugin 化改造方案

> **当前阶段**：方向决策已定（**Plugin**），等待复审立项。**尚未进入实施**。
> **分支**：`plugin-conversion`（本方案全部工作在此分支推进，不在 `dev` / `master` 上进行）。
> **触发**：两份框架审查（`FRAMEWORK_REVIEW.md` / `FRAMEWORK_REVIEW_II.md`）一致指出 AICC 的三大结构性缺口——**无强制执行层、手动注入摩擦、体量失控**；用户据此重新评估“skill 化”是否应升级为“plugin 化”。

---

## 一、核心结论：不是“skill vs plugin”，而是“plugin 内含 skill”

用户的问题“改造成 skill 还是 plugin 更合适”预设了二者互斥。经对 Claude Code 官方机制核验，**这是一个伪二选一**：

> **Plugin 是分发与打包的容器；skill / subagent / hook / MCP 是容器内的组件类型。一个 plugin 可以打包任意多个 skill。**

| 概念 | 角色 | 能否承载 AICC 全貌 |
| --- | --- | --- |
| **单个 skill** | 一个 SKILL.md + 可选 references/scripts，由 description 触发 | ❌ 不可能。AICC 有 11 类工作流、约 20 个角色、80 个工具脚本、Git 安全、配置系统——塞进一个 skill 既违反 500 行上限，也丢失渐进式披露与角色隔离 |
| **Plugin（内含多 skill + agents + hooks + bin）** | 版本化、可经 marketplace/git 一键安装的发布单元 | ✅ 唯一能承载者。每条工作流 = 1 个 skill（渐进式披露），角色 = subagents，工具 = bin/scripts，**强制执行 = hooks** |

**因此本方案的结论是：改造为 Plugin。** 而且——**体量越大，plugin 的优势越强**：plugin + 渐进式披露正是“体量管理”的官方机制（SKILL.md 主体 200–300 行，6 万行语料降级为按需 Read 的 references，取代当前 811 行必读入口）。

### 1.1 与既有 `skill-migration` 规划的关系

**关键澄清**：`dev/plan/skill-migration/` 名为“skill 化”，但其**锁定决策 #2 实为“单 plugin × 多扁平 skill”**——它本质上**早已是一份 plugin 规划**，只是命名误导，正是这个命名引发了用户本次的二选一困惑。

因此本方案**不推翻、而是吸收并扩展** skill-migration：

- ✅ **保留**其已锁定的 12 项架构决策（单 plugin、短名多 skill、无总入口、build-time copy、Python 主 JS 降级、真实资产为准等）——这些经核验仍然成立，不重复论证（详见 `../skill-migration/README.md` §三）。
- ➕ **新增**其缺失的两条主线（见下）。
- 🔁 **更名**整个工作项：`skill-migration` → `plugin-conversion`，消除“skill vs plugin”的概念混淆。skill-migration 目录标注为“已被本方案吸收”，作为历史输入保留。

### 1.2 本方案相对 skill-migration 的两条新增主线

两份审查的最高优先级缺口，skill-migration 规划**均未实质解决**：

| 缺口（两份审查共识） | skill-migration 的处理 | 本方案的升级 |
| --- | --- | --- |
| **① 无强制执行层**（一切流程皆“建议”，靠 AI 自觉；无 CI、无门禁） | 仅把 `on-session-start.json` 作为“可选占位”，Git 安全仍是 skill 内部自查 | **把 hooks 作为一等公民**：`PreToolUse` 在 `git commit`/危险 Git 操作前强制跑校验器并可 **deny**；`SessionStart` 自动注入框架上下文。详见 `01` §三。这是 plugin 形态**唯一能给 AICC 补上的、clone 模式给不了的能力** |
| **② 手动注入摩擦**（每次手动粘贴 AI_ENTRY_POINT.md） | skill description 自动触发（部分缓解），但无会话级上下文注入 | `SessionStart` hook + skill 自动触发，**安装一次、永久生效**，彻底消除手动粘贴 |
| **③ 体量失控 + 6 万行散文** | 1:1 复制现有 workflows/templates 到 references | **迁移即收敛**：把改造作为强制瘦身契机——入口压缩、模板去变体、角色去骨架，**只迁移收敛后的资产**，而非搬运债务。详见 `02` §二 |

---

## 二、为什么 plugin 同时解决了“体量”与“强制”两大根因

```
审查根因 ①「无反熵机制」 ──► Plugin hooks（PreToolUse 门禁 + SessionStart 注入）
审查根因 ②「体量失控」   ──► Plugin 多 skill + 渐进式披露（按需加载，主体仅 200-300 行）
审查根因 ③「规格-实现鸿沟」──► skill description = 唯一契约；config → settings.json/hooks，真正驱动行为
审查根因 ④「手动注入摩擦」 ──► 一键 /plugin install，SessionStart 自动注入
审查根因 ⑤「无遥测」      ──► PostToolUse hook 可做最小审计日志，为量化宣称提供真实数据
```

> 一句话：**plugin 不只是“换个分发方式”，它是把 AICC 从“需要人读、靠人自觉的文档系统”升级为“自动加载、系统强制的工程系统”的载体。** 这正是两份审查 §7 的共同结论“把‘AI 应当遵守’变成‘系统保证执行’”的落地路径。

---

## 三、文档导航

| 文档 | 主题 | 优先级 |
| --- | --- | --- |
| **README.md**（本文） | 方向决策、与 skill-migration 的关系、根因映射 | ⭐⭐⭐ 必读 |
| [`01-plugin-architecture-and-enforcement.md`](./01-plugin-architecture-and-enforcement.md) | plugin 目录骨架、hooks 强制执行层设计（核心增量）、组件映射增量、Phase-0 开放问题已答清单 | ⭐⭐⭐ 必读 |
| [`02-implementation-roadmap.md`](./02-implementation-roadmap.md) | “迁移即收敛”路线图、阶段门禁、与 skill-migration 8 阶段的差异、风险与回退 | ⭐⭐ 实施前必读 |

> skill-migration 的 `02-component-mapping.md`（11-skill 映射）、`04-edge-cases`、`05-open-questions` **仍然有效，不在此重复**；本方案只补其增量与纠其偏差。

---

## 四、状态与决策登记

| 字段 | 值 |
| --- | --- |
| 方向决策 | **Plugin（单 plugin × 多 skill × hooks 强制层 × 迁移即收敛）** |
| 关联分支 | `plugin-conversion`（不在 dev/master 上工作） |
| 前置输入 | `FRAMEWORK_REVIEW.md`、`FRAMEWORK_REVIEW_II.md`、`skill-migration/*` |
| 复审人 | _待指定_ |
| 立项决策日期 | _待定_ |
| 与 skill-migration 关系 | 吸收其架构决策 + 新增 hooks/收敛两线；建议将 skill-migration 标注为 superseded |

**修订记录**

| 日期 | 内容 | 修订人 |
| --- | --- | --- |
| 2026-06-11 | 初版：定向 plugin，吸收 skill-migration，新增 hooks 强制层与迁移即收敛两线 | 架构审查（AI 协作） |

---

## 五、给复审人的 3 个待决问题

1. **是否接受“迁移即收敛”原则**？即：plugin 化**不做** 6 万行 1:1 搬运，而是与瘦身（入口、模板、角色去骨架）**强绑定**。若否，plugin 将继承现有体量债。
2. **是否接受 hooks 作为一等强制层**？这会让 AICC 在 Claude Code 上具备 clone 模式永远不具备的 deny 能力，但也意味着要维护跨平台 hook 兼容（非 Claude Code 平台无 hooks，退化为 skill 内自查）。
3. **是否同意将 `skill-migration` 正式更名/标注为被 `plugin-conversion` 吸收**，以避免 `dev/plan/` 出现两份竞争规划（这正是 `FRAMEWORK_REVIEW_II.md` P6 批评的“计划只增不收敛”）。
