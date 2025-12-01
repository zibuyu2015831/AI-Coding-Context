# 架构分析师角色使用示例

**角色**: 架构分析师 (Architecture Analyst)  
**文档**: [architecture_analyst.md](../development/architecture_analyst.md)

---

## 📋 目录

- [示例 1: 设计用户积分系统](#示例1-设计用户积分系统)
- [示例 2: 设计秒杀系统](#示例2-设计秒杀系统)

---

## 示例 1: 设计用户积分系统

### 场景说明

产品经理提出需求:实现用户积分获取、消耗、过期功能,预计用户量 1000 万。需要架构分析师设计技术方案。

### 用户输入

```markdown
# 需求

- 用户完成任务获得积分
- 用户消费积分兑换商品
- 积分有效期 1 年,过期自动清零
- 预计用户量 1000 万,日活 100 万
```

### 角色响应

````markdown
# 用户积分系统技术方案

## 1. 需求分析

### 核心功能

1. 积分获取(任务完成、活动奖励)
2. 积分消耗(兑换商品)
3. 积分过期(1 年有效期)
4. 积分查询(余额、历史)

### 非功能需求

- **用户规模**: 1000 万用户
- **并发**: 日活 100 万,峰值 QPS 预估 5000
- **一致性**: 积分扣减需强一致性
- **可用性**: 99.9%

---

## 2. 领域模型设计

### 核心实体

**UserPoints (聚合根)**

- 用户总积分
- 管理积分变动

**PointRecord (实体)**

- 积分流水记录
- 追溯每笔积分来源和去向

**PointRule (值对象)**

- 积分规则(获取/消耗规则)

### 类图

```
UserPoints (聚合根)
├── userId: Long
├── totalPoints: BigDecimal
├── version: Int (乐观锁)
└── updatedAt: Timestamp

PointRecord (实体)
├── id: Long
├── userId: Long
├── amount: BigDecimal
├── type: Enum(EARN, DEDUCT, EXPIRE)
├── expireAt: Timestamp
├── reason: String
└── createdAt: Timestamp
```

---

## 3. 数据库设计

### 表结构

```sql
-- 用户积分表
CREATE TABLE user_points (
    user_id BIGINT PRIMARY KEY,
    total_points DECIMAL(10, 2) NOT NULL DEFAULT 0,
    version INT NOT NULL DEFAULT 0,  -- 乐观锁
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB;

-- 积分流水表
CREATE TABLE point_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type ENUM('EARN', 'DEDUCT', 'EXPIRE') NOT NULL,
    expire_at TIMESTAMP NULL,  -- 获取积分时记录过期时间
    reason VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_expire (user_id, expire_at),
    INDEX idx_user_created (user_id, created_at DESC)
) ENGINE=InnoDB;
```

### 索引策略

1. `idx_user_expire`: 支持过期积分查询
2. `idx_user_created`: 支持积分历史查询(分页)

---

## 4. 核心接口设计

### 4.1 积分获取接口

```typescript
POST /api/points/earn

Request:
{
  "userId": "123",
  "amount": 100,
  "reason": "完成每日任务",
  "expireAt": "2025-12-01T00:00:00Z"
}

Response:
{
  "success": true,
  "newBalance": 1100
}
```

### 4.2 积分扣减接口

```typescript
POST /api/points/deduct

Request:
{
  "userId": "123",
  "amount": 50,
  "reason": "兑换商品"
}

Response:
{
  "success": true,
  "newBalance": 1050
}
```

### 4.3 积分查询接口

```typescript
GET /api/points/balance?userId=123

Response:
{
  "userId": "123",
  "totalPoints": 1050,
  "availablePoints": 1000,  // 扣除即将过期的积分
  "expiringSoon": 50  // 30天内过期
}
```

---

## 5. 并发控制方案

### 问题

高并发场景下,多个请求同时扣减积分可能导致超扣。

### 方案: 乐观锁

```sql
-- 扣减积分时使用version字段
UPDATE user_points
SET total_points = total_points - ?,
    version = version + 1,
    updated_at = NOW()
WHERE user_id = ?
  AND version = ?
  AND total_points >= ?;  -- 防止扣成负数

-- 检查affected rows
-- 如果为0,说明version不匹配或余额不足,需要重试或返回错误
```

**优势**:

- 无需分布式锁
- 性能好,适合高并发
- 数据库原生支持

---

## 6. 积分过期方案

### 方案 A: 定时任务扫描(推荐)

**实现**:

```sql
-- 每天凌晨执行
SELECT user_id, SUM(amount) as expired_amount
FROM point_records
WHERE type = 'EARN'
  AND expire_at < NOW()
  AND expire_at IS NOT NULL
GROUP BY user_id;

-- 批量扣减过期积分
-- 插入EXPIRE类型的流水记录
```

**优势**: 简单可靠,对实时性要求不高

---

### 方案 B: 实时计算(备选)

**实现**: 查询/扣减时实时计算可用积分

```sql
SELECT SUM(amount) as available
FROM point_records
WHERE user_id = ?
  AND (expire_at IS NULL OR expire_at > NOW());
```

**优势**: 实时准确  
**劣势**: 查询性能差

---

## 7. 缓存策略

### 缓存内容

```
Key: user_points:{userId}
Value: {
  "totalPoints": 1050,
  "version": 10,
  "updatedAt": "2025-12-01T10:00:00Z"
}
TTL: 1小时
```

### 缓存更新策略

- 积分变动时: 删除缓存(Cache Aside)
- 查询时: 缓存未命中则从 DB 加载

---

## 8. 性能优化

### 8.1 读写分离

- 写操作: 主库
- 查询操作: 从库

### 8.2 分库分表(未来扩展)

当单表数据量超过 1 亿时,按 user_id 分表:

```
point_records_0
point_records_1
...
point_records_99
```

---

## 9. 风险评估

| 风险       | 影响 | 应对措施          |
| ---------- | ---- | ----------------- |
| 并发超扣   | 高   | 乐观锁 + 余额检查 |
| 数据不一致 | 高   | 事务保证          |
| 性能瓶颈   | 中   | 缓存 + 读写分离   |
| 积分丢失   | 高   | 流水表完整记录    |

---

## 10. 实施计划

### Phase 1: MVP (2 周)

- 基础表结构
- 积分获取/扣减/查询接口
- 乐观锁并发控制

### Phase 2: 完善 (1 周)

- 积分过期定时任务
- 缓存层
- 监控告警

### Phase 3: 优化 (按需)

- 读写分离
- 分库分表

---

**方案版本**: v1.0  
**设计者**: Architecture Analyst  
**设计时间**: 2025-12-01
````

### 关键点说明

- ✅ **完整的技术方案**: 从需求分析到实施计划
- ✅ **领域模型**: DDD 思想,聚合根+实体+值对象
- ✅ **数据库设计**: 完整的 DDL 和索引策略
- ✅ **并发方案**: 乐观锁解决并发问题
- ✅ **风险评估**: 识别风险并给出应对措施

---

## 示例 2: 设计秒杀系统

### 场景说明

电商平台需要设计秒杀功能,预计峰值 QPS 10 万。

### 用户输入

```markdown
# 需求

- 商品限量 1000 件
- 10 万用户同时抢购
- 防止超卖
- 防止黄牛刷单
```

### 角色响应

````markdown
# 秒杀系统技术方案

## 1. 核心挑战

- **高并发**: 10 万 QPS
- **库存准确**: 绝对不能超卖
- **防刷**: 防止黄牛和脚本

---

## 2. 架构设计

### 分层架构

```
用户 → CDN → 接入层(限流) → 业务层(Redis库存) → 数据库(订单)
```

### 核心流程

1. **前端限流**: 按钮置灰,防止重复点击
2. **接入层限流**: Nginx 限流,QPS 超过阈值直接返回
3. **Redis 扣库存**: 原子操作,防止超卖
4. **异步创建订单**: 消息队列削峰

---

## 3. 库存扣减方案

### Redis 原子扣减

```lua
-- Lua脚本保证原子性
local stock = redis.call('GET', KEYS[1])
if tonumber(stock) > 0 then
    redis.call('DECR', KEYS[1])
    return 1
else
    return 0
end
```

**优势**:

- 性能极高(10 万 QPS)
- 原子操作,不会超卖

---

## 4. 防刷方案

### 4.1 验证码

秒杀前弹出验证码,防止脚本

### 4.2 限流

- 用户维度: 每个用户 10 秒内只能请求 1 次
- IP 维度: 每个 IP 1 秒内最多 10 次

### 4.3 风控

- 检测异常行为(同一 IP 大量请求)
- 黑名单机制

---

## 5. 数据一致性

### 问题

Redis 扣减成功,但订单创建失败 → 库存丢失

### 方案: 补偿机制

```
1. Redis扣减成功 → 发送MQ消息
2. 消费者创建订单
3. 如果失败,回滚Redis库存
```

---

**方案版本**: v1.0
````

### 关键点说明

- ✅ **高并发方案**: Redis + Lua 脚本
- ✅ **分层设计**: CDN + 限流 + 异步
- ✅ **防刷策略**: 验证码 + 限流 + 风控

---

## 📝 使用建议

1. **首次使用**: 建议先查看示例 1,了解完整的方案结构
2. **不同场景**:
   - 常规业务系统 → 示例 1
   - 高并发场景 → 示例 2
3. **关注重点**: 领域模型、数据库设计、并发控制、风险评估

---

**示例版本**: v1.0  
**最后更新**: 2025-12-01
