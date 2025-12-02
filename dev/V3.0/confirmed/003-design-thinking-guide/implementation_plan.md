# 实施方案: 003 - 设计思维引导模式

**对应优化点**: [003-design-thinking-guide.md](./003-design-thinking-guide.md)  
**优先级**: P0  
**状态**: 🟡 待实施  
**负责人**: Framework Team

---

## 1. 目标描述

本实施方案旨在将 "设计思维引导模式" 集成到 AI Coding Context 框架中。通过引入专家团队（Facilitator, PM, Architect, QA）和 5 步引导流程，将 AI 从单纯的代码生成器升级为具备深度思考能力的架构顾问。

核心交付物包括：

1.  **新增 AI 角色**: `design_facilitator`, `product_manager`。
2.  **工作流集成**: 在 `AI_ENTRY_POINT.md` 中增加触发逻辑。
3.  **规则更新**: 在 `AI_RULES.md` 中增加强制引导规则。
4.  **示例库**: 提供完整的用户登录功能设计示例。

---

## 2. 实施步骤

### 阶段 1: 角色定义 (Role Definition)

**目标**: 建立专家团队的基础角色文件。

- [ ] **创建 `agents/runtime/design_facilitator.md`**
  - 职责: 流程编排、洞察整合、冲突解决。
  - 关键技能: `facilitate_discussion`, `synthesize_insights`, `resolve_conflict`。
- [ ] **创建 `agents/development/product_manager.md`**
  - 职责: 价值分析、验收标准定义。
  - 关键技能: `5_why_analysis`, `define_success_criteria`。
- [ ] **验证现有角色**
  - 确认 `agents/development/architecture_analyst.md` 是否具备方案对比能力。
  - 确认 `agents/runtime/test_engineer.md` 是否能制定测试策略。

### 阶段 2: 工作流实现 (Workflow Implementation)

**目标**: 实现 5 步引导的核心逻辑和 Prompt。

- [ ] **开发 Prompt 模板**
  - `templates/prompts/design_thinking/step1_why.md` (PM)
  - `templates/prompts/design_thinking/step2_how.md` (Architect)
  - `templates/prompts/design_thinking/step3_risk.md` (Architect & QA)
  - `templates/prompts/design_thinking/step4_reflection.md` (Facilitator)
  - `templates/prompts/design_thinking/step5_decision.md` (Facilitator)
- [ ] **实现自动触发逻辑**
  - 复用 013 的复杂度评估脚本。
  - 编写触发判断逻辑 (Threshold > 60)。

### 阶段 3: 框架集成 (Framework Integration)

**目标**: 将功能接入框架主流程。

- [ ] **更新 `AI_ENTRY_POINT.md`**
  - 在 "方案生成" 节点前插入 "设计思维引导" 检查点。
  - 解析 `@think` 系列指令。
- [ ] **更新 `AI_Coding_Context.md`**
  - 补充 "设计思维引导" 核心概念。
- [ ] **更新 `AI_RULES.md`**
  - 添加 P0 规则: "Complex Task requires Design Thinking"。

### 阶段 4: 示例建设 (Example Construction)

**目标**: 提供最佳实践参考。

- [ ] **创建 `agents/examples/design_thinking/user_login_flow.md`**
  - 模拟一个完整的对话过程。
  - 展示 PM 如何追问价值。
  - 展示 Architect 如何对比 "JWT vs Session" 方案。
  - 展示 QA 如何补充 "Token 泄露" 测试用例。

---

## 3. 验证计划

### 自动化验证

- 运行 `tools/py/complexity_check.py` (假设存在或需新增) 验证复杂度评估逻辑。
- 验证 `@think` 指令解析的正则表达式。

### 手动验证 (Walkthrough)

1.  **场景 1: 简单任务 (Fix typo)**
    - 输入: "Fix typo in README"
    - 预期: 自动跳过引导，直接生成代码。
2.  **场景 2: 复杂任务 (Add Payment)**
    - 输入: "Add Stripe payment support"
    - 预期: 自动触发引导询问 "检测到复杂任务..."。
3.  **场景 3: 强制引导**
    - 输入: "@think:deep Refactor Auth module"
    - 预期: 启动深度辩论模式。

---

## 4. 用户审查记录

- [ ] 角色定义确认
- [ ] Prompt 模板确认
- [ ] 框架集成点确认
