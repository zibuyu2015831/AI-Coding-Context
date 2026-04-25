---
title: 文档引用审查报告
summary: 全项目 305 个 Markdown 文档的跨文档引用审查全程记录。两批共修复 32 处确定性失效引用 + 新建 1 个文件 + 给案例样本加顶部说明。所有 P1/P2 项已处理完毕。
scope: 全项目（含 dev/）
audit_date: 2026-04-25
auditor: AI（6 个并行子代理扫描 + 主线程逐条核验）
status: 已完结
---

# 文档引用审查报告

## 审查方法

- **范围**：项目内全部 305 个 `.md` 文件，含 `dev/` 目录
- **引用定义**：仅文档间的相互引用；外部 URL 不在范围
- **修复政策**（用户最终拍板）：
  - **dev/ 内**：FRAMEWORK_CONTEXT 必须 100% 准确；其余可"修复或删除"
  - **dev/ 外**：缺失文件需站在全局角度阅读相关文档后**补全**
- **已剔除范围**：
  - `dev/reference/ai-coding-prompt-java-main/` 内部互引（vendored sub-project）
  - `.py` / `.js` 等非文档文件的引用
  - markdown 代码块内的"示例引用"（不是真实链接，是教学/演示性内容）

---

## 修复总账

| 批次 | 类型 | 数量 | 文件数 |
|------|------|------|--------|
| Batch 1 (commit `457a4f9`) | 路径修正 | 22 处 | 11 个 |
| Batch 2 (本次)             | 路径修正 + 重指向 + 删除 | 13 处 | 11 个 |
| Batch 2 (本次)             | 新建文件 | 1 个   | — |
| Batch 2 (本次)             | 加顶部说明 | 1 处 | 1 个 |
| **合计**                   | — | **35 处操作** | **17 个文件 + 1 新文件** |

---

## Batch 1 已修复（22 处）

详见 commit `457a4f9 refactor(refs): 引用清理 Batch D：22 处确定性失效引用修复 + 审查报告`。涉及：
- `.kiro/specs/post-generation-audit/QUICK_START.md`：3 处路径深度差 1
- `dev/FRAMEWORK_CONTEXT.md:746`：`../quality/README.md` → `./quality/README.md`
- `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md`：3 处同目录引用应为兄弟目录（含 001→013 编号笔误）
- `dev/V3.0/confirmed/011|012|013/*.md`：8 处系统性路径深度错
- `dev/real_case/002/quality_review/*.md`：4 处指向 workflows/templates/FRAMEWORK_CONTEXT 的深度错
- `workflows|guides/generation_workflow.md`：4 处"参考资源"块的 ./ 应为 ../

---

## Batch 2 已修复（本次）

### A. 路径修正（13 处）

| # | 文件 | 行 | 修改 |
|---|------|----|------|
| 1 | `dev/FRAMEWORK_CONTEXT.md` | 744 | `[reference/design_decisions.md](../reference/...)` → `[core/design_decisions.md](../core/...)`（链接文本与路径同步） |
| 2 | 同上 | 745 | 同模式：`reference/SUMMARY_FORMAT_SPEC.md` → `core/SUMMARY_FORMAT_SPEC.md` |
| 3 | `dev/V3.0/confirmed/014-doc-reading-habit-guide/014-doc-reading-habit-guide.md` | 476 | `../../reference/design_decisions.md` → `../../../../core/design_decisions.md`（同 1） |
| 4 | `dev/V3.0/confirmed/010-cross-project-knowledge/self-evolution-system.md` | 1024 | `../FRAMEWORK_CONTEXT.md` → `../../../FRAMEWORK_CONTEXT.md` |
| 5 | 同上 | 1025 | `../DISCUSSION_CONTEXT.md` → `../../DISCUSSION_CONTEXT.md` |
| 6 | `dev/V3.0/confirmed/010-cross-project-knowledge/cli-commands.md` | 596 | `../tools/README.md` → `../../../../tools/README.md` |
| 7 | `dev/V3.0/confirmed/016-unified-config-system/016-unified-config-system.md` | 226 | `../../AI_ENTRY_POINT.md` → `../../../../AI_ENTRY_POINT.md` |
| 8 | 同上 | 227 | `../../README.md` → `../../../../README.md` |
| 9 | 同上 | 228 | 删除"[优化点 016](../../dev/V3.0/confirmed/016-unified-config-system/)"自引行（路径错且自指无意义） |
| 10 | `dev/V3.0/archived/015-quality-assurance-system.md` | 317 | `../../workflows/document_health_check.md` → `../../../workflows/document_health_check.md` |
| 11 | 同上 | 318 | `./011-doc-error-fix-workflow.md` → `../confirmed/011-doc-error-fix-workflow/011-doc-error-fix-workflow.md` |
| 12 | 同上 | 319 | `./012-mandatory-doc-summary.md` → `../confirmed/012-mandatory-doc-summary/012-mandatory-doc-summary.md` |
| 13 | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` | 270 | `./_templates/agent_template.md` → `../../../../agents/_templates/agent_template.md`（指向真实存在的 agents/_templates/） |

### B. 二次修正 Batch 1 中的次优解（4 行）

之前 Batch 1 把 `[文档体系规范](./README.md)` 修复为 `(../README.md)`，但语义不对——repo 根 README.md 是项目介绍，并非"文档体系规范"。`core/framework_spec.md` 的标题字面就是"AI 辅助开发文档体系规范"，是真正的目标。同时同块的 STRUCTURE_SPEC.md 全仓不存在，删除该行：

| # | 文件 | 行 | 修改 |
|---|------|----|------|
| 14 | `workflows/generation_workflow.md` | 1089 | `[文档体系规范](../README.md)` → `[文档体系规范](../core/framework_spec.md)` |
| 15 | 同上 | 1090 | 删除 `- [结构规范](./STRUCTURE_SPEC.md)`（全仓无此文件，且 framework_spec.md 已含"标准目录结构"章节） |
| 16 | `guides/generation_workflow.md` | 594 | 同 14 |
| 17 | 同上 | 595 | 同 15 |

### C. 修复编号错位（1 个文件 2 行）

| # | 文件 | 行 | 修改 |
|---|------|----|------|
| 18 | `agents/_progress/implementation_progress.md` | 3 | `**项目**: 013 - AI 角色库实施` → `**项目**: 001 - AI 角色库实施`（实际项目编号是 001，013 是 ai-mutual-review） |
| 19 | 同上 | 5 | `[013-ai-agent-library-implementation.md](../../../dev/V3.0/confirmed/013-ai-agent-library-implementation.md)` → `[001-ai-agent-library/implementation.md](../../dev/V3.0/confirmed/001-ai-agent-library/implementation.md)`（同时修正深度差 1） |

### D. 新建文件（1 个）

`agents/examples/product_manager_examples.md` —— 按 `api_designer_examples.md` 同款双示例结构（场景说明 / 用户输入 / 角色响应 / 关键点说明），结合 `product_manager.md` 的角色定义补全。例子包括"明确功能请求（密码重置）"和"模糊需求收敛（提升体验）"两种典型 PM 场景。

### E. 顶部说明（1 处）

`dev/real_case/002/AI_Coding_Context.md` —— 在 H1 后插入醒目 callout，说明本文是为 Claude Code（Anthropic）项目生成的样本，所有外链面向那个项目假设的目录结构，在本仓库内无法跳转是**预期行为**。原文链接均保留不动（因为这些是案例的核心展示内容，删除会破坏样本完整性）。

---

## 子代理误判校正记录（透明度）

| 来源 | 误判内容 | 实际情况 |
|------|---------|---------|
| Agent 3 | 把 `guides/project_types.md:275` 的 `[API Reference](./api_reference.md)` 标为 P1 broken | 该行在 `````markdown` 代码块内，是"库 SDK 项目主文档应包含的章节"示例内容，不是真实链接。**P3 / 无需修改** |
| Agent 4 | 把 `dev/FRAMEWORK_CONTEXT.md:746` 的 `../quality/README.md` 归为 ANCHOR_ONLY | 实际是路径错误（少 `dev/` 前缀），是 CERTAIN_FIX。已在 Batch 1 修复 |
| Agent 5 | 把 V2.3 的 7 处 `./workflows/...`、`./core/...` 归为 P2 历史失效 | 这 7 处全部在 markdown 代码块内（写给 AI_ENTRY_POINT.md 的示例片段），是 P3 教学内容，不是真实链接。**无需修改** |
| Agent 5 | 把 V3.0/confirmed 多文件的 `../../workflows/...` 归为 UNCERTAIN | 实际是系统性路径深度错（应为 `../../../../`），目标全部存在。Batch 1+2 已批量修复 |
| Agent 6 | 把 `dev/real_case/002/AI_Coding_Context.md` 内 17+ 处引用归为 CERTAIN_FIX | 该文件是为 Claude Code 项目生成的样本，引用面向那个项目结构，不是失效引用。Batch 2 加顶部说明而非修改链接 |

---

## P3：模板/示例性引用（保留）

以下引用是**设计上的占位符或示例**，不是真实失效，按用户指示**整体保留**：

- `core/framework_spec.md:196-208` —— 规范示例（演示 plan 文档命名）
- `templates/AI_Coding_Context_TEMPLATE.md:110, 192, 215, 231, 258` —— 模板内占位（用户复制后才会有真实路径）
- `templates/{generation_plan_*,GENERATION_PLAN_TEMPLATE}.md:143` 及 `dev/real_case/001/generation_plan.md:140`、`dev/reference/生产级Vue3文档体系方案.md:104` —— 引用规则示例
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md:495-496`、`templates/plans_README_TEMPLATE.md:129` —— 模板示例
- `agents/_templates/agent_template.md:114, 128, 132, 136` —— 模板占位符
- `agents/workflows/understanding_guardian.md:117, 138, 164, 185` —— Agent 提示词内的"示例输出"
- `workflows/path_b_health_check.md:339, 343` —— Mock 健康检查输出
- `workflows/monorepo_workflow.md:230, 237, 244, 279, 280, 281` —— Monorepo 用法示例
- `dev/V3.0/confirmed/001-ai-agent-library/implementation.md:440, 676, 754` —— `角色名_examples.md` 占位
- `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md:230-248` —— 结构定义示例
- V2.3 的 7 处代码块内引用（写给 AI_ENTRY_POINT.md 的示例片段）
- `guides/project_types.md:275` 等 markdown 代码块内的库 SDK 项目示例内容

---

## 出范围说明

- **外部 URL** —— 用户明确不要求验证
- **`.py` / `.js` 等代码文件**的引用（如 `tools/py/git_diff_analyzer.py`、`tools/install_hooks.js`）
- **`dev/reference/ai-coding-prompt-java-main/`**：vendored sub-project，内部引用不审查
- **代码块内的示例引用**：教学/演示性内容，不是真实链接

---

## 复盘要点

1. **子代理判断不可全信**：6 个 Explore 子代理一起跑出 100+ 候选项，主线程逐条核读后，**约 30% 的"CERTAIN_FIX"是误判**（多为代码块内示例被识别成真实链接），约 20% 的"UNCERTAIN"实为可机械修复的 CERTAIN_FIX（系统性路径深度错）。
2. **路径深度错是最高频问题**：V3.0/confirmed/ 下 5+ 个文件用了一致的"少 2 级"或"少 1 级"路径模式，疑似从浅层位置批量复制时未更新 `../`。
3. **链接文本与路径不一致是另一类隐患**：FRAMEWORK_CONTEXT.md 的 "reference/design_decisions.md" 链接文本明明叫 reference/，实际目标在 core/，导致诊断难度上升。
4. **样本/模板类文档需要明确标注**：`real_case/002/AI_Coding_Context.md` 这类样本如不加 disclaimer，容易被工具/读者当作普通文档对待，浪费审查精力。

后续若再做此类审查：
- 优先用 grep 模式扫描"路径深度错"的常见 pattern
- 对子代理报告中"目标文件不存在"的项，优先怀疑路径深度错而非"文件被删除"
- 给 case study / sample 类文件统一加 frontmatter 标志（如 `is_sample: true`），方便工具识别
