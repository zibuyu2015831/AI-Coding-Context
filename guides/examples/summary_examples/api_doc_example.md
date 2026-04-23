# API 文档摘要示例

本文档展示 API 规范类文档的标准摘要格式。

---

## 完整示例

```markdown
---
title: API 层设计规范
summary: 定义前端 API 调用的统一接口规范，包括请求封装、错误处理、拦截器配置和 TypeScript 类型定义
keywords: API | HTTP | Axios | 错误处理 | 拦截器 | TypeScript | 类型定义
scope: 前端 API 层 (src/api/)
related_files: src/api/http.ts | src/api/types.ts | src/api/interceptors.ts | src/api/user.ts | src/api/post.ts
dependencies: dev_docs/state_management.md | dev_docs/authentication.md | dev_docs/error_handling.md
verified_at: 2025-12-03
---

# API 层设计规范

## 概述

本文档定义前端与后端通信的标准 API 调用规范...

## 核心文件

### 1. HTTP 封装 (\`src/api/http.ts\`)

\`\`\`typescript
import axios from 'axios';

const http = axios.create({
baseURL: import.meta.env.VITE_API_BASE_URL,
timeout: 10000,
});

export default http;
\`\`\`

### 2. 类型定义 (\`src/api/types.ts\`)

\`\`\`typescript
export interface ApiResponse<T> {
code: number;
data: T;
message: string;
}

export interface PaginationParams {
page: number;
pageSize: number;
}
\`\`\`

### 3. 拦截器 (\`src/api/interceptors.ts\`)

- 请求拦截：添加 token、请求日志
- 响应拦截：统一错误处理、数据转换

### 4. 业务 API (\`src/api/user.ts\`)

\`\`\`typescript
import http from './http';
import type { User, ApiResponse } from './types';

export const getUserInfo = (id: number): Promise<ApiResponse<User>> => {
return http.get(\`/user/\${id}\`);
};
\`\`\`

## 规范

### 错误处理

- 网络错误：显示统一提示
- 业务错误：根据 code 处理
- 认证错误：重定向登录

### 命名规范

- API 函数：动词开头（get, create, update, delete）
- 文件名：资源名复数（users.ts, posts.ts）
```

---

## 字段说明

### title

- **值**: `API 层设计规范`
- **说明**: 清晰说明是 API 规范文档

### summary

- **值**: `定义前端 API 调用的统一接口规范，包括请求封装、错误处理、拦截器配置和 TypeScript 类型定义`
- **说明**:
  - 说明文档目的（统一接口规范）
  - 列举关键内容（请求封装、错误处理等）
  - 突出技术栈（TypeScript）

### keywords

- **值**: `API | HTTP | Axios | 错误处理 | 拦截器 | TypeScript | 类型定义`
- **说明**:
  - 核心概念：API, HTTP
  - 技术栈：Axios, TypeScript
  - 关键功能：错误处理、拦截器、类型定义

### scope

- **值**: `前端 API 层 (src/api/)`
- **说明**:
  - 明确范围（前端 API 层）
  - 指定目录（src/api/）

### related_files

- **值**: `src/api/http.ts | src/api/types.ts | src/api/interceptors.ts | src/api/user.ts | src/api/post.ts`
- **说明**:
  - 核心文件：http.ts（封装）、types.ts（类型）、interceptors.ts（拦截器）
  - 示例文件：user.ts、post.ts（展示用法）
  - **注意**: 如果有 20+ 个业务 API 文件，不需要全部列出，选择 2-3 个代表性示例即可

### dependencies

- **值**: `dev_docs/state_management.md | dev_docs/authentication.md | dev_docs/error_handling.md`
- **说明**:
  - state_management: API 与状态管理的集成
  - authentication: Token 管理
  - error_handling: 错误处理策略

### verified_at

- **值**: `2025-12-03`
- **说明**: 标准日期格式

---

## API 文档特点

### related_files 选择原则

**包含**:

- ✅ HTTP 封装文件（http.ts, request.ts）
- ✅ 类型定义文件（types.ts, interfaces.ts）
- ✅ 拦截器配置（interceptors.ts）
- ✅ 2-3 个业务 API 示例文件（user.ts, post.ts）

**不包含**:

- ❌ 所有 20+ 个业务 API 文件
- ❌ Mock 数据文件
- ❌ 测试文件

**原因**: API 文档关注的是**规范和模式**，业务 API 文件仅作为示例。如果列出所有业务 API：

1. 列表过长
2. 每次新增 API 都要更新文档（不必要）

### keywords 建议

API 文档的 keywords 应包含：

1. 核心概念：API、REST、GraphQL
2. 技术栈：Axios、Fetch、HTTP
3. 关键功能：错误处理、拦截器、重试、缓存
4. 类型系统：TypeScript、类型定义、接口

---

## ✅ 正确示例

### 示例 1: RESTful API 文档

```yaml
---
title: RESTful API 规范
summary: 定义后端 REST API 的统一设计规范，包括资源命名、HTTP 方法、状态码和响应格式
keywords: REST | API | HTTP | 资源设计 | 状态码 | JSON
scope: 后端 API 设计 (src/controllers/)
related_files: src/controllers/BaseController.java | src/controllers/UserController.java | src/dto/ApiResponse.java
dependencies: dev_docs/database_schema.md | dev_docs/authentication.md
verified_at: 2025-12-03
---
```

### 示例 2: GraphQL API 文档

```yaml
---
title: GraphQL API 设计规范
summary: 定义 GraphQL 查询和变更的设计规范，包括 Schema 定义、Resolver 实现和错误处理
keywords: GraphQL | Schema | Query | Mutation | Resolver | 类型系统
scope: GraphQL API 层 (src/graphql/)
related_files: src/graphql/schema.graphql | src/graphql/resolvers/user.ts | src/graphql/resolvers/post.ts
dependencies: dev_docs/database_schema.md
verified_at: 2025-12-03
---
```

---

## ❌ 常见错误

### 错误 1: 列出所有业务 API 文件

```yaml
# ❌ 错误（有 30 个业务 API 文件）
related_files: src/api/http.ts | src/api/user.ts | src/api/post.ts | src/api/comment.ts | src/api/like.ts | ... (30+ 文件)

# ✅ 正确
related_files: src/api/http.ts | src/api/types.ts | src/api/interceptors.ts | src/api/user.ts | src/api/post.ts
```

### 错误 2: keywords 过于宽泛

```yaml
# ❌ 错误
keywords: 前端 | 后端 | API

# ✅ 正确
keywords: API | HTTP | Axios | 错误处理 | 拦截器 | TypeScript
```

### 错误 3: summary 缺少关键信息

```yaml
# ❌ 错误
summary: API 调用规范

# ✅ 正确
summary: 定义前端 API 调用的统一接口规范，包括请求封装、错误处理、拦截器配置和 TypeScript 类型定义
```

---

**相关文档**:

- [SUMMARY_FORMAT_SPEC.md](../SUMMARY_FORMAT_SPEC.md) - 完整格式规范
- [architecture_doc_example.md](./architecture_doc_example.md) - 架构文档示例
