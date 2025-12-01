# 代码审查员角色使用示例

**角色**: 代码审查员 (Code Reviewer)  
**文档**: [code_reviewer.md](../runtime/code_reviewer.md)

---

## 📋 目录

- [示例 1: 审查业务逻辑代码](#示例1-审查业务逻辑代码)
- [示例 2: 审查 API 接口代码](#示例2-审查api接口代码)
- [示例 3: 审查数据库操作代码](#示例3-审查数据库操作代码)

---

## 示例 1: 审查业务逻辑代码

### 场景说明

审查订单创建的业务逻辑代码,检查代码质量、潜在 bug 和最佳实践。

### 用户输入

```typescript
// 订单创建服务
class OrderService {
  async createOrder(userId: string, items: any[]) {
    // 计算总价
    let total = 0;
    for (let i = 0; i < items.length; i++) {
      total += items[i].price * items[i].quantity;
    }

    // 检查库存
    for (let i = 0; i < items.length; i++) {
      const stock = await db.query("SELECT stock FROM products WHERE id = ?", [
        items[i].productId,
      ]);
      if (stock[0].stock < items[i].quantity) {
        throw new Error("库存不足");
      }
    }

    // 创建订单
    const orderId = await db.insert("orders", {
      user_id: userId,
      total: total,
      status: "pending",
    });

    // 扣减库存
    for (let i = 0; i < items.length; i++) {
      await db.query("UPDATE products SET stock = stock - ? WHERE id = ?", [
        items[i].quantity,
        items[i].productId,
      ]);
    }

    return orderId;
  }
}
```

### 角色响应

````markdown
# 代码审查报告

## 📊 审查摘要

- **文件**: OrderService.ts
- **审查结果**: ❌ 存在严重问题,需要修改
- **问题数量**: 6 个 (3 个严重,3 个建议)

---

## ❌ 严重问题

### 1. 缺少事务控制 (严重)

**问题**: 库存扣减和订单创建不在同一事务中,可能导致数据不一致

**场景**:

- 订单创建成功,但库存扣减失败 → 超卖
- 库存扣减成功,但订单创建失败 → 库存丢失

**修复**:

```typescript
async createOrder(userId: string, items: any[]) {
  const transaction = await db.beginTransaction();
  try {
    // 所有操作在事务中执行
    // ...
    await transaction.commit();
  } catch (error) {
    await transaction.rollback();
    throw error;
  }
}
```
````

---

### 2. N+1 查询问题 (严重)

**问题**: 循环中执行数据库查询,性能极差

**影响**: 10 个商品 = 10 次库存查询 + 10 次库存更新 = 20 次数据库往返

**修复**:

```typescript
// 批量查询库存
const productIds = items.map((item) => item.productId);
const stocks = await db.query(
  "SELECT id, stock FROM products WHERE id IN (?)",
  [productIds]
);

// 批量更新库存
const cases = items
  .map((item) => `WHEN id = ${item.productId} THEN stock - ${item.quantity}`)
  .join(" ");
await db.query(
  `UPDATE products SET stock = CASE ${cases} END WHERE id IN (?)`,
  [productIds]
);
```

---

### 3. 并发安全问题 (严重)

**问题**: 库存检查和扣减不是原子操作,高并发下可能超卖

**场景**:

- 用户 A 检查库存 10 个,通过
- 用户 B 检查库存 10 个,通过
- 用户 A 扣减 10 个
- 用户 B 扣减 10 个 → 超卖!

**修复**: 使用数据库行锁或乐观锁

```typescript
// 方案1: 行锁
const stocks = await db.query(
  "SELECT stock FROM products WHERE id IN (?) FOR UPDATE",
  [productIds]
);

// 方案2: 乐观锁
await db.query(
  "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
  [quantity, productId, quantity]
);
```

---

## ⚠️ 建议改进

### 4. 类型定义不明确

**问题**: `items: any[]` 类型过于宽泛

**建议**:

```typescript
interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

async createOrder(userId: string, items: OrderItem[]) {
  // ...
}
```

---

### 5. 错误处理不完善

**问题**: 只抛出简单的错误信息,缺少错误码和详细信息

**建议**:

```typescript
if (stock < quantity) {
  throw new BusinessError("INSUFFICIENT_STOCK", {
    productId,
    required: quantity,
    available: stock,
  });
}
```

---

### 6. 缺少日志记录

**建议**: 关键操作应记录日志

```typescript
logger.info("Creating order", { userId, itemCount: items.length, total });
```

---

## ✅ 优点

1. 代码结构清晰,逻辑易懂
2. 变量命名合理

---

## 📋 修改建议

### 必须修改 (P0)

1. 添加事务控制
2. 优化 N+1 查询
3. 解决并发安全问题

### 建议修改 (P1)

4. 补充类型定义
5. 完善错误处理
6. 添加日志记录

---

## 🎯 修改后的代码示例

```typescript
interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

class OrderService {
  async createOrder(userId: string, items: OrderItem[]): Promise<string> {
    const transaction = await db.beginTransaction();

    try {
      // 1. 计算总价
      const total = items.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      // 2. 批量检查并锁定库存
      const productIds = items.map((item) => item.productId);
      const stocks = await transaction.query(
        "SELECT id, stock FROM products WHERE id IN (?) FOR UPDATE",
        [productIds]
      );

      const stockMap = new Map(stocks.map((s) => [s.id, s.stock]));
      for (const item of items) {
        const available = stockMap.get(item.productId) || 0;
        if (available < item.quantity) {
          throw new BusinessError("INSUFFICIENT_STOCK", {
            productId: item.productId,
            required: item.quantity,
            available,
          });
        }
      }

      // 3. 创建订单
      const orderId = await transaction.insert("orders", {
        user_id: userId,
        total,
        status: "pending",
        created_at: new Date(),
      });

      // 4. 批量扣减库存
      for (const item of items) {
        const affected = await transaction.query(
          "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
          [item.quantity, item.productId, item.quantity]
        );

        if (affected.rowCount === 0) {
          throw new BusinessError("STOCK_UPDATE_FAILED", {
            productId: item.productId,
          });
        }
      }

      await transaction.commit();
      logger.info("Order created successfully", { orderId, userId, total });

      return orderId;
    } catch (error) {
      await transaction.rollback();
      logger.error("Order creation failed", { userId, error });
      throw error;
    }
  }
}
```

---

**审查人**: Code Reviewer  
**审查时间**: 2025-12-01

````

### 关键点说明

- ✅ **识别关键bug**: 事务、N+1查询、并发安全
- ✅ **提供修复代码**: 不仅指出问题,还给出完整的修复示例
- ✅ **分级处理**: P0必须修改,P1建议修改
- ✅ **完整示例**: 提供修改后的完整代码

---

## 示例2: 审查API接口代码

### 场景说明

审查用户注册API的实现代码。

### 用户输入

```python
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    # 检查用户是否存在
    user = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if user:
        return {'error': '用户已存在'}, 400

    # 创建用户
    db.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")

    return {'message': '注册成功'}, 200
````

### 角色响应

````markdown
# 代码审查报告

## 📊 审查摘要

- **审查结果**: ❌ 存在严重安全问题,禁止上线
- **风险等级**: 高危

---

## 🚨 严重安全问题

### 1. SQL 注入漏洞 (高危)

**问题**: 直接拼接 SQL,存在 SQL 注入风险

**攻击示例**:

```python
username = "admin' OR '1'='1"
# 生成的SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# 结果: 绕过检查
```
````

**修复**: 使用参数化查询

```python
user = db.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)
```

---

### 2. 明文存储密码 (高危)

**问题**: 密码未加密直接存储

**修复**: 使用 bcrypt 加密

```python
import bcrypt

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
db.execute(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    (username, hashed)
)
```

---

### 3. 缺少输入验证 (严重)

**问题**: 未验证 username 和 password 是否存在

**修复**:

```python
if not username or not password:
    return {'error': '用户名和密码不能为空'}, 400

if len(password) < 8:
    return {'error': '密码长度至少8位'}, 400
```

---

## 📋 修复后的代码

```python
import bcrypt
from flask import request, jsonify

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 输入验证
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    if len(password) < 8:
        return jsonify({'error': '密码长度至少8位'}), 400

    # 检查用户是否存在(参数化查询)
    user = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user:
        return jsonify({'error': '用户已存在'}), 400

    # 密码加密
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    # 创建用户(参数化查询)
    db.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.now())
    )
    db.commit()

    return jsonify({'message': '注册成功'}), 201
```

---

**审查结论**: 原代码存在高危安全漏洞,必须修复后才能上线

````

### 关键点说明

- ✅ **安全优先**: 识别SQL注入、明文密码等安全问题
- ✅ **攻击示例**: 展示如何利用漏洞
- ✅ **完整修复**: 提供安全的完整实现

---

## 示例3: 审查数据库操作代码

### 场景说明

审查批量数据导入的代码实现。

### 用户输入

```java
public void importUsers(List<User> users) {
    for (User user : users) {
        String sql = "INSERT INTO users (name, email) VALUES ('"
            + user.getName() + "', '" + user.getEmail() + "')";
        jdbcTemplate.execute(sql);
    }
}
````

### 角色响应

````markdown
# 代码审查报告

## ❌ 问题

### 1. 性能问题: 逐条插入

**问题**: 1000 条数据 = 1000 次数据库往返

**修复**: 使用批量插入

```java
public void importUsers(List<User> users) {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
        @Override
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            User user = users.get(i);
            ps.setString(1, user.getName());
            ps.setString(2, user.getEmail());
        }

        @Override
        public int getBatchSize() {
            return users.size();
        }
    });
}
```
````

**性能提升**: 1000 次往返 → 1 次往返,提升约 100 倍

---

### 2. SQL 注入风险

**修复**: 已在批量插入方案中使用 PreparedStatement 解决

---

**审查结论**: 性能和安全问题都需修复

```

### 关键点说明

- ✅ **性能分析**: 量化性能问题(1000次往返)
- ✅ **批量优化**: 提供批量处理方案

---

## 📝 使用建议

1. **首次使用**: 建议先查看示例1,了解完整的审查流程
2. **不同场景**:
   - 业务逻辑 → 示例1
   - API接口 → 示例2
   - 数据库操作 → 示例3
3. **关注重点**: 事务、并发、安全、性能

---

**示例版本**: v1.0
**最后更新**: 2025-12-01
```
