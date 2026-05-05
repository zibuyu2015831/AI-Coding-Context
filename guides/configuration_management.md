---
title: 配置管理最佳实践
summary: 说明项目配置管理的推荐策略、配置分层原则与敏感信息处理方式，帮助维护者建立可演进且可审计的配置体系。
keywords: configuration | guide | best-practice | env | secrets | aicc
scope: 项目配置管理与配置文档化实践
related_files: 无
dependencies: config/README.md | config/CONFIG_TEMPLATE.md | core/security_rules.md
verified_at: 2026-05-05
---

# 配置管理最佳实践

> **版本**: v2.3  
> **创建日期**: 2025-11-28  
> **用途**: 指导项目配置管理的最佳实践

---

## 📋 概述

良好的配置管理是项目可维护性的关键。本指南说明：

- 配置方案对比
- 推荐的分层配置策略
- 敏感信息处理
- 配置文档化建议

---

## 🆚 配置方案对比

### 方案 1: 环境变量 (.env)

**适用**: 小型项目、快速开发

**优点**:

- ✅ 简单直观
- ✅ 广泛支持（大部分框架）
- ✅ 敏感信息不提交 Git

**缺点**:

- ❌ 无类型检查
- ❌ 无默认值机制
- ❌ 难以管理复杂配置

**示例**:

```bash
# .env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp_db
API_KEY=sk-your-api-key-here
```

---

### 方案 2: 配置文件 (YAML/JSON)

**适用**: 中大型项目、配置复杂

**优点**:

- ✅ 结构化配置
- ✅ 支持注释（YAML）
- ✅ 易于版本控制
- ✅ 可以提交到 Git（非敏感部分）

**缺点**:

- ❌ 敏感信息需要单独处理
- ❌ 需要解析库

**示例 (YAML)**:

```yaml
# config.yaml
database:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  name: ${DB_NAME:-myapp_db}

api:
  timeout: 30
  retries: 3

logging:
  level: info
  format: json
```

---

### 方案 3: 代码配置 (Python/JS 等)

**适用**: 需要逻辑判断的配置

**优点**:

- ✅ 类型安全（TypeScript）
- ✅ 可以包含逻辑
- ✅ IDE 支持好

**缺点**:

- ❌ 修改需要重新编译/部署
- ❌ 不够灵活

**示例 (Python)**:

```python
# config.py
import os

class Config:
    DATABASE_HOST = os.getenv('DB_HOST', 'localhost')
    DATABASE_PORT = int(os.getenv('DB_PORT', 5432))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

---

## 🎯 推荐方案：分层配置

**最佳实践**: 结合环境变量 + 配置文件

```
配置层次:
1. 默认配置（config.default.yaml）- 提交到Git
2. 环境配置（.env.development、.env.production）- 不提交
3. 环境变量（运营时动态设置）- 最高优先级
```

---

### 实施方案

#### 文件结构

```
project/
├── config/
│   ├── config.default.yaml    # 默认配置（Git提交）
│   ├── config.development.yaml # 开发环境配置（Git提交）
│   ├── config.production.yaml  # 生产环境配置（Git提交）
│   └── config.schema.json      # 配置Schema（可选）
│
├── .env.example               # 环境变量示例（Git提交）
├── .env.development           # 开发环境变量（不提交）
├── .env.production            # 生产环境变量（不提交）
└── .gitignore                 # 忽略.env文件
```

---

#### 配置文件示例

**config/config.default.yaml** (可提交):

```yaml
# 默认配置 - 非敏感信息

server:
  host: localhost
  port: ${PORT:-3000} # 可被环境变量覆盖

database:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  name: ${DB_NAME:-myapp}
  # 密码从环境变量读取

redis:
  host: ${REDIS_HOST:-localhost}
  port: ${REDIS_PORT:-6379}

api:
  timeout: 30
  retries: 3
  rateLimit:
    max: 100
    window: 60
```

**config/config.development.yaml** (可提交):

```yaml
# 开发环境配置

server:
  port: 3000
  debug: true

database:
  name: myapp_dev

logging:
  level: debug
  format: pretty
```

**config/config.production.yaml** (可提交):

```yaml
# 生产环境配置

server:
  port: 8080
  debug: false

database:
  pool:
    min: 10
    max: 100

logging:
  level: info
  format: json
```

**.env.example** (可提交):

```bash
# 环境变量示例 - 复制为.env并填写实际值

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_PASSWORD=your-password-here

# API密钥
API_KEY=your-api-key-here
JWT_SECRET=your-jwt-secret-here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

**.env.development** (不提交):

```bash
# 开发环境实际值

DB_HOST=localhost
DB_PASSWORD=dev_password_123
API_KEY=sk-dev-1234567890abcdef
JWT_SECRET=dev-secret-key-please-change
```

**.env.production** (不提交):

```bash
# 生产环境实际值（通过CI/CD或运维平台设置）

DB_HOST=db.production.internal
DB_PASSWORD=******************
API_KEY=sk-prod-******************
JWT_SECRET=******************
```

---

#### 配置加载逻辑

**Python 示例**:

```python
# config_loader.py
import os
import yaml
from pathlib import Path

def load_config():
    """加载分层配置"""

    # 1. 确定环境
    env = os.getenv('APP_ENV', 'development')

    # 2. 加载默认配置
    with open('config/config.default.yaml') as f:
        config = yaml.safe_load(f)

    # 3. 加载环境特定配置（覆盖默认）
    env_config_path = f'config/config.{env}.yaml'
    if Path(env_config_path).exists():
        with open(env_config_path) as f:
            env_config = yaml.safe_load(f)
            deep_merge(config, env_config)

    # 4. 应用环境变量（最高优先级）
    config = substitute_env_vars(config)

    return config

def substitute_env_vars(config):
    """替换配置中的环境变量引用"""
    # 递归处理 ${VAR:-default} 语法
    pass

def deep_merge(base, updates):
    """深度合并配置字典"""
    for key, value in updates.items():
        if isinstance(value, dict) and key in base:
            deep_merge(base[key], value)
        else:
            base[key] = value
```

**Node.js 示例**:

```javascript
// configLoader.js
const fs = require("fs");
const yaml = require("js-yaml");
const dotenv = require("dotenv");

function loadConfig() {
  // 1. 加载环境变量
  const env = process.env.NODE_ENV || "development";
  dotenv.config({ path: `.env.${env}` });

  // 2. 加载默认配置
  const defaultConfig = yaml.load(
    fs.readFileSync("config/config.default.yaml", "utf8")
  );

  // 3. 加载环境特定配置
  const envConfigPath = `config/config.${env}.yaml`;
  const envConfig = fs.existsSync(envConfigPath)
    ? yaml.load(fs.readFileSync(envConfigPath, "utf8"))
    : {};

  // 4. 合并配置
  const config = deepMerge(defaultConfig, envConfig);

  // 5. 替换环境变量
  return substituteEnvVars(config);
}

function substituteEnvVars(obj) {
  // 递归替换 ${VAR:-default} 语法
  const regex = /\$\{(\w+)(?::-(.*?))?\}/g;

  if (typeof obj === "string") {
    return obj.replace(regex, (match, varName, defaultValue) => {
      return process.env[varName] || defaultValue || "";
    });
  }

  if (typeof obj === "object" && obj !== null) {
    const result = Array.isArray(obj) ? [] : {};
    for (const key in obj) {
      result[key] = substituteEnvVars(obj[key]);
    }
    return result;
  }

  return obj;
}
```

---

## 🔒 敏感信息处理

### 原则

1. **永远不提交敏感信息到 Git**
2. **使用环境变量存储敏感信息**
3. **提供.env.example 作为模板**
4. **生产环境通过 CI/CD 或密钥管理服务注入**

---

### 敏感信息清单

重新整理以下信息都属于敏感信息：

| 类型       | 示例                    | 存储方式               |
| ---------- | ----------------------- | ---------------------- |
| 数据库密码 | `DB_PASSWORD`           | 环境变量               |
| API 密钥   | `OPENAI_API_KEY`        | 环境变量               |
| JWT Secret | `JWT_SECRET`            | 环境变量               |
| OAuth 凭证 | `GOOGLE_CLIENT_SECRET`  | 环境变量               |
| 云服务密钥 | `AWS_SECRET_ACCESS_KEY` | 环境变量或服务凭证     |
| 加密密钥   | `ENCRYPTION_KEY`        | 环境变量或密钥管理服务 |

---

### 生产环境最佳实践

**不推荐** ❌:

```bash
# 直接在服务器上创建.env文件
echo "DB_PASSWORD=prod_password" > .env
```

**推荐方案** ✅:

**方案 1: 使用 CI/CD 环境变量**

```yaml
# .gitlab-ci.yml
deploy:
  variables:
    DB_PASSWORD: $CI_DB_PASSWORD # 从GitLab CI/CD变量读取
    API_KEY: $CI_API_KEY
```

**方案 2: 使用密钥管理服务**

```python
# 从AWS Secrets Manager读取
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

DB_PASSWORD = get_secret('myapp/db/password')
```

**方案 3: 使用容器环境变量**

```yaml
# docker-compose.yml
services:
  web:
    environment:
      - DB_PASSWORD=${DB_PASSWORD} # 从宿主机环境变量读取
    env_file:
      - .env.production # 或从文件读取
```

---

## 📝 配置文档化

### 文档模板

**在 dev_docs 中创建 `configuration.md`**:

```markdown
# 配置文档

## 配置文件结构
```

config/
├── config.default.yaml # 默认配置
├── config.development.yaml # 开发环境
└── config.production.yaml # 生产环境

````

## 环境变量

### 必需的环境变量

| 变量名 | 说明 | 示例值 | 默认值 |
|--------|------|--------|--------|
| `DB_PASSWORD` | 数据库密码 | `********` | 无 |
| `API_KEY` | OpenAI API密钥 | `sk-...` | 无 |
| `JWT_SECRET` | JWT签名密钥 | `********` | 无 |

### 可选的环境变量

| 变量名 | 说明 | 示例值 | 默认值 |
|--------|------|--------|--------|
| `PORT` | 服务器端口 | `3000` | `3000` |
| `LOG_LEVEL` | 日志级别 | `debug` | `info` |

## 配置说明

### 数据库配置

**位置**: `config.default.yaml` → `database`

```yaml
database:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  name: ${DB_NAME:-myapp}
  pool:
    min: 2
    max: 10
````

**说明**:

- `host`: 数据库地址，可通过`DB_HOST`环境变量覆盖
- `pool.max`: 连接池最大连接数，生产环境建议 50-100

### API 配置

**位置**: `config.default.yaml` → `api`

```yaml
api:
  timeout: 30 # API请求超时时间（秒）
  retries: 3 # 失败重试次数
```

## 环境切换

### 开发环境

```bash
# 使用开发环境配置
export APP_ENV=development
npm start
```

### 生产环境

```bash
# 使用生产环境配置
export APP_ENV=production
npm start
```

## 新增配置项

添加新配置时：

1. 在`config.default.yaml`中添加默认值
2. 如需环境变量覆盖，使用`${VAR:-default}`语法
3. 更新本文档
4. 如果是敏感信息，添加到`.env.example`

```

---

## 🎯 配置管理检查清单

### 新项目配置清单

- [ ] 创建 `config/config.default.yaml`
- [ ] 创建环境特定配置文件
- [ ] 创建 `.env.example`
- [ ] 在 `.gitignore` 中排除 `.env*`（除.env.example）
- [ ] 编写配置加载逻辑
- [ ] 编写配置文档 `dev_docs/configuration.md`
- [ ] 验证所有敏感信息都使用环境变量

### 配置变更检查清单

变更配置时：

- [ ] 配置文件已更新
- [ ] `.env.example` 已同步
- [ ] 配置文档已更新
- [ ] 团队成员已通知（如有新环境变量）
- [ ] 生产环境CI/CD变量已更新（如适用）

---

## 🔗 相关文档

- [core/security_rules.md](../core/security_rules.md) - 敏感信息脱敏规范
- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 框架主入口

---

## 💡 最佳实践总结

1. **分层配置** - 默认配置 + 环境配置 + 环境变量
2. **敏感信息分离** - 永不提交敏感信息到Git
3. **提供示例** - .env.example让新成员快速上手
4. **文档化** - 所有配置都有说明
5. **类型安全** - 使用config schema验证（可选）
6. **环境变量优先** - 允许运行时覆盖配置

---

**版本**: v2.3
**最后更新**: 2025-11-28
**路径**: `guides/configuration_management.md`
```
