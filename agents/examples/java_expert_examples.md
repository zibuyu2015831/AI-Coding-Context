# Java 专家 (Java Expert) 角色使用示例

**角色**: Java 专家
**文档**: [java_expert.md](../language_specific/java/java_expert.md)

---

## 📋 目录

- [示例 1: 使用 Java 17 Record 和 Stream API](#示例1)
- [示例 2: 高并发环境下的线程安全缓存](#示例2)
- [示例 3: Spring Boot 异步任务处理](#示例3)

---

## <a id="示例1"></a>示例 1: 使用 Java 17 Record 和 Stream API

### 场景说明

定义一个不可变的数据传输对象 (DTO)，并对数据集合进行复杂的过滤和转换操作，展示 Modern Java 的简洁性。

### 用户输入

```text
定义一个 Transaction 类，包含 id, amount, type, date。
写一个方法，筛选出最近一周 amount > 1000 的交易，按金额降序排列，并提取出 id 列表。
请使用 Java 17+ 特性。
```

### 角色响应

```java
import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;

// 1. 使用 Record 定义不可变 DTO (Java 14+)
public record Transaction(String id, double amount, String type, LocalDate date) {
    // Compact Constructor 进行数据校验
    public Transaction {
        if (amount < 0) throw new IllegalArgumentException("Amount cannot be negative");
    }
}

public class TransactionService {

    /**
     * 筛选高额近期交易
     */
    public List<String> findLargeRecentTransactions(List<Transaction> transactions) {
        LocalDate oneWeekAgo = LocalDate.now().minusWeeks(1);

        return transactions.stream()
            // 2. Stream API 过滤
            .filter(t -> t.amount() > 1000)
            .filter(t -> t.date().isAfter(oneWeekAgo))
            // 3. 排序 (Comparator)
            .sorted(Comparator.comparingDouble(Transaction::amount).reversed())
            // 4. 映射
            .map(Transaction::id)
            // 5. 收集结果 (Java 16+ 直接 toList)
            .toList();
    }
}
```

### 关键点说明

- ✅ **Record**: 使用 `record` 减少样板代码 (getter, equals, hashCode, toString)。
- ✅ **Compact Constructor**: 在 record 构造器中进行简洁的校验。
- ✅ **Stream API**: 链式调用，声明式处理数据集合。
- ✅ **toList()**: 直接使用 Java 16 引入的 `Stream.toList()` 替代 `collect(Collectors.toList())`。

---

## <a id="示例2"></a>示例 2: 高并发环境下的线程安全缓存

### 场景说明

在不使用 Redis 的情况下，实现一个简单的进程内缓存，要求高并发下的读写安全，并具备过期清理功能。

### 用户输入

```text
写一个线程安全的本地缓存 Cache<K, V>，支持 put, get 和过期时间。
```

### 角色响应

```java
import java.util.Map;
import java.util.concurrent.*;

public class SimpleLocalCache<K, V> {
    // 使用 ConcurrentHashMap 保证基础的线程安全
    private final Map<K, V> store = new ConcurrentHashMap<>();
    private final Map<K, Long> expiryMap = new ConcurrentHashMap<>();
    // 定时清理任务
    private final ScheduledExecutorService cleanUpExecutor = Executors.newSingleThreadScheduledExecutor();

    public SimpleLocalCache() {
        // 每分钟清理一次过期数据
        cleanUpExecutor.scheduleAtFixedRate(this::removeExpired, 1, 1, TimeUnit.MINUTES);
    }

    public void put(K key, V value, long ttlMillis) {
        store.put(key, value);
        expiryMap.put(key, System.currentTimeMillis() + ttlMillis);
    }

    public V get(K key) {
        Long expireTime = expiryMap.get(key);
        if (expireTime == null) {
            return null; // 或者返回 store.get(key) 取决于是否允许永不过期
        }

        if (System.currentTimeMillis() > expireTime) {
            store.remove(key);
            expiryMap.remove(key);
            return null;
        }
        return store.get(key);
    }

    private void removeExpired() {
        long now = System.currentTimeMillis();
        expiryMap.forEach((key, time) -> {
            if (now > time) {
                store.remove(key);
                expiryMap.remove(key);
            }
        });
    }
}
```

### 关键点说明

- ✅ **ConcurrentHashMap**: 保证 map 操作的原子性和可见性。
- ✅ **ScheduledExecutorService**: 专门的线程处理过期清理，避免阻塞主业务。
- ✅ **线程安全**: 解释了为什么需要线程安全的集合类。

---

## <a id="示例3"></a>示例 3: Spring Boot 异步任务处理

### 场景说明

配置 Spring Boot 使用自定义线程池执行异步任务，并处理异常。

### 用户输入

```text
Spring Boot 中如何配置 @Async 使用自定义的线程池？还需要捕获异步方法抛出的异常。
```

### 角色响应

```java
@Configuration
@EnableAsync // 1.以此开启异步支持
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        // 2. 自定义线程池
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10); // 核心线程数
        executor.setMaxPoolSize(50);  // 最大线程数
        executor.setQueueCapacity(100); // 队列容量
        executor.setThreadNamePrefix("MyAsync-");
        executor.initialize();
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        // 3. 自定义异常处理
        return (ex, method, params) -> {
            System.err.println("Exception in async method: " + method.getName());
            System.err.println("Error: " + ex.getMessage());
        };
    }
}

// 使用示例
@Service
public class NotificationService {

    @Async
    public void sendEmail(String email) {
        // 模拟耗时操作
        if (email == null) throw new IllegalArgumentException("Email is null");
        System.out.println("Sending email in " + Thread.currentThread().getName());
    }
}
```

### 关键点说明

- ✅ **ThreadPoolTaskExecutor**: 不使用默认的 SimpleAsyncTaskExecutor (因为不复用线程)，而是配置生产级线程池。
- ✅ **AsyncUncaughtExceptionHandler**: 异步方法的异常无法在调用处捕获，必须通过此 Handler 处理。

---

## 📝 使用建议

1.  **JDK 版本**: 默认依然广泛使用 Java 8，但在新项目中强烈建议从 **示例 1** 学习 Java 17/21 新特性。
2.  **并发编程**: 涉及多线程时，优先参考 **示例 2** 和 **示例 3**，避免手动创建 Thread。
