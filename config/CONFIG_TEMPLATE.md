---
# ===========================================
# AI Coding Context - 框架配置
# ===========================================

# 核心配置
configVersion: "3.0"
documentLanguage: zh-CN
frameworkVersion: v3.0
lastUpdated: 2025-12-01

# V3.0 功能开关
enableMutualReview: false
enforceDesignThinking: false
enableADR: false
enableDocReadingGuide: true
aiCapabilityTier: auto
preferredRoles: []

# 用户偏好
verboseMode: false
defaultHealthCheckMode: standard

# 工具库配置
tools:
  preferredRuntime: python # 优先使用的运行时 (python|nodejs)
  autoFallback: true # 工具失败时自动降级
  timeoutSeconds: 10 # 工具超时时间(秒)
  maxFileScan: 5000 # 最大扫描文件数

# 设计思维引导配置
design_thinking:
  auto_trigger_threshold: 60 # 自动触发阈值 (0-100, 复杂度评分)
  default_mode: standard # 默认引导模式 (standard|deep|quick)
  expert_team:
    include_security_expert: false # 是否默认包含安全专家
    include_performance_expert: false # 是否默认包含性能专家
  skip_trivial_tasks: true # 是否跳过简单任务 (如 Fix typo)

# Git 安全规范配置
git_safety:
  mode: standard # 安全模式 (strict|standard|permissive)
  protected_branches: ["main", "master", "production"] # 保护分支列表
  require_branch_naming: true # 是否要求分支命名规范
  warn_on_large_commit: true # 单commit超过500行时警告
  enable_pre_commit_hook: false # 是否启用 pre-commit hook

# 文档阅读引导配置
doc_reading_guide:
  recommendation: true    # 智能文档推荐
  recommendation_frequency: normal  # 推荐频率 (always|normal|rare|never)
  deviation_detect: true  # 理解偏差检测

# Commit-Guided Documentation 配置
commit_guided_documentation:
  enabled: true # 是否启用 Commit-Guided 功能
  commit_format:
    prefix_aliases: ["prompt", "ai", "doc"] # 触发前缀别名
    require_what: true # 是否要求 WHAT 字段
    require_why: true # 是否要求 WHY 字段
    require_how: true # 是否要求 HOW 字段
  token_optimization:
    time_window_days: 7 # 默认分析最近N天commit
    max_commits_per_batch: 50 # 单批次最多分析commit数
    enable_aggregation: true # 启用同类commit聚合
    skip_doc_only_commits: true # 跳过纯文档commit
  auto_detect_updates: true # 自动检测文档更新需求
  auto_generate_draft: true # 自动生成更新草稿
  require_user_confirmation: true # 需要用户确认
---

# 框架配置说明

> 📝 本文档记录用户的个性化配置
>
> **配置方式**: 修改上方 YAML frontmatter 中的值
> **生效时机**: 下次运行框架时自动应用

---

## 🌍 文档语言

**YAML 字段**: `documentLanguage`  
**当前值**: `zh-CN`

**说明**: 控制生成文档的语言

**可选值**:

- `zh-CN` - 中文(简体,默认)
- `en-US` - 英文
- `ja-JP` - 日语

**示例**:

```yaml
documentLanguage: en-US # 切换到英文
```

---

## 🤖 AI 互审机制

**YAML 字段**: `enableMutualReview`  
**当前值**: `false`  
**对应优化点**: 013-AI 互审

**说明**: 启用后,AI 生成的方案会由另一个 AI 角色审查

**可选值**:

- `true` - 启用(推荐用于重要项目)
- `false` - 禁用(默认,快速项目)

**影响**:

- ✅ 启用: 方案质量更高,发现更多问题,但生成时间 +20%
- ❌ 禁用: 生成更快,但可能遗漏问题

---

## 🧠 设计思维引导

**YAML 字段**: `enforceDesignThinking` (全局开关) + `design_thinking` (详细配置)  
**当前值**: `false` (全局) + 见 frontmatter (详细)  
**对应优化点**: 003-设计思维引导

**说明**: 控制 AI 是否进行深度设计思考(5 Why、多方案对比、风险评估)

### 全局开关 (`enforceDesignThinking`)

**可选值**:

- `true` - 强制启用
  - 适用: 重要功能开发、架构设计
  - 效果: AI 必须提供多个方案对比、深度分析
- `false` - 不强制(默认)
  - 适用: 快速原型、小功能
  - 效果: 根据复杂度自动判断是否启动

### 详细配置 (`design_thinking`)

#### `auto_trigger_threshold`

**类型**: `number` (0-100)  
**默认值**: `60`

**说明**: 自动触发设计思维引导的复杂度阈值

- **≥ 60 分**: AI 会主动提议启动引导流程
- **< 60 分**: 默认跳过,直接生成方案

**调优建议**:

```yaml
# 严格模式 (更频繁引导)
design_thinking:
  auto_trigger_threshold: 40

# 宽松模式 (仅复杂任务引导)
design_thinking:
  auto_trigger_threshold: 80
```

#### `default_mode`

**类型**: `string`  
**默认值**: `standard`  
**可选值**: `standard` | `deep` | `quick`

**说明**: 默认的引导模式

- `standard` - 标准引导 (完整 5 步流程)
- `deep` - 深度辩论 (多轮专家对话,适合复杂架构)
- `quick` - 快速对齐 (仅确认目标、方案、验收)

#### `expert_team`

**类型**: `object`  
**说明**: 配置专家团队组成

- `include_security_expert`: 是否默认包含安全专家 (用于安全敏感项目)
- `include_performance_expert`: 是否包含性能专家 (用于高性能要求项目)

**示例**:

```yaml
design_thinking:
  expert_team:
    include_security_expert: true # 金融、支付类项目
    include_performance_expert: true # 高并发系统
```

#### `skip_trivial_tasks`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否自动跳过简单任务 (如 Fix typo, 调整样式)

- `true` - 自动跳过 (推荐)
- `false` - 所有任务都判断复杂度

### 使用指令覆盖配置

即使配置了默认值,用户仍可通过指令覆盖:

- `@think` / `@think:standard` - 强制标准引导
- `@think:deep` - 强制深度辩论
- `@think:quick` - 强制快速对齐
- `@think:skip` - 强制跳过引导

---

## 📚 架构决策记录 (ADR)

**YAML 字段**: `enableADR`  
**当前值**: `false`  
**对应优化点**: 004-ADR 系统

**说明**: 是否启用架构决策记录系统

**可选值**:

- `true` - 启用
  - 自动为重大架构决策创建 ADR 文档
  - 提升架构演进可追溯性
- `false` - 禁用(默认)

---

## 🎯 AI 能力分级

**YAML 字段**: `aiCapabilityTier`  
**当前值**: `auto`  
**对应优化点**: 008-AI 能力分级

**说明**: 指定当前使用的 AI 能力级别,框架会据此调整任务复杂度

**可选值**:

- `auto` - 自动检测(默认)
- `basic` - 基础级别(GPT-3.5、Claude Haiku)
- `intermediate` - 中级(GPT-4o-mini)
- `advanced` - 高级(GPT-4、Claude Sonnet)
- `expert` - 专家级(Claude Opus、o1)

---

## 🎭 AI 角色偏好

**YAML 字段**: `preferredRoles`  
**当前值**: `[]`  
**对应优化点**: 001-AI 角色库

**说明**: 优先使用的 AI 角色列表

**示例**:

```yaml
preferredRoles:
  - architecture_analyst
  - security_expert
  - performance_optimizer
```

**可用角色**: 参见 `agents/` 目录

---

## ⚙️ 其他偏好

### 详细模式

**YAML 字段**: `verboseMode`  
**当前值**: `false`

**说明**: 控制 AI 输出的详细程度

- `true` - 详细解释每个步骤
- `false` - 简洁输出(默认)

---

### 默认健康检查模式

**YAML 字段**: `defaultHealthCheckMode`  
**当前值**: `standard`

**说明**: 文档健康度检查的默认模式

**可选值**:

- `quick` - 快速扫描(1 分钟)
- `standard` - 标准检查(3-5 分钟,默认)
- `deep` - 深度分析(10-15 分钟)

---

## 💡 配置最佳实践

### 快速开发模式(个人学习项目)

```yaml
documentLanguage: zh-CN
enableMutualReview: false # 快速开发
enforceDesignThinking: false # 不强制
aiCapabilityTier: auto
```

### 标准开发模式(日常开发)

```yaml
documentLanguage: zh-CN
enableMutualReview: false
enforceDesignThinking: false
aiCapabilityTier: auto
```

### 严格模式(重要项目/生产环境)

```yaml
enableMutualReview: true # 保证质量
enforceDesignThinking: true # 强制设计思考
enableADR: true # 记录架构决策
aiCapabilityTier: advanced # 使用高级 AI
```

---

## 🛠️ 工具库配置

**YAML 字段**: `tools` (对象)  
**当前值**: 见 frontmatter  
**对应优化点**: 017-实用脚本工具库

**说明**: 配置工具库的运行行为和性能参数

### `preferredRuntime`

**类型**: `string`  
**默认值**: `python`  
**可选值**: `python` | `nodejs`

**说明**: 当同时存在 Python 和 Node.js 版本时,优先使用哪个运行时

```yaml
tools:
  preferredRuntime: nodejs # 优先使用 Node.js 版本
```

### `autoFallback`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 工具失败时是否自动降级

- `true` - 自动降级（ripgrep 失败 → Python 遍历）
- `false` - 失败即停止,不尝试降级

### `timeoutSeconds`

**类型**: `number`  
**默认值**: `10`

**说明**: 工具执行的最大超时时间(秒)

**调优建议**:

- 快速 CI 环境: `5`
- 本地开发: `10`(默认)
- 慢速服务器: `15-20`

```yaml
tools:
  timeoutSeconds: 15 # 慢速环境延长超时
```

### `maxFileScan`

**类型**: `number`  
**默认值**: `5000`

**说明**: 允许扫描的最大文件数,超过此数量时:

- AI 会收到性能警告
- 建议切换到 IDE 内置工具或缩小范围

**调优建议**:

- 小型项目: `1000`
- 中型项目: `5000`(默认)
- 大型项目: `10000`(需配合优化策略)

---

## 🛡️ Git 安全规范配置 🆕

**YAML 字段**: `git_safety` (对象)  
**当前值**: 见 frontmatter  
**对应优化点**: 018-Commit-Guided Documentation

**说明**: 配置 AI 操作 Git 的安全规范,防止误操作保护分支或执行危险命令

### `mode`

**类型**: `string`  
**默认值**: `standard`  
**可选值**: `strict` | `standard` | `permissive`

**说明**: Git 安全模式

- `strict` - 严格模式

  - **适用**: 生产环境、多人协作项目
  - **行为**: Strict 规则不可覆盖,Standard 规则默认阻止
  - **示例**: 绝对禁止 force push、merge,保护分支零容忍

- `standard` - 标准模式(默认)

  - **适用**: 日常开发
  - **行为**: Strict 规则不可覆盖,Standard 规则可明确授权后放行
  - **示例**: 禁止危险操作,但允许在 feature 分支正常开发

- `permissive` - 宽松模式
  - **适用**: 个人学习项目
  - **行为**: 仅警告,不阻止

**示例**:

```yaml
# 生产环境
git_safety:
  mode: strict

# 开发环境
git_safety:
  mode: standard # 默认

# 个人项目
git_safety:
  mode: permissive
```

### `protected_branches`

**类型**: `array`  
**默认值**: `["main", "master", "production"]`

**说明**: 保护分支列表,AI 绝对不能在这些分支直接操作

**示例**:

```yaml
git_safety:
  protected_branches:
    - main
    - master
    - production
    - release/* # 支持通配符
    - hotfix/*
```

### `require_branch_naming`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否要求分支命名符合规范

- `true` - 要求 feature/xxx, bugfix/xxx, refactor/xxx 格式
- `false` - 不限制分支命名

### `warn_on_large_commit`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 单个 commit 超过 500 行时是否警告

- `true` - 警告并建议拆分 commit
- `false` - 不检查 commit 大小

### `enable_pre_commit_hook`

**类型**: `boolean`  
**默认值**: `false`

**说明**: 是否启用 pre-commit hook 进行本地拦截

- `true` - 安装 hook,在 commit 前检查格式和安全性
- `false` - 不安装 hook(默认)

**安装方式**:

```bash
python tools/py/install_hooks.py
```

---

## 📝 Commit-Guided Documentation 配置 🆕

**YAML 字段**: `commit_guided_documentation` (对象)  
**当前值**: 见 frontmatter  
**对应优化点**: 018-Commit-Guided Documentation

**说明**: 配置基于 Commit 信息的自动化文档更新功能

### `enabled`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否启用 Commit-Guided 功能

- `true` - 启用,AI 会自动解析 commit 并推荐文档更新
- `false` - 禁用,回退到传统的手动解释变更方式

### `commit_format` (对象)

#### `prefix_aliases`

**类型**: `array`  
**默认值**: `["prompt", "ai", "doc"]`

**说明**: 触发 Commit-Guided 的前缀别名,任一前缀即可触发

**示例**:

```yaml
commit_guided_documentation:
  commit_format:
    prefix_aliases: ["prompt", "ai", "智能"] # 支持中文前缀
```

**Commit 示例**:

```bash
# 方式1
git commit -m "prompt(feature): 新增用户积分系统"

# 方式2
git commit -m "ai(feature): 新增用户积分系统"

# 方式3
git commit -m "智能(feature): 新增用户积分系统"
```

#### `require_what` / `require_why` / `require_how`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否要求 commit message 包含 WHAT/WHY/HOW 字段

- `true` - 要求完整的三段式结构
- `false` - 不强制,允许部分字段缺失

### `token_optimization` (对象)

#### `time_window_days`

**类型**: `number`  
**默认值**: `7`

**说明**: 默认分析最近 N 天的 commit

**调优建议**:

- 快速迭代项目: `1-3` 天
- 正常项目: `7` 天(默认)
- 长周期项目: `30` 天

```yaml
commit_guided_documentation:
  token_optimization:
    time_window_days: 3 # 只分析最近3天
```

#### `max_commits_per_batch`

**类型**: `number`  
**默认值**: `50`

**说明**: 单批次最多分析的 commit 数量,防止 token 消耗过大

#### `enable_aggregation`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否启用同类 commit 聚合

- `true` - 聚合同类变更,减少 token 消耗 85%+
- `false` - 逐个分析,token 消耗较大

#### `skip_doc_only_commits`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否跳过纯文档 commit(避免循环更新)

- `true` - 跳过 `prompt(doc):` 类型的 commit
- `false` - 分析所有 commit

### `auto_detect_updates`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否自动检测文档更新需求

- `true` - AI 自动分析 commit 并推荐需要更新的文档
- `false` - 需要用户手动触发

### `auto_generate_draft`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否自动生成文档更新草稿

- `true` - 自动生成草稿供用户确认
- `false` - 仅提示需要更新,不生成草稿

### `require_user_confirmation`

**类型**: `boolean`  
**默认值**: `true`

**说明**: 是否需要用户确认后才执行文档更新

- `true` - 需要用户确认(推荐)
- `false` - 自动执行更新(风险较高)

---

## 💡 配置组合建议 🆕

### 个人学习项目

```yaml
git_safety:
  mode: permissive
  enable_pre_commit_hook: false

commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: false # 不强制完整格式
    require_why: false
    require_how: false
  token_optimization:
    time_window_days: 3
```

### 团队协作项目

```yaml
git_safety:
  mode: standard # 标准保护
  protected_branches: ["main", "master", "develop"]
  require_branch_naming: true
  enable_pre_commit_hook: true # 启用 hook

commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: true # 要求完整格式
    require_why: true
    require_how: true
  require_user_confirmation: true
```

### 生产环境项目

```yaml
git_safety:
  mode: strict # 严格保护
  protected_branches: ["main", "master", "production", "release/*"]
  require_branch_naming: true
  warn_on_large_commit: true
  enable_pre_commit_hook: true

commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: true
    require_why: true
    require_how: true
  token_optimization:
    time_window_days: 7
    enable_aggregation: true
  require_user_confirmation: true
```

## 📖 文档阅读引导配置 🆕

**YAML 字段**: `enableDocReadingGuide` (全局开关) + `doc_reading_guide` (详细配置)
**当前值**: `true` (全局) + 见 frontmatter (详细)
**对应优化点**: 014-文档阅读习惯引导

**说明**: 控制 AI 是否主动推荐文档和检测理解偏差

### 全局开关 (`enableDocReadingGuide`)

**可选值**:

- `true` - 启用（推荐）
  - 适用: 新项目、团队协作
  - 效果: AI 会根据任务推荐文档，检测理解偏差
- `false` - 禁用
  - 适用: 快速原型、临时项目
  - 效果: AI 直接处理需求，不推荐或检测

### 详细配置 (`doc_reading_guide`)

#### `recommendation`

**类型**: `boolean`
**默认值**: `true`

**说明**: 是否启用智能文档推荐

- `true` - AI 会根据用户任务推荐相关文档
- `false` - 不推荐文档，但保留偏差检测

#### `recommendation_frequency`

**类型**: `string`
**默认值**: `normal`

**说明**: 推荐频率控制

**可选值**:
- `always` - 每次任务都推荐
- `normal` - 正常频率（默认），每会话最多 3 次
- `rare` - 稀有频率，只在重大任务时推荐
- `never` - 等同于 `recommendation: false`

#### `deviation_detect`

**类型**: `boolean`
**默认值**: `true`

**说明**: 是否启用理解偏差检测

- `true` - AI 会检测用户理解偏差并温和提醒
- `false` - 不检测偏差，但保留文档推荐

---

### 配置组合建议

#### 严格模式（推荐用于重要项目）
```yaml
enableDocReadingGuide: true
doc_reading_guide:
  recommendation: true
  recommendation_frequency: normal
  deviation_detect: true
```

#### 快速模式（跳过推荐，只保留检测）
```yaml
enableDocReadingGuide: true
doc_reading_guide:
  recommendation: false
  deviation_detect: true
```

#### 极简模式（完全关闭）
```yaml
enableDocReadingGuide: false
```

---

_💡 提示: 修改 frontmatter 中的值后保存,下次运行框架时自动生效_
