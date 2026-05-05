---
title: 性能优化专家角色使用示例
summary: 展示性能优化专家角色在慢查询和高并发接口场景中的分析与优化建议输出，帮助用户理解其瓶颈定位方式。
keywords: example | performance-optimizer | performance | query | concurrency | aicc
scope: 性能优化专家角色示例
related_files: 无
dependencies: agents/runtime/performance_optimizer.md | agents/examples/README.md
verified_at: 2026-05-05
---

# 性能优化专家角色使用示例

**角色**: 性能优化专家 (Performance Optimizer)  
**文档**: [performance_optimizer.md](../runtime/performance_optimizer.md)

---

## 📋 目录

- [示例 1: 优化慢查询](#示例1-优化慢查询)
- [示例 2: 优化高并发接口](#示例2-优化高并发接口)

---

## 示例 1: 优化慢查询

### 场景说明

订单列表查询接口响应慢,需要分析并优化。

### 用户输入

```markdown
# 问题

订单列表接口响应时间 2-3 秒

# 慢查询 SQL

SELECT \* FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 20

# 数据量

orders 表有 500 万条数据
```

### 角色响应

````markdown
# 性能优化方案

## 1. 瓶颈分析

### 问题定位

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 20;
```

**分析结果**:

- type: ALL (全表扫描)
- rows: 5000000 (扫描 500 万行)
- Extra: Using filesort (文件排序)

**根本原因**: 缺少索引,导致全表扫描+文件排序

---

## 2. 优化方案

### 方案 A: 添加复合索引 (推荐)

```sql
CREATE INDEX idx_user_created ON orders(user_id, created_at DESC);
```

**优化效果**:

- 查询复杂度: O(N) → O(logN)
- 预计响应时间: 2-3 秒 → 50ms 以内

**验证**:

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 20;
-- type: ref
-- rows: 20
-- Extra: Using index
```

---

### 方案 B: 分页优化 (补充)

如果用户翻页很深,使用游标分页:

```sql
-- 传统分页(慢)
SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10000, 20;

-- 游标分页(快)
SELECT * FROM orders
WHERE user_id = 123 AND created_at < '2025-12-01 10:00:00'
ORDER BY created_at DESC
LIMIT 20;
```

---

## 3. 实施步骤

1. 在测试环境创建索引
2. 验证查询性能
3. 在生产环境创建索引(在线 DDL)

---

## 4. 监控指标

- 响应时间: 目标<100ms
- QPS: 目标>1000
- CPU 使用率: 目标<50%
````

### 关键点说明

- ✅ **数据驱动**: 使用 EXPLAIN 分析
- ✅ **量化效果**: 明确优化前后对比
- ✅ **实施步骤**: 可执行的优化步骤

---

## 示例 2: 优化高并发接口

### 场景说明

商品详情接口在高并发下响应慢。

### 用户输入

```markdown
# 问题

商品详情接口,QPS 5000 时响应时间 1 秒

# 当前实现

每次请求都查询数据库
```

### 角色响应

````markdown
# 高并发优化方案

## 1. 瓶颈分析

**问题**: 数据库成为瓶颈

- QPS 5000 → 数据库连接池耗尽
- 大量重复查询相同数据

---

## 2. 优化方案

### 方案: Redis 缓存

```python
def get_product_detail(product_id):
    # 1. 先查缓存
    cache_key = f"product:{product_id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. 缓存未命中,查数据库
    product = db.query("SELECT * FROM products WHERE id = ?", [product_id])

    # 3. 写入缓存
    redis.setex(cache_key, 3600, json.dumps(product))  # TTL 1小时

    return product
```

**优化效果**:

- 缓存命中率: 预计 95%
- 响应时间: 1 秒 → 10ms (缓存命中时)
- 数据库 QPS: 5000 → 250 (降低 95%)

---

## 3. 缓存更新策略

### 商品信息更新时

```python
def update_product(product_id, data):
    # 1. 更新数据库
    db.update("products", data, {"id": product_id})

    # 2. 删除缓存(Cache Aside模式)
    redis.delete(f"product:{product_id}")
```

---

## 4. 风险控制

### 缓存穿透

```python
# 空值也缓存,防止缓存穿透
if not product:
    redis.setex(cache_key, 60, "null")  # 短TTL
```

### 缓存雪崩

```python
# 随机TTL,防止同时过期
import random
ttl = 3600 + random.randint(0, 600)  # 3600-4200秒
redis.setex(cache_key, ttl, data)
```
````

### 关键点说明

- ✅ **缓存策略**: Cache Aside 模式
- ✅ **风险控制**: 缓存穿透、雪崩
- ✅ **量化收益**: 95%性能提升

---

## 📝 使用建议

1. **数据库优化** → 示例 1
2. **缓存优化** → 示例 2

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
