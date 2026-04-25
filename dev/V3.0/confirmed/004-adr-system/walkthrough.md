# 004 ADR 系统 - 实施产出与验证指南

本文档总结了 004-ADR 架构决策记录系统的实施成果，并提供标准化的验证场景以确保系统功能的正确性与稳定性。

## 🎯 实施产出摘要

### 1. 📂 目录结构与规范
- **Active 区**: `dev_docs/architecture/decisions/` - 存放生效中的架构协议。
- **Archived 区**: `dev_docs/architecture/decisions/archived/` - 隔离已废弃决策，防止 AI 检索污染。
- **模板**: `dev_docs/architecture/adr-template.md` - 包含 Frontmatter 规范、冲突检查清单及 AaC (架构即代码) 约束槽。
- **可视化**: `dev_docs/architecture/evolution.md` - 基于 Mermaid 的时序/依赖演进图谱。

### 2. 🔄 工作流挂载 (V3.0 深度集成)
- **生成端拦截**: `workflows/generation_workflow.md` 已植入「架构阈值评估」卡口，强制 AI 在重大变更前起草 ADR。
- **审查端卡控**: `workflows/review-workflow.md` 已植入「5.3 ADR 符合性审查」，要求 AI 在互审时作为“架构警察”阻断违规实现。

### 3. 🛠️ 支持工具链 (Dual-Engine: Py/JS)
- **探针工具**: `why_tool.py` & `why_tool.js` - 支持 L1 注解提取与模糊关键字匹配，解决“为何这样做”的认知盲点。
- **断言工具**: `aac_validator.py` & `aac_validator.js` - 自动提取 ADR 中的 YAML 约束并对物理文件执行静态查杀。

---

## 🔍 验证场景

### 场景 A: 架构阈值触发
**操作**: 模拟一个涉及重大技术选型变更的需求（如“将现有的 REST 协议全面替换为 GraphQL”）。
**预期结果**:
1. AI 在「设计思维引导 Step 5」输出时，勾选「涉及跨越架构阈值的核心决策」。
2. AI 明确提示：在生成详细实施计划前，必须基于模板起草一份新 ADR。

### 场景 B: 架构符合性阻断 (AI 互审)
**操作**: 提交一份代码，故意违反已有的 ADR 约束（例如：ADR-001 规定文档必须是 Markdown，尝试在 `dev_docs` 下新增一个 Word 文档）。
**预期结果**:
1. AI 执行互审时，识别到 `dev_docs/architecture/decisions/001-markdown-as-first-class-doc.md` 的约束。
2. 审查报告给出 **⛔ 驳回** 意见，标记为 P0 问题，并指出违背了 ADR-001。

### 场景 C: 使用 Why-Tool 溯源背景
**操作**: 运行工具查询特定代码的设计意图。
**示例命令**: `python tools/py/why_tool.py --query "分层文档"`。
**预期结果**:
1. 工具应能精准定位到 `002-layered-documentation.md`。
2. 输出包含该决策的 Title 和 Summary，帮助 AI/人类快速对齐背景。

### 场景 D: AaC 自动化静态拦截
**操作**: 在 `dev_docs` 下创建一个非 `.md` 的文件，然后运行验证器。
**示例命令**: `node tools/js/aac_validator.js`。
**预期结果**:
1. 验证器解析 ADR-001 中的 `regex_check` 约束。
2. 输出 `❌ Found architecture violation(s)`，准确指回违规文件及对应的 ADR 来源。

---

## 验证记录表

| 场景 | 修改日期 | 结果 | 备注 |
| :--- | :--- | :--- | :--- |
| A: 阈值触发拦截 | 2026-04-12 | ✅ 通用 | 已在 AICC 自举流程中通过方案审核验证 |
| B: 互审符合性卡控 | 2026-04-12 | ✅ 通过 | 逻辑已挂载至 review-workflow |
| C: Why-Tool 检索精度| 2026-04-12 | ✅ 通过 | 双语言版本均能准确提取关键字相关 ADR |
| D: AaC 静态查杀拦截 | 2026-04-12 | ✅ 通过 | 能够识别 ADR 代码块中的 YAML 约束 |

---
**版本**: v1.0  
**维护者**: Framework Team
