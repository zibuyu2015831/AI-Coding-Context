---
title: 后端 API 项目配置
summary: 定义后端 API 项目（Node.js/Python/Java/Go 等）的推荐子文档清单、特殊关注点和核心代码模式。包括 RESTful/GraphQL 设计、数据库模型、认证授权等关键规范。
keywords: backend-api | rest | graphql | database | authentication | middleware | orm
scope: 后端 API 项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 后端 API 项目

> **适用语言**: Node.js / Python / Java / Go / Ruby / PHP / .NET / Rust

---

## 🎯 适用框架

### Node.js
- **Express**: 成熟稳定，生态丰富
- **Fastify**: 高性能，TypeScript 友好
- **NestJS**: 企业级，依赖注入，装饰器
- **Koa**: 轻量级，中间件洋葱模型
- **Hono**: 边缘计算，超轻量

### Python
- **Flask**: 轻量级，灵活
- **FastAPI**: 现代，异步，自动文档
- **Django**: 全功能，ORM 强大
- **Sanic**: 异步，高性能

### Java
- **Spring Boot**: 企业标准，功能完整
- **Quarkus**: 云原生，快速启动
- **Micronaut**: 编译时依赖注入

### Go
- **Gin**: 高性能，简洁
- **Echo**: 高性能，中间件丰富
- **Fiber**: Express 风格，极速

### 其他
- **Ruby**: Rails / Sinatra
- **PHP**: Laravel / Symfony
- **.NET**: ASP.NET Core
- **Rust**: Actix-web / Rocket / Axum

---

## 📋 推荐子文档清单

| 优先级 | 文档名称                      | 用途                 |
| ------ | ----------------------------- | -------------------- |
| 🔴 高  | `api_design.md`               | RESTful/GraphQL 设计 |
| 🔴 高  | `database_schema.md`          | 数据库模型与关系     |
| 🔴 高  | `authentication.md`           | 认证与授权           |
| 🟡 中  | `middleware_guide.md`         | 中间件使用           |
| 🟡 中  | `error_handling.md`           | 错误处理与日志       |
| 🟡 中  | `testing_guide.md`            | 单元/集成测试        |
| 🟢 低  | `performance_optimization.md` | 性能优化策略         |

---

## 🔍 特殊关注点

### ORM/ODM 使用

#### Node.js
- **Prisma**: 现代 ORM，类型安全，迁移管理
- **TypeORM**: 装饰器风格，支持多数据库
- **Mongoose**: MongoDB ODM
- **Sequelize**: 成熟 ORM，支持多数据库
- **Drizzle**: 轻量级，类型安全

#### Python
- **SQLAlchemy**: 功能强大，灵活
- **Django ORM**: 集成在 Django 中
- **Tortoise ORM**: 异步 ORM
- **Pydantic**: 数据验证（配合 FastAPI）

#### Java
- **Hibernate**: JPA 标准实现
- **JPA**: Java 持久化 API
- **MyBatis**: SQL 映射框架

#### Go
- **GORM**: 功能丰富
- **sqlx**: 轻量级扩展
- **ent**: Facebook 开源，代码生成

### 数据验证

#### Node.js
- **Zod**: TypeScript 优先，类型推断
- **Joi**: 成熟稳定
- **class-validator**: 装饰器风格（NestJS）
- **Yup**: 简洁易用

#### Python
- **Pydantic**: FastAPI 标配，类型安全
- **Marshmallow**: 序列化/反序列化
- **Cerberus**: 轻量级验证

#### Java
- **Bean Validation**: JSR 303/380 标准
- **Hibernate Validator**: Bean Validation 实现

#### Go
- **validator**: 结构体标签验证
- **ozzo-validation**: 代码优先验证

### 缓存策略

- **Redis**: 内存缓存，支持多种数据结构
- **Memcached**: 简单高效的键值缓存
- **应用内缓存**: Node-cache / lru-cache

### 消息队列

- **RabbitMQ**: 功能丰富，支持多种协议
- **Kafka**: 高吞吐，分布式流处理
- **NATS**: 轻量级，云原生
- **Bull**: Node.js 任务队列（基于 Redis）

### 日志系统

#### Node.js
- **Winston**: 功能丰富，传输层灵活
- **Pino**: 高性能，JSON 格式
- **Bunyan**: 结构化日志

#### Python
- **structlog**: 结构化日志
- **loguru**: 简单易用
- **Python logging**: 标准库

#### Java
- **Logback**: SLF4J 实现
- **Log4j2**: 高性能
- **SLF4J**: 日志门面

---

## 💻 核心代码模式

### 路由定义（Express + TypeScript）

```typescript
import { Router } from 'express'
import { authenticate } from '@/middleware/auth'
import { validate } from '@/middleware/validate'
import { userController } from '@/controllers/user'
import { createUserSchema } from '@/schemas/user'

const router = Router()

// GET 请求
router.get('/users', authenticate, userController.list)

// POST 请求（带验证）
router.post(
  '/users',
  authenticate,
  validate(createUserSchema),
  userController.create
)

// 参数路由
router.get('/users/:id', authenticate, userController.getById)

// PUT/PATCH 更新
router.patch('/users/:id', authenticate, userController.update)

// DELETE 删除
router.delete('/users/:id', authenticate, userController.delete)

export default router
```

### 数据库模型（Prisma）

```prisma
// schema.prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  password  String
  role      Role     @default(USER)
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
  @@map("users")
}

model Post {
  id        String   @id @default(uuid())
  title     String
  content   String   @db.Text
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
  @@map("posts")
}

enum Role {
  USER
  ADMIN
}
```

### 中间件（认证）

```typescript
import { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'

interface AuthRequest extends Request {
  user?: {
    id: string
    email: string
    role: string
  }
}

export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    // 从 header 获取 token
    const token = req.headers.authorization?.replace('Bearer ', '')
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' })
    }

    // 验证 token
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
      id: string
      email: string
      role: string
    }

    // 附加用户信息到请求
    req.user = decoded
    next()
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' })
  }
}

// 角色检查中间件
export const requireRole = (role: string) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (req.user?.role !== role) {
      return res.status(403).json({ error: 'Insufficient permissions' })
    }
    next()
  }
}
```

### 数据验证（Zod）

```typescript
import { z } from 'zod'

// 定义 schema
export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email('Invalid email format'),
    name: z.string().min(2, 'Name must be at least 2 characters'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    role: z.enum(['USER', 'ADMIN']).optional()
  })
})

export const updateUserSchema = z.object({
  params: z.object({
    id: z.string().uuid('Invalid user ID')
  }),
  body: z.object({
    email: z.string().email().optional(),
    name: z.string().min(2).optional(),
    password: z.string().min(8).optional()
  })
})

// 验证中间件
import { AnyZodObject } from 'zod'

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params
      })
      next()
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        })
      }
      next(error)
    }
  }
}
```

### 错误处理

```typescript
// 自定义错误类
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message)
    Object.setPrototypeOf(this, AppError.prototype)
  }
}

// 全局错误处理中间件
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: 'error',
      message: err.message
    })
  }

  // 未知错误
  console.error('ERROR:', err)
  return res.status(500).json({
    status: 'error',
    message: 'Internal server error'
  })
}

// 使用示例
import { AppError } from '@/utils/errors'

const user = await prisma.user.findUnique({ where: { id } })
if (!user) {
  throw new AppError(404, 'User not found')
}
```

### FastAPI 示例（Python）

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn

app = FastAPI()

# 数据模型
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    
    class Config:
        from_attributes = True

# 依赖注入
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 验证 token 逻辑
    return user

# 路由
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # 创建用户逻辑
    return created_user

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    # 获取用户列表
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## ⚠️ 常见问题

### 问题 1: N+1 查询问题

**解决方案**: 使用 ORM 的预加载功能

```typescript
// ❌ 错误：N+1 查询
const users = await prisma.user.findMany()
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } })
}

// ✅ 正确：使用 include
const users = await prisma.user.findMany({
  include: { posts: true }
})
```

### 问题 2: 密码明文存储

**解决方案**: 使用 bcrypt 加密

```typescript
import bcrypt from 'bcrypt'

// 注册时加密
const hashedPassword = await bcrypt.hash(password, 10)

// 登录时验证
const isValid = await bcrypt.compare(password, user.password)
```

### 问题 3: SQL 注入风险

**解决方案**: 使用参数化查询或 ORM

```typescript
// ❌ 危险：字符串拼接
const users = await db.query(`SELECT * FROM users WHERE email = '${email}'`)

// ✅ 安全：参数化查询
const users = await db.query('SELECT * FROM users WHERE email = $1', [email])

// ✅ 安全：使用 ORM
const users = await prisma.user.findMany({ where: { email } })
```

---

## 🎯 检查清单

生成后端 API 项目文档前，确认：

- [ ] 已识别主要语言和框架（Node.js/Python/Java/Go 等）
- [ ] 已确定 API 风格（RESTful/GraphQL/gRPC）
- [ ] 已确定数据库类型（PostgreSQL/MySQL/MongoDB 等）
- [ ] 已确定 ORM/ODM（Prisma/TypeORM/SQLAlchemy 等）
- [ ] 已确定认证方案（JWT/OAuth2/Session 等）
- [ ] 已确定数据验证库（Zod/Joi/Pydantic 等）
- [ ] 已检查是否需要缓存（Redis 等）
- [ ] 已检查是否需要消息队列（RabbitMQ/Kafka 等）
- [ ] 已确定日志方案（Winston/Pino/structlog 等）

---

**版本**: v3.0  
**路径**: `core/project_types/backend_api.md`  
**最后更新**: 2026-01-21
