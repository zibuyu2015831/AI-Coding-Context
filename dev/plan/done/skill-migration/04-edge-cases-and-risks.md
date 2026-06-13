---
title: AICC Skill 化 — 边界条件与风险全景
summary: 系统梳理 skill 化迁移过程中可能遇到的边界条件与风险，按 8 个类别（skill 系统约束 / token / 互调用 / 工具脚本 / 项目检测 / 用户认知 / 升级兼容 / 多平台 / dogfood）归并；每条记录现象、影响、缓解措施、是否 Phase 已覆盖。
keywords: aicc | skill | edge-cases | risks | mitigation
scope: dev/plan/done/skill-migration 子项目（风险评估阶段）
related_files: 01-feasibility-and-architecture.md | 02-component-mapping.md | 03-implementation-roadmap.md | 05-open-questions.md | README.md
dependencies: 01-feasibility-and-architecture.md | 03-implementation-roadmap.md
verified_at: 2026-04-26
---

# 04 — 边界条件与风险全景

> **本文档使用方法**：所有边界 / 风险按"类别 → 编号 → 现象 → 影响 → 缓解 → 是否 Phase 已覆盖"格式记录。Phase 已覆盖项可在实施时直接回查。未覆盖项则需在实施前补设计。

---

## 一、skill 系统约束相关

### EC-1.1：SKILL.md 500 行硬上限 vs AICC 现有 workflow 文档普遍 600+ 行

**现象**：AICC 当前 `path_a_first_generation.md` ≈ 650 行，`commit_guided_update.md` ≈ 480 行，`git_safety_workflow.md` ≈ 520 行。直接复制为 SKILL.md 会超限。

**影响**：超过 500 行后 Anthropic 官方建议拆分；不拆分会导致 skill 加载性能下降、Claude 难以快速找到信息。

**缓解**：
- 强制要求：每个 SKILL.md 只保留"导航与决策框架"（200-300 行），具体步骤拆 `references/step_N.md`
- 在 Phase 0 standards 文档中固化此规则
- CI 加 lint：`wc -l skills/*/SKILL.md` > 500 即报错

**Phase 覆盖**：✅ Phase 0（standards + CI）

---

### EC-1.2：description 1024 字符 + "Use when..." 风格强制

**现象**：当前 AICC 文档头部多用"职责说明"、"目的"开头，不是 trigger-style。description 写不好的两种典型错误：
- 太短："Use for AICC" → 无法精确触发
- 总结 workflow："Use when ... will run 8 steps including X, Y, Z" → Claude 跟着 description 跳过 SKILL.md（writing-skills 警告的反模式）

**影响**：触发准确率下降；skill body 被跳过。

**缓解**：
- 在 Phase 0 standards 文档 `description-style-guide.md` 中给出 BAD/GOOD 范本
- 每个 skill 的 description 必须经过同行 review（PR 审查清单）
- 触发准确率 baseline eval 加入"用户应触发但未触发"和"用户不应触发但触发了"两类负样本

**Phase 覆盖**：✅ Phase 0（standards）+ Phase 1-3（每 skill 必带 baseline eval）

---

### EC-1.3：references 只能 1 层深

**现象**：AICC 现有引用是 3 层链：
```
path_a_first_generation.md → workflows/shared/failure_handling.md → core/security_rules.md
```

**影响**：skill 模式下，Claude 可能用 `head -100` 等部分读取方式，导致信息丢失。

**缓解**：
- 每个 skill 的 references/ 内文件**只能由 SKILL.md 直接引用**，不能 references 之间互引
- 跨 skill 共享的内容统一上提到 `plugin/references/`
- 长 reference（> 100 行）必须在文件头部加 TOC

**Phase 覆盖**：✅ Phase 0（layout 规范）+ Phase 1-3（每 skill 验收）

---

### EC-1.4：100+ skill 同时存在的命名空间污染

**现象**：用户机器上可能同时安装多个 plugin（superpowers、document-skills、aicc...）。所有 skill 的 metadata 都进 cold-start 系统提示。

**影响**：
- AICC 的 11 个 skill metadata（每个 ~150 token）= ~1.5k token 进 base prompt
- 加上其他 plugin，可能累计到 5-10k
- description 模糊或重叠会导致触发冲突

**缓解**：
- Claude Code plugin 内使用短 skill 名，并依赖 plugin namespace（如 `/aicc:init`）避免显式冲突
- 面向无 namespace 平台的 flat 包构建时再添加 `aicc-` 前缀
- description 中使用差异化关键词（如 `mutual-review` 限定 "for AICC-generated plans"，不与 superpowers:requesting-code-review 抢通用代码 review）
- 每个 skill 的 description 中显式列 "NOT for X"

**Phase 覆盖**：✅ Phase 0（命名规范）+ Phase 2（与 superpowers 兼容性测试）

---

### EC-1.5：Claude Code plugin namespace 与 `aicc-*` skill 前缀重复

**现象**：Claude Code plugin 会把 skill 暴露为 `/plugin-name:skill-name`。如果 plugin 名为 `aicc` 且 skill 目录仍叫 `aicc-init`，用户显式调用会变成 `/aicc:aicc-init`。

**影响**：资深用户使用时感到冗余；README、eval、跨平台文档会混淆；后续若再产出 flat skill 包，会难以区分"源码名"与"发布名"。

**缓解**：
- Claude Code plugin 内使用短名：`init`、`health-check`、`incremental-update`
- 面向无 namespace 平台的 flat 包由 build 阶段生成 `aicc-init` 等前缀名
- CI 检查 plugin 内不得出现 `skills/aicc-*` 目录

**Phase 覆盖**：✅ Phase 0a（namespace 实测）+ Phase 0b（命名规范）

---

### EC-1.6：真实资产映射偏差

**现象**：初版组件映射中出现了当前仓库不存在的 agent 名称（如 `frontend_expert`、`document_generator`、`auto_reviewer`），同时漏掉真实存在的 `templates/prompts/`、`templates/review/`、`workflows/review_standards/` 等目录。

**影响**：如果直接按规划实施，会出现引用断裂、能力缺失或为了匹配计划而新造不必要资产。

**缓解**：
- Phase 0b 生成 `plugin-manifest.generated.json`
- 每个 skill 的 references/scripts/templates/agents 必须来自真实资产清单
- CI 校验所有引用目标存在，release artifact 排除缓存和开发产物

**Phase 覆盖**：✅ Phase 0b（真实资产清单 + CI）

---

## 二、token 与上下文相关

### EC-2.1：plugin 加载后 base 系统提示膨胀

**现象**：Claude Code 启动加载所有 plugin 的 skill metadata，每个 ~100-200 token。

**影响**：用户的 100k 上下文窗口被无意义占用。

**缓解**：
- 每个 skill 的 description 严控 < 500 字符（远低于 1024 上限）
- skill 总数控制（11 个目标，不再增加）
- 监控指标：plugin 加载后 base prompt size < 5k token（Phase 1 验收）

**Phase 覆盖**：✅ Phase 1+（监控）

---

### EC-2.2：误触发导致无谓加载

**现象**：用户说"check this"，可能同时命中 health-check、mutual-review、doc-fallacy-fix 三个 skill 的 description。

**影响**：Claude 可能依次加载多个 skill 的 SKILL.md，浪费 token。

**缓解**：
- description 中 "NOT for X" 防御条款
- description 第一句话精确锚定（"Use when project already has dev_docs/ AND user wants to assess..."）
- baseline eval 包含"近义词混淆"测试用例

**Phase 覆盖**：✅ Phase 1-3（每 skill eval）

---

### EC-2.3：references 加载顺序与回读

**现象**：Claude 可能不按预期顺序读 references，或重复读同一文件。

**影响**：步骤被跳过，或多次加载浪费 token。

**缓解**：
- SKILL.md 在 Workflow 章节用清晰的"Step N → references/step_N.md"映射表
- 复杂多步流程使用 checklist 格式（参考 `anthropic-best-practices.md` 的 PDF 表单填充例）
- 关键节点用"copy this checklist into your response"显式提示 Claude 跟踪进度

**Phase 覆盖**：✅ Phase 1（init 是第一个测试目标）

---

## 三、skill 互调用相关

### EC-3.1：`Skill` 工具能否在 skill body 内被调用

**现象**：init Step 5.5 需要 design-thinking、Step 7 需要 mutual-review。当前不确定 skill A 内部能否 invoke skill B。

**影响**：如不支持，init 无法委托给 design-thinking，必须在 init 内部嵌入简版（重复维护）。

**缓解**：
- Phase 0 第 1 周即验证（用 superpowers 跑实验）
- 准备三种回退方案：
  - (a) 直接 `Skill` 调用（首选）
  - (b) Subagent 调度（次选，参考 superpowers:subagent-driven-development）
  - (c) 内嵌简版（兜底）
- 把验证结果记入 `05-open-questions.md` Q5

**Phase 覆盖**：✅ Phase 0（验证）+ Phase 2（互调用闭环）

---

### EC-3.2：循环触发风险

**现象**：`init` 调用 `design-thinking`，`design-thinking` 又触发 `mutual-review`，`mutual-review` 又调用 `design-thinking`...

**影响**：无限递归 / 循环 / token 爆炸。

**缓解**：
- 每个 skill 的 SKILL.md 在 "Related Skills" 章节明确"何时调用"和"调用后是否返回"
- 测试场景包含"复杂任务"以观察是否成环
- 实现"调用栈深度提示"约定（每个 skill body 在被调用时检查上下文是否已有同类调用）

**Phase 覆盖**：✅ Phase 2（互调用测试）

---

### EC-3.3：skill 上下文继承不一致

**现象**：init 调用 design-thinking 时，design-thinking 是否能拿到 init 已收集的项目上下文？

**影响**：如不能继承，每次调用都要重新让 Claude 从用户对话历史中拼装上下文。

**缓解**：
- 在 SKILL.md 的"Related Skills"章节明确"调用前需要在对话中确认 X、Y、Z 已存在"
- 用临时文件作为状态传递（init 写 `dev_docs/_analysis/in-flight.json`，design-thinking 读）
- 在 Phase 2 测试场景观察 Claude 实际行为

**Phase 覆盖**：⚠️ 部分（Phase 2 验证）；如发现严重问题，需补独立设计

---

## 四、工具与脚本相关

### EC-4.1：Python / Node.js 都不可用

**现象**：用户在受限环境（如某些 sandbox、CI 镜像）没有 Python 也没有 Node。

**影响**：所有依赖脚本的 skill 失效。

**缓解**：
- 保留 `scripts/fallback/`（Bash / PowerShell 速查）
- 每个 skill 的 SKILL.md 在"Required Tools"章节给出三级降级（py → js → fallback）
- init 的 Step 1 "环境预检" 一开始就检测可用性，不可用时给用户明确提示

**Phase 覆盖**：✅ Phase 1（init 验证）

---

### EC-4.2：sandbox 模式下脚本无法运行

**现象**：Claude Code 的 sandboxed mode 限制 Bash 写权限或网络。

**影响**：`project_scanner.py` 写 report 文件可能失败。

**缓解**：
- 脚本设计：所有写操作输出到 stdout，由 Claude 接收并写文件（避免脚本直接写盘）
- 在 SKILL.md 提示用户"如在 sandbox 中遇到 permission denied，请退出 sandbox 重试"

**Phase 覆盖**：⚠️ 待 Phase 1 测试

---

### EC-4.2b：直接依赖 plugin root 环境变量导致脚本路径不稳

**现象**：初版规划假设存在 `${CLAUDE_PLUGIN_ROOT}`，但该变量是否稳定、跨平台、跨安装方式一致尚未验证。

**影响**：所有 skill 的脚本调用语句可能需要返工；用户在 git URL、zip artifact、本地 path 三种安装方式下行为可能不同。

**缓解**：
- 主方案改为 `bin/` 包装命令（如 `aicc-project-scan`），由 plugin 机制加入 PATH
- Phase 0a 实测 `bin/`，不可用时再定义 `AICC_PLUGIN_ROOT` fallback
- SKILL.md 不直接硬编码长路径，脚本路径细节集中在 `scripts-call-convention.md`

**Phase 覆盖**：✅ Phase 0a + Phase 0b

---

### EC-4.3：Windows 路径与 shell 差异

**现象**：用户在 Windows 上跑 plugin，PowerShell vs Bash 命令差异。

**影响**：脚本调用失败或路径解析错误。

**缓解**：
- 全部用 forward slash（已是 Anthropic 强制要求）
- 脚本调用使用 `python` 命令而非 `python3`（兼容性）
- env_diagnosis.py 自动检测平台并切换命令风格
- references/platform_compat/ 提供 Windows/Linux 命令对照表

**Phase 覆盖**：✅ Phase 1（env_diagnosis 已有逻辑）

---

### EC-4.4：脚本依赖第三方库

**现象**：复杂脚本（如 complexity_scanner.py）可能依赖 `tree-sitter` 等第三方包。

**影响**：用户首次使用 plugin 时遇到 ImportError。

**缓解**：
- plugin 自带 `requirements.txt`（位于 `scripts/py/`）
- SKILL.md 在 "Required Tools" 章节列出依赖
- 脚本本身用 try/except 给出友好错误提示（参考 `anthropic-best-practices.md` 的 "Solve, don't punt"）

**Phase 覆盖**：⚠️ 待 Phase 0 验证 plugin 是否支持 requirements.txt 自动安装

---

## 五、项目检测相关

### EC-5.1：dev_docs/ 已存在但不完整

**现象**：用户之前用 clone 模式半途中断，dev_docs/ 只有主文档没有子文档。

**影响**：init 不会触发（因为 dev_docs/ 已存在），但 health-check 会报告"严重不完整"。

**缓解**：
- health-check 检测到不完整时，handoff 给"修复"路径而非"重新生成"
- 提供独立 skill `init` 的强制启动选项：用户说"reset and regenerate"
- 在 README 文档中说明这种边界

**Phase 覆盖**：✅ Phase 1（handoff 网络）

---

### EC-5.2：用户重命名了框架目录或 dev_docs/

**现象**：用户把 `dev_docs/` 改成 `docs/ai/`，或框架目录命名特殊。

**影响**：检测命令失败。

**缓解**：
- 每个 skill 的检测逻辑使用 glob pattern + 内容特征（找带 frontmatter 的 AI_Coding_Context.md），而非硬路径
- 检测失败时主动询问用户而非默认假设

**Phase 覆盖**：✅ Phase 1（detection 逻辑增强）

---

### EC-5.3：Monorepo / 多包项目

**现象**：用户在 monorepo 根目录运行 plugin，但每个 package 应该有自己的 dev_docs/。

**影响**：单一 dev_docs/ 不足以描述 monorepo 内多个独立模块。

**缓解**：
- init 检测到 monorepo（package.json workspaces / lerna.json / turbo.json） → 询问用户
- references/special_scenarios/monorepo.md 提供处理策略

**Phase 覆盖**：✅ Phase 1（init special scenarios）

---

### EC-5.4：多个项目共享一份框架配置

**现象**：用户希望多个项目共享一些约定（如团队规范）。

**影响**：每个项目独立的 dev_docs/ 难以共享。

**缓解**：
- knowledge-reuse skill 专门解决此问题（V3.0 010）
- Phase 3 完成后此场景才完整支持

**Phase 覆盖**：✅ Phase 3（knowledge-reuse）

---

## 六、用户认知相关

### EC-6.1：用户不知道有哪些 skill

**现象**：用户装了 aicc plugin，但不知道有 11 个能力，只用过其中 1-2 个。

**影响**：能力浪费；用户主观觉得"不就那点东西"。

**缓解**：
- plugin 安装后首次启动时（hooks/on-session-start）显示 skill 概览
- README.md 头部清晰列出 11 个 skill 与触发示例
- 考虑保留"`aicc-overview` skill"作为"显示菜单"用途（如不与其他 skill 抢触发权）

**Phase 覆盖**：✅ Phase 0（README）+ Phase 1（hook 设计）

---

### EC-6.2：skill 误触发让用户困惑

**现象**：用户随口说"check"，触发了不期望的 skill。

**影响**：信任度下降。

**缓解**：
- description 中 "NOT for X" 防御条款
- skill body 头部加"Sanity Check"：先问用户"我理解你想做 X，对吗？"
- 用户反馈机制（skill 触发后请求确认）

**Phase 覆盖**：⚠️ 待 Phase 1-3 用户测试

---

### EC-6.3：应触发但没触发

**现象**：用户说"我的 dev_docs 怎么有点乱"，本应触发 health-check 但没触发。

**影响**：用户体验劣化。

**缓解**：
- baseline eval 包含 30+ 自然语言变体测试
- description 关键词覆盖中文与英文
- 用户可显式 `/aicc:health-check` 触发；commands/ 仅作为 Phase 1 后可选 shortcut

**Phase 覆盖**：✅ Phase 1（commands + eval）

---

### EC-6.4：不同语言用户的触发体验差异

**现象**：中文用户说"做一次健康检查"，英文用户说"do a health check"，触发率可能不一致。

**影响**：中文用户体验差。

**缓解**：
- description 包含中英文关键词
- baseline eval 必须有中文样本

**Phase 覆盖**：✅ Phase 1（中英文 eval）

---

## 七、升级与版本兼容

### EC-7.1：plugin 升级后用户已有 dev_docs/ 不兼容

**现象**：aicc@0.5 生成的 dev_docs/ 在 aicc@1.0 中识别不出来。

**影响**：用户被迫重新 init。

**缓解**：
- dev_docs/ 主文档 frontmatter 加 `aicc_version` 字段
- health-check 检测到旧版本 → 触发自动 migration
- 严格 SemVer：major 版本更新时提供 migration 脚本

**Phase 覆盖**：✅ Phase 5（migration 脚本设计）

---

### EC-7.2：plugin 多版本并存

**现象**：用户 A 项目固定 aicc@0.5，用户 B 项目升级到 aicc@1.0。

**影响**：同一台机器跨项目使用混乱。

**缓解**：
- plugin 支持 per-project 版本锁定（通过 `.claude/plugins.lock` 或类似机制，待验证）
- README 明确说明 plugin 是 user-scope 安装，不能 per-project

**Phase 覆盖**：⚠️ 待 Phase 5 调研

---

### EC-7.3：clone 模式 vs plugin 模式输出不一致

**现象**：同一项目，clone 模式生成 dev_docs/ 与 plugin 模式生成的略有差异。

**影响**：双轨用户困惑。

**缓解**：
- Phase 1 验收明确要求差异 < 5%
- 差异点全部记录到 `migrate-from-clone.md`
- 长期：以 plugin 模式为 canonical，clone 模式逐步对齐

**Phase 覆盖**：✅ Phase 1 + Phase 5

---

### EC-7.4：symlink 作为发布机制不可移植

**现象**：初版规划考虑用 symlink 让 `plugin/references/` 指向上层 `core/`，但 release artifact、Windows、marketplace 审核和 zip 解压都可能破坏 symlink。

**影响**：用户安装后 references 丢失或路径异常；CI 本地通过但发布包不可用。

**缓解**：
- symlink 仅允许作为本地开发便利，不作为 release 机制
- 发布前统一 build-time copy 到 `plugin/references/`
- 用 `plugin-manifest.generated.json` 校验复制结果

**Phase 覆盖**：✅ Phase 0b

---

### EC-7.5：commands/ 与 skills/ 双路由混淆

**现象**：如果同时提供 `commands/init.md` 和 `skills/init/SKILL.md`，用户和模型会面对两套入口。

**影响**：文档重复、触发行为不一致、eval 难以判断失败归因。

**缓解**：
- MVP 不做 `commands/`
- 只有当 Phase 1 用户反馈显示显式 shortcut 明显必要时，才补少量 commands
- commands 必须只是薄封装，不能复制 skill workflow

**Phase 覆盖**：✅ Phase 0b + Phase 1 用户反馈

---

## 八、多平台相关

### EC-8.1：Gemini CLI 不支持 plugin commands/

**现象**：commands/ 是 Claude Code 特有，Gemini 没有 slash command 体系。

**影响**：`/init` 等命令在 Gemini 上不可用。

**缓解**：
- skill 自动触发是主路径，commands/ 是兜底
- Gemini 用户使用自然语言触发（与 description 匹配）
- 文档说明此差异

**Phase 覆盖**：✅ Phase 4（多平台说明）

---

### EC-8.2：tool name 在不同平台不同

**现象**：Claude Code 用 `Edit`，Gemini 可能叫 `replace_in_file`。

**影响**：SKILL.md 内硬编码工具名会失效。

**缓解**：
- SKILL.md body 用语义描述（"use the file editing tool"）
- tool 调用细节放 `references/platform_compat/<platform>.md`
- 维护翻译表

**Phase 覆盖**：✅ Phase 4

---

### EC-8.3：Codex / Copilot CLI 无 plugin 概念

**现象**：这两个平台只支持 flat skill 加载。

**影响**：plugin 形态发布的 aicc 无法直接用。

**缓解**：
- Phase 后期可提供 "flat repackage" 镜像 release（把 plugin/skills/* 平铺到 ~/.agents/skills/）
- 当前 backlog 中，不阻塞主线

**Phase 覆盖**：📋 Backlog（不在路线图内）

---

## 九、dogfood 相关

### EC-9.1：framework 自身的 dev/quality/ 与 systematic-review 边界

**现象**：dev/quality/ 是框架自审；systematic-review 是用户项目自审。两者用同一种方法论。

**影响**：可能让维护者混淆"我现在用的是哪一套"。

**缓解**：
- systematic-review SKILL.md 头部明确："for user projects only, NOT for the AICC framework's own development workflow"
- dev/quality/ 体系保持原样不动
- 框架团队如想 dogfood，可在自己框架仓库运行 systematic-review，但这是可选行为

**Phase 覆盖**：✅ Phase 3（systematic-review SKILL.md 边界声明）

---

### EC-9.2：framework 自身的 ADR（dev/architecture/）vs adr skill

**现象**：dev/architecture/decisions/ 是框架自身 ADR；adr 是用户项目 ADR。

**影响**：同上，边界不清。

**缓解**：
- adr SKILL.md 头部声明 "for user projects"
- dev/architecture/ 保留原样

**Phase 覆盖**：✅ Phase 2

---

### EC-9.3：framework dev 流程是否要用 plugin 维护

**现象**：用 plugin 维护 plugin 自身（dogfood 极致版）。

**影响**：鸡生蛋问题；如果 plugin 有 bug 会自我影响。

**缓解**：
- 框架开发使用 clone 模式 + dev/ 体系（保留原状）
- plugin 的开发与发布走独立 CI（与 dev/ 工作流松耦合）
- 长期可选：plugin 稳定后做有限 dogfood，但不是首要目标

**Phase 覆盖**：✅ 设计原则（已写入 `01-feasibility-and-architecture.md §5.3`）

---

## 十、风险矩阵汇总

| 风险编号 | 概率 | 影响 | 风险等级 | 已 Phase 覆盖 |
|---|---|---|---|---|
| EC-1.1（500 行） | 高 | 中 | M | ✅ |
| EC-1.2（description 风格） | 中 | 高 | H | ✅ |
| EC-1.3（reference 嵌套） | 中 | 中 | M | ✅ |
| EC-1.4（命名空间污染） | 低 | 中 | L | ✅ |
| EC-1.5（namespace 与前缀重复） | 中 | 中 | M | ✅ Phase 0a |
| EC-1.6（真实资产映射偏差） | 中 | 高 | **H** | ✅ Phase 0b |
| EC-2.1（base prompt 膨胀） | 中 | 中 | M | ✅ |
| EC-2.2（误触发） | 中 | 中 | M | ✅ |
| EC-2.3（references 加载顺序） | 中 | 低 | L | ✅ |
| EC-3.1（互调用机制） | 中 | 高 | **H** | ⚠️ Phase 0 验证 |
| EC-3.2（循环触发） | 低 | 高 | M | ✅ Phase 2 |
| EC-3.3（上下文继承） | 中 | 中 | M | ⚠️ |
| EC-4.1（无运行时） | 低 | 中 | L | ✅ |
| EC-4.2（sandbox） | 中 | 中 | M | ⚠️ Phase 1 |
| EC-4.2b（plugin root 路径） | 中 | 高 | **H** | ✅ Phase 0a |
| EC-4.3（Windows） | 中 | 中 | M | ✅ |
| EC-4.4（第三方库） | 中 | 高 | **H** | ⚠️ Phase 0 |
| EC-5.1（不完整 dev_docs/） | 中 | 中 | M | ✅ |
| EC-5.2（重命名） | 低 | 低 | L | ✅ |
| EC-5.3（Monorepo） | 中 | 中 | M | ✅ |
| EC-5.4（共享配置） | 中 | 低 | L | ✅ Phase 3 |
| EC-6.1（不知道有哪些 skill） | 高 | 中 | **H** | ✅ Phase 0 + 1 |
| EC-6.2（误触发用户困惑） | 中 | 中 | M | ⚠️ |
| EC-6.3（应触发未触发） | 中 | 中 | M | ✅ |
| EC-6.4（中英文差异） | 中 | 中 | M | ✅ |
| EC-7.1（升级不兼容） | 低 | 高 | M | ✅ Phase 5 |
| EC-7.2（多版本并存） | 中 | 低 | L | ⚠️ |
| EC-7.3（clone vs plugin 输出） | 中 | 中 | M | ✅ |
| EC-7.4（symlink 发布风险） | 中 | 高 | **H** | ✅ Phase 0b |
| EC-7.5（commands 双路由） | 中 | 中 | M | ✅ Phase 0b |
| EC-8.1（Gemini commands） | 高 | 低 | M | ✅ Phase 4 |
| EC-8.2（tool name 差异） | 高 | 中 | M | ✅ Phase 4 |
| EC-8.3（Codex/Copilot） | 低 | 低 | L | 📋 backlog |
| EC-9.1（systematic-review 边界） | 低 | 低 | L | ✅ |
| EC-9.2（ADR 边界） | 低 | 低 | L | ✅ |
| EC-9.3（plugin 自维护） | 低 | 中 | L | ✅ |

**高风险项（H 级）**：4 项，集中在 EC-1.2 / EC-3.1 / EC-4.4 / EC-6.1。这些必须在 Phase 0 - Phase 1 期间验证或解决。

**未覆盖待补项（⚠️）**：6 项，在实施时需补充设计或测试用例。

---

## 十一、本章小结

| 维度 | 数值 |
|---|---|
| 类别数 | 8 |
| 总风险条目数 | 31 |
| 高风险（H）数 | 4 |
| 已 Phase 覆盖比例 | 80%+ |
| 未覆盖待补项 | 6 |

**关键判断**：
- 没有发现"根本性阻塞" —— 即没有任何风险足以让整个迁移规划不可行
- 4 个高风险项均为可缓解（互调用降级方案 / Python 依赖打包 / 用户认知引导）
- 实施时按 Phase Gate 严格走，可控

**下一文档**：[`05-open-questions.md`](./05-open-questions.md) —— 当前未决问题清单，含决策方与影响面。
