---
title: 后端工程师角色使用示例
summary: 展示基础后端工程师角色在接口设计、事务处理与查询优化场景中的典型输出，用于帮助用户理解其实现导向的工作方式。
keywords: example | backend-engineer | api | transaction | optimization | aicc
scope: 后端工程师角色示例
related_files: 无
dependencies: agents/language_specific/base/backend_engineer.md | agents/examples/README.md
verified_at: 2026-05-05
---

# 后端工程师 (Backend Engineer) 角色使用示例

**角色**: 后端工程师 (基础)
**文档**: [backend_engineer.md](../language_specific/base/backend_engineer.md)

---

## 📋 目录

- [示例 1: RESTful API 接口设计](#示例1)
- [示例 2: 复杂业务逻辑与事务处理](#示例2)
- [示例 3: 数据库查询优化](#示例3)

---

## <a id="示例1"></a>示例 1: RESTful API 接口设计

### 场景说明

设计一个用户注册功能的 API 接口，要求符合 RESTful 规范，包含输入校验和错误处理。

### 用户输入

```text
请设计一个用户注册接口：
1. 路径: /api/users/register
2. 字段: username, email, password
3. 要求: 校验邮箱格式，密码长度至少8位，返回标准 HTTP 状态码。
```

### 角色响应

```java
// Controller 层接口定义
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 用户注册接口
     * POST /api/users/register
     */
    @PostMapping("/register")
    public ResponseEntity<UserDto> register(@Valid @RequestBody UserRegisterRequest request) {
        // 调用 Service 层处理业务
        UserDto createdUser = userService.registerUser(request);

        // 返回 201 Created 状态码
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }
}

// DTO 定义与校验
public class UserRegisterRequest {

    @NotBlank(message = "用户名不能为空")
    private String username;

    @Email(message = "邮箱格式不正确")
    @NotBlank(message = "邮箱不能为空")
    private String email;

    @Size(min = 8, message = "密码长度至少为8位")
    @NotBlank(message = "密码不能为空")
    private String password;

    // Getters and Setters...
}
```

### 关键点说明

- ✅ **RESTful 规范**: 使用 POST 方法，成功创建返回 201 状态码。
- ✅ **输入校验**: 使用 `@Valid` 和 Bean Validation 注解进行参数校验。
- ✅ **职责分离**: Controller 只负责接收请求和返回响应，业务逻辑交给 Service。

---

## <a id="示例2"></a>示例 2: 复杂业务逻辑与事务处理

### 场景说明

实现一个“创建订单”的业务逻辑，涉及扣减库存、保存订单、发送通知等操作，需要保证数据一致性。

### 用户输入

```text
实现 createOrder 方法：
1. 检查库存是否充足
2. 扣减库存
3. 保存订单记录
4. 如果任何一步失败，回滚所有操作
```

### 角色响应

```java
@Service
public class OrderService {

    @Autowired
    private ProductRepository productRepository;
    @Autowired
    private OrderRepository orderRepository;

    /**
     * 创建订单 - 事务方法
     */
    @Transactional(rollbackFor = Exception.class) // 开启事务
    public OrderDto createOrder(CreateOrderCommand cmd) {
        // 1. 检查并锁定库存 (使用悲观锁或乐观锁)
        Product product = productRepository.findByIdForUpdate(cmd.getProductId())
            .orElseThrow(() -> new NotFoundException("商品不存在"));

        if (product.getStock() < cmd.getQuantity()) {
            throw new BusinessException("库存不足");
        }

        // 2. 扣减库存
        product.setStock(product.getStock() - cmd.getQuantity());
        productRepository.save(product);

        // 3. 创建并保存订单
        Order order = new Order();
        order.setProductId(cmd.getProductId());
        order.setUserId(cmd.getUserId());
        order.setStatus(OrderStatus.CREATED);
        order.setAmount(product.getPrice().multiply(BigDecimal.valueOf(cmd.getQuantity())));
        Order savedOrder = orderRepository.save(order);

        // 4. 发送通知 (通常这步可以异步，不放在主事务中，视业务要求而定)
        // notificationService.send(savedOrder);

        return convertToDto(savedOrder);
    }
}
```

### 关键点说明

- ✅ **事务管理**: 使用 `@Transactional` 确保原子性，异常时自动回滚。
- ✅ **并发控制**: 提示使用 `findByIdForUpdate` (悲观锁) 防止超卖。
- ✅ **异常处理**: 定义明确的业务异常 `BusinessException`。

---

## <a id="示例3"></a>示例 3: 数据库查询优化

### 场景说明

优化一个慢查询：查询最近登录的活跃用户及其最新一条订单信息，解决 N+1 问题。

### 用户输入

```text
优化这段代码，现在每次循环都去查数据库，性能很差：
users = userRepository.findActiveUsers();
for (User user : users) {
    user.setLatestOrder(orderRepository.findLatestByUserId(user.getId()));
}
```

### 角色响应

```java
// 优化方案：使用 JOIN Fetch 或 批量查询

// 方案 A: JPA/Hibernate Join Fetch (适合关联关系明确)
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.orders o WHERE u.lastLogin > :date")
    List<User> findActiveUsersWithOrders(@Param("date") LocalDateTime date);
}

// 方案 B: 批量查询 (应用层组装，适合微服务或简单SQL)
public List<UserDto> getActiveUsersWithLatestOrder() {
    // 1. 一次性查出所有用户
    List<User> users = userRepository.findActiveUsers();
    List<Long> userIds = users.stream().map(User::getId).toList();

    // 2. 一次性查出这些用户的最新订单 (使用 IN 查询)
    List<Order> latestOrders = orderRepository.findLatestOrdersByUserIds(userIds);

    // 3. 内存中组装
    Map<Long, Order> orderMap = latestOrders.stream()
        .collect(Collectors.toMap(Order::getUserId, Function.identity()));

    users.forEach(user -> {
        user.setLatestOrder(orderMap.get(user.getId()));
    });

    return convertToDtos(users);
}
```

### 关键点说明

- ✅ **识别 N+1**: 指出循环查库的问题根源。
- ✅ **方案对比**: 提供了 DB 层 (Join) 和 应用层 (Batch Query) 两种解法。
- ✅ **性能收益**: 将 N+1 次查询降低为 2 次查询。

---

## 📝 使用建议

1.  **首次使用**: 先参考示例 1 了解标准的 Layered Architecture (Controller-Service-Repository) 写法。
2.  **安全性**: 在设计接口时，始终参考示例 1 中的输入校验部分。
3.  **复杂场景**: 遇到并发或数据一致性问题时，参考示例 2。
