---
title: AICC 框架问题根因分析与优化方案
summary: 从 AI-Coding-Context 框架自身出发，分析首版 dev_docs 生成中出现质量问题的系统性原因，并提出可执行的框架级改进方案。
keywords: aicc | framework | root-cause | quality-gate | templates | workflow
scope: AI-Coding-Context 框架的规范、模板、工作流与校验机制
related_files: AI_ENTRY_POINT.md | core/framework_spec.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | workflows/document_health_check.md | workflows/shared/ai_checklist.md | templates/AI_Coding_Context_TEMPLATE.md | templates/GENERATION_PLAN_TEMPLATE.md | tools/py/doc_health_checker.py
dependencies: 无
verified_at: 2026-05-12
---

# AICC 框架问题根因分析与优化方案

## 目标

这份文档不讨论 `ai_processing` 项目本身该怎么修，而是回答两个框架问题：

1. 为什么 AICC 在一次“看似成功的首版生成”中，仍然会产出不够可靠的 `dev_docs/`
2. 应该如何改 AICC 框架，降低后续项目再出现类似问题的概率

结论先说：这不是单点失误，而是 **AICC 当前存在“规范、模板、工作流、校验器”四层脱节**。  
只要这四层没有形成闭环，后续无论换哪个项目，都仍然可能生成“结构像样，但内容不够可信”的开发文档体系。

## 非目标

这份文档当前**不**覆盖以下内容：

- 不直接修改某个用户项目的 `dev_docs/`
- 不讨论单次生成时具体 AI 模型能力差异
- 不把“用户未继续维护首版文档”视为框架生成阶段的问题
- 不设计完整的实现代码，只给出框架级改造方向与任务化建议

这样做是为了把问题范围锁定在 **AICC 首版生成机制本身**，避免把项目侧执行习惯或后续维护纪律混进框架根因里。

## 一、问题不是偶发，而是框架机制导致的

基于这次对 `ai_processing` 生成结果的复查，以及对 `ai processing框架利用AICC的审查报告.md` 的再分析，可以把问题归成五类：

- **结构类问题**：主文档最终产物没有稳定满足 `framework_spec` 的章节要求
- **内容类问题**：代码示例没有被真实代码证据约束，最终可能写出误导性示例
- **验证类问题**：工作流里写了“要检查”，但没有强制生成“检查已通过”的证据产物
- **运行记录问题**：`_analysis/` 产物存在，但不足以完整复盘一次标准首版生成过程
- **复查能力问题**：自动检查能覆盖格式层，但高价值语义问题仍主要依赖人工深审

这些问题都不是“某个 AI 不够认真”那么简单，而是框架没有把质量要求固化成强约束。

## 二、深入原因分析

## 原因 1：SSOT 规范与模板没有真正绑定，导致“规范正确，但模板无法稳定产出符合规范的主文档”

### 现象

`framework_spec` 已明确规定主文档必须包含 10 个必需章节，其中包括：

- `🏢 业务模块映射`
- `🔧 常见任务速查`

证据：

- [core/framework_spec.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/core/framework_spec.md:85): 必需章节清单

但当前主文档模板 `templates/AI_Coding_Context_TEMPLATE.md` 并没有把这两个章节作为“强约束且高质量的主干结构”来保证。模板前半段强调了：

- `项目概览`
- `关键目录速查`
- `场景快速导航`
- `文档索引`
- `开发流程规范`

而 `业务模块映射` 与 `常见任务速查` 虽然在模板后半段出现了，但它们：

- 没有在模板前部作为必达主干结构被强调
- 与“设计思维引导”“AI 角色库”等框架性说明混杂在一起
- 没有被任何工具校验为主文档交付前的必需章节

证据：

- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:58)
- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:182)
- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:328)
- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:364)

而且模板本身还有明显坏味道，例如场景导航表格中混入了未清理的说明性句子，说明模板自身缺少结构校验：

- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:77)

### 根因

`framework_spec` 虽然被定义为 SSOT，但它只是“文字上的 SSOT”，还不是“可执行的 SSOT”。

当前链路是：

`framework_spec` 定义标准  
→ 模板作者手工同步  
→ 工作流作者再手工记住  
→ AI 按模板生成

这条链路里任何一环漂移，最终产物就会偏离规范。

也就是说，AICC 现在的 SSOT 是“人肉同步型 SSOT”，不是“编译期/校验期绑定型 SSOT”。

## 原因 2：框架要求“代码示例必须真实”，但最终生成路径没有强制证据化

### 现象

`GENERATION_PLAN_TEMPLATE.md` 对代码示例的要求其实非常明确：

- 代码示例必须来自真实项目代码
- 每个示例都要注明文件路径和行号
- 不允许编造代码示例

证据：

- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:117)
- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:123)
- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:133)

共享自检清单也强调：

- 所有代码示例都有文件路径和行号
- 所有数据来自方案中标注的实际代码

证据：

- [workflows/shared/ai_checklist.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/shared/ai_checklist.md:23)
- [workflows/shared/ai_checklist.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/shared/ai_checklist.md:66)

但问题在于，**主文档模板本身并没有为“证据化示例”提供结构位**。  
例如模板里写的是抽象的：

- “使用示例”
- “代码示例”

却没有强制要求示例下方必须有“来源文件”“来源行号”“是否为原样摘录/经裁剪整理”等字段。

证据：

- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:124)

### 根因

框架当前把“示例必须真实”放在了**方案约束层**，但没有放进**最终产物结构层**。

这会导致一种典型断裂：

1. 方案阶段说“示例必须来自真实代码”
2. 生成阶段模板只要求“给个示例”
3. AI 在写最终文档时，为了可读性或压缩信息，容易把示例“重新表述成一个看起来合理的综合示例”

于是最终产物就从“基于真实代码”滑向了“基于真实代码理解后重新编写的伪示例”。

这不是 AI 个体问题，而是框架没有把“证据绑定”设计成最终渲染时的硬约束。

## 原因 3：工作流把验证写成了 checklist，但没有把验证变成 release gate

### 现象

首次生成流程 Step 8 强调：

- 必须创建进度记录
- 必须更新生成进度

证据：

- [workflows/path_a_first_generation.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/path_a_first_generation.md:628)

详细生成流程也规定了验证优化阶段，要求检查：

- 所有必需章节都包含
- 代码示例基于实际代码
- 子文档链接有效

证据：

- [workflows/generation_workflow.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/generation_workflow.md:797)
- [workflows/generation_workflow.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/generation_workflow.md:805)
- [workflows/generation_workflow.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/generation_workflow.md:815)
- [workflows/path_b_health_check.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/path_b_health_check.md:569)

但这些要求目前仍然是“文字 checklist”，不是“产物闸门”。

例如：

- 虽然健康检查流程已经把 `dev_docs/_analysis/health_check_report.md` 作为标准分析报告产物示例，但首版生成流程没有要求在交付前必须产出它
- 没有要求 `doc_health_checker` 结果必须为通过，才能把 `generation_progress.md` 标记为完成
- 没有要求缺失必需章节时必须阻断交付

### 根因

当前 AICC 的验证逻辑更像“人工建议式 QA”，不是“流水线式 gate”。

也就是说：

- 框架知道应该检查什么
- 但框架没有规定“检查不通过时不能交付”

这会直接导致：

- 进度文件可以写“已完成”
- 但质量并未经过结构化验收

本质上，AICC 目前有流程说明，但缺少 **Definition of Done**。

## 原因 4：现有健康检查器覆盖面不够，查得到格式问题，查不到最关键的语义问题

### 现象

`tools/py/doc_health_checker.py` 当前主要检查：

- 文件路径准确性
- 代码块最小语法有效性
- 依赖版本对照
- frontmatter 合规

证据：

- [tools/py/doc_health_checker.py](/Users/zibuyu/code/zibuyu/AI-Coding-Context/tools/py/doc_health_checker.py:9)
- [tools/py/doc_health_checker.py](/Users/zibuyu/code/zibuyu/AI-Coding-Context/tools/py/doc_health_checker.py:217)

但它没有检查下面这些对本次问题更关键的内容：

- 主文档是否覆盖 `framework_spec` 的 10 个必需章节
- 示例是否带有来源文件和行号
- 示例是否可能是“综合编造示例”
- 模板里是否还残留占位符、坏表格、说明性垃圾文本
- 工作流、模板、规范之间是否出现互相矛盾

### 根因

`doc_health_checker` 目前更偏“文档静态健康检查器”，不是“框架契约校验器”。

它能发现：

- 路径错了
- frontmatter 错了
- Python 代码块语法错了

但它发现不了：

- 这份文档虽然格式没错，但章节缺了
- 这份文档虽然代码块能编译，但不是来自真实代码
- 这份模板虽然是合法 Markdown，但已经偏离框架规范

也就是说，当前 checker 解决的是“文档能不能读”，而不是“文档能不能信”。

## 原因 5：框架自身缺少 dogfooding 级别的一致性回归

### 现象

框架内部已经能看到多处漂移信号：

1. `framework_spec` 的标准产物路径没有 `review/` 目录，但 `generation_workflow.md` 的完整性检查仍要求生成 `review/`

证据：

- [core/framework_spec.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/core/framework_spec.md:61)
- [workflows/generation_workflow.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/generation_workflow.md:818)

2. 主文档模板虽然覆盖了部分必需章节，但整体仍带有明显未整理内容，且没有强结构约束

证据：

- [templates/AI_Coding_Context_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/AI_Coding_Context_TEMPLATE.md:85)

### 根因

这说明 AICC 自己还没有建立起一套“框架文档自审流水线”。

换句话说，AICC 当前能检查“用户项目生成出来的文档”，但还不够能检查“自己这套模板、工作流、规范是不是彼此一致”。

这会产生一个典型后果：

- 框架越迭代，内部漂移越大
- 漂移不是立刻炸掉，而是以“生成质量越来越不稳定”的方式表现出来

## 原因 6：AICC 对“运行留痕”有模板要求，但没有把运行记录完整性做成强约束

### 现象

在 `ai_processing` 这次首版生成里，`_analysis/` 下已经存在：

- `generation_plan.md`
- `project_analysis_report.md`
- `generation_progress.md`

这说明 AICC 至少留下了**基础运行痕迹**。但这些记录不足以完整复盘一次标准首版生成过程。

具体表现：

1. `generation_progress.md` 只记录了“首版已生成”和少量已完成事项，没有记录模板要求的：
   - 开始时间
   - 最后更新时间
   - 总体步骤进度
   - 分阶段文档完成状态
   - 总任务数/完成数

证据：

- [templates/PROGRESS_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/PROGRESS_TEMPLATE.md:11)
- [workflows/path_a_first_generation.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/path_a_first_generation.md:632)

2. `generation_plan.md` 没有完整承载模板中的复杂度评估、阶段工作量、交互确认点、风险点、业务模块识别、验证方式明细等过程信息。

证据：

- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:20)
- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:74)
- [templates/GENERATION_PLAN_TEMPLATE.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/templates/GENERATION_PLAN_TEMPLATE.md:164)

3. 首次生成流程 Step 7.5 明确要求方案生成后暂停等待人工审核，但当前运行记录没有把“审核等待”和“审核通过后进入生成”本身留痕下来。

证据：

- [workflows/path_a_first_generation.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/workflows/path_a_first_generation.md:600)

4. 验证状态只写了“链接自检：生成完成后执行”，没有留下执行命令、执行结果、发现问题或通过证据。

### 根因

AICC 现在对运行记录的要求仍然停留在：

- “应该创建哪些文件”
- “这些文件建议写什么”

但没有进一步要求：

- 这些文件必须达到什么粒度
- 哪些字段缺失会导致流程不算完成
- 运行记录与真实执行步骤如何一一对应

结果就是：

- 运行记录“存在”
- 但记录质量不稳定
- 后续只能知道“做过”，却很难知道“怎么做的、做到哪一步、哪些检查真的执行过”

这会削弱两个关键价值：

1. **可复盘性**：无法完整回放一次首版生成的执行路径
2. **可恢复性**：会话中断后，后续 AI 很难基于记录精确续跑

## 原因 7：AICC 的复查能力分层断裂，自动化只覆盖格式层，高价值问题仍依赖人工深审

### 现象

从这次 `ai processing框架利用AICC的审查报告.md` 可以看到，审查者发现了 3 个真正重要的问题：

1. `dev_docs` 与源码/README/用户文档之间的推荐实践分叉
2. 入口文档中的量化规模数据失真
3. `testing_guide` 对示例侧真实测试资产覆盖不足

但同一次审查里，`doc_health_checker` 返回的是 0 issue。

这说明：

- AICC 的**人工语义复查能力是存在的**
- 但 AICC 的**自动化复查能力主要停留在格式、路径、frontmatter 这一层**

换句话说，AICC 当前不是“完全不会复查”，而是“**能被人工复查出问题，但框架自己还不能稳定复查出这些问题**”。

### 证据

- 运行记录中明确提到：
  - 结构、frontmatter、路径链接层面基本健康
  - `doc_health_checker.py --full-check` 返回 0 issue
  - 真正的问题主要是“语义一致性”和“覆盖面”

这类现象直接说明，当前 checker 的能力边界与高价值审查需求之间存在断层。

### 根因

AICC 目前的复查能力大致分成两层：

1. **基础静态复查**
   - frontmatter
   - 路径
   - 代码块最小语法
   - 依赖版本漂移

2. **人工深度复查**
   - 事实源冲突识别
   - 量化数据复核
   - 测试覆盖面/测试资产分布审计

但两层之间缺少第三层：

3. **半自动语义复查层**
   - 自动发现“推荐实践冲突”
   - 自动复算“量化声明”
   - 自动枚举“测试资产拓扑”

没有这第三层，AICC 就会长期处于一种状态：

- 机器检查都过了
- 但真正重要的问题只有人工二审才能发现

这意味着框架的复查能力还没有产品化，只是“被经验丰富的审查者补齐了”。

## 三、根因总结

从框架工程角度看，本次问题的核心不是“生成器不聪明”，而是 AICC 缺少下面六个关键机制：

1. **规范到模板的强绑定机制**
2. **示例与数据的证据绑定机制**
3. **生成完成前的硬性验收闸门**
4. **框架自身的一致性回归机制**
5. **运行记录完整性约束机制**
6. **半自动语义复查机制**

只要这些机制不补上，类似问题会继续以不同形式重复出现。

## 四、问题到机制的映射

为了避免方案停留在抽象层，下面把这次暴露出来的实际问题直接映射到框架缺失机制：

| 暴露的问题 | 表层表现 | 框架缺失机制 | 最直接的改造点 |
| --- | --- | --- | --- |
| 主文档最终产物未稳定满足必需章节要求 | 生成结果与 `framework_spec` 不一致 | 规范到模板的强绑定 | `framework_spec` 契约化 + 模板契约检查 |
| 代码示例可能失真或被“总结性重写” | 文档看起来合理，但不一定可追溯 | 示例证据绑定 | 证据提取层 + 示例 provenance 结构 |
| 进度文件可写“完成”，但缺少验收证据 | 生成完成不等于质量通过 | 交付闸门 | 首版 health check 报告 + completion gate |
| 框架内部对 `review/` 等产物要求不一致 | `framework_spec`、workflow、template 漂移 | 框架 dogfood 回归 | framework contract checker |
| 模板里残留异常表格、占位符、框架自说自话段落 | 模板本身就可能把噪音带进用户项目 | 模板质量基线 | 模板 lint + 必需章节优先级重排 |
| `_analysis/` 文件存在，但不足以复盘整个首版生成过程 | 只能知道“做过”，很难知道“怎么做的” | 运行记录完整性约束 | progress/plan 模板强制字段 + 运行记录 gate |
| checker 返回 0 issue，但人工仍能发现高价值问题 | 自动检查与人工深审脱节 | 半自动语义复查 | 冲突检查器 + 量化校验器 + 测试资产拓扑检查 |

这个映射的意义是：后续实施时不需要再从“原则”反推“任务”，可以直接从“问题 -> 机制 -> 文件改造点”落地。

## 五、改进思路对比

这里有三种改造方向。

### 方案 A：只补模板

做法：

- 修模板，补缺失章节
- 清理模板中的坏占位符

优点：

- 成本低
- 见效快

缺点：

- 只能解决“漏项”和“坏模板”
- 解决不了“示例不真实”和“验证无证据”问题

结论：

- 适合作为 P0 热修
- 不能作为长期方案

### 方案 B：只补 checker

做法：

- 强化 `doc_health_checker`
- 增加章节覆盖、示例来源、占位符残留等检查

优点：

- 能把很多问题自动发现出来

缺点：

- 发现问题不等于避免问题
- 如果工作流不强制执行 checker，问题还是会流出

结论：

- 必须做
- 但单独做不够

### 方案 C：重构为“规范驱动 + 证据驱动 + gate 驱动”的闭环

做法：

1. 让 `framework_spec` 成为可执行契约
2. 让模板从契约派生或至少受契约校验
3. 生成过程拆成“证据提取”和“文档渲染”两阶段
4. 用健康检查报告作为交付前硬闸门
5. 对框架自身跑 dogfood 回归
6. 把运行记录从“可选细节”升级为“流程完成条件的一部分”
7. 在格式检查与人工深审之间补一层“半自动语义复查”

优点：

- 能同时解决结构、内容、验证、运行记录和复查能力这几类问题
- 能随框架演进持续稳定

缺点：

- 需要改动 workflow、template、tool 三层

结论：

- 这是推荐方案

## 六、推荐优化方案

推荐采用：**方案 C，为主；方案 A 和 B 作为其首批落地点。**

## 6.1 建立“可执行 SSOT”，消除 spec/template/workflow 漂移

### 目标

把 `framework_spec` 从“说明文档”升级为“契约源”。

### 具体改法

1. 新增一个结构化契约文件，例如：
   - `core/contracts/main_doc_contract.yaml`
   - 内容包括：
     - 必需章节列表
     - 每章最小要求
     - 某些章节对不同项目类型是否可选

2. 让 `templates/AI_Coding_Context_TEMPLATE.md` 受这个契约校验，而不是手工维护

3. 增加一个校验脚本，例如：
   - `tools/py/framework_contract_checker.py`
   - 用来检查：
     - 模板是否覆盖所有必需章节
     - workflow 中引用的标准目录是否仍与 `framework_spec` 一致
     - 是否出现过时目录要求，如 `review/`

### 预期收益

- 一旦 `framework_spec` 更新，模板和工作流的漂移会被自动暴露
- “规范正确但模板结构漂移或弱约束”会变成可检测问题，而不是事后审查问题

## 6.2 把“真实代码证据”从软要求变成渲染约束

### 目标

避免 AI 在最终文档里把真实代码“理解后重写成综合示例”。

### 具体改法

1. 调整文档生成流程为两阶段：

**阶段 A：证据提取**

- 提取结构化证据项：
  - `type`: example / metric / architecture_claim
  - `source_file`
  - `source_lines`
  - `snippet`
  - `normalized_explanation`

**阶段 B：文档渲染**

- 文档只能消费证据项，不允许自由编造示例

2. 修改模板，为代码示例增加固定结构：

```markdown
### 示例标题

**来源**: `path/to/file.py:10-26`
**说明**: 为什么这个示例代表该模式

```python
[摘录或裁剪后的真实代码]
```
```

3. 给主文档和关键子文档增加规则：

- 若出现代码块但没有来源字段，则检查失败
- 若来源路径不存在，则检查失败
- 若来源行号不存在或为空，则检查失败

4. 对“总结性伪示例”单独定义语义：

- 若确实需要综合示例，必须标记为：
  - `示意示例（非源码摘录）`
- 且不能用于“核心代码模式”这种高信任区域

### 预期收益

- 示例真实性可追溯
- AI 更难在高风险段落里悄悄“写一个看起来合理的例子”

## 6.3 引入首版生成的交付闸门

### 目标

让“已完成”必须意味着“通过最低质量验收”。

### 具体改法

1. 首版生成结束后强制执行：

```bash
python tools/py/doc_health_checker.py --full-check --doc-dir <project>/dev_docs
```

2. 新增首版专用报告产物：

- `dev_docs/_analysis/health_check_report.md`
- 使用现有 `templates/HEALTH_CHECK_REPORT_TEMPLATE.md` 或扩展为“首版交付报告”模板

3. 调整 `generation_progress.md` 完成定义：

- 只有当：
  - 所有文档生成完成
  - 健康检查通过
  - 报告落盘
  才能标记“状态：已完成”

4. 在 `path_a_first_generation.md` 中新增一个明确步骤：

- Step 8.5: 首版质量验收

### 预期收益

- 进度文件不再只是“文件都写完了”
- 而是“最低质量门槛已过”

## 6.4 升级 doc_health_checker：从静态健康检查器变成契约检查器

### 目标

让 checker 能发现本次真实暴露出来的问题。

### 应新增的检查项

1. **主文档必需章节检查**
   - 对照 `framework_spec` 或契约文件
   - 缺章节直接报错

2. **模板残留物检查**
   - 检测 `[填写]`、`[PROJECT_NAME]`、`...`
   - 检测异常 Markdown 表格行

3. **代码示例来源检查**
   - 代码块前是否有来源字段
   - 来源文件是否存在
   - 行号范围是否合法

4. **高风险语义检查**
   - 检测“推荐”“必须”“最佳实践”等高强度表述
   - 若对应段落没有来源支撑，则降为 warning 或 error

5. **框架内部一致性检查**
   - `framework_spec`、template、workflow 之间的目录引用是否一致
   - 是否引用了标准中不存在的产物目录

### 文件建议

- 扩展：`tools/py/doc_health_checker.py`
- 新增：`tools/py/framework_contract_checker.py`
- 可选新增：`tools/py/example_provenance_checker.py`

## 6.5 增加框架自身 dogfood 回归

### 目标

在发布框架前，先检查框架自己有没有内生漂移。

### 具体改法

1. 对以下内容建立固定回归检查：

- `core/framework_spec.md`
- `templates/*.md`
- `workflows/*.md`

2. 检查内容：

- 标准产物路径是否一致
- 主文档模板是否覆盖全部必需章节
- workflow 是否引用已废弃目录
- 模板是否含未清理占位符

3. 增加一个 dogfood 命令，例如：

```bash
python tools/py/framework_contract_checker.py --self-check
```

### 预期收益

- AICC 在影响用户项目之前，先暴露自己的漂移问题

## 6.6 把运行记录完整性纳入首版生成契约

### 目标

让 `_analysis/` 不只是“有几个文件”，而是真正能复盘和续跑的运行日志。

### 具体改法

1. 为 `generation_progress.md` 定义最低必填字段：
   - `开始时间`
   - `最后更新`
   - `当前状态`
   - `总体步骤进度`
   - `逐文档完成状态`
   - `总任务数/已完成数`

2. 为 `generation_plan.md` 定义最低必填字段：
   - 复杂度评估
   - 风险点
   - 交互确认点
   - 子文档清单
   - 验证方式

3. 在 Step 7.5 和 Step 8 之间增加运行留痕要求：
   - 记录“等待人工审核”
   - 记录“用户确认后开始正式生成”

4. 将“验证状态”从摘要描述升级为可追溯条目：
   - 检查项
   - 执行命令或检查方式
   - 结果
   - 是否通过

5. 在 checker 中新增运行记录完整性检查：
   - `generation_progress.md` 字段是否齐全
   - 是否存在空泛状态如“已执行/已完成”但没有对应细节
   - 是否缺少关键步骤留痕

### 预期收益

- 首版生成完成后，可以真正复盘执行路径
- 会话中断时，后续 AI 能更准确续跑
- 框架运行记录从“辅助说明”升级为“过程资产”

## 6.7 建立半自动语义复查层

### 目标

让 AICC 不再只会检查“文档能不能读”，而开始检查“文档是不是可信”。

### 具体改法

1. 新增“事实源冲突检查”
   - 检查 `dev_docs` 与 `README.md`、`docs/`、关键源码注释之间，是否存在互斥推荐实践
   - 重点扫描：
     - `推荐/应当/必须/优先使用`
     - `deprecated/弃用/不建议`

2. 新增“量化声明校验”
   - 自动识别文档中的：
     - 文件数
     - 测试数
     - 代码量
     - 模块数
   - 用扫描命令复算，并比对差异

3. 新增“测试资产拓扑检查”
   - 自动枚举：
     - `tests/`
     - `examples/**/tests/`
     - 其他常见测试目录
   - 生成测试分布摘要，供 `testing_guide` 和审查器使用

4. 将这三项结果汇总为“语义复查报告”
   - 可作为：
     - `dev_docs/_analysis/semantic_review_report.md`
   - 或并入 `health_check_report.md`

### 预期收益

- 自动检查能覆盖更高价值的问题类型
- 人工复查从“发现问题”转向“确认复杂问题”
- AICC 的复查能力开始从经验依赖转向机制依赖

## 七、实施优先级

## P0：一周内完成的最小闭环

1. 修复 `AI_Coding_Context_TEMPLATE.md`
   - 清理异常表格和残留模板文本
   - 将 `业务模块映射`、`常见任务速查` 前移或提升为明确主干结构
   - 收敛与项目无关的框架宣传性段落，避免淹没主文档必需内容

2. 扩展 `doc_health_checker`
   - 增加必需章节检查
   - 增加占位符残留检查

3. 在 `path_a_first_generation.md` 增加“首版质量验收”步骤
4. 为 `generation_progress.md` 和 `generation_plan.md` 增加最小必填字段校验
5. 新增量化声明校验与测试资产拓扑检查的最小实现

这一步的目标不是完美，而是先把这次暴露出来的三个问题堵住。

## P1：一到两周内完成的质量硬化

1. 新增 `framework_contract_checker.py`
2. 让 workflow/template 跑框架内部一致性检查
3. 把 `health_check_report.md` 纳入首版交付产物
4. 把 `generation_progress.md` 的“完成”语义改成“生成完成 + 验收通过”
5. 把运行记录完整性纳入交付 gate
6. 引入事实源冲突检查，并把结果接入复查报告

## P2：中期演进

1. 重构为“证据提取 → 文档渲染”两阶段
2. 为示例建立统一 provenance 结构
3. 对高风险断言增加证据检查

## 八、建议的文件级改造范围

为了让后续实施更直接，下面列出每项改造最可能触达的框架文件。

### P0 预计涉及

- `templates/AI_Coding_Context_TEMPLATE.md`
- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/project_scanner.py` 或配套扫描逻辑

### P1 预计涉及

- `core/framework_spec.md`
- `workflows/generation_workflow.md`
- `workflows/path_b_health_check.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- `tools/py/framework_contract_checker.py`（新增）
- `tools/js/framework_contract_checker.js`（若继续保持双脚本对称，则同步新增）
- `tools/py/semantic_review_checker.py`（新增）
- `tools/js/semantic_review_checker.js`（若保持对称，则同步新增）

### P2 预计涉及

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/shared/ai_checklist.md`
- `tools/py/example_provenance_checker.py`（新增，可选）
- 后续若做结构化证据中间产物，还需要新增对应模板或 schema 文件

## 九、实施时的设计约束

改造 AICC 时应坚持以下约束，否则容易把问题从“质量不稳定”变成“框架过重”：

1. **优先增量改造，不推翻现有工作流**
   - 先补 gate 和 checker，再考虑重构生成架构

2. **保持双脚本对称原则**
   - Python / JS 工具若当前体系要求对称，就不要只在一边增强

3. **把契约检查与文档生成解耦**
   - checker 应独立可运行，不能只能在某个大工作流里间接生效

4. **高风险断言优先于低风险格式**
   - “示例是否真实”优先级高于“表格是否漂亮”

5. **不要把框架宣传内容继续塞进用户主文档模板**
   - 主文档应优先服务用户项目理解，而不是解释 AICC 自己有多完整

6. **优先把“人工已稳定发现的问题类型”产品化**
   - 如果一种问题在人工复查中已反复出现，就应尽快进入半自动审查层

## 十、建议的验收标准

如果后续要判断这轮框架改造是否成功，建议使用下面这组标准：

### P0 验收

- `AI_Coding_Context_TEMPLATE.md` 不再含明显异常表格或残留模板垃圾文本
- `doc_health_checker` 能自动报出主文档必需章节缺失
- 首版生成流程文字上出现明确的“质量验收”步骤
- 能自动报出明显失真的量化声明或遗漏的大块测试目录

### P1 验收

- 存在可运行的 `framework_contract_checker`
- 能检测 `framework_spec` / template / workflow 的目录漂移
- 首版生成完成前，必须落地产出 `health_check_report.md`
- 存在可运行的 `semantic_review_checker`
- 能发现至少一类事实源冲突和一类测试资产覆盖遗漏

### P2 验收

- 高信任代码示例都能追溯到 `source_file + source_lines`
- checker 能区分“源码摘录示例”和“示意示例”
- 生成系统从“文本约束”升级为“证据约束”
- 自动化复查从“格式层”升级为“格式层 + 半自动语义层”

## 十一、建议的框架改造顺序

推荐按下面顺序推进：

1. **先修模板**
   - 因为这是最低成本、最高显性收益

2. **再补 checker**
   - 把当前已知问题变成自动可检

3. **再加 gate**
   - 让检查结果真正影响“是否完成”

4. **最后做 evidence-driven 生成重构**
   - 这是长期最稳的方案，但改动最大

## 十二、最终判断

从框架角度看，这次暴露的问题说明：

- AICC 的理念已经相当完整
- 但它目前更像“有经验的生成手册”
- 还不是“质量要求可执行、可回归、可阻断的生成系统”

后续优化的关键不是继续堆更多规则文本，而是把这些规则转化为：

- 契约
- 结构化证据
- 自动检查
- 交付闸门

只有这样，AICC 才能从“生成文档的指南”升级成“稳定产出可信 dev_docs 的框架”。
