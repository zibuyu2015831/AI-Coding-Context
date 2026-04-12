# 实用脚本库 (Utility Script Library)

本目录包含了一系列标准化的实用脚本，旨在帮助 AI 代理高效、安全地分析和操作项目。

## 📂 目录结构

```
tools/
├── py/                 # Python 实现 (首选)
├── js/                 # Node.js 实现 (备选)
├── fallback/           # 降级命令文档 (当无运行时环境时使用)
└── README.md           # 本文档
```

## 🛠️ 工具清单

所有工具均提供 Python 和 Node.js 双版本，功能保持一致。

| 工具名称                  | 功能描述               | 典型用途                                        |
| :------------------------ | :--------------------- | :---------------------------------------------- |
| `project_scanner`         | 智能扫描项目结构 ⭐    | 自适应输出策略，重要文件优先，Token 优化 60-80% |
| `file_reader`             | 安全读取文件内容       | 读取大文件、处理编码、检测二进制文件            |
| `content_searcher`        | 高效搜索内容 (类 grep) | 查找代码引用、TODO、特定字符串                  |
| `file_finder`             | 查找文件 (类 find)     | 根据文件名模式查找文件                          |
| `env_diagnosis`           | 环境诊断               | 检查 Python/Node.js 版本及可用性                |
| `git_inspector`           | Git 信息检查           | 获取当前分支、变更状态                          |
| `timestamp_analyzer`      | 文件时间戳采集         | 供 AI 分析文档健康度，判断文档是否过期          |
| `git_diff_analyzer`       | Git 差异分析           | 供 AI 判断哪些文档需要更新                      |
| `summary_extractor`       | 文档摘要提取           | 提取文档 YAML Frontmatter 摘要                  |
| `summary_validator`       | 摘要格式验证           | 验证摘要格式、必填字段和关联文件存在性          |
| `summary_related_checker` | 关联文档检查           | 检测代码变更影响的文档（基于 related_files）    |
| `summary_index_generator` | 摘要索引生成           | 生成文档摘要索引页（暂不启用）                  |
| `git_safety`              | Git 安全检查           | 检查保护分支、验证危险命令、建议分支名          |
| `commit_parser`           | Commit 解析            | 解析结构化/传统 commit，提取 WHAT/WHY/HOW       |
| `commit_quality_scorer`   | Commit 质量评分        | 5 维度评分，生成改进建议                        |
| `commit_aggregator`       | Commit 聚合            | 同类 commit 聚合，Token 优化（减少 85%+）       |
| `commit_template_cli`     | Commit 模板            | 交互式生成结构化 commit message                 |
| `commit_integrity_validator` | Commit 诚信验证        | 对比提议信息与物理变更，输出诚信分 (0-100)      |
| `install_hooks`           | Git Hooks 安装         | 安装/卸载 pre-commit hook，支持备份恢复         |
| `why_tool`                | 架构探针检索 (ADR)     | 根据隐性 `@architecture` 注解或源码全局检索对应技术决策理由 |
| `aac_validator`           | 架构即代码验证 (AaC)   | 本地提取并校验代码层面是否违背了最新活跃决策文档 (ADR) 的预埋断言 |

## 🚀 使用指南

### Python 版本 (推荐)

```bash
python tools/py/project_scanner.py --max-files 1000
```

### Node.js 版本

```bash
node tools/js/project_scanner.js --max-files 1000
```

## 🚫 项目扫描工具的排除机制

### 自动排除机制

项目扫描工具会自动排除以下内容：

1. **`.gitignore` 文件中的所有模式**

   - 工具会自动读取项目根目录的 `.gitignore` 文件
   - 所有 gitignore 规则都会被尊重

2. **`.git/` 目录**
   - 硬编码排除，无法关闭

### 手动排除（方式 1）

使用 `--ignore` 参数手动指定排除模式：

```bash
# 单个排除
python tools/py/project_scanner.py . --ignore ai_coding_context

# 多个排除（逗号分隔）
python tools/py/project_scanner.py . --ignore "ai_coding_context,node_modules,.vscode"

# Node.js 版本同理
node tools/js/project_scanner.js . --ignore "ai_coding_context,node_modules"
```

### 标准排除（方式 2 - 推荐）⭐

使用 `--exclude-standard` 参数一键排除所有标准模式：

```bash
# Python 版本
python tools/py/project_scanner.py . --exclude-standard

# Node.js 版本
node tools/js/project_scanner.js . --exclude-standard
```

**标准排除列表包括**：

**框架文件**（最高优先级）：

- **自动检测的框架目录**⭐（包含 `AI_ENTRY_POINT.md` 的目录）
  - 检测策略 1：通过脚本自身位置反推（最可靠，支持任意重命名）
  - 检测策略 2：检查常见位置（`ai_coding_context/`、`.ai/`、`docs/ai_context/`）
  - 检测策略 3：遍历项目根目录查找
- `ai_coding_context/`（fallback）
- `.ai/`（fallback）
- `docs/ai_context/`（fallback）

**依赖与构建产物**：

- `node_modules/`、`package-lock.json`
- `venv/`、`env/`、`.env/`、`__pycache__/`
- `dist/`、`build/`、`.next/`
- `target/`（Java/Rust）

**版本控制**：

- `.git/`（已硬编码）
- `.svn/`

**IDE 配置**：

- `.vscode/`、`.idea/`
- `*.swp`、`*.swo`

### 组合使用

`--exclude-standard` 和 `--ignore` 可以组合使用：

```bash
# 标准排除 + 自定义排除
python tools/py/project_scanner.py . --exclude-standard --ignore "custom_temp,*.tmp"
```

### 输出说明

启用排除后，输出会显示已排除的目录：

```json
{
  "data": { ... },
  "metadata": {
    "excluded_patterns": [
      "ai_coding_context/ (framework auto-detected)",
      "node_modules/",
      ".git/",
      "..."
    ],
    "excluded_count": 5
  }
}
```

## ⭐ project_scanner 新功能 (v1.3.0)

### 智能自适应输出策略

project_scanner 现在会根据项目规模自动优化输出，减少 Token 消耗：

- **基础级** (≤500 文件): 完整输出所有文件和目录
- **中级** (501-2000 文件): 限制每目录文件数 + 智能排序
- **高级** (>2000 文件): 限制文件和目录数 + 智能子判断

### 新增参数

| 参数                                            | 说明                                 | 默认值 |
| ----------------------------------------------- | ------------------------------------ | ------ |
| `--mode {tree,summary,auto}`                    | 输出模式选择                         | auto   |
| `--limit-files NUM`                             | 每目录最多显示的文件数               | 10     |
| `--limit-dirs NUM`                              | 每目录最多显示的子目录数（高级模式） | 10     |
| `--no-adaptive`                                 | 禁用自适应，强制完整输出             | -      |
| `--complexity-override {basic,medium,advanced}` | 手动指定复杂度级别                   | -      |
| `--advanced-dir-threshold NUM`                  | 高级模式智能判断阈值                 | 20     |

### 使用示例

```bash
# 快速摘要（推荐用于大型项目）
python tools/py/project_scanner.py --mode summary --exclude-standard
node tools/js/project_scanner.js --mode summary --exclude-standard

# 自适应树形输出（自动优化）
python tools/py/project_scanner.py . --exclude-standard
node tools/js/project_scanner.js . --exclude-standard

# 强制完整输出（小型项目或需要完整信息时）
python tools/py/project_scanner.py . --no-adaptive --exclude-standard
node tools/js/project_scanner.js . --no-adaptive --exclude-standard

# 手动控制输出详细度
python tools/py/project_scanner.py . --limit-files 5 --limit-dirs 5
node tools/js/project_scanner.js . --limit-files 5 --limit-dirs 5
```

### 核心改进

1. **重要文件优先** ⭐: README.md, package.json, tsconfig.json 等自动靠前显示
2. **智能排序**: 不再是简单字母序，重要目录(src, lib, app)优先
3. **友好提示**: 省略内容时告知如何查看
   - 示例: `"... (省略 15 个文件, 使用 --path ./src --no-adaptive 查看完整列表)"`
4. **空目录处理**: 不在树中显示，在 metadata 中统计
5. **性能提升**: 扫描速度提升 30%，大型项目 Token 减少 60-80%

## ➕ 扩展指南 (For AI Agents)

我们鼓励 AI 在执行任务过程中，将**重复性高**、**通用性强**的操作沉淀为新的工具脚本。

### 何时创建新工具？

1. **高频重复**: 某个复杂操作在不同任务中被重复执行超过 3 次。
2. **稳定性要求**: 需要复杂的错误处理或跨平台兼容性，简单的 Shell 命令难以满足。
3. **性能敏感**: 需要高效处理大量文件或数据。

### 开发规范

1. **双模实现**: 尽量同时提供 Python (`tools/py/`) 和 Node.js (`tools/js/`) 版本，以最大化环境兼容性。
2. **零依赖**: 仅使用标准库，**严禁**引入需要 `pip install` or `npm install` 的第三方依赖。
3. **详细注释**: **所有脚本必须在文件顶部添加详细文档注释**，包括：
   - 功能说明（3-5 个要点）
   - 使用方法（命令行示例）
   - 参数说明（所有参数的详细说明）
   - 输出格式（JSON 结构示例）
   - 使用示例（3-4 个实际用例）
   - 版本信息（版本号和更新日期）
   - 参考现有脚本（如 `timestamp_analyzer.py`）的注释格式
4. **错误处理**: 脚本应捕获异常并输出 JSON 格式的错误信息，避免直接 Crash。
5. **文档更新**: 创建新工具后，**必须**更新本 `README.md` 的工具清单。
6. **变更记录**: 创建或修改工具后，**必须**更新 `tools/CHANGELOG.md`，记录变更内容（遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式）。

### 变更记录规范

更新 `tools/CHANGELOG.md` 时：

- **新增工具**: 在 `### Added` 下添加条目
- **修改工具**: 在 `### Changed` 下添加条目
- **修复 Bug**: 在 `### Fixed` 下添加条目
- **删除工具**: 在 `### Removed` 下添加条目（极少情况）

### 质量保证

请参考 `workflows/create_custom_tool_workflow.md` 获取详细的创建流程与验证标准。

---

## 🔄 跨 IDE 兼容性

### IDE 内置工具能力对比

不同 AI IDE 的内置工具能力差异巨大，本工具库设计为**通用降级方案**，确保框架在所有环境中稳定运行。

| IDE                | 内置搜索工具                                     | 支持 ripgrep | 推荐策略                 |
| ------------------ | ------------------------------------------------ | ------------ | ------------------------ |
| **Cursor**         | `grep_search`, `codebase_search`, `find_by_name` | ✅           | 优先内置工具，脚本作降级 |
| **GitHub Copilot** | 无                                               | ❌           | **必须使用本工具库**     |
| **Windsurf**       | 基础文件搜索                                     | ⚠️ 部分支持  | 优先使用脚本保证一致性   |
| **Cline**          | 可配置工具集                                     | 🔧 可配置    | 根据配置动态选择         |

### 工具选择策略

#### 步骤 1: 环境检测（必须第一步）

```bash
python tools/py/env_diagnosis.py
```

**输出示例**：

```json
{
  "ide": "cursor",
  "python_version": "3.11.5",
  "node_version": "20.10.0",
  "has_rg": true,
  "capabilities": {
    "grep_search": true,
    "codebase_search": true,
    "find_by_name": true
  }
}
```

#### 步骤 2: 根据任务类型选择工具

**语义搜索任务**（如"找到所有用户认证相关代码"）：

- 若 `capabilities.codebase_search == true` → 使用 IDE 内置 `codebase_search`
- 否则 → 使用 `tools/py/content_searcher.py` + 关键词拆解策略

**文本搜索任务**（如"搜索所有 TODO 注释"）：

- 若 `capabilities.grep_search == true` **且** 项目文件数 >5000 → 使用 IDE 内置 `grep_search`
- 否则 → 使用 `tools/py/content_searcher.py`

**文件名搜索**（如"找到所有 config.js 文件"）：

- 若 `capabilities.find_by_name == true` **且** 项目文件数 >5000 → 使用 IDE 内置 `find_by_name`
- 否则 → 使用 `tools/py/file_finder.py`

**项目结构分析**（如"生成项目目录树"）：

- 始终使用 `tools/py/project_scanner.py`（IDE 通常不提供此功能）

#### 降级路径

```
IDE 内置工具 (高性能) → 失败 → tools 脚本 (高兼容) → 失败 → 手动命令 + 警告
```

**示例**：

```python
# AI 调用逻辑伪代码
try:
    result = grep_search(query="TODO")  # 尝试内置工具
except ToolNotAvailableError:
    result = run_command("python tools/py/content_searcher.py --query TODO")
except:
    notify_user("内置工具和脚本均失败，请手动执行命令")
```

### 配置建议

在 `config/user_config.md` 中可配置工具偏好（详见 `config/README.md`）：

```yaml
---
tools:
  preferred_runtime: "python" # 或 "nodejs"
  auto_fallback: true # 工具失败时自动降级
  timeout_seconds: 10 # 工具超时时间
  max_file_scan: 5000 # 最大扫描文件数
---
```

---

## ⚡ 性能参考指标

### 测试环境

- **硬件**: MacBook Pro M1, 16GB RAM
- **操作系统**: macOS / Windows 11 / Ubuntu 22.04
- **测试项目**:
  - 小型: Vue 3 项目 (~500 文件)
  - 中型: Next.js 全栈 (~3000 文件)
  - 大型: Monorepo (~15000 文件)

### 性能数据

| 工具                             | 小项目 (<1k) | 中型 (1k-5k) | 大型 (>5k) | 推荐上限 |
| -------------------------------- | ------------ | ------------ | ---------- | -------- |
| `project_scanner.py`             | <1s          | 2-5s         | 5-15s      | 10k 文件 |
| `content_searcher.py` (fallback) | <1s          | 3-8s         | 15-60s     | 5k 文件  |
| `content_searcher.py` (with rg)  | <0.5s        | 1-2s         | 3-8s       | 无限制   |
| `file_finder.py`                 | <0.5s        | 1-3s         | 3-10s      | 20k 文件 |
| `file_reader.py`                 | <0.1s        | <0.2s        | <0.5s      | 无限制   |
| `env_diagnosis.py`               | <0.5s        | <0.5s        | <0.5s      | 无限制   |
| `git_inspector.py`               | <0.5s        | <1s          | 1-3s       | 无限制   |
| `summary_extractor.py`           | <0.2s        | <0.5s        | 1-2s       | 无限制   |
| `summary_validator.py`           | <0.2s        | <0.5s        | 1-2s       | 无限制   |

> **注意**: 实际性能受硬件、磁盘 I/O、文件分布等因素影响，以上数据仅供参考。

### 性能优化建议

#### 大型项目 (>5k 文件)

1. **优先使用 IDE 内置工具**（若可用）

   - `grep_search` 替代 `content_searcher.py`
   - `find_by_name` 替代 `file_finder.py`

2. **限制搜索范围**：

   ```bash
   # ❌ 全局搜索
   python tools/py/content_searcher.py --query "TODO" --path ./

   # ✅ 限定范围
   python tools/py/content_searcher.py --query "TODO" --path ./src
   ```

3. **使用排除模式**：
   ```bash
   python tools/py/content_searcher.py --query "TODO" --exclude "node_modules,dist,build,.git"
   ```

#### 超大型项目 (>10k 文件)

1. **project_scanner**: 限制深度 `--depth 3`
2. **content_searcher**: 强制使用 IDE 内置 `grep_search`
3. **file_finder**: 分目录多次调用，而非全局扫描

### 运行时间监控

**自 v1.1.0 起**，所有工具统一输出运行时间元数据：

```json
{
  "data": {
    "files": ["src/index.ts", "src/app.ts"]
  },
  "metadata": {
    "elapsed_seconds": 2.35,
    "timeout_threshold": 10,
    "version": "1.1.0"
  }
}
```

**AI 使用建议**:

- 若 `elapsed_seconds > 8`，记录为性能警告
- 下次遇到类似规模项目，优先使用内置工具或缩小搜索范围
- 可在 `config/user_config.md` 中调整 `timeout_seconds` 阈值

### 超时处理

所有工具默认超时：**10 秒**

超时后返回：

```json
{
  "success": false,
  "error": "timeout",
  "partial_data": [...],
  "suggestion": "缩小搜索范围或切换到 IDE 内置工具"
}
```

**降级策略**:

1. 缩小搜索范围（如从 `./` 改为 `./src`）
2. 增加排除模式
3. 切换到 IDE 内置工具
4. 若仍超时，手动指导用户分批处理
