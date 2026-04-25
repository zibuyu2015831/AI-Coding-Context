---
title: 文档摘要格式规范
summary: 定义 AICC 框架所有 Markdown 文档强制 frontmatter 摘要的字段、格式、严格模式校验规则；为 V3.0-012 强制文档摘要机制的规范源（自指：本文件首部含示范级 frontmatter 作为规范的自证）
keywords: frontmatter | summary | spec | yaml | v3-012
scope: 框架内所有 .md 文档的 frontmatter 标准
related_files: tools/py/summary_validator.py | tools/py/summary_extractor.py | dev/V3.0/confirmed/012-mandatory-doc-summary
dependencies: 无
verified_at: 2026-04-26
---

# 文档摘要格式规范

**版本**: v1.0  
**最后更新**: 2025-12-03  
**所属**: V3.0 - 012-强制文档摘要机制

---

## 📋 概述

本文档定义了框架中所有文档的标准化摘要格式。摘要使用 **YAML Frontmatter** 格式，位于文档开头，包含 7 个核心字段。

### 核心价值

1. **快速判断相关性** - AI 仅读摘要即可判断是否需要完整阅读，节省 60-70% Token
2. **建立文档-代码关联** - 通过 `related_files` 字段自动检测需要更新的文档
3. **准确定位文档** - 通过 `keywords` 和 `scope` 字段快速查找
4. **追踪文档健康度** - 通过 `verified_at` 字段监控文档时效性

---

## 🔧 格式定义

### 完整示例

```markdown
---
title: API 层设计规范
summary: 定义前端 API 调用的统一接口规范，包括请求封装、错误处理和类型定义
keywords: API | HTTP | Axios | 错误处理 | 类型定义
scope: 前端 API 层 (src/api/)
related_files: src/api/http.ts | src/api/types.ts | src/api/user.ts | src/api/post.ts
dependencies: dev_docs/state_management.md | dev_docs/authentication.md
verified_at: 2025-12-03
---

# API 层设计规范

（文档正文内容...）
```

---

## 📊 字段详解

### 1. title（必填）

**定义**: 文档的完整标题

**格式**: 单行字符串，30-60 个汉字或 50-100 个英文字符

**要求**:

- 必须准确反映文档主题
- 避免过于简略或过于冗长
- 使用规范的技术术语

**示例**:

```yaml
# ✅ 正确
title: API 层设计规范
title: 数据库 Schema 设计文档
title: 增量更新工作流

# ❌ 错误
title: API  # 过于简略
title: 这是一个关于前端API层设计的完整规范文档包括所有接口定义  # 过于冗长
```

---

### 2. summary（必填）

**定义**: 文档内容的精炼概述

**格式**: 1-3 句话，100-200 个汉字或 150-300 个英文字符

**要求**:

- 说明文档的核心内容
- 突出关键规范或流程
- 避免重复 `title` 的内容
- 必须是完整的句子

**示例**:

```yaml
# ✅ 正确
summary: 定义前端 API 调用的统一接口规范，包括请求封装、错误处理和类型定义

# ❌ 错误
summary: API 规范  # 过于简略，未说明核心内容
summary: API 层设计规范  # 仅重复标题
```

---

### 3. keywords（必填）

**定义**: 文档的关键词列表，用于快速匹配和检索

**格式**: 使用 `|` 分隔的单行字符串，3-8 个关键词

**要求**:

- 必须单行，不能换行
- 使用 `|` 分隔，前后可以有空格
- 包含技术栈、核心概念、主要功能
- 优先使用用户可能搜索的术语

**示例**:

```yaml
# ✅ 正确
keywords: API | HTTP | Axios | 错误处理 | 类型定义
keywords: 数据库 | PostgreSQL | Schema | 迁移 | 关系模型
keywords: 工作流 | 增量更新 | 文档维护 | Git | 变更检测

# ❌ 错误
keywords: API, HTTP, Axios  # 使用了逗号而非竖线
keywords: |  # 多行格式
  - API
  - HTTP
```

---

### 4. scope（必填）

**定义**: 文档涵盖的范围或边界

**格式**: 简短描述，可选包含代码路径

**要求**:

- 说明文档的适用范围
- 如果是代码相关文档，应包含主要目录或模块
- 格式：`<范围描述> (<代码路径>)`（可选）

**示例**:

```yaml
# ✅ 正确
scope: 前端 API 层 (src/api/)
scope: 后端数据库设计 (server/database/)
scope: 框架文档生成工作流
scope: V3.0 配置管理系统 (config/)

# ❌ 错误
scope: 整个项目  # 过于宽泛
scope: src/api/http.ts  # 过于具体（应在 related_files）
```

---

### 5. related_files（必填）

**定义**: 文档中提及或关联的所有代码文件路径

**格式**: 使用 `|` 分隔的单行字符串

**重要性**: ⭐⭐⭐⭐⭐（最关键字段）

**用途**:

- 代码变更时自动检测需要更新的文档
- 建立文档与代码的双向关联
- 支持影响分析

**提取规则**:

1. **包含所有在文档正文中明确提及的源代码文件**

   - 作为示例引用的文件
   - 在规范中说明的文件
   - 流程图中涉及的文件

2. **不包含**:

   - 其他文档（放入 `dependencies`）
   - 配置文件（除非是文档主题）
   - 测试文件（除非是测试文档）
   - 第三方库文件

3. **路径格式**:
   - 使用相对于项目根目录的路径
   - 保持与项目中实际路径一致
   - 使用正斜杠 `/`（跨平台兼容）

**示例**:

```yaml
# ✅ 正确
related_files: src/api/http.ts | src/api/types.ts | src/api/user.ts | src/api/post.ts

# 架构文档可能包含多个模块
related_files: src/core/App.tsx | src/router/index.ts | src/store/index.ts | src/plugins/i18n.ts

# 工作流文档可能不包含代码文件
related_files: 无

# ❌ 错误
related_files: |  # 多行格式
  - src/api/http.ts
  - src/api/types.ts

related_files: http.ts, types.ts  # 使用逗号，且缺少路径

related_files: dev_docs/state_management.md  # 文档应在 dependencies
```

**验证**:

- 文件路径必须存在（summary_validator 会检查）
- 路径格式必须统一
- 如果文档不涉及代码，填写 `无`

---

### 6. dependencies（必填）

**定义**: 文档依赖或关联的其他文档

**格式**: 使用 `|` 分隔的单行字符串

**要求**:

- 列出文档中引用或需要配合阅读的其他文档
- 使用相对于项目根目录的路径
- 如果无依赖，填写 `无`

**示例**:

```yaml
# ✅ 正确
dependencies: dev_docs/state_management.md | dev_docs/authentication.md

# 主文档可能依赖多个子文档
dependencies: dev_docs/api_layer.md | dev_docs/database_schema.md | workflows/generation_workflow.md

# 独立文档
dependencies: 无

# ❌ 错误
dependencies: 状态管理文档  # 应使用路径
```

---

### 7. verified_at（必填）

**定义**: 摘要最后验证或更新的日期

**格式**: `YYYY-MM-DD`

**要求**:

- 使用 ISO 8601 日期格式
- 每次更新文档内容时必须更新此字段
- 用于检测过期文档（超过 90 天）

**示例**:

```yaml
# ✅ 正确
verified_at: 2025-12-03

# ❌ 错误
verified_at: 2025/12/03  # 错误的分隔符
verified_at: 12-03-2025  # 错误的顺序
verified_at: 2025-12-3   # 缺少前导零
```

---

## ✅ 完整示例

### 示例 1: API 文档

```markdown
---
title: API 层设计规范
summary: 定义前端 API 调用的统一接口规范，包括请求封装、错误处理和类型定义
keywords: API | HTTP | Axios | 错误处理 | 类型定义
scope: 前端 API 层 (src/api/)
related_files: src/api/http.ts | src/api/types.ts | src/api/user.ts | src/api/post.ts
dependencies: dev_docs/state_management.md | dev_docs/authentication.md
verified_at: 2025-12-03
---
```

### 示例 2: 工作流文档

```markdown
---
title: 增量更新工作流
summary: 定义代码变更后文档更新的标准流程，包括变更检测、影响分析和更新策略
keywords: 工作流 | 增量更新 | 文档维护 | Git | 变更检测
scope: 框架文档维护流程
related_files: 无
dependencies: workflows/generation_workflow.md | workflows/document_health_check.md
verified_at: 2025-12-03
---
```

### 示例 3: 工具文档

```markdown
---
title: 摘要提取工具使用指南
summary: 提供从文档中提取 YAML Frontmatter 摘要的命令行工具，支持单文件和批量模式
keywords: 工具 | 摘要提取 | Python | Node.js | CLI
scope: 框架工具库 (tools/)
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js
dependencies: core/SUMMARY_FORMAT_SPEC.md | tools/README.md
verified_at: 2025-12-03
---
```

---

## 🚨 常见错误

### 错误 1: 多行格式

```yaml
# ❌ 错误
keywords: |
  - API
  - HTTP
  - Axios

# ✅ 正确
keywords: API | HTTP | Axios
```

### 错误 2: 使用逗号分隔

```yaml
# ❌ 错误
related_files: src/api/http.ts, src/api/types.ts

# ✅ 正确
related_files: src/api/http.ts | src/api/types.ts
```

### 错误 3: 文档路径写在 related_files

```yaml
# ❌ 错误
related_files: src/api/http.ts | dev_docs/state_management.md

# ✅ 正确
related_files: src/api/http.ts
dependencies: dev_docs/state_management.md
```

### 错误 4: 相对路径不一致

```yaml
# ❌ 错误
related_files: ./src/api/http.ts | api/types.ts | /src/api/user.ts

# ✅ 正确
related_files: src/api/http.ts | src/api/types.ts | src/api/user.ts
```

---

## 🔍 验证工具

框架提供了自动验证工具 `summary_validator`：

```bash
# Python
python tools/py/summary_validator.py --file dev_docs/api_layer.md

# Node.js
node tools/js/summary_validator.js --file dev_docs/api_layer.md
```

**验证内容**:

1. YAML Frontmatter 格式是否正确
2. 所有必填字段是否存在
3. `related_files` 和 `dependencies` 中的文件是否存在
4. `verified_at` 是否过期（> 90 天）
5. 字段格式是否符合规范

---

## 📚 相关文档

- [示例集合](../guides/examples/summary_examples/) - 5 种文档类型的完整示例
- [工具使用指南](../tools/README.md) - 摘要相关工具说明
- [文档生成工作流](../workflows/generation_workflow.md) - 如何生成摘要

---

**文档版本**: v1.0  
**维护者**: Framework Team  
**反馈**: 如有疑问请通过仓库 Issues 提出（贡献者另请参见 `CONTRIBUTING.md`）
