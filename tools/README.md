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

| 工具名称           | 功能描述                   | 典型用途                                    |
| :----------------- | :------------------------- | :------------------------------------------ |
| `project_scanner`  | 扫描项目结构，生成 JSON 树 | 快速了解项目规模与结构，自动忽略 .gitignore |
| `file_reader`      | 安全读取文件内容           | 读取大文件、处理编码、检测二进制文件        |
| `content_searcher` | 高效搜索内容 (类 grep)     | 查找代码引用、TODO、特定字符串              |
| `file_finder`      | 查找文件 (类 find)         | 根据文件名模式查找文件                      |
| `env_diagnosis`    | 环境诊断                   | 检查 Python/Node.js 版本及可用性            |
| `git_inspector`    | Git 信息检查               | 获取当前分支、变更状态                      |

## 🚀 使用指南

### Python 版本 (推荐)

```bash
python tools/py/project_scanner.py --max-files 1000
```

### Node.js 版本

```bash
node tools/js/project_scanner.js --max-files 1000
```

## ➕ 扩展指南 (For AI Agents)

我们鼓励 AI 在执行任务过程中，将**重复性高**、**通用性强**的操作沉淀为新的工具脚本。

### 何时创建新工具？

1. **高频重复**: 某个复杂操作在不同任务中被重复执行超过 3 次。
2. **稳定性要求**: 需要复杂的错误处理或跨平台兼容性，简单的 Shell 命令难以满足。
3. **性能敏感**: 需要高效处理大量文件或数据。

### 开发规范

1. **双模实现**: 尽量同时提供 Python (`tools/py/`) 和 Node.js (`tools/js/`) 版本，以最大化环境兼容性。
2. **零依赖**: 仅使用标准库，**严禁**引入需要 `pip install` or `npm install` 的第三方依赖。
3. **错误处理**: 脚本应捕获异常并输出 JSON 格式的错误信息，避免直接 Crash。
4. **文档更新**: 创建新工具后，**必须**更新本 `README.md` 的工具清单。

### 质量保证

请参考 `workflows/create_custom_tool_workflow.md` 获取详细的创建流程与验证标准。
