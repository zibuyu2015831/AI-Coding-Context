# 工具库更新日志 (Changelog)

本文档记录工具库的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.1.0] - 2025-12-02

### Added

- 新增 `timestamp_analyzer.py` - 采集文件时间戳供 AI 分析文档健康度
- 新增 `git_diff_analyzer.py` - 分析 git 差异供 AI 判断文档更新需求
- 新增 `timestamp_analyzer.js` - Node.js 版本时间戳分析工具
- 新增 `git_diff_analyzer.js` - Node.js 版本 Git 差异分析工具
- 所有工具统一输出运行时间（`metadata.elapsed_seconds`）
- 统一错误处理机制（结构化 JSON 错误，不 Crash）
- 补充 `README.md` - 跨 IDE 兼容性章节
- 补充 `README.md` - 性能参考指标章节
- **为所有 12 个脚本添加详细文档注释**（Python 6 个 + Node.js 6 个，共 558 行专业注释）
  - 包含功能说明、使用方法、参数说明、输出格式、使用示例、版本信息
  - 实现脚本自文档化，人类可直接阅读脚本了解用法

### Changed

- 错误处理改为脚本内部优雅处理（编码、权限、超时等场景）
- 时间戳采集统一使用 `st_mtime`（跨平台一致性）

### Fixed

- `content_searcher.py` 修复 Windows 路径分隔符问题
- `project_scanner.py` 改进 `.gitignore` 解析逻辑
- `content_searcher.py` 修复文档注释中的转义序列警告（`\s` → `\\s`）

---

## [1.0.0] - 2025-12-01

### Added

- 初始版本发布
- `project_scanner.py` - 项目结构扫描
- `content_searcher.py` - 内容搜索（支持 ripgrep 加速）
- `file_finder.py` - 文件名搜索
- `file_reader.py` - 安全文件读取
- `env_diagnosis.py` - 环境诊断
- `git_inspector.py` - Git 信息检查
- Python 和 Node.js 双模实现
- 零依赖设计
