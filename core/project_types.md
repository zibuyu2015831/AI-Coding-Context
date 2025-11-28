# 项目类型适配指南

> **用途**: 指导如何为不同类型的项目生成合适的文档体系  
> **版本**: v1.0  
> **最后更新**: 2025-11-27

---

## 📋 概述

本指南覆盖 11 种项目类型，支持 25+主流框架，每种类型都提供：

- 推荐的子文档清单
- 特殊关注点
- AI 分析重点
- 代码模式示例

---

## 🌐 Web 前端项目

### 适用框架

Vue.js / React / Angular / Svelte / Solid.js

### 推荐子文档清单

| 优先级 | 文档名称                  | 用途                            |
| ------ | ------------------------- | ------------------------------- |
| 🔴 高  | `api_layer.md`            | API 调用规范                    |
| 🔴 高  | `state_management.md`     | 状态管理（Pinia/Redux/Zustand） |
| 🔴 高  | `routing_guide.md`        | 路由与权限                      |
| 🟡 中  | `component_guide.md`      | 组件开发规范                    |
| 🟡 中  | `styling_guide.md`        | CSS/样式方案                    |
| 🟡 中  | `form_validation.md`      | 表单验证                        |
| 🟢 低  | `internationalization.md` | 国际化方案                      |

### 特殊关注点

- UI 组件库使用（Element Plus/Ant Design/MUI 等）
- CSS 方案（Tailwind/UnoCSS/CSS Modules）
- 构建工具配置（Vite/Webpack/Rollup）
- SEO 优化策略（如使用 SSR）

### 核心代码模式

```typescript
// API调用模式
import { api } from '@/api'
const { data, loading, error } = await api.get('/endpoint')

// 组件开发模式
<script setup lang="ts">
// Props, Emits, State, Methods
</script>

// 状态管理模式
const store = useStore()
const { state, actions } = storeToRefs(store)
```

---

## 🔧 后端 API 项目

### 适用框架

**Node.js**: Express / Fastify / NestJS / Koa  
**Python**: Flask / FastAPI / Django  
**Java**: Spring Boot / Quarkus  
**Go**: Gin / Echo / Fiber  
**Ruby**: Rails / Sinatra  
**PHP**: Laravel / Symfony  
**.NET**: ASP.NET Core  
**Rust**: Actix-web / Rocket

### 推荐子文档清单

| 优先级 | 文档名称                      | 用途                 |
| ------ | ----------------------------- | -------------------- |
| 🔴 高  | `api_design.md`               | RESTful/GraphQL 设计 |
| 🔴 高  | `database_schema.md`          | 数据库模型与关系     |
| 🔴 高  | `authentication.md`           | 认证与授权           |
| 🟡 中  | `middleware_guide.md`         | 中间件使用           |
| 🟡 中  | `error_handling.md`           | 错误处理与日志       |
| 🟡 中  | `testing_guide.md`            | 单元/集成测试        |
| 🟢 低  | `performance_optimization.md` | 性能优化策略         |

### 特殊关注点

- ORM/ODM 使用
  - Node.js: Prisma / TypeORM / Mongoose / Sequelize
  - Python: SQLAlchemy / Django ORM / Tortoise ORM
  - Java: Hibernate / JPA / MyBatis
  - Ruby: ActiveRecord
  - PHP: Eloquent / Doctrine
- 数据验证
  - Node.js: Zod / Joi / class-validator
  - Python: Pydantic / Marshmallow
  - Java: Bean Validation
  - Go: validator
- 缓存策略（Redis/Memcached）
- 消息队列（RabbitMQ/Kafka/NATS）
- 日志系统（Winston/Pino/structlog/Logback）

### 核心代码模式

```typescript
// 路由定义
router.post('/users', authenticate, validate(schema), userController.create)

// 数据库模型
const User = prisma.defineModel({...})

// 中间件
const authMiddleware = async (req, res, next) => {...}
```

---

## 📜 脚本项目（新增）

### 适用场景

Python 脚本 / Shell 脚本 / 数据处理 / 自动化任务

### 推荐子文档清单

| 优先级 | 文档名称            | 用途         |
| ------ | ------------------- | ------------ |
| 🔴 高  | `script_usage.md`   | 脚本使用说明 |
| 🔴 高  | `configuration.md`  | 配置文件说明 |
| 🟡 中  | `data_flow.md`      | 数据流程图   |
| 🟡 中  | `error_handling.md` | 异常处理机制 |
| 🟢 低  | `scheduling.md`     | 定时任务配置 |

### 特殊关注点

- 环境依赖（Python 虚拟环境/系统依赖）
- 配置管理（环境变量/配置文件）
- 日志输出（位置/格式/轮转）
- 错误恢复机制
- 定时任务设置（cron/schedule）

### 主文档特殊章节

````markdown
## 🚀 快速开始

### 环境准备

```bash
# Python项目
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Shell脚本
chmod +x script.sh
```
````

### 运行示例

```bash
# 基本运行
python main.py --config config.yaml

# 定时运行
0 2 * * * /path/to/script.py
```

## 📁 关键文件说明

- `config.yaml` - 配置文件
- `requirements.txt` - Python 依赖
- `logs/` - 日志目录
- `data/` - 数据目录

````

---

## 🔨 CLI工具项目（新增）

### 适用场景
命令行工具 / 开发者工具 / 运维工具

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `cli_usage.md` | 命令使用手册 |
| 🔴 高 | `installation.md` | 安装与配置 |
| 🟡 中 | `plugin_system.md` | 插件系统（如有） |
| 🟡 中 | `configuration.md` | 配置文件说明 |
| 🟢 低 | `contributing.md` | 贡献指南 |

### 特殊关注点
- 命令结构（commander/yargs/click/cobra）
- 参数验证
- 交互式提示（inquirer/questionary）
- 输出格式（表格/JSON/进度条）
- 错误提示友好性
- 自动补全支持

### 核心代码模式
```typescript
// 命令定义
program
  .command('init')
  .option('-t, --template <type>')
  .action(async (options) => {
    // 实现
  })

// 交互式输入
const answers = await inquirer.prompt([...])

// 友好输出
console.log(chalk.green('✓ Success!'))
spinner.start('Processing...')
````

---

## 📦 库/SDK 项目（新增）

### 适用场景

npm 包 / PyPI 包 / Go module / Rust crate

### 推荐子文档清单

| 优先级 | 文档名称             | 用途         |
| ------ | -------------------- | ------------ |
| 🔴 高  | `api_reference.md`   | API 文档     |
| 🔴 高  | `getting_started.md` | 快速开始     |
| 🔴 高  | `examples.md`        | 使用示例     |
| 🟡 中  | `migration_guide.md` | 版本迁移指南 |
| 🟡 中  | `contributing.md`    | 贡献指南     |
| 🟢 低  | `changelog.md`       | 变更日志     |

### 特殊关注点

- API 设计一致性
- 向后兼容性
- 类型定义（TypeScript 声明文件）
- 打包配置（UMD/ESM/CJS）
- 版本管理策略（semver）
- 文档自动生成（JSDoc/typedoc/Sphinx）

### 主文档特殊章节

````markdown
## 📦 安装

```bash
npm install package-name
# 或
pip install package-name
```
````

## 🚀 快速开始

```typescript
import { feature } from "package-name";

const result = feature({ option: value });
```

## 📖 API 文档

详见 [API Reference](./api_reference.md)

## 🔄 版本兼容

| 版本 | Node.js | TypeScript |
| ---- | ------- | ---------- |
| 2.x  | >=14    | >=4.5      |
| 1.x  | >=12    | >=4.0      |

````

---

## 🎲 全栈项目

### 适用框架

Next.js / Nuxt / Remix / SvelteKit / Astro / Qwik

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `architecture_overview.md` | 前后端架构 |
| 🔴 高 | `api_layer.md` | API层（前端） |
| 🔴 高 | `data_fetching.md` | 数据获取策略 |
| 🟡 中 | `database_schema.md` | 数据库设计 |
| 🟡 中 | `deployment_guide.md` | 部署流程 |
| 🟡 中 | `testing_guide.md` | E2E测试 |

### 特殊关注点
- SSR/SSG/ISR策略
- API Routes设计
- 数据获取模式（getServerSideProps等）
- 认证流程（NextAuth等）
- Monorepo管理（Turborepo/Nx）

---

## 📲 移动应用项目

### 适用框架

React Native / Flutter / Ionic / NativeScript
**原生**: SwiftUI (iOS) / Jetpack Compose (Android)

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `platform_specific.md` | 平台特定代码 |
| 🔴 高 | `navigation.md` | 导航结构 |
| 🔴 高 | `native_modules.md` | 原生模块 |
| 🟡 中 | `state_management.md` | 状态管理 |
| 🟡 中 | `build_release.md` | 构建与发布 |
| 🟡 中 | `testing_guide.md` | 测试策略 |

### 特殊关注点
- 原生依赖管理（CocoaPods/Gradle）
- 热更新方案（CodePush）
- 性能优化（列表渲染/图片优化）
- 平台差异处理
- 打包签名配置

---

## 🖥️ 桌面应用项目

### 适用框架
Electron / Tauri / Qt

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `architecture.md` | 主进程/渲染进程 |
| 🔴 高 | `ipc_communication.md` | 进程间通信 |
| 🟡 中 | `native_integration.md` | 系统集成 |
| 🟡 中 | `auto_update.md` | 自动更新机制 |
| 🟡 中 | `packaging.md` | 打包与分发 |

---

## ☁️ Serverless项目（新增）

### 适用平台
AWS Lambda / Azure Functions / Google Cloud Functions / Vercel/Netlify Functions

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `function_structure.md` | 函数组织结构 |
| 🔴 高 | `deployment.md` | 部署配置 |
| 🟡 中 | `environment_vars.md` | 环境变量管理 |
| 🟡 中 | `cold_start_optimization.md` | 冷启动优化 |
| 🟡 中 | `monitoring.md` | 监控与日志 |

### 特殊关注点
- 函数触发器配置
- 权限设置（IAM/RBAC）
- 资源限制（内存/超时）
- 冷启动优化
- 成本优化策略

---

## 🐳 容器化项目

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `dockerfile_guide.md` | Dockerfile说明 |
| 🔴 高 | `docker_compose.md` | 本地开发环境 |
| 🟡 中 | `kubernetes.md` | K8s部署（如适用） |
| 🟡 中 | `ci_cd.md` | CI/CD流程 |

---

## 📊 数据科学项目（新增）

### 适用场景

Jupyter Notebook / 数据分析 / 机器学习 / 深度学习

**常用框架**:
- **数据处理**: Pandas / NumPy / Polars
- **机器学习**: Scikit-learn / XGBoost / LightGBM
- **深度学习**: TensorFlow / PyTorch / JAX
- **可视化**: Matplotlib / Seaborn / Plotly

### 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `data_pipeline.md` | 数据处理流程 |
| 🔴 高 | `model_documentation.md` | 模型文档 |
| 🟡 中 | `experiments.md` | 实验记录 |
| 🟡 中 | `environment_setup.md` | 环境配置 |
| 🟢 低 | `visualization.md` | 可视化说明 |

### 特殊关注点
- 数据来源与格式（CSV/Parquet/HDF5）
- 特征工程说明
- 模型参数调优（网格搜索/贝叶斯优化）
- 实验结果记录（MLflow/Weights & Biases）
- Notebook组织结构
- 依赖管理（conda/poetry/pip-tools）
- GPU环境配置（CUDA/cuDNN）
- 模型版本管理
- 数据版本控制（DVC）

---

## 🔄 选择指南

### 快速决策树

```mermaid
graph TD
    A[项目类型?] --> B{用户界面?}
    B -->|是| C{运行环境?}
    C -->|浏览器| D[Web前端]
    C -->|移动设备| E[移动应用]
    C -->|桌面| F[桌面应用]

    B -->|否| G{提供API?}
    G -->|是| H[后端API]
    G -->|否| I{用途?}

    I -->|工具| J[CLI工具]
    I -->|库| K[库/SDK]
    I -->|分析| L[数据科学]
    I -->|自动化| M[脚本项目]
````

### 混合项目

如果项目包含多个类型（如全栈+移动端），建议：

1. 在主文档中说明架构组成
2. 为每个部分创建独立的子文档集
3. 建立清晰的模块划分

---

## 📝 使用建议

1. **先确定项目类型** - 使用决策树
2. **选择对应的文档清单** - 从高优先级开始
3. **根据项目特点调整** - 增删文档
4. **保持文档同步** - 代码变更时更新

---

## 🎯 总结

不同项目类型有不同的关注点，但核心原则相同：

- ✅ 基于实际代码生成
- ✅ 提供清晰的使用指南
- ✅ 包含实用的代码示例
- ✅ 保持文档新鲜度

---

## 🔀 混合项目类型处理规范 (v2.2 新增)

> **上级文档**: [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md)

### 定义澄清

**平级混合** (❌ 不支持):

- 前端和后端代码混在同一目录层级
- 例如: 根目录同时有 `package.json` 和 `requirements.txt`,且代码未分离
- 无明确的目录分离

**分层混合** (✅ 支持):

- 代码按模块/功能清晰分层
- 例如: Monorepo 结构 (`packages/frontend`, `packages/backend`)
- 有明确的目录分离

### 判断流程

```mermaid
graph TD
    A[检测到多种项目类型特征] --> B{代码是否在不同目录?}
    B -->|是| C{是Monorepo结构?}
    B -->|否| D[平级混合 - 不支持]

    C -->|是| E[分层混合 - 支持]
    C -->|否| F{各部分独立可分?}

    F -->|是| G[建议: 分别生成文档]
    F -->|否| D

    E --> H[参考AI_ENTRY_POINT场景2]
    G --> I[让用户选择主要部分]
    D --> J[提示用户重构或选择]
```

### 处理策略

#### 如检测到平级混合

**输出模板**:

```markdown
❌ 检测到平级混合项目类型:

- 前端特征: package.json
- 后端特征: requirements.txt
- 位置: 都在根目录,代码未分离

🛑 **框架限制**: 本框架不支持平级混合项目类型。

💡 **建议**:

1. **重构项目结构** (推荐):
```

project/
├── frontend/ # 前端代码
│ └── package.json
├── backend/ # 后端代码
│ └── requirements.txt
└── README.md

```
重构后可为每个部分分别生成文档。

2. **选择主要部分**:
如果一部分是主要的,另一部分是辅助的,
请告诉我您希望为哪部分生成文档?

请确认您希望采用哪种方式?
```

**暂停执行,等待用户选择**

#### 如检测到分层混合(Monorepo)

**输出模板**:

```markdown
✅ 检测到分层混合(Monorepo)结构

📦 子项目检测:

- packages/frontend (Vue 3)
- packages/backend (Node.js + Express)
- packages/shared (TypeScript 工具库)

💡 **建议策略**: 全局文档策略
理由: 可以在主文档中说明整体架构,
在子目录中添加各自的详细说明。

是否采用此策略? (是/否/选择其他)
```

**参考**: AI_ENTRY_POINT.md 中的"场景 2: Monorepo 项目"

---

**版本**: v2.2  
**路径**: `core/project_types.md`
