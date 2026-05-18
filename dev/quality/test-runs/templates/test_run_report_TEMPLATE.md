---
title: AICC 测试项目运行复盘模板
summary: 记录单个真实测试项目运行 AICC 后的产物、检查结果、失败点、框架根因和后续验证方式。
keywords: aicc | test-run | review | regression
scope: 单次真实项目 AICC 运行复盘
related_files: dev/quality/test-runs/README.md | dev/plan/README.md
dependencies: dev/quality/README.md | dev/quality/test-runs/README.md
verified_at: 2026-05-18
---

# AICC 测试项目运行复盘

## 1. 基本信息

- **测试项目**: [项目名称]
- **项目路径**: `[绝对路径或仓库相对路径]`
- **AICC commit**: `[commit hash 或分支状态]`
- **运行日期**: [YYYY-MM-DD]
- **用户指令原文**: `[粘贴或摘要，敏感内容需脱敏]`
- **运行阶段**: [首次生成 / Phase 1 复查 / 正式文档生成 / 首版验收 / 增量更新]

## 2. 生成产物

| 路径 | 状态 | 说明 |
| --- | --- | --- |
| `dev_docs/_analysis/generation_plan.md` | [生成/未生成/更新] | [说明] |

## 3. 复跑命令与结果

| tool | implementation | command | exit_code | issue_count | 结论 |
| --- | --- | --- | ---: | ---: | --- |
| summary_validator | python | `python3 tools/py/summary_validator.py --dir dev_docs --recursive --strict` | [n] | [n] | 只代表元数据/摘要格式 |
| doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | [n] | [n] | [结论] |
| semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | [n] | [n] | [结论] |

## 4. 失败点

| 优先级 | 问题 | 证据 | 框架归因 | 是否已转方案 |
| --- | --- | --- | --- | --- |
| P0 | [问题描述] | [文件/命令/输出] | [根因] | [是/否] |

## 5. 框架修复记录

| 修复项 | 涉及文件 | 验证方式 | 状态 |
| --- | --- | --- | --- |
| [修复项] | `[路径]` | `[命令]` | [未开始/进行中/已完成] |

## 6. Fixture 提炼

- **是否已提炼 fixture**: [是/否]
- **fixture 路径**: `[tools/testdata/... 或不适用]`
- **覆盖的 checker 测试**: [测试名称或不适用]

## 7. 后续验证方式

1. [重新运行指令或 checker 命令]
2. [预期结果]
