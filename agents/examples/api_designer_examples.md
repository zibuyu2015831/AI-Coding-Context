# API 设计师角色使用示例

**角色**: API 设计师 (API Designer)  
**文档**: [api_designer.md](../development/api_designer.md)

---

## 📋 目录

- [示例 1: 设计 RESTful API](#示例1-设计restful-api)
- [示例 2: 设计分页查询 API](#示例2-设计分页查询API)

---

## 示例 1: 设计 RESTful API

### 场景说明

为用户管理功能设计 RESTful API。

### 用户输入

```markdown
# 需求

- 创建用户
- 查询用户列表
- 查询用户详情
- 更新用户
- 删除用户
```

### 角色响应

````markdown
# 用户管理 API 设计

## 1. API 列表

| 方法   | 路径            | 描述         |
| ------ | --------------- | ------------ |
| POST   | /api/users      | 创建用户     |
| GET    | /api/users      | 查询用户列表 |
| GET    | /api/users/{id} | 查询用户详情 |
| PUT    | /api/users/{id} | 更新用户     |
| DELETE | /api/users/{id} | 删除用户     |

---

## 2. API 详细设计

### 2.1 创建用户

**请求**:

```http
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "user"
}
```

**响应**:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "createdAt": "2025-12-01T10:00:00Z"
}
```

**错误响应**:

```http
HTTP/1.1 400 Bad Request

{
  "error": "VALIDATION_ERROR",
  "message": "邮箱格式不正确",
  "field": "email"
}
```

---

### 2.2 查询用户列表

**请求**:

```http
GET /api/users?page=1&pageSize=20&role=admin&sort=createdAt:desc
```

**响应**:

```http
HTTP/1.1 200 OK

{
  "data": [
    {
      "id": 123,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "admin",
      "createdAt": "2025-12-01T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

---

### 2.3 查询用户详情

**请求**:

```http
GET /api/users/123
```

**响应**:

```http
HTTP/1.1 200 OK

{
  "id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "admin",
  "profile": {
    "avatar": "https://example.com/avatar.jpg",
    "bio": "Software Engineer"
  },
  "createdAt": "2025-12-01T10:00:00Z",
  "updatedAt": "2025-12-01T12:00:00Z"
}
```

**错误响应**:

```http
HTTP/1.1 404 Not Found

{
  "error": "USER_NOT_FOUND",
  "message": "用户不存在"
}
```

---

### 2.4 更新用户

**请求**:

```http
PUT /api/users/123
Content-Type: application/json

{
  "email": "newemail@example.com",
  "profile": {
    "bio": "Senior Engineer"
  }
}
```

**响应**:

```http
HTTP/1.1 200 OK

{
  "id": 123,
  "username": "john_doe",
  "email": "newemail@example.com",
  "updatedAt": "2025-12-01T13:00:00Z"
}
```

---

### 2.5 删除用户

**请求**:

```http
DELETE /api/users/123
```

**响应**:

```http
HTTP/1.1 204 No Content
```

---

## 3. 通用规范

### 3.1 HTTP 状态码

| 状态码 | 含义                  | 使用场景         |
| ------ | --------------------- | ---------------- |
| 200    | OK                    | 成功(GET, PUT)   |
| 201    | Created               | 创建成功(POST)   |
| 204    | No Content            | 删除成功(DELETE) |
| 400    | Bad Request           | 参数错误         |
| 401    | Unauthorized          | 未认证           |
| 403    | Forbidden             | 无权限           |
| 404    | Not Found             | 资源不存在       |
| 500    | Internal Server Error | 服务器错误       |

### 3.2 错误响应格式

```json
{
  "error": "ERROR_CODE",
  "message": "用户友好的错误信息",
  "field": "出错的字段(可选)",
  "details": {}
}
```

### 3.3 认证

```http
Authorization: Bearer <token>
```
````

### 关键点说明

- ✅ **RESTful 规范**: 正确使用 HTTP 方法和状态码
- ✅ **完整示例**: 请求和响应的完整 JSON
- ✅ **错误处理**: 标准化的错误响应

---

## 示例 2: 设计分页查询 API

### 场景说明

设计支持分页、排序、筛选的列表查询 API。

### 用户输入

```markdown
# 需求

- 支持分页
- 支持按字段排序
- 支持多条件筛选
```

### 角色响应

````markdown
# 分页查询 API 设计

## 查询参数设计

```http
GET /api/orders?
  page=1&
  pageSize=20&
  status=PAID&
  userId=123&
  startDate=2025-01-01&
  endDate=2025-12-31&
  sort=createdAt:desc,total:asc
```

### 参数说明

| 参数      | 类型   | 必填 | 说明                         |
| --------- | ------ | ---- | ---------------------------- |
| page      | int    | 否   | 页码,默认 1                  |
| pageSize  | int    | 否   | 每页数量,默认 20,最大 100    |
| status    | string | 否   | 订单状态                     |
| userId    | int    | 否   | 用户 ID                      |
| startDate | date   | 否   | 开始日期                     |
| endDate   | date   | 否   | 结束日期                     |
| sort      | string | 否   | 排序字段,格式:field:asc/desc |

---

## 响应设计

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  },
  "filters": {
    "status": "PAID",
    "userId": 123
  }
}
```
````

### 关键点说明

- ✅ **灵活的查询参数**: 支持分页、排序、筛选
- ✅ **分页元数据**: 包含总数、总页数等信息

---

## 📝 使用建议

1. **CRUD API** → 示例 1
2. **列表查询** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
