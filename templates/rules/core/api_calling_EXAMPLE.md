# API调用规范

<!-- 使用说明 START -->
<!-- ⚠️ 复制到IDE时请删除此部分（从START到END标记之间的所有内容） -->

## 📋 Rule使用说明

**Rule名称**: API调用规范  
**类型**: Core  
**优先级**: P0-必须  
**使用层级**: **必须携带**  
**生成时间**: [自动填写]  
**最后更新**: [自动填写]

---

### 📌 使用层级说明

- **必须携带**: 此rule必须包含在IDE配置中，核心规范不可缺少
- **AI决策**: AI根据场景决定是否应用此rule，IDE可配置为可选加载
- **手动携带**: 用户根据个人/团队需要选择是否包含

**本Rule的使用层级**: **必须携带**

**建议配置**:

- Cursor: 包含在.cursorrules（必需）
- Windsurf: 添加到Custom Rules（必需）
- 所有IDE: 此为核心规范，强烈建议包含

---

### 📐 适用场景

- 所有涉及HTTP请求的场景
- API数据获取和提交
- 与后端服务通信

### 🔄 更新触发条件

此rule需要更新的情况:

- [ ] API封装方式变更
- [ ] HTTP客户端库更换
- [ ] 错误处理机制调整
- [ ] 拦截器配置变更

### 📚 依赖关系

**依赖的其他rule**:

- `core/error_handling.md` - 错误处理规范

**被依赖的rule**:

- `workflow/feature_development.md` - 需要遵守API调用规范

---

### ⚠️ 复制提醒

将此rule复制到IDE配置时:

1. 删除从`<!-- 使用说明 START -->`到`<!-- 使用说明 END -->`的所有内容
2. 仅保留下方"实际Rule内容"部分
3. 确保删除所有HTML注释标记

---

<!-- 使用说明 END -->

<!-- ================================= -->
<!-- 实际Rule内容 START - 复制此部分到IDE -->
<!-- ================================= -->

## API调用规范

### 核心要求

1. **使用统一API封装**

   - 必须使用项目`src/api/`目录下的封装函数
   - 禁止在组件中直接使用axios、fetch或其他HTTP客户端
   - 所有API调用都必须经过统一的请求/响应拦截器

2. **完整的错误处理**

   - 每个API调用都必须处理错误情况
   - 使用统一的错误处理器或error boundary
   - 提供用户友好的错误提示

3. **加载状态管理**
   - 提供明确的加载状态反馈
   - 避免重复请求
   - 支持请求取消（长时间请求）

---

### ✅ 检查清单

在编写API调用代码时，确保:

- [ ] 使用了`src/api/*`下的封装函数
- [ ] 包含了完整的错误处理
- [ ] 有loading状态管理
- [ ] 有适当的用户反馈（加载中/成功/失败）
- [ ] 避免了重复请求

---

### 💡 代码示例

**✅ 正确示例**:

```typescript
// 使用API封装
import { userApi } from "@/api/user";

const fetchUsers = async () => {
  loading.value = true;
  try {
    const { data } = await userApi.getList(params);
    users.value = data;
  } catch (error) {
    handleError(error); // 统一错误处理
  } finally {
    loading.value = false;
  }
};
```

**❌ 错误示例**:

```typescript
// 直接使用axios
import axios from "axios";

const fetchUsers = async () => {
  const res = await axios.get("/api/users"); // ❌ 绕过封装
  users.value = res.data; // ❌ 无错误处理
  // ❌ 无加载状态
};
```

---

### 🔗 相关文档

当涉及API调用时，应参考:

- `dev_docs/api_layer.md` - 完整的API层文档
- `dev_docs/error_handling.md` - 错误处理最佳实践

---

<!-- ================================= -->
<!-- 实际Rule内容 END -->
<!-- ================================= -->

<!-- 元信息 - 仅供框架内部使用 -->
<!--
适用项目类型: 前端/全栈
技术栈: Vue 3, React, Angular, 所有前端框架
最小版本: v1.0
-->
