# 004-ADR 系统实施方案与进度表

本文档旨在落实 V3.0 P1 阶段核心优化点“004-ADR 架构决策记录系统”。系统的核心目标是将 ADR 从静态复盘转化为 AI 与人类的架构约束宪法（Anchor of Consensus）。

## 执行优先级与灰度策略

遵循“先文档化与 MVP 规范，再实现代码级工具拦截”的路线，分阶段逐步落地。

---

## Proposed Changes

### Phase 1: 模板落地与结构验证

**目标**：搭建符合标准的 ADR 目录架构、核心模板，并在框架自身开发进程中创建首批 ADR 以“试毒”验证（即实现自举）。

#### [NEW] `dev_docs/architecture/adr-template.md`
创建包含标准结构（决策信息、背景、决策、替代方案、影响分析以及 L1 级轻量化架构断言 AaC YAML片段）的 ADR 规范模板。模板中还将包含前置冲突检查清单，以及层级（level/domain/year）等 Metadata 规范。

#### [NEW] `dev_docs/architecture/evolution.md`
创建架构演进综述文件，预留基于 Mermaid 的核心架构决策时序/依赖图谱节点。

#### 建立目录结构体系：
- 📂 `dev_docs/architecture/decisions/` —— 用于存放 Active 状态的决策。
- 📂 `dev_docs/architecture/decisions/archived/` —— 用于存放已废弃或被替代的决策，避免检索污染。

#### 起草测试/试毒 ADR 文件：
视当前框架内现有状况，起草前几项实际的框架本身的基础架构决策文档，放置于 `decisions` 目录下：
- [NEW] `dev_docs/architecture/decisions/001-markdown-as-first-class-doc.md` (示例：将所有文档定为 Markdown 的决策)
- [NEW] `dev_docs/architecture/decisions/002-layered-documentation.md` (示例：分层文档架构决策)

---

### Phase 2: 工作流挂载与工具开发

**目标**：打通 AI Context 闭环，将 ADR 起草机制与互审阻断机制无缝挂载至现有流中，降低隐性违规；同时开发配套支持工具。

#### [MODIFY] `workflows/generation_workflow.md` (或同级核心工作流文档)
**修改内容**：在方案生成（Plan First）环节植入“跨越架构阈值触发器”。
- 添加**阈值检查**：要求 AI 在提炼需求后必须回答“是否涉及跨过架构阈值的决策？(Yes/No)”  
- 强制**自动起草**：如有跨越，阻塞直接编码或常规计划生成，优先基于 `adr-template.md` 起草新 ADR。

#### [MODIFY] `quality/README.md` (或具体互审工作流/模板文件)
**修改内容**：在 AI 互审机制（ai_mutual_review）中，植入 ADR 判例依据。
- 添加审查准则：审查 AI 必须在执行逻辑检查前，检索 Active 的 ADR。
- 提出强制问题：“断言当前实现是否与 {当前ADR} 冲突？如有违规，直接驳回”。

#### [NEW] `tools/why_tool.py` (架构探针检索工具)
**工具拆解任务**：
1. **输入解析**：获取需要查询的疑惑代码行或关键字。
2. **L1 注解识别**：利用正则提取代码中预埋的 `@architecture ADR-XXX:` 或 `@reason` 注释。
3. **文本/目录匹配**：若无注解，根据文件所在层级（frontend/backend）或依赖关键词，全局检索 `dev_docs/architecture/decisions/` 找出关联度最高的 Active ADR 路径与摘要返回。
4. **输出拼装**：将历史上下文呈现给 AI。

---

### Phase 3: AaC 高级断言拦截探索（预研与试点阶段）
**目标**：探索代码级别强卡控（将二层半自动化断言真正变为护栏）。

#### [NEW] `tools/aac_validator.py` 及 `tools/js/aac_validator.js`
创建实验性架构静态检查脚本。
- **功能**：遍历 `dev_docs/architecture/decisions/*.md` 下 FrontMatter 或特定区块的 YAML `constraints` (如 `forbidden_patterns`).
- **校验**：读取项目的源文件或变更 diff，进行简单的正则或 AST 层拦截。
- **整合**：支持双语言实现 (Py/JS) 并在 `tools/README.md` 中注册。

---

## 验证计划
详见同目录下的 `walkthrough.md`。
