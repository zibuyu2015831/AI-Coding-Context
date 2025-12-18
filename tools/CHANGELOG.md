# 工具库更新日志 (Changelog)

本文档记录工具库的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.3.0] - 2025-12-11

### Added

- 新增 `git_safety.py` & `.js` - Git 安全检查工具
  - 检查当前分支是否为保护分支（main/master/production 等）
  - 验证 Git 命令是否安全（RED ZONE: force push, reset --hard 等）
  - 建议符合规范的分支名（feature/bugfix/refactor/docs）
  - 包含 29 个单元测试，覆盖率 >95%
- 新增 `commit_parser.py` & `.js` - Commit 解析工具
  - 解析结构化 commit（prompt:格式）提取 WHAT/WHY/HOW
  - 解析 Conventional Commits 格式
  - 传统 commit 降级处理
  - 支持 commit 聚合和合并分析
- 新增 `commit_quality_scorer.py` & `.js` - Commit 质量评分工具
  - 5 维度评分：WHAT 清晰度(30 分)、WHY 深度(30 分)、HOW 完整性(20 分)、粒度合理性(10 分)、可测试性(10 分)
  - 自动生成改进建议
  - 识别优质 commit（≥80 分）
- 新增 `commit_aggregator.py` & `.js` - Commit 聚合工具
  - 同类 commit 聚合
  - Token 优化（实测减少 85.91%）
  - 智能过滤规则
- 新增 `commit_template_cli.py` - Commit 模板 CLI 工具（仅 Python）
  - 交互式向导生成结构化 commit
  - 实时质量评分
  - 快速模式支持
- 支持 018-Commit-Guided Documentation 优化点
  - 实现 Commit-as-Prompt 理念
  - 整合 Git 安全规范
  - 为文档自动更新提供基础工具

### Performance

- 所有新工具响应时间 <0.1 秒
- commit_parser 解析 100 个 commit <5 秒
- Token 优化效果超预期（85.91% vs 目标 30%）

## [1.2.0] - 2025-12-03

### Added

- 新增 `summary_extractor.py` & `.js` - 提取文档 YAML Frontmatter 摘要
- 新增 `summary_validator.py` & `.js` - 验证摘要格式、必填字段和关联文件存在性
- 新增 `summary_related_checker.py` & `.js` - 检测代码变更影响的文档（基于 related_files）
- 新增 `summary_index_generator.py` & `.js` - 生成文档摘要索引页（暂不启用）
- 支持 012-强制文档摘要机制，提升文档定位效率和更新准确性

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
