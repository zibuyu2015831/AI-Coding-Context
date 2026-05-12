---
title: "ADR-002: 分层文档架构"
summary: "定义主文档 (AI_Coding_Context.md) 与子文档 (dev_docs/*.md) 的分工与加载边界"
keywords: adr | architecture | layered | docs
scope: "全局系统架构"
related_files: "/AI_ENTRY_POINT.md | templates/AI_Coding_Context_TEMPLATE.md"
dependencies: "dev/architecture/decisions/001-markdown-as-first-class-doc.md"
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

# ADR-002: 分层文档架构

## 1. 决策信息
- **日期**: 2026-04-12
- **状态**: 已接受 (Accepted)
- **参与者**: AICC Framework Team

## 2. 背景与上下文 (Context)
随着大型项目的迭代，AI 对项目整体背景的学习会带来极其庞大的 Token 负担。在早期的 V1.x/V2.x 尝试中，将所有的 API、数据库 Schema、交互逻辑甚至业务演进放入一个巨型文档会导致 AI “认知过载（Cognitive Load）”，不仅使得对话初始化极慢，而且在生成代码时更容易忽略其中某些微小的角落，导致产生错误代码。

## 3. 决策 (Decision)
为了彻底解决大项目上下文超载难题，框架强推“分层文档架构”范式：
1. 项目根目录仅保留唯一的索引与顶层架构入口文档：`AI_Coding_Context.md`（主文档，上限控制在 500-800 行左右）。
2. 在 `dev_docs/` 目录下按具体的领域或特性存放详细子文档（如 `api_layer.md`、`configuration.md`）。
3. 主文档通过提供场景式的超链接索引，指引 AI 去按需 (On-Demand) 加载对应的子文档。

## 4. 替代方案考量 (Considered Alternatives)
- **[方案 A] 拆分出多个同等重要的入口文档，例如 Frontend.md 和 Backend.md**
  - **为何拒绝**: 对于 Fullstack 或者 Monorepo 项目，多个零散的入口会让 AI 面对第一句指令时出现“不知道先看哪个”的盲区。维护一个不可撼动的“唯一索引入口”对于确定性的 Agent 状态流转是必须的。
- **[方案 B] 放在代码注释里而不是写外部文档**
  - **为何拒绝**: 虽然 JSDoc/Python Docstring 极有价值，但也只能涵盖微观的函数边界，无法跨文件阐明整个子系统的运行机制和高层设计约束。

## 5. 影响分析 (Consequences)
- **正面影响**:
  - 系统具备无限扩展性：每个子文档独立演进，修改隔离度好（变更不会引起冲突）。
  - Token 大幅节省：单次加载不需要阅读所有不相关子系统的细节。
- **负面影响**:
  - 新建或重构一个跨界大特性时，需要 AI/开发者跨越多个文档，修改 `AI_Coding_Context.md` 的索引及数个子文档。

## 6. 架构断言 (Architecture Assertions / AaC)

```yaml
constraints:
  - type: "documentation_only"
    note: "根目录下必须有且仅有 `AI_Coding_Context.md` 是全局级指导规范；其余的详细设计文档一律下放至 `dev_docs/`。"
```
