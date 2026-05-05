---
title: 测试工程师角色使用示例
summary: 展示测试工程师角色在登录功能和订单接口场景中的测试用例设计与测试代码输出方式。
keywords: example | test-engineer | testing | regression | qa | aicc
scope: 测试工程师角色示例
related_files: 无
dependencies: agents/runtime/test_engineer.md | agents/examples/README.md
verified_at: 2026-05-05
---

# 测试工程师角色使用示例

**角色**: 测试工程师 (Test Engineer)  
**文档**: [test_engineer.md](../runtime/test_engineer.md)

---

## 📋 目录

- [示例 1: 为登录功能生成测试用例](#示例1-为登录功能生成测试用例)
- [示例 2: 为订单接口生成集成测试](#示例2-为订单接口生成集成测试)

---

## 示例 1: 为登录功能生成测试用例

### 场景说明

为用户登录功能设计完整的测试用例,覆盖正常流程和异常场景。

### 用户输入

```markdown
# 登录功能需求

- 用户输入用户名和密码
- 验证成功返回 Token
- 验证失败返回错误信息
```

### 角色响应

````markdown
# 登录功能测试用例

## 测试用例列表

| ID     | 名称         | 输入                         | 预期结果              | 优先级 |
| ------ | ------------ | ---------------------------- | --------------------- | ------ |
| TC-001 | 正常登录     | 正确的用户名和密码           | 200 OK, 返回 Token    | P0     |
| TC-002 | 密码错误     | 正确用户名,错误密码          | 401 Unauthorized      | P0     |
| TC-003 | 用户不存在   | 不存在的用户名               | 404 Not Found         | P0     |
| TC-004 | 用户名为空   | 空用户名                     | 400 Bad Request       | P1     |
| TC-005 | 密码为空     | 空密码                       | 400 Bad Request       | P1     |
| TC-006 | SQL 注入测试 | username: `admin' OR '1'='1` | 401/400               | P0     |
| TC-007 | 密码长度边界 | 密码 1 位                    | 400 Bad Request       | P1     |
| TC-008 | 并发登录     | 同一用户同时登录             | 都成功,返回不同 Token | P1     |

---

## 测试代码 (Python/PyTest)

```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestLogin:

    def test_login_success(self):
        """TC-001: 正常登录"""
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "token" in response.json()
        assert len(response.json()["token"]) > 0

    def test_login_wrong_password(self):
        """TC-002: 密码错误"""
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "error" in response.json()

    def test_login_user_not_found(self):
        """TC-003: 用户不存在"""
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": "nonexistuser",
            "password": "password123"
        })
        assert response.status_code == 404

    def test_login_empty_username(self):
        """TC-004: 用户名为空"""
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": "",
            "password": "password123"
        })
        assert response.status_code == 400

    def test_login_sql_injection(self):
        """TC-006: SQL注入测试"""
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": "admin' OR '1'='1",
            "password": "anything"
        })
        assert response.status_code in [400, 401]
        assert "token" not in response.json()
```

---

## 测试数据

```json
{
  "validUsers": [
    { "username": "testuser", "password": "password123" },
    { "username": "admin", "password": "admin123" }
  ],
  "invalidCases": [
    { "username": "", "password": "password123" },
    { "username": "testuser", "password": "" },
    { "username": "admin' OR '1'='1", "password": "anything" }
  ]
}
```
````

### 关键点说明

- ✅ **全面覆盖**: 正常流程+异常流程+边界条件+安全测试
- ✅ **可执行代码**: 真实的 PyTest 测试代码
- ✅ **测试数据**: 提供测试数据集

---

## 示例 2: 为订单接口生成集成测试

### 场景说明

测试订单创建接口的完整流程,包括库存扣减、订单创建、支付等。

### 用户输入

```markdown
# 订单创建接口

POST /api/orders

- 检查库存
- 创建订单
- 扣减库存
- 返回订单 ID
```

### 角色响应

````markdown
# 订单创建集成测试

## 测试场景

### 场景 1: 正常下单流程

```python
def test_create_order_success(db, api_client):
    # 准备: 设置商品库存
    db.execute("UPDATE products SET stock = 100 WHERE id = 1")

    # 执行: 创建订单
    response = api_client.post("/api/orders", json={
        "userId": "user123",
        "items": [
            {"productId": 1, "quantity": 2, "price": 99.99}
        ]
    })

    # 验证: 订单创建成功
    assert response.status_code == 201
    order_id = response.json()["orderId"]

    # 验证: 库存正确扣减
    stock = db.query("SELECT stock FROM products WHERE id = 1")[0]
    assert stock["stock"] == 98

    # 验证: 订单记录存在
    order = db.query("SELECT * FROM orders WHERE id = ?", [order_id])[0]
    assert order["user_id"] == "user123"
    assert order["total"] == 199.98
```

### 场景 2: 库存不足

```python
def test_create_order_insufficient_stock(db, api_client):
    # 准备: 设置库存为1
    db.execute("UPDATE products SET stock = 1 WHERE id = 1")

    # 执行: 尝试购买2个
    response = api_client.post("/api/orders", json={
        "userId": "user123",
        "items": [
            {"productId": 1, "quantity": 2, "price": 99.99}
        ]
    })

    # 验证: 返回错误
    assert response.status_code == 400
    assert "库存不足" in response.json()["error"]

    # 验证: 库存未变化
    stock = db.query("SELECT stock FROM products WHERE id = 1")[0]
    assert stock["stock"] == 1

    # 验证: 订单未创建
    orders = db.query("SELECT COUNT(*) as count FROM orders WHERE user_id = 'user123'")[0]
    assert orders["count"] == 0
```
````

### 关键点说明

- ✅ **集成测试**: 测试多个组件的协作
- ✅ **数据验证**: 验证数据库状态变化
- ✅ **回滚验证**: 验证失败时数据未变化

---

## 📝 使用建议

1. **首次使用**: 建议先查看示例 1,了解测试用例设计
2. **不同场景**:
   - 单元测试 → 示例 1
   - 集成测试 → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
