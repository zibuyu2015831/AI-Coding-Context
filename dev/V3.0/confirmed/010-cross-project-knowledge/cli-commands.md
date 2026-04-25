# 010 - 跨项目知识复用：CLI 命令参考

**文档类型**: CLI 命令参考文档
**相关优化点**: 010-cross-project-knowledge.md
**创建日期**: 2026-04-13
**最后更新**: 2026-04-13
**状态**: 🟢 已确认

---

## 📋 概述

本文档详细描述了跨项目知识复用优化点的命令行接口（CLI）。这些命令提供了对知识库的完整管理，包括配置、启用/禁用、更新、状态查询和策略调整。

## 🚀 命令结构

### 命令命名规范

所有知识库管理命令遵循统一的命名规范：

```bash
# 通用格式
aicc knowledge <command> [options]

# 简写（可选）
aicc k <command> [options]
```

### 执行方法

**Node.js 版本（推荐）：**
```bash
node tools/js/knowledge_cli.js <command> [options]

# 或使用 npm 脚本（需要在 package.json 中配置）
npm run aicc:knowledge -- <command> [options]
```

**Python 版本：**
```bash
python tools/py/knowledge_cli.py <command> [options]
```

---

## 📝 命令参考

### 1. 查看知识库状态

#### 命令：`status`

**功能**: 显示当前知识库的配置和使用状态

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js status

# Python 版本
python tools/py/knowledge_cli.py status

# 预期输出示例
📚 知识库配置状态
  本地知识库: ✅ dev_docs/knowledge/
  共享知识库: ❌ 未配置
  匹配策略: local-first
```

**详细参数**:
- 无额外参数

---

### 2. 配置共享知识库

#### 命令：`config`

**功能**: 配置或更新共享知识库的 Git 仓库地址

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js config --shared https://github.com/your-org/shared-knowledge.git

# Python 版本
python tools/py/knowledge_cli.py config --shared https://github.com/your-org/shared-knowledge.git

# 预期输出示例
✅ 共享知识库配置成功！
  仓库地址: https://github.com/your-org/shared-knowledge.git
  缓存路径: .aicc-cache/shared-knowledge/
  匹配策略: local-first
```

**详细参数**:
- `--shared <url>` (必需): 共享知识库的 Git 仓库地址
- `--branch <name>` (可选): 指定分支，默认使用 main/master
- `--depth <number>` (可选): 克隆深度，用于优化性能，默认完整克隆
- `--force` (可选): 强制重新配置，覆盖现有设置

**配置流程**:
1. 验证 Git 地址的有效性
2. 检查是否已在 .gitignore 中排除共享知识库缓存目录
3. 克隆或更新共享仓库到本地缓存
4. 显示迁移选项（如果有本地知识）
5. 保存配置到 .aicc/config.yml

---

### 3. 启用共享知识库

#### 命令：`enable-shared`

**功能**: 启用已配置的共享知识库

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js enable-shared

# Python 版本
python tools/py/knowledge_cli.py enable-shared

# 预期输出示例
✅ 共享知识库已启用
```

**详细参数**:
- 无额外参数

**前提条件**:
- 共享知识库必须已通过 `config` 命令配置

---

### 4. 禁用共享知识库

#### 命令：`disable-shared`

**功能**: 禁用共享知识库，但保留配置信息

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js disable-shared

# Python 版本
python tools/py/knowledge_cli.py disable-shared

# 预期输出示例
⚠️ 共享知识库已禁用
```

**详细参数**:
- 无额外参数

**注意**: 禁用共享知识库不会删除本地缓存，但在文档生成时将不再使用共享知识。

---

### 5. 更新共享知识库

#### 命令：`update-shared`

**功能**: 从远程仓库更新共享知识库内容

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js update-shared

# Python 版本
python tools/py/knowledge_cli.py update-shared

# 预期输出示例
✅ 共享知识库已更新
  更新时间: 2026-04-13 12:34:56
```

**详细参数**:
- `--force` (可选): 强制更新，忽略本地变更
- `--no-dirty-check` (可选): 跳过工作区脏检查

**更新流程**:
1. 检查本地缓存是否有未提交的变更
2. 执行 Git pull 操作
3. 更新配置中的 last_updated 时间戳
4. 重新计算知识匹配索引（按需）

---

### 6. 配置知识匹配策略

#### 命令：`strategy`

**功能**: 配置知识匹配和合并策略

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js strategy --mode shared-first

# Python 版本
python tools/py/knowledge_cli.py strategy --mode shared-first

# 预期输出示例
✅ 知识匹配策略已切换为: shared-first
```

**详细参数**:
- `--mode <strategy>` (必需): 匹配策略，可选值：
  - `local-first`: 本地知识优先（默认）
  - `shared-first`: 共享知识优先
  - `hybrid`: 混合模式，根据质量和相关性综合选择

---

### 7. 显示帮助信息

#### 命令：`help` 或 `--help`

**功能**: 显示所有可用命令和参数的帮助信息

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js --help

# 或查看特定命令的帮助
node tools/js/knowledge_cli.js config --help

# Python 版本
python tools/py/knowledge_cli.py --help
python tools/py/knowledge_cli.py config --help
```

**输出格式示例**:
```
📚 知识库管理 CLI 工具

用法: aicc knowledge <command> [options]

命令:
  status              查看知识库配置状态
  config              配置共享知识库
  enable-shared       启用共享知识库
  disable-shared      禁用共享知识库
  update-shared       更新共享知识库
  strategy            配置知识匹配策略
  help                显示帮助信息

常用选项:
  --help              显示此帮助信息
  --version           显示版本信息

更多详细信息，请使用: aicc knowledge <command> --help
```

---

## 🔧 高级功能

### 1. 知识库初始化与发布

#### 命令：`init`

**功能**: 初始化本地 knowledge 目录为共享知识库，创建标准结构和配置文件

**实现状态**: 🟡 阶段 2 实现

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js init --as-shared

# Python 版本
python tools/py/knowledge_cli.py init --as-shared
```

**详细参数**:
- `--as-shared`: 标记为共享知识库（必填）
- `--force`: 强制初始化，覆盖现有配置
- `--template <name>`: 使用特定模板初始化（可选，默认使用标准模板）
- `--dry-run`: 模拟初始化过程，不实际执行

**初始化流程**:
1. 检查本地 knowledge 目录结构是否符合标准
2. 创建 .aicc/ 配置目录和元数据文件
3. 初始化 Git 仓库（git init）
4. 配置标准的 .gitignore 文件
5. 验证并修复目录结构问题

---

#### 命令：`publish`

**功能**: 将本地共享知识库发布到云端 Git 仓库

**实现状态**: 🟡 阶段 2 实现

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js publish --remote https://github.com/your-org/shared-knowledge.git --branch main

# Python 版本
python tools/py/knowledge_cli.py publish --remote https://github.com/your-org/shared-knowledge.git --branch main
```

**详细参数**:
- `--remote <url>`: 远程仓库地址（必填）
- `--branch <name>`: 分支名称（可选，默认 main）
- `--message <msg>`: 提交信息（可选）
- `--force`: 强制推送，覆盖远程仓库
- `--dry-run`: 模拟发布过程，不实际执行

**发布流程**:
1. 检查本地仓库状态，确保所有更改已提交
2. 添加远程仓库地址（git remote add）
3. 首次发布时设置 upstream 分支（git push -u）
4. 后续发布使用增量更新（git push）
5. 验证远程仓库内容与本地一致

---

### 2. 知识库迁移工具

#### 命令：`migrate`

**功能**: 管理知识从本地到共享知识库的迁移

**实现状态**: 🟡 阶段 2 实现

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js migrate --list
node tools/js/knowledge_cli.js migrate --select <id>

# Python 版本
python tools/py/knowledge_cli.py migrate --list
python tools/py/knowledge_cli.py migrate --select <id>
```

**详细参数**:
- `--list`: 列出可迁移的本地知识条目
- `--select <id>`: 选择特定条目进行迁移
- `--all`: 迁移所有可迁移的知识
- `--dry-run`: 模拟迁移过程，不实际执行
- `--force`: 强制迁移，覆盖已存在的知识

---

### 3. 知识质量评估

#### 命令：`quality`

**功能**: 评估知识库的质量和完整性

**实现状态**: 🟡 阶段 2 实现

**使用方法**:
```bash
# Node.js 版本
node tools/js/knowledge_cli.js quality --local
node tools/js/knowledge_cli.js quality --shared

# Python 版本
python tools/py/knowledge_cli.py quality --local
python tools/py/knowledge_cli.py quality --shared
```

**详细参数**:
- `--local`: 评估本地知识库
- `--shared`: 评估共享知识库
- `--report <format>`: 输出格式，可选 html 或 markdown（默认文本）
- `--threshold <score>`: 质量阈值，低于该分数的知识将被标记

---

## 🎯 使用场景示例

### 场景 1：首次配置共享知识库

```bash
# 1. 查看当前状态
node tools/js/knowledge_cli.js status

# 2. 配置共享知识库
node tools/js/knowledge_cli.js config --shared https://github.com/your-org/shared-knowledge.git

# 3. 启用共享知识库（可选，配置后默认启用）
node tools/js/knowledge_cli.js enable-shared

# 4. 验证配置
node tools/js/knowledge_cli.js status
```

### 场景 2：团队协作中的知识库管理

```bash
# 项目负责人配置共享知识库
node tools/js/knowledge_cli.js config --shared https://github.com/your-org/shared-knowledge.git

# 团队成员克隆项目后
npm install  # 安装依赖
node tools/js/knowledge_cli.js update-shared  # 更新共享知识库

# 正常使用
node tools/js/project_scanner.js --exclude-standard
```

### 场景 3：共享知识库更新流程

```bash
# 定期更新共享知识库
node tools/js/knowledge_cli.js update-shared

# 查看更新结果
node tools/js/knowledge_cli.js status
```

### 场景 4：将本地项目知识转化为共享知识库

```bash
# 1. 确保在已使用 AICC 框架的项目中
cd your-project

# 2. 查看当前状态
node tools/js/knowledge_cli.js status

# 3. 初始化本地 knowledge 为共享知识库
node tools/js/knowledge_cli.js init --as-shared

# 4. 验证初始化结果
node tools/js/knowledge_cli.js status

# 5. 发布到云端仓库（假设已创建空仓库）
node tools/js/knowledge_cli.js publish --remote https://github.com/your-org/shared-knowledge.git --branch main

# 6. 验证发布成功
node tools/js/knowledge_cli.js status

# 7. 团队成员可以通过 config 命令使用该知识库
node tools/js/knowledge_cli.js config --shared https://github.com/your-org/shared-knowledge.git
```

**场景说明**:
- 项目 A 拥有丰富的知识积累，想分享给项目 B 使用。项目 B 可以直接 config 共享知识库，复用项目 A 的知识。

---

## 🛠️ 开发和扩展

### 1. CLI 实现架构

**核心组件**：
```
knowledge_cli.js
├── 命令解析模块
│   ├── parseArgs()        # 解析命令行参数
│   ├── validateArgs()     # 验证参数有效性
│   └── helpGenerator()    # 生成帮助信息
│
├── 命令处理模块
│   ├── StatusCommand()    # 处理 status 命令
│   ├── ConfigCommand()    # 处理 config 命令
│   ├── UpdateCommand()    # 处理 update-shared 命令
│   └── StrategyCommand()  # 处理 strategy 命令
│
├── 知识库管理模块
│   ├── KnowledgeConfigManager()
│   └── KnowledgePathManager()
│
└── 工具集成
    ├── Git操作       (git_clone(), git_pull(), git_add())
    └── 交互提示      (askUser(), showMigrationOptions())
```

### 2. 扩展命令开发

**步骤**：
1. 在 `commands/` 目录中创建新命令类
2. 实现 `run()` 方法处理命令逻辑
3. 在 `parseArgs()` 中添加参数解析
4. 在 `helpGenerator()` 中添加帮助信息
5. 更新文档

### 3. 与其他工具的集成

**知识库管理 CLI** 与其他 AICC 工具的集成：

```javascript
// knowledge_cli.js
const ProjectScanner = require('./project_scanner');
const GitInspector = require('./git_inspector');
const SummaryExtractor = require('./summary_extractor');

class KnowledgeCLI {
  async run() {
    // 使用 ProjectScanner 扫描项目结构
    const scanner = new ProjectScanner();
    const projectStructure = await scanner.scan();

    // 使用 GitInspector 检查状态
    const gitInspector = new GitInspector();
    const gitStatus = await gitInspector.inspect();

    // 使用 SummaryExtractor 提取元数据
    const extractor = new SummaryExtractor();
    const metadata = await extractor.extract('dev_docs/');

    // 知识库管理逻辑...
  }
}
```

---

## 📋 兼容性说明

### 1. 系统要求

**Node.js 版本**：
- 最低版本：14.0.0
- 推荐版本：18.0.0+
- 依赖：无额外第三方依赖，使用 Node.js 标准库

**Python 版本**：
- 最低版本：3.6.0
- 推荐版本：3.10.0+
- 依赖：无额外第三方依赖，使用 Python 标准库

### 2. 平台支持

- **Windows**：✅ 完整支持
- **macOS**：✅ 完整支持
- **Linux**：✅ 完整支持
- **WSL（Windows Subsystem for Linux）**：✅ 完整支持

---

## 🔍 故障排除

### 1. 常见错误和解决方法

#### 错误：无法连接到 Git 仓库

```bash
# 错误信息
❌ 无法连接到 Git 仓库: https://github.com/your-org/shared-knowledge.git
  错误: getaddrinfo ENOTFOUND github.com

# 解决方法
1. 检查网络连接
2. 验证 Git 地址是否正确
3. 尝试使用 HTTPS 替代 SSH（或相反）
4. 检查防火墙和代理设置
```

#### 错误：共享仓库缓存目录未被忽略

```bash
# 错误信息
⚠️ 共享知识库缓存目录未在 .gitignore 中列出
  建议添加: .aicc-cache/

# 解决方法
# 1. 手动添加到 .gitignore
echo ".aicc-cache/" >> .gitignore

# 2. 使用 CLI 命令自动添加
node tools/js/knowledge_cli.js config --shared https://github.com/your-org/shared-knowledge.git --force
```

#### 错误：本地知识库路径无效

```bash
# 错误信息
❌ 本地知识库路径无效: dev_docs/knowledge/
  目录不存在

# 解决方法
1. 确保已初始化 AICC 文档体系
2. 运行项目扫描：node tools/js/project_scanner.js --exclude-standard
3. 或手动创建目录：mkdir -p dev_docs/knowledge
```

---

## 📚 相关文档

- [010 - 跨项目知识复用主文档](./010-cross-project-knowledge.md)
- [知识仓库架构设计](./architecture-design.md)
- [框架自进化系统](./self-evolution-system.md)
- [AICC 工具库开发规范](../../../../tools/README.md)

---

## 📝 更新记录

### v1.0.0 (2026-04-13)

**新增功能**：
- 首次发布知识库管理 CLI 文档
- 包含核心命令：status、config、enable-shared、disable-shared、update-shared、strategy
- 提供完整的使用场景示例和故障排除指南

**设计决策**：
- 采用分层架构设计，易于扩展
- 遵循框架的工具开发规范（零第三方依赖）
- 支持 Node.js 和 Python 双版本实现

---

**状态图例**：
- 🟢 已实现
- 🟡 阶段 2 实现
- 🔴 已废弃

**最后更新**：2026-04-15