---
title: "ADR-XXX: [决策标题]"
summary: "[一句话描述决策的核心内容与背景]"
keywords: adr | architecture | [关键字1] | [关键字2]
scope: "[受该决策影响的系统、模块或边界范围]"
related_files: "[受影响的关键源文件路径或其他规范文档]"
dependencies: "[依赖的前置 ADR 编号或文件名，无则留空]"
verified_at: YYYY-MM-DD
level: "core | domain | detail"
domain: "global | frontend | backend | devops | [自定义]"
year: YYYY
---

> **创建 ADR 前的强制检查清单**
> - [ ] 我已搜索现有 ADR，确认无重复主题。
> - [ ] 我已检查依赖的 ADR（在 frontmatter 的 dependencies 中列出）均处于 Active 状态。
> - [ ] 我已验证本决策不与任何 Active ADR 冲突。
> - [ ] 如有潜在冲突，我已在“替代方案考量”中说明了处理策略（例如调整自身范围或对旧决策发起取代更新）。

# ADR-XXX: [决策标题]

## 1. 决策信息
- **日期**: YYYY-MM-DD
- **状态**: 提案 (Proposed) / 已接受 (Accepted) / 已废弃 (Deprecated) / 已替代 (Superseded by ADR-YYY)
- **参与者**: [发起人与审核人的名字或 AI 角色]

## 2. 背景与上下文 (Context)
[为什么需要这个决策？描述当前面临的痛点、特定的技术限制，以及促使我们做出改变的核心驱动力。可以引用之前的问题或是某些发现的技术债。]

## 3. 决策 (Decision)
[明确说明我们最终决定做什么。如果需要，提供必要的代码范式和工程规约。]

## 4. 替代方案考量 (Considered Alternatives)
- **[方案 A]**: [简单描述]
  - **为何拒绝**: [优缺点对比分析，特别是它的劣势如何触发了我们的底线。例如：为何其未能解决当前的主要痛点。]
- **[方案 B]**: [简单描述]
  - **为何拒绝**: [同上]

## 5. 影响分析 (Consequences)
- **正面影响**:
  - [例如：解耦了UI和状态层，组件渲染性能增加等]
- **负面影响**:
  - [例如：项目初期样板代码变多，需额外维护一层中间件等]

## 6. 架构断言 (Architecture Assertions / AaC)
*[可选] 使用 YAML 片段定义本决策的机器可读约束，用于通过脚本实现初步的安全拦截或作为 AI 互审的判断准则。*

```yaml
constraints:
  - type: "documentation_only"
    note: "此处声明对人类和 AI 的期望规范，实际硬性拦截规则可在后续 Phase 落地。"
    # 示例规则：
    # forbidden_patterns: ["any", "ts-ignore"]
    # required_dependencies: ["zod", "trpc"]
```
