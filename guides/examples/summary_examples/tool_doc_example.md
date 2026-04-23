# 工具文档摘要示例

本文档展示工具类文档的标准摘要格式。

---

## 完整示例

```markdown
---
title: 摘要提取工具使用指南
summary: 提供从 Markdown 文档中提取 YAML Frontmatter 摘要的命令行工具，支持单文件和批量模式，输出 JSON 格式
keywords: 工具 | CLI | 摘要提取 | Python | Node.js | YAML | JSON
scope: 框架工具库 (tools/)
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js
dependencies: core/SUMMARY_FORMAT_SPEC.md | tools/README.md | tools/CHANGELOG.md
verified_at: 2025-12-03
---

# 摘要提取工具使用指南

## 概述

\`summary_extractor\` 是一个跨平台命令行工具，用于从 Markdown 文档中提取 YAML Frontmatter 摘要。

## 工具文件

### Python 版本

**文件**: \`tools/py/summary_extractor.py\`

**特点**:

- 零依赖（仅使用 Python 标准库）
- 支持 YAML 解析和正则备用方案
- 10 秒超时机制
- JSON 格式输出

### Node.js 版本

**文件**: \`tools/js/summary_extractor.js\`

**特点**:

- 与 Python 版本功能一致
- 适合前端项目使用

## 使用方法

### 单文件模式

\`\`\`bash

# Python

python tools/py/summary_extractor.py --file dev_docs/api_layer.md

# Node.js

node tools/js/summary_extractor.js --file dev_docs/api_layer.md
\`\`\`

**输出**:
\`\`\`json
{
"success": true,
"data": {
"title": "API 层设计规范",
"summary": "定义前端 API 调用的统一接口规范...",
"keywords": ["API", "HTTP", "Axios"],
"scope": "前端 API 层 (src/api/)",
"related_files": ["src/api/http.ts", "src/api/types.ts"],
"dependencies": ["dev_docs/state_management.md"],
"verified_at": "2025-12-03"
},
"metadata": {
"file_path": "dev_docs/api_layer.md",
"elapsed_seconds": 0.12
}
}
\`\`\`

### 批量模式

\`\`\`bash

# Python

python tools/py/summary_extractor.py --batch-mode --dir dev_docs/

# Node.js

node tools/js/summary_extractor.js --batch-mode --dir dev_docs/
\`\`\`

**输出**:
\`\`\`json
{
"success": true,
"data": [
{
"file": "dev_docs/api_layer.md",
"summary": { ... }
},
{
"file": "dev_docs/state_management.md",
"summary": { ... }
}
],
"metadata": {
"total_files": 15,
"successful": 14,
"failed": 1,
"elapsed_seconds": 1.8
}
}
\`\`\`

## 错误处理

### 无摘要文档

\`\`\`json
{
"success": false,
"error": "no_summary_found",
"message": "文档未包含 YAML Frontmatter 摘要"
}
\`\`\`

### 格式错误

\`\`\`json
{
"success": false,
"error": "yaml_parse_error",
"message": "YAML 解析失败: invalid syntax at line 3"
}
\`\`\`

## 技术实现

### YAML 解析

优先使用 YAML 解析库（Python 标准库 \`yaml\`，Node.js \`js-yaml\`）

### 正则备用方案

当 YAML 解析失败时，使用正则表达式提取字段：

\`\`\`python
pattern = r'^---\\s*\\n(.+?)\\n---\\s*\\n'
\`\`\`

### 性能优化

- 单文件: \u003c 0.5 秒
- 批量（50 个文档）: \u003c 5 秒
- 超时机制: 10 秒自动中断

## 配合其他工具

### 与 summary_validator 联用

\`\`\`bash

# 先提取，再验证

python tools/py/summary_extractor.py --file doc.md | \\
python tools/py/summary_validator.py --from-stdin
\`\`\`

### 与 git_diff_analyzer 联用

\`\`\`bash

# 检测变更并提取摘要

python tools/py/git_diff_analyzer.py --since "7 days ago" | \\
python tools/py/summary_related_checker.py --from-stdin | \\
python tools/py/summary_extractor.py --files-from-stdin
\`\`\`
```

---

## 字段说明

### title

- **值**: `摘要提取工具使用指南`
- **说明**: 清晰说明是工具使用文档

### summary

- **值**: `提供从 Markdown 文档中提取 YAML Frontmatter 摘要的命令行工具，支持单文件和批量模式，输出 JSON 格式`
- **说明**:
  - 说明工具功能（提取摘要）
  - 说明关键特性（单文件/批量模式、JSON 输出）
  - 说明输入和输出格式

### keywords

- **值**: `工具 | CLI | 摘要提取 | Python | Node.js | YAML | JSON`
- **说明**:
  - 文档类型：工具、CLI
  - 工具功能：摘要提取
  - 技术栈：Python、Node.js
  - 数据格式：YAML、JSON

### scope

- **值**: `框架工具库 (tools/)`
- **说明**:
  - 说明文档范围（框架工具库）
  - 指定目录（tools/）

### related_files

- **值**: `tools/py/summary_extractor.py | tools/js/summary_extractor.js`
- **说明**:
  - 包含工具的实现文件（Python 和 Node.js 版本）
  - **重点**: 工具文档必须包含工具文件

### dependencies

- **值**: `core/SUMMARY_FORMAT_SPEC.md | tools/README.md | tools/CHANGELOG.md`
- **说明**:
  - 摘要格式规范（工具处理的数据格式）
  - 工具库总体说明
  - 工具变更日志

### verified_at

- **值**: `2025-12-03`
- **说明**: 标准日期格式

---

## 工具文档特点

### related_files 选择原则

**必须包含**:

- ✅ 工具的所有实现文件（Python、Node.js、Shell 等）
- ✅ 工具的配置文件（如有）
- ✅ 工具的数据文件（Schema、模板等）

**不包含**:

- ❌ 工具的测试文件（除非文档专门说明测试）
- ❌ 工具的示例输出文件
- ❌ 其他工具文件

**示例**:

```yaml
# 单一工具
related_files: tools/py/summary_extractor.py

# 跨平台工具
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js

# 带配置的工具
related_files: tools/py/analyzer.py | tools/config/analyzer_config.json

# 带数据文件的工具
related_files: tools/py/generator.py | tools/templates/output_template.md
```

### keywords 建议

工具文档的 keywords 应包含：

1. 文档类型：工具、CLI、脚本
2. 工具功能：提取、验证、生成、转换
3. 技术栈：Python、Node.js、Shell
4. 数据格式：JSON、YAML、Markdown

---

## ✅ 正确示例

### 示例 1: 单一脚本工具

```yaml
---
title: Git Diff Analyzer 使用指南
summary: 分析 Git 代码变更历史，识别变更类型、影响范围和优先级，输出 JSON 格式报告
keywords: 工具 | Git | 代码分析 | 变更检测 | Python | Node.js
scope: 框架工具库 (tools/)
related_files: tools/py/git_diff_analyzer.py | tools/js/git_diff_analyzer.js
dependencies: tools/README.md | workflows/incremental_update_workflow.md
verified_at: 2025-12-03
---
```

### 示例 2: 复杂工具（带配置）

```yaml
---
title: 项目分析工具使用指南
summary: 扫描项目代码结构、依赖关系和复杂度指标，支持自定义分析规则和输出格式
keywords: 工具 | 项目分析 | 代码扫描 | 依赖分析 | 复杂度 | 配置
scope: 框架工具库 (tools/)
related_files: tools/py/project_analyzer.py | tools/js/project_analyzer.js | tools/config/analyzer_rules.json
dependencies: tools/README.md | core/analysis_metrics.md
verified_at: 2025-12-03
---
```

### 示例 3: 工具库总览

```yaml
---
title: 框架工具库使用指南
summary: 提供框架所有工具的总览、开发规范、使用示例和故障排除指南
keywords: 工具 | 工具库 | CLI | 开发规范 | Python | Node.js
scope: 框架工具库 (tools/)
related_files: tools/README.md | tools/CHANGELOG.md
dependencies: core/tool_development_guide.md
verified_at: 2025-12-03
---
```

---

## ❌ 常见错误

### 错误 1: 缺少工具实现文件

```yaml
# ❌ 错误
title: 摘要提取工具使用指南
related_files: 无

# ✅ 正确
title: 摘要提取工具使用指南
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js
```

### 错误 2: 包含测试文件

```yaml
# ❌ 错误
related_files: tools/py/summary_extractor.py | tools/tests/test_summary_extractor.py

# ✅ 正确
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js
```

### 错误 3: summary 没有说明关键特性

```yaml
# ❌ 错误
summary: 摘要提取工具

# ✅ 正确
summary: 提供从 Markdown 文档中提取 YAML Frontmatter 摘要的命令行工具，支持单文件和批量模式，输出 JSON 格式
```

---

## 📝 工具文档 vs 工作流文档

### 区别

| 维度              | 工具文档                     | 工作流文档                 |
| ----------------- | ---------------------------- | -------------------------- |
| **目的**          | 说明工具的实现和用法         | 说明流程和步骤             |
| **related_files** | 必须包含工具文件             | 通常为 `无`                |
| **keywords**      | 工具、脚本、CLI              | 工作流、流程、步骤         |
| **内容重点**      | 命令参数、输出格式、技术实现 | 流程步骤、决策点、协作方式 |

### 示例对比

**工具文档**:

```yaml
title: 摘要提取工具使用指南
scope: 框架工具库 (tools/)
related_files: tools/py/summary_extractor.py | tools/js/summary_extractor.js
keywords: 工具 | CLI | 摘要提取
```

**工作流文档**:

```yaml
title: 增量更新工作流
scope: 框架文档维护流程
related_files: 无
keywords: 工作流 | 增量更新 | 文档维护
```

---

**相关文档**:

- [SUMMARY_FORMAT_SPEC.md](../SUMMARY_FORMAT_SPEC.md) - 完整格式规范
- [workflow_doc_example.md](./workflow_doc_example.md) - 工作流文档示例
