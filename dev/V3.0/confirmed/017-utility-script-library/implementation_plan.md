# 实施计划 - 实用脚本工具库 (017)

**目标**: 创建一个标准化的、跨平台的实用脚本工具库 (`tools/`)，以替代临时的 Shell 命令进行 AI 项目分析，确保准确性、效率和一致的 JSON 输出。

## 需要用户审查

> [!IMPORTANT] > **双模运行时策略**: 我们将同时实现所有工具的 Python 和 Node.js 版本，以确保最大的兼容性。这会增加维护成本，但能保证可用性。
> **Ripgrep 依赖**: `content_searcher` 将优先尝试使用 `rg` (ripgrep) 以获得高性能，但如果未找到，**必须**回退到原生正则实现。

## 建议变更

### 1. 基础设施建设

#### [NEW] `tools/` 目录结构

在项目根目录下创建以下目录结构：

```
tools/
├── py/                 # Python 实现
│   ├── project_scanner.py
│   ├── file_reader.py
│   ├── content_searcher.py
│   ├── file_finder.py
│   ├── env_diagnosis.py
│   └── git_inspector.py
├── js/                 # Node.js 实现
│   ├── project_scanner.js
│   ├── file_reader.js
│   ├── content_searcher.js
│   ├── file_finder.js
│   ├── env_diagnosis.js
│   └── git_inspector.js
└── fallback/           # 无运行时环境的降级方案
    ├── commands_win.md
    └── commands_unix.md
```

### 2. 核心工具实现

#### [NEW] `project_scanner` (py/js)

- **功能**: 目录结构的 BFS (广度优先) 遍历。
- **特性**:
  - 默认遵守 `.gitignore`。
  - **支持额外排除**: 提供 `--ignore` 参数 (支持 glob 模式，如 `*,other,docs`)，用于排除不相关的目录（如参考文档、遗留代码）。
  - **边界处理**:
    - **软链接 (Symlinks)**: 默认不跟随，防止死循环；可配置 `--follow-symlinks`。
    - **权限错误**: 遇到无权访问的目录/文件，记录警告但不中断扫描。
    - **超大目录**: 设置单目录最大文件数限制 (默认 1000)，超过截断并标记 `truncated: true`。
  - **路径标准化**: 输出 JSON 中统一使用正斜杠 `/`，消除 OS 差异。
  - 生成 Tree 视图或 JSON，支持最大深度控制。
- **输出**: JSON `{ "structure": "...", "stats": { "files": 10, "dirs": 2 } }`

#### [NEW] `file_reader` (py/js)

- **功能**: 带分页的安全文件读取。
- **特性**:
  - 支持 `offset`/`limit`。
  - **编码检测**: 尝试 UTF-8 -> 尝试系统默认 -> 失败则视为二进制。
  - **二进制保护**: 检测到二进制内容（如空字节）直接返回 `is_binary: true`，不返回内容。
- **输出**: JSON `{ "content": "...", "lines_read": 100, "total_lines": 500, "truncated": true, "is_binary": false }`

#### [NEW] `content_searcher` (py/js)

- **功能**: 内容搜索。
- **特性**:
  - 优先尝试 `rg` -> 降级为原生正则。
  - 支持 `include` 模式。
  - **支持排除**: 提供 `--exclude` 参数，过滤掉不需要搜索的目录。
  - **超时控制**: 设置搜索超时时间 (默认 5s)，防止正则回溯卡死。
- **输出**: JSON `{ "matches": [ { "file": "path", "line": 10, "content": "..." } ] }`

#### [NEW] `file_finder` (py/js)

- **功能**: Glob 模式匹配。
- **特性**: 快速文件查找。
- **输出**: JSON `{ "files": ["path/to/file1", "path/to/file2"] }`

#### [NEW] `env_diagnosis` & `git_inspector` (py/js)

- **功能**: 环境和 Git 状态检查。
- **特性**:
  - **版本检查**: 明确 Python (>=3.6) 和 Node.js (>=14) 的最低版本要求。
- **输出**: JSON 格式的状态信息。

### 3. 框架集成

#### [MODIFY] [AI_ENTRY_POINT.md](../../../../AI_ENTRY_POINT.md)

- 更新 "步骤 0" 和 "步骤 1" 以使用 `tools/project_scanner`。
- 更新 "步骤 2" 逻辑以使用扫描器的 JSON 输出。
- 更新 "数据验证" 以使用 `tools/content_searcher`。

## 验证计划

### 自动化测试

由于这些是独立脚本，我们将创建一个测试运行脚本 `tools/test_suite.py` (或类似脚本) 来针对测试用例目录进行验证。

1.  **测试用例设置**: 创建一个临时目录 `tests/fixtures/`，包含已知的文件结构（嵌套目录、文本文件、二进制文件、.gitignore）。
2.  **测试运行器**:
    - 运行 `project_scanner` -> 验证 JSON 输出是否匹配测试用例结构。
    - 运行 `file_reader` -> 验证内容读取、分页和行数统计。
    - 运行 `content_searcher` -> 验证正则匹配和 `rg` 回退（模拟 `rg` 缺失）。
    - 运行 Python 和 Node.js 版本并断言输出完全一致。

### 手动验证

1.  **环境检查**: 在用户当前环境中运行 `env_diagnosis`。
2.  **真实项目扫描**: 在 `ai_coding_context` 仓库本身运行 `project_scanner` 并检查 Tree 视图输出。
3.  **搜索测试**: 运行 `content_searcher` 以查找仓库中的已知字符串。
