---
title: 安全规范 — 敏感信息脱敏
summary: 定义 AICC 框架在文档生成、commit 分析、知识沉淀等场景下对敏感信息的识别与脱敏规则；涉及密钥、令牌、内部 URL、个人信息等
keywords: security | redaction | sensitive-data | aicc
scope: AI 在 AICC 框架内处理代码或文档时对敏感信息的处理约束
related_files: AI_ENTRY_POINT.md | core/framework_spec.md
dependencies: 无
verified_at: 2026-04-26
---

# 安全规范 - 敏感信息脱敏

> **上级文档**: [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md)  
> **版本**: v3.0  
> **最后更新**: 2026-04-20

---

## 🔒 核心原则

**在生成任何文档时都必须遵守脱敏规则,确保不泄露敏感信息**

---

## 📋 脱敏规则 (7 类)

### 1. API 密钥

**规则**: 替换为 `sk-xxx...xxx` (保留前后各 3 位)

**示例**:

- ❌ 错误: `sk-1234567890abcdefghijklmn`
- ✅ 正确: `sk-123...lmn` 或 `process.env.API_KEY`

### 2. 数据库密码

**规则**: 替换为 `********`

**示例**:

- ❌ 错误: `MyS3cr3tP@ssw0rd`
- ✅ 正确: `********` 或 `process.env.DB_PASSWORD`

### 3. 私钥文件内容

**规则**: 替换为 `[REDACTED]`

**示例**:

- ❌ 错误: 显示完整 RSA 私钥
- ✅ 正确: `[REDACTED]` 或说明"私钥文件路径:..."

### 4. 真实域名

**规则**: 替换为 `example.com` 或 `yourdomain.com`

**示例**:

- ❌ 错误: `db.mycompany.com`
- ✅ 正确: `db.example.com` 或 `process.env.DB_HOST`

### 5. 真实 IP 地址

**规则**: 替换为 `192.168.x.x` 或 `10.0.x.x`

**示例**:

- ❌ 错误: `123.456.789.012`
- ✅ 正确: `192.168.1.x` 或 `process.env.SERVER_IP`

### 6. 个人身份信息 (PII)

**规则**: 替换为 `[PII_REDACTED]`

**包括**: 真实姓名、邮箱、电话、身份证号等

**示例**:

- ❌ 错误: `张三`, `zhangsan@company.com`, `13800138000`
- ✅ 正确: `[用户名]`, `user@example.com`, `13800******`

### 7. JWT Token

**规则**: 替换为 `eyJxxx...xxx` (保留前后各 3 个字符)

**示例**:

- ❌ 错误: 完整 token
- ✅ 正确: `eyJ...xyz` 或 `[JWT_TOKEN]`

---

## 🛑 Git 安全规范 (SAFETY RED ZONES)

**AI 在执行 Git 操作时必须严格遵守以下红线,任何违反行为都将触发机械式阻断。**

### 1. 保护分支操作 (Protected Branch Operations)
- ⛔ **绝对禁止** 在 `main`, `master`, `production`, `release/*` 分支执行 `commit` 或 `push`。
- ⛔ **绝对禁止** 直接在保护分支上进行任何破坏性变更。

### 2. 危险命令 (Dangerous Commands)
- ⛔ **绝对禁止** 执行 `git reset --hard` (历史重写)。
- ⛔ **绝对禁止** 执行 `git push --force` 或 `git push -f` (强推)。
- ⛔ **绝对禁止** 执行 `git rebase` (变基)。

### 3. 合并操作 (Merge Operations)
- ⛔ **绝对禁止** 执行 `git merge` (除 `git merge --abort` 外)。
- 💡 **原则**: 所有代码合并、冲突解决及集成操作必须由**用户手动**执行。

### 4. 分支与标签管理 (Branch & Tag Management)
- ⛔ **绝对禁止** 执行 `git branch -D` (强制删除本地分支)。
- ⛔ **绝对禁止** 执行 `git push [remote] :[branch]` (删除远程分支)。
- ⛔ **绝对禁止** 执行任何 `git tag` 操作(创建、删除、重命名)。
- ⛔ **绝对禁止** 推送标签 (`git push --tags`)。

---

## ⚠️ 受限操作 (YELLOW ZONE)

**以下操作需要用户明确审核或二次授权**:
- `git checkout -b [branch-name]`: 需确认分支命名规范。
- `git commit`: 需根据 ADR 003 审核 WHAT/WHY/HOW 格式。
- `git push origin [branch-name]`: 需确认推送的目标分支。

---

## 📝 详细代码示例

### 示例 1: API 密钥脱敏

**场景**: 第三方服务集成

**❌ 不安全的代码** (绝对禁止):

```python
# ❌ 硬编码密钥 - 严重安全风险
OPENAI_API_KEY = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
STRIPE_SECRET_KEY = "sk_live_51AbCdEfGhIjKlMnOpQrStUvWxYz"

def call_api():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.post("https://api.openai.com/v1/chat", headers=headers)
```

**✅ 安全的代码** (文档中应该这样写):

```python
# ✅ 使用环境变量 - 安全
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 示例值: sk-proj-abc...xyz
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")  # 示例值: sk_live_51A...Yz

def call_api():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.post("https://api.openai.com/v1/chat", headers=headers)
```

**配置说明**:

```bash
# .env 文件 (不提交到Git)
OPENAI_API_KEY=sk-proj-actual-key-here
STRIPE_SECRET_KEY=sk_live_actual-key-here

# .env.example 文件 (可以提交到Git)
OPENAI_API_KEY=sk-proj-your-key-here
STRIPE_SECRET_KEY=sk_live_your-key-here
```

---

### 示例 2: 数据库连接信息脱敏

**场景**: 数据库配置

**❌ 不安全的代码**:

```python
# ❌ 硬编码数据库密码
DATABASE_CONFIG = {
    "host": "db-prod.mycompany.com",
    "port": 5432,
    "username": "admin",
    "password": "MyS3cr3tP@ssw0rd123!",
    "database": "production_db"
}

# SQLAlchemy 连接字符串
DATABASE_URL = "postgresql://admin:MyS3cr3tP@ssw0rd123!@db-prod.mycompany.com:5432/production_db"
```

**✅ 安全的代码**:

```python
# ✅ 使用环境变量
import os

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),  # 示例: db.example.com
    "port": int(os.getenv("DB_PORT", "5432")),
    "username": os.getenv("DB_USER"),  # 示例: dbuser
    "password": os.getenv("DB_PASSWORD"),  # ********
    "database": os.getenv("DB_NAME")  # 示例: myapp_db
}

# SQLAlchemy 连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")
# 示例: postgresql://dbuser:********@db.example.com:5432/myapp_db
```

**配置文件示例** (YAML):

```yaml
# ❌ 错误 - config.yaml
database:
  host: db-prod.mycompany.com
  password: MyS3cr3tP@ssw0rd123!

# ✅ 正确 - config.yaml (使用环境变量引用)
database:
  host: ${DB_HOST}  # db.example.com
  password: ${DB_PASSWORD}  # ********

# 说明: 实际值从环境变量读取，配置文件只包含引用
```

---

### 示例 3: JWT Token 和 OAuth 凭证脱敏

**场景**: 用户认证

**❌ 不安全的代码**:

```javascript
// ❌ 硬编码 JWT Secret
const JWT_SECRET = "my-super-secret-jwt-key-12345";
const GOOGLE_CLIENT_SECRET = "GOCSPX-1234567890abcdefghij";

// 生成 Token
const token = jwt.sign({ userId: 123 }, JWT_SECRET);

// OAuth 配置
const oauth2Client = new OAuth2(
  "client-id.apps.googleusercontent.com",
  "GOCSPX-1234567890abcdefghij", // ❌ 硬编码
  "http://localhost:3000/callback"
);
```

**✅ 安全的代码**:

```javascript
// ✅ 使用环境变量
const JWT_SECRET = process.env.JWT_SECRET; // ******** (至少32字符)
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET; // GOCSPX-abc...hij

// 生成 Token
const token = jwt.sign({ userId: 123 }, JWT_SECRET);
// 示例 Token: eyJhbGciOiJIUzI1NiIs...xyz (实际使用时已脱敏)

// OAuth 配置
const oauth2Client = new OAuth2(
  process.env.GOOGLE_CLIENT_ID, // xxx.apps.googleusercontent.com
  process.env.GOOGLE_CLIENT_SECRET, // GOCSPX-abc...hij
  process.env.OAUTH_REDIRECT_URI // http://localhost:3000/callback
);
```

**Token 使用示例**:

```javascript
// ❌ 错误 - 日志中暴露完整 Token
console.log(`User token: ${fullToken}`);

// ✅ 正确 - 脱敏后记录
console.log(`User token: ${fullToken.substring(0, 10)}...`);
// 输出: User token: eyJhbGciOi...
```

---

### 示例 4: 云服务凭证脱敏

**场景**: AWS/阿里云/腾讯云配置

**❌ 不安全的代码**:

```python
# ❌ 硬编码云服务密钥
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# 初始化客户端
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
```

**✅ 安全的代码**:

```python
# ✅ 使用环境变量或 IAM 角色
import os
import boto3

# 方式1: 环境变量
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  # AKIA...PLE
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  # ********

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# ✅ 方式2: IAM 角色 (生产环境推荐)
s3_client = boto3.client('s3')
# 说明: EC2/ECS 实例自动使用 IAM 角色，无需显式提供密钥
```

**文档说明格式**:

```markdown
## AWS 配置

### 开发环境

使用本地凭证文件 `~/.aws/credentials`:
```

[default]
aws_access_key_id = AKIA...PLE
aws_secret_access_key = **\*\*\*\***

```

### 生产环境
使用 IAM 角色，无需配置密钥。
EC2 实例角色: `MyApp-S3-Access-Role`
```

---

### 示例 5: 私钥和证书脱敏

**场景**: HTTPS/SSH 配置

**❌ 不安全的代码**:

```python
# ❌ 硬编码私钥内容
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz...
全部私钥内容 (绝对禁止!)
-----END RSA PRIVATE KEY-----"""

def sign_data(data):
    key = RSA.import_key(PRIVATE_KEY)
    return key.sign(data)
```

**✅ 安全的代码**:

```python
# ✅ 从文件读取私钥
import os
from Crypto.PublicKey import RSA

PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/etc/ssl/private/app.key")

def sign_data(data):
    # 从安全位置读取私钥
    with open(PRIVATE_KEY_PATH, 'r') as f:
        key = RSA.import_key(f.read())
    return key.sign(data)

# 文档中的说明
"""
私钥文件配置:
- 路径: /etc/ssl/private/app.key
- 权限: 400 (仅所有者可读)
- 内容: [REDACTED] (2048位 RSA 私钥)
- 生成命令: openssl genrsa -out app.key 2048
"""
```

**证书配置示例** (Nginx):

```nginx
# ❌ 错误 - 文档中展示完整私钥路径和内容
ssl_certificate /etc/nginx/ssl/mycompany-cert.pem;
ssl_certificate_key /etc/nginx/ssl/mycompany-private.key;  # 内容: [展示完整私钥]

# ✅ 正确 - 只展示配置结构
ssl_certificate /path/to/certificate.pem;  # 证书文件
ssl_certificate_key /path/to/private.key;  # 私钥文件 [REDACTED]

# 说明:
# - 证书和私钥文件需要手动配置
# - 权限要求: 证书 644, 私钥 400
# - 私钥内容严格保密，不在文档中展示
```

---

## 🎯 常见敏感信息速查表

| 类型           | 识别特征                                 | 脱敏方式             | 文档中的写法                                   |
| -------------- | ---------------------------------------- | -------------------- | ---------------------------------------------- |
| **API 密钥**   | `API_KEY`, `SECRET_KEY`, `sk_`, `pk_`    | 保留前后 3 位        | `os.getenv("API_KEY")  # sk-abc...xyz`         |
| **数据库密码** | 连接字符串中的密码                       | 全部替换为`********` | `os.getenv("DB_PASSWORD")  # ********`         |
| **JWT Secret** | `JWT_SECRET`, `TOKEN_SECRET`             | 完全隐藏             | `process.env.JWT_SECRET  // ********`          |
| **OAuth 凭证** | `CLIENT_SECRET`, `GOCSPX-`               | 保留前缀+后缀        | `GOCSPX-abc...hij`                             |
| **云服务密钥** | `AWS_SECRET_ACCESS_KEY`, `ALIYUN_SECRET` | 完全隐藏             | `os.getenv("AWS_SECRET")  # ********`          |
| **私钥内容**   | `-----BEGIN PRIVATE KEY-----`            | `[REDACTED]`         | `文件路径 + [REDACTED]`                        |
| **数据库 URL** | `postgresql://user:pass@host`            | 密码部分脱敏         | `postgresql://user:********@db.example.com/db` |
| **真实域名**   | 生产环境域名                             | 替换为示例域名       | `db.example.com` 或 `${DB_HOST}`               |
| **真实 IP**    | 公网 IP 地址                             | 替换为内网 IP        | `192.168.1.x` 或 `${SERVER_IP}`                |
| **个人信息**   | 姓名、邮箱、电话                         | 使用占位符           | `user@example.com`, `138****0000`              |

---

## 🔍 AI 检测规则

**生成文档时，AI 应该检测以下模式并自动脱敏**:

```regex
# API 密钥模式
sk-[a-zA-Z0-9]{32,}          → 脱敏为 sk-abc...xyz
pk-[a-zA-Z0-9]{32,}          → 脱敏为 pk-abc...xyz

# JWT Token 模式
eyJ[a-zA-Z0-9_-]{100,}       → 脱敏为 eyJ...xyz

# 数据库连接字符串
://[^:]+:([^@]+)@            → 密码部分替换为 ********

# OAuth Client Secret
GOCSPX-[a-zA-Z0-9_-]{20,}    → 脱敏为 GOCSPX-abc...xyz

# AWS 密钥
AKIA[A-Z0-9]{16}             → 脱敏为 AKIA...PLE
```

**自动脱敏流程**:

1. **检测**: 扫描生成的文档内容
2. **匹配**: 使用正则表达式匹配敏感模式
3. **脱敏**: 应用对应的脱敏规则
4. **验证**: 确认无遗漏
5. **标注**: 在注释中说明配置来源

---

## 💡 环境变量处理

### 推荐做法

在文档中**始终使用环境变量引用**,而非硬编码:

✅ **推荐**:

```javascript
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
const dbHost = process.env.DB_HOST;
```

✅ **带脱敏示例的注释**:

```javascript
const apiKey = process.env.API_KEY; // sk-abc...xyz
const dbPassword = process.env.DB_PASSWORD; // ********
const dbHost = process.env.DB_HOST; // db.example.com
```

❌ **禁止**:

```javascript
const apiKey = "sk-1234567890abcdefghijklmn";
const dbPassword = "MyS3cr3tP@ssw0rd";
const dbHost = "db.mycompany.com";
```

### Python 示例

✅ **正确**:

```python
import os

API_KEY = os.getenv('API_KEY')  # sk-abc...xyz
DB_PASSWORD = os.getenv('DB_PASSWORD')  # ********
DB_HOST = os.getenv('DB_HOST')  # db.example.com
```

❌ **错误**:

```python
API_KEY = "sk-1234567890abcdefghijklmn"
DB_PASSWORD = "MyS3cr3tP@ssw0rd"
```

---

## ✅ 生成后自检清单

**每生成一个文档后,AI 必须自检以下项目**:

- [ ] 是否包含真实 API 密钥?
- [ ] 是否包含真实密码?
- [ ] 是否包含真实域名/IP?
- [ ] 是否包含个人身份信息?
- [ ] 所有敏感配置是否使用环境变量?
- [ ] 代码示例是否正确脱敏?
- [ ] 注释中的示例值是否已脱敏?

---

## 🚨 特殊情况处理

### 配置文件示例

当需要展示配置文件时:

✅ **正确**:

```yaml
# config.yaml
database:
  host: ${DB_HOST} # db.example.com
  password: ${DB_PASSWORD} # ********

api:
  key: ${API_KEY} # sk-abc...xyz
```

❌ **错误**:

```yaml
database:
  host: db-prod.mycompany.com
  password: MyS3cr3tP@ssw0rd
```

### 日志/错误信息

如果需要展示日志:

✅ **正确**:

```
Error: Failed to connect to db.example.com
API Key validation failed for key sk-abc...xyz
```

❌ **错误**:

```
Error: Failed to connect to db-prod.mycompany.com
API Key validation failed for key sk-1234567890abcdefghijklmn
```

---

## 🔗 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 主流程文档
- [项目类型规范](./project_types.md) - 不同项目的特殊安全考虑

---

**版本**: v3.0  
**路径**: `core/security_rules.md`
