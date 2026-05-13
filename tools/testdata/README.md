---
title: 测试数据目录说明
summary: 说明 AICC 工具测试数据的目录约定、命名规范和各 case 的用途，便于后续为 checker 增加回归样本。
keywords: testdata | checker | regression | fixtures | aicc
scope: tools/testdata 目录说明
related_files: tools/py/tests/test_framework_contract_checker.py | tools/py/tests/test_semantic_review_checker.py | tools/js/framework_contract_checker.test.js | tools/js/semantic_review_checker.test.js
dependencies: 无
verified_at: 2026-05-12
---

# 测试数据目录说明

`tools/testdata/` 用于承载 checker 的回归样本。每个 case 都应同时表达：

- 输入内容是什么
- 预期要触发或避免什么问题
- 这个 case 服务于哪个 checker / 哪条规则

## 目录约定

- `framework_contracts/`: 契约与 workflow 漂移相关样本
- `semantic_review/`: 量化声明、事实冲突、测试资产拓扑相关样本
- `doc_health/`: 结构健康、运行记录、模板残留相关样本

## 命名规则

- 目录名必须直接表达意图，例如 `missing_sections_template`、`metric_drift_case`
- 不使用 `sample1`、`demo` 之类弱语义命名
- 如 case 同时包含输入与说明，优先使用 `README.md` 描述预期
