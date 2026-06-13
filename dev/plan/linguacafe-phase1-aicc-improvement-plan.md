---
title: AICC Phase 1 审核机制二次改进计划
summary: 基于 LinguaCafe 作为测试项目暴露出的 AICC 首次生成与 Phase 1 审核问题，评估 Dayflow Phase 1 改进落地后的实际效果，并沉淀下一轮 AICC 框架完善方向。
keywords: aicc | linguacafe | phase1 | first-generation | evidence-level | self-check | project-positioning
scope: AICC 首次生成与 Phase 1 审核机制的二次改进方案；LinguaCafe 仅作为测试样本，不包含 LinguaCafe 正式 dev_docs 生成，也不直接实施框架代码修改
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | core/contracts/run_record_contract.yaml | core/project_types/fullstack.md | core/project_types/web_frontend.md | core/project_types/containerized.md | tools/py/doc_health_checker.py | tools/js/doc_health_checker.js | tools/py/semantic_review_checker.py | tools/js/semantic_review_checker.js | tools/py/project_scanner.py | tools/js/project_scanner.js | tools/py/framework_contract_checker.py | tools/js/framework_contract_checker.js
dependencies: dev/plan/done/dayflow-phase1-aicc-improvement-plan.md | AI_ENTRY_POINT.md | core/framework_spec.md
verified_at: 2026-05-18
status: proposed（待审核）
---

# AICC Phase 1 审核机制二次改进计划

> **当前阶段**：复盘与方案记录。本文档用于人工审核，审核通过后再进入 AICC 框架完善实施。
> **重要边界**：LinguaCafe 只是用于测试 AICC 框架的样本项目，不是本计划要改进的目标项目。本文档真正要改进的是 AICC 在“首次生成后进入 Phase 1 人工审核”时的框架能力。
> **阶段边界**：LinguaCafe 本次也是 AICC 路径 A 的首次运行，只要求产出 `dev_docs/_analysis/generation_plan.md`、`project_analysis_report.md` 和 `generation_progress.md`。因此，未生成正式 `AI_Coding_Context.md`、子文档、AI Rules 和最终 `health_check_report.md` 不算缺失。
> **核心判断**：Dayflow 后的 Phase 1 改进已经有效降低明显事实误判，但 LinguaCafe 暴露出新的框架缺口：自检证据没有落盘、证据等级没有强制进入产物、项目定位没有充分驱动文档清单，且 Phase 1 审核尚未被建模为可验证状态机。

---

## 一、复盘目标

本复盘不评价 LinguaCafe 项目质量，也不继续生成 LinguaCafe 文档体系。LinguaCafe 在这里的角色是测试夹具和问题暴露样本。本文档要回答的是 AICC 框架本身的问题：

1. Dayflow 后的 AICC Phase 1 改进，在 LinguaCafe 首次运行中哪些已经生效？
2. LinguaCafe 运行结果还暴露出哪些框架层缺口？
3. 这些缺口应通过工作流、模板、契约、检查器还是项目类型策略来修复？
4. 后续实施应按什么顺序推进，如何验证不会重新引入 Dayflow 类问题？

---

## 二、真实触发场景

### 2.1 用户实际使用方式

为了测试 AICC 是否能依赖自身入口文档完成审核，而不是依赖用户提供长篇审核清单，本轮采用更接近日常使用的短指令：

```text
AI-Coding-Context/AI_ENTRY_POINT.md 审核 dev_docs/_analysis 下已经生成的方案和分析结果，判断这次 Phase 1 是否可以通过，是否可以进入正式文档生成阶段。
```

这条指令只携带 AICC 入口文档和用户目标，没有显式列出以下细节：

- 应读取哪些 workflow 和模板。
- 应运行哪些 checker。
- 应检查证据等级。
- 应复核待确认事项准入。
- 应检查 `CONTRIBUTING.md`、`manual/`、`docker-compose*.yml` 等项目定位信号。
- 应把自检命令、issue 数、人工复核结论写回 `generation_progress.md`。

### 2.2 对 AICC 的真实要求

AICC 框架应能从 `AI_ENTRY_POINT.md` 自行推导出完整的 Phase 1 审核流程。用户只说“审核 `_analysis` 并判断能否进入正式生成”时，AI 也必须自动进入 Phase 1 Review Gate，而不是把这当作普通文档阅读请求。

因此，前期长提示词中的审核责任需要内化到 AICC，而不是要求用户每次复述。内化后的触发条件包括：

- 用户提到 `AI_ENTRY_POINT.md`。
- 用户要求“审核 `dev_docs/_analysis`”。
- 用户要求判断“Phase 1 是否通过”。
- 用户要求判断“是否可以进入正式文档生成阶段”。

只要满足上述任一或组合条件，AICC 应触发 Phase 1 审核响应流程。

### 2.3 从测试样本到框架改进的转化原则

LinguaCafe 暴露的问题只作为 AICC dogfood 证据使用，不能把后续实施方向写成“继续完善 LinguaCafe 文档体系”。本计划中的每一项修复都必须满足：

- **修复对象是 AICC**：落点只能是 `AI_ENTRY_POINT.md`、workflow、template、contract、checker、project scanner、project type 规则、fixture 或 AICC 自身文档。
- **LinguaCafe 只提供测试夹具**：可以把 LinguaCafe-like 结构抽象成 `tools/testdata/` fixture，用于复现问题和验证修复，但不把 `/Users/zibuyu/code/openSource/LinguaCafe` 当作实施目标。
- **规则必须可泛化**：从 LinguaCafe 得出的规则应覆盖同类项目，例如开源自托管项目、传统后端框架 + SPA 前端项目、带用户手册项目、字典/语言/外部数据密集项目。
- **用户提示词不能成为前提**：前面长审核提示词只能作为需求来源，不能要求真实用户每次复述。AICC 必须能通过短指令和入口文档触发完整审核。

### 2.4 系统架构评审原则

从系统架构角度，本轮完善不能只增加提示词或单点检查规则，而要补齐 AICC Phase 1 审核子系统的几个基础边界：

| 架构维度 | 需要明确的问题 | 本计划中的落点 |
| --- | --- | --- |
| 状态机 | Phase 1 从“方案生成”到“可进入正式生成”有哪些合法状态和阻塞条件 | Phase 1 Review Gate、run record contract、progress 模板 |
| 单一事实源 | `generation_plan.md`、`project_analysis_report.md`、`generation_progress.md` 谁负责当前结论、问题和执行状态 | 全文回写清单、review writeback 检查 |
| 证据模型 | 哪些结论可由 E1/E2/E3/E4 支撑，哪些只能作为风险假设 | generation plan / analysis report 模板和 semantic checker |
| 工具边界 | checker PASS 代表什么，不代表什么；Python/JS 结果如何保持一致 | doc/semantic checker、framework contract checker |
| 项目定位 | 技术栈之外，开源、自托管、用户手册、外部数据/API 等信号如何影响文档规划 | project scanner、project type 规则、semantic coverage |
| 降级策略 | Node 不可用、checker 误报、超大项目扫描超时、外部 Wiki 无法联网时如何记录 | progress 自检记录、人工复核结论、未覆盖风险 |

---

## 三、LinguaCafe 测试样本运行事实

### 3.1 已生成产物

LinguaCafe 的 `dev_docs/` 当前只有方案阶段产物：

- `dev_docs/_analysis/generation_plan.md`
- `dev_docs/_analysis/project_analysis_report.md`
- `dev_docs/_analysis/generation_progress.md`

这符合 AICC 路径 A 的首次运行阶段定义。

### 3.2 代码级抽查确认的有效结论

本次运行中的主要技术判断基本成立：

| 结论 | 证据 | 判断 |
| --- | --- | --- |
| 主后端为 Laravel 11 / PHP 8.2 | `composer.json` 中 `laravel/framework`、`laravel/horizon`、`laravel/reverb`、`laravel/sanctum` | 已确认 |
| 主前端为 Vue 2 + Laravel Mix + Vuetify 2 | 根 `package.json`、`resources/js/app.js`、`webpack.mix.js` | 已确认 |
| `resources/vue3/` 是独立嵌套前端目录，但生产定位需确认 | `resources/vue3/package.json`、`resources/vue3/vite.config.js`，根目录无 workspace 配置 | 已确认“存在”，用途待确认 |
| 业务接口主要集中在 `routes/web.php` | `routes/web.php` 承载 auth/admin 下业务接口，`routes/api.php` 只有 Sanctum `/user` | 已确认 |
| Docker Compose 覆盖 webserver、mysql、redis、python 服务 | `docker-compose.yml` | 已确认 |
| 队列和广播是章节处理链路的一部分 | `app/Jobs/ProcessChapter.php` 实现 `ShouldQueue`，`routes/channels.php` 定义私有频道 | 已确认 |
| 当前自动化测试主要是认证与示例测试 | `tests/Feature/Auth/`、`tests/Feature/ExampleTest.php`、`tests/Unit/ExampleTest.php` | 已确认 |

### 3.3 工具复核结果

对 LinguaCafe 当前 `dev_docs/` 实际运行：

```bash
python3 tools/py/doc_health_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs
python3 tools/py/semantic_review_checker.py --full-check --doc-dir /Users/zibuyu/code/openSource/LinguaCafe/dev_docs --repo-root /Users/zibuyu/code/openSource/LinguaCafe
```

结果：

- `doc_health_checker`: PASS，0 issues。
- `semantic_review_checker`: PASS，0 issues。

这说明现有检查器能覆盖基础结构、模板残留、路径和部分语义一致性，但无法证明方案已经满足 Phase 1 所需的全部语义质量。

---

## 四、已经生效的 AICC 改进

### 4.1 正确区分首次运行阶段

LinguaCafe 没有把正式文档未生成误判为缺失，而是明确停在 Phase 1 人工审核门。这修复了 Dayflow 初评时容易误判“正式文档缺失”的风险。

### 4.2 进度口径明显改善

`generation_progress.md` 已拆分：

- `流程阶段进度`: 当前处于 Phase 1 人工审核门。
- `产物完成度`: 已完成 `_analysis` 方案产物，正式文档尚未开始。
- `当前 gate`: Phase 1 人工审核。
- `下一步动作`: 等待用户确认后进入正式文档生成。

这说明 `PROGRESS_TEMPLATE.md` 与 run record contract 的改进已被模型吸收。

### 4.3 事实判断比 Dayflow 首轮更谨慎

LinguaCafe 方案没有把可由代码确认的 Laravel、Vue 2、Docker、web 路由、队列等事实交给用户确认；`resources/vue3/`、部署范围、单用户约束等才进入用户确认。这符合“自动事实优先”的方向。

### 4.4 当前 AICC 开发进度约束

截至本计划形成时，AICC 已具备以下基础能力：

- Path A 已区分首次运行方案阶段和正式文档生成阶段。
- `PROGRESS_TEMPLATE.md` 和 run record contract 已要求区分流程阶段进度与产物完成度。
- Python/JS 均已有 `doc_health_checker`、`semantic_review_checker` 和 `framework_contract_checker`。
- 已存在 Dayflow-like、combined_case 等 semantic review testdata。

但这些能力仍处在“结构健康 + 部分语义检查”阶段，尚未完成：

- Phase 1 Review Gate 的状态机化。
- Phase 1 PASS 的阻塞条件自动检查。
- 审核请求后的全文回写验证。
- 项目定位信号的系统化扫描与规划覆盖检查。
- Python/JS checker 的标准排除策略一致性。

---

## 五、仍然暴露的框架缺口

### 5.1 Phase 1 自检没有形成可复查记录

现象：

- `generation_progress.md` 勾选了“Phase 1 自检”。
- 同一文件的验收进度仍显示 `doc_health_checker` 和 `semantic_review_checker` 未执行。
- 文档没有记录自检命令、运行时间、issue 数、PASS/FAIL、人工判定或是否跳过。

问题性质：

这是运行记录一致性问题。当前框架允许 AI 写出“已自检”的状态，但没有强制要求自检证据落盘。

框架缺口：

- `Phase 1 自检门` 的“推荐命令”仍不够硬。
- run record contract 没有要求记录 Phase 1 自检命令和结果。
- `doc_health_checker` 没有检查“Phase 1 自检已勾选，但 checker 执行项未记录”的矛盾。

### 5.2 证据等级机制没有进入实际方案产物

现象：

- AICC 模板已定义 E1-E4 证据等级。
- LinguaCafe 的 `generation_plan.md` 只有普通“证据与验证记录”，没有为关键事实标注 E1/E2/E3/E4。
- `project_analysis_report.md` 中的警告、疑问、建议也没有统一证据等级字段。

问题性质：

这是模板约束没有被模型稳定执行的问题。没有证据等级时，二轮复查很难快速判断哪些是配置事实、源码事实、工具验证结果，哪些只是目录级风险假设。

框架缺口：

- `GENERATION_PLAN_TEMPLATE.md` 有证据等级章节，但 Path A 工作流没有将其列为交付必需项。
- `semantic_review_checker` 当前只能识别少数强结论缺证据，不能检查关键事实表是否真正包含证据等级。
- 项目分析报告模板没有要求每个警告/疑问都标注证据等级与当前状态。

### 5.3 项目定位没有充分驱动子文档清单

现象：

LinguaCafe 是自托管开源语言学习项目，代码库中已有：

- `CONTRIBUTING.md`: 贡献边界、PR 规则、测试策略、分支策略、开发环境。
- `README.md`: 产品定位、语言支持、安装 Wiki、单用户/单服务器说明。
- `manual/`: 用户手册内容。
- `docker-compose-dev.yml` 和 `docker-compose-dev-macos.yml`: 开发环境路径。
- 大量字典、语言资源与 attribution 信息。

当前方案虽列出 `testing_guide.md`、`deployment_guide.md`、`dictionary_language_domain.md`，但没有把“开源贡献与开发环境指南”作为必要文档，也没有明确字典/语言文档需要覆盖数据来源、授权、外部 API 和用户导入边界。

问题性质：

这是“项目技术栈识别正确，但项目愿景和协作模式没有反向驱动文档体系”的问题。AICC 如果只按通用全栈项目模板生成，容易遗漏对开源自托管项目最关键的协作和数据边界文档。

框架缺口：

- 项目类型策略只覆盖技术形态，不够覆盖产品/协作定位。
- 文档清单生成缺少“项目定位触发器”：开源项目、自托管项目、数据/资源密集项目、用户手册项目、外部 API 密集项目。

### 5.4 测试建议没有吸收维护者协作规则

现象：

`project_analysis_report.md` 正确指出核心业务测试覆盖不足，但 LinguaCafe 的 `CONTRIBUTING.md` 明确写明维护者当前不使用 JS/Python/PHP 测试，并建议 PR 暂时不要直接添加测试。

问题性质：

“测试覆盖不足”是代码事实，但“优先补齐核心业务测试”作为建议需要同时考虑项目维护者规则。否则正式文档可能指导 AI 创建与项目协作规则冲突的 PR。

框架缺口：

- AICC 的测试文档生成策略默认从工程最佳实践出发，但没有要求读取 `CONTRIBUTING.md`、`DEVELOPMENT.md`、`docs/contributing` 等维护者规则。
- `testing_guide.md` 模板缺少“当前项目是否鼓励测试 PR”的字段。

### 5.5 检查器 PASS 容易造成过度信任

现象：

LinguaCafe 的两个检查器均 PASS，但仍存在上述自检证据未落盘、证据等级缺失、项目定位文档漏项等问题。

问题性质：

结构检查和现有语义检查是必要但不充分条件。框架需要明确 PASS 的含义边界，并让检查器覆盖更多 Phase 1 必需语义。

框架缺口：

- `doc_health_checker` 当前偏结构健康。
- `semantic_review_checker` 当前偏事实漂移与少量一致性模式。
- Phase 1 缺少“方案完整性评分”或“必需决策点覆盖检查”。

### 5.6 入口文档没有把新 gate 讲清楚

现象：

用户可以通过 `AI_ENTRY_POINT.md` 找到 AICC 路径 A、检查器和复查机制，但 LinguaCafe 运行结果显示，AI 仍可能把“进入人工审核”理解成只要写完三个 `_analysis` 文件即可，而不是“写完三个文件并完成可复查的 Phase 1 自检记录”。

问题性质：

这是入口指令和工作流细节之间的传导问题。即使底层模板和检查器改进了，如果入口文档没有把 Phase 1 gate 的完成条件讲清楚，首次运行仍可能绕过自检落盘。

框架缺口：

- `AI_ENTRY_POINT.md` 需要明确：Path A 首次运行在提交给用户审核前，必须完成 `_analysis` 方案自检并记录结果。
- 入口文档需要说明 `doc_health_checker` PASS 和 `semantic_review_checker` PASS 的边界，避免把结构 PASS 当成方案语义完整。

---

### 5.7 审核触发语义没有内化

现象：

用户真实指令只写了“`AI_ENTRY_POINT.md` 审核 `dev_docs/_analysis` 并判断 Phase 1 是否可以通过”，没有列出详细审核清单。如果 AICC 框架不内化审核责任，AI 可能只做普通摘要或只看 checker 输出，无法自动执行完整 Phase 1 Review Gate。

问题性质：

这是框架入口路由问题。AICC 不应要求用户知道并复述内部审核清单；用户只需要给出入口和目标，框架应负责把目标路由到正确工作流。

框架缺口：

- `AI_ENTRY_POINT.md` 缺少“Phase 1 审核请求”的触发语义。
- `workflows/path_a_first_generation.md` 缺少“收到用户审核请求后如何响应”的流程，而不只是“生成方案后如何等待用户审核”。
- 检查器和模板缺少对“审核响应完成”的可验证输出要求。

### 5.8 第二次运行只更新进度记录，没有全文回写方案主体

现象：

LinguaCafe 第二次运行使用真实短指令触发审核后，`generation_progress.md` 被更新为 `doc_health_checker` 和 `semantic_review_checker` 已执行，并写入 `Phase 1 verdict = PASS`。但 `generation_plan.md` 和 `project_analysis_report.md` 仍基本保持第一次版本：

- `generation_plan.md` 的“证据与验证记录”仍是 `结论 / 证据文件 / 验证方式` 三列表，没有 `证据等级`。
- `project_analysis_report.md` 仍没有给警告、疑问、建议补充统一的 E1/E2/E3/E4 证据等级。
- `generation_plan.md` 仍把“是否加入更完整的开源贡献者指南”作为用户确认问题，而不是根据 `CONTRIBUTING.md` 明确规划贡献/开发环境文档覆盖方式。
- `project_analysis_report.md` 仍建议“优先补齐核心业务测试”，没有吸收 `CONTRIBUTING.md` 中维护者不建议 PR 直接添加测试的规则。

问题性质：

这是 Phase 1 Review Gate 的核心失败模式：AI 响应了“审核”，但把审核理解成“更新进度和宣布 PASS”，没有执行“发现问题后全文回写 `_analysis` 文档”的责任。

框架缺口：

- Path A 缺少“审核请求后的全文回写责任清单”。
- `doc_health_checker` 没有检查 `Phase 1 verdict = PASS` 与缺失证据等级、缺失自检记录、缺失项目定位覆盖之间的矛盾。
- `semantic_review_checker` 没有检查“审核后只更新 progress，generation_plan / project_analysis_report 未同步更新”的 stale review 模式。

### 5.9 Phase 1 PASS 缺少阻塞条件

现象：

第二次运行在 `generation_progress.md` 中写入 `Phase 1 verdict = PASS，可进入正式文档生成`，但以下 Phase 1 必需条件仍未满足：

- 自检记录没有命令、exit code、issue 数和人工复核结论。
- 关键事实没有证据等级。
- 项目定位触发器没有充分进入子文档规划。
- 测试建议没有吸收维护者协作规则。

问题性质：

这是 gate 判定标准缺失。当前 AICC 允许“检查器通过”直接升级为“Phase 1 PASS”，但检查器自身尚未覆盖全部 Phase 1 语义要求。

框架缺口：

- `generation_progress.md` 模板缺少 Phase 1 PASS 前置条件清单。
- run record contract 只检查字段存在，不检查 PASS 结论是否具备证据。
- 检查器缺少 `phase1_pass_without_required_review_evidence` 类错误。

### 5.10 Python/JS 检查器对框架 symlink 排除不一致

现象：

对同一份 LinguaCafe `dev_docs` 运行检查器时：

- Python `doc_health_checker`: PASS，0 issues。
- Python `semantic_review_checker`: PASS，0 issues。
- Node `doc_health_checker`: PASS，0 issues。
- Node `semantic_review_checker`: FAIL，11 issues。

Node 失败的主要原因是 LinguaCafe 根目录下的 `AI-Coding-Context` symlink 被当作项目源码扫描，导致 AICC 自身的测试目录、testdata 和 dogfood 文档被纳入 LinguaCafe 的测试拓扑与事实冲突检查。

问题性质：

这是工具一致性问题。AICC 要求 Python/JS checker 等价，但当前在 framework symlink、标准排除目录和 testdata 处理上存在差异。真实项目为了运行 AICC 经常会把框架目录 symlink 到项目根，如果检查器不能稳定排除它，就会污染项目审核结果。

框架缺口：

- Python/JS `semantic_review_checker` 没有共享同一套标准排除规则。
- `project_scanner --exclude-standard` 的排除语义没有被 semantic checker 复用。
- 缺少带 `AI-Coding-Context` symlink 的 fixture，无法防止 Python/JS 行为漂移。

### 5.11 Phase 1 审核状态机没有形式化

现象：

文档中同时出现“等待人工审核”“Phase 1 自检”“Phase 1 verdict = PASS”“可进入正式文档生成”等状态语句，但框架没有定义这些状态之间的合法迁移。例如，第二次运行在用户尚未明确回复“方案审核通过”时写入“可进入正式文档生成”，这会弱化人工审核门。

问题性质：

这是状态机缺失问题。Phase 1 不只是一个文档阶段，而是一个 gate。gate 至少需要区分“待审核”“审核中”“需修正”“审核建议通过”“用户已确认”“正式生成中”。

框架缺口：

- `generation_progress.md` 没有枚举合法状态和状态迁移条件。
- `run_record_contract.yaml` 只检查字段存在，不检查状态组合是否合法。
- AI 响应审核请求时缺少“建议通过”和“用户已确认”之间的边界。

### 5.12 三份 `_analysis` 文档的权责边界不清

现象：

第二次运行只改了 `generation_progress.md`，没有同步更新 `generation_plan.md` 和 `project_analysis_report.md`。这说明 AI 没有理解三份文档的职责：

- `generation_plan.md` 应是当前文档体系生成方案的权威来源。
- `project_analysis_report.md` 应是当前风险、疑问、建议和待确认事项的权威来源。
- `generation_progress.md` 应是执行状态和检查记录的权威来源。

问题性质：

这是单一事实源边界问题。若 progress 可以单独宣布 PASS，而 plan/report 仍保留旧结论，后续 AI 会基于不一致的输入继续执行。

框架缺口：

- AICC 没有定义 `_analysis` 三件套的写入职责和同步规则。
- checker 没有检查“状态文档比方案/报告更新但主体结论未回写”的不一致。

### 5.13 审核证据缺少可审计的留存格式

现象：

第二次运行只写了 checker 已执行和通过，没有留下命令、版本、exit code、issue 数、原始输出摘要、人工复核说明和未覆盖风险。

问题性质：

这是审计证据缺口。Phase 1 Review Gate 的价值不只是“跑过工具”，而是后续人或 AI 能复现当时为什么允许或不允许进入下一阶段。

框架缺口：

- progress 模板没有标准的 “Phase 1 Review Packet”。
- checker 输出没有统一摘要格式供 AI 粘贴或结构化写回。
- 没有区分“机器检查通过”“人工复核通过”“用户确认通过”。

### 5.14 工具不可用和误报的降级策略不完整

现象：

真实项目中 Node 版 checker 可能不可用、Python/JS 结果可能不一致、symlink 可能造成误报、外部 Wiki 可能无法联网读取。当前方案要求运行工具，但没有充分定义工具失败时的合法处理路径。

问题性质：

这是可运维性问题。框架不能假设所有运行环境都有完整 Node/Python 工具链，也不能把已知误报直接等同于项目方案失败。

框架缺口：

- 缺少 `未运行 / 运行失败 / 误报人工豁免 / 阻塞失败` 的统一状态。
- 缺少“人工豁免必须记录原始 issue、原因、复查人/AI 判定、后续框架改进项”的规则。
- 缺少工具超时或大项目性能降级策略。

### 5.15 严重度和阻塞级别没有统一

现象：

方案中已有 error/warning 的描述，但未定义哪些问题必须阻塞 Phase 1，哪些可以作为正式生成时保留的风险说明。例如“用户手册边界缺失”可以是 warning，但“Phase 1 PASS 缺少证据”必须是 blocker。

问题性质：

这是 gate policy 问题。没有统一严重度模型，AI 可能把所有问题都降级成“建议”，也可能把非阻塞问题误判为不能继续。

框架缺口：

- checker issue 缺少统一 `severity` 与 `blocks_phase1` 字段。
- progress 中没有记录“阻塞项数量 / warning 数量 / 已人工豁免数量”。

### 5.16 大项目与多形态项目的扩展边界不足

现象：

LinguaCafe 是 Laravel + Vue 2 + Vue3 嵌套目录 + Docker + Python tokenizer 的多形态项目。Dayflow 是 Swift/macOS 项目。两者暴露的问题不同，但都说明 AICC 需要适应多语言、多运行时、多入口、多文档源项目。

问题性质：

这是扩展性问题。Phase 1 审核不能依赖某一个项目类型的固定清单，而应先识别项目形态，再选择审核关注面。

框架缺口：

- project type 规则对“传统后端框架 + SPA 前端”“开源自托管应用”“外部数据/API 密集应用”的组合覆盖不足。
- scanner 需要输出组合信号，而不只是单一 project type。
- checker 需要避免在超大项目或多 workspace 项目中全量深扫导致性能或误报问题。

---

## 六、框架完善目标

### 6.1 Phase 1 自检必须可追溯

目标状态：

- 如果文档写“Phase 1 自检已完成”，则必须同时记录自检命令、执行结果、issue 数、人工判定和下一步动作。
- 如果未运行检查器，则不得勾选“Phase 1 自检已完成”，只能写“待执行”或“跳过并说明原因”。

### 6.2 关键事实必须有证据等级

目标状态：

- `generation_plan.md` 的关键事实表必须包含 `证据等级` 列。
- `project_analysis_report.md` 的每个警告、疑问、建议必须能追溯到证据等级或标记为用户确认项。
- E1 只能支撑风险假设，E2/E3 才能支撑技术栈和架构事实，E4 才能支撑“已验证通过/失败”。

### 6.3 子文档规划必须受项目定位驱动

目标状态：

- AICC 不只识别技术栈，还识别项目定位触发器。
- 开源项目必须考虑贡献指南、开发环境、分支策略和维护者规则。
- 自托管项目必须考虑部署、安全配置、备份、升级和默认凭据风险。
- 数据/资源密集项目必须考虑数据来源、授权、attribution、外部 API、导入边界。
- 存在用户手册的项目必须考虑用户手册和开发文档的边界。

### 6.4 检查器 PASS 必须有明确语义边界

目标状态：

- `doc_health_checker` PASS 表示结构、路径、模板、运行记录基础健康。
- `semantic_review_checker` PASS 表示其已覆盖规则下的关键事实、证据等级、复查一致性、项目定位触发项没有明显缺口；不代表已经完成完整代码审计。
- 如果某类语义仍无法自动判断，检查器输出应明确“未覆盖项”，不能让用户误以为已经完整复核。

### 6.5 入口说明必须和 gate 条件一致

目标状态：

- `AI_ENTRY_POINT.md`、Path A 工作流、progress 模板和 checker 规则对 Phase 1 完成条件使用同一套口径。
- AI 在首次运行结束时不能只告诉用户“方案已生成”，还必须说明 Phase 1 自检结果、未覆盖风险和当前人工审核问题。

### 6.6 真实短指令必须能触发完整审核

目标状态：

- 用户只给出 `AI_ENTRY_POINT.md` 和“审核 `_analysis` / 判断 Phase 1 是否通过”的目标时，AI 必须自动读取 AICC 入口、进入 Phase 1 Review Gate，并执行审核责任。
- AICC 不依赖用户提供详细审核清单；详细清单应由框架入口、workflow、template、contract 和 checker 共同提供。
- 审核响应禁止直接进入正式文档生成，除非用户随后明确回复“方案审核通过”或等价确认。

### 6.7 Phase 1 PASS 必须可证明

目标状态：

- `Phase 1 verdict = PASS` 只能在所有 Phase 1 阻塞条件清零后出现。
- PASS 之前必须具备：自检记录完整、证据等级完整、待确认事项准入合格、项目定位触发器已处理或说明合并覆盖方式、审核结论已全文回写。
- 如果任一条件缺失，状态应保持 `等待人工审核 / 需修正`，不能写“可进入正式文档生成”。

### 6.8 Python/JS 工具结果必须一致

目标状态：

- Python/JS `doc_health_checker` 和 `semantic_review_checker` 对同一 fixture 的核心 verdict 必须一致。
- 所有 checker 默认排除 AICC 框架目录、symlink 框架目录、工具 testdata、`.git`、`vendor`、`node_modules` 等非目标项目内容。
- 如果工具实现差异导致结果不同，必须有 fixture 和测试捕获。

### 6.9 Phase 1 审核状态机必须显式化

目标状态：

- `generation_progress.md` 只能使用框架定义的状态：`待审核`、`审核中`、`需修正`、`建议通过`、`用户已确认`、`正式生成中`、`首版验收中`、`已完成`。
- `建议通过` 不等同于 `用户已确认`；AI 不得在用户确认前执行正式文档生成。
- 状态迁移必须有触发事件和证据，例如 checker 结果、人工复核、用户确认。

### 6.10 `_analysis` 三件套必须有单一事实源边界

目标状态：

- `generation_plan.md` 负责当前生成方案和子文档清单。
- `project_analysis_report.md` 负责当前风险、疑问、建议和用户确认项。
- `generation_progress.md` 负责执行状态、工具运行记录、verdict 和下一步动作。
- 任何审核结论改变事实状态时，必须同步更新对应权威文档。

### 6.11 工具降级和人工豁免必须可审计

目标状态：

- 工具未运行、运行失败、超时、误报豁免都必须以统一格式记录。
- 人工豁免不能直接变成 PASS，必须说明原始 issue、豁免原因、残余风险和后续框架改进项。
- checker 输出应提供可供 progress 写回的简明摘要。

### 6.12 严重度模型必须驱动 gate 判定

目标状态：

- 所有 checker issue 至少包含 `severity` 和 `blocks_phase1`。
- blocker 未清零时不得出现 `Phase 1 verdict = PASS`。
- warning 可以不阻塞正式生成，但必须进入方案风险或后续文档规划。

---

## 七、改进方案

### 7.0 Phase 1 Review Contract 与状态机

目标文件：

- `core/contracts/run_record_contract.yaml`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`

改进内容：

1. 定义 Phase 1 审核状态机：

```text
方案已生成 -> 待审核 -> 审核中 -> 需修正 -> 待审核
方案已生成 -> 待审核 -> 审核中 -> 建议通过 -> 用户已确认 -> 正式生成中
```

2. 明确状态含义：
   - `建议通过`: AI 认为 Phase 1 gate 已满足，但仍等待用户确认。
   - `用户已确认`: 用户明确回复“方案审核通过”或等价指令。
   - `正式生成中`: 只有用户确认后才能进入。
3. 增加非法状态组合检查：
   - `当前状态 = 等待人工审核` 但 `下一步 = 进入正式文档生成`，且未记录用户确认，应报 warning 或 blocker。
   - `Phase 1 verdict = PASS` 但 blocker 未清零，应报 blocker。
4. 在 contract 中定义三件套权责边界：
   - plan changes require plan writeback。
   - risk/question changes require report writeback。
   - tool/status changes require progress writeback。

### 7.1 工作流改进：强化 Phase 1 自检门

目标文件：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`

改进内容：

1. 将 Phase 1 自检从“推荐命令”升级为“必须记录的 gate”。
2. 在进入“等待人工审核”前，要求 `_analysis/generation_progress.md` 写入：
   - `Phase 1 自检时间`
   - `doc_health_checker 命令`，分别记录 Python/JS 实现或说明只运行一个实现的原因
   - `doc_health_checker 结果`，包含 exit code、issue 数和 PASS/FAIL
   - `semantic_review_checker 命令`，分别记录 Python/JS 实现或说明只运行一个实现的原因
   - `semantic_review_checker 结果`，包含 exit code、issue 数和 PASS/FAIL
   - `人工复核结论`
   - `未覆盖风险`
3. 明确：如果工具未运行，不得把 Phase 1 自检标记为完成。
4. 明确：如果工具在当前项目类型上有已知误判，可以人工复核，但必须记录“工具原始 issue + 人工判定 + 后续框架改进建议”。
5. 在 `AI_ENTRY_POINT.md` 中补充 Path A 输出条件：提交用户审核前必须有 `_analysis` 三件套和 Phase 1 自检记录。
6. 在 `AI_ENTRY_POINT.md` 中新增 Phase 1 Review Gate 触发语义。示例触发语：
   - “审核 `dev_docs/_analysis`”
   - “判断 Phase 1 是否可以通过”
   - “是否可以进入正式文档生成”
   - “按 AICC 入口审核方案”
7. 在 Path A workflow 中新增“收到 Phase 1 审核请求后的响应流程”，明确 AI 必须先审核和必要修正 `_analysis` 文档，不得直接生成正式文档。
8. 在 Path A workflow 中新增“审核全文回写清单”，要求审核修改至少检查并必要更新：
   - `generation_plan.md` 的摘要、技术栈、子文档清单、证据表、待确认问题、AI 互审结果。
   - `project_analysis_report.md` 的问题统计、警告、疑问、建议、可继续生成判断。
   - `generation_progress.md` 的自检记录、状态变更、下一步动作、Phase 1 verdict。
9. 明确禁止“只更新 `generation_progress.md` 后宣布 PASS”的审核结果。
10. 明确 Phase 1 审核输出必须使用“建议通过/需修正”措辞，而不是在用户确认前写成“已通过并进入正式生成”。

### 7.2 模板改进：证据等级进入必填结构

目标文件：

- `templates/GENERATION_PLAN_TEMPLATE.md`
- `templates/generation_plan_trivial.md`
- `templates/generation_plan_simple.md`
- `templates/generation_plan_medium.md`
- `templates/generation_plan_complex.md`
- `templates/generation_plan_critical.md`
- `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`

改进内容：

1. 在所有 generation plan 模板中加入“关键事实表必须包含证据等级”的硬性验收项。
2. 在 project analysis report 模板中，将警告、疑问、建议统一扩展为：

```markdown
**证据等级**: E1/E2/E3/E4
**当前状态**: 已确认/待代码核查/待用户确认/风险假设
**证据位置**:
- `path:line`
**为什么需要用户确认**:
- [仅当状态为待用户确认时填写；必须说明代码为什么无法回答]
```

3. 将“待用户确认”列表改为准入制：
   - 技术栈、依赖、入口文件、路由、测试目录、部署配置等可由代码确认的事实，不得直接进入用户确认清单。
   - 用户确认项必须解释“为什么无法从代码或仓库文档判断”。

### 7.3 进度契约改进：自检记录成为 contract 字段

目标文件：

- `core/contracts/run_record_contract.yaml`
- `templates/PROGRESS_TEMPLATE.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`

改进内容：

1. 在 `generation_progress` contract 中新增 Phase 1 自检必需项：
   - `Phase 1 自检`
   - `doc_health_checker`
   - `semantic_review_checker`
   - `issue 数`
   - `人工复核结论`
2. `doc_health_checker` 新增一致性检查：
   - 若“Phase 1 自检”已勾选，但 checker 执行项未勾选或缺少结果，报 `phase1_self_check_record_missing`。
   - 若当前状态是“等待人工审核”，但 Phase 1 自检结果缺失，报 `phase1_gate_without_self_check`。
   - 若工具结果写 PASS，但 issue 数不是 0 且无人工复核说明，报 `checker_result_issue_count_mismatch`。
   - 若出现 `Phase 1 verdict = PASS`，但缺少证据等级、自检记录、issue 数或人工复核结论，报 `phase1_pass_without_required_review_evidence`。
   - 若 `generation_progress.md` 更新时间晚于 `generation_plan.md` / `project_analysis_report.md`，且写入 PASS 但两个主体文档没有复查记录或证据等级更新，报 `phase1_progress_only_review`.
3. 进度模板新增“Phase 1 自检记录”小节，统一写法：

```markdown
## Phase 1 自检记录

| 工具 | 命令 | 结果 | issue 数 | 人工复核结论 |
| --- | --- | --- | ---: | --- |
| doc_health_checker.py | `python3 ...` | PASS/FAIL/未运行 | 0 | [结论] |
| doc_health_checker.js | `node ...` | PASS/FAIL/未运行 | 0 | [结论] |
| semantic_review_checker.py | `python3 ...` | PASS/FAIL/未运行 | 0 | [结论] |
| semantic_review_checker.js | `node ...` | PASS/FAIL/未运行 | 0 | [结论] |
```
4. 增加 “Phase 1 Review Packet” 小节，记录：
   - `review_started_at`
   - `review_completed_at`
   - `review_trigger`
   - `machine_check_summary`
   - `manual_review_summary`
   - `blocker_count`
   - `warning_count`
   - `waived_issue_count`
   - `phase1_recommendation`

### 7.4 语义检查器改进：证据等级和项目定位触发器

目标文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

改进内容：

1. 新增 `evidence_level_completeness` 检查：
   - `generation_plan.md` 有“证据与验证记录”但缺少 `证据等级` 列时报 issue。
   - `project_analysis_report.md` 存在“警告/疑问/建议”但未标注证据等级时报 issue。
2. 新增 `confirmation_admission` 检查：
   - 用户确认项中出现“依赖管理工具、主前端版本、数据库技术、测试目录、部署 Compose 是否存在”等可由代码确认的事实时报 issue。
   - 如果确认项没有说明“代码无法回答的原因”，报 issue。
3. 新增 `project_positioning_coverage` 检查：
   - 如果仓库存在 `CONTRIBUTING.md`，但计划中没有贡献/开发环境/维护者规则相关文档或说明，报 issue。
   - 如果仓库存在 `manual/` 或用户手册目录，但计划中没有说明用户手册与 AI 开发文档边界，报 warning。
   - 如果 README 或源码含大量 attribution、dictionary、language、external API 线索，但字典/数据文档没有覆盖数据来源和授权边界，报 warning。
4. 新增 `review_writeback_completeness` 检查：
   - 如果 progress 声明 Phase 1 已复查/PASS，但 generation plan 的关键事实表仍缺证据等级，报 issue。
   - 如果 progress 声明 Phase 1 已复查/PASS，但 project analysis report 的警告/疑问/建议仍缺证据等级，报 issue。
   - 如果 progress 声明 Phase 1 已复查/PASS，但待确认问题中仍包含可由代码或仓库文档确认的事实，报 issue。
5. 新增维护者规则一致性检查：
   - 如果存在 `CONTRIBUTING.md` 且其中包含测试、PR、分支或开发环境规则，`testing_guide.md` 规划或分析报告必须引用这些规则或说明未采用原因。
6. 给 issue 增加统一字段：
   - `severity`: `blocker` / `error` / `warning` / `info`
   - `blocks_phase1`: `true` / `false`
   - `suggested_writeback_target`: `generation_plan.md` / `project_analysis_report.md` / `generation_progress.md`

### 7.5 项目扫描器改进：输出项目定位信号

目标文件：

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `tools/py/tests/test_project_scanner.py`
- `tools/js/project_scanner.test.js`

改进内容：

在 scanner JSON 输出中增加：

```json
{
  "project_positioning_signals": {
    "open_source": {
      "detected": true,
      "evidence": ["LICENSE", "CONTRIBUTING.md"]
    },
    "self_hosted": {
      "detected": true,
      "evidence": ["README.md", "docker-compose.yml"]
    },
    "user_manual": {
      "detected": true,
      "evidence": ["manual/"]
    },
    "external_data_or_api": {
      "detected": true,
      "evidence": ["README.md", "config/linguacafe.php"]
    }
  }
}
```

用途：

- 让 generation plan 自动把项目定位信号纳入子文档清单。
- 让 semantic checker 能判断“明明有贡献指南，却没有开发贡献文档”的缺口。
- 将 LinguaCafe 的开源、自托管、用户手册、外部数据/API 特征抽象为通用检测信号，而不是写死 LinguaCafe 项目名称或路径。

### 7.5A Checker 标准排除规则统一

目标文件：

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/tests/test_semantic_review_checker.py`
- `tools/js/semantic_review_checker.test.js`
- `tools/testdata/semantic_review/`

改进内容：

1. 抽象并复用同一套标准排除规则：
   - `AI-Coding-Context/`
   - `ai_coding_context/`
   - `.ai/`
   - `.git/`
   - `node_modules/`
   - `vendor/`
   - `tools/testdata/` 中非当前 fixture 的嵌套样例
2. 对 symlink 框架目录执行真实路径识别，避免 `AI-Coding-Context -> /Users/.../AI-Coding-Context` 被当作目标项目源码。
3. Python/JS semantic checker 对同一 LinguaCafe-like symlink fixture 必须返回一致 verdict。

### 7.5B 工具降级与性能边界

目标文件：

- `workflows/path_a_first_generation.md`
- `templates/PROGRESS_TEMPLATE.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`

改进内容：

1. 定义工具结果状态：
   - `PASS`
   - `FAIL`
   - `NOT_RUN`
   - `UNAVAILABLE`
   - `TIMEOUT`
   - `WAIVED_FALSE_POSITIVE`
2. 对 `UNAVAILABLE` / `TIMEOUT` 要求写明：
   - 原始命令
   - 失败原因
   - 替代检查
   - 残余风险
3. 对大项目增加扫描边界：
   - 默认排除标准目录和框架目录。
   - semantic checker 应优先扫描 `_analysis`、关键配置、项目定位信号和测试拓扑，不做无限制全文深扫。
   - 超时或跳过目录必须写入 progress 的未覆盖风险。

### 7.6 项目类型策略改进：新增定位触发规则

目标文件：

- `core/project_types/fullstack.md`
- `core/project_types/web_frontend.md`
- `core/project_types/containerized.md`
- `workflows/path_a_first_generation.md`

改进内容：

新增通用定位触发规则：

| 触发信号 | 必须考虑的文档或章节 | 说明 |
| --- | --- | --- |
| `CONTRIBUTING.md` | `development_contribution_guide.md` 或并入 `testing_guide.md`/`deployment_guide.md` | 记录 PR、分支、测试、开发环境规则 |
| `manual/` 或 user manual | `user_manual_boundary.md` 或主文档中的边界章节 | 区分用户手册和 AI 开发文档 |
| `docker-compose*.yml` + README 自托管描述 | `deployment_guide.md` 必须覆盖生产/开发 Compose、默认凭据、备份、升级 |
| 大量 dictionary/language/attribution/API 线索 | 数据/字典/外部 API 文档必须覆盖授权与来源边界 | 防止 AI 只看代码不看资源约束 |

特别说明：

- 当前 `core/project_types/fullstack.md` 更偏 Next.js/Nuxt/Remix/SvelteKit 等 SSR 全栈框架，不足以覆盖 Laravel + Vue 这类后端框架承载 SPA/API 的全栈应用。本轮实施应补充“传统后端框架 + SPA 前端”的识别与文档规划要求。
- 当前 `core/project_types/containerized.md` 已有 Docker/Compose 关注点，但缺少自托管产品的默认凭据、备份、升级、开发 Compose 与生产 Compose 边界要求，应在该文件或 Path A 通用规则中补强。

---

## 八、建议实施顺序

### Task 0：定义 Phase 1 Review Contract 和状态机

原因：

- 后续 checker、模板和 workflow 都依赖统一的 gate 状态与阻塞条件。先定义 contract，可避免各工具各自解释 PASS。

文件：

- `core/contracts/run_record_contract.yaml`
- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`

验收：

- fixture 中 `Phase 1 verdict = PASS` 但当前状态仍是 `等待人工审核` 且下一步写“进入正式文档生成”时，contract checker 或 doc health checker 必须报出状态组合问题。
- fixture 中 `建议通过` 与 `用户已确认` 状态边界清晰，未确认前不得进入正式生成。

### Task 1：修进度契约和自检记录

原因：

- LinguaCafe 最明显的问题是“写了 Phase 1 自检，但没有自检证据”。
- 这是 gate 可信度问题，应优先修复。

文件：

- `core/contracts/run_record_contract.yaml`
- `templates/PROGRESS_TEMPLATE.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- 对应 Python/JS 测试

验收：

- 构造一个 LinguaCafe-like fixture：`Phase 1 自检` 已勾选，但 checker 项未执行。
- Python/JS `doc_health_checker --full-check` 必须报 `phase1_self_check_record_missing`。
- 构造一个 progress-only fixture：`generation_progress.md` 写入 `Phase 1 verdict = PASS`，但 `generation_plan.md` 仍缺证据等级，必须报 `phase1_pass_without_required_review_evidence` 或 `phase1_progress_only_review`。
- 修正 fixture 后必须 PASS。

### Task 2：强制证据等级进入分析产物

原因：

- Dayflow 和 LinguaCafe 都证明“有证据来源”不等于“证据强度清楚”。

文件：

- generation plan 模板
- project analysis report 模板
- `semantic_review_checker`
- 对应测试 fixture

验收：

- `generation_plan.md` 有证据表但缺 `证据等级` 时，semantic checker 必须失败。
- `project_analysis_report.md` 中警告/疑问没有证据等级时，semantic checker 必须失败或 warning。

### Task 3：增加项目定位信号扫描

原因：

- LinguaCafe 的开源、自托管、用户手册、字典资源属性直接影响文档体系，不应只靠 AI 自由发挥。

文件：

- `project_scanner.py`
- `project_scanner.js`
- scanner 测试
- LinguaCafe-like testdata

验收：

- fixture 含 `CONTRIBUTING.md`、`LICENSE`、`manual/`、`docker-compose.yml`、README 自托管关键词时，scanner 输出对应 positioning signals。

### Task 4：把项目定位信号接入语义检查

原因：

- 只扫描信号还不够，必须能检查方案是否响应该信号。

文件：

- `semantic_review_checker.py`
- `semantic_review_checker.js`
- semantic review fixture

验收：

- fixture 有 `CONTRIBUTING.md`，但 generation plan 没有贡献/开发环境相关文档或章节时，报 `missing_project_positioning_doc`。
- fixture 有 `manual/`，但方案没有用户手册边界说明时，报 warning。
- fixture 的 `CONTRIBUTING.md` 写明不建议 PR 直接添加测试，而 analysis report 仍建议优先补测试且未说明维护者规则时，报维护者规则一致性 issue。

### Task 4A：统一 Python/JS checker 的 framework symlink 排除

原因：

- LinguaCafe 第二次复测中，Python semantic checker PASS，而 Node semantic checker 因扫描 `AI-Coding-Context` symlink 失败 11 个 issue。AICC 不能让同一份审核因工具实现不同而得出相反 verdict。

文件：

- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`
- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- 对应 Python/JS 测试和 LinguaCafe-like symlink fixture

验收：

- fixture 根目录包含 `AI-Coding-Context` symlink 时，Python/JS semantic checker 都不得把框架自身 tests、testdata、dogfood 文档计入目标项目。
- Python/JS 对该 fixture 的 `summary.passed` 和 issue 类型集合一致。

### Task 4B：补充工具降级、误报豁免和性能边界

原因：

- AICC 会运行在不同本地环境和不同规模项目中。工具不可用、超时、误报不能被静默忽略，也不能一律阻塞。

文件：

- `templates/PROGRESS_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `tools/py/doc_health_checker.py`
- `tools/js/doc_health_checker.js`
- `tools/py/semantic_review_checker.py`
- `tools/js/semantic_review_checker.js`

验收：

- fixture 中 Node checker 标记为 `UNAVAILABLE` 时，progress 必须记录替代检查和残余风险。
- fixture 中 checker issue 被标记为 `WAIVED_FALSE_POSITIVE` 时，必须记录原始 issue、豁免原因和后续框架改进项。
- semantic checker 对大型 fixture 不扫描标准排除目录，且能报告被跳过的高风险范围。

### Task 5：更新工作流和项目类型规则

原因：

- 工具能报错，但 AI 还需要在入口流程中知道为什么要做这些事。

文件：

- `AI_ENTRY_POINT.md`
- `workflows/path_a_first_generation.md`
- `workflows/generation_workflow.md`
- `core/project_types/fullstack.md`
- `core/project_types/web_frontend.md`
- `core/project_types/containerized.md`

验收：

- Path A 明确要求在人工审核前记录自检结果。
- 项目类型规则明确列出定位触发器和对应文档规划要求。
- `AI_ENTRY_POINT.md` 明确 Path A 人工审核前必须完成 Phase 1 自检记录。

### Task 6：补充框架契约自检与入口一致性验证

原因：

- 本轮改动会同时触及入口文档、工作流、模板、契约和检查器。需要避免“模板要求”和“入口指令”再次漂移。

文件：

- `tools/py/framework_contract_checker.py`
- `tools/js/framework_contract_checker.js`
- 对应 Python/JS 测试或现有 self-check fixture

验收：

- self-check 能确认 `AI_ENTRY_POINT.md`、Path A 工作流和 `PROGRESS_TEMPLATE.md` 都提到 Phase 1 自检记录。
- self-check 能确认 run record contract 的必填项与 progress 模板字段一致。

---

## 九、验证计划

实施后至少运行：

```bash
python3 -m unittest discover tools/py/tests
for f in tools/js/*.test.js; do node "$f" || exit 1; done
python3 tools/py/framework_contract_checker.py --self-check
node tools/js/framework_contract_checker.js --self-check
python3 tools/py/doc_health_checker.py --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs
node tools/js/doc_health_checker.js --full-check --doc-dir tools/testdata/semantic_review/combined_case/dev_docs
```

新增 LinguaCafe-like fixture 后，还应运行：

```bash
python3 tools/py/semantic_review_checker.py --full-check --doc-dir tools/testdata/semantic_review/linguacafe_like_case/dev_docs --repo-root tools/testdata/semantic_review/linguacafe_like_case
node tools/js/semantic_review_checker.js --full-check --doc-dir tools/testdata/semantic_review/linguacafe_like_case/dev_docs --repo-root tools/testdata/semantic_review/linguacafe_like_case
```

负向 fixture 应覆盖：

- Phase 1 自检已勾选但 checker 结果未记录。
- 当前状态/下一步动作非法组合，例如未获用户确认却写“进入正式文档生成”。
- 关键事实表缺少证据等级。
- 用户确认项包含可由代码确认的事实。
- 有 `CONTRIBUTING.md` 但无贡献/开发环境文档规划。
- 有 `manual/` 但无用户手册边界说明。
- 只更新 `generation_progress.md` 并写入 Phase 1 PASS，但主体分析文档未回写。
- `AI-Coding-Context` symlink 污染 semantic checker 扫描范围。
- Node/Python 工具不可用、超时或误报豁免但缺少残余风险记录。

人工复核还应覆盖：

- `AI_ENTRY_POINT.md`、Path A 工作流、progress 模板中 Phase 1 自检 gate 的定义是否一致。
- `core/project_types/fullstack.md` 是否覆盖 Laravel + Vue 这类传统全栈结构，而不是只覆盖 SSR 元框架。
- `core/project_types/containerized.md` 是否覆盖自托管产品常见的默认凭据、备份、升级和开发/生产 Compose 边界。
- Python/JS checker 在同一 testdata 上的 verdict 是否一致。

---

## 十、风险与边界

### 10.1 不应把 Phase 1 变成完整代码审计

Phase 1 的目标仍是“方案可审核”，不是完整理解项目所有业务代码。新规则应防止错误结论和遗漏关键文档面，而不是要求 AI 在方案阶段完成所有正式文档分析。

### 10.2 检查器不应过度绑定 LinguaCafe

项目定位信号应是通用规则，LinguaCafe 只作为 fixture 和触发样例。规则应适用于其他开源、自托管、资源密集、用户手册型项目。

### 10.3 Warning 与 Error 要区分

- 自检证据缺失、证据等级缺失、确认项准入错误：应作为 error 阻塞进入人工审核。
- 用户手册边界、授权数据文档缺失：可先作为 warning，但必须在方案中记录处理方式。

### 10.4 不要求所有项目都新增更多文档

框架应允许合并文档。例如 `development_contribution_guide.md` 可以独立存在，也可以作为 `testing_guide.md` 和 `deployment_guide.md` 的章节；检查器只要求方案解释覆盖方式，不强制固定文件名。

### 10.5 不应让状态机过度复杂

Phase 1 状态机只服务于首次生成方案审核，不应扩展成完整项目管理系统。状态数量应保持少量、明确、可检查；复杂任务管理仍应留给 `dev_docs/plans/` 或后续正式文档体系。

### 10.6 不应要求双工具都必须成功才能工作

Python/JS checker 结果应尽量一致，但真实环境可能只安装其中一套运行时。框架应要求“可用工具必须运行，缺失工具必须记录”，而不是强制所有环境都具备 Node 和 Python。

---

## 十一、建议结论

LinguaCafe 复测说明 Dayflow 后的 AICC 改进方向是有效的，但还没有把 Phase 1 gate 做成真正可审计的闭环。

下一轮 AICC 完善应聚焦三件事：

1. **自检证据落盘**：任何“已自检”必须有命令、结果、issue 数和人工判定。
2. **证据等级强制**：关键事实、警告、疑问和建议都要能区分 E1/E2/E3/E4。
3. **项目定位驱动文档规划**：开源、自托管、用户手册、外部数据/API 等信号必须影响子文档清单。

审核通过后，建议按 Task 0 到 Task 6 顺序实施，先定义 Phase 1 Review Contract 和状态机，再修 gate 可信度，随后扩展语义检查、项目定位能力、工具一致性和降级策略，最后用框架契约自检防止入口、模板和检查器口径漂移。
