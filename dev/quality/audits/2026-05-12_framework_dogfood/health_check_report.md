---
title: 2026-05-12 Framework Dogfood Health Check Report
summary: 记录 P1 新增 checker 在 AICC 框架内的一次自审 dogfood；覆盖契约自检、结构健康检查、语义复查与误报修正结果。
keywords: dogfood | health-check | semantic-review | framework-contract | aicc
scope: AICC 框架 P1 checker 自审
related_files: tools/py/framework_contract_checker.py | tools/js/framework_contract_checker.js | tools/py/doc_health_checker.py | tools/js/doc_health_checker.js | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js | tools/testdata/semantic_review/combined_case/dev_docs/AI_Coding_Context.md
dependencies: framework_improvement_implementation_plan.md | templates/HEALTH_CHECK_REPORT_TEMPLATE.md
verified_at: 2026-05-12
---

# 2026-05-12 Framework Dogfood Health Check Report

## 📊 总体结论

- 检查时间: 2026-05-12
- 检查范围: `AI-Coding-Context` 框架自身 + `tools/testdata/semantic_review/combined_case/dev_docs`
- 最终 verdict: PASS
- 结论说明: P1 新增 checker 已可运行、可被 workflow 消费，并在 dogfood 中暴露出 2 个真实框架误报，已当场修复。

## 1. 执行命令

```bash
python3 -m unittest tools/py/tests/test_framework_contract_checker.py
python3 -m unittest tools/py/tests/test_doc_health_checker.py
python3 -m unittest tools/py/tests/test_semantic_review_checker.py
node tools/js/framework_contract_checker.test.js
node tools/js/doc_health_checker.test.js
node tools/js/semantic_review_checker.test.js
python3 tools/py/framework_contract_checker.py --self-check --format text
node tools/js/framework_contract_checker.js --self-check --format text
python3 tools/py/doc_health_checker.py --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs
node tools/js/doc_health_checker.js --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs --repo-root tools/testdata/semantic_review/combined_case
node tools/js/semantic_review_checker.js --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs --repo-root tools/testdata/semantic_review/combined_case
python3 tools/py/semantic_review_checker.py --check-test-topology --doc-dir tools/testdata/semantic_review/test_topology_case/dev_docs --repo-root tools/testdata/semantic_review/test_topology_case
node tools/js/semantic_review_checker.js --check-test-topology --doc-dir tools/testdata/semantic_review/test_topology_case/dev_docs --repo-root tools/testdata/semantic_review/test_topology_case
```

## 2. 契约自检结果

- `framework_contract_checker`（Python / JS）: PASS
- 模板必需章节: PASS
- workflow 路径漂移: PASS

说明：此前自检曾报出 `AI_Coding_Context_TEMPLATE.md` 的 `文档索引` 标题不一致，以及 `generation_workflow.md` 把 `review/` 当标准产物的遗留表述；本轮 dogfood 前已修复，因此当前为 PASS。

## 3. 结构健康检查结果

- `doc_health_checker`（Python / JS）对 `combined_case/dev_docs` 的 `--full-check`: PASS
- 文件路径检查: PASS
- frontmatter 检查: PASS
- 主文档必需章节检查: PASS
- 运行记录完整性检查: PASS
- 模板残留检查: PASS

### 本轮 dogfood 发现并修复的误报

1. `_analysis/generation_plan.md` / `generation_progress.md` 被错误要求带 YAML frontmatter
2. `generation_progress.md` 中的 `已完成数` 被错误当成“当前状态已完成”，从而误报缺少 `health_check_report`

### 修正结论

- `_analysis/` 过程资产不再纳入 frontmatter 严格校验
- `health_check_report` 留痕只在 `当前状态: 已完成` 时强制要求

## 4. 语义复查结果

### 综合样本 `combined_case`

- `fact_conflicts`: 1
  - `AI_Coding_Context.md` 写了“不要调用 `session.commit()`”
  - `README.md` 权威源写了“必须调用 `session.commit()`”
- `metrics`: 1
  - `testing_guide.md` 声明“1 个测试文件”，实际扫描为 2 个
- `test_topology`: 0
  - 原因：综合样本主文档已显式覆盖 `examples/book_rewriting/tests/` 目录，因此不应报错

### 拓扑专项样本 `test_topology_case`

- `test_topology`: 1
  - `examples/book_rewriting/tests/` 未被文档覆盖，正确报出 `uncovered_test_topology`

## 5. 阈值与默认模式结论

- `framework_contract_checker --self-check` 适合作为框架维护与发布前检查
- `doc_health_checker --full-check` 默认启用结构类检查是合理的
- `semantic_review_checker --full-check` 适合作为首版交付 gate 与 Path B 标准/深度检查的补充，不建议替代基础健康检查
- 当前第一版规则没有出现大面积噪音，不需要再收缩默认扫描范围

## 6. 结果判断

- 框架契约层: 可运行、可自检
- 结构健康层: 可稳定通过合法样本，且已修复 dogfood 暴露的误报
- 语义复查层: 已能稳定覆盖事实冲突、量化失真、测试拓扑遗漏三类问题

## 7. 后续动作

- 将本次 dogfood 作为 P1 完成证据保留
- 后续进入 P2 前，可再找一个真实项目 `dev_docs/` 进行一次跨仓库试跑
