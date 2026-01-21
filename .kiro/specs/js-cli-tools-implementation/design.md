# Design Document

## Overview

本设计文档描述了 `install_hooks.js` 和 `commit_template_cli.js` 两个 Node.js 工具的实现方案。这两个工具将与现有的 Python 版本保持功能一致，使用 Node.js 标准库实现，确保零依赖和跨平台兼容性。

设计目标：
- 功能与 Python 版本完全对等
- 使用 Node.js 标准库（fs, path, readline, child_process）
- 跨平台兼容（Windows, macOS, Linux）
- 符合工具库开发规范
- 提供友好的用户交互体验

## Architecture

### 整体架构

```
tools/js/
├── install_hooks.js          # Git Hooks 安装工具
├── commit_template_cli.js    # Commit 模板 CLI 工具
├── commit_parser.js          # 依赖：解析 commit
└── commit_quality_scorer.js  # 依赖：评分 commit
```

### 模块依赖关系

```
install_hooks.js
  └── Node.js 标准库 (fs, path, readline)

commit_template_cli.js
  ├── Node.js 标准库 (fs, path, readline)
  ├── commit_parser.js (可选，用于质量评分)
  └── commit_quality_scorer.js (可选，用于质量评分)
```

### 跨平台兼容性策略

1. **路径处理**: 使用 `path.join()` 和 `path.resolve()` 处理路径
2. **文件权限**: 使用 `fs.chmodSync()` 设置执行权限，Windows 上跳过
3. **用户输入**: 使用 `readline` 模块实现交互式输入
4. **进程退出**: 使用 `process.exit()` 返回正确的退出码

## Components and Interfaces

### Component 1: install_hooks.js

**职责**: 安装和卸载 Git pre-commit hook

**核心函数**:

```javascript
/**
 * 查找 Git 仓库根目录
 * @returns {string|null} Git 仓库根目录路径，未找到返回 null
 */
function findGitRoot()

/**
 * 安装 pre-commit hook
 * @param {string} gitRoot - Git 仓库根目录
 * @returns {Promise<boolean>} 安装是否成功
 */
async function installPreCommitHook(gitRoot)

/**
 * 卸载 pre-commit hook
 * @param {string} gitRoot - Git 仓库根目录
 * @returns {Promise<boolean>} 卸载是否成功
 */
async function uninstallPreCommitHook(gitRoot)

/**
 * 显示使用说明
 */
function showUsage()

/**
 * 询问用户确认
 * @param {string} question - 问题文本
 * @returns {Promise<boolean>} 用户是否确认
 */
async function askConfirmation(question)
```

**命令行参数**:
- `--help` / `-h`: 显示帮助信息
- `--uninstall` / `-u`: 卸载 hook

### Component 2: commit_template_cli.js

**职责**: 交互式生成结构化 commit message

**核心函数**:

```javascript
/**
 * 交互式模式
 * @returns {Promise<Object>} { commitType, what, why, howItems }
 */
async function interactiveMode()

/**
 * 生成 commit message
 * @param {string} commitType - Commit 类型
 * @param {string} what - WHAT 内容
 * @param {string} why - WHY 内容
 * @param {Array<string>} howItems - HOW 列表
 * @returns {string} 生成的 commit message
 */
function generateCommitMessage(commitType, what, why, howItems)

/**
 * 计算质量评分（调用外部工具）
 * @param {string} message - Commit message
 * @returns {Object|null} 评分结果，失败返回 null
 */
function calculateQualityScore(message)

/**
 * 询问用户输入
 * @param {string} prompt - 提示文本
 * @returns {Promise<string>} 用户输入
 */
async function askQuestion(prompt)

/**
 * 询问多行输入
 * @param {string} prompt - 提示文本
 * @returns {Promise<Array<string>>} 用户输入的行数组
 */
async function askMultiline(prompt)
```

**命令行参数**:
- `--help` / `-h`: 显示帮助信息
- `--quick`: 快速模式
- `--type TYPE`: Commit 类型
- `--what WHAT`: WHAT 内容
- `--why WHY`: WHY 内容
- `--how HOW`: HOW 内容（逗号分隔）

## Data Models

### CommitTemplate

```javascript
{
  commitType: string,    // 'feature' | 'fix' | 'architecture' | 'other'
  what: string,          // WHAT 描述
  why: string,           // WHY 原因
  howItems: string[]     // HOW 步骤列表
}
```

### HookInstallResult

```javascript
{
  success: boolean,      // 是否成功
  message: string,       // 提示信息
  backupPath: string?    // 备份文件路径（如果有）
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Git 仓库检测一致性

*For any* 目录路径，如果该路径或其父目录包含 `.git` 目录，则 `findGitRoot()` 应返回包含 `.git` 的最近父目录路径；否则返回 null

**Validates: Requirements 1.1**

### Property 2: Hook 安装幂等性

*For any* Git 仓库，多次执行安装操作（用户确认覆盖）应产生相同的最终状态：hook 文件存在且内容正确

**Validates: Requirements 1.2, 1.3**

### Property 3: 备份恢复对称性

*For any* 已安装的 hook，如果存在备份文件，则卸载并恢复备份后，hook 文件内容应与备份前的原始内容一致

**Validates: Requirements 1.5**

### Property 4: Commit message 格式一致性

*For any* 有效的 CommitTemplate 输入，生成的 commit message 应符合 `prompt(type): what\n\nWHAT: ...\nWHY: ...\nHOW:\n- ...` 格式

**Validates: Requirements 2.2**

### Property 5: 交互式与快速模式等价性

*For any* 相同的输入参数，交互式模式（用户输入相同内容）和快速模式应生成完全相同的 commit message

**Validates: Requirements 2.5**

### Property 6: 跨平台路径处理正确性

*For any* 文件路径操作，在 Windows 和 Unix 系统上应产生正确的路径结果，不因路径分隔符差异导致错误

**Validates: Requirements 3.4**

### Property 7: 错误处理优雅性

*For any* 异常情况（文件不存在、权限不足、用户取消），工具应捕获异常并返回清晰的错误信息，而不是崩溃

**Validates: Requirements 3.2, 4.3**

### Property 8: 输出格式一致性

*For any* 相同的操作和输入，JS 版本和 Python 版本应产生格式一致的输出信息（忽略语言特定的细微差异）

**Validates: Requirements 3.1**

## Error Handling

### install_hooks.js 错误场景

1. **未找到 Git 仓库**
   - 检测: `findGitRoot()` 返回 null
   - 处理: 显示错误信息 "❌ 错误: 未找到 Git 仓库"，退出码 1

2. **源 hook 文件不存在**
   - 检测: `fs.existsSync(sourceHook)` 返回 false
   - 处理: 显示 "❌ 源文件不存在: {path}"，返回 false

3. **用户取消覆盖**
   - 检测: 用户输入不是 'y'
   - 处理: 显示 "❌ 取消安装"，返回 false

4. **文件操作权限错误**
   - 检测: `fs.copyFileSync()` 或 `fs.chmodSync()` 抛出异常
   - 处理: 捕获异常，显示错误信息，返回 false

### commit_template_cli.js 错误场景

1. **依赖工具不存在**
   - 检测: 尝试 require 或执行外部脚本失败
   - 处理: 跳过质量评分，继续执行

2. **用户输入为空**
   - 检测: 输入字符串 trim 后为空
   - 处理: 使用默认值 "未指定" 或提示重新输入

3. **命令行参数缺失**
   - 检测: 快速模式下必需参数为 undefined
   - 处理: 使用默认值或显示警告

## Testing Strategy

### Unit Testing

使用 Node.js 内置的 `assert` 模块编写单元测试，覆盖核心函数：

**install_hooks.js 测试用例**:
1. `findGitRoot()` 在不同目录层级的行为
2. `installPreCommitHook()` 在文件已存在/不存在时的行为
3. `uninstallPreCommitHook()` 在有/无备份时的行为
4. 路径处理在 Windows/Unix 上的正确性

**commit_template_cli.js 测试用例**:
1. `generateCommitMessage()` 生成的格式正确性
2. 不同 commit 类型的映射正确性
3. 空输入的默认值处理
4. 多行输入的解析正确性

### Property-Based Testing

使用 `fast-check` 库（如果允许）或手动实现简单的属性测试：

**测试属性**:
1. Git 仓库检测的一致性（Property 1）
2. Hook 安装的幂等性（Property 2）
3. Commit message 格式的一致性（Property 4）
4. 跨平台路径处理的正确性（Property 6）

### Integration Testing

**端到端测试场景**:
1. 在临时 Git 仓库中测试完整的安装/卸载流程
2. 测试交互式模式的完整流程（使用模拟输入）
3. 测试快速模式的参数解析和输出
4. 验证与 Python 版本的输出一致性

### Manual Testing

**跨平台测试**:
- Windows 10/11
- macOS (Intel & Apple Silicon)
- Linux (Ubuntu 22.04)

**测试检查项**:
- 文件权限设置正确
- 路径分隔符处理正确
- 用户交互体验流畅
- 错误提示清晰易懂

## Implementation Notes

### 使用 readline 实现交互式输入

```javascript
const readline = require('readline');

function createInterface() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

async function askQuestion(prompt) {
  const rl = createInterface();
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}
```

### 跨平台文件权限设置

```javascript
const fs = require('fs');
const os = require('os');

function setExecutable(filePath) {
  if (os.platform() !== 'win32') {
    const stats = fs.statSync(filePath);
    fs.chmodSync(filePath, stats.mode | 0o111); // +x for user, group, others
  }
}
```

### 调用外部脚本获取质量评分

```javascript
const { execSync } = require('child_process');

function calculateQualityScore(message) {
  try {
    const result = execSync(
      `node tools/js/commit_quality_scorer.js --message "${message.replace(/"/g, '\\"')}"`,
      { encoding: 'utf8' }
    );
    return JSON.parse(result);
  } catch (error) {
    return null; // 失败时返回 null，不影响主流程
  }
}
```

### 文档注释格式

遵循 JSDoc 风格，包含：
- 功能说明（3-5 个要点）
- 使用方法（命令行示例）
- 参数说明（所有参数的详细说明）
- 输出格式（如果适用）
- 使用示例（3-4 个实际用例）
- 版本信息（版本号和更新日期）

## Performance Considerations

- 文件操作使用同步 API（`fs.copyFileSync`, `fs.readFileSync`），因为这些是 CLI 工具，不需要异步
- 用户输入使用异步 API（`readline`），提供更好的交互体验
- 避免不必要的文件读取和系统调用
- 预期执行时间 <1 秒

## Security Considerations

- 不执行用户提供的任意代码
- 文件路径使用 `path.resolve()` 规范化，防止路径遍历
- 备份文件使用固定的 `.backup` 后缀，避免覆盖其他文件
- 用户输入进行基本的清理（trim），但不执行复杂的验证（commit message 内容由用户负责）
