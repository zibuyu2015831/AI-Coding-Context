---
title: 微服务架构项目配置
summary: 定义微服务架构项目的推荐子文档清单、特殊关注点和核心代码模式。包括服务拓扑、服务间通信、服务发现、API网关、分布式追踪等关键规范。
keywords: microservices | distributed-systems | service-mesh | api-gateway | service-discovery | grpc | message-queue
scope: 微服务架构项目类型配置
related_files: 无
dependencies: core/project_types.md | core/project_types/backend_api.md
verified_at: 2026-01-21
---

# 微服务架构

> **适用场景**: 分布式服务架构 / 云原生应用 / 大规模系统

---

## 🎯 核心技术栈

### 服务框架
- **Node.js**: NestJS / Fastify
- **Java**: Spring Boot / Quarkus / Micronaut
- **Go**: Go-kit / Go-micro
- **.NET**: ASP.NET Core
- **Python**: FastAPI / Nameko

### 服务间通信
- **同步**: REST / gRPC / GraphQL
- **异步**: RabbitMQ / Kafka / NATS / Redis Streams

### 服务发现
- **Consul**: HashiCorp 服务发现
- **Eureka**: Netflix 服务注册
- **etcd**: Kubernetes 原生
- **Nacos**: 阿里云服务发现

### API 网关
- **Kong**: 开源 API 网关
- **Traefik**: 云原生边缘路由
- **APISIX**: 高性能网关
- **AWS API Gateway**: 托管服务

### 服务网格
- **Istio**: 功能最全
- **Linkerd**: 轻量级
- **Consul Connect**: HashiCorp 方案

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `service_topology.md` | 服务拓扑图 |
| 🔴 高 | `inter_service_communication.md` | 服务间通信 |
| 🔴 高 | `service_discovery.md` | 服务发现与注册 |
| 🟡 中 | `api_gateway.md` | API 网关配置 |
| 🟡 中 | `distributed_tracing.md` | 分布式追踪 |
| 🟡 中 | `circuit_breaker.md` | 熔断与降级 |
| 🟢 低 | `service_mesh.md` | 服务网格（如适用） |

---

## 🔍 特殊关注点

### 服务拓扑图

- 服务依赖关系
- 数据流向
- 同步/异步调用
- 外部依赖

### 服务间通信

- **REST**: 简单易用，广泛支持
- **gRPC**: 高性能，强类型
- **消息队列**: 异步解耦

### 服务发现与注册

- 健康检查
- 负载均衡
- 故障转移

### API 网关配置

- 路由规则
- 认证授权
- 限流熔断
- 请求转换

### 分布式追踪

- **Jaeger**: CNCF 项目
- **Zipkin**: Twitter 开源
- **OpenTelemetry**: 统一标准

### 熔断与降级

- **Hystrix**: Netflix（已停止维护）
- **Resilience4j**: 现代替代方案
- **Sentinel**: 阿里云流量控制

---

## 💻 核心代码模式

### gRPC 服务定义

```protobuf
// user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (GetUserResponse);
  rpc CreateUser (CreateUserRequest) returns (CreateUserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  string id = 1;
  string name = 2;
  string email = 3;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  string id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}

message UserResponse {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

### gRPC 服务实现（Node.js）

```typescript
import * as grpc from '@grpc/grpc-js'
import * as protoLoader from '@grpc/proto-loader'

const packageDefinition = protoLoader.loadSync('user.proto')
const userProto = grpc.loadPackageDefinition(packageDefinition).user

// 实现服务
const userService = {
  async getUser(call, callback) {
    const { id } = call.request
    
    try {
      const user = await db.user.findUnique({ where: { id } })
      callback(null, user)
    } catch (error) {
      callback({
        code: grpc.status.NOT_FOUND,
        message: 'User not found'
      })
    }
  },
  
  async createUser(call, callback) {
    const { name, email } = call.request
    
    try {
      const user = await db.user.create({ data: { name, email } })
      callback(null, { id: user.id })
    } catch (error) {
      callback({
        code: grpc.status.INTERNAL,
        message: error.message
      })
    }
  },
  
  async listUsers(call) {
    const { page, pageSize } = call.request
    
    const users = await db.user.findMany({
      skip: (page - 1) * pageSize,
      take: pageSize
    })
    
    for (const user of users) {
      call.write(user)
    }
    call.end()
  }
}

// 启动服务器
const server = new grpc.Server()
server.addService(userProto.UserService.service, userService)
server.bindAsync(
  '0.0.0.0:50051',
  grpc.ServerCredentials.createInsecure(),
  () => {
    console.log('gRPC server running on port 50051')
    server.start()
  }
)
```

### 消息队列（RabbitMQ）

```typescript
import amqp from 'amqplib'

// 生产者
class MessagePublisher {
  private connection: amqp.Connection
  private channel: amqp.Channel

  async connect() {
    this.connection = await amqp.connect('amqp://localhost')
    this.channel = await this.connection.createChannel()
  }

  async publish(queue: string, message: any) {
    await this.channel.assertQueue(queue, { durable: true })
    this.channel.sendToQueue(
      queue,
      Buffer.from(JSON.stringify(message)),
      { persistent: true }
    )
  }
}

// 消费者
class MessageConsumer {
  private connection: amqp.Connection
  private channel: amqp.Channel

  async connect() {
    this.connection = await amqp.connect('amqp://localhost')
    this.channel = await this.connection.createChannel()
  }

  async consume(queue: string, handler: (msg: any) => Promise<void>) {
    await this.channel.assertQueue(queue, { durable: true })
    this.channel.prefetch(1)

    this.channel.consume(queue, async (msg) => {
      if (msg) {
        try {
          const content = JSON.parse(msg.content.toString())
          await handler(content)
          this.channel.ack(msg)
        } catch (error) {
          console.error('Error processing message:', error)
          this.channel.nack(msg, false, true)  // 重新入队
        }
      }
    })
  }
}
```

### 服务发现（Consul）

```typescript
import Consul from 'consul'

const consul = new Consul({
  host: 'localhost',
  port: 8500
})

// 注册服务
async function registerService() {
  await consul.agent.service.register({
    id: 'user-service-1',
    name: 'user-service',
    address: 'localhost',
    port: 3000,
    check: {
      http: 'http://localhost:3000/health',
      interval: '10s',
      timeout: '5s'
    }
  })
}

// 发现服务
async function discoverService(serviceName: string) {
  const result = await consul.health.service({
    service: serviceName,
    passing: true
  })
  
  return result.map(entry => ({
    address: entry.Service.Address,
    port: entry.Service.Port
  }))
}

// 负载均衡（简单轮询）
class ServiceClient {
  private services: Array<{ address: string; port: number }> = []
  private currentIndex = 0

  async refreshServices(serviceName: string) {
    this.services = await discoverService(serviceName)
  }

  getNextService() {
    const service = this.services[this.currentIndex]
    this.currentIndex = (this.currentIndex + 1) % this.services.length
    return service
  }
}
```

### 熔断器（Resilience4j 风格）

```typescript
class CircuitBreaker {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'
  private failureCount = 0
  private successCount = 0
  private lastFailureTime = 0
  
  constructor(
    private failureThreshold = 5,
    private timeout = 60000,  // 1分钟
    private halfOpenRequests = 3
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN'
        this.successCount = 0
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }

    try {
      const result = await fn()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess() {
    this.failureCount = 0
    
    if (this.state === 'HALF_OPEN') {
      this.successCount++
      if (this.successCount >= this.halfOpenRequests) {
        this.state = 'CLOSED'
      }
    }
  }

  private onFailure() {
    this.failureCount++
    this.lastFailureTime = Date.now()
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN'
    }
  }
}

// 使用示例
const breaker = new CircuitBreaker()

async function callExternalService() {
  return await breaker.execute(async () => {
    const response = await fetch('http://external-service/api')
    return response.json()
  })
}
```

### 分布式追踪（OpenTelemetry）

```typescript
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node'
import { registerInstrumentations } from '@opentelemetry/instrumentation'
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http'
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express'
import { JaegerExporter } from '@opentelemetry/exporter-jaeger'

// 配置追踪
const provider = new NodeTracerProvider()

provider.addSpanProcessor(
  new BatchSpanProcessor(
    new JaegerExporter({
      endpoint: 'http://localhost:14268/api/traces'
    })
  )
)

provider.register()

registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation()
  ]
})

// 手动创建 span
import { trace } from '@opentelemetry/api'

const tracer = trace.getTracer('user-service')

async function processUser(userId: string) {
  const span = tracer.startSpan('processUser')
  span.setAttribute('user.id', userId)
  
  try {
    // 业务逻辑
    const user = await getUser(userId)
    span.setStatus({ code: SpanStatusCode.OK })
    return user
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message
    })
    throw error
  } finally {
    span.end()
  }
}
```

---

## ⚠️ 常见问题

### 问题 1: 服务间调用失败

**解决方案**: 实现重试和熔断机制

```typescript
async function callWithRetry(fn: () => Promise<any>, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === retries - 1) throw error
      await sleep(Math.pow(2, i) * 1000)  // 指数退避
    }
  }
}
```

### 问题 2: 分布式事务

**解决方案**: 使用 Saga 模式或事件溯源

```typescript
// Saga 编排器
class OrderSaga {
  async execute(order: Order) {
    try {
      // 步骤1: 创建订单
      await orderService.create(order)
      
      // 步骤2: 扣减库存
      await inventoryService.reserve(order.items)
      
      // 步骤3: 处理支付
      await paymentService.charge(order.amount)
      
      // 步骤4: 发送通知
      await notificationService.send(order.userId)
    } catch (error) {
      // 补偿操作
      await this.compensate(order)
      throw error
    }
  }
  
  async compensate(order: Order) {
    await paymentService.refund(order.id)
    await inventoryService.release(order.items)
    await orderService.cancel(order.id)
  }
}
```

### 问题 3: 服务依赖过多

**解决方案**: 使用 API 网关聚合请求

```typescript
// API 网关聚合
async function getUserProfile(userId: string) {
  const [user, orders, preferences] = await Promise.all([
    userService.getUser(userId),
    orderService.getUserOrders(userId),
    preferenceService.getUserPreferences(userId)
  ])
  
  return {
    ...user,
    orders,
    preferences
  }
}
```

---

## 🎯 检查清单

生成微服务架构项目文档前，确认：

- [ ] 已绘制服务拓扑图
- [ ] 已确定服务间通信方式（REST/gRPC/消息队列）
- [ ] 已确定服务发现方案（Consul/Eureka/etcd）
- [ ] 已确定 API 网关（Kong/Traefik/APISIX）
- [ ] 已确定分布式追踪方案（Jaeger/Zipkin）
- [ ] 已确定熔断降级策略
- [ ] 已确定配置中心（Consul/Nacos/Spring Cloud Config）
- [ ] 已确定日志聚合方案（ELK/Loki）
- [ ] 已确定监控方案（Prometheus/Grafana）
- [ ] 已考虑分布式事务处理

---

**版本**: v3.0  
**路径**: `core/project_types/microservices.md`  
**最后更新**: 2026-01-21
