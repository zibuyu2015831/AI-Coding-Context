---
title: 全栈项目配置
summary: 定义全栈项目（Next.js/Nuxt/Remix/SvelteKit）的推荐子文档清单、特殊关注点和核心代码模式。包括 SSR/SSG 策略、API Routes、数据获取等关键规范。
keywords: fullstack | nextjs | nuxt | remix | sveltekit | ssr | ssg | isr | api-routes
scope: 全栈项目类型配置
related_files: 无
dependencies: core/project_types.md | core/project_types/web_frontend.md | core/project_types/backend_api.md
verified_at: 2026-01-21
---

# 全栈项目

> **适用框架**: Next.js / Nuxt / Remix / SvelteKit / Astro / Qwik

---

## 🎯 适用框架

- **Next.js**: React 全栈框架，App Router / Pages Router
- **Nuxt**: Vue 全栈框架，SSR/SSG/ISR
- **Remix**: React 全栈框架，Web 标准优先
- **SvelteKit**: Svelte 全栈框架，轻量高效
- **Astro**: 内容优先，多框架支持
- **Qwik**: 可恢复性架构，极致性能

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `architecture_overview.md` | 前后端架构 |
| 🔴 高 | `api_layer.md` | API层（前端） |
| 🔴 高 | `data_fetching.md` | 数据获取策略 |
| 🟡 中 | `database_schema.md` | 数据库设计 |
| 🟡 中 | `deployment_guide.md` | 部署流程 |
| 🟡 中 | `testing_guide.md` | E2E测试 |

---

## 🔍 特殊关注点

### SSR/SSG/ISR 策略

#### Next.js (App Router)
```typescript
// app/page.tsx - 服务端组件（默认）
export default async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store' // 动态渲染（SSR）
  })
  return <div>{data}</div>
}

// 静态生成（SSG）
export default async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'force-cache' // 静态生成
  })
  return <div>{data}</div>
}

// 增量静态再生成（ISR）
export const revalidate = 60 // 60秒后重新验证

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

#### Nuxt 3
```vue
<script setup>
// SSR + 客户端水合
const { data } = await useFetch('/api/data')

// 仅客户端
const { data } = await useFetch('/api/data', {
  server: false
})

// 静态生成
const { data } = await useFetch('/api/data', {
  lazy: true
})
</script>
```

### API Routes 设计

#### Next.js (App Router)
```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const users = await db.user.findMany()
  return NextResponse.json(users)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const user = await db.user.create({ data: body })
  return NextResponse.json(user, { status: 201 })
}

// 动态路由: app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await db.user.findUnique({ where: { id: params.id } })
  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }
  return NextResponse.json(user)
}
```

#### Nuxt 3
```typescript
// server/api/users.get.ts
export default defineEventHandler(async (event) => {
  const users = await db.user.findMany()
  return users
})

// server/api/users.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const user = await db.user.create({ data: body })
  return user
})

// server/api/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const user = await db.user.findUnique({ where: { id } })
  if (!user) {
    throw createError({ statusCode: 404, message: 'User not found' })
  }
  return user
})
```

### 数据获取模式

#### Next.js (Pages Router)
```typescript
// 服务端渲染
export async function getServerSideProps(context) {
  const data = await fetch('https://api.example.com/data')
  return { props: { data } }
}

// 静态生成
export async function getStaticProps() {
  const data = await fetch('https://api.example.com/data')
  return { props: { data }, revalidate: 60 }
}

// 动态路由静态生成
export async function getStaticPaths() {
  const posts = await fetch('https://api.example.com/posts')
  const paths = posts.map(post => ({ params: { id: post.id } }))
  return { paths, fallback: 'blocking' }
}
```

### 认证流程

#### NextAuth.js
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!
    }),
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        const user = await verifyCredentials(credentials)
        return user || null
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      session.user.id = token.id
      session.user.role = token.role
      return session
    }
  }
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
```

### Monorepo 管理

#### Turborepo
```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

---

## 💻 核心代码模式

### 服务端组件 vs 客户端组件（Next.js App Router）

```typescript
// app/ServerComponent.tsx - 服务端组件（默认）
export default async function ServerComponent() {
  const data = await fetch('https://api.example.com/data')
  
  return (
    <div>
      <h1>Server Component</h1>
      <ClientComponent data={data} />
    </div>
  )
}

// app/ClientComponent.tsx - 客户端组件
'use client'

import { useState } from 'react'

export default function ClientComponent({ data }) {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

### 中间件（Next.js）

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 检查认证
  const token = request.cookies.get('token')
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // 添加自定义 header
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'value')
  
  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*']
}
```

### 环境变量管理

```typescript
// .env.local
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_API_URL="https://api.example.com"
JWT_SECRET="your-secret-key"

// 在服务端使用
const dbUrl = process.env.DATABASE_URL

// 在客户端使用（必须以 NEXT_PUBLIC_ 开头）
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

---

## ⚠️ 常见问题

### 问题 1: 水合不匹配（Hydration Mismatch）

**原因**: 服务端和客户端渲染的 HTML 不一致

**解决方案**:
```typescript
// ❌ 错误：使用客户端专有 API
export default function Component() {
  return <div>{window.innerWidth}</div>
}

// ✅ 正确：使用 useEffect
'use client'
import { useState, useEffect } from 'react'

export default function Component() {
  const [width, setWidth] = useState(0)
  
  useEffect(() => {
    setWidth(window.innerWidth)
  }, [])
  
  return <div>{width || 'Loading...'}</div>
}
```

### 问题 2: API Routes 性能问题

**解决方案**: 使用边缘运行时

```typescript
// app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return new Response('Hello from Edge!')
}
```

### 问题 3: 静态导出限制

**解决方案**: 了解哪些功能不支持静态导出

```typescript
// next.config.js
module.exports = {
  output: 'export', // 静态导出
  // 以下功能不可用：
  // - Image Optimization
  // - Rewrites
  // - Redirects
  // - Headers
  // - Middleware
  // - Incremental Static Regeneration
}
```

---

## 🎯 检查清单

生成全栈项目文档前，确认：

- [ ] 已识别主要框架（Next.js/Nuxt/Remix/SvelteKit）
- [ ] 已确定渲染策略（SSR/SSG/ISR）
- [ ] 已确定数据获取方式（Server Components/getServerSideProps 等）
- [ ] 已确定认证方案（NextAuth/Lucia/自定义）
- [ ] 已确定数据库和 ORM（Prisma/Drizzle 等）
- [ ] 已确定部署平台（Vercel/Netlify/自托管）
- [ ] 已检查是否使用 Monorepo（Turborepo/Nx）
- [ ] 已确定 API Routes 设计
- [ ] 已确定环境变量管理策略

---

**版本**: v3.0  
**路径**: `core/project_types/fullstack.md`  
**最后更新**: 2026-01-21
