# 架构文档摘要示例

本文档展示架构类文档的标准摘要格式。

---

## 完整示例

```markdown
---
title: 前端应用架构设计
summary: 定义基于 Vue 3 的单页应用架构，包括目录结构、模块划分、路由设计和状态管理策略
keywords: 架构 | Vue 3 | SPA | 路由 | 状态管理 | 模块化
scope: 前端应用架构 (src/)
related_files: src/main.ts | src/App.vue | src/router/index.ts | src/store/index.ts | src/plugins/i18n.ts
dependencies: dev_docs/state_management.md | dev_docs/api_layer.md | dev_docs/component_library.md
verified_at: 2025-12-03
---

# 前端应用架构设计

## 概述

本文档定义了基于 Vue 3 + TypeScript + Vite 的单页应用架构...

## 目录结构

\`\`\`
src/
├── main.ts # 应用入口
├── App.vue # 根组件
├── router/ # 路由配置
│ └── index.ts
├── store/ # 状态管理
│ └── index.ts
├── views/ # 页面组件
├── components/ # 通用组件
├── api/ # API 层
├── utils/ # 工具函数
└── plugins/ # 插件配置
└── i18n.ts
\`\`\`

## 核心模块

### 1. 路由层 (router/)

- **文件**: \`src/router/index.ts\`
- **责任**: 定义路由规则、导航守卫、路由元信息

### 2. 状态管理 (store/)

- **文件**: \`src/store/index.ts\`
- **责任**: 全局状态、用户信息、主题配置

### 3. 国际化 (plugins/)

- **文件**: \`src/plugins/i18n.ts\`
- **责任**: 多语言支持
```

---

## 字段说明

### title

- **值**: `前端应用架构设计`
- **说明**: 明确说明是架构文档，指明技术栈（前端）

### summary

- **值**: `定义基于 Vue 3 的单页应用架构，包括目录结构、模块划分、路由设计和状态管理策略`
- **说明**:
  - 说明核心技术（Vue 3）
  - 列举主要内容（目录结构、模块划分等）
  - 避免重复标题

### keywords

- **值**: `架构 | Vue 3 | SPA | 路由 | 状态管理 | 模块化`
- **说明**:
  - 包含文档类型（架构）
  - 包含核心技术（Vue 3, SPA）
  - 包含关键概念（路由、状态管理、模块化）

### scope

- **值**: `前端应用架构 (src/)`
- **说明**:
  - 说明文档范围（前端应用架构）
  - 包含主要目录（src/）

### related_files

- **值**: `src/main.ts | src/App.vue | src/router/index.ts | src/store/index.ts | src/plugins/i18n.ts`
- **说明**:
  - 包含所有在文档中作为示例的核心文件
  - 入口文件（main.ts）
  - 根组件（App.vue）
  - 各模块的主文件（router, store, plugins）
  - **不包含** views/ 和 components/ 下的所有文件（范围过大）

### dependencies

- **值**: `dev_docs/state_management.md | dev_docs/api_layer.md | dev_docs/component_library.md`
- **说明**:
  - 列出需要配合阅读的相关文档
  - 架构文档通常依赖多个子文档

### verified_at

- **值**: `2025-12-03`
- **说明**: 标准日期格式 YYYY-MM-DD

---

## 架构文档特点

### related_files 选择原则

**包含**:

- ✅ 主入口文件（main.ts, index.ts）
- ✅ 核心配置文件（router, store, plugins）
- ✅ 根组件（App.vue）
- ✅ 架构示意图中的关键文件

**不包含**:

- ❌ 所有页面组件（views/\*）
- ❌ 所有通用组件（components/\*）
- ❌ 工具函数（utils/\*）
- ❌ API 层文件（有专门的 api_layer.md）

**原因**: 架构文档关注的是**结构和模块关系**，而非每个具体实现文件。如果列出所有文件，会导致：

1. 列表过长，失去重点
2. 任何文件变更都触发架构文档更新（过于频繁）

### keywords 建议

架构文档的 keywords 应包含：

1. 文档类型：架构、设计
2. 技术栈：Vue 3、React、Spring Boot
3. 架构模式：MVC、MVVM、分层架构、微服务
4. 核心概念：路由、状态管理、依赖注入

---

## ✅ 正确示例

```yaml
---
title: 后端微服务架构设计
summary: 定义基于 Spring Boot 的微服务架构，包括服务划分、通信机制、配置中心和服务发现
keywords: 架构 | 微服务 | Spring Boot | 服务发现 | 配置中心 | API Gateway
scope: 后端微服务架构 (services/)
related_files: services/gateway/src/main/java/Gateway.java | services/user/src/main/java/UserService.java | services/config/application.yml
dependencies: dev_docs/service_communication.md | dev_docs/deployment.md
verified_at: 2025-12-03
---
```

---

## ❌ 常见错误

### 错误 1: related_files 包含所有文件

```yaml
# ❌ 错误
related_files: src/main.ts | src/views/Home.vue | src/views/About.vue | src/views/User.vue | src/components/Header.vue | ...（50+ 个文件）

# ✅ 正确
related_files: src/main.ts | src/App.vue | src/router/index.ts | src/store/index.ts
```

### 错误 2: summary 过于简略

```yaml
# ❌ 错误
summary: 前端架构文档

# ✅ 正确
summary: 定义基于 Vue 3 的单页应用架构，包括目录结构、模块划分、路由设计和状态管理策略
```

### 错误 3: scope 过于宽泛

```yaml
# ❌ 错误
scope: 整个项目

# ✅ 正确
scope: 前端应用架构 (src/)
```

---

**相关文档**:

- [SUMMARY_FORMAT_SPEC.md](../SUMMARY_FORMAT_SPEC.md) - 完整格式规范
- [api_doc_example.md](./api_doc_example.md) - API 文档示例
