---
title: AICC Plugin 架构与强制执行层设计
summary: 定义 AICC 作为 Claude Code Plugin 的目录骨架、组件映射增量，并重点设计 skill-migration 缺失的【hooks 强制执行层】（PreToolUse 门禁 + SessionStart 注入 + PostToolUse 审计），将两份审查指出的“无强制层/手动注入/无遥测”三大根因落地。附 Phase-0 五个高优开放问题（Q1–Q5）基于官方机制核验后的已答清单。
keywords: plugin | hooks | enforcement | skill | subagent | claude-plugin-root | settings
scope: dev/plan/plugin（plugin 架构与强制层）
related_files: ./README.md | ./02-implementation-roadmap.md | ./03-execution-spec.md | ../skill-migration/02-component-mapping.md
dependencies: ./README.md
verified_at: 2026-06-13
status: done（已实施）
---

# AICC Plugin 架构与强制执行层设计

> 本文是本方案的技术核心（设计/理由层）。**逐文件的执行蓝图见 `./03-execution-spec.md`（英文）。** 约定：11-skill 的语义映射沿用 `../skill-migration/02-component-mapping.md`，本文只写其增量与官方机制核验后的修正，不重复。
>
> **语言强制（D5）**：本文为中文规划稿；但**一切 plugin 产物（plugin.json description、SKILL.md、references、hooks 注释与消息、bin 帮助、plugin README）必须为英文**。下文出现的中文仅为设计说明，落地时全部以英文实现。

---

## 一、Plugin 目录骨架（基于 Claude Code 官方结构核验）

```text
aicc/                                   # plugin 根（release 产物，由 build-time copy 生成）
├── .claude-plugin/
│   └── plugin.json                     # 唯一放在 .claude-plugin/ 内的文件
│
├── skills/                             # 多 skill（每条工作流一个，渐进式披露）
│   ├── init/                           # = 现 Path A 首次生成
│   │   ├── SKILL.md                    # 主体 ≤300 行，body 只放“何时触发 + 主流程骨架”
│   │   ├── references/                 # 按需 Read：详细步骤、模板、project_types
│   │   └── agents/                     # 与本 skill 强耦合的 runtime 角色（plan_reviewer 等）
│   ├── health-check/                   # = Path B
│   ├── incremental-update/             # = Path C（含 commit-guided + git-safety 触发点）
│   ├── design-thinking/  mutual-review/  adr/        # = Path D 三类
│   └── …（complexity / doc-fallacy-fix / systematic-review / doc-reading-habit / knowledge-reuse）
│
├── agents/                            # 开发期高频 subagents（plugin 根级，可被 Agent tool 调用）
│   ├── architecture_analyst.md  api_designer.md  database_designer.md  product_manager.md
│
├── hooks/                            # ★ 本方案核心增量：强制执行层（skill-migration 缺失）
│   ├── hooks.json
│   ├── pre_commit_gate.py            # PreToolUse: git commit 前强制校验
│   ├── dangerous_git_guard.py        # PreToolUse: 拦截 push --force / reset --hard 等
│   ├── session_inject.py             # SessionStart: 自动注入框架上下文 + 项目状态
│   └── post_tool_audit.py            # PostToolUse: 最小遥测日志（可选）
│
├── scripts/                          # 现 tools/ 原始脚本（Python 主、JS 降级、fallback）
│   ├── py/  js/  fallback/
│
├── bin/                              # 包装命令加入 PATH：aicc-scan / aicc-doc-health / aicc-summary-validate …
│
├── references/                       # 跨 skill 共享（一层）：language_rules / security_rules / SUMMARY_FORMAT_SPEC / project_types
├── settings.json                     # plugin 默认配置（替代部分 config/ 体系，见 §四）
└── README.md
```

**与 skill-migration 骨架的差异**：①`hooks/` 从“可选占位”升格为**独立一等目录并承载强制逻辑**；②`config/` **不再原样进入 plugin**，拆分为 `settings.json` + hook 行为（§四）。

---

## 二、组件映射增量（仅修正/补充 skill-migration 02）

| 组件 | skill-migration 原映射 | 本方案修正 | 理由 |
| --- | --- | --- | --- |
| Git 安全 | `incremental-update` skill 内部自查 + `scripts/hooks/` 显式调用 | **升级为 `hooks/` 自动门禁**（PreToolUse deny） | skill 内自查仍是“建议”；只有 PreToolUse 能真正**阻断**。这是审查 D1/P3 的唯一解 |
| config 系统 | 整体放弃，移到 settings.json 或用户 `dev_docs/configuration.md` | **拆分**：行为开关 → `settings.json`；强制项 → hook 读取并执行 | 审查 P1 指出“配置弱接线”；放进 hook 才真正驱动行为 |
| AI_ENTRY_POINT.md（811 行） | 拆入各 skill description + references | **不迁移其 90%**：路由职责由 skill description 承担，边界规则压成 `references/boundary.md`（数行） | 审查 P2：入口过载；plugin 化是删除它的契机 |
| 6 个 generation_plan 变体模板 | 作为 references 迁移 | **先收敛为 1 主模板 + 条件片段，再迁移** | 审查 P2：模板爆炸；迁移即收敛 |
| personas（Linus/Fowler/Uncle Bob） | 未明确 | **不迁移为独立文件**，折叠为 review skill 的视角参数 | 审查 P1：personas 是参数非能力 |
| 复杂度仪表盘 | 列为 `complexity-dashboard` skill | **先做实或降级**：阈值（150/200/300）须按项目规模校准，否则不迁移 | 审查 P6/D7：当前是“剧场” |

---

## 三、★ 强制执行层设计（本方案最大增量）

> 两份审查的第一缺口是“**一切皆建议、无程序性强制**”。clone 模式永远无法解决——但 **Claude Code plugin 的 hooks 可以**。这是选择 plugin 而非继续 clone 的决定性理由。

### 3.1 PreToolUse 门禁 —— 把“建议”变“可阻断”

**目标**：AI 执行 `git commit` 前，强制跑 `summary_validator` + `framework_contract_checker`，不通过则 `deny`。

`hooks/hooks.json`（节选）：

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "if": "Bash(git commit*)",
        "hooks": [{
          "type": "command",
          "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/pre_commit_gate.py\"",
          "description": "AICC: commit 前文档健康/契约门禁"
        }]
      },
      {
        "matcher": "Bash",
        "if": "Bash(git (push --force*|reset --hard*|clean -f*))",
        "hooks": [{
          "type": "command",
          "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/dangerous_git_guard.py\"",
          "description": "AICC: 危险 Git 操作拦截"
        }]
      }
    ]
  }
}
```

`pre_commit_gate.py` 返回 deny 的契约（官方机制）：

```python
# 读取 stdin JSON → 跑校验器 → 不通过则 deny
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",            # allow | deny | ask
    "permissionDecisionReason": "summary_validator 失败：3 处 frontmatter 缺失"
}}))
sys.exit(0)
```

> **这一条 hook，等价于审查 P0 要求的“CI 门禁 + 反熵机制”，且无需 GitHub Actions——在本地会话内即时生效。** 它把“摘要合规率不会回退到 14%”从愿望变成机制保证。

### 3.2 SessionStart 注入 —— 消除“手动粘贴入口”

**目标**：安装一次后，每次会话自动注入框架心智模型与当前项目文档状态，AI 无需用户再发 `AI_ENTRY_POINT.md`。

```jsonc
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/session_inject.py\"",
        "description": "AICC: 注入框架上下文 + 项目文档健康快照"
      }]
    }]
  }
}
```

`session_inject.py` 通过 `additionalContext` 注入：①AICC 可用 skill 清单与触发时机；②本项目 `dev_docs/` 是否存在、健康度快照（复用 `doc_health_checker`）。**这同时解决审查 D2（手动注入）与 EC-6.1（用户不知有哪些能力）。**

### 3.3 PostToolUse 审计 —— 给“量化宣称”补上真实数据

**目标**：审查 P4 批评 99%/80%/50% 等数字无据。最小遥测可改变这一点。

PostToolUse hook（异步、不阻断）把“哪个 skill 被触发、跑了哪个工具、产出多少文档”追加到 `${CLAUDE_PLUGIN_DATA}/aicc_telemetry.jsonl`。**即便不做对照实验，也能用真实触发数据替代拍脑袋数字。**

### 3.4 平台范围与 Codex 退化策略（D4：仅 Claude Code + Codex）

目标平台收敛为两个，**不为 Gemini/Copilot 等任何其它平台适配**。Codex **无 hooks 机制**，强制层退化为建议级。

| 能力 | Claude Code（主形态） | Codex（次形态，flat 包） |
| --- | --- | --- |
| skill 触发 | description 自动 + `/aicc:*` | `aicc-*` 前缀 prompt/AGENTS.md 引导 |
| commit 门禁 | `PreToolUse` deny（强制） | skill body 内“请先运行 `aicc-doc-health`”（建议） |
| 上下文注入 | `SessionStart` 自动 | 用户手动触发入口 skill |
| 审计遥测 | `PostToolUse` 自动 | 无 |

**Codex 形态如何产出**：由 build-time 从**同一套 skill 源**生成 flat 包——把短名加 `aicc-` 前缀、把 hooks 的强制语义降级为 SKILL.md body 内的“建议步骤”文字。Codex 包**不复制独立内容**，仅是主形态的“降级投影”，避免双份维护。

> **结论**：强制层是 Claude Code 主形态的差异化优势，作为主打；Codex 明确标注“退化为建议级”，**主设计不被 Codex 能力上限拉低**。Codex 适配排在所有 Claude Code 能力之后（见 `02` 路线）。

---

## 四、配置体系重构（修正审查 P1“配置弱接线”）

skill-migration 决策是“config 不进 plugin”。本方案细化为**三去向**：

1. **行为开关**（documentLanguage / enableMutualReview / git_safety.mode 等）→ plugin `settings.json` + 用户 `.claude/settings.json` 覆盖。Claude Code 原生读取，**真正生效**，而非现在的“纸面声明”。
2. **强制项**（protected_branches / require_branch_naming）→ 由 §3.1 的 hook **读取并执行**，从“提示”变“拦截”。
3. **项目级配置说明**（项目如何管理环境变量等）→ 仍作为用户项目 `dev_docs/configuration.md` 子文档。

> 这样，审查实测“`enableMutualReview` 仅在 2 个工作流被引用、形同虚设”的问题被根治：开关要么被 Claude Code settings 真正消费，要么被 hook 真正执行。

---

## 五、Phase-0 高优开放问题（Q1–Q5）已答清单

skill-migration `05-open-questions.md` 把 Q1–Q5 列为“Phase 0 必须验证、可能迫使架构返工”。基于官方机制核验，现给出**已可定调的答案**，大幅降低 Phase 0 风险：

| # | 原开放问题 | 核验结论 |
| --- | --- | --- |
| Q1 | plugin.json schema 未知 | ✅ 已明确：`.claude-plugin/plugin.json`，必填 `name`/`description`，可选 `version`(无则用 git SHA)/`author`/`repository`/`license`。组件目录（skills/agents/hooks/）须在 plugin 根、**不在** `.claude-plugin/` 内 |
| Q2 | `bin/` 是否稳定加入 PATH | ✅ 支持 `bin/`；同时 `${CLAUDE_PLUGIN_ROOT}` 可绝对引用。建议 bin 为主、env 变量为辅，与决策 #8 一致 |
| Q3 | skill 能否读 `../references/` 共享层 | ✅ 可。一个 plugin 内多 skill 共享 plugin 根的 `references/`，无需各自拷贝（呼应决策 #9） |
| Q4 | 发布渠道 marketplace vs git URL | ✅ 二者皆可：`/plugin install <git-url|.zip>` 或注册 marketplace.json。MVP 用 git URL，成熟后上 marketplace（含 Anthropic 官方/社区两个公共 marketplace） |
| Q5 | SKILL.md 能否直接调用其他 `/aicc:*` skill | ✅ 可在 body 指示“运行 `/aicc:health-check`”，或委托 subagent；二者皆官方支持。**无需再把“互调用不可行”作为高风险**，但仍建议 Phase 1 做一次实测确认链式触发稳定性 |

> **影响**：skill-migration 把 Q1–Q5 视为可能导致架构返工的高风险未知；核验后**5 项全部落地为“已支持”**，Phase 0a 从“探索性验证”收敛为“确认性冒烟测试”，可压缩工期（详见 `02` 路线图）。

---

## 六、本文小结

plugin 形态给 AICC 带来三件 clone/单 skill 都给不了的东西：**(1) 可阻断的强制门禁（hooks）、(2) 自动上下文注入（SessionStart）、(3) 真实遥测底座（PostToolUse）**。它们精确对应两份审查的前三大根因。架构骨架与组件映射沿用 skill-migration 已锁定决策，本方案的净增量集中在**强制执行层**与**配置真正生效**两处。
