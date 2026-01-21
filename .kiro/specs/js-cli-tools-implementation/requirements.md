# Requirements Document

## Introduction

本需求文档定义了为 `install_hooks` 和 `commit_template_cli` 两个 Python 工具实现 Node.js 版本的需求。这两个工具目前仅有 Python 实现，违反了工具库的"双模实现"原则。实现 JS 版本将提升跨环境兼容性，确保在没有 Python 环境的系统中也能使用这些工具。

## Glossary

- **System**: 指 `install_hooks.js` 和 `commit_template_cli.js` 两个 Node.js 脚本
- **Git Hooks**: Git 仓库中的钩子脚本，在特定事件触发时自动执行
- **Pre-commit Hook**: 在执行 `git commit` 前触发的钩子
- **Commit Template**: 结构化的 commit message 模板，包含 WHAT/WHY/HOW 字段
- **Interactive Mode**: 交互式命令行界面，通过问答方式引导用户输入
- **Quick Mode**: 快速模式，通过命令行参数直接生成结果，跳过交互
- **Quality Score**: Commit 质量评分，基于 WHAT/WHY/HOW 等维度的综合评分

## Requirements

### Requirement 1

**User Story:** 作为开发者，我希望在没有 Python 环境的系统中也能安装 Git hooks，以便在所有环境中使用统一的 commit 检查机制。

#### Acceptance Criteria

1. WHEN 用户执行 `node tools/js/install_hooks.js` THEN the System SHALL 自动检测当前目录或父目录中的 Git 仓库根目录
2. WHEN Git 仓库根目录被找到 THEN the System SHALL 将 `tools/git-hooks/pre-commit` 文件复制到 `.git/hooks/pre-commit` 位置
3. WHEN 目标 hook 文件已存在 THEN the System SHALL 提示用户是否覆盖，并在用户确认后备份原文件
4. WHEN hook 文件被成功安装 THEN the System SHALL 在非 Windows 系统上设置文件的可执行权限
5. WHEN 用户执行 `node tools/js/install_hooks.js --uninstall` THEN the System SHALL 删除已安装的 hook 文件，并提示是否恢复备份

### Requirement 2

**User Story:** 作为开发者，我希望通过交互式界面生成结构化的 commit message，以便快速创建符合规范的高质量 commit。

#### Acceptance Criteria

1. WHEN 用户执行 `node tools/js/commit_template_cli.js` THEN the System SHALL 启动交互式向导，依次询问 commit 类型、WHAT、WHY、HOW 信息
2. WHEN 用户完成所有输入 THEN the System SHALL 生成格式为 `prompt(type): what\n\nWHAT: ...\nWHY: ...\nHOW:\n- ...` 的 commit message
3. WHEN commit message 生成后 THEN the System SHALL 调用 `commit_quality_scorer.js` 和 `commit_parser.js` 计算质量评分并显示
4. WHEN 质量评分显示后 THEN the System SHALL 询问用户是否执行 commit，并提供操作提示
5. WHEN 用户执行 `node tools/js/commit_template_cli.js --quick --what "..." --why "..." --how "..."` THEN the System SHALL 跳过交互直接生成 commit message

### Requirement 3

**User Story:** 作为开发者，我希望 JS 版本工具与 Python 版本功能完全一致，以便在不同环境中获得相同的用户体验。

#### Acceptance Criteria

1. WHEN JS 版本工具执行时 THEN the System SHALL 产生与 Python 版本相同的输出格式和提示信息
2. WHEN 工具遇到错误情况（如未找到 Git 仓库、文件不存在）THEN the System SHALL 显示与 Python 版本一致的错误提示
3. WHEN 用户使用 `--help` 参数 THEN the System SHALL 显示与 Python 版本一致的使用说明
4. WHEN 工具处理文件路径时 THEN the System SHALL 正确处理 Windows 和 Unix 系统的路径分隔符差异
5. WHEN 工具需要用户输入时 THEN the System SHALL 使用 Node.js 标准库实现交互式输入，无需第三方依赖

### Requirement 4

**User Story:** 作为工具库维护者，我希望新增的 JS 工具符合工具库开发规范，以便保持代码库的一致性和可维护性。

#### Acceptance Criteria

1. WHEN JS 工具文件被创建 THEN the System SHALL 在文件顶部包含详细的文档注释，包括功能说明、使用方法、参数说明、输出格式、使用示例、版本信息
2. WHEN 工具执行完成 THEN the System SHALL 输出包含 `metadata.elapsed_seconds` 和 `metadata.version` 的结构化数据（仅适用于需要输出 JSON 的场景）
3. WHEN 工具遇到异常 THEN the System SHALL 捕获异常并优雅处理，避免直接崩溃
4. WHEN 工具被实现 THEN the System SHALL 仅使用 Node.js 标准库，不引入任何需要 `npm install` 的第三方依赖
5. WHEN 工具被添加到代码库 THEN the System SHALL 更新 `tools/README.md` 工具清单和 `tools/CHANGELOG.md` 变更记录

### Requirement 5

**User Story:** 作为开发者，我希望工具提供清晰的使用说明和帮助信息，以便快速了解如何使用这些工具。

#### Acceptance Criteria

1. WHEN 用户执行 `node tools/js/install_hooks.js --help` THEN the System SHALL 显示包含功能介绍、使用方式、Hook 功能列表的帮助信息
2. WHEN 用户执行 `node tools/js/commit_template_cli.js --help` THEN the System SHALL 显示包含参数说明、使用示例的帮助信息
3. WHEN 工具成功完成操作 THEN the System SHALL 显示成功提示和后续操作建议
4. WHEN 工具执行失败 THEN the System SHALL 显示清晰的错误信息和可能的解决方案
5. WHEN 交互式工具运行时 THEN the System SHALL 使用 emoji 和格式化文本提升用户体验
