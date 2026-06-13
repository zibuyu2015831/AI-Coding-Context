---
title: Dayflow 首次运行复盘与 AICC Phase 1 改进计划
summary: 基于 Dayflow 项目首次运行 AICC 后生成的 generation_plan、project_analysis_report 与 progress 记录，以及方案代码级复查后的第二轮评估，复盘方案阶段暴露的问题，并提出 AICC 首次生成流程、模板、检查器与项目检测能力的改进计划。
keywords: aicc | dayflow | phase1 | first-generation | generation-plan | semantic-review | project-scanner
scope: AICC 首次生成流程的方案阶段改进；不包含 Dayflow dev_docs 正式文档生成，也不直接实施框架代码修改
related_files: workflows/path_a_first_generation.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | core/contracts/run_record_contract.yaml | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js | tools/py/project_scanner.py | tools/js/project_scanner.js
dependencies: AI_ENTRY_POINT.md | core/framework_spec.md | workflows/generation_workflow.md
verified_at: 2026-05-18
status: 已实施
---

# Dayflow 首次运行复盘与 AICC Phase 1 改进计划

> **当前阶段**：复盘与方案记录。本文档用于人工审核，审核通过后再进入 AICC 框架完善实施。
> **重要边界**：Dayflow 本次是 AICC 首次运行的方案阶段，只要求产出 `dev_docs/_analysis/generation_plan.md`、`project_analysis_report.md` 和 `generation_progress.md`。因此，未生成 `AI_Coding_Context.md`、P0/P1 子文档、规则文件和最终健康报告不算缺失。
> **实施状态**：本计划已于 2026-05-18 落地到 AICC workflow、模板、契约、Python/JS checker、project scanner、testdata 和专项验证记录。

---

## 一、复盘目标

本复盘不是评价 Dayflow 项目本身，也不是继续生成 Dayflow 文档体系，而是回答：

1. Dayflow 首次运行结果暴露出 AICC Phase 1 的哪些框架缺口？
2. 哪些问题应由模板或工作流约束解决？
3. 哪些问题应由工具检查器自动发现？
4. 后续实施应按什么顺序推进，如何验收？

---

## 二、Dayflow 本次运行事实

### 2.1 已生成产物

Dayflow 的 `dev_docs/` 目前只有方案阶段产物：

- `dev_docs/_analysis/generation_plan.md`
- `dev_docs/_analysis/project_analysis_report.md`
- `dev_docs/_analysis/generation_progress.md`

这符合“首次运行先生成方案，等待人工审核后再搭建文档体系”的阶段定义。

### 2.2 运行结果中的有效部分

本次运行有几个方向是正确的：

- 正确识别为大型 macOS Swift/SwiftUI 桌面项目。
- 规模统计经复核基本可信：262 个 Swift 文件，约 88,022 行 Swift 代码。
- 文档规划方向合理：优先规划 `architecture_overview.md`、`data_storage.md`、`ai_integration.md`，再扩展到录屏、隐私、UI、时间线、测试和分发。
- 明确进入人工审核门，没有直接生成完整文档体系。

### 2.3 暴露的问题

本次运行也暴露出 Phase 1 的质量边界不够硬：

1. **可由代码直接确认的事实被外包给用户确认**
   - `StorageManager.swift` 已明确 `import GRDB` 且使用 `DatabasePool`，但报告仍把数据库技术列为“需用户确认”。
   - `Package.resolved` 存在于 Xcode workspace 下，且列出 GRDB、PostHog、Sentry、Sparkle，但报告仍写“未发现 Package.resolved / 依赖管理需确认”。

2. **目录级分析给出了过强的架构结论**
   - 报告声明“基于目录结构和文件名的初步扫描”“分析覆盖度 20%”，但同时给出 `StorageManager 职责过重`、`技术债务 4-6 周`、`测试覆盖度不足 5%` 等较强判断。
   - 这些判断可以作为风险假设，但不应在缺少代码级证据时写成结论。

3. **方案阶段缺少独立质量门**
   - `doc_health_checker` 能发现未替换的模板填空标记，但 Path A 没有明确要求 Phase 1 在交给用户审核前必须跑自检。
   - `semantic_review_checker` 发现测试文件计数漂移，但其 Swift/Xcode 测试拓扑识别能力不足，导致自身也出现误判。

4. **进度记录口径混用**
   - `generation_progress.md` 同时出现流程步骤进度和整体产物完成度，但命名不清，容易把“已到人工审核门”误读成“整体文档体系完成度”。

### 2.4 第二轮复查后的新增发现

根据本计划给出的指令，Dayflow 项目中的 AI 对 `_analysis` 三个文档进行了代码级复查。第二轮评估显示，这种“AI 复查方案 → 修正方案 → 再由人工评估”的机制方向正确，但复查结果仍暴露出新的框架缺口：

1. **复查以追加修正为主，没有强制全文回写**
   - 文档新增了“复查记录”“代码级验证”等章节，正确确认了 GRDB、SPM 依赖、状态管理等事实。
   - 但 `generation_plan.md` 前文仍残留 `其他核心库: 待确认 (AI SDK, 可能的 SQLite.swift / GRDB)`、`检查 Package.resolved / Podfile.lock 确认依赖`、`SQLite/Core Data`、`存储方案: SQLite / Core Data / SwiftData (待确认)` 等旧结论。
   - 这说明 AICC 目前缺少“复查结论必须回写全文所有受影响段落”的约束。

2. **统计摘要没有跟随局部修正更新**
   - `project_analysis_report.md` 后文已将数据库、状态管理、依赖管理标记为已确认，但摘要仍写“🔵 疑问 5 个需确认”。
   - 这类摘要漂移会误导用户判断当前人工审核负担，也会误导后续 AI 继续向用户询问已经关闭的问题。

3. **强结论仍然残留在问题报告尾部**
   - 虽然复查已补充代码证据，`project_analysis_report.md` 仍保留“技术债务评估”“测试覆盖度低 P0”“预计 4-6 周解决核心问题”等强判断。
   - 这些内容应降级为“风险假设与后续验证建议”，并标注证据等级，而不是作为 Phase 1 的确定性治理结论。

4. **复查记录自身出现口径不一致**
   - 某处写“仍需人工确认 2 项”，另一处又列出 3 项，其中 `DayflowBackendProvider` 实际是 AI Provider 商业策略问题的子项。
   - 这说明 AICC 需要要求“待确认事项清单”只有一个权威列表，其他位置只能引用或摘要。

5. **运行记录尾部元信息未同步**
   - `generation_progress.md` 顶部最后更新为 13:00，底部仍为 12:00。
   - `semantic_review_checker` 运行记录写 4 个 drift，但第二轮实测为 5 个 issue。
   - 这说明进度记录需要检查同名元信息和工具输出摘要的一致性。

6. **结构检查 PASS 不能代表语义一致**
   - `doc_health_checker` 对 Dayflow `_analysis` 三个文档返回 PASS、0 issues，但仍无法发现上述旧结论残留、摘要漂移、路径拼写 `xcsharedata` 等问题。
   - 因此 Phase 1 需要在结构检查和人工审核之间增加“复查后全文一致性检查”。

---

## 三、AICC 需要完善的原则

### 3.1 Phase 1 可以不完整，但必须可审核

首次运行方案阶段不要求生成全部文档，但必须满足：

- 事实来源可追溯。
- 推断和结论分级清楚。
- 待确认事项不能包含明显可由代码确认的事实。
- 进度记录能准确表达当前 gate 和产物完成度。
- 方案文档自身不含模板残留。
- 复查后的修正必须回写全文，不得只在文末追加更正说明。

### 3.2 自动事实优先，不把工具可查事实交给用户

AICC 应把待确认事项分为三类：

| 类别 | 定义 | 示例 | Phase 1 处理方式 |
|---|---|---|---|
| 已由代码确认 | 已从源码、配置、锁文件或 README 直接确认 | `import GRDB`、`Package.resolved` | 写入事实表，标明证据文件 |
| 可继续读取确认 | 当前未读取到，但可通过继续读代码确认 | 迁移版本策略、模型覆盖范围 | 列为下一步代码级核查，不优先问用户 |
| 只能由用户确认 | 代码无法表达的产品、路线或业务优先级 | Provider 是否计划废弃、业务语义优先级 | 放入人工审核问题 |

### 3.3 证据等级决定措辞强度

建议 AICC 引入证据等级：

| 等级 | 证据来源 | 允许措辞 |
|---|---|---|
| E1 | 目录结构、文件名、文件数量 | “疑似”“风险假设”“建议后续验证” |
| E2 | 配置文件、锁文件、README、项目文件 | “已从配置确认”“技术栈事实” |
| E3 | 源码片段、协议、关键函数、调用链 | “代码显示”“实现方式为” |
| E4 | 构建、测试、脚本运行、工具检查结果 | “已验证”“检查通过/失败” |

规则：

- E1 不得直接生成 P0/P1 技术债结论。
- 架构判断至少需要 E3。
- “必须修复”“严重问题”至少需要 E3，并最好有 E4 验证。
- 方案阶段允许 E1 风险假设，但必须明确后续验证动作。

### 3.4 复查不是追加补丁，必须形成全文一致状态

Dayflow 第二轮复查显示，AI 能识别并更正关键事实，但容易把更正写入新增章节，而不清理旧段落。AICC 应明确：

- 复查结论一旦改变事实状态，必须同步更新摘要、正文、表格、待确认清单、行动计划和进度记录。
- 同一事实只能有一个当前状态；历史变化应进入“复查记录”，不能与正文当前结论冲突。
- “仍需人工确认”的权威清单只能有一份；其他章节只能引用该清单或给出数量摘要。
- 工具运行结果必须记录真实 issue 数量、命令参数和人工判定，不得只写概括性结论。
- 若 `doc_health_checker` 通过但全文一致性扫描失败，Phase 1 仍不得进入人工审核通过状态。

---

## 四、改进范围

### 4.1 工作流改进

目标文件：

- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`

建议变更：

1. 在 Path A 的 Step 7 “AI 互审”后、Step 7.5 “等待人工审核”前新增 **Phase 1 自检门**。
2. 明确 Phase 1 自检不要求主文档或子文档存在，但要求 `_analysis` 产物质量达标。
3. 新增失败处理规则：若存在模板残留、明显事实漂移、进度口径冲突，AI 必须先修正方案文档，再请求用户审核。
4. 新增复查后收敛规则：若 AI 复查改变了事实或疑问状态，必须执行全文一致性清理，再输出“等待人工审核”。

建议自检命令：

```bash
python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs
node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .
node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .
```

过渡期说明：在 Task 5 完成前，`semantic_review_checker` 对 Swift/Xcode 测试拓扑可能误判。Phase 1 自检仍应运行该工具，但 Swift/Xcode 相关失败项需要人工复核后再决定是否阻塞审核。

### 4.2 模板改进

目标文件：

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/generation_plan_trivial.md`
- `templates/generation_plan_simple.md`
- `templates/generation_plan_complex.md`
- `templates/generation_plan_medium.md`
- `templates/generation_plan_critical.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`

建议变更：

1. 强化现有“证据与验证记录”章节：

```markdown
## 🧾 证据与验证记录

| 事实 | 证据等级 | 来源文件 | 验证方式 | 结论 |
|---|---|---|---|---|
| [事实描述] | E2/E3/E4 | `[path:line]` | [读取/命令/测试] | [已确认/待复核] |
```

2. 新增“待确认事项准入规则”：

```markdown
以下内容不得直接放入用户确认清单：
- 可从依赖锁文件确认的依赖管理工具和依赖列表
- 可从源码 import/use 关系确认的数据库或核心库
- 可从 README 或项目配置确认的构建入口

如果当前未确认，必须先列为“下一步代码级核查”，而不是直接要求用户回答。
```

3. 将问题报告中的“技术债务评估”调整为“风险假设与证据等级”，避免 Phase 1 过早给出工期和优先级结论。若仍保留技术债务表，必须为每一项标注证据等级和验证状态。

4. 新增“复查回写要求”：

```markdown
## 🔄 复查回写要求

当复查结论改变事实状态时，必须同步检查并更新：
- 报告摘要中的技术栈、疑问数量和问题统计
- 正文中的项目基础分析、业务模块表和模式总结
- 需要人工确认的项目特性清单
- 审核与行动计划
- 证据与验证记录
- generation_progress.md 中的状态、时间、工具运行结果

禁止只在文末追加“复查记录”而保留正文旧结论。
```

### 4.3 进度记录改进

目标文件：

- `templates/PROGRESS_TEMPLATE.md`
- `core/contracts/run_record_contract.yaml`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

建议变更：

1. 将单一“进度”拆成两个字段：

```markdown
- **流程阶段进度**: Step 6/9，当前处于人工审核门
- **产物完成度**: 3/18，已完成 `_analysis` 产物，主文档和子文档尚未开始
```

2. 在 run record contract 中要求 `generation_progress.md` 同时包含：
   - `流程阶段进度`
   - `产物完成度`
   - `当前 gate`
   - `下一步动作`

3. 增加检查逻辑：同一文档中出现多个百分比时，必须标明它们分别代表什么。

4. 增加检查逻辑：同一进度文件中出现多个“最后更新”或工具 issue 数量时，必须一致；若不一致则报错。

### 4.4 Swift/Xcode 项目检测改进

目标文件：

- `core/project_types/desktop_app.md`
- `core/project_types/mobile_app.md`
- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`

建议变更：

1. 在 macOS/iOS 项目检测清单中加入：
   - `*.xcodeproj/project.pbxproj`
   - `*.xcworkspace/xcshareddata/swiftpm/Package.resolved`
   - `Info.plist`
   - `*.entitlements`
   - `README.md`
   - `scripts/`

2. 在 `project_scanner` 输出中新增结构化字段：

```json
{
  "dependency_manifest_candidates": [
    "Dayflow/Dayflow.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved"
  ],
  "xcode_project_files": [
    "Dayflow/Dayflow.xcodeproj/project.pbxproj"
  ],
  "platform_config_files": [
    "Dayflow/Dayflow/Info.plist",
    "Dayflow/Dayflow/Dayflow.entitlements"
  ]
}
```

3. 首次运行方案阶段必须引用这些字段，避免只扫描根目录导致误判。

### 4.5 语义检查器改进

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

建议变更：

1. 扩展测试拓扑识别：
   - `tests/`
   - `test/`
   - `*Tests/`
   - `*UITests/`
   - `*Tests.swift`
   - `*UITests.swift`

2. 对 Swift/Xcode 项目，将测试文件数量定义为测试目录下的测试源码文件数量，而不是只统计 `tests/` 目录。

3. 增加 Dayflow-like fixture：

```text
fixture/
├── Dayflow/
│   ├── Dayflow.xcodeproj/
│   │   └── project.xcworkspace/xcshareddata/swiftpm/Package.resolved
│   └── Dayflow/Core/Recording/StorageManager.swift
├── DayflowTests/TimeParsingTests.swift
└── DayflowUITests/DayflowUITests.swift
```

4. 增加回归断言：
   - 能识别 Swift 测试目录和测试文件。
   - 不把测试文件数算成 0。
   - 能识别 `Package.resolved` 不在仓库根目录的情况。

### 4.6 复查后全文一致性检查

目标文件：

- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/testdata/semantic_review/`

建议变更：

1. 增加“旧结论残留”规则，检测同一文档中同时出现已确认事实和旧待确认措辞。例如：
   - 已确认 GRDB 后，仍出现 `SQLite/Core Data`、`SwiftData (待确认)`、`可能的 SQLite.swift / GRDB`。
   - 已确认 SPM 依赖后，仍出现 `Package.resolved 待确认` 或 `检查 Package.resolved 确认依赖`。
   - 已确认 `EnvironmentObject` 状态管理后，仍出现 `状态管理方式: @State / @ObservedObject / @EnvironmentObject (待确认)`。

2. 增加“摘要与正文统计一致”规则：
   - 问题统计中的疑问数量必须等于当前仍需用户确认的问题数量。
   - 若疑问已关闭，应进入“已关闭疑问”或“已确认事实”，不得仍计入待确认总数。

3. 增加“权威待确认清单”规则：
   - `generation_plan.md` 和 `project_analysis_report.md` 中允许有多个引用位置，但必须能识别同一组当前待确认事项。
   - 子问题可以缩进到父问题下，不能在总数上重复计算。

4. 增加“强结论证据等级”规则：
   - `技术债务评估`、`P0`、`必须修复`、`预计 X 周` 等强结论如果出现在 Phase 1 报告中，必须同表包含证据等级和验证状态。
   - 缺少证据等级时，检查器应提示改为“风险假设”。

5. 增加“路径拼写与实际存在性增强”规则：
   - 对常见路径相似拼写进行提示，例如 `xcsharedata` 应为 `xcshareddata`。
   - 对引用的关键证据路径执行存在性校验，不能只检查 Markdown 格式。

6. 增加 Dayflow second-review fixture，覆盖以下失败样本：
   - 文末复查记录确认 GRDB，但正文仍写 `SQLite/Core Data`。
   - 摘要仍写 5 个疑问，但正文只有 2 个当前待确认事项。
   - 顶部与底部 `最后更新` 不一致。
   - 工具运行记录 issue 数量与实际输出不一致。

---

## 五、实施任务拆解

### Task 1：修订 Phase 1 工作流

**文件：**

- 修改：`workflows/path_a_first_generation.md`
- 修改：`workflows/generation_workflow.md`

**验收标准：**

- Path A 明确区分“方案阶段”和“完整文档体系阶段”。
- Step 7 后新增 Phase 1 自检门。
- 文档说明 Phase 1 不要求主文档存在，但要求 `_analysis` 产物通过基础质量检查。
- Phase 1 自检同时列出 Python 与 JS 检查器命令；Swift/Xcode 语义检查误判在 Task 5 完成前按人工复核处理。

### Task 2：修订方案与问题报告模板

**文件：**

- 修改：`templates/GENERATION_PLAN_TEMPLATE.md`
- 修改：`templates/generation_plan_trivial.md`
- 修改：`templates/generation_plan_simple.md`
- 修改：`templates/generation_plan_complex.md`
- 修改：`templates/generation_plan_medium.md`
- 修改：`templates/generation_plan_critical.md`
- 修改：`templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`

**验收标准：**

- 模板包含证据等级定义。
- 模板包含“自动事实优先”规则。
- `GENERATION_PLAN_TEMPLATE.md` 既有“证据与验证记录”章节被增强，而不是重复新增一个同名章节。
- 所有 `templates/generation_plan_*.md` 分级模板的 Phase 1 审核规则保持一致，不能只修 medium/complex 后让其他复杂度路径继续生成旧口径方案。
- 模板中的问题/建议示例不再把 E1 推断写成强结论。
- 模板中的待确认清单只包含代码无法直接确认的问题。

### Task 3：修订进度模板和运行记录契约

**文件：**

- 修改：`templates/PROGRESS_TEMPLATE.md`
- 修改：`core/contracts/run_record_contract.yaml`
- 修改：`tools/py/doc_health_checker.py`
- 修改：`tools/js/doc_health_checker.js`
- 修改：相关测试文件

**验收标准：**

- `generation_progress.md` 契约要求同时记录流程阶段进度和产物完成度。
- 检查器能发现未标注含义的多百分比进度。
- Python 和 JS 检查器行为一致。

### Task 4：增强 Swift/Xcode 项目检测

**文件：**

- 修改：`core/project_types/desktop_app.md`
- 修改：`core/project_types/mobile_app.md`
- 修改：`tools/py/project_scanner.py`
- 修改：`tools/js/project_scanner.js`
- 修改：相关测试或 testdata

**验收标准：**

- 扫描器能发现 workspace 内的 `Package.resolved`。
- 扫描器能输出 Xcode 项目文件、平台配置文件和依赖 manifest 候选列表。
- Swift/macOS 项目类型说明文档包含这些必查文件。

### Task 5：增强语义复查的 Swift/Xcode 适配

**文件：**

- 修改：`tools/py/semantic_review_checker.py`
- 修改：`tools/js/semantic_review_checker.js`
- 修改：`tools/py/tests/test_semantic_review_checker.py`
- 修改：`tools/js/semantic_review_checker.test.js`
- 新增或修改：`tools/testdata/semantic_review/` 下的 Dayflow-like fixture

**验收标准：**

- `*Tests/` 和 `*UITests/` 被识别为测试目录。
- `*Tests.swift` 和 `*UITests.swift` 被识别为测试文件。
- Swift/Xcode fixture 中测试文件数不会被误报为 0。
- Python 与 JS 版本保持对称。

### Task 6：补充框架自检与回归验证

**文件：**

- 修改：`tools/py/tests/`
- 修改：`tools/js/*.test.js`
- 修改：`dev/quality/audits/` 中的 dogfood 记录或新增一次专项验证记录

**验收标准：**

- `python3 tools/py/framework_contract_checker.py --self-check` 通过。
- `node tools/js/framework_contract_checker.js --self-check` 通过。
- `python3 tools/py/doc_health_checker.py --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs` 通过。
- `node tools/js/doc_health_checker.js --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs` 通过。
- Python checker 测试通过。
- JS checker 测试通过。
- 新增 Dayflow-like fixture 覆盖本次复盘暴露的问题。

### Task 7：增加复查后全文一致性规则

**文件：**

- 修改：`tools/py/doc_health_checker.py`
- 修改：`tools/js/doc_health_checker.js`
- 修改：`tools/py/semantic_review_checker.py`
- 修改：`tools/js/semantic_review_checker.js`
- 修改：`tools/py/tests/test_doc_health_checker.py`
- 修改：`tools/py/tests/test_semantic_review_checker.py`
- 修改：`tools/js/doc_health_checker.test.js`
- 修改：`tools/js/semantic_review_checker.test.js`
- 新增或修改：`tools/testdata/semantic_review/dayflow_second_review_case/`

**验收标准：**

- 能发现“文末复查记录已确认 GRDB，但正文仍写 SQLite/Core Data 或待确认”的冲突。
- 能发现“摘要疑问数量”和“当前待确认清单数量”不一致。
- 能发现同一文档中多个 `最后更新` 不一致。
- 能发现 `xcsharedata` 这类关键路径拼写错误或关键证据路径不存在。
- 能提示 Phase 1 报告中的 `技术债务评估`、`P0`、`预计 X 周` 必须带证据等级，否则降级为风险假设。
- Python 与 JS 版本保持对称。

---

## 六、建议实施顺序

1. **先改文档和流程**
   - Task 1、Task 2、Task 3 先做。
   - 这些改动能最快防止后续 AICC 首次运行继续产生误导性方案。

2. **再改检查器**
   - Task 5 和 Task 7 优先于 Task 4。
   - 原因：Dayflow 中已经暴露出测试拓扑误判和复查后全文不一致，语义检查器与结构检查器自身需要先可信。

3. **最后增强扫描器**
   - Task 4 需要同时维护 Python/JS 对称输出，改动面较大，适合在模板和检查器目标明确后实施。

4. **收尾做 dogfood**
   - Task 6 用 Dayflow-like fixture 与 second-review fixture 验证所有改动确实覆盖本次问题。

---

## 七、风险与注意事项

### 7.1 避免把 AICC 变成过重审计工具

本次改进目标是提高 Phase 1 方案质量，不是要求首次运行就完成完整代码审计。证据等级机制应帮助 AI 控制措辞，而不是强制读取全项目。

### 7.2 保持 Python/JS 双脚本对称

AICC 已有双脚本红线。任何检查器或扫描器增强都必须同步 Python 和 JS 实现，并补充对应测试。

### 7.3 不要求 Phase 1 生成最终健康报告

Phase 1 可以记录自检命令和结果，但不应把 `health_check_report.md` 作为必需产物。最终健康报告仍应属于首版文档体系生成后的验收阶段。

### 7.4 防止“待确认事项”被过度压缩

不是所有问题都能自动确认。业务语义、产品路线、云端 Provider 维护状态等仍应进入用户审核清单。改进目标是过滤掉“代码已能回答的问题”。

### 7.5 防止复查记录变成“补丁日志”

复查记录应保留历史变化，但不能替代正文修正。AICC 应避免生成“正文仍错，文末说明已更正”的文档状态，因为后续 AI 读取时可能优先使用正文旧信息。

---

## 八、审核清单

请审核以下问题：

- [ ] 是否认可“Phase 1 不要求完整文档体系，但要求方案自检通过”的边界？
- [ ] 是否认可 E1-E4 证据等级作为 AICC 模板统一表达规则？
- [ ] 是否认可“自动事实优先，不把工具可查事实交给用户”的待确认事项准入规则？
- [ ] 是否认可优先实施模板/流程，再实施检查器和扫描器？
- [ ] 是否认可将“复查后全文一致性检查”作为 Phase 1 自检门的一部分？
- [ ] 是否需要把本计划拆成多个独立实施计划，分别覆盖模板、检查器、扫描器？

---

## 九、审核通过后的下一步

审核通过后，已按以下方式完成实施：

1. 新建或确认实施分支。
2. 按 Task 1-3 先完成文档/契约改动。
3. 运行框架契约检查器确认模板和 workflow 未漂移。
4. 按 Task 5 增强语义检查器并补 Swift/Xcode fixture。
5. 按 Task 7 增加复查后全文一致性规则和 second-review fixture。
6. 按 Task 4 增强项目扫描器。
7. 执行完整回归与 dogfood，记录验证结果。

专项验证记录见 `dev/quality/audits/2026-05-18_dayflow_phase1_aicc_improvement_verification.md`。

---

## 十、参考证据

本计划基于以下本地复查证据形成：

- Dayflow 首次运行产物：`/Users/zibuyu/code/openSource/Dayflow/dev_docs/_analysis/generation_plan.md`
- Dayflow 问题报告：`/Users/zibuyu/code/openSource/Dayflow/dev_docs/_analysis/project_analysis_report.md`
- Dayflow 进度记录：`/Users/zibuyu/code/openSource/Dayflow/dev_docs/_analysis/generation_progress.md`
- Dayflow 第二轮复查评估：`generation_plan.md` 中旧结论残留、`project_analysis_report.md` 中疑问数量与技术债务评估残留、`generation_progress.md` 中最后更新时间与 checker issue 数量不一致
- Dayflow 存储事实：`/Users/zibuyu/code/openSource/Dayflow/Dayflow/Dayflow/Core/Recording/StorageManager.swift`
- Dayflow 依赖事实：`/Users/zibuyu/code/openSource/Dayflow/Dayflow/Dayflow.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved`
- AICC Path A 工作流：`workflows/path_a_first_generation.md`
- AICC 方案模板：`templates/GENERATION_PLAN_TEMPLATE.md`
- AICC 问题报告模板：`templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`
- AICC 语义检查器：`tools/py/semantic_review_checker.py` 与 `tools/js/semantic_review_checker.js`
