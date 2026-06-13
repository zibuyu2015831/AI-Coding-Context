---
title: AICC 框架改造实施计划
summary: 基于 framework_improvement_analysis.md 的结论，给出可直接执行的 AICC 框架级改造实施计划，覆盖模板、工作流、校验器、运行记录与半自动语义复查能力。
keywords: aicc | implementation-plan | quality-gate | checker | workflow | template
scope: AI-Coding-Context 框架自身改造，不涉及任何业务项目 dev_docs 的直接修复
related_files: framework_improvement_analysis.md | ai processing框架利用AICC的审查报告.md | core/framework_spec.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | workflows/path_b_health_check.md | templates/AI_Coding_Context_TEMPLATE.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | templates/HEALTH_CHECK_REPORT_TEMPLATE.md | tools/py/doc_health_checker.py | tools/js/doc_health_checker.js
dependencies: 无
verified_at: 2026-05-12
---

# AICC Framework Improvement Implementation Plan

> **状态：✅ 已执行（EXECUTED in V3.0）** — 本方案提出的契约层（core/contracts/）、双语言校验器（framework_contract_checker / semantic_review_checker）与提交门禁（pre_commit_gate.py）均已实现并合入 dev/master。保留作开发档案；下方 checkbox 为历史工作清单，非待办。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 执行本计划。所有任务使用 checkbox 语法跟踪，不要跳步，不要脱离本文档自行改 scope。

**Goal:** 把 AICC 从“规范存在但执行靠经验”的框架，升级成“契约可执行、质量可校验、交付有闸门、运行可复盘、复查可半自动化”的稳定生成系统。

**Architecture:** 这次改造不推翻现有框架，而是在现有 Public 层之上补三条主线：`契约层`、`交付 gate 层`、`半自动语义复查层`。实现策略是增量改造模板、工作流和双脚本 checker，并新增少量契约/测试数据文件，让首版生成流程具备可验证闭环。

**Tech Stack:** Markdown、YAML、Python 3 标准库、Node.js 标准库、现有 `tools/py/*` 与 `tools/js/*` 薄编排工具体系。

---

## 1. 文档用途与执行边界

这份文档是 **AICC 框架自身的实施计划**，不是分析报告，也不是某个业务项目的修复清单。

拿到这份文档的执行 AI，需要先理解以下边界：

- 本次改造对象是当前仓库 `AI-Coding-Context`
- 目标是避免后续任意项目在使用 AICC 生成 `dev_docs/` 时重复出现同类问题
- 不在本计划内直接修改 `ai_processing` 或其他业务仓库
- 允许新增 framework 内部契约文件、checker、测试数据和测试脚本
- 必须保持 Python / JS 双脚本能力对称，除非文档明确说明是“仅 Python 先行验证”的临时策略
- 必须保留 `doc_health_checker` 当前“thin orchestrator / delegate-first / zero-dependency”的设计原则，不能把它改成引入第三方库的大而全工具

## 2. 为什么要做这次改造

上游分析见：

- [framework_improvement_analysis.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/framework_improvement_analysis.md)
- [ai processing框架利用AICC的审查报告.md](/Users/zibuyu/code/zibuyu/AI-Coding-Context/ai%20processing框架利用AICC的审查报告.md)

已经确认的框架问题有五类：

1. 主文档结构不能稳定满足 `framework_spec` 必需章节
2. 真实代码示例要求没有被最终产物结构强约束
3. 验证是 checklist，不是交付 gate
4. `_analysis/` 运行记录存在，但不足以完整复盘
5. 自动化复查只覆盖格式层，高价值语义问题依赖人工深审

本计划就是把这五类问题拆成可执行任务，并给出每项任务对应的文件、命令、验收口径和依赖顺序。

## 3. 执行前必须知道的仓库事实

这些信息已经核实过，执行 AI 不要再做错误假设：

1. 当前 `doc_health_checker` 已存在，且是薄编排层，不是空壳。
   - `tools/py/doc_health_checker.py`：318 行
   - `tools/js/doc_health_checker.js`：327 行

2. 两个 checker 当前主要覆盖：
   - file paths
   - code sample 最小语法
   - dependency drift
   - frontmatter

3. 当前 Public 层关键文件体量较大，改动时必须控制节奏：
   - `workflows/path_a_first_generation.md`：930 行
   - `workflows/generation_workflow.md`：1606 行
   - `templates/GENERATION_PLAN_TEMPLATE.md`：868 行
   - `core/framework_spec.md`：547 行

4. 仓库没有统一顶层 `tests/` 目录。
   - Python 现有测试在 `tools/py/tests/`
   - JS 现有测试主要是 `tools/js/*.test.js` 这类独立脚本式测试

5. 当前 `package.json` 没有现成 `scripts.test` 编排，不要假设存在统一 `npm test` 入口。

6. 当前框架已经广泛引用 `doc_health_checker.py/.js`。
   - 新增能力时要优先保持 CLI 向后兼容
   - 不能破坏已有 `--file` / `--mode` / `--full-check` 等入口

## 4. 总体交付物

本轮改造完成后，仓库中应至少新增或稳定产出以下结果：

### 4.1 新增契约源

- `core/contracts/main_doc_contract.yaml`
- `core/contracts/run_record_contract.yaml`

### 4.2 新增 checker

- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`

### 4.3 增强现有 checker

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

### 4.4 新增测试数据与测试脚本

- `tools/testdata/framework_contracts/`
- `tools/testdata/semantic_review/`
- `tools/py/tests/test_doc_health_checker.py`
- `tools/py/tests/test_framework_contract_checker.py`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/doc_health_checker.test.js`
- `tools/js/framework_contract_checker.test.js`
- `tools/js/semantic_review_checker.test.js`

### 4.5 被改造的框架文档与模板

- `core/framework_spec.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `workflows/path_b_health_check.md`
- `templates/AI_Coding_Context_TEMPLATE.md`
- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/PROGRESS_TEMPLATE.md`
- `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- 如需要：`workflows/shared/ai_checklist.md`

## 5. 设计原则

执行时必须遵守以下设计原则，否则实现会偏离本计划：

1. **增量优先**
   - 先补契约和 gate，再考虑大规模重构

2. **双脚本对称**
   - Python 和 JS 都要可运行、可验收、可被 Public workflow 引用

3. **契约先行**
   - 新规则不要只写在自然语言 workflow 里，优先沉淀到 YAML 契约或机器可检的规则集

4. **编排优先于重写**
   - 能复用现有 `project_scanner.py/.js`、`doc_dependency_tracer.py/.js`、`summary_validator.py/.js` 的地方，不重复实现

5. **格式检查不是终点**
   - 新 checker 必须覆盖至少三类高价值问题：章节缺失、量化声明失真、测试资产覆盖遗漏

6. **计划/进度文件属于过程资产**
   - `_analysis/` 运行记录必须被当作交付物的一部分，而不是“可有可无的说明文字”

## 6. 实施分期

本计划按三个阶段推进，禁止直接跳到 P2。

### P0

目标：把这次已经暴露出来的问题类型先堵住，形成最小闭环。

### P1

目标：把“契约 + gate + 语义复查”从局部增强提升到框架级稳定能力。

### P2

目标：为后续“证据提取 → 文档渲染”两阶段重构建立基础，不要求本轮一次性完成。

## 7. 文件责任映射

| 文件 | 责任 |
| --- | --- |
| `framework_improvement_analysis.md` | 上游分析，作为本计划事实来源，不再继续扩展实现细节 |
| `core/framework_spec.md` | Public 规范说明文档，继续保留人类可读性，但与契约文件保持一致 |
| `core/contracts/main_doc_contract.yaml` | 主文档结构契约，作为 required sections 的机器真相源 |
| `core/contracts/run_record_contract.yaml` | 首版生成运行记录契约，约束 `generation_plan.md` / `generation_progress.md` 最低字段 |
| `templates/AI_Coding_Context_TEMPLATE.md` | 主入口文档模板，必须按主文档契约对齐 |
| `templates/GENERATION_PLAN_TEMPLATE.md` | 分析方案模板，必须补齐运行记录与证据字段要求 |
| `templates/PROGRESS_TEMPLATE.md` | 进度模板，必须支持可复盘状态机 |
| `templates/HEALTH_CHECK_REPORT_TEMPLATE.md` | 首版交付 gate 报告模板 |
| `workflows/path_a_first_generation.md` | 首版生成主流程，必须接入质量验收和运行留痕 gate |
| `workflows/generation_workflow.md` | 详细生成流程，必须对齐新契约、新 checker 和 DoD |
| `workflows/path_b_health_check.md` | 健康检查流程，需与首版交付报告复用产物格式 |
| `tools/py/doc_health_checker.py` | 文档健康检查编排层，扩展章节/占位符/运行记录检查 |
| `tools/js/doc_health_checker.js` | JS 对称实现 |
| `tools/py/framework_contract_checker.py` | 框架内部 contract 自检 |
| `tools/js/framework_contract_checker.js` | JS 对称实现 |
| `tools/py/semantic_review_checker.py` | 半自动语义复查编排层 |
| `tools/js/semantic_review_checker.js` | JS 对称实现 |

## 8. 实施任务

### Task 1: 建立契约源并冻结规则边界

**Files:**
- Create: `core/contracts/main_doc_contract.yaml`
- Create: `core/contracts/run_record_contract.yaml`
- Modify: `core/framework_spec.md`

- [ ] **Step 1: 梳理需要契约化的规则**

从 `core/framework_spec.md` 提取机器可检规则，只放入两类信息：

- 主文档必需章节
- 运行记录必需字段

不要把所有自然语言说明都搬进 YAML，避免契约膨胀。

- [ ] **Step 2: 写出 `main_doc_contract.yaml` 初版**

最低结构要求如下：

```yaml
contract_version: 1
document: AI_Coding_Context
required_sections:
  - id: project_overview
    title: "📌 项目概览"
  - id: key_directories
    title: "📁 关键目录速查"
  - id: scenario_navigation
    title: "🎯 场景快速导航"
  - id: document_index
    title: "🗂️ 文档索引"
  - id: core_patterns
    title: "💡 核心代码模式"
  - id: development_workflow
    title: "🔄 开发流程规范"
  - id: naming_rules
    title: "📝 命名与放置规范"
  - id: business_modules
    title: "🏢 业务模块映射"
  - id: ai_taboo
    title: "🚫 AI 编码禁忌"
  - id: common_tasks
    title: "🔧 常见任务速查"
```

- [ ] **Step 3: 写出 `run_record_contract.yaml` 初版**

最低结构要求如下：

```yaml
contract_version: 1
documents:
  generation_plan:
    required_headings:
      - "复杂度评估"
      - "风险点"
      - "交互确认点"
      - "子文档清单"
      - "验证方式"
  generation_progress:
    required_fields:
      - "开始时间"
      - "最后更新"
      - "当前状态"
      - "总体步骤进度"
      - "逐文档完成状态"
      - "总任务数"
      - "已完成数"
```

- [ ] **Step 4: 在 `framework_spec.md` 中补一小节说明“规范文档与契约文件”的关系**

要求：

- `framework_spec.md` 继续是 Public 人类可读 SSOT 说明
- 机器校验以 `core/contracts/*.yaml` 为执行契约
- 两者漂移时，以修正 Public 说明和契约一致性为准，不允许长期分叉

- [ ] **Step 5: 自检并记录 diff 范围**

Run:

```bash
git diff -- core/framework_spec.md core/contracts/main_doc_contract.yaml core/contracts/run_record_contract.yaml
```

Expected:

- 只包含契约文件新增和 `framework_spec.md` 的最小说明性改动

**Done when:**

- 契约文件可读、字段命名稳定、没有把自然语言大段复制进 YAML

### Task 2: 修主文档模板并让其结构对齐契约

**Files:**
- Modify: `templates/AI_Coding_Context_TEMPLATE.md`
- Modify: `templates/GENERATION_PLAN_TEMPLATE.md`
- Modify: `templates/PROGRESS_TEMPLATE.md`

- [ ] **Step 1: 清理 `AI_Coding_Context_TEMPLATE.md` 中明显异常内容**

至少修掉：

- 场景快速导航中的异常表格/说明性垃圾文本
- 与用户项目理解无关、会稀释主干结构的框架宣传性段落
- 易让 AI 误以为可以自由发挥的模糊占位块

- [ ] **Step 2: 提升两个关键章节为主干结构**

必须把下列章节提升到和前半部分同等显著层级：

- `🏢 业务模块映射`
- `🔧 常见任务速查`

不要再把它们埋在后半段框架说明之后。

- [ ] **Step 3: 为高信任代码示例增加 provenance 槽位**

在主模板和相关子模板中，对高信任示例统一增加以下结构：

```markdown
**来源**: `path/to/file.py:10-26`
**说明**: 该示例代表的模式
```

规则：

- `核心代码模式` 中的示例默认必须有来源
- 若是示意示例，必须明确标记“示意示例（非源码摘录）”

- [ ] **Step 4: 补强 `GENERATION_PLAN_TEMPLATE.md` 中的证据与验证字段**

至少新增或强化以下显式字段：

- 量化声明来源
- 测试资产扫描结果
- 推荐实践事实源
- 最终验证命令

- [ ] **Step 5: 补强 `PROGRESS_TEMPLATE.md` 中的状态字段**

要求模板能明确记录：

- 审核等待中
- 已获用户确认
- 生成中
- 首版验收中
- 已完成
- 已阻塞

- [ ] **Step 6: 目视复核模板是否仍然可供 AI 直接复制使用**

Run:

```bash
sed -n '1,240p' templates/AI_Coding_Context_TEMPLATE.md
sed -n '1,220p' templates/PROGRESS_TEMPLATE.md
```

Expected:

- 模板主干章节清晰
- 没有明显残留垃圾文本
- provenance 槽位容易被模型照抄

**Done when:**

- 模板层已经能显式承载“必需章节 + 示例来源 + 运行状态”

### Task 3: 实现 framework contract checker

**Files:**
- Create: `tools/py/framework_contract_checker.py`
- Create: `tools/js/framework_contract_checker.js`
- Create: `tools/testdata/framework_contracts/valid_template.md`
- Create: `tools/testdata/framework_contracts/missing_sections_template.md`
- Create: `tools/testdata/framework_contracts/spec_workflow_drift_case/`
- Create: `tools/py/tests/test_framework_contract_checker.py`
- Create: `tools/js/framework_contract_checker.test.js`

- [ ] **Step 1: 设计 CLI**

Python / JS CLI 都应支持：

```bash
--self-check
--check-template <file>
--check-workflow <file>
--contract <yaml>
--format json|text
```

- [ ] **Step 2: 实现主文档章节检查**

最小能力：

- 读取 `main_doc_contract.yaml`
- 扫描模板或目标文档中的二级标题
- 判断 required sections 是否缺失
- 输出 machine-readable JSON

- [ ] **Step 3: 实现 workflow 与 spec 的路径一致性检查**

最小能力：

- 扫描 `core/framework_spec.md`
- 扫描 `workflows/generation_workflow.md` 和 `workflows/path_a_first_generation.md`
- 检测是否仍出现与 SSOT 不一致的标准目录要求，例如 `review/`

- [ ] **Step 4: 加入框架自审模式**

`--self-check` 至少检查：

- `templates/AI_Coding_Context_TEMPLATE.md`
- `workflows/generation_workflow.md`
- `workflows/path_a_first_generation.md`
- `core/framework_spec.md`

- [ ] **Step 5: 为 checker 添加最小测试数据**

`tools/testdata/framework_contracts/` 至少包含：

- 完整通过样本
- 缺少 `业务模块映射` 样本
- 缺少 `常见任务速查` 样本
- workflow / spec 路径漂移样本

- [ ] **Step 6: 运行 Python 与 JS 测试**

Run:

```bash
python3 -m unittest tools/py/tests/test_framework_contract_checker.py
node tools/js/framework_contract_checker.test.js
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
```

Expected:

- 单测通过
- `--self-check` 至少能输出 PASS/FAIL 和具体问题列表

**Done when:**

- 框架内部漂移不再只能靠人工发现

### Task 4: 升级 doc_health_checker 为“契约 + 文档健康”复合检查器

**Files:**
- Modify: `tools/py/doc_health_checker.py`
- Modify: `tools/js/doc_health_checker.js`
- Create: `tools/py/tests/test_doc_health_checker.py`
- Create: `tools/js/doc_health_checker.test.js`
- Reuse: `core/contracts/main_doc_contract.yaml`
- Reuse: `core/contracts/run_record_contract.yaml`

- [ ] **Step 1: 保持现有 CLI 向后兼容**

已存在的入口必须继续可用：

- `--file`
- `--mode quick|standard|deep`
- `--check-file-paths`
- `--check-code-samples`
- `--check-dependencies`
- `--full-check`

- [ ] **Step 2: 增加主文档必需章节检查**

建议新增显式开关：

```bash
--check-required-sections
```

同时把它接入：

- `--mode deep`
- `--full-check`

- [ ] **Step 3: 增加模板残留物检查**

至少识别：

- `[填写]`
- `[PROJECT_NAME]`
- `TODO`
- `...`
- 明显异常 Markdown 表格行

- [ ] **Step 4: 增加运行记录完整性检查**

至少识别：

- `generation_plan.md` 是否具备契约要求的 heading
- `generation_progress.md` 是否具备 required fields
- 是否存在“已完成/已执行”但没有对应细节字段的空泛状态

- [ ] **Step 5: 设计输出结构扩展**

现有输出 JSON 中新增：

```json
{
  "checks": {
    "required_sections": {"checked": 1, "issues": []},
    "template_residue": {"checked": 3, "issues": []},
    "run_record_integrity": {"checked": 2, "issues": []}
  }
}
```

- [ ] **Step 6: 编写回归测试**

至少覆盖：

- 缺少主文档必需章节时返回 issue
- `generation_progress.md` 缺字段时返回 issue
- 有残留占位符时返回 issue
- 老 CLI 行为未被破坏

- [ ] **Step 7: 执行验证**

Run:

```bash
python3 -m unittest tools/py/tests/test_doc_health_checker.py
node tools/js/doc_health_checker.test.js
python3 tools/py/doc_health_checker.py --help
node tools/js/doc_health_checker.js --help
```

Expected:

- 新检查项出现在帮助信息里
- 旧用法仍可执行

**Done when:**

- `doc_health_checker` 能自动发现这次已经被人工确认过的基础结构问题和运行记录问题

### Task 5: 实现半自动语义复查 checker

**Files:**
- Create: `tools/py/semantic_review_checker.py`
- Create: `tools/js/semantic_review_checker.js`
- Create: `tools/testdata/semantic_review/conflict_case/`
- Create: `tools/testdata/semantic_review/metric_drift_case/`
- Create: `tools/testdata/semantic_review/test_topology_case/`
- Create: `tools/py/tests/test_semantic_review_checker.py`
- Create: `tools/js/semantic_review_checker.test.js`
- Reuse where possible: `tools/py/project_scanner.py`, `tools/js/project_scanner.js`

- [ ] **Step 1: 设计最小可行 CLI**

CLI 至少支持：

```bash
--doc-dir <dir>
--repo-root <dir>
--format json|text
--check-fact-conflicts
--check-metrics
--check-test-topology
--full-check
```

- [ ] **Step 2: 实现量化声明校验**

最小实现要求：

- 从文档中抓取“X 个文件 / Y 个模块 / Z 个测试”等模式
- 对指定目录进行复算
- 输出差异值和原文位置

允许第一版只覆盖最常见表达式，不追求 NLP 完整识别。

- [ ] **Step 3: 实现测试资产拓扑检查**

最小实现要求：

- 扫描：
  - `tests/`
  - `examples/**/tests/`
  - `test/`
  - 其他现成 `project_scanner` 已能发现的测试线索
- 生成测试资产摘要：
  - 目录
  - 文件数
  - 是否被 `testing_guide` 覆盖

- [ ] **Step 4: 实现事实源冲突检查**

第一版不做复杂语义推理，只做规则化冲突扫描：

- 从 `dev_docs` 抽取高强度表述：
  - `推荐`
  - `必须`
  - `优先`
  - `不建议`
  - `deprecated`
- 与以下来源做近邻比对：
  - `README.md`
  - `docs/**/*.md`
  - 关键源码注释（先只扫高频目录，避免全仓全文索引过重）

- [ ] **Step 5: 输出统一报告结构**

JSON 输出至少包括：

```json
{
  "summary": {"passed": false},
  "checks": {
    "fact_conflicts": [],
    "metrics": [],
    "test_topology": []
  }
}
```

- [ ] **Step 6: 编写最小测试数据与测试**

至少覆盖：

- 数字失真 case
- `examples/**/tests/` 漏报 case
- 推荐实践冲突 case

- [ ] **Step 7: 执行验证**

Run:

```bash
python3 -m unittest tools/py/tests/test_semantic_review_checker.py
node tools/js/semantic_review_checker.test.js
python3 tools/py/semantic_review_checker.py --help
node tools/js/semantic_review_checker.js --help
```

Expected:

- CLI 可运行
- 三类最小能力都能返回结构化结果

**Done when:**

- AICC 自动化复查能力不再只停留在格式层

### Task 6: 把 health check 和 semantic review 接入首版生成流程

**Files:**
- Modify: `workflows/path_a_first_generation.md`
- Modify: `workflows/generation_workflow.md`
- Modify: `workflows/path_b_health_check.md`
- Modify: `templates/HEALTH_CHECK_REPORT_TEMPLATE.md`
- Modify: `workflows/shared/ai_checklist.md`（如需要）

- [ ] **Step 1: 在 `path_a_first_generation.md` 新增“首版质量验收”步骤**

插入位置：

- Step 8 之后
- Step 8.5 或同等显式命名

内容必须包括：

- 运行 `doc_health_checker`
- 运行 `semantic_review_checker`
- 生成 `health_check_report.md`
- 验收不通过时不得写“已完成”

- [ ] **Step 2: 调整 `generation_progress.md` 的完成语义**

必须明确：

- “文档已生成” ≠ “任务已完成”
- 只有“文档生成完成 + 验收通过 + 报告落盘”才可写“已完成”

- [ ] **Step 3: 让 `generation_workflow.md` 对齐新的 Definition of Done**

至少改清楚：

- 必需章节检查
- 运行记录完整性检查
- 语义复查最小要求
- 失败时的阻断策略

- [ ] **Step 4: 复用或扩展 `HEALTH_CHECK_REPORT_TEMPLATE.md`**

模板要能承载：

- 结构检查结果
- 运行记录检查结果
- 量化声明校验结果
- 测试资产拓扑摘要
- 事实源冲突摘要
- 最终 verdict

- [ ] **Step 5: 对齐 `path_b_health_check.md`**

要求：

- 首版交付报告和路径 B 健康检查报告尽量同构
- 但不要强迫所有 Path B 细节都进入首版流程

- [ ] **Step 6: 目视复核 workflow 是否仍可被用户直接照着走**

Run:

```bash
rg -n "health_check_report|semantic_review|质量验收|已完成" workflows/path_a_first_generation.md workflows/generation_workflow.md workflows/path_b_health_check.md templates/HEALTH_CHECK_REPORT_TEMPLATE.md
```

Expected:

- 三个 workflow 与模板在命名和产物路径上保持一致

**Done when:**

- AICC 首版生成从“写完文件”升级为“写完 + 通过验收”

### Task 7: 把运行留痕纳入流程完成条件

**Files:**
- Modify: `templates/GENERATION_PLAN_TEMPLATE.md`
- Modify: `templates/PROGRESS_TEMPLATE.md`
- Modify: `workflows/path_a_first_generation.md`
- Modify: `workflows/generation_workflow.md`
- Reuse: `core/contracts/run_record_contract.yaml`

- [ ] **Step 1: 明确 Step 7.5 的留痕要求**

必须要求记录：

- 方案已生成
- 等待用户审核
- 用户确认时间或确认状态
- 正式进入生成阶段

- [ ] **Step 2: 让 `generation_plan.md` 成为“可执行计划”而非摘要**

至少要求有：

- 复杂度评估
- 子文档生成范围
- 量化声明来源
- 测试扫描范围
- 验收命令

- [ ] **Step 3: 让 `generation_progress.md` 成为状态机记录**

至少要求状态变更包含：

- 当前状态
- 更新时间
- 本步结果
- 下一步
- 阻塞原因（如果存在）

- [ ] **Step 4: 将运行记录完整性接入 checker**

此步骤不新写逻辑，只验证 Task 4 的输出已经在 workflow 中被真正要求使用。

- [ ] **Step 5: 对照模板和 workflow 做一致性扫描**

Run:

```bash
rg -n "开始时间|最后更新|当前状态|等待人工审核|用户确认|验收命令" templates/GENERATION_PLAN_TEMPLATE.md templates/PROGRESS_TEMPLATE.md workflows/path_a_first_generation.md workflows/generation_workflow.md
```

Expected:

- 模板和 workflow 都能找到对应字段/步骤

**Done when:**

- 会话中断后，后续 AI 可以只靠 `_analysis/` 基本恢复执行现场

### Task 8: 为新能力补充测试数据、回归命令与文档入口

**Files:**
- Create or Modify: `tools/testdata/**`
- Modify: `templates/README.md`（若有必要）
- Modify: `workflows/maintenance_workflow.md`
- Optional Modify: `README.md` 或 `AI_ENTRY_POINT.md`（仅在 Public 入口需要暴露新 checker 时）

- [ ] **Step 1: 建立统一测试数据目录约定**

推荐新增：

- `tools/testdata/framework_contracts/`
- `tools/testdata/semantic_review/`
- `tools/testdata/doc_health/`

规则：

- 每个 case 目录内同时放输入和期望输出说明
- 文件名要表达 case 意图，不使用 `sample1` 这类弱命名

- [ ] **Step 2: 在维护工作流中补入新 checker 命令**

至少补入：

```bash
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs
node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs
```

- [ ] **Step 3: 确认入口文档是否需要露出新能力**

只有当新 checker 已经稳定可用时，才在入口文档里增加引用。
不要先在 Public 入口宣传、后补实现。

- [ ] **Step 4: 执行整体验证命令清单**

Run:

```bash
python3 -m unittest tools/py/tests/test_framework_contract_checker.py
python3 -m unittest tools/py/tests/test_doc_health_checker.py
python3 -m unittest tools/py/tests/test_semantic_review_checker.py
node tools/js/framework_contract_checker.test.js
node tools/js/doc_health_checker.test.js
node tools/js/semantic_review_checker.test.js
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
```

Expected:

- 全部通过
- 没有 CLI 回归破坏

**Done when:**

- 新能力不仅存在，而且被框架自己的维护流程消费

### Task 9: 执行一次框架自审 dogfood

**Files:**
- Modify if needed: 本轮涉及的任意文件
- Create: `dev/quality/audits/<date>_framework_dogfood/health_check_report.md` 或其他已存在的框架审计目录下等价记录文件

- [ ] **Step 1: 对当前仓库跑 contract checker**

Run:

```bash
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
```

- [ ] **Step 2: 选一个框架内可控的 `dev_docs/` 样本跑 health checker 与 semantic review**

优先级如下：

1. 若仓库内已有稳定 `dev_docs/` 样本，直接使用
2. 若没有，使用 `tools/testdata/semantic_review/` 下综合样本
3. 不要为了 dogfood 临时在框架根目录伪造一套新的 `dev_docs/`

- [ ] **Step 3: 记录发现的问题并只修框架问题**

重点观察：

- 规则是否过严导致大量噪音
- 目录扫描是否过宽导致误报
- 帮助信息和 JSON 输出是否足够让后续 AI 消费

- [ ] **Step 4: 收敛阈值和默认模式**

如果误报太多，优先调整：

- 默认扫描范围
- 仅告警 vs 直接 error 的分级
- `--full-check` 中是否默认启用全部语义检查

**Done when:**

- 新增能力至少在一次真实框架自审中可运行、可读、可调

## 9. 推荐提交顺序

按下面顺序提交，便于回滚与审查：

1. `contracts + spec sync`
2. `template cleanup + provenance slots`
3. `framework contract checker`
4. `doc health checker enhancements`
5. `semantic review checker`
6. `workflow + health report gate`
7. `run-record hardening`
8. `dogfood + docs polish`

## 10. 全局验收标准

全部任务完成后，必须满足下面这些最终条件：

1. `framework_contract_checker` 存在且可运行
2. `doc_health_checker` 能报出主文档缺章、模板残留、运行记录缺字段
3. `semantic_review_checker` 至少能覆盖：
   - 量化声明失真
   - 测试资产拓扑遗漏
   - 一类事实源冲突
4. `path_a_first_generation.md` 出现明确质量验收步骤
5. `generation_progress.md` 的“完成”含义已被收紧为“生成完成 + 验收通过”
6. `AI_Coding_Context_TEMPLATE.md` 已提升 `业务模块映射` 和 `常见任务速查` 的主干地位
7. Python / JS 两侧 CLI 都可运行且关键输出结构一致
8. 框架本身至少完成一次自审 dogfood

## 11. 不要做的事

执行 AI 在实施时不要做下面这些事：

- 不要一上来重写 `doc_health_checker`
- 不要先改 Public 入口宣传，再补工具实现
- 不要把语义复查第一版做成复杂 LLM 依赖工具
- 不要在没有测试数据的情况下硬写大量规则
- 不要把所有新能力都塞进一个脚本里
- 不要跳过 JS 对称实现然后默认“以后再补”

## 12. 计划完成后的执行建议

如果由 AI 继续执行，推荐分两轮：

1. 第一轮只做 P0
   - contracts
   - template cleanup
   - doc_health_checker 增强
   - path A 验收 gate

2. 第二轮再做 P1
   - framework_contract_checker
   - semantic_review_checker
   - dogfood 自审

P2 的“证据提取 → 文档渲染”重构不建议与 P0/P1 混在同一轮，否则实施风险和 review 负担都会明显增大。
