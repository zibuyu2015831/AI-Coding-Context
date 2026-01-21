---
title: Web 前端项目配置
summary: 定义 Web 前端项目（Vue.js/React/Angular/Svelte）的推荐子文档清单、特殊关注点和核心代码模式。包括 API 调用、状态管理、路由配置等关键规范。
keywords: web-frontend | vue | react | angular | svelte | spa | api-layer | state-management
scope: Web 前端项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# Web 前端项目

> **适用框架**: Vue.js / React / Angular / Svelte / Solid.js

---

## 🎯 适用框架

- **Vue 生态**: Vue 3 + Vite + Vue Router + Pinia
- **React 生态**: React 18 + Vite/CRA + React Router + Zustand/Redux
- **Angular**: Angular 15+ + RxJS + NgRx
- **Svelte**: SvelteKit + Svelte Store
- **Solid.js**: Solid + Solid Router + Solid Store

---

## 📋 推荐子文档清单

| 优先级 | 文档名称                  | 用途                            |
| ------ | ------------------------- | ------------------------------- |
| 🔴 高  | `api_layer.md`            | API 调用规范                    |
| 🔴 高  | `state_management.md`     | 状态管理（Pinia/Redux/Zustand） |
| 🔴 高  | `routing_guide.md`        | 路由与权限                      |
| 🟡 中  | `component_guide.md`      | 组件开发规范                    |
| 🟡 中  | `styling_guide.md`        | CSS/样式方案                    |
| 🟡 中  | `form_validation.md`      | 表单验证                        |
| 🟢 低  | `internationalization.md` | 国际化方案                      |

---

## 🔍 特殊关注点

### UI 组件库

- **Vue**: Element Plus / Ant Design Vue / Naive UI / Vuetify
- **React**: Ant Design / Material-UI / Chakra UI / shadcn/ui
- **Angular**: Angular Material / PrimeNG / NG-ZORRO

### CSS 方案

- **原子化 CSS**: Tailwind CSS / UnoCSS / Windi CSS
- **CSS-in-JS**: Styled Components / Emotion
- **CSS Modules**: 模块化 CSS
- **预处理器**: Sass / Less / Stylus

### 构建工具配置

- **Vite**: 推荐用于现代项目（快速 HMR）
- **Webpack**: 成熟项目或需要复杂配置
- **Rollup**: 库开发
- **Turbopack**: Next.js 13+ 实验性支持

### SEO 优化策略

- **SSR**: 使用 Nuxt / Next.js / SvelteKit
- **SSG**: 静态站点生成
- **预渲染**: Prerender SPA Plugin
- **Meta 标签**: vue-meta / react-helmet

---

## 💻 核心代码模式

### API 调用模式

```typescript
// 统一的 API 封装
import { api } from '@/api'

// GET 请求
const { data, loading, error } = await api.get('/users')

// POST 请求
const result = await api.post('/users', {
  name: 'John',
  email: 'john@example.com'
})

// 错误处理
try {
  const data = await api.get('/endpoint')
} catch (error) {
  if (error.response?.status === 401) {
    // 处理未授权
  }
}
```

### 组件开发模式（Vue 3）

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props
interface Props {
  title: string
  count?: number
}
const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// Emits
interface Emits {
  (e: 'update', value: number): void
  (e: 'delete'): void
}
const emit = defineEmits<Emits>()

// State
const localCount = ref(props.count)

// Computed
const doubleCount = computed(() => localCount.value * 2)

// Methods
const increment = () => {
  localCount.value++
  emit('update', localCount.value)
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="counter">
    <h2>{{ title }}</h2>
    <p>Count: {{ localCount }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>
```

### 组件开发模式（React）

```typescript
import { useState, useEffect, useCallback } from 'react'

interface CounterProps {
  title: string
  initialCount?: number
  onUpdate?: (value: number) => void
}

export const Counter: React.FC<CounterProps> = ({
  title,
  initialCount = 0,
  onUpdate
}) => {
  const [count, setCount] = useState(initialCount)

  const increment = useCallback(() => {
    const newCount = count + 1
    setCount(newCount)
    onUpdate?.(newCount)
  }, [count, onUpdate])

  useEffect(() => {
    console.log('Component mounted')
  }, [])

  return (
    <div className="counter">
      <h2>{title}</h2>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  )
}
```

### 状态管理模式（Pinia）

```typescript
// stores/user.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    token: ''
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.user?.name || 'Guest'
  },
  
  actions: {
    async login(credentials: LoginCredentials) {
      const { user, token } = await api.post('/auth/login', credentials)
      this.user = user
      this.token = token
    },
    
    logout() {
      this.user = null
      this.token = ''
    }
  }
})

// 在组件中使用
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const { isLoggedIn, userName } = storeToRefs(userStore)
```

### 路由配置模式

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

## ⚠️ 常见问题

### 问题 1: API 调用分散，难以维护

**解决方案**: 创建统一的 API 层

- 集中管理所有 API 端点
- 统一错误处理和拦截器
- 类型安全的请求/响应定义

### 问题 2: 状态管理混乱

**解决方案**: 明确状态管理策略

- 全局状态使用 Pinia/Redux/Zustand
- 组件状态使用 useState/ref
- 服务器状态使用 TanStack Query/SWR

### 问题 3: 组件复用性差

**解决方案**: 遵循组件设计原则

- 单一职责原则
- Props 接口清晰
- 使用组合式 API/Hooks
- 提取可复用逻辑（Composables/Custom Hooks）

---

## 🎯 检查清单

生成 Web 前端项目文档前，确认：

- [ ] 已识别主要框架（Vue/React/Angular/Svelte）
- [ ] 已确定状态管理方案（Pinia/Redux/Zustand 等）
- [ ] 已确定 UI 组件库（Element Plus/Ant Design 等）
- [ ] 已确定 CSS 方案（Tailwind/CSS Modules 等）
- [ ] 已确定构建工具（Vite/Webpack）
- [ ] 已检查是否需要 SSR/SSG
- [ ] 已确定路由方案（Vue Router/React Router）
- [ ] 已确定是否需要国际化

---

**版本**: v3.0  
**路径**: `core/project_types/web_frontend.md`  
**最后更新**: 2026-01-21
