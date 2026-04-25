---
title: Claude Code AI 编码上下文
summary: Claude Code项目的核心文档入口，提供项目概览、架构指南、开发规范和快速导航。本文档为AI辅助编程的快速上下文入口，80%的常见场景可直接获取答案，详细内容请查阅对应的子文档。
keywords: Claude Code | AI Coding Context | 文档体系 | 开发指南 | 架构 | Anthropic | 智能编程助手 | 插件系统
scope: 整个项目 (全局上下文)
related_files: dev_docs/architecture.md | dev_docs/api_reference.md | dev_docs/development_guide.md
dependencies: dev_docs/project_overview.md | dev_docs/architecture/framework_overview.md
verified_at: 2025-12-19
---

# Claude Code AI 编码上下文

> ⚠️ **本文件为"案例样本"，请勿当作真实文档使用**
>
> 本文档是为 Claude Code（Anthropic）项目生成的 AI 编码上下文示例，用于演示框架在真实项目上的产出形态。
>
> 文中所有 markdown 链接（如 `architecture.md`、`api_reference.md`、`dev_docs/...`、`ai_coding_context/...`）均面向 Claude Code 项目假设的目录结构，**在本仓库内无法跳转**，这是**预期行为**，不是失效引用。

> **文档定位**:
>
> - 本文档为 AI 辅助编程的快速上下文入口（索引 + 速查手册）
> - 80%的常见场景可在本文档直接获取答案
> - 详细内容请查阅对应的子文档（见"文档索引"章节）
>
> **适用版本**: Claude Code v1.0 | Node.js/Python
> **最后更新**: 2025-12-19

## 📊 项目概览

- **规模**: 353个文件 | 约15,000行代码
- **技术栈**: Node.js + Python + Git Hooks + Jest
- **架构**: 多语言工具链 + 插件化架构 + AI辅助框架
- **开发者**: Anthropic
- **类型**: 智能编程助手 | 终端代理式编程工具

### 项目简介

Claude Code 是 Anthropic 开发的智能编程助手，是一个存在于终端中的代理式编程工具。它能够理解代码库、执行常规任务、解释复杂代码并处理 Git 工作流，所有这些都通过自然语言命令完成。

#### 核心特性

- **智能编程助手**: 在终端中提供自然语言编程接口
- **代码理解能力**: 能够深度理解项目代码结构和依赖关系
- **Git 工作流集成**: 自动处理版本控制和代码提交流程
- **多平台支持**: 支持 MacOS、Linux 和 Windows 系统
- **插件生态系统**: 提供丰富的插件扩展功能

## 📂 关键目录速查

- `ai_coding_context/agents/` - AI角色定义与专家系统
- `ai_coding_context/config/` - 框架配置文件
- `ai_coding_context/core/` - 核心框架代码
- `ai_coding_context/templates/` - 文档和代码模板
- `ai_coding_context/tools/` - 核心工具实现 (JS/Python)
- `dev_docs/` - 项目文档体系
- `ai_coding_context/workflows/` - 标准化工作流程

## 🎯 场景快速导航

| 我要... | 参考文档 |
| --- | --- |
| 理解项目整体架构 | [架构总览](architecture.md) |
| 查看API接口参考 | [API参考文档](api_reference.md) |
| 开始开发新功能 | [开发指南](development_guide.md) |
| 运行测试 | [测试指南](testing_guide.md) |
| 部署项目 | [部署指南](deployment_guide.md) |
| 了解项目概况 | [项目概览](project_overview.md) |
| 分析项目代码 | [项目分析](project_analysis.md) |

## 🚀 文档索引 (快速导航)

### 核心架构

- [架构总览](architecture.md) - 技术架构深度解析
- [API参考文档](api_reference.md) - 完整API接口文档
- [框架概览](architecture/framework_overview.md) - **核心框架机制** ⭐ (必读)

### 开发指南

- [开发指南](development_guide.md) - 环境设置与开发流程
- [插件开发指南](architecture/plugin_development_guide.md) - 插件系统开发
- [编码规范](development_guide.md#编码规范) - 项目编码标准

### 项目信息

- [项目概览](project_overview.md) - 项目基本信息与特性
- [项目分析](project_analysis.md) - 深度代码分析报告

### 测试与部署

- [测试指南](testing_guide.md) - 测试策略与实践
- [部署指南](deployment_guide.md) - 部署流程与运维

### 工具参考

- [命令行工具参考](tools/cli_reference.md) - 命令行工具使用指南
- [Git Hooks工具](tools/install_hooks.js) - 标准化Git工作流

## ⭐ 核心架构特点

**说明**: Claude Code 采用分层的模块化架构设计，通过 AI 编码上下文框架提供智能的代码理解和辅助功能。

### 架构分层

#### 1. 用户接口层 (User Interface Layer)
- **职责**: 处理用户交互和命令行接口
- **特性**: 自然语言命令解析、多平台兼容性、实时交互支持

#### 2. 业务逻辑层 (Business Logic Layer)
- **职责**: 实现核心业务逻辑和工作流程
- **组件**: 
  - 代码分析器 (Code Analyzer)
  - AI代理管理器 (Agent Manager)
  - 工作流引擎 (Workflow Engine)

#### 3. 插件系统层 (Plugin System Layer)
- **职责**: 提供可扩展的插件架构
- **特性**: 标准化插件接口、动态加载机制、插件生命周期管理

#### 4. AI编码上下文框架层 (AI Coding Context Framework)
- **职责**: 提供AI辅助编码的核心能力
- **组件**:
  - 设计思维引导 (Design Thinking Guidance)
  - AI角色库 (Agent Library)
  - 上下文管理 (Context Management)

**详情**: [架构总览](architecture.md)

## 🧠 设计思维引导 (v3.0 新增)

**说明**: 框架集成了设计思维引导模式,在复杂任务开发前自动引导深度思考,避免"想不清就开干"。

### 核心价值

- ✅ **多方案对比**: 至少 2-3 种技术方案,避免盲目跟风
- ✅ **提前识别风险**: 通过 Architect 和 QA 识别技术风险和应对措施
- ✅ **明确业务价值**: 通过 5 Why 分析挖掘根本动机
- ✅ **清晰验收标准**: 确保开发目标明确可测

### 触发方式

**自动触发** (推荐):

- 框架会评估任务复杂度,达到阈值(默认 60)时主动提议
- 涉及核心模块 (Auth, Payment) 或架构重构时触发

**手动触发**:

- `@think` - 标准引导 (5 步流程)
- `@think:deep` - 深度辩论 (多轮专家对话)
- `@think:quick` - 快速对齐 (仅确认目标、方案、验收)

### 5 步引导流程

1. **问题本质** (PM) → 5 Why 分析挖掘业务价值
2. **方案探索** (Architect) → 至少 2-3 种方案对比
3. **风险与测试** (Architect & QA) → 识别风险、制定测试策略
4. **反思与整合** (Facilitator) → 全局反思、识别冲突
5. **最终决策** (Facilitator) → 输出结构化方案

## 🛠️ 开发流程规范

### **方案驱动开发** (强制执行)

> 在开发功能或修复 Bug 前，**必须先创建方案文档**，作为人工审核点和 AI 上下文传递载体。

#### 1️⃣ 创建方案文档

- **位置**: `dev_docs/plans/features/` (功能) 或 `dev_docs/plans/bugfixes/` (Bug)
- **命名**: `YYYY-MM-DD_简短描述.md`
- **模板**: 见 [plans/README.md](./plans/README.md)

**可跳过方案的场景**:

- 单纯文案修改（如翻译文本）
- 简单样式调整（如颜色、边距）
- 配置项修改
- 修复拼写错误

**其他场景均需创建方案文档！**

#### 2️⃣ 实施开发

按方案文档执行，严格遵循项目规范。

#### 3️⃣ 沉淀知识

完成后，若方案有价值（耗时>2h 或难度高），提炼到 `dev_docs/knowledge/`。

#### 4️⃣ 沉淀工具

若开发过程中遇到**高频重复**或**高稳定性要求**的操作，请参考 `workflows/create_custom_tool_workflow.md` 创建通用脚本工具，并更新 `tools/README.md`。

**详细规范**: [开发指南](development_guide.md)

## 🤖 AI 角色库 (Agent Library)

> **说明**: 本项目集成了标准化的 AI 角色库，可辅助完成特定任务。

### 常用角色

- **[方案审查员]** - 负责审查技术方案
- **[代码审查员]** - 负责审查代码质量
- **[测试工程师]** - 负责生成测试用例
- **[性能专家]** - 负责性能优化
- **[安全审计员]** - 负责安全检查

**完整索引**: [AI角色库文档](ai_coding_context/agents/README.md)

## 📚 知识库使用说明

### **何时参考知识库？**

- ✅ 遇到类似技术难题
- ✅ 需要实现类似功能模式
- ✅ 性能优化需求
- ✅ 排查疑难 Bug

### 已有知识文档

**问题解决** (`knowledge/troubleshooting/`)

- 故障排除指南

**架构模式** (`knowledge/patterns/`)

- 插件架构模式
- AI上下文管理模式

**性能优化** (`knowledge/performance/`)

- 代码分析优化
- 工具链性能优化

## 💻 核心代码模式

### 模式 1: Git Hooks 安装

```javascript
// 文件: install_hooks.js
const findGitRoot = () => {
  let currentDir = process.cwd();
  
  while (currentDir !== path.dirname(currentDir)) {
    if (fs.existsSync(path.join(currentDir, '.git'))) {
      return currentDir;
    }
    currentDir = path.dirname(currentDir);
  }
  return null;
};

const installHooks = () => {
  const gitRoot = findGitRoot();
  if (!gitRoot) {
    console.log('❌ 未找到 Git 仓库');
    return;
  }
  
  const hooksDir = path.join(gitRoot, '.git', 'hooks');
  if (!fs.existsSync(hooksDir)) {
    fs.mkdirSync(hooksDir, { recursive: true });
  }
  
  console.log('✅ Git Hooks 安装成功');
};
```

### 模式 2: 工具链集成

```python
# 文件: commit_template_cli.py
import argparse
import json
from pathlib import Path

def generate_commit_template():
    """生成标准化的提交信息模板"""
    template = {
        "type": "feat|fix|docs|style|refactor|test|chore",
        "scope": "模块范围",
        "subject": "简短描述",
        "body": "详细描述",
        "breaking": "破坏性变更说明"
    }
    return template

def main():
    parser = argparse.ArgumentParser(description='生成提交模板')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json')
    args = parser.parse_args()
    
    template = generate_commit_template()
    print(json.dumps(template, indent=2, ensure_ascii=False))
```

### 模式 3: 测试框架

```javascript
// 文件: install_hooks.test.js
const assert = require('assert');
const path = require('path');
const fs = require('fs');

// 测试 findGitRoot 函数
try {
    console.log('测试 1: findGitRoot() 应该找到当前 Git 仓库');
    const gitRoot = findGitRoot();
    assert.ok(gitRoot !== null, 'Git 仓库根目录不应为 null');
    assert.ok(fs.existsSync(path.join(gitRoot, '.git')), '.git 目录应该存在');
    console.log('✅ 测试 1 通过\n');
} catch (error) {
    console.log(`❌ 测试 1 失败: ${error.message}\n`);
}
```

## 📋 命名规范

- **文件**: kebab-case (如 `user-profile.ts`)
- **组件**: PascalCase (如 `UserProfile.vue`)
- **变量/函数**: camelCase (如 `getUserProfile`)
- **常量**: UPPER_CASE (如 `MAX_RETRY_COUNT`)
- **Git 分支**: feature/功能名 (如 `feature/user-authentication`)
- **Git 提交**: 约定式提交 (如 `feat: 添加用户认证功能`)

## 🏢 业务模块映射

### 核心模块

| 模块名称 | 职责 | 关键文件 |
| --- | --- | --- |
| AI编码上下文 | 提供AI辅助编码核心功能 | `ai_coding_context/core/` |
| 工具链 | 提供多语言工具支持 | `ai_coding_context/tools/` |
| 代理系统 | 管理AI角色和工作流程 | `ai_coding_context/agents/` |
| 配置管理 | 处理框架配置 | `ai_coding_context/config/` |

## 📌 重要提醒

- 📌 所有新功能开发前需要创建方案文档
- 📌 严格遵循编码规范和Git工作流
- 📌 重要修改需要通过代码审查
- 📌 所有核心功能必须有对应测试

## 🔗 相关链接

- [项目 GitHub 仓库](https://github.com/anthropics/claude-code)
- [Anthropic 官方网站](https://www.anthropic.com)
- [设计思维引导](ai_coding_context/agents/examples/design_thinking/user_login_flow.md)
- [插件开发指南](architecture/plugin_development_guide.md)