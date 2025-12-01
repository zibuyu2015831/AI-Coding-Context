# Vue3 专家角色使用示例

**角色**: Vue3 专家 (Vue3 Expert)  
**文档**: [vue3_expert.md](../language_specific/vue3_expert.md)

---

## 📋 目录

- [示例 1: 创建用户列表组件](#示例1-创建用户列表组件)
- [示例 2: 创建表单组件](#示例2-创建表单组件)

---

## 示例 1: 创建用户列表组件

### 场景说明

创建一个带搜索和分页的用户列表组件。

### 用户输入

```markdown
# 需求

- 显示用户列表(表格)
- 支持搜索
- 支持分页
- 点击编辑按钮
```

### 角色响应

```vue
<template>
  <div class="user-list">
    <a-input-search
      v-model:value="searchText"
      placeholder="搜索用户..."
      @search="handleSearch"
      :loading="loading"
      style="margin-bottom: 16px"
    />

    <a-table
      :columns="columns"
      :data-source="data"
      :pagination="pagination"
      :loading="loading"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a @click="handleEdit(record)">编辑</a>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import type { TableColumnsType, TablePaginationConfig } from "ant-design-vue";
import { getUserList } from "@/api/user";

// 类型定义
interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

// 状态
const loading = ref(false);
const searchText = ref("");
const data = ref<User[]>([]);
const pagination = reactive<TablePaginationConfig>({
  current: 1,
  pageSize: 10,
  total: 0,
});

// 表格列定义
const columns: TableColumnsType = [
  { title: "ID", dataIndex: "id", key: "id", width: 80 },
  { title: "用户名", dataIndex: "username", key: "username" },
  { title: "邮箱", dataIndex: "email", key: "email" },
  { title: "角色", dataIndex: "role", key: "role" },
  { title: "操作", key: "action", width: 100 },
];

// 方法
const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getUserList({
      query: searchText.value,
      page: pagination.current,
      pageSize: pagination.pageSize,
    });
    data.value = res.data;
    pagination.total = res.total;
  } catch (error) {
    console.error("获取用户列表失败:", error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.current = 1;
  fetchData();
};

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchData();
};

const handleEdit = (user: User) => {
  console.log("编辑用户:", user);
  // 跳转到编辑页面或打开编辑弹窗
};

// 初始化
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.user-list {
  padding: 24px;
  background: #fff;
}
</style>
```

### 关键点说明

- ✅ **Composition API**: 使用`<script setup>`
- ✅ **TypeScript**: 完整的类型定义
- ✅ **响应式**: 正确使用 ref 和 reactive
- ✅ **生命周期**: onMounted 初始化数据

---

## 示例 2: 创建表单组件

### 场景说明

创建用户编辑表单,包含验证。

### 用户输入

```markdown
# 需求

- 用户名、邮箱、角色字段
- 表单验证
- 提交保存
```

### 角色响应

```vue
<template>
  <a-form
    :model="formState"
    :rules="rules"
    :label-col="{ span: 6 }"
    :wrapper-col="{ span: 18 }"
    @finish="handleSubmit"
  >
    <a-form-item label="用户名" name="username">
      <a-input v-model:value="formState.username" placeholder="请输入用户名" />
    </a-form-item>

    <a-form-item label="邮箱" name="email">
      <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
    </a-form-item>

    <a-form-item label="角色" name="role">
      <a-select v-model:value="formState.role" placeholder="请选择角色">
        <a-select-option value="user">普通用户</a-select-option>
        <a-select-option value="admin">管理员</a-select-option>
      </a-select>
    </a-form-item>

    <a-form-item :wrapper-col="{ offset: 6, span: 18 }">
      <a-button type="primary" html-type="submit" :loading="loading">
        保存
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import type { Rule } from "ant-design-vue/es/form";
import { updateUser } from "@/api/user";
import { message } from "ant-design-vue";

// Props
interface Props {
  userId: number;
}
const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  success: [];
}>();

// 表单状态
const formState = reactive({
  username: "",
  email: "",
  role: "user",
});

// 验证规则
const rules: Record<string, Rule[]> = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度3-20个字符", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
};

const loading = ref(false);

// 提交表单
const handleSubmit = async () => {
  loading.value = true;
  try {
    await updateUser(props.userId, formState);
    message.success("保存成功");
    emit("success");
  } catch (error) {
    message.error("保存失败");
  } finally {
    loading.value = false;
  }
};
</script>
```

### 关键点说明

- ✅ **表单验证**: 使用 rules 定义验证规则
- ✅ **Props 和 Emits**: TypeScript 类型定义
- ✅ **错误处理**: try-catch + 用户提示

---

## 📝 使用建议

1. **列表组件** → 示例 1
2. **表单组件** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
