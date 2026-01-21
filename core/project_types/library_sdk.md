---
title: 库/SDK 项目配置
summary: 定义库/SDK 项目（npm包/PyPI包/Go module/Rust crate）的推荐子文档清单、特殊关注点和核心代码模式。包括 API 设计、版本管理、打包配置等关键规范。
keywords: library | sdk | npm | pypi | package | api-design | versioning | typescript
scope: 库/SDK 项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 库/SDK 项目

> **适用场景**: npm 包 / PyPI 包 / Go module / Rust crate / Maven 库

---

## 🎯 适用平台

- **JavaScript/TypeScript**: npm / yarn / pnpm
- **Python**: PyPI / conda
- **Go**: Go modules
- **Rust**: crates.io
- **Java**: Maven Central / JCenter
- **Ruby**: RubyGems
- **.NET**: NuGet

---

## 📋 推荐子文档清单

| 优先级 | 文档名称             | 用途         |
| ------ | -------------------- | ------------ |
| 🔴 高  | `api_reference.md`   | API 文档     |
| 🔴 高  | `getting_started.md` | 快速开始     |
| 🔴 高  | `examples.md`        | 使用示例     |
| 🟡 中  | `migration_guide.md` | 版本迁移指南 |
| 🟡 中  | `contributing.md`    | 贡献指南     |
| 🟢 低  | `changelog.md`       | 变更日志     |

---

## 🔍 特殊关注点

### API 设计一致性

- 命名规范统一
- 参数顺序一致
- 返回值类型明确
- 错误处理统一

### 向后兼容性

- 遵循语义化版本（Semver）
- 废弃 API 提供迁移路径
- 主版本变更文档化

### 类型定义

- **TypeScript**: 提供 `.d.ts` 声明文件
- **Python**: 提供类型提示（Type Hints）
- **Go**: 导出类型和接口
- **Rust**: 完整的类型系统

### 打包配置

- **UMD**: 浏览器全局变量
- **ESM**: ES Modules（现代标准）
- **CJS**: CommonJS（Node.js）
- **Tree-shaking**: 支持按需引入

### 版本管理策略

- **Semver**: `MAJOR.MINOR.PATCH`
- **Changelog**: 记录所有变更
- **Git Tags**: 版本标签
- **Release Notes**: 发布说明

### 文档自动生成

- **JavaScript**: JSDoc / TypeDoc / API Extractor
- **Python**: Sphinx / MkDocs / pdoc
- **Go**: godoc
- **Rust**: rustdoc

---

## 💻 核心代码模式

### TypeScript 库结构

```typescript
// src/index.ts - 主入口
export { createClient } from './client'
export { type Config, type Options } from './types'
export * from './utils'

// src/client.ts
import type { Config } from './types'

export class Client {
  private config: Config

  constructor(config: Config) {
    this.config = config
  }

  async request<T>(endpoint: string): Promise<T> {
    // 实现
  }
}

export function createClient(config: Config): Client {
  return new Client(config)
}

// src/types.ts
export interface Config {
  apiKey: string
  baseURL?: string
  timeout?: number
}

export interface Options {
  retry?: boolean
  cache?: boolean
}
```

### package.json 配置

```json
{
  "name": "my-library",
  "version": "1.0.0",
  "description": "A sample library",
  "main": "./dist/index.js",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.js",
      "types": "./dist/utils.d.ts"
    }
  },
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "test": "vitest",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["library", "sdk"],
  "author": "Your Name",
  "license": "MIT",
  "devDependencies": {
    "tsup": "^8.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

### Python 库结构

```python
# src/my_library/__init__.py
from .client import Client, create_client
from .types import Config, Options

__version__ = "1.0.0"
__all__ = ["Client", "create_client", "Config", "Options"]

# src/my_library/client.py
from typing import TypeVar, Generic
from .types import Config

T = TypeVar('T')

class Client:
    def __init__(self, config: Config):
        self.config = config
    
    async def request(self, endpoint: str) -> dict:
        # 实现
        pass

def create_client(config: Config) -> Client:
    return Client(config)

# src/my_library/types.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    api_key: str
    base_url: Optional[str] = None
    timeout: Optional[int] = None

@dataclass
class Options:
    retry: bool = False
    cache: bool = False
```

### pyproject.toml 配置

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-library"
version = "1.0.0"
description = "A sample library"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
keywords = ["library", "sdk"]
authors = [
  {name = "Your Name", email = "you@example.com"}
]
classifiers = [
  "Development Status :: 4 - Beta",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
]
dependencies = [
  "httpx>=0.24.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "black>=23.0.0",
  "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/username/my-library"
Documentation = "https://my-library.readthedocs.io"
Repository = "https://github.com/username/my-library"
```

### Go Module 结构

```go
// client.go
package mylibrary

import "context"

type Config struct {
    APIKey  string
    BaseURL string
    Timeout int
}

type Client struct {
    config Config
}

func NewClient(config Config) *Client {
    return &Client{config: config}
}

func (c *Client) Request(ctx context.Context, endpoint string) (interface{}, error) {
    // 实现
    return nil, nil
}

// go.mod
module github.com/username/my-library

go 1.21

require (
    github.com/some/dependency v1.0.0
)
```

### 版本发布流程

```bash
# 1. 更新版本号
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0

# 2. 更新 CHANGELOG.md
# 3. 提交变更
git add .
git commit -m "chore: release v1.1.0"
git tag v1.1.0
git push origin main --tags

# 4. 发布到 npm
npm publish

# Python
python -m build
python -m twine upload dist/*

# Go (通过 Git Tag)
git tag v1.1.0
git push origin v1.1.0
```

---

## 📝 主文档特殊章节

### 安装说明

```markdown
## 📦 安装

### npm
\`\`\`bash
npm install my-library
# 或
yarn add my-library
# 或
pnpm add my-library
\`\`\`

### Python
\`\`\`bash
pip install my-library
# 或
poetry add my-library
\`\`\`

### Go
\`\`\`bash
go get github.com/username/my-library
\`\`\`
```

### 快速开始

```markdown
## 🚀 快速开始

\`\`\`typescript
import { createClient } from 'my-library'

const client = createClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.example.com'
})

const result = await client.request('/endpoint')
\`\`\`
```

### 版本兼容性

```markdown
## 🔄 版本兼容

| 版本 | Node.js | TypeScript | Python |
| ---- | ------- | ---------- | ------ |
| 2.x  | >=14    | >=4.5      | >=3.8  |
| 1.x  | >=12    | >=4.0      | >=3.7  |
```

---

## ⚠️ 常见问题

### 问题 1: 破坏性变更未文档化

**解决方案**: 使用 CHANGELOG.md 和迁移指南

```markdown
## [2.0.0] - 2024-01-01

### Breaking Changes
- `createClient()` now requires `apiKey` parameter
- Removed deprecated `oldMethod()`

### Migration Guide
\`\`\`typescript
// v1.x
const client = createClient()
client.setApiKey('key')

// v2.x
const client = createClient({ apiKey: 'key' })
\`\`\`
```

### 问题 2: 类型定义不完整

**解决方案**: 确保所有导出都有类型定义

```typescript
// ❌ 错误
export function createClient(config: any) {
  return new Client(config)
}

// ✅ 正确
export function createClient(config: Config): Client {
  return new Client(config)
}
```

### 问题 3: Tree-shaking 不生效

**解决方案**: 使用 ESM 格式和 sideEffects 配置

```json
{
  "type": "module",
  "sideEffects": false,
  "exports": {
    ".": {
      "import": "./dist/index.mjs"
    }
  }
}
```

---

## 🎯 检查清单

生成库/SDK 项目文档前，确认：

- [ ] 已识别目标平台（npm/PyPI/Go/Rust 等）
- [ ] 已确定打包格式（ESM/CJS/UMD）
- [ ] 已确定是否提供类型定义
- [ ] 已确定版本管理策略（Semver）
- [ ] 已确定文档生成工具（TypeDoc/Sphinx 等）
- [ ] 已确定测试框架（Vitest/pytest 等）
- [ ] 已确定发布流程
- [ ] 已准备 README 和 CHANGELOG
- [ ] 已确定许可证（MIT/Apache/GPL 等）

---

**版本**: v3.0  
**路径**: `core/project_types/library_sdk.md`  
**最后更新**: 2026-01-21
