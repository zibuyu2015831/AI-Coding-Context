---
title: AICC 测试项目复盘归档规范
summary: 定义 Dayflow、LinguaCafe、Memex 等真实项目复测结果的归档位置、记录字段和与优化方案文档的分工。
keywords: aicc | test-runs | regression | archive | review
scope: AICC 框架在真实测试项目上的运行复盘归档
related_files: dev/plan/README.md | dev/quality/test-runs/templates/test_run_report_TEMPLATE.md
dependencies: dev/quality/README.md | dev/quality/standards/QUALITY_CHECKLIST.md
verified_at: 2026-05-18
---

# AICC 测试项目复盘归档规范

本目录用于保存真实项目复测的原始记录和可回放依据。`dev/plan/` 只保留由复测问题转化出的框架优化方案；原始终端输出、复跑命令、检查结果和样本说明应沉淀到本目录。

## 归档边界

每次使用真实项目测试 AICC 时，应按以下目录结构归档：

```text
dev/quality/test-runs/<project>/<YYYY-MM-DD>/
```

建议文件：

- `run_report.md`: 本次运行复盘主记录，使用 `templates/test_run_report_TEMPLATE.md`。
- `terminal_output.md`: 用户或 AI 提供的终端摘要，必要时脱敏。
- `checker_results/`: 可选，保存 `doc_health_checker`、`semantic_review_checker`、`summary_validator` 的 JSON 输出。
- `fixture_notes.md`: 可选，说明是否已经提炼成 checker fixture。

## 必填字段

每份 `run_report.md` 必须记录：

- 测试项目路径。
- AICC commit 或分支状态。
- 用户指令原文。
- 生成产物清单。
- 复跑命令。
- 失败点。
- 框架根因。
- 已实施的框架修复。
- 未实施的后续任务。
- 后续验证方式。

## 与优化方案的关系

当复测暴露框架问题时：

1. 原始事实和可回放证据进入 `dev/quality/test-runs/`。
2. 框架修复要求进入 `dev/plan/` 中的具体优化方案。
3. 若问题可自动检测，应优先提炼为 `tools/testdata/` fixture 和 checker 测试。
4. 完成修复后，在对应 `run_report.md` 和方案文档中写明实现状态与验证命令。
