# 016 - 配置管理系统 (包含智能系统追踪器)

**优先级**: P0 (基础设施)  
**状态**: 🟡 待讨论  
**预估工作量**: 4 天 (含 System Tracker)  
**来源**: 用户洞察 + 前瞻性设计需求  
**依赖**: 无（基础设施）  
**被依赖**: 013、002、003、004、008、001、017 等多个优化点

---

## 📋 1. 问题描述

### 1.1 核心痛点

**问题 1: 配置分散，缺少统一管理**
当前框架中，用户配置散落在多处（如 `generation_plan.md`、`core/language_rules.md`），且语言偏好等设置每次生成都需要重复询问，缺乏持久化记忆。

**问题 2: V3.0 功能开关无处存储**
V3.0 规划的多个优化点（如 AI 互审、危险指令拦截、ADR 系统）都需要开关配置。如果没有统一的配置系统，这些功能将难以管理。

**问题 3: 跨会话无法追踪高频操作**
框架目前无法记忆用户的习惯。例如，用户经常执行某种复杂的 `find` 命令或文件重命名操作，框架无法识别这种模式并推荐将其固化为工具。

### 1.2 V2.3 现状

- **配置**: 仅依靠文档中的硬编码规则或临时文件，无统一配置文件。
- **记忆**: 无跨会话记忆能力。

---

## 💡 2. 解决方案：配置管理系统

### 2.1 系统架构

专为**独立开发者**设计，摒弃复杂的团队配置和环境变量覆盖，保持简单纯粹。

```
config/
├── .gitignore              # 排除用户个人配置
├── README.md               # 配置系统说明文档
├── CONFIG_TEMPLATE.md      # 配置模板（框架默认值，提交到仓库）
└── user_config.md          # 用户个人配置（不提交，由用户本地管理）
```

#### config/README.md 完整内容

````markdown
# AI Coding Context 配置系统

## 📖 概述

本目录包含 AI Coding Context 框架的配置文件，用于管理框架行为和用户偏好。

## 📁 文件说明

### CONFIG_TEMPLATE.md

**作用**: 框架默认配置模板

**特点**:

- 包含所有可用配置项及其默认值
- 包含详细的配置说明和最佳实践
- 提交到 Git 仓库，随框架分发

**使用方式**:

- **查看**: 了解所有可用配置项
- **复制**: 创建个人配置时参考
- **不要修改**: 这是框架默认配置，修改无效

### user_config.md

**作用**: 用户个人配置文件

**特点**:

- 不提交到 Git（已在 .gitignore 中排除）
- 覆盖 CONFIG_TEMPLATE.md 中的默认值
- 首次使用时自动创建

**使用方式**:

1. 复制 CONFIG_TEMPLATE.md 为 user_config.md
2. 修改 frontmatter 中的配置值
3. 保存后下次运行自动生效

## 🚀 快速开始

### 首次配置

如果 `user_config.md` 不存在，框架会在首次运行时：

1. 询问基本配置（如文档语言）
2. 自动创建 `user_config.md`
3. 写入您的选择

### 手动配置

```bash
# 1. 复制模板
cp CONFIG_TEMPLATE.md user_config.md

# 2. 编辑配置
# 修改 frontmatter 中的值

# 3. 保存文件
# 配置立即生效
```
````

## ⚙️ 配置项说明

详细配置项说明请参阅 `CONFIG_TEMPLATE.md` 文档正文。

### 核心配置

- `documentLanguage` - 文档语言（zh-CN/en-US/ja-JP）
- `configVersion` - 配置版本（自动管理）

### V3.0 功能开关

- `enableMutualReview` - AI 互审机制
- `dangerousCommandGuard` - 危险指令拦截级别
- `enforceDesignThinking` - 设计思维引导
- `enableADR` - 架构决策记录
- `aiCapabilityTier` - AI 能力分级

### 用户偏好

- `preferredRoles` - 偏好的 AI 角色
- `verboseMode` - 详细输出模式
- `defaultHealthCheckMode` - 默认健康检查模式

## 🔒 安全与隐私

### 什么会被提交到 Git？

✅ **会提交**:

- `CONFIG_TEMPLATE.md` - 框架默认配置
- `README.md` - 本说明文档
- `.gitignore` - 排除规则

❌ **不会提交**:

- `user_config.md` - 您的个人配置
- `.system/` - 运行时状态数据

### 团队协作建议

本框架专为**独立开发者**设计，无团队配置功能。如果您在团队环境中使用：

1. **个人偏好**: 保留在 `user_config.md`（不提交）
2. **团队约定**: 在团队文档中说明推荐配置
3. **项目规范**: 在项目 README 中注明必需的功能开关

## 🔧 配置优先级

```
user_config.md (个人配置，最高)
       ↓
CONFIG_TEMPLATE.md (框架默认)
       ↓
硬编码默认值 (兜底)
```

## 📝 配置文件格式

采用 **Markdown + YAML Frontmatter** 格式：

```markdown
---
documentLanguage: zh-CN
enableMutualReview: false
---

# 配置说明

正文部分包含详细的配置项说明...
```

**为什么选择这种格式？**

1. ✅ 人类和 AI 都易读
2. ✅ 配置即文档，鼓励阅读
3. ✅ 符合框架统一的 Markdown 风格

## 🆘 常见问题

### Q: 配置不生效怎么办？

**检查步骤**:

1. 确认 `user_config.md` 位于 `config/` 目录
2. 确认 YAML frontmatter 格式正确
3. 查看框架启动时是否有警告信息

**降级机制**: 如果配置文件损坏，框架会自动使用默认配置并警告。

### Q: 如何恢复默认配置？

```bash
# 方法 1: 删除个人配置
rm user_config.md

# 方法 2: 重新复制模板
cp CONFIG_TEMPLATE.md user_config.md
```

### Q: 配置会影响已有项目吗？

不会。配置只影响**新生成的文档**。已有项目的文档不会自动更新。

### Q: V3.1 升级后配置会失效吗？

不会。框架采用**增量式设计**：

- 旧配置项继续有效
- 新配置项使用默认值
- 升级时会提示您查看新增配置项

## 📚 相关文档

- [AI_ENTRY_POINT.md](../../../../AI_ENTRY_POINT.md) - 框架入口
- [README.md](../../../../README.md) - 框架介绍

---

**最后更新**: 2025-12-01  
**框架版本**: V3.0

````

### 2.2 配置优先级

```mermaid
graph TD
    A[AI 读取配置] --> B{user_config.md 存在?}
    B -->|是| C[读取用户配置]
    B -->|否| D[读取 CONFIG_TEMPLATE.md]

    C --> E{配置项缺失?}
    D --> E

    E -->|是| F[使用默认值补全]
    E -->|否| G[配置加载完成]
    F --> G
````

**优先级规则**:

1. `user_config.md` (个人配置，最高优先级)
2. `CONFIG_TEMPLATE.md` (框架默认)
3. 硬编码默认值 (兜底)

### 2.3 配置文件格式

**🎯 核心设计原则**：

> **符合框架理念**：鼓励用户阅读文档
>
> 配置文件本身就是文档，用户修改配置时会理解每个选项的含义

**选择**: **Markdown + YAML Frontmatter**

**理由**:

1. ✅ **高度可读** - 人类和机器都友好
2. ✅ **自文档化** - 配置即文档，包含详细说明
3. ✅ **框架一致** - 所有框架文件都是 Markdown
4. ✅ **鼓励阅读** - 用户修改时会看到说明和最佳实践
5. ✅ **标准格式** - YAML 是广泛使用的配置格式
6. ✅ **可扩展** - 可以添加示例、最佳实践、常见问题

**格式示例**:

````markdown
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
dangerousCommandGuard: moderate
enforceDesignThinking: false
enableADR: false
aiCapabilityTier: auto
preferredRoles: []

# 用户偏好
verboseMode: false
defaultHealthCheckMode: standard
---

# 框架配置说明

> 📝 本文档记录您的个性化配置
>
> **配置方式**: 修改上方 YAML frontmatter 中的值
> **生效时机**: 下次运行框架时自动应用

---

## 🌍 文档语言

**YAML 字段**: `documentLanguage`  
**当前值**: `zh-CN`

**说明**: 控制生成文档的语言

**可选值**:

- `zh-CN` - 中文（简体，默认）
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

**说明**: 启用后，AI 生成的方案会由另一个 AI 角色审查

**可选值**:

- `true` - 启用（推荐用于重要项目）
- `false` - 禁用（默认，快速项目）

**影响**:

- ✅ 启用: 方案质量更高，发现更多问题，但生成时间 +20%
- ❌ 禁用: 生成更快，但可能遗漏问题

---

## 🛡️ 危险指令拦截

**YAML 字段**: `dangerousCommandGuard`  
**当前值**: `moderate`  
**对应优化点**: 002-危险指令拦截

**说明**: 防止 AI 执行可能导致数据丢失的危险命令

**可选值**:

- `strict` - 严格模式
  - **适用**: 生产环境、重要项目
  - **拦截**: 文件删除、数据库删除、系统级操作
  - **行为**: 拦截并拒绝执行
- `moderate` - 适中模式（默认）
  - **适用**: 开发环境
  - **拦截**: 数据库删除、系统级操作
  - **警告**: 文件删除
- `permissive` - 宽松模式
  - **适用**: 个人学习项目
  - **行为**: 仅警告，不拦截

**使用场景**:

```yaml
# 生产环境
dangerousCommandGuard: strict

# 开发环境
dangerousCommandGuard: moderate

# 个人学习项目
dangerousCommandGuard: permissive
```

---

## 🧠 设计思维引导

**YAML 字段**: `enforceDesignThinking`  
**当前值**: `false`  
**对应优化点**: 003-设计思维引导

**说明**: 是否强制 AI 进行深度设计思考（5 Why、多方案对比、边界定义）

**可选值**:

- `true` - 强制启用
  - 适用: 重要功能开发、架构设计
  - 效果: AI 必须提供多个方案对比、深度分析
- `false` - 不强制（默认）
  - 适用: 快速原型、小功能
  - 效果: AI 可以快速给出方案

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
- `false` - 禁用（默认）

---

## 🎯 AI 能力分级

**YAML 字段**: `aiCapabilityTier`  
**当前值**: `auto`  
**对应优化点**: 008-AI 能力分级

**说明**: 指定当前使用的 AI 能力级别，框架会据此调整任务复杂度

**可选值**:

- `auto` - 自动检测（默认）
- `basic` - 基础级别（GPT-3.5、Claude Haiku）
- `intermediate` - 中级（GPT-4o-mini）
- `advanced` - 高级（GPT-4、Claude Sonnet）
- `expert` - 专家级（Claude Opus、o1）

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
- `false` - 简洁输出（默认）

---

### 默认健康检查模式

**YAML 字段**: `defaultHealthCheckMode`  
**当前值**: `standard`

**说明**: 文档健康度检查的默认模式

**可选值**:

- `quick` - 快速扫描（1 分钟）
- `standard` - 标准检查（3-5 分钟，默认）
- `deep` - 深度分析（10-15 分钟）

---

## 💡 配置最佳实践

### 快速开发模式（个人学习项目）

```yaml
documentLanguage: zh-CN
enableMutualReview: false # 快速开发
dangerousCommandGuard: permissive # 宽松保护
enforceDesignThinking: false # 不强制
aiCapabilityTier: auto
```

### 标准开发模式（日常开发）

```yaml
documentLanguage: zh-CN
enableMutualReview: false
dangerousCommandGuard: moderate # 适度保护（默认）
enforceDesignThinking: false
aiCapabilityTier: auto
```

### 严格模式（重要项目/生产环境）

```yaml
enableMutualReview: true # 保证质量
dangerousCommandGuard: strict # 严格保护
enforceDesignThinking: true # 强制设计思考
enableADR: true # 记录架构决策
aiCapabilityTier: advanced # 使用高级 AI
```

---

_💡 提示: 修改 frontmatter 中的值后保存，下次运行框架时自动生效_
````

#### 4. .gitignore 配置

**config/.gitignore**:

```gitignore
# 用户个人配置，不提交到版本控制
user_config.md

# 备份文件
*.backup
*.bak
```

**用户项目 .gitignore 建议**（在 README 中提醒）:

```gitignore
# AI Coding Context 个人配置
ai_coding_context/config/user_config.md
```

---

### 2.4 实现方式

#### 1. 配置读取流程

**位置**: `AI_ENTRY_POINT.md` 最开始

**伪代码**:

```
步骤 -1: 读取配置

1. 检测 config/user_config.md
   - 存在: 解析 YAML frontmatter → userConfig
   - 不存在: userConfig = {}

2. 读取 config/CONFIG_TEMPLATE.md
   - 解析 YAML frontmatter → defaultConfig

3. 合并配置（优先级: user > default）
   finalConfig = merge(defaultConfig, userConfig)

4. 验证配置
   - 检查必需字段
   - 验证值的有效性
   - 如有问题，使用默认值并警告

5. 使用 finalConfig 进行后续流程
```

#### 2. 配置初始化流程

**首次生成时**:

```
1. 读取配置（如上）
2. 如果 user_config.md 不存在:
   - 询问用户关键配置（如语言）
   - 创建 user_config.md（从 CONFIG_TEMPLATE.md 复制）
   - 写入用户选择的值
3. 后续流程使用配置文件
```

#### 3. 配置更新机制

**用户主动修改**:

- 直接编辑 `config/user_config.md`
- 保存后下次运行自动生效

**框架自动更新**:

- 检测到新版本时，提示用户查看新增配置项
- 不自动覆盖用户配置

#### 4. 向后兼容

**V2.3 → V3.0 升级**:

```
1. 检测到旧项目（无 config/ 目录）
2. 读取 dev_docs/_analysis/generation_plan.md 中的语言配置
3. 创建 config/ 目录和 user_config.md
4. 迁移已有配置
5. 提示用户配置系统已启用
```

### 2.5 稳健性与自动修复 (Auto-Repair)

为了防止用户误修改导致配置损坏，引入自动修复机制：

#### 配置项粒度划分

**用户可见配置**（`user_config.md` frontmatter）：

- `documentLanguage` - 文档语言
- `enableMutualReview` - AI 互审开关
- `dangerousCommandGuard` - 危险指令拦截级别
- `enforceDesignThinking` - 设计思维引导开关
- `enableADR` - ADR 系统开关
- `aiCapabilityTier` - AI 能力分级
- `preferredRoles` - 偏好角色列表
- `verboseMode` - 详细模式
- `defaultHealthCheckMode` - 默认健康检查模式

**内部配置**（不暴露给用户）：

- 框架内部阈值（如复杂度计算公式）
- 系统路径配置
- 调试选项
- System Tracker 阈值（除非用户需要自定义）

#### 配置验证策略

**1. YAML 格式验证**：

```
格式错误 → 降级到 CONFIG_TEMPLATE.md + 警告用户检查配置文件
```

**2. 字段值验证**：

```yaml
# 示例：语言字段
documentLanguage: "xxx"  # 无效值
↓
使用默认值 "zh-CN" + 警告："配置项 documentLanguage 的值 'xxx' 无效，已使用默认值 'zh-CN'"
```

**3. 缺失字段处理**：

```yaml
# user_config.md 中缺失某些字段
↓
自动从 CONFIG_TEMPLATE.md 补全 + 不警告（正常情况）
```

**4. 文件丢失处理**：

```
user_config.md 不存在 → 正常（使用默认配置）
CONFIG_TEMPLATE.md 不存在 → 错误（框架损坏，提示重新安装）
```

#### 配置版本管理

**版本标识**：

```yaml
configVersion: "3.0" # 在 frontmatter 中标识
```

**升级策略**（增量式设计）：

- V3.0 → V3.1：只添加新字段，不删除旧字段
- 检测到版本不匹配时，提示用户查看新增配置项
- 旧配置项继续有效，新配置项使用默认值

**示例**：

```
用户配置版本: 3.0
框架版本: 3.1
↓
提示: "检测到新版本配置，建议查看 CONFIG_TEMPLATE.md 了解新增配置项：
  - newFeatureToggle (默认: false)
  - anotherOption (默认: auto)"
```

### 2.6 热重载机制 (Per-Session Reload)

由于本框架是基于文档的 AI 辅助工具，"运行"通常指一次 AI 会话。因此，**每次会话开始时都会重新读取配置**，用户修改后无需重启任何服务，即刻生效。

---

## 🔌 3. 扩展模块：智能系统追踪器 (System Tracker)

> 原 016.5 优化点，现作为配置系统的核心扩展模块。

### 3.1 核心概念

利用配置系统的存储能力，建立运行时状态文件 `config/.system/usage_stats.json`，用于记录高频操作，驱动工具沉淀。

### 3.2 状态存储设计

文件位置: `config/.system/usage_stats.json` (隐藏目录，避免干扰用户)

**数据结构 (简化版)**：
针对独立开发者场景，采用简化的**命令归一化**逻辑，而非复杂的指纹算法。

```json
{
  "config_version": "3.0",
  "last_updated": "2025-12-01T12:00:00Z",
  "tracking_config": {
    "command_frequency_threshold": 10,
    "time_window_days": 30,
    "enabled": true
  },
  "normalization_rules": {
    "path_placeholder": "<PATH>",
    "file_placeholder": "<FILE>",
    "ignore_flags": ["-v", "--verbose", "-h", "--help"]
  },
  "command_stats": {
    "find_js_files": {
      "pattern": "find <PATH> -name '*.js'",
      "count": 12,
      "first_used": "2025-11-15",
      "last_used": "2025-12-01"
    },
    "grep_error_logs": {
      "pattern": "grep 'Error' <FILE>",
      "count": 5,
      "first_used": "2025-11-28",
      "last_used": "2025-11-30"
    }
  },
  "tool_recommendations": [
    {
      "id": "rec_001",
      "trigger": "find_js_files > 10",
      "action": "suggest_use_tool",
      "tool_name": "project_scanner",
      "tool_path": "tools/py/project_scanner.py",
      "context": "您在30天内执行了12次JS文件查找，建议使用 project_scanner 工具，它能自动忽略 node_modules 并提供结构化输出",
      "status": "pending"
    }
  ]
}
```

### 3.3 命令归一化规则

**目标**：将相似命令归类，统计频率。

**归一化示例**：

```bash
# 原始命令
find /home/user/project/src -name '*.js'
find ./components -name '*.jsx'
find /var/www/app -name '*.ts'

# 归一化后
find <PATH> -name '*.js'  # count: 3
```

**规则**：

1. 路径替换为 `<PATH>`
2. 文件名替换为 `<FILE>`（当文件名是变量时）
3. 忽略调试标志（`-v`, `--verbose` 等）
4. 保留核心参数（`-name`, `-type` 等）

### 3.4 工作流程

**1. 记录阶段 (Record)**：

- AI 执行 shell 命令前，应用归一化规则
- 更新 `command_stats` 中的计数器
- 记录首次和最后使用时间

**2. 分析阶段 (Analyze)**：

- 每次会话开始时读取 `usage_stats.json`
- 检查是否有命令超过阈值（默认 10 次）
- 检查时间窗口（默认 30 天内）

**3. 触发阶段 (Trigger)**：

- 满足条件时生成推荐
- 提示用户："检测到您在 30 天内执行了 12 次 `find <PATH> -name '*.js'`，建议使用 `tools/py/project_scanner.py`，它能提供结构化输出并自动忽略 node_modules"

**4. 反馈阶段 (Feedback)**：

- 用户采纳推荐后，标记为 `accepted`
- 用户忽略推荐后，不再重复提示该条

---

## 📊 4. 价值评估

### 用户体验提升

1. **消除重复询问**

   - 现状: 每次生成都要选择语言
   - 改进: 只需设置一次

2. **配置透明化**

   - 现状: 不知道框架有哪些可配置项
   - 改进: 配置文件即文档，一目了然

3. **个性化**
   - 现状: 所有用户使用相同默认值
   - 改进: 可根据项目类型调整配置

### 开发效率提升

1. **统一管理**

   - 现状: 配置分散在多个文件
   - 改进: 集中在 config/ 目录

2. **易于扩展**

   - 现状: 新增配置需要修改多处
   - 改进: 只需在配置 schema 中添加

3. **工具沉淀**
   - 现状: 无法记忆高频操作
   - 改进: System Tracker 自动识别并推荐工具化

### 框架演进支持

1. **为 V3.0 铺路**

   - 多个优化点需要配置项
   - 提前建立配置系统避免后续重构

2. **可扩展性**
   - 新功能需要配置时，直接添加即可
   - 不需要修改核心工作流

---

## ⚠️ 5. 风险与疑问

### 1. 兼容性风险

**❓ 问题**: 现有 V2.3 用户升级到 V3.0，配置系统如何平滑迁移？

**方案**:

- 自动检测旧项目，创建配置文件
- 迁移已有配置（如语言偏好）
- 提供升级指南

---

### 2. 复杂度风险

**❓ 问题**: 配置系统是否会增加框架复杂度，违反 KISS 原则？

**分析**:

- ✅ 合理复杂度：配置系统是必需的基础设施
- ✅ 降低长期复杂度：避免后续重构
- ✅ 用户透明：对用户是简化（不需要重复选择）

---

### 3. Markdown 解析风险

**❓ 问题**: Markdown + YAML Frontmatter 解析复杂度如何？

**分析**:

- ✅ YAML frontmatter 是标准格式，AI 可轻松解析
- ✅ 只需解析 frontmatter，不需要解析 Markdown 正文
- ⚠️ 需要验证 YAML 格式正确性

**降级方案**: 如果解析失败，使用默认配置并警告用户

---

### 4. 已解决的问题 ✅

以下问题已在 2025-12-01 讨论中确认并解决：

1. **✅ 配置项的粒度** - 已明确划分用户可见配置和内部配置（见 2.5 节）
2. **✅ 配置验证策略** - 已定义 4 层验证策略（格式/字段值/缺失字段/文件丢失）
3. **✅ 配置版本管理** - 采用增量式设计，添加 configVersion 字段
4. **✅ 优先级调整** - 从 P1 调整为 P0（基础设施）
5. **✅ 团队配置支持** - 确认专为独立开发者设计，移除团队配置
6. **✅ System Tracker 实现细节** - 补充命令归一化规则、阈值配置和工作流程（见 3.3-3.4 节）

### 5. 待实施阶段确认的细节

以下细节可在实施阶段进一步细化，不阻碍当前确认：

1. **System Tracker 归一化算法的边界情况处理**
   - 如何处理复杂的命令管道？
   - 如何处理带引号的参数？
2. **配置文件的错误提示文案优化**
   - 具体的错误提示措辞
   - 多语言支持

以上问题不影响整体设计，可在实施时根据实际情况调整。

---

## 🎯 6. 实施计划

### Phase 1: 设计和规范（1 天）

**任务**:

1. 确认配置 schema（所有配置项及默认值）
2. 编写 `config/README.md`（配置系统说明）
3. 编写 `config/CONFIG_TEMPLATE.md`（配置模板）
4. 编写 `.gitignore` 规则

**产出**:

- 完整的配置文件模板
- 配置系统文档

---

### Phase 2: 工作流集成（1 天）

**任务**:

1. 修改 `AI_ENTRY_POINT.md`
   - 添加"步骤 -1: 读取配置"
2. 修改 `core/language_rules.md`
   - 优先读取配置，不存在时才询问
3. 修改 `workflows/detection_workflow.md`
   - 使用配置中的工具偏好
4. 修改 `workflows/document_health_check.md`
   - 使用配置中的默认检查模式
5. 更新 `README.md`
   - 在文件结构中添加 `config/`，并简要介绍配置方式
6. 更新 `CONTRIBUTING.md`
   - 添加 `config/` 目录说明，以及"如何添加新配置项"的指南

**产出**:

- 集成配置系统的工作流文档

---

### Phase 3: 向后兼容（0.5 天）

**任务**:

1. 编写升级指南
2. 实现配置迁移逻辑
3. 测试 V2.3 项目升级场景

**产出**:

- 升级指南文档
- 迁移方案

---

### Phase 4: V3.0 功能集成（0.5 天）

**任务**:

1. 为 013-001 等优化点添加配置项
2. 更新 CONFIG_TEMPLATE.md
3. 在各优化点文档中注明配置项名称

**产出**:

- 完整的 V3.0 配置 schema

---

### Phase 5: System Tracker 集成（1 天）

**任务**:

1. 创建 `config/.system/` 目录
2. 实现简单的命令归一化与计数逻辑
3. 定义初始的推荐规则

**产出**:

- 运行时状态跟踪系统

---

### 总计工作量: 4 天

---

## 🔗 7. 相关优化点

**依赖此优化点的**:

- 013-AI 互审机制
- 002-危险指令拦截
- 003-设计思维引导
- 004-ADR 系统
- 008-AI 能力分级
- 001-AI 角色库
- 017-实用脚本库（System Tracker）

**建议顺序**:

1. 先实施 016-配置管理系统（基础设施）
2. 再实施依赖它的功能优化点

---

**创建日期**: 2025-12-01  
**讨论完成日期**: 2025-12-01  
**讨论进度**: 100%
