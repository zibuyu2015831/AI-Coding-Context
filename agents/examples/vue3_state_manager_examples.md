# Vue3 状态管理师角色使用示例

**角色**: Vue3 状态管理师 (Vue3 State Manager)  
**文档**: [vue3_state_manager.md](../language_specific/vue3_state_manager.md)

---

## 📋 目录

- [示例 1: 创建用户 Store](#示例1-创建用户store)
- [示例 2: 创建购物车 Store](#示例2-创建购物车store)

---

## 示例 1: 创建用户 Store

### 场景说明

使用 Pinia 创建用户状态管理 Store。

### 用户输入

```markdown
# 需求

- 存储用户信息
- 登录/登出
- 获取用户信息
```

### 角色响应

```typescript
// stores/user.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "@/types/user";
import { login as loginApi, getUserInfo } from "@/api/auth";

export const useUserStore = defineStore("user", () => {
  // State
  const token = ref<string>("");
  const userInfo = ref<User | null>(null);

  // Getters
  const isLoggedIn = computed(() => !!token.value);
  const username = computed(() => userInfo.value?.username || "");
  const role = computed(() => userInfo.value?.role || "guest");

  // Actions
  const login = async (username: string, password: string) => {
    try {
      const res = await loginApi({ username, password });
      token.value = res.token;
      localStorage.setItem("token", res.token);

      // 登录成功后获取用户信息
      await fetchUserInfo();

      return true;
    } catch (error) {
      console.error("登录失败:", error);
      return false;
    }
  };

  const logout = () => {
    token.value = "";
    userInfo.value = null;
    localStorage.removeItem("token");
  };

  const fetchUserInfo = async () => {
    try {
      const res = await getUserInfo();
      userInfo.value = res.data;
    } catch (error) {
      console.error("获取用户信息失败:", error);
      // 如果获取失败,清除token
      logout();
    }
  };

  // 初始化:从localStorage恢复token
  const init = () => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      token.value = savedToken;
      fetchUserInfo();
    }
  };

  return {
    // State
    token,
    userInfo,
    // Getters
    isLoggedIn,
    username,
    role,
    // Actions
    login,
    logout,
    fetchUserInfo,
    init,
  };
});
```

### 使用示例

```vue
<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import { onMounted } from "vue";

const userStore = useUserStore();

onMounted(() => {
  userStore.init();
});

const handleLogin = async () => {
  const success = await userStore.login("admin", "password");
  if (success) {
    console.log("登录成功");
  }
};
</script>

<template>
  <div v-if="userStore.isLoggedIn">
    欢迎, {{ userStore.username }}
    <button @click="userStore.logout">登出</button>
  </div>
  <div v-else>
    <button @click="handleLogin">登录</button>
  </div>
</template>
```

### 关键点说明

- ✅ **Setup 语法**: 使用 Composition API 风格
- ✅ **类型安全**: 完整的 TypeScript 类型
- ✅ **持久化**: localStorage 存储 token
- ✅ **错误处理**: try-catch 处理异常

---

## 示例 2: 创建购物车 Store

### 场景说明

创建购物车状态管理,包含添加、删除、计算总价等功能。

### 用户输入

```markdown
# 需求

- 添加商品到购物车
- 删除商品
- 修改数量
- 计算总价
```

### 角色响应

```typescript
// stores/cart.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image: string;
}

export const useCartStore = defineStore("cart", () => {
  // State
  const items = ref<CartItem[]>([]);

  // Getters
  const totalItems = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  );

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  const isEmpty = computed(() => items.value.length === 0);

  // Actions
  const addItem = (product: Omit<CartItem, "quantity">) => {
    const existingItem = items.value.find((item) => item.id === product.id);

    if (existingItem) {
      existingItem.quantity++;
    } else {
      items.value.push({ ...product, quantity: 1 });
    }

    saveToStorage();
  };

  const removeItem = (productId: number) => {
    const index = items.value.findIndex((item) => item.id === productId);
    if (index > -1) {
      items.value.splice(index, 1);
      saveToStorage();
    }
  };

  const updateQuantity = (productId: number, quantity: number) => {
    const item = items.value.find((item) => item.id === productId);
    if (item) {
      if (quantity <= 0) {
        removeItem(productId);
      } else {
        item.quantity = quantity;
        saveToStorage();
      }
    }
  };

  const clear = () => {
    items.value = [];
    saveToStorage();
  };

  // 持久化
  const saveToStorage = () => {
    localStorage.setItem("cart", JSON.stringify(items.value));
  };

  const loadFromStorage = () => {
    const saved = localStorage.getItem("cart");
    if (saved) {
      items.value = JSON.parse(saved);
    }
  };

  return {
    // State
    items,
    // Getters
    totalItems,
    totalPrice,
    isEmpty,
    // Actions
    addItem,
    removeItem,
    updateQuantity,
    clear,
    loadFromStorage,
  };
});
```

### 使用示例

```vue
<script setup lang="ts">
import { useCartStore } from "@/stores/cart";
import { onMounted } from "vue";

const cartStore = useCartStore();

onMounted(() => {
  cartStore.loadFromStorage();
});

const handleAddToCart = () => {
  cartStore.addItem({
    id: 1,
    name: "iPhone 15",
    price: 5999,
    image: "/images/iphone15.jpg",
  });
};
</script>

<template>
  <div class="cart">
    <div class="cart-header">购物车 ({{ cartStore.totalItems }}件商品)</div>

    <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
      <img :src="item.image" :alt="item.name" />
      <div>{{ item.name }}</div>
      <div>¥{{ item.price }}</div>
      <a-input-number
        :value="item.quantity"
        :min="1"
        @change="(val) => cartStore.updateQuantity(item.id, val)"
      />
      <button @click="cartStore.removeItem(item.id)">删除</button>
    </div>

    <div class="cart-footer">总价: ¥{{ cartStore.totalPrice.toFixed(2) }}</div>
  </div>
</template>
```

### 关键点说明

- ✅ **计算属性**: 使用 computed 计算总价
- ✅ **数组操作**: 正确处理添加、删除、更新
- ✅ **持久化**: localStorage 保存购物车
- ✅ **类型定义**: CartItem 接口

---

## 📝 使用建议

1. **用户状态** → 示例 1
2. **购物车状态** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
