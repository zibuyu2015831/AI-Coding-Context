# 003 - 设计思维引导模式 (Design Thinking Guide)

**优先级**: P0  
**状态**: 🟢 已确认  
**确认日期**: 2025-12-02
**预估工作量**: 1 周  
**来源**: 《AI 编程的现状.md》方法 3 + 《AI_PROGRAMMING_ANALYSIS.md》 + `other_project/深度思考设计.md`  
**依赖**: 001 (AI 角色库) - 需要 ProductManager, ArchitectureAnalyst, TestEngineer 角色

---

## 📋 问题描述

### 核心痛点

1.  **AI 沦为"代码生成器"**: 缺乏对业务价值和架构设计的深度思考，直接跳进代码实现。
2.  **方案单一**: 往往只给出一个"能跑"的方案，缺乏多方案对比和权衡。
3.  **缺乏全局视角**: 容易陷入局部细节，忽视了系统整体的复杂性和边界情况。
4.  **V2.3 现状**: 虽然有方案生成环节，但缺乏系统化的**思维引导流程**和**多角色协作**。

### 目标

将 AI 从"执行者"升级为**"专家顾问团"**，通过结构化的思维引导，确保在编码前想清楚**为什么做**、**怎么做最好**以及**潜在风险**。

---

## 💡 解决方案

### 1. 专家团队模式 (Expert Team Model)

引入多角色协作机制，模拟真实研发团队的讨论流程。为了符合框架架构，我们将角色分为 **Runtime (运行时)** 和 **Development (开发时)** 两类：

| 角色                       | 对应 Agent                    | 类型            | 职责                                                                               |
| :------------------------- | :---------------------------- | :-------------- | :--------------------------------------------------------------------------------- |
| **引导者 (Facilitator)**   | `design_facilitator` (新增)   | **Runtime**     | **流程编排与洞察整合**。负责拆解任务、委派专家、总结观点，并进行最终的"反思整合"。 |
| **产品经理 (PM)**          | `product_manager` (新增)      | **Development** | **价值与验收**。负责 5 Why 分析，明确业务价值，定义成功标准 (验收条件)。           |
| **系统架构师 (Architect)** | `architecture_analyst` (复用) | **Development** | **方案与风险**。负责技术方案设计、多方案对比、边界定义和技术风险评估。             |
| **质量工程师 (QA)**        | `test_engineer` (复用)        | **Runtime**     | **测试与保障**。负责制定测试策略，确保验收标准的可测性。                           |

### 2. 触发机制 (Hybrid Trigger)

采用 **"用户指令优先 + 自动复杂度评估"** 的混合机制，介入时机为 **方案生成 (Plan Generation) 阶段**：

#### A. 用户指令 (Think Levels)

用户可以通过指令显式控制思考深度：

- `@think` / `@think:standard`: **标准引导** (默认)。执行完整的 5 步引导流程。
- `@think:deep`: **深度辩论**。专家团队进行多轮辩论，适合复杂架构设计。
- `@think:quick`: **快速对齐**。仅确认目标、方案简述和验收标准。
- `@think:skip`: **跳过引导**。直接进入编码 (仅限简单任务)。

#### B. 自动触发 (Auto-Trigger)

当用户未明确指令时，基于 **013 的复杂度评估逻辑** (复用)：

- **复杂度 > 60 分** (涉及核心模块、架构变更) → **主动提议**:
  > "检测到此任务涉及核心模块 [Auth, Payment]，建议先进行设计思维引导以降低风险。是否启动？(Y/n)"
- **复杂度 < 60 分** → 默认跳过，直接生成方案。
- **Trivial 任务** (如 Fix typo) → **强制跳过**，防止过度设计。

#### C. 配置集成 (Configuration)

用户可在 `config/user_config.md` 中自定义行为：

```yaml
design_thinking:
  auto_trigger_threshold: 60 # 自动触发阈值 (0-100)
  default_mode: "standard" # standard/deep/quick
  expert_team: # 可自定义专家团队
    include_security_expert: false # 是否默认包含安全专家
```

### 3. 5 步引导流程 (The Process)

引导者 (Facilitator) 将按以下步骤指挥团队：

#### 🛑 前置检查 (Pre-check)

_Facilitator 快速判断任务性质。如果是简单任务，直接跳过。_

#### 1️⃣ 问题本质 (The "Why")

_执行者: ProductManager_

- **5 Why 分析**: 挖掘深层需求。
- **业务价值**: 明确"为什么要做"。
- **成功标准**: 初步定义验收条件。

#### 2️⃣ 方案探索 (The "How")

_执行者: ArchitectureAnalyst_

- **多方案生成**: 提出 2-3 种可行方案 (如：轻量级 vs 完整架构)。
- **对比分析**: 优缺点、成本、风险对比。
- **边界定义**: 明确"做什么"和"不做什么"。

#### 3️⃣ 风险与测试 (The "Risk")

_执行者: ArchitectureAnalyst & TestEngineer_

- **风险评估**: 识别技术难点和副作用。
- **测试策略**: 定义如何验证方案。

#### 🔄 4️⃣ 反思与整合 (Synthesis & Reflection) ⭐

_执行者: Facilitator_

- **全局反思**: 整合 PM、Architect、QA 的观点。
- **冲突解决**: 若专家意见不一致 (如 Architect 认为可行但 QA 认为不可测)，Facilitator 需指出冲突并要求用户裁决。
- **迭代判断**: 如果存在知识空白或高风险，**回溯**到 Step 2 进行深化。

#### 5️⃣ 最终决策 (Final Decision)

_执行者: Facilitator_

- **输出方案**: 生成结构化的最终方案。
- **无缝衔接**: 此输出将直接作为 **Plan Generator** 的输入，生成正式的 `implementation_plan.md`。

---

## 📝 输出格式

### 1. 推理记录 (Reasoning Transcript)

_(可选，折叠显示)_
记录专家团队的讨论过程，展示决策脉络。为了节省 Token，中间过程可使用摘要形式。

### 2. 最终方案 (Final Answer)

结构化的 Markdown 文档，包含：

- **背景与目标** (来自 PM)
- **推荐方案** (来自 Architect)
- **风险与应对** (来自 Architect)
- **验收标准** (来自 QA)
- **下一步行动** (Task List)

---

## 🛣️ 实施计划

### 阶段 1: 角色定义 (Role Definition)

- [ ] 创建 `agents/runtime/design_facilitator.md` (流程编排者)
- [ ] 创建 `agents/development/product_manager.md` (价值分析者)
- [ ] 确认 `agents/development/architecture_analyst.md` (复用)
- [ ] 确认 `agents/runtime/test_engineer.md` (复用)

### 阶段 2: 工作流实现 (Workflow Implementation)

- [ ] 实现 Facilitator 的编排 Prompt (参考 `other_project/深度思考设计.md`)。
- [ ] 实现 5 步引导的 Prompt 模板。
- [ ] 实现 "反思与整合" 及 "冲突解决" 的逻辑。

### 阶段 3: 框架集成 (Framework Integration) ⭐

- [ ] **更新 `AI_ENTRY_POINT.md`**:
  - 在 "方案生成" 节点前增加 "设计思维引导" 检查点。
  - 集成 `@think` 指令的解析逻辑。
  - 集成自动触发逻辑 (调用 013 的复杂度评估)。
- [ ] **更新 `AI_Coding_Context.md`**:
  - 在 "核心概念" 中增加 "设计思维引导" 章节。
  - 在 "核心工作流" 图表中补充引导环节。
- [ ] **更新 `AI_RULES.md`**:
  - 增加规则: "遇到复杂任务必须优先进行设计思维引导"。
  - 增加规则: "禁止在未明确价值和风险的情况下直接生成代码"。

### 阶段 4: 示例建设 (Example)

- [ ] 创建 `agents/examples/design_thinking/user_login_flow.md`。
- [ ] 展示一个完整的"用户登录功能"设计过程，包含 PM 追问、架构师对比方案、QA 补充测试用例的完整对话。

---

## 📊 价值评估

- **设计质量**: 通过多视角对抗和反思，设计缺陷率降低 **40%**。
- **返工减少**: "想清楚再动手"，返工率降低 **50%**。
- **知识沉淀**: 讨论过程本身就是高质量的架构决策记录 (ADR)。

## ⚠️ 风险与应对

1.  **过度设计**: 对简单任务强行引导。
    - _应对_: 严格的"前置检查"和"自动触发阈值"。
2.  **Token 消耗**: 多角色对话消耗较大。
    - _应对_: 使用 `Reasoning Transcript` 折叠中间过程，仅保留高价值结论；支持 `@think:quick` 模式。
3.  **专家冲突**: 专家意见不一致导致死循环。
    - _应对_: Facilitator 拥有最终裁决权，或在 2 轮争论后强制抛出给用户决策。
