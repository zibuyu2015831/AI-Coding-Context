# 配置文档摘要示例

本文档展示配置类文档的标准摘要格式。

---

## 完整示例

```markdown
---
title: 用户配置文件规范
summary: 定义框架用户配置文件的结构和字段说明，包括语言偏好、功能开关、文档详细程度和工具选择
keywords: 配置 | 用户偏好 | 功能开关 | YAML | Markdown
scope: 配置管理系统 (config/)
related_files: config/CONFIG_TEMPLATE.md | config/.system/recommended_config.md
dependencies: config/README.md | config/MIGRATION_GUIDE.md
verified_at: 2025-12-03
---

# 用户配置文件规范

## 概述

用户配置文件使用 **Markdown + YAML Frontmatter** 格式，位于项目根目录 \`config/user_config.md\`。

## 文件格式

## \`\`\`markdown

# 基础配置

document_language: zh-CN
detail_level: normal

# V3.0 功能开关

v3_features:
ai_mutual_review: true
dangerous_command_guard: true
design_thinking_guide: false

# 工具偏好

preferred_tools:
package_manager: npm
script_language: python

---

# 我的项目配置

（可选的配置说明...）
\`\`\`

## 配置字段

### 1. document_language

**类型**: string  
**可选值**: \`zh-CN\` | \`en-US\`  
**默认值**: \`zh-CN\`  
**说明**: 生成文档的默认语言

### 2. detail_level

**类型**: string  
**可选值**: \`concise\` | \`normal\` | \`detailed\`  
**默认值**: \`normal\`  
**说明**:

- \`concise\`: 简洁模式，仅核心信息
- \`normal\`: 标准模式，平衡详细程度
- \`detailed\`: 详细模式，包含所有细节

### 3. v3_features

**类型**: object  
**说明**: V3.0 功能开关配置

**子字段**:

- \`ai_mutual_review\`: AI 互审机制（默认 true）
- \`dangerous_command_guard\`: 危险指令拦截（默认 true）
- \`design_thinking_guide\`: 设计思维引导（默认 false）

### 4. preferred_tools

**类型**: object  
**说明**: 工具偏好配置

**子字段**:

- \`package_manager\`: 包管理器（npm | yarn | pnpm）
- \`script_language\`: 脚本语言（python | nodejs）

## 配置文件位置

### 用户配置

\`config/user_config.md\` - 个人配置，不提交到 Git

### 团队配置

\`config/team_config.md\` - 团队共享配置，提交到 Git

### 系统配置

\`config/.system/recommended_config.md\` - 框架推荐配置，只读

## 优先级

\`\`\`
用户配置 (user_config.md)
↓ 覆盖
团队配置 (team_config.md)
↓ 覆盖
系统配置 (.system/recommended_config.md)
\`\`\`
```

---

## 字段说明

### title

- **值**: `用户配置文件规范`
- **说明**: 清晰说明是配置规范文档

### summary

- **值**: `定义框架用户配置文件的结构和字段说明，包括语言偏好、功能开关、文档详细程度和工具选择`
- **说明**:
  - 说明文档目的（定义配置文件）
  - 列举主要配置项（语言、功能开关等）

### keywords

- **值**: `配置 | 用户偏好 | 功能开关 | YAML | Markdown`
- **说明**:
  - 核心概念：配置、用户偏好、功能开关
  - 技术格式：YAML, Markdown

### scope

- **值**: `配置管理系统 (config/)`
- **说明**:
  - 说明文档范围（配置管理系统）
  - 指定目录（config/）

### related_files

- **值**: `config/CONFIG_TEMPLATE.md | config/.system/recommended_config.md`
- **说明**:
  - 包含配置模板文件
  - 包含系统推荐配置
  - **注意**: 不包含用户的实际配置文件（user_config.md, team_config.md），因为这些是**用户数据**，不是**规范定义**

### dependencies

- **值**: `config/README.md | config/MIGRATION_GUIDE.md`
- **说明**:
  - 配置系统使用指南
  - 配置迁移指南

### verified_at

- **值**: `2025-12-03`
- **说明**: 标准日期格式

---

## 配置文档特点

### related_files 选择原则

**包含**:

- ✅ 配置模板文件（CONFIG_TEMPLATE.md）
- ✅ 系统配置文件（.system/\*.md）
- ✅ 配置 Schema 文件（如有）

**不包含**:

- ❌ 用户实际配置文件（user_config.md）
- ❌ 团队配置文件（team_config.md）
- ❌ 临时配置文件
- ❌ 配置备份文件

**原因**: 配置规范文档关注的是**格式和字段定义**，而非具体的配置实例。用户配置文件是**数据**，不是**规范**。

### keywords 建议

配置文档的 keywords 应包含：

1. 核心概念：配置、设置、偏好
2. 配置类型：用户配置、团队配置、环境配置
3. 配置格式：YAML、JSON、Markdown
4. 配置内容：功能开关、语言、工具

---

## ✅ 正确示例

### 示例 1: 环境配置文档

```yaml
---
title: 环境变量配置规范
summary: 定义应用运行所需的环境变量，包括数据库连接、API 密钥、服务端口和日志级别
keywords: 配置 | 环境变量 | .env | 数据库 | API 密钥
scope: 应用环境配置 (根目录)
related_files: .env.example | .env.production.example | docker-compose.yml
dependencies: dev_docs/deployment.md | dev_docs/database_schema.md
verified_at: 2025-12-03
---
```

### 示例 2: 构建配置文档

```yaml
---
title: Vite 构建配置说明
summary: 定义 Vite 构建工具的配置选项，包括别名设置、插件配置、构建优化和开发服务器选项
keywords: 配置 | Vite | 构建 | 别名 | 插件 | 优化
scope: 前端构建配置 (根目录)
related_files: vite.config.ts | tsconfig.json | env.d.ts
dependencies: dev_docs/project_structure.md
verified_at: 2025-12-03
---
```

### 示例 3: TypeScript 配置文档

```yaml
---
title: TypeScript 配置规范
summary: 定义 TypeScript 编译器选项和项目配置，包括模块解析、类型检查、路径映射和编译目标
keywords: 配置 | TypeScript | tsconfig | 编译选项 | 类型检查
scope: TypeScript 配置 (根目录)
related_files: tsconfig.json | tsconfig.node.json
dependencies: dev_docs/coding_standards.md
verified_at: 2025-12-03
---
```

---

## ❌ 常见错误

### 错误 1: 将用户配置文件列为 related_files

```yaml
# ❌ 错误
title: 用户配置文件规范
related_files: config/user_config.md | config/team_config.md | config/CONFIG_TEMPLATE.md

# ✅ 正确
title: 用户配置文件规范
related_files: config/CONFIG_TEMPLATE.md | config/.system/recommended_config.md
```

**理由**:

- `user_config.md` 是用户数据，不是规范
- 规范文档只关联**模板**和**示例**，不关联**实例**

### 错误 2: summary 没有列举配置项

```yaml
# ❌ 错误
summary: 用户配置文件格式说明

# ✅ 正确
summary: 定义框架用户配置文件的结构和字段说明，包括语言偏好、功能开关、文档详细程度和工具选择
```

### 错误 3: scope 过于宽泛

```yaml
# ❌ 错误
scope: 整个项目的配置

# ✅ 正确
scope: 配置管理系统 (config/)
```

---

## 📝 配置文档 vs 配置文件

### 区别

| 维度              | 配置规范文档         | 配置文件           |
| ----------------- | -------------------- | ------------------ |
| **目的**          | 说明配置格式和字段   | 存储实际配置值     |
| **格式**          | Markdown（包含示例） | YAML / JSON / .env |
| **版本控制**      | 必须提交 Git         | 视情况而定         |
| **related_files** | 包含模板和示例       | N/A（配置是数据）  |

### 示例对比

**配置规范文档** (`dev_docs/config_spec.md`):

```yaml
title: 用户配置文件规范
scope: 配置管理系统 (config/)
related_files: config/CONFIG_TEMPLATE.md
```

**配置模板** (`config/CONFIG_TEMPLATE.md`):

```yaml
---
document_language: zh-CN
detail_level: normal
---
```

**用户配置** (`config/user_config.md`) - 不是文档，是数据:

```yaml
---
document_language: en-US
detail_level: detailed
---
```

---

**相关文档**:

- [SUMMARY_FORMAT_SPEC.md](../../../core/SUMMARY_FORMAT_SPEC.md) - 完整格式规范
- [tool_doc_example.md](./tool_doc_example.md) - 工具文档示例
