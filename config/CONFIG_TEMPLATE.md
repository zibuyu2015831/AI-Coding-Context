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

# 工具库配置 (V3.0 新增)
tools:
  preferredRuntime: python # 优先使用的运行时 (python|nodejs)
  autoFallback: true # 工具失败时自动降级
  timeoutSeconds: 10 # 工具超时时间(秒)
  maxFileScan: 5000 # 最大扫描文件数
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
- `moderate` - 适中模式(默认)
  - **适用**: 开发环境
  - **拦截**: 数据库删除、系统级操作
  - **警告**: 文件删除
- `permissive` - 宽松模式
  - **适用**: 个人学习项目
  - **行为**: 仅警告,不拦截

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

**说明**: 是否强制 AI 进行深度设计思考(5 Why、多方案对比、边界定义)

**可选值**:

- `true` - 强制启用
  - 适用: 重要功能开发、架构设计
  - 效果: AI 必须提供多个方案对比、深度分析
- `false` - 不强制(默认)
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
dangerousCommandGuard: permissive # 宽松保护
enforceDesignThinking: false # 不强制
aiCapabilityTier: auto
```

### 标准开发模式(日常开发)

```yaml
documentLanguage: zh-CN
enableMutualReview: false
dangerousCommandGuard: moderate # 适度保护(默认)
enforceDesignThinking: false
aiCapabilityTier: auto
```

### 严格模式(重要项目/生产环境)

```yaml
enableMutualReview: true # 保证质量
dangerousCommandGuard: strict # 严格保护
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

_💡 提示: 修改 frontmatter 中的值后保存,下次运行框架时自动生效_
