---
title: "ADR-001: 文档第一性原理 (Markdown)"
summary: "决定所有 AICC 框架与用户工程文档均采用 Markdown 纯文本格式作为第一级语言载体。"
keywords: adr | architecture | markdown | format
scope: "全局系统架构"
related_files: "dev/FRAMEWORK_CONTEXT.md"
dependencies: ""
verified_at: "2026-04-12"
level: "core"
domain: "global"
year: 2026
---

> **创建 ADR 前的强制检查清单**
> - [x] 我已搜索现有 ADR，确认无重复主题。
> - [x] 我已检查依赖的 ADR（在 frontmatter 的 dependencies 中列出）均处于 Active 状态。
> - [x] 我已验证本决策不与任何 Active ADR 冲突。
> - [x] 如有潜在冲突，我已在“替代方案考量”中说明了处理策略。

# ADR-001: 文档第一性原理 (Markdown)

## 1. 决策信息
- **日期**: 2026-04-12
- **状态**: 已接受 (Accepted)
- **参与者**: AICC Framework Team

## 2. 背景与上下文 (Context)
在建设 AICC (AI Coding Context) 框架时，我们需要一种能在人类开发者和多种大语言模型（LLMs）之间都能顺畅流转的通用知识载体。不仅要解决“可展示”的需求，还要能进行 diff 比对、方便基于工具化分析。过去有许多图文并茂的方案（如 Office，Confluence，Notion），但它们要么无法用 Git 做精细粒度版本控制，要么因为携带过多不可见标签，对消耗 Token 和误导 AI 构成挑战。

## 3. 决策 (Decision)
因此，框架做出一项根本性决定：所有文档（包括架构说明、互审流程、代码上下文规则、配置）都必须且仅能使用 Markdown 纯文本格式。
这包含了所有补充协议：如需要表格时必须用 Markdown table，需要流程图时采用内嵌的 Mermaid 图表语法。

## 4. 替代方案考量 (Considered Alternatives)
- **[方案 A] XML 或 JSON 配置文件为骨干，Markdown 为辅助**
  - **为何拒绝**: XML 或 JSON 对人员书写与检阅不够友好。大段的解释性内容放到 JSON Value 里难于阅读，而且难以处理换行和超链接等排版。这会阻断“人类和AI友好互换”的桥梁。
- **[方案 B] 仅在特定的项目阶段产出 PDF/HTML 报告**
  - **为何拒绝**: 静态产物无法进行 Git Diff 管理。在 Vibe Coding 的时代背景下，文档是随着每一次 commit 迭代更新的“活水”，PDF 无法实现这种连续增量更新。

## 5. 影响分析 (Consequences)
- **正面影响**:
  - 全面 Git 友好，任何人/AI 都可以轻松审查文档的变化 (PR)。
  - 对 AI 最友好，所有预训练大模型对 Markdown 拥有极高的结构识别和代码解析能力，节约解析 Token 成本。
- **负面影响**:
  - 表示高度复杂的交互式图表或深层嵌套 UI 时，受到 Mermaid 或普通 ASCII 的表现力限制。

## 6. 架构断言 (Architecture Assertions / AaC)

```yaml
constraints:
  - type: "documentation_only"
    note: "所有生成到 dev_docs 目录下的解释性知识必须是 .md 文件。"
  - type: "regex_check"
    pattern: "\\.(docx?|pdf|pptx?)$"
    forbidden_in: ["dev_docs/**"]
    message: "请不要在 dev_docs 下引入二进制格式或专有格式文档，只能使用 Markdown (.md)。"
```
