---
title: 数据库设计师角色使用示例
summary: 展示数据库设计师角色在订单系统与权限系统场景中的建模和表设计方式，帮助用户理解其数据层设计思路。
keywords: example | database-designer | schema | sql | modeling | aicc
scope: 数据库设计师角色示例
related_files: 无
dependencies: agents/development/database_designer.md | agents/examples/README.md
verified_at: 2026-05-05
---

# 数据库设计师角色使用示例

**角色**: 数据库设计师 (Database Designer)  
**文档**: [database_designer.md](../development/database_designer.md)

---

## 📋 目录

- [示例 1: 设计电商订单表](#示例1-设计电商订单表)
- [示例 2: 设计用户权限系统](#示例2-设计用户权限系统)

---

## 示例 1: 设计电商订单表

### 场景说明

为电商系统设计订单相关的数据库表结构。

### 用户输入

```markdown
# 需求

- 用户下单购买商品
- 订单包含多个商品
- 订单有状态(待支付、已支付、已发货、已完成)
- 需要记录订单历史
```

### 角色响应

````markdown
# 订单系统数据库设计

## 1. ER 图

```
User 1---N Order N---N Product
Order 1---N OrderItem
Order 1---N OrderHistory
```

---

## 2. 表结构设计

### 订单主表 (orders)

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL COMMENT '订单号',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    status ENUM('PENDING', 'PAID', 'SHIPPED', 'COMPLETED', 'CANCELLED')
        NOT NULL DEFAULT 'PENDING' COMMENT '订单状态',
    payment_method VARCHAR(20) COMMENT '支付方式',
    shipping_address TEXT COMMENT '收货地址',
    remark VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL COMMENT '支付时间',
    shipped_at TIMESTAMP NULL COMMENT '发货时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',

    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_order_no (order_no),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```

---

### 订单明细表 (order_items)

```sql
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL COMMENT '订单ID',
    product_id BIGINT NOT NULL COMMENT '商品ID',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称(冗余)',
    product_price DECIMAL(10, 2) NOT NULL COMMENT '商品单价(冗余)',
    quantity INT NOT NULL COMMENT '购买数量',
    subtotal DECIMAL(10, 2) NOT NULL COMMENT '小计',

    INDEX idx_order (order_id),
    INDEX idx_product (product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';
```

---

### 订单历史表 (order_history)

```sql
CREATE TABLE order_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL COMMENT '订单ID',
    old_status VARCHAR(20) COMMENT '原状态',
    new_status VARCHAR(20) NOT NULL COMMENT '新状态',
    operator VARCHAR(50) COMMENT '操作人',
    remark VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_order (order_id),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单历史表';
```

---

## 3. 索引策略

### 核心查询场景

1. **用户查询自己的订单**:

   ```sql
   SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 20;
   ```

   索引: `idx_user_created (user_id, created_at DESC)`

2. **按订单号查询**:

   ```sql
   SELECT * FROM orders WHERE order_no = ?;
   ```

   索引: `idx_order_no (order_no)` (UNIQUE)

3. **按状态查询(管理后台)**:
   ```sql
   SELECT * FROM orders WHERE status = 'PENDING' ORDER BY created_at DESC;
   ```
   索引: `idx_status (status)`

---

## 4. 设计说明

### 4.1 冗余字段

在`order_items`表中冗余`product_name`和`product_price`:

- **原因**: 商品信息可能变化,订单需要记录下单时的信息
- **权衡**: 空间换一致性

### 4.2 订单号设计

```python
# 订单号生成规则: 时间戳 + 用户ID后4位 + 随机数
import time
import random

def generate_order_no(user_id):
    timestamp = int(time.time())
    user_suffix = str(user_id)[-4:].zfill(4)
    random_suffix = random.randint(1000, 9999)
    return f"{timestamp}{user_suffix}{random_suffix}"
```

### 4.3 状态流转

```
PENDING → PAID → SHIPPED → COMPLETED
   ↓
CANCELLED (任何状态都可取消)
```

---

## 5. 性能优化

### 5.1 分表策略(未来扩展)

当订单量超过 1000 万时,按月分表:

```
orders_202501
orders_202502
...
```

### 5.2 归档策略

6 个月前的订单归档到历史表:

```sql
CREATE TABLE orders_archive LIKE orders;
```
````

### 关键点说明

- ✅ **完整的 DDL**: 包含字段、索引、注释
- ✅ **索引策略**: 基于查询场景设计
- ✅ **设计说明**: 解释冗余字段等设计决策

---

## 示例 2: 设计用户权限系统

### 场景说明

设计 RBAC(基于角色的访问控制)权限系统。

### 用户输入

```markdown
# 需求

- 用户有多个角色
- 角色有多个权限
- 支持权限继承
```

### 角色响应

````markdown
# RBAC 权限系统设计

## 表结构

### 用户表 (users)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

### 角色表 (roles)

```sql
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    parent_id BIGINT NULL COMMENT '父角色ID,支持继承',
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB;
```

### 权限表 (permissions)

```sql
CREATE TABLE permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(100) UNIQUE NOT NULL COMMENT '权限编码',
    name VARCHAR(100) NOT NULL,
    resource VARCHAR(100) COMMENT '资源',
    action VARCHAR(50) COMMENT '操作'
) ENGINE=InnoDB;
```

### 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    INDEX idx_role (role_id)
) ENGINE=InnoDB;
```

### 角色权限关联表 (role_permissions)

```sql
CREATE TABLE role_permissions (
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    INDEX idx_permission (permission_id)
) ENGINE=InnoDB;
```

---

## 权限检查查询

```sql
-- 查询用户的所有权限(包含继承)
WITH RECURSIVE role_tree AS (
    -- 用户直接拥有的角色
    SELECT r.id, r.parent_id
    FROM roles r
    JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = ?

    UNION ALL

    -- 递归查询父角色
    SELECT r.id, r.parent_id
    FROM roles r
    JOIN role_tree rt ON r.id = rt.parent_id
)
SELECT DISTINCT p.*
FROM permissions p
JOIN role_permissions rp ON p.id = rp.permission_id
JOIN role_tree rt ON rp.role_id = rt.id;
```
````

### 关键点说明

- ✅ **RBAC 模型**: 用户-角色-权限
- ✅ **权限继承**: 支持角色层级
- ✅ **递归查询**: CTE 实现权限继承

---

## 📝 使用建议

1. **业务表设计** → 示例 1
2. **权限系统** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
