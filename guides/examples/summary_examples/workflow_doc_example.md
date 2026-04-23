# 工作流文档摘要示例

本文档展示工作流类文档的标准摘要格式。

---

## 完整示例

```markdown
---
title: 增量更新工作流
summary: 定义代码变更后文档更新的标准流程，包括变更检测、影响分析、更新策略和验证机制
keywords: 工作流 | 增量更新 | 文档维护 | Git | 变更检测 | 影响分析
scope: 框架文档维护流程
related_files: 无
dependencies: workflows/generation_workflow.md | workflows/document_health_check.md | tools/README.md
verified_at: 2025-12-03
---

# 增量更新工作流

## 概述

本工作流定义了代码变更后如何检测和更新相关文档的标准流程。

## 触发条件

- P0: API 变更、Schema 变更、核心模块重构
- P1: 新增模块、流程调整、配置变更
- P2: 性能优化、代码重构、注释更新

## 流程

### 1. 变更检测

使用 \`git_diff_analyzer\` 工具分析代码变更：

\`\`\`bash
python tools/py/git_diff_analyzer.py --since "7 days ago"
\`\`\`

### 2. 影响分析

使用 \`summary_related_checker\` 识别受影响的文档：

\`\`\`bash
python tools/py/git_diff_analyzer.py --since "7 days ago" | \\
python tools/py/summary_related_checker.py --from-stdin
\`\`\`

### 3. 更新策略

根据优先级执行更新：

- **P0 变更**: 立即更新，验证后部署
- **P1 变更**: 每周批量更新
- **P2 变更**: 每月或每季度更新

### 4. 验证

- 运行 \`summary_validator\` 验证摘要格式
- 运行 \`document_health_check\` 评估文档健康度
- 人工审核关键变更

## AI 指令模板

\`\`\`
请根据以下代码变更更新文档 [文档路径]:

变更文件: [变更文件列表]
变更类型: [新增/修改/删除]
影响范围: [具体影响]

更新要求:

1. 更新相关代码示例
2. 调整规范说明（如有必要）
3. 更新摘要的 verified_at 字段
4. 确保 related_files 字段准确
   \`\`\`
```

---

## 字段说明

### title

- **值**: `增量更新工作流`
- **说明**: 清晰说明工作流的目的

### summary

- **值**: `定义代码变更后文档更新的标准流程，包括变更检测、影响分析、更新策略和验证机制`
- **说明**:
  - 说明工作流的目的（文档更新）
  - 列举关键步骤（变更检测、影响分析等）
  - 强调标准化流程

### keywords

- **值**: `工作流 | 增量更新 | 文档维护 | Git | 变更检测 | 影响分析`
- **说明**:
  - 文档类型：工作流
  - 核心概念：增量更新、文档维护
  - 相关技术：Git、变更检测、影响分析

### scope

- **值**: `框架文档维护流程`
- **说明**:
  - 说明工作流的适用范围
  - **注意**: 工作流文档通常是**流程性文档**，不涉及具体代码目录

### related_files

- **值**: `无`
- **说明**:
  - 工作流文档通常**不直接关联代码文件**
  - 即使提到了 git_diff_analyzer.py，这些是**工具引用**，不是文档的核心关联
  - **例外**: 如果工作流文档详细说明了某个脚本的使用方法，可以包含该脚本

### dependencies

- **值**: `workflows/generation_workflow.md | workflows/document_health_check.md | tools/README.md`
- **说明**:
  - 列出相关的工作流文档
  - 包含使用的工具文档

### verified_at

- **值**: `2025-12-03`
- **说明**: 标准日期格式

---

## 工作流文档特点

### related_files 原则

工作流文档通常 `related_files` 为 `无`，除非：

**例外情况**:

- ✅ 工作流文档详细说明了某个脚本的实现细节
- ✅ 工作流包含必须修改的配置文件
- ✅ 工作流是代码文件的使用指南

**示例**:

```yaml
# 一般工作流（流程说明）
title: 代码审查工作流
related_files: 无

# 脚本使用指南（详细说明实现）
title: Git Diff Analyzer 使用指南
related_files: tools/py/git_diff_analyzer.py | tools/js/git_diff_analyzer.js

# 部署工作流（包含配置文件）
title: 生产环境部署流程
related_files: deploy/production.yml | docker-compose.prod.yml
```

### dependencies 原则

工作流文档的 `dependencies` 通常包含：

1. 前置工作流文档
2. 相关的规范文档
3. 使用的工具文档

---

## ✅ 正确示例

### 示例 1: 纯流程工作流

```yaml
---
title: 代码审查工作流
summary: 定义团队代码审查的标准流程，包括提交前检查、审查清单、反馈机制和合并策略
keywords: 工作流 | 代码审查 | Code Review | PR | 合并策略
scope: 团队开发流程
related_files: 无
dependencies: dev_docs/coding_standards.md | workflows/git_workflow.md
verified_at: 2025-12-03
---
```

### 示例 2: 工具使用工作流

```yaml
---
title: 项目分析工具使用指南
summary: 详细说明如何使用项目分析工具进行代码扫描、依赖分析和复杂度评估
keywords: 工具 | 项目分析 | 代码扫描 | 依赖分析 | 复杂度
scope: 框架工具库使用
related_files: tools/py/project_analyzer.py | tools/js/project_analyzer.js
dependencies: tools/README.md | core/tool_development_guide.md
verified_at: 2025-12-03
---
```

### 示例 3: 部署工作流

```yaml
---
title: Docker 容器化部署流程
summary: 定义应用容器化和生产环境部署的标准流程，包括镜像构建、配置管理和健康检查
keywords: 工作流 | Docker | 部署 | 容器化 | CI/CD
scope: 应用部署流程 (deploy/)
related_files: Dockerfile | docker-compose.yml | deploy/production.yml | .dockerignore
dependencies: dev_docs/environment_config.md | workflows/ci_cd_workflow.md
verified_at: 2025-12-03
---
```

---

## ❌ 常见错误

### 错误 1: 将工具引用当作 related_files

```yaml
# ❌ 错误（仅提到工具，未详细说明实现）
title: 增量更新工作流
related_files: tools/py/git_diff_analyzer.py | tools/py/summary_related_checker.py

# ✅ 正确
title: 增量更新工作流
related_files: 无
dependencies: tools/README.md
```

### 错误 2: summary 没有列举关键步骤

```yaml
# ❌ 错误
summary: 文档更新流程

# ✅ 正确
summary: 定义代码变更后文档更新的标准流程，包括变更检测、影响分析、更新策略和验证机制
```

### 错误 3: scope 指定了代码目录

```yaml
# ❌ 错误（工作流不涉及特定代码目录）
scope: 框架工具层 (tools/)

# ✅ 正确
scope: 框架文档维护流程
```

---

## 📝 工作流文档 vs 工具文档

### 区别

| 维度              | 工作流文档         | 工具文档             |
| ----------------- | ------------------ | -------------------- |
| **目的**          | 说明流程和步骤     | 说明工具的实现和用法 |
| **related_files** | 通常为 `无`        | 包含工具脚本文件     |
| **keywords**      | 工作流、流程、步骤 | 工具、脚本、CLI      |
| **scope**         | 流程范围           | 工具目录             |

### 示例对比

**工作流文档**:

```yaml
title: 增量更新工作流
scope: 框架文档维护流程
related_files: 无
```

**工具文档**:

```yaml
title: Git Diff Analyzer 使用指南
scope: 框架工具库 (tools/)
related_files: tools/py/git_diff_analyzer.py | tools/js/git_diff_analyzer.js
```

---

**相关文档**:

- [SUMMARY_FORMAT_SPEC.md](../SUMMARY_FORMAT_SPEC.md) - 完整格式规范
- [tool_doc_example.md](./tool_doc_example.md) - 工具文档示例
