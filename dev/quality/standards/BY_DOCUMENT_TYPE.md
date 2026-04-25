# 按文档类型的专项质量标准

> **用途**：在 `COMMON_STANDARDS.md`（五维度通用标准）与 `QUALITY_CHECKLIST.md`（快速核对）之上，为 AICC 每一类文档提供**类型专属**的检查项与反模式
> **使用方式**：审查时先核对通用标准，再按本文件查找对应类型的专项标准
> **版本**：v1.0（2026-04-25 创建，填补 quality/ 体系长期缺口）

---

## 📋 类型清单

本框架包含以下文档类型，按角色不同有不同的质量要求：

| 类型 | 典型路径 | 主要受众 | 章节 |
|---|---|---|---|
| 入口文档 | `AI_ENTRY_POINT.md`、`README.md`、`CONTRIBUTING.md` | AI / 终端用户 / 贡献者 | [§1](#1-入口文档) |
| 核心规范 | `core/*.md` | AI（强约束执行者） | [§2](#2-核心规范-coremd) |
| 工作流 | `workflows/*.md` | AI（流程执行者） | [§3](#3-工作流-workflowsmd) |
| AI 角色定义 | `agents/**/*.md` | AI（角色扮演者） | [§4](#4-ai-角色定义-agentsmd) |
| 工具脚本 | `tools/py/*.py`、`tools/js/*.js` | 主程序/Agent 调用 | [§5](#5-工具脚本-toolspypy--toolsjsjs) |
| 模板 | `templates/*.md` | AI（实例化生成器） | [§6](#6-模板-templatesmd) |
| 指南 | `guides/*.md` | 终端用户 | [§7](#7-指南-guidesmd) |
| 配置文档 | `config/*.md` | 用户 + AI | [§8](#8-配置文档-configmd) |
| ADR / 架构记录 | `dev/architecture/decisions/*.md` | 维护者 | [§9](#9-adr-架构决策记录-devarchitecturedecisions) |
| Quality 体系自身 | `dev/quality/*.md` | AI 审查者 + 维护者 | [§10](#10-quality-体系自身) |

---

## 1. 入口文档

**包含**：`AI_ENTRY_POINT.md`、`README.md`、`CONTRIBUTING.md`

### 必需章节

| 文档 | 必需章节 |
|---|---|
| `AI_ENTRY_POINT.md` | 框架定位 / 设计理念 / 工作流分派决策树 / 完整文档索引 / 何时读取何文档 |
| `README.md` | 一句话定位 / 框架是什么 / 为什么用 / 30 秒上手 / 链接到 AI_ENTRY_POINT 与 guides/quick_start |
| `CONTRIBUTING.md` | 如何提 issue / 如何提 PR / 代码规范 / 文档规范 / 框架自身审查流程入口 |

### 特定检查项

- [ ] **索引完整性**：`AI_ENTRY_POINT.md` 索引表覆盖所有 Public 层关键文档（不能遗漏新增的 workflow / template）
- [ ] **何时读取明确**：每个被索引文档的"何时读取"描述具体（禁止"需要时"这种空话）
- [ ] **决策树可执行**：工作流分派决策树有明确判断条件、覆盖典型场景、有异常分支
- [ ] **链接全部 Public**：视角 A 下，入口文档不得引用 `dev/` 任何路径（CONTRIBUTING.md 例外，因其本身面向贡献者，但需明确标注"仅 dev 分支可见"）
- [ ] **README 30 秒能读完前 10 行**：定位、价值主张、入口链接必须在头部

### 常见反模式

- ❌ 索引漏列新增文档（增量维护失败的典型症状）
- ❌ 决策树跳过异常路径（"如果检测失败"没说怎么办）
- ❌ "详见某某"链接断裂或指向 dev/
- ❌ README 头部全是 badges 而非定位描述

---

## 2. 核心规范 (core/*.md)

**包含**：`framework_spec.md`、`design_decisions.md`、`language_rules.md`、`security_rules.md`、`project_types.md`、`update_triggers.md`、`SUMMARY_FORMAT_SPEC.md`、以及 `core/project_types/*.md`

### 必需章节

- 规范的**强制性级别**（必须 / 应该 / 可以）
- **触发条件**（何时此规范生效）
- **执行方法**（AI/工具如何遵守）
- **验证方法**（如何检查是否遵守）
- **反例 + 正例**对照
- **例外情况**（如有）

### 特定检查项

- [ ] **强制性词汇明确**：使用"必须 (MUST) / 应该 (SHOULD) / 可以 (MAY)"而非模糊"建议"
- [ ] **可执行**：每条规则都能转化为 yes/no 二元判断（否则无法被 AI 或工具校验）
- [ ] **有反例**：每条核心规则至少配 1 个反例
- [ ] **与下游文档一致**：core 规范与 workflows / templates / agents 中的具体执行步骤一致
- [ ] **`security_rules.md` 红线封闭**：所有"严禁"操作在 `git_safety_workflow` / `commit_guided_update` 等下游有阻断或拦截
- [ ] **`project_types/` 目录对称**：每个项目类型文件结构对称（必含：技术栈识别、典型目录、关键文件、AI 编码禁忌、生成策略）

### 常见反模式

- ❌ "应当遵循最佳实践"（什么是最佳实践？无法验证）
- ❌ 规范定义在 core/ 但没有任何下游文档真正强制执行
- ❌ project_types 子文件结构不对称（有的有"AI 禁忌"有的没有）
- ❌ design_decisions 引用 dev/ 路径但视角 A 下断链

---

## 3. 工作流 (workflows/*.md)

**包含**：`path_a/b/c/d_*.md`、`generation_workflow.md`、`commit_guided_update.md`、`git_safety_workflow.md`、`doc_error_fix_workflow.md`、`document_health_check.md`、`incremental_update_workflow.md`、`detection_workflow.md`、`decision_workflow.md`、`monorepo_workflow.md` 等

### 必需章节

- **触发条件**：何时进入此工作流（用户指令 / 自动检测 / 上游工作流路由）
- **前置条件**：开始前必须满足什么
- **步骤序列**：编号、动词明确、有预期产出
- **流程图**：复杂工作流必须有 Mermaid 图
- **输入/输出**：每步骤的 I/O 清晰
- **异常处理**：失败 / 中断 / 降级方案
- **退出条件**：何时算完成

### 特定检查项

- [ ] **可端到端执行**：照着工作流跑一遍能产出预期结果，不需要额外猜测
- [ ] **AI 指令模板可直接复制**：步骤中给 AI 的 prompt 应可直接 copy-paste
- [ ] **流程衔接闭环**：path_a → path_b → path_c 之间的衔接条件明确，不出现"孤儿状态"
- [ ] **commit_guided_update 必须挂载 git_safety**：v3.0 强制约束，工作流中应有强制校验阻断
- [ ] **doc_error_fix_workflow 与 011 ADR 的关系标注清晰**：视角 A 下不得直接链接 dev/V3.0/confirmed/011/
- [ ] **review-workflow 在 Complex/Critical 变更下强制触发**：不能依赖人主动调用

### 常见反模式

- ❌ "AI 自行判断"（判断标准未给出，等于没说）
- ❌ 流程文字描述但无图，复杂依赖看不出来
- ❌ 异常处理只有"报告用户"，未给恢复路径
- ❌ 与 review_standards/ 下的标准不一致

---

## 4. AI 角色定义 (agents/**/*.md)

**包含**：`agents/runtime/`、`development/`、`language_specific/`、`personas/`、`workflows/`、`examples/`

### 必需章节

- **角色定位**：一句话说明"我是谁"
- **核心职责**：3-5 条，"动词 + 对象"格式
- **能力边界**：能做什么，**不能做什么**（同样重要）
- **典型 Prompt 模板**：用户如何调用此角色
- **输入/输出格式**：调用时的预期 I/O
- **与其他角色的协作关系**：被谁触发、触发谁
- **使用示例**：至少 1 个完整对话片段

### 特定检查项

- [ ] **职责非重叠**：与同目录其他角色职责边界清晰（如 `code_reviewer` vs `security_auditor`）
- [ ] **示例与定位一致**：`examples/` 中的对话样本能体现该角色的核心能力
- [ ] **Personas 角色边界合规**：`linus_torvalds` / `martin_fowler` / `uncle_bob` 等借名角色须明确"模拟其方法论"而非冒充本人，不得输出本人未公开的观点
- [ ] **language_specific 与生态对齐**：`vue3_expert` 等版本敏感角色必须标注当前对齐的框架版本
- [ ] **workflows/ 子目录角色不与 workflows/ 主目录的工作流重复**：例如 `agents/workflows/document_recommender.md` vs `agents/runtime/document_recommender.md`，应有明确分工

### 常见反模式

- ❌ 缺少"不能做什么"边界，导致 AI 角色失控
- ❌ 角色定位过度抽象（"全栈专家"）无法落地
- ❌ Personas 输出"我是 XX 本人"而非"我借鉴 XX 的方法论"
- ❌ 没有典型 Prompt 模板，用户不知如何调用

---

## 5. 工具脚本 (tools/py/*.py & tools/js/*.js)

### 必需要素

- **文件头部 docstring**：说明用途、输入、输出、退出码
- **CLI usage**：`--help` 输出明确
- **零依赖**：只允许标准库
- **跨平台兼容**：Python `python` / `python3` 双兼容；JS 兼容 Node ≥ 18 标准库
- **退出码语义**：0=成功 / 1=用户错误 / 2=系统错误（保持一致）
- **结构化输出**：默认 stdout 输出可被 grep；`--json` 输出机器可读

### V3.0 强制双版本约束

- [ ] `tools/py/<name>.py` 与 `tools/js/<name>.js` 文件名严格对应
- [ ] 两版本功能等价（CLI 参数、退出码、输出格式相同）
- [ ] `tools/fallback/` 下提供降级方案（cmd / shell 命令）

### 特定检查项

- [ ] **import 检查**：Python 仅 `import` 标准库；JS 仅 `require` Node 内置或本仓库其他 tools/
- [ ] **headers 完整**：每个脚本头部含 docstring（用途 / 用法 / 输入 / 输出 / 退出码 / 作者）
- [ ] **可独立运行**：不依赖任何全局环境变量（除非显式声明）
- [ ] **错误信息清晰**：失败时打印的错误含修复建议
- [ ] **`--help` 不报错**：所有脚本支持 `-h / --help`，输出 usage

### 常见反模式

- ❌ Python 脚本 `import requests`（违反零依赖）
- ❌ JS 脚本 `require('lodash')`（违反零依赖）
- ❌ 仅有 Py 版本无 JS（违反双版本约束）
- ❌ 脚本无 docstring 直接进入逻辑
- ❌ 错误时 `sys.exit(1)` 但没打印任何提示

### 合规扫描自动化

```bash
# 双版本对称性
diff <(ls tools/py/*.py | xargs -n1 basename | sed 's/\.py$//') \
     <(ls tools/js/*.js | xargs -n1 basename | sed 's/\.js$//')

# Python 零依赖
grep -rn "^import\|^from" tools/py/ | grep -v "import os\|import sys\|import json\|import re\|import argparse\|import pathlib\|import subprocess\|import datetime\|import collections\|import itertools\|import typing\|import functools\|import hashlib\|import textwrap\|import shutil\|import tempfile\|import logging\|import enum\|import abc\|import yaml" # 标准库白名单

# JS 零依赖
grep -rn "require(" tools/js/ | grep -v "require('fs')\|require('path')\|require('child_process')\|require('os')\|require('util')\|require('crypto')"
```

---

## 6. 模板 (templates/*.md)

### 必需要素

- **占位符规范**：使用统一格式（如 `{{var_name}}` 或 `[占位符]`），含义注释明确
- **必需章节**：模板要生成的目标文档的所有必需章节都体现
- **章节示例**：每个章节有示例值（标注"示例" 或注释）
- **复用说明**：可复制使用的指引
- **生成规则**：哪些字段 AI 自动填、哪些用户提供
- **与上游 prompt 配对**：模板配套的 generation prompt 在哪

### 特定检查项

- [ ] **占位符语义清晰**：`[项目名称]` vs `[项目类型]` 不会混淆
- [ ] **必需章节完备**：对照 `core/SUMMARY_FORMAT_SPEC.md` 检查 YAML Frontmatter 字段齐全
- [ ] **复杂度变体一致**：trivial / simple / medium / complex / critical 5 套 GENERATION_PLAN_TEMPLATE 结构对称，仅深度差异
- [ ] **AI_RULES_TEMPLATE 规则明确**：可被 IDE 直接加载执行
- [ ] **示例可运行**：模板中的代码示例可直接复制使用
- [ ] **prompts/ 与 templates/ 配对**：`templates/prompts/step1_why.md` 与设计思维步骤工作流对应

### 常见反模式

- ❌ 模板有占位符但无说明（用户不知道填什么）
- ❌ 同类模板章节不对称（complex 比 medium 多个章节但没说为什么）
- ❌ 模板示例自身不符合 SUMMARY_FORMAT_SPEC
- ❌ AI_RULES 规则模糊（如"遵守项目规范"——哪些规范？）

---

## 7. 指南 (guides/*.md)

### 必需要素

- **目标读者**：明确（新手 / 进阶 / 维护者）
- **预期用时**：30 分钟 / 1 小时 / 半天
- **前置条件**：必需的工具、知识、已完成的步骤
- **步骤可执行**：编号、命令可复制、结果可验证
- **常见问题 (FAQ)**：每个指南至少 3 个 FAQ
- **下一步**：完成后应去看哪个文档

### 特定检查项

- [ ] **30 秒能定位**：扫读标题就能判断"是不是我要看的"
- [ ] **命令可直接复制**：不含未替换的 `{{}}` 占位符
- [ ] **示例完整**：代码示例含 import / 上下文，能跑通
- [ ] **从简到难递进**：步骤难度递增，新手不被劝退
- [ ] **`quick_start.md` 真的"快"**：理论上 5-10 分钟内能跑出第一个产物
- [ ] **`faq.md` 来源真实**：FAQ 应基于实际用户提问，不是想象

### 常见反模式

- ❌ 指南越写越长，最终成"参考手册"而非"上手指引"
- ❌ 跳过环境配置直接到使用
- ❌ FAQ 全是 AI 自编（无真实场景）
- ❌ 没有"下一步去哪"

---

## 8. 配置文档 (config/*.md)

### 必需要素

- **每个配置项**含：默认值、可选值、含义、影响范围、何时修改
- **配置加载顺序**：项目级 / 用户级 / 默认值的优先级
- **示例配置**：覆盖典型场景
- **迁移说明**：如有版本变化，给出迁移步骤
- **不要在 README 里塞配置项**，用 CONFIG_TEMPLATE.md

### 特定检查项

- [ ] **CONFIG_TEMPLATE 字段齐全**：覆盖所有 V3.0 功能开关（`enableMutualReview`、`enableDesignThinking`、`enableKnowledgeReuse` 等）
- [ ] **默认值合理**：未配置时框架行为符合 90% 用户预期
- [ ] **MIGRATION_GUIDE 有版本对照**：v1 → v2 字段重命名/语义变化清晰
- [ ] **不含真实凭据**：示例中无 token / API key

---

## 9. ADR (架构决策记录, dev/architecture/decisions/)

### 必需要素（基于 ADR 模板）

- **状态**：Proposed / Accepted / Deprecated / Superseded
- **背景 (Context)**：促成此决策的力量
- **决策 (Decision)**：明确的选择
- **后果 (Consequences)**：好的、坏的、中性的
- **替代方案 (Alternatives)**：考虑过但未选
- **关联 ADR**：被谁取代 / 取代谁

### 特定检查项

- [ ] **不可变性**：已 Accepted 的 ADR 不应再修改决策本身（错了就 Superseded 一份新的）
- [ ] **编号唯一且递增**：001、002……不重号
- [ ] **决策可追溯到代码**：能找到 commit / PR 实现该决策
- [ ] **`evolution.md` 时间线与 decisions/ 一致**

### 常见反模式

- ❌ ADR 写得像设计文档（"我们将做 X"）而非决策记录（"我们已决定 X，因为 Y"）
- ❌ 反复修改已 Accepted 的 ADR
- ❌ 决策无后果分析（只说好处不说代价）

---

## 10. Quality 体系自身

`dev/quality/` 自身的文档应符合上述全部相应类型标准（如 `Framework_Review_Guidelines.md` 是规范类、`AUDIT_WORKFLOW.md` 是工作流类）。**自指一致性**是审查中的特别要求：

### 特定检查项

- [ ] **`README.md` 索引覆盖率**：与实际 Public 层文件数量对齐（不能仍停留在"30+"而实际有 200+）
- [ ] **`Framework_Review_Guidelines.md` 内部不自相矛盾**（如 dev/ 是否纳入审查）
- [ ] **被引用的 standards 文件都存在**（如本文件 `BY_DOCUMENT_TYPE.md` 长期被引用却缺失，是历史教训）
- [ ] **`contexts/` 真实数量** ≥ README 索引中标注 🔴 的数量
- [ ] **`audits/` 目录真实存在**（不能只在文档中提及但物理不存在）
- [ ] **sub-agent 名称对齐 `agents/runtime/` 真实角色**（不能引用不存在的角色名）

### 常见反模式

- ❌ Guidelines 写得很完整，但 README 索引滞后
- ❌ 引用的标准文件不存在
- ❌ 沉重的方法论文档但 audits/ 是空的（"自己不用自己"）

---

## 🔗 相关文档

- [`COMMON_STANDARDS.md`](./COMMON_STANDARDS.md) — 五维度通用标准（准确 / 完整 / 一致 / 可读 / 可操作）
- [`QUALITY_CHECKLIST.md`](./QUALITY_CHECKLIST.md) — 快速核对清单
- [`../AUDIT_WORKFLOW.md`](../AUDIT_WORKFLOW.md) — 9 步审查流程
- [`../Framework_Review_Guidelines.md`](../Framework_Review_Guidelines.md) — 全框架审查方法论

---

**版本**：v1.0
**创建日期**：2026-04-25
**维护者**：Framework Team
**说明**：本文件填补长期被引用却缺失的历史空白（HOW_TO_GENERATE_CONTEXTS / COMMON_STANDARDS / QUALITY_CHECKLIST 中均有指向）。后续每新增一类文档应在此文件追加专项章节。
