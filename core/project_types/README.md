---
title: 项目类型配置索引
summary: AICC 框架支持的 13 种项目类型详细配置目录的索引；每个 type 含适用场景、关键库识别规则、子文档清单建议、特殊场景处理等
keywords: project-types | index | configurations | aicc
scope: 项目类型详细配置文档的目录入口（与 core/project_types.md 决策树配套使用）
related_files: core/project_types.md | AI_ENTRY_POINT.md | workflows/path_a_first_generation.md
dependencies: 无
verified_at: 2026-04-26
---

# 项目类型配置索引

> **目录**: `core/project_types/`  
> **用途**: 存放所有项目类型的详细配置文档

---

## 📋 概述

本目录包含 **13 种项目类型**的详细配置文档，每个文档提供：

- 🎯 适用框架和技术栈
- 📋 推荐子文档清单
- 🔍 特殊关注点
- 💻 核心代码模式
- ⚠️ 常见问题和解决方案
- 🎯 检查清单

---

## 🗂️ 项目类型列表

### 前端与全栈

| 文档 | 描述 | 适用框架 |
|------|------|---------|
| [web_frontend.md](./web_frontend.md) | Web 前端项目 | Vue.js / React / Angular / Svelte |
| [fullstack.md](./fullstack.md) | 全栈项目 | Next.js / Nuxt / Remix / SvelteKit |
| [mobile_app.md](./mobile_app.md) | 移动应用 | React Native / Flutter / 原生 |
| [desktop_app.md](./desktop_app.md) | 桌面应用 | Electron / Tauri / Qt |

### 后端与服务

| 文档 | 描述 | 适用框架 |
|------|------|---------|
| [backend_api.md](./backend_api.md) | 后端 API | Express / FastAPI / Spring Boot / Gin |
| [microservices.md](./microservices.md) | 微服务架构 | gRPC / 消息队列 / 服务网格 |
| [serverless.md](./serverless.md) | Serverless | AWS Lambda / Cloud Functions |
| [containerized.md](./containerized.md) | 容器化 | Docker / Kubernetes |

### 工具与库

| 文档 | 描述 | 适用场景 |
|------|------|---------|
| [cli_tool.md](./cli_tool.md) | CLI 工具 | 命令行工具 / 开发者工具 |
| [library_sdk.md](./library_sdk.md) | 库/SDK | npm 包 / PyPI 包 / Go module |
| [script.md](./script.md) | 脚本项目 | Python 脚本 / Shell 脚本 / 自动化 |

### 数据与 AI

| 文档 | 描述 | 适用场景 |
|------|------|---------|
| [data_science.md](./data_science.md) | 数据科学 | Jupyter / 机器学习 / 深度学习 |
| [ai_llm_app.md](./ai_llm_app.md) | AI/LLM 应用 | RAG / Prompt 工程 / AI Agent |

---

## 🚀 使用指南

### 1. 识别项目类型

使用 [../project_types.md](../project_types.md) 中的决策树快速识别项目类型。

### 2. 按需加载配置

只读取对应的1个配置文档，不要一次性加载所有文档。

**示例**:
```
# 识别为 Web 前端项目
读取 core/project_types/web_frontend.md
```

### 3. 生成子文档清单

根据配置文档中的"推荐子文档清单"和项目规模生成文档列表。

---

## 📊 项目类型对比

| 类型 | 复杂度 | 常见规模 | 主要关注点 |
|------|--------|---------|-----------|
| Web 前端 | 中 | 中-大 | UI 组件、状态管理、API 调用 |
| 后端 API | 中 | 中-大 | 数据库、认证、API 设计 |
| 全栈 | 高 | 大 | SSR/SSG、数据获取、部署 |
| CLI 工具 | 低 | 小-中 | 命令结构、参数验证、输出格式 |
| 库/SDK | 中 | 小-中 | API 设计、版本管理、文档 |
| 脚本 | 低 | 小 | 配置管理、错误处理、日志 |
| 移动应用 | 高 | 中-大 | 平台差异、性能优化、原生模块 |
| 桌面应用 | 中 | 中 | IPC 通信、系统集成、打包 |
| Serverless | 中 | 小-中 | 冷启动、成本优化、触发器 |
| 容器化 | 中 | 中-大 | Dockerfile、编排、CI/CD |
| 数据科学 | 高 | 中-大 | 数据处理、模型训练、实验跟踪 |
| 微服务 | 高 | 大 | 服务通信、服务发现、分布式追踪 |
| AI/LLM | 高 | 中-大 | Prompt 管理、RAG、成本优化 |

---

## 🔄 更新记录

- **2026-01-21**: 初始版本，包含 13 种项目类型
  - 新增: `microservices.md` - 微服务架构
  - 新增: `ai_llm_app.md` - AI/LLM 应用

---

## 📚 相关文档

- [../project_types.md](../project_types.md) - 项目类型索引与决策树
- [../../AI_ENTRY_POINT.md](../../AI_ENTRY_POINT.md) - 框架入口文档
- [../../workflows/path_a_first_generation.md](../../workflows/path_a_first_generation.md) - 首次生成工作流

---

**版本**: v3.0  
**路径**: `core/project_types/README.md`  
**最后更新**: 2026-01-21
