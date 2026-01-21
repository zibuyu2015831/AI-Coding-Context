---
title: Serverless 项目配置
summary: 定义 Serverless 项目（AWS Lambda/Cloud Functions）的推荐子文档清单、特殊关注点和核心代码模式。包括函数组织结构、部署配置、冷启动优化等关键规范。
keywords: serverless | aws-lambda | cloud-functions | faas | cold-start | deployment
scope: Serverless 项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# Serverless 项目

> **适用平台**: AWS Lambda / Azure Functions / Google Cloud Functions / Vercel/Netlify Functions

---

## 🎯 适用平台

- **AWS Lambda**: 最成熟的 FaaS 平台
- **Azure Functions**: 微软云函数
- **Google Cloud Functions**: Google 云函数
- **Vercel Functions**: 边缘函数，Next.js 集成
- **Netlify Functions**: JAMstack 友好
- **Cloudflare Workers**: 边缘计算

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `function_structure.md` | 函数组织结构 |
| 🔴 高 | `deployment.md` | 部署配置 |
| 🟡 中 | `environment_vars.md` | 环境变量管理 |
| 🟡 中 | `cold_start_optimization.md` | 冷启动优化 |
| 🟡 中 | `monitoring.md` | 监控与日志 |

---

## 🔍 特殊关注点

### 函数触发器配置

- **HTTP**: API Gateway / HTTP Trigger
- **事件**: S3 / DynamoDB / EventBridge
- **定时**: CloudWatch Events / Cron
- **队列**: SQS / Service Bus

### 权限设置

- **AWS**: IAM Roles / Policies
- **Azure**: RBAC / Managed Identity
- **GCP**: Service Accounts

### 资源限制

- **内存**: 128MB - 10GB
- **超时**: 最长 15 分钟（Lambda）
- **并发**: 预留并发 / 临时并发

### 冷启动优化

- 减小包大小
- 使用预留并发
- 选择合适的运行时
- 代码优化

### 成本优化策略

- 合理设置内存
- 使用 ARM 架构（Graviton）
- 监控和优化执行时间
- 使用预留容量

---

## 💻 核心代码模式

### AWS Lambda (Node.js)

```typescript
// handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda'

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    const body = JSON.parse(event.body || '{}')
    
    // 处理逻辑
    const result = await processData(body)
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(result)
    }
  } catch (error) {
    console.error('Error:', error)
    
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error' })
    }
  }
}

// S3 事件触发
import { S3Event } from 'aws-lambda'

export const s3Handler = async (event: S3Event) => {
  for (const record of event.Records) {
    const bucket = record.s3.bucket.name
    const key = record.s3.object.key
    
    console.log(`Processing file: ${bucket}/${key}`)
    // 处理文件
  }
}
```

### Serverless Framework 配置

```yaml
# serverless.yml
service: my-service

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  memorySize: 256
  timeout: 30
  environment:
    TABLE_NAME: ${self:custom.tableName}
    API_KEY: ${env:API_KEY}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:PutItem
            - dynamodb:GetItem
          Resource: !GetAtt MyTable.Arn

functions:
  api:
    handler: handler.handler
    events:
      - http:
          path: /api/{proxy+}
          method: ANY
          cors: true
  
  processFile:
    handler: handler.s3Handler
    events:
      - s3:
          bucket: my-bucket
          event: s3:ObjectCreated:*
          rules:
            - prefix: uploads/
            - suffix: .jpg
  
  scheduled:
    handler: handler.scheduledHandler
    events:
      - schedule: rate(5 minutes)

resources:
  Resources:
    MyTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.tableName}
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST

custom:
  tableName: my-table-${sls:stage}
```

### AWS SAM 配置

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    Runtime: nodejs18.x
    Environment:
      Variables:
        TABLE_NAME: !Ref MyTable

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: handler.handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /api/{proxy+}
            Method: ANY
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MyTable
  
  MyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
```

### 冷启动优化

```typescript
// 在函数外部初始化连接（复用）
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'

const dynamoClient = new DynamoDBClient({ region: 'us-east-1' })

export const handler = async (event) => {
  // 使用已初始化的客户端
  // 避免每次调用都创建新连接
}

// 使用 Provisioned Concurrency
// serverless.yml
functions:
  api:
    handler: handler.handler
    provisionedConcurrency: 5  # 预留5个实例
```

### 环境变量管理

```typescript
// 使用 AWS Systems Manager Parameter Store
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm'

const ssmClient = new SSMClient({ region: 'us-east-1' })

async function getSecret(name: string): Promise<string> {
  const command = new GetParameterCommand({
    Name: name,
    WithDecryption: true
  })
  
  const response = await ssmClient.send(command)
  return response.Parameter?.Value || ''
}

// 使用 AWS Secrets Manager
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager'

const secretsClient = new SecretsManagerClient({ region: 'us-east-1' })

async function getSecretValue(secretId: string): Promise<any> {
  const command = new GetSecretValueCommand({ SecretId: secretId })
  const response = await secretsClient.send(command)
  return JSON.parse(response.SecretString || '{}')
}
```

### 错误处理和重试

```typescript
// 使用 DLQ (Dead Letter Queue)
// serverless.yml
functions:
  processor:
    handler: handler.process
    onError: arn:aws:sqs:us-east-1:123456789:my-dlq
    events:
      - sqs:
          arn: !GetAtt MyQueue.Arn
          batchSize: 10

// 代码中的重试逻辑
async function processWithRetry(data: any, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await process(data)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await sleep(Math.pow(2, i) * 1000)  // 指数退避
    }
  }
}
```

### 监控和日志

```typescript
// 结构化日志
console.log(JSON.stringify({
  level: 'INFO',
  message: 'Processing request',
  requestId: event.requestContext.requestId,
  userId: event.requestContext.authorizer?.userId
}))

// 使用 AWS X-Ray 追踪
import AWSXRay from 'aws-xray-sdk-core'
const AWS = AWSXRay.captureAWS(require('aws-sdk'))

// 自定义指标
import { CloudWatch } from 'aws-sdk'
const cloudwatch = new CloudWatch()

await cloudwatch.putMetricData({
  Namespace: 'MyApp',
  MetricData: [{
    MetricName: 'ProcessingTime',
    Value: duration,
    Unit: 'Milliseconds'
  }]
}).promise()
```

---

## ⚠️ 常见问题

### 问题 1: 冷启动时间过长

**解决方案**: 优化包大小和使用预留并发

```typescript
// 使用 esbuild 打包减小体积
// package.json
{
  "scripts": {
    "build": "esbuild handler.ts --bundle --platform=node --target=node18 --outfile=dist/handler.js"
  }
}

// 使用预留并发
// serverless.yml
functions:
  api:
    provisionedConcurrency: 5
```

### 问题 2: 超时

**解决方案**: 增加超时时间或拆分函数

```yaml
# serverless.yml
functions:
  longRunning:
    handler: handler.longTask
    timeout: 900  # 15分钟（最大值）
```

### 问题 3: 成本过高

**解决方案**: 优化内存和执行时间

```yaml
# 监控并调整内存设置
functions:
  api:
    memorySize: 256  # 从1024降到256
    # 注意: 内存越大，CPU 也越强
```

---

## 🎯 检查清单

生成 Serverless 项目文档前，确认：

- [ ] 已识别目标平台（AWS/Azure/GCP/Vercel）
- [ ] 已确定函数触发器类型（HTTP/事件/定时）
- [ ] 已确定运行时（Node.js/Python/Go 等）
- [ ] 已确定内存和超时设置
- [ ] 已确定权限和 IAM 策略
- [ ] 已确定环境变量管理方式
- [ ] 已确定监控和日志策略
- [ ] 已确定部署工具（Serverless Framework/SAM/Terraform）
- [ ] 已考虑冷启动优化
- [ ] 已考虑成本优化

---

**版本**: v3.0  
**路径**: `core/project_types/serverless.md`  
**最后更新**: 2026-01-21
