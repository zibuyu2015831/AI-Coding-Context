---
title: 综合样本主文档
summary: 用于 dogfood 的综合 dev_docs 样本，结构层完整，语义层故意包含几类可识别问题。
keywords: dogfood | semantic-review | doc-health | aicc
scope: tools/testdata/semantic_review/combined_case
related_files: README.md | tests/unit/test_root.py
dependencies: 无
verified_at: 2026-05-12
---

# AI 编码上下文

## 📊 项目概览

- 综合样本，仅用于 checker dogfood。

## 📂 关键目录速查

- `tests/` - 根测试目录
- `examples/book_rewriting/tests/` - 示例工程测试目录

## 🎯 场景快速导航

| 我要... | 参考文档 |
| --- | --- |
| 查看测试说明 | `testing_guide.md` |

## 🚀 文档索引

- [测试指南](./testing_guide.md)

## 💻 核心代码模式

- 不要调用 `session.commit()`。

## 🛠️ 开发流程规范

- 先写方案，再写文档。

## 📋 命名规范

- 目录全小写。

## 🏢 业务模块映射

- 当前样本仅包含测试相关模块。

## ⚠️ AI 编码禁忌

- 不要臆测不存在的目录。

## 🔧 常见任务速查

- 运行测试前先看 `testing_guide.md`。
