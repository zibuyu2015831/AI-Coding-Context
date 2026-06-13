---
title: AICC Plugin 化实施路线图（迁移即收敛）
summary: 定义 plugin 改造的分阶段实施路线，核心原则是“迁移即收敛”——每迁移一块能力，先按两份审查的瘦身要求收敛，再打包，绝不 1:1 搬运体量债。给出与 skill-migration 8 阶段路线的差异、阶段门禁、风险与回退，以及 Phase 0 因开放问题已答而可压缩的工期。
keywords: roadmap | migration | convergence | phases | gate | rollback
scope: dev/plan/plugin（实施路线）
related_files: ./README.md | ./01-plugin-architecture-and-enforcement.md | ./03-execution-spec.md | ../skill-migration/03-implementation-roadmap.md
dependencies: ./01-plugin-architecture-and-enforcement.md
verified_at: 2026-06-11
status: 规划完成
---

# AICC Plugin 化实施路线图（迁移即收敛）

> 本路线图**不复制** skill-migration `03-implementation-roadmap.md` 的 8 阶段细节，而是叠加两个新约束：**①每阶段强制耦合“收敛动作”；②Phase 0 因 Q1–Q5 已答而收敛为冒烟测试。**

> **用于一次性 `/goal` 执行**：下列阶段**不是 7.5 人月的人工排期，而是单次 goal 会话应遵循的「构建顺序 + 检查点」**。执行者按 P0→P5 顺序推进，**每完成一个阶段做一次 checkpoint commit**（含该阶段验收自检），失败则在本阶段内自我修复后再进入下一阶段。逐文件的“构建什么”见 `./03-execution-spec.md`（英文蓝图）。

---

## 一、第一原则：迁移即收敛（Migration = Convergence）

`FRAMEWORK_REVIEW_II.md` 的核心警告是：AICC 用“写更多文档”解决“文档过载”，已积累 6.3 万行体量债。**若 plugin 化只是把 6 万行 1:1 搬进 references，等于把债务原样搬家，还多一层打包成本。**

因此本路线图的硬规则：

> **每迁移一块能力进 plugin 之前，必须先完成对应的收敛动作；未收敛的资产不许进 plugin。** 收敛是迁移的入场券，不是可选项。

| 迁移对象 | 强制前置收敛动作 | 对应审查项 |
| --- | --- | --- |
| AI_ENTRY_POINT.md (811) | 删除 90%，路由职责交给 skill description，边界压成数行 reference | P2 入口过载 |
| generation_plan ×6 变体 | 收敛为 1 主模板 + 条件片段 | P2 模板爆炸 |
| 进度模板 ×2 / commit-guided 引导 ×2 | 各自合一 | P2 冗余 9–11% |
| 角色 ×20（50% 骨架） | 抽公共模板，personas 折叠为参数 | P1 角色去骨架 |
| 量化宣称（99/80/50…） | 迁移文案时一并删除或改定性 | P4 伪精确 |
| 复杂度仪表盘 | 阈值按规模校准或降级删除 | P6/D7 剧场 |

**度量目标**：plugin 内总文档行数应显著低于当前公共 6.3 万行（建议设硬指标，如 references 总量 ≤ 现有的 50%），并在每阶段门禁核验。

---

## 二、阶段路线（在 skill-migration 8 阶段上的差异视图）

> 标 ➕ 为本方案新增/强化，🔁 为对 skill-migration 阶段的修改，= 为沿用。

| 阶段 | 目标 | 与 skill-migration 的差异 | 退出门禁 |
| --- | --- | --- | --- |
| **P0a 冒烟确认** | 验证 plugin.json / bin / 共享 references / 链式 skill / hooks 五项可跑通 | 🔁 **由“探索性验证”降级为“确认性冒烟”**（Q1–Q5 已答，见 `01` §五），工期从 0.25 月压缩 | 一个含 1 个空 skill + 1 个 PreToolUse hook 的最小 plugin 可安装、hook 能 deny |
| **P0b 骨架 + 收敛标准** | plugin 骨架、build-time copy、CI lint、**收敛标准文档（入口/模板/角色瘦身规则 + 行数硬指标）** | ➕ 新增“收敛标准”为交付物；➕ CI lint 增加“行数预算”检查 | 可安装空 plugin + 收敛规则与行数预算已定 |
| **P1 MVP（init + health-check）** | 两个低风险 skill；**同时落地 SessionStart 注入 hook** | ➕ hook 提前到 MVP（skill-migration 推迟到 Phase 1+）；🔁 迁移前先收敛 AI_ENTRY_POINT 与模板 | 用户零粘贴完成首次生成 + 健康检查；触发准确率 ≥85% |
| **P1.5 增量更新 + ★强制门禁** | `incremental-update`；**PreToolUse commit 门禁 + 危险 Git 拦截** | ➕➕ **本方案核心**：把 Git 安全从 skill 内自查升级为 hook 强制 deny | commit 门禁能真实阻断不合规提交；危险操作被拦截 |
| **P2 思维类 skill** | design-thinking / mutual-review / adr | = 沿用；➕ mutual-review 与 PreToolUse 门禁串联 | 链式 skill 触发稳定；互审可被门禁调用 |
| **P3 其余 V3.0 能力** | complexity / doc-fallacy-fix / systematic-review / doc-reading-habit / knowledge-reuse | 🔁 complexity 必须先做实或删除，不许带“剧场”进 plugin | 全能力收敛后入 plugin；总行数达标 |
| **P3.5 ➕ 遥测闭环** | PostToolUse 审计 + 用真实数据回填/修正宣称 | ➕ skill-migration 无此阶段 | 至少一项原“量化宣称”被真实数据替换或撤回 |
| **P4 Codex 投影** | 由同一套源 build-time 生成 `dist/codex/`（`aicc-` 前缀；hooks 退化为 body 内建议） | 🔁 平台收敛为 Codex 单一次形态，**不做 Gemini/Copilot** | Codex flat 包可由同源生成 |
| **P5 迁移与归档** | clone→plugin 迁移指南；clone 模式弃用策略 | = 沿用 | 老用户有迁移路径 |

---

## 三、关键排序理由

1. **hooks 前置**：skill-migration 把强制/注入 hook 推迟为后期可选；本方案把 **SessionStart 提到 P1、PreToolUse 提到 P1.5**。因为两份审查一致认定“无强制层”是第一缺口——**应尽早证明 plugin 形态确实补上了它**，而非留到最后。
2. **收敛先于打包**：每阶段先收敛对应资产再迁移，避免“先搬 6 万行、以后再瘦身”（以后永远不会到来，正是 P6“计划只增不收敛”的成因）。
3. **遥测独立成阶段（P3.5）**：让“撤回/修正伪精确宣称”成为显式交付物与门禁，否则它永远是“以后再说”。

---

## 四、风险与回退

| 风险 | 缓解 / 回退 |
| --- | --- |
| Codex 无 hooks，强制层不可用 | 这是 by-design 退化：强制层仅在 Claude Code 主形态保证；Codex 形态显式标注“建议级”，写入退化矩阵（`01` §3.4）。不为此增加跨平台维护负担 |
| PreToolUse deny 误伤正常 commit（过严） | 门禁先以 `ask`（提示+人工确认）灰度，稳定后再升 `deny`；阈值与白名单可在 settings.json 调 |
| 收敛动作与迁移耦合拖慢进度 | 收敛只针对“即将迁移”的那块，按 skill 切片增量进行，不要求一次性全仓瘦身 |
| skill 链式触发实测不稳定 | 回退到 subagent 调用或 body 内嵌片段（skill-migration 已有三级回退，沿用） |
| 与 skill-migration 双规划并存造成混淆 | 已把 skill-migration 标注 superseded，单一真相源落在 `dev/plan/plugin`（呼应审查 P6） |

---

## 五、与原 8 阶段的工期变化（定性）

- **P0a 压缩**：Q1–Q5 已答 → 探索变冒烟。
- **P1/P1.5 增重**：新增两个 hook 的实现与测试（净增工作，但兑现核心价值）。
- **P3 可能减重**：收敛使部分能力（如 complexity 剧场）直接删除而非迁移。
- **新增 P3.5**：遥测闭环（小阶段）。

> 总体工期与 skill-migration 的 ~7.5 人月**同量级**，但**价值密度更高**：同样的投入额外换来强制执行层、真实遥测、体量减半。

---

## 六、执行前置 checklist（决策已锁定 D1–D7，无未决问题）

- [x] 决策 D1–D7 已由用户确认锁定（见 `README.md` §一）
- [x] `skill-migration` 已标注 superseded，单一真相源落在 `dev/plan/plugin`
- [x] `dev` 基线已先行修复审查硬伤（版本标题、无依据量化宣称）并合入 `plugin`
- [ ] 在新会话以 `PLUGIN_BUILD_KICKOFF.md` 启动 `/goal`，在 `plugin` 分支一次性执行（不在 dev/master 推进）
- [ ] （可选）为本工作项在 `dev/` 状态系统登记为 V3.1 / V4.0 工作项
