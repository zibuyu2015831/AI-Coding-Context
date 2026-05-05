---
title: TypeScript 专家角色使用示例
summary: 展示 TypeScript 专家角色在泛型约束、可辨识联合类型和运行时校验场景中的典型输出方式。
keywords: example | typescript-expert | generics | zod | types | aicc
scope: TypeScript 专家角色示例
related_files: 无
dependencies: agents/language_specific/typescript/typescript_expert.md | agents/examples/README.md
verified_at: 2026-05-05
---

# TypeScript 专家 (TypeScript Expert) 角色使用示例

**角色**: TypeScript 专家
**文档**: [typescript_expert.md](../language_specific/typescript/typescript_expert.md)

---

## 📋 目录

- [示例 1: 泛型约束与工具类型](#示例1)
- [示例 2: 可辨识联合类型 (Discriminated Unions)](#示例2)
- [示例 3: Zod 运行时校验与类型推导](#示例3)

---

## <a id="示例1"></a>示例 1: 泛型约束与工具类型

### 场景说明

编写一个通用的更新函数，要求只能更新对象中存在的属性，并且值的类型必须匹配。

### 用户输入

```text
写一个 updateObject(obj, key, value) 函数。
要求：
1. key 必须是 obj 里的键
2. value 的类型必须和 obj[key] 的类型一致
3. 要有完整的类型提示
```

### 角色响应

```typescript
/**
 * 更新对象属性
 * @param obj 目标对象
 * @param key 属性名 (仅限于 obj 已有的 key)
 * @param value 属性值 (必须匹配 obj[key] 的类型)
 */
function updateObject<T, K extends keyof T>(obj: T, key: K, value: T[K]): void {
  obj[key] = value;
}

// 使用示例
interface User {
  id: number;
  name: string;
  isActive: boolean;
}

const user: User = { id: 1, name: "Alice", isActive: true };

// ✅ 正确
updateObject(user, "name", "Bob");
updateObject(user, "isActive", false);

// ❌ 错误：Key 不存在
// updateObject(user, "age", 18); // Error: Argument of type '"age"' is not assignable to parameter of type 'keyof User'.

// ❌ 错误：Value 类型不匹配
// updateObject(user, "name", 123); // Error: Argument of type 'number' is not assignable to parameter of type 'string'.
```

### 关键点说明

- ✅ **Generic Constraint**: `<K extends keyof T>` 确保 key 只能是对象的键。
- ✅ **Indexed Access Type**: `T[K]` 动态获取对应属性的类型，确保 value 类型安全。

---

## <a id="示例2"></a>示例 2: 可辨识联合类型 (Discriminated Unions)

### 场景说明

处理多种可能的状态（如 API 请求的 Loading, Success, Error），使用类型守卫进行安全的模式匹配。

### 用户输入

```text
定义一个 API 响应状态，可能有三种情况：
1. Loading
2. Success (包含 data)
3. Error (包含 error 信息)
写一个函数根据状态渲染不同的文本。
```

### 角色响应

```typescript
// 1. 定义三种状态接口，拥有共同的区分字段 'status'
interface LoadingState {
  status: "loading";
}

interface SuccessState {
  status: "success";
  data: string;
}

interface ErrorState {
  status: "error";
  error: Error;
}

// 2. 联合类型
type RequestState = LoadingState | SuccessState | ErrorState;

// 3. 类型守卫函数
function renderState(state: RequestState): string {
  switch (state.status) {
    case "loading":
      // 在此分支下，TS 知道 state 是 LoadingState
      return "Loading...";

    case "success":
      // 能够安全访问 data
      return `Data: ${state.data}`;

    case "error":
      // 能够安全访问 error
      return `Error: ${state.error.message}`;

    default:
      // 穷尽性检查 (Exhaustiveness checking)
      const _exhaustiveCheck: never = state;
      return _exhaustiveCheck;
  }
}
```

### 关键点说明

- ✅ **Discriminated Union**: 利用 `status` 字段区分类型。
- ✅ **Type Narrowing**: `switch` 或 `if` 语句后，TS 会自动收窄类型。
- ✅ **Exhaustiveness Check**: `never` 类型确保覆盖了所有情况，如果新增状态未处理，编译会报错。

---

## <a id="示例3"></a>示例 3: Zod 运行时校验与类型推导

### 场景说明

定义数据校验 Schema，并利用它自动生成 TypeScript 类型，避免写两遍重复代码。

### 用户输入

```text
使用 Zod 库定义一个 User Schema：
包含 id (数字), email (邮箱格式), role (admin 或 user)
并从中推导出 User 类型。
```

### 角色响应

```typescript
import { z } from "zod";

// 1. 定义 Schema (既是运行时校验逻辑，又是类型定义的来源)
const UserSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email(),
  role: z.enum(["admin", "user"]),
  settings: z
    .object({
      theme: z.enum(["dark", "light"]).default("light"),
    })
    .optional(),
});

// 2. 推导 TS 类型
type User = z.infer<typeof UserSchema>;

// 等价于:
// type User = {
//     id: number;
//     email: string;
//     role: "admin" | "user";
//     settings?: { theme: "dark" | "light" } | undefined;
// }

// 3. 运行时校验
function processUser(input: unknown) {
  try {
    const user: User = UserSchema.parse(input);
    console.log("Valid user:", user.email);
  } catch (err) {
    console.error("Validation failed");
  }
}
```

### 关键点说明

- ✅ **Single Source of Truth**: Schema 即类型，避免类型定义与校验逻辑不同步。
- ✅ **z.infer**: 利用工具类型提取 Schema 对应的静态类型。
- ✅ **Runtime Safety**: 解决了 TS 无法在编译后进行类型检查的问题。

---

## 📝 使用建议

1.  **基础**: 掌握 **示例 1** 中的泛型用法是编写高质量 TS 库的基础。
2.  **业务逻辑**: 在处理 Redux 状态或 API 响应时，**示例 2** 的模式非常强大且安全。
3.  **IO 边界**: 在处理外部输入（API, Form）时，强烈建议使用 **示例 3** 结合 Zod/Yup。
