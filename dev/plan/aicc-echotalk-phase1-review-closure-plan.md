---
title: AICC EchoTalk Phase 1 复查闭环优化方案
summary: 记录 EchoTalk 第二轮 Phase 1 方案复查后仍暴露的 summary 严格校验漏跑、进度状态自相矛盾、代码事实漂移和项目愿景校准不足问题，并提出 AICC 复查闭环的下一轮优化方案。
keywords: aicc | echotalk | phase1-review | summary-validator | progress-consistency | evidence-model | project-vision
scope: AI-Coding-Context 路径 A Phase 1 方案复查阶段、_analysis 三件套回写、机器检查门禁、代码事实一致性和项目定位校准机制
related_files: AI_ENTRY_POINT.md | workflows/path_a_first_generation.md | workflows/generation_workflow.md | templates/GENERATION_PLAN_TEMPLATE.md | templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md | templates/PROGRESS_TEMPLATE.md | tools/py/summary_validator.py | tools/py/doc_health_checker.py | tools/py/semantic_review_checker.py | tools/js/doc_health_checker.js | tools/js/semantic_review_checker.js | core/contracts/run_record_contract.yaml
dependencies: dev/plan/aicc-generation-plan-review-process-gap-plan.md | dev/plan/aicc-phase1-review-gate-followup-plan.md | dev/plan/aicc-first-release-acceptance-gate-improvement-plan.md | dev/plan/aicc-memex-first-run-regression-plan.md
verified_at: 2026-05-19
---

# AICC EchoTalk Phase 1 复查闭环优化方案

## 1. 背景

EchoTalk 是本轮 AICC 的新测试项目，路径为：

- 示例项目根目录：`/Users/zibuyu/code/openSource/EchoTalk`
- AICC 运行产物：`/Users/zibuyu/code/openSource/EchoTalk/dev_docs/_analysis`
- AICC 框架目录：`/Users/zibuyu/code/zibuyu/AI-Coding-Context`

用户在 EchoTalk 第一次运行后，使用更贴近真实使用场景的自然指令触发复查：

```text
请根据 AI-Coding-Context/AI_ENTRY_POINT.md，对生成方案进行复查和优化
```

这条指令没有逐项列出检查器、字段、证据等级、进度回写等细节，符合 AICC 需要支持的目标场景：用户只携带入口文档和一个简短意图，AI 应能根据框架规范完成方案复查、修正 `_analysis` 文档、给出是否建议通过 Phase 1 的可信结论。

第二轮结果显示：AICC 近期针对 Memex、LinguaCafe 暴露的问题已经产生效果，AI 能主动停留在 Phase 1 审核阶段，没有直接生成正式文档；也能运行并回写 `doc_health_checker`、`semantic_review_checker` 的结果。但这次测试继续暴露出一个更深层的问题：**复查流程已经被触发，却还没有形成“最终结论必须由完整检查矩阵和代码事实模型反推”的闭环**。

## 2. 本次复核结论

### 2.1 总体判断

EchoTalk 第二轮 Phase 1 复查结果应判定为：

| 维度 | 结论 | 说明 |
| --- | --- | --- |
| Phase 1 停门 | 通过 | 正式文档尚未生成，`generation_progress.md` 明确记录正式生成未授权。 |
| 方案复查触发 | 部分通过 | AI 已对 `_analysis` 三件套进行复查和回写。 |
| doc health 检查 | 通过 | Python/JS `doc_health_checker` 当前均可通过。 |
| semantic review 检查 | 通过 | Python/JS `semantic_review_checker` 当前均可通过。 |
| summary 严格校验 | 不通过 | `summary_validator --strict` 对 3 个 `_analysis` 文档全部判定 invalid。 |
| 进度记录一致性 | 不通过 | `checker_status_matrix` 仍写 `NOT_RUN`，后文 `machine_checks` 又写 PASS。 |
| 代码事实一致性 | 不通过 | 文件数、依赖数、服务数、`app.ts` 行数、AI API 集成边界仍有多处漂移。 |
| 项目定位校准 | 不通过 | EchoTalk 的 privacy-first/offline PWA、Android TWA、可选在线音频分析没有被充分纳入方案。 |
| 是否建议进入正式文档生成 | 不建议 | 需要继续修正 `_analysis` 三件套并复跑完整检查矩阵。 |

### 2.2 复核命令与结果

继续复跑现有结构和语义检查：

| 工具 | 当前结果 | 关键观察 |
| --- | --- | --- |
| Python `doc_health_checker --full-check` | PASS，0 issue | `frontmatter.checked=0`，说明它没有覆盖 `_analysis` frontmatter 严格契约。 |
| JS `doc_health_checker --full-check` | PASS，0 issue | 与 Python 结果一致，同样没有拦截 summary/frontmatter invalid。 |
| Python `semantic_review_checker --full-check` | PASS，0 issue | 当前规则未覆盖 EchoTalk 的外部音频分析 API 与隐私定位冲突。 |
| JS `semantic_review_checker --full-check` | PASS，0 issue | 与 Python 结果一致，未发现量化事实残留和 AI 边界误判。 |

这说明本轮问题不是“某一个已运行 checker 失败后被忽略”，而是 **Phase 1 复查矩阵本身缺少必需门禁，并且现有 checker 的覆盖范围不足**。

在 AICC 仓库中复跑：

```bash
python3 tools/py/summary_validator.py --dir /Users/zibuyu/code/openSource/EchoTalk/dev_docs/_analysis --recursive --strict
```

结果：

| 指标 | 值 |
| --- | ---: |
| total_files | 3 |
| processed | 3 |
| valid | 0 |
| invalid | 3 |
| total_warnings | 13 |

三个文件均缺少 `title`、`keywords`、`scope` 等必填字段，并存在 `related_files` / `dependencies` 被错误解析的问题。这说明 `_analysis` 文档仍使用了不符合 AICC 当前规范的嵌套 frontmatter 或引号格式。

继续复跑项目扫描：

```bash
python3 tools/py/project_scanner.py /Users/zibuyu/code/openSource/EchoTalk --exclude-standard --mode summary --format json
```

当前返回：

| 指标 | 值 |
| --- | ---: |
| total_files | 68 |
| total_dirs | 22 |
| max_depth | 3 |
| complexity_level | basic |

代码事实复核还显示：

| 事实 | 当前仓库证据 | 文档残留问题 |
| --- | --- | --- |
| 依赖数量 | `package.json` 为 3 个 dependencies、11 个 devDependencies | 文档仍写 8 个开发依赖。 |
| 主入口体量 | `wc -l src/app.ts` 为 780 行，文件约 33KB | 文档仍写 900+ 行或超过 800 行。 |
| 服务文件数量 | `src/services/*.ts` 为 7 个文件 | 文档多处仍写 6 个服务类。 |
| 测试拓扑 | `src/tests` 下 17 个 `.test.ts` + `setup.ts` | 只在部分证据表修正，前文摘要未同步。 |
| 在线 AI 接口 | `ai.service.ts` 使用 `spellApiKey` 并调用 `GetAccuracyFromRecordedAudio` | 文档仍写未集成任何 AI API、当前为手动复制模式。 |
| 项目定位 | README 写明 privacy-first、offline PWA、Android TWA | 方案没有把隐私、离线、TWA 和音频上传边界作为正式文档重点。 |

### 2.3 第二轮运行的正向信号

本次测试不是简单失败，它验证了近期 AICC 优化已经覆盖了一部分风险：

1. AI 没有绕过 Phase 1 直接生成正式文档。
2. `generation_progress.md` 仍记录“正式生成授权：未授权”。
3. AI 能主动复查三件套，并回写部分问题。
4. `doc_health_checker` 和 `semantic_review_checker` 的 Python/JS 双实现结果已经能进入复查记录。
5. 测试数量漂移、模板标题和 machine checks 数字字段等上一轮常见问题已有修复迹象。

但是，AICC 的目标不是“让 AI 做一次复查动作”，而是让 AI 在自然指令下稳定得出可信结论。因此，本轮暴露的问题需要作为复查闭环的下一层优化。

## 3. 暴露的问题

### 3.1 P0：Phase 1 复查没有强制纳入 `summary_validator --strict`

#### 现象

AI 的复查总结宣称检查器均通过，但实际复跑：

- `generation_plan.md` invalid。
- `project_analysis_report.md` invalid。
- `generation_progress.md` invalid。

主要错误是缺少必填 frontmatter 字段：`title`、`keywords`、`scope`。这意味着 AICC 最基础的文档元数据契约没有通过。

#### 为什么这是框架问题

`summary_validator` 在 AICC 中承担的是元数据和文档入口可索引性的基础契约。Phase 1 复查如果只运行 `doc_health_checker` 和 `semantic_review_checker`，就会出现“结构/语义检查通过，但文档元数据契约失败”的断层。

更关键的是，`generation_progress.md` 中已经有 `summary_validator 已执行` 的检查项，但复查记录没有真实回写该工具的 exit code、issue_count 和状态；`checker_status_matrix` 还将 metadata / `summary_validator` 标记为 `required=no`。这说明模板有提示，但没有形成门禁。

#### 风险

- `_analysis` 文档无法作为规范 AICC 文档被后续工具稳定索引。
- 后续正式文档生成可能继承错误 frontmatter。
- AI 会误把不完整检查矩阵表述为“所有检查通过”。

#### 优化方向

1. Path A Phase 1 复查阶段必须把 `summary_validator --strict` 列为必需检查。
2. `generation_progress.md` 的 `machine_checks` 必须包含 `summary_validator`，不得只包含 doc health 和 semantic review。
3. 任一 `_analysis` 文档 summary invalid 时，Phase 1 最终状态只能是“需修正”，不得写“建议通过”。
4. `doc_health_checker` 或 `semantic_review_checker` 应增加交叉检查：如果 `generation_progress.md` 声明 `summary_validator 已执行`，但没有结构化结果，应报 blocker。
5. `doc_health_checker` 若在 `dev_docs/_analysis` 中检测到 frontmatter 但 `frontmatter.checked=0`，应明确报告覆盖缺口，避免用户误以为结构检查已经包含 metadata 契约。

### 3.2 P0：复查结果无法反推最终状态，进度记录自相矛盾

#### 现象

`generation_progress.md` 同时存在两套互相冲突的状态：

- `checker_status_matrix` 中 `summary_validator`、Python/JS `doc_health_checker`、Python/JS `semantic_review_checker`、`health_check_report` 均为 `NOT_RUN`。
- metadata / `summary_validator` 在矩阵中被标为 `required=no`，与 Phase 1 复查所需的元数据门禁不匹配。
- 后文 `machine_checks` 又写 Python/JS `doc_health_checker` 和 `semantic_review_checker` 均为 `PASS`。
- `verified_at` 和“最后更新”仍为 `2026-05-18`，但复查记录时间为 `2026-05-19`。

#### 为什么这是框架问题

当前 AICC 允许同一份进度文档中存在多个状态源：

- 顶部当前状态。
- 阶段进度。
- 验收进度 checklist。
- checker status matrix。
- machine checks。
- 人工复查记录。
- 文末最后更新时间。

这些字段没有被定义为单一状态机，也没有工具验证它们之间的派生关系。AI 可以修复一个表格，却遗漏另一个表格。

#### 风险

- 用户和后续 AI 无法判断 Phase 1 到底是否完成复查。
- 恢复运行时可能根据 `NOT_RUN` 重新执行，也可能根据 PASS 继续推进。
- 进度记录失去审计价值。

#### 优化方向

1. 在 `run_record_contract.yaml` 中定义 Phase 1 复查状态机和派生规则。
2. 将 `machine_checks` 作为唯一机器检查事实源，`checker_status_matrix` 只能从它派生或废弃。
3. `verified_at`、文首“最后更新”、文末“最后更新”必须一致，并等于最近一次复查回写日期。
4. 新增检查规则：同一工具在同一文档中不得同时出现 `NOT_RUN` 和 `PASS`。
5. 新增检查规则：Phase 1 review 中 metadata / `summary_validator` 必须为 `required=yes`。
6. 新增检查规则：若正式生成未授权，则 Phase 1 可为“等待人工审核”或“需修正”，但不得把首版验收项混入已完成状态。

### 3.3 P0：代码事实漂移没有被完整追踪和同步回写

#### 现象

EchoTalk 的 `_analysis` 文档中仍存在多处事实漂移：

- 文件数仍写 65，而当前 scanner 返回 68。
- 开发依赖仍写 8，而 `package.json` 中 devDependencies 为 11。
- 服务层仍写 6 个服务类，而 `src/services/*.ts` 为 7 个文件。
- `src/app.ts` 仍写 900+ 行或超过 800 行，而当前 `wc -l` 为 780。
- 测试数量只在后部证据表修正，摘要、规模评估和前文仍未同步。

#### 为什么这是框架问题

Phase 1 方案复查不是只修复单个命中的 issue，而是要确保所有引用同一事实的段落同步更新。当前工具能发现部分 metric drift，但无法建立“事实项 -> 所有引用位置”的映射，也没有要求 AI 在修正一个事实后全文搜索同义表达。

#### 风险

- 正式文档计划将基于错误规模评估分配文档批次。
- “服务层 6 个类”和“7 个服务文件”会导致架构文档漏写 `prompts.service.ts` 或其他边界。
- 依赖数量错误会影响构建、测试、平台文档准确性。

#### 优化方向

1. Phase 1 复查必须生成 `evidence_inventory`，记录每个量化事实的来源命令、当前值和引用位置。
2. 修改任一量化事实后，AI 必须全文搜索旧值和同义表述。
3. `semantic_review_checker` 增加同文档 metric consistency 检查：
   - 文件总数。
   - 测试文件数。
   - 依赖数量。
   - 主要目录文件数。
   - 大文件行数。
4. 对“6 个服务实例”和“7 个服务文件”这类口径差异，要求文档显式区分：
   - app 注入的运行时服务实例数。
   - `src/services/` 下的服务文件数。
   - 是否包含纯 prompt/helper 服务。

### 3.4 P0：AI 能力和隐私边界判断错误

#### 现象

文档仍将 EchoTalk 的 AI 功能描述为“未集成任何 AI API 调用”“当前为手动复制模式”。但代码显示：

- `src/services/ai.service.ts` 从 URL 或 `localStorage` 读取 `spellApiKey`。
- `spellApiKey` 会写入 `localStorage`。
- 代码调用 `https://alisol.ir/Projects/GetAccuracyFromRecordedAudio/` 检查 API key。
- 代码将录音 `FormData` POST 到同一外部 endpoint 做准确度分析。
- README 同时说明支持 offline prompts。

正确边界应为：

1. 手动 Prompt 模式：生成 ChatGPT/Gemini 等外部 AI 可用的 prompt，用户手动复制。
2. 在线发音/准确度分析模式：可选 API key，调用外部 endpoint，并上传录音数据。
3. 离线优先模式：PWA 首次加载后可离线使用，录音默认保存在设备本地。

#### 为什么这是框架问题

AICC 当前容易把“是否调用 OpenAI/Gemini API”误判为“是否存在直接 AI API 调用”。EchoTalk 使用的是项目自有或第三方发音分析 endpoint，不属于常见 LLM Provider，但仍然是外部 AI/音频分析服务，且涉及隐私边界。

#### 风险

- 正式文档会错误宣传为完全本地/无外部上传。
- 隐私、安全、数据流和用户配置文档会漏掉 API key 与录音上传。
- 后续 AI 修改代码时可能破坏用户授权、离线模式或隐私预期。

#### 优化方向

1. AICC 增加“外部智能服务/外部数据处理 endpoint”识别，不局限于 OpenAI、Gemini、Claude 等 Provider 名称。
2. `semantic_review_checker` 增加扫描维度：
   - `fetch(` / `XMLHttpRequest` / SDK client。
   - `FormData` 上传。
   - `localStorage` / IndexedDB 中的 key/token/API key。
   - README 中 privacy/offline 叙述与代码中外部请求的关系。
3. `generation_plan.md` 模板新增“AI/外部服务边界”强制章节：
   - 本地 AI / 手动 Prompt。
   - 直接外部 API。
   - 上传的数据类型。
   - API key 存储位置。
   - 用户授权或配置入口。
   - 与项目隐私愿景的关系。
4. 对 privacy-first/offline 项目，任何外部上传都必须提升为 P0/P1 事实并进入正式文档计划。

### 3.5 P1：项目定位和愿景没有进入方案验收条件

#### 现象

README 明确描述 EchoTalk 是：

- privacy-first。
- offline language training tool。
- Progressive Web App。
- no server。
- recordings securely on device。
- Android Application (TWA)。
- 支持 AI pronunciation analysis，offline prompts supported。

但 Phase 1 方案主要从代码目录、服务层、测试和构建角度组织正式文档，未把这些定位转化成验收要求。

#### 为什么这是框架问题

AICC 的文档体系不是普通代码索引，而是“后续 AI 编码上下文”。项目愿景决定哪些事实是不可破坏的边界。对于 EchoTalk，隐私、离线、本地录音、PWA/TWA、可选在线分析是核心产品约束，不是 README 装饰语。

#### 风险

- 后续 AI 可能为了简化实现引入后端依赖，违背 no server 定位。
- 可能把可选在线分析写成核心必需能力，破坏离线优先。
- 可能忽略 Android TWA 发布路径，导致平台文档不完整。

#### 优化方向

1. Phase 1 方案复查必须有“项目定位与不可破坏约束”检查。
2. 从 README、manifest、PWA 配置、Docker/服务端缺失等证据中提取愿景级约束。
3. 正式文档计划必须将愿景级约束落入具体文档：
   - `architecture/overview.md`：offline-first/no-server 架构。
   - `architecture/data_storage.md`：IndexedDB/localStorage/录音数据。
   - `architecture/external_services.md` 或相关章节：可选外部发音分析。
   - `platform/pwa_twa_release.md`：PWA 和 Android TWA。
   - `rules/combined/AI_RULES.md`：不得默认引入后端、不得绕过用户授权上传录音。
4. `semantic_review_checker` 应检测 README 中出现的高权重定位词是否在 `generation_plan.md` 中有对应文档安排。

### 3.6 P1：复查总结缺少“阻断条件优先”的结论模板

#### 现象

AI 的复查总结强调已修复的问题和 PASS 的 checker，但没有因为 `summary_validator` 失败、进度矛盾、AI API 事实错误而明确判定“不可通过”。

#### 为什么这是框架问题

当前 AICC 允许复查总结以“完成了哪些修复”为中心，而不是以“是否满足通过门槛”为中心。对于审核流程，输出格式应先给 verdict，再列证据。

#### 风险

- 用户需要自己从长报告中判断是否可通过。
- AI 容易把局部修复包装成整体通过。

#### 优化方向

1. Phase 1 复查输出模板必须先给 `verdict`：
   - `BLOCKED_NEEDS_FIX`
   - `READY_FOR_USER_REVIEW`
   - `APPROVED_TO_GENERATE_FORMAL_DOCS` 仅在用户明确确认后出现。
2. verdict 必须由 hard gates 计算：
   - summary strict pass。
   - doc health pass。
   - semantic review pass。
   - progress consistency pass。
   - unresolved P0 fact conflicts = 0。
   - formal generation authorization state correct。
3. 如果任一 hard gate 失败，复查总结必须第一屏说明“不建议进入正式文档生成”。

## 4. 根因分析

### 4.1 检查器分层没有统一进入 Phase 1 复查矩阵

AICC 目前已经有多个工具，但不同阶段对工具的使用不一致：

- 首次生成可能只运行 `summary_validator`。
- Phase 1 复查可能只运行 doc health 和 semantic review。
- 首版验收又需要 health report。

这种分层本身合理，但缺少“当前阶段最小必需检查集”。EchoTalk 证明：只要 `summary_validator` 不在 Phase 1 hard gate 中，AI 就可能漏跑。

### 4.2 运行记录是自然语言文档，不是状态契约的投影

`generation_progress.md` 同时承担进度展示、恢复上下文、验收 checklist、检查器记录和人工复查摘要。它需要结构化契约，否则很容易出现一个区域更新、另一个区域遗漏。

### 4.3 事实模型是局部 grep，不是全局证据图

AI 能修正某个被工具指出的 test count，但不能自动保证所有引用同一事实的位置一致。AICC 需要把量化事实当作实体管理，而不是把每个段落当作孤立文本。

### 4.4 项目愿景还没有成为验收输入

目前 AICC 更擅长识别技术栈、目录结构和测试拓扑，但对 README 中的定位词、用户承诺、隐私声明、平台目标还没有形成同等强度的检查。这会导致“代码事实正确但产品边界错误”的文档。

### 4.5 外部服务识别过于 Provider 中心

EchoTalk 不是典型“集成 OpenAI SDK”的项目，而是通过自定义 endpoint 做音频分析。AICC 如果只按 LLM Provider 识别 AI 集成，就会漏掉真实隐私和数据流风险。

## 5. 优化目标

### 5.1 总目标

将 AICC Phase 1 方案复查从“执行若干检查并修正明显问题”升级为“完整检查矩阵、状态契约、证据图和项目愿景共同驱动的可审计通过判定”。

### 5.2 具体目标

1. Phase 1 复查必须包含 `summary_validator --strict`、Python/JS `doc_health_checker`、Python/JS `semantic_review_checker`。
2. 任何必需检查失败时，不得建议进入正式文档生成。
3. `generation_progress.md` 的状态、矩阵、机器检查表和更新时间必须一致。
4. 量化事实必须有唯一事实源和引用同步机制。
5. AI/外部服务边界必须以数据流和隐私影响为中心识别，而不是只识别常见 Provider。
6. README 中的项目定位、愿景和用户承诺必须进入正式文档计划和验收条件。
7. 复查输出必须先给 verdict，且 verdict 可由结构化数据反推。

## 6. 目标状态设计

### 6.1 Phase 1 复查 hard gates

建议将 Phase 1 复查的必需 gate 定义为：

| gate | 必需输入 | 通过条件 | 失败处置 |
| --- | --- | --- | --- |
| metadata_contract | `_analysis/*.md` | `summary_validator --strict` valid = total | 回写 frontmatter 并复跑。 |
| structure_contract | `dev_docs/_analysis` | Python/JS `doc_health_checker` 均 PASS | 修正文档结构或模板残留。 |
| semantic_contract | `dev_docs/_analysis` + repo root | Python/JS `semantic_review_checker` 均 PASS | 修正事实冲突、测试拓扑、审核门状态。 |
| progress_contract | `generation_progress.md` | 状态、matrix、machine_checks、时间一致 | 回写唯一状态源。 |
| evidence_contract | `generation_plan.md` + `project_analysis_report.md` | P0/P1 事实均有证据等级、命令或文件路径 | 补证据或降级为待确认。 |
| vision_contract | README/manifest/config + plan | 项目定位和不可破坏约束进入文档计划 | 补充正式文档规划。 |
| authorization_contract | `generation_progress.md` | 未获用户确认时正式文档未生成 | 继续等待人工审核。 |

### 6.2 `machine_checks` 标准表

`generation_progress.md` 中 Phase 1 复查必须包含：

```markdown
## machine_checks

| phase | tool | implementation | command | exit_code | issue_count | status | required | disposition |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| phase1_review | summary_validator | python | `python3 AI-Coding-Context/tools/py/summary_validator.py --dir dev_docs/_analysis --recursive --strict` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | python | `python3 AI-Coding-Context/tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | js | `node AI-Coding-Context/tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | python | `python3 AI-Coding-Context/tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | js | `node AI-Coding-Context/tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |
```

约束：

- `required=yes` 且 `status != PASS` 时，Phase 1 verdict 必须为 `BLOCKED_NEEDS_FIX`。
- `issue_count` 必须为数字。
- `exit_code` 必须为数字。
- 同一工具不得在其他表格中出现冲突状态。

### 6.3 Phase 1 verdict 计算

建议在 `generation_progress.md` 中新增：

```markdown
## phase1_review_verdict

| field | value |
| --- | --- |
| verdict | BLOCKED_NEEDS_FIX |
| reason | summary_validator failed for 3 _analysis files |
| can_generate_formal_docs | no |
| user_confirmation_required | yes |
| next_action | 修复 _analysis frontmatter、进度状态一致性和 AI 外部服务事实后复跑完整检查矩阵 |
```

允许值：

| verdict | 含义 |
| --- | --- |
| `BLOCKED_NEEDS_FIX` | 存在 hard gate 失败或 P0 事实冲突。 |
| `READY_FOR_USER_REVIEW` | 所有 gate 通过，等待用户审核方案。 |
| `USER_APPROVED_FORMAL_GENERATION` | 用户明确回复方案通过后才可记录。 |

禁止 AI 在没有用户确认时写 `USER_APPROVED_FORMAL_GENERATION`。

### 6.4 证据图和事实同步

建议 Phase 1 复查时生成或内嵌 `evidence_inventory`：

```markdown
## evidence_inventory

| fact_id | fact | current_value | evidence_command_or_file | referenced_in | stale_values_found | status |
| --- | --- | --- | --- | --- | --- | --- |
| project.total_files | 项目文件数 | 68 | `project_scanner ... --format json` | generation_plan:core_points, generation_plan:scale_table, project_analysis_report:summary | 65 | needs_update |
| deps.dev_count | devDependencies 数量 | 11 | `package.json` | generation_plan:dependency_section | 8 | needs_update |
| app.entry_lines | `src/app.ts` 行数 | 780 | `wc -l src/app.ts` | generation_plan:complexity, report:architecture | 900+, 超过800 | needs_update |
```

此表可以先作为模板要求，不一定第一轮就工具化。但后续应逐步由 `semantic_review_checker` 自动抽取和验证。

### 6.5 项目愿景校准表

建议 `generation_plan.md` 必须包含：

```markdown
## project_positioning_constraints

| constraint | evidence | documentation_impact | ai_rules_impact | status |
| --- | --- | --- | --- | --- |
| privacy-first | README line ... | 数据流、隐私边界、录音存储必须独立说明 | 不得默认上传录音或引入后端 | confirmed |
| offline PWA | README + manifest/vite config | 平台文档需覆盖 PWA 缓存和离线限制 | 修改功能时不得破坏离线核心路径 | confirmed |
| no server | README | 架构文档不能写后端服务依赖 | 不得新增服务端作为默认架构 | confirmed |
| optional online pronunciation analysis | `ai.service.ts` fetch + FormData | 需说明外部 endpoint、API key、音频上传 | 上传前需保持用户授权/配置边界 | confirmed |
| Android TWA | README | 平台文档需覆盖 TWA/APK 分发 | 平台改动需考虑 Android 浏览器 | confirmed |
```

### 6.6 外部服务和隐私边界识别

建议 AICC 将“AI Provider”扩展为“AI/外部智能服务边界”：

| 识别项 | 示例 | 文档要求 |
| --- | --- | --- |
| LLM Provider | OpenAI、Gemini、Claude SDK/API | Provider、模型、密钥、数据发送边界。 |
| 自定义智能服务 endpoint | `GetAccuracyFromRecordedAudio` | endpoint 作用、上传数据、API key、失败降级。 |
| 手动 Prompt 模式 | 用户复制 prompt 到 ChatGPT/Gemini | 说明不由应用直接调用 Provider。 |
| 本地推理/本地算法 | WebAudio、相似度算法、本地 tokenizer | 说明数据不离开设备。 |
| 混合模式 | 离线核心 + 可选在线分析 | 明确默认路径和可选路径。 |

## 7. 实施方案

### 7.1 文档规范修改

修改 `workflows/path_a_first_generation.md`：

1. 在 Phase 1 复查步骤中加入必需检查矩阵。
2. 明确 `summary_validator --strict` 是 Phase 1 hard gate。
3. 明确任一 required checker 失败时只能继续修正，不能建议通过。
4. 明确自然指令“对生成方案进行复查和优化”应触发完整 Phase 1 复查流程。

修改 `AI_ENTRY_POINT.md`：

1. 在路径 A 路由中补充“方案复查/优化”意图识别。
2. 明确复查不是重新生成正式文档。
3. 明确复查输出必须先给 verdict。
4. 明确项目愿景和隐私边界属于 Phase 1 必查内容。

修改 `templates/PROGRESS_TEMPLATE.md`：

1. 统一 `machine_checks` 标准表。
2. 新增 `phase1_review_verdict`。
3. 删除或弱化容易与 `machine_checks` 冲突的 `checker_status_matrix`，或声明其必须由 `machine_checks` 派生。
4. 统一 `verified_at` 和最后更新时间规则。

修改 `templates/GENERATION_PLAN_TEMPLATE.md`：

1. 新增 `evidence_inventory`。
2. 新增 `project_positioning_constraints`。
3. 新增 `ai_external_service_boundaries`。
4. 增加“事实修正后全文同步”检查项。

修改 `templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md`：

1. 增加项目愿景与当前代码实现的对照章节。
2. 增加外部请求、API key、上传数据类型的代码证据表。
3. 要求“待用户确认”只用于代码无法回答的策略问题，不得用于可由代码确认的事实。

### 7.2 契约和检查器修改

修改 `core/contracts/run_record_contract.yaml`：

1. 增加 Phase 1 review required tools：
   - `summary_validator`
   - `doc_health_checker.py`
   - `doc_health_checker.js`
   - `semantic_review_checker.py`
   - `semantic_review_checker.js`
2. 增加 verdict allowed values。
3. 增加 machine check 字段类型约束。
4. 增加状态一致性约束。

修改 Python/JS `doc_health_checker`：

1. 检查 `_analysis` 阶段是否存在 `summary_validator` 结构化记录。
2. 检查 `checker_status_matrix` 与 `machine_checks` 冲突。
3. 检查 `verified_at` 和“最后更新”日期不一致。
4. 检查 `phase1_review_verdict` 是否存在且与 machine checks 一致。
5. 检查正式生成未授权时没有正式文档产物。
6. 检查 `_analysis` 文档存在 frontmatter 时，frontmatter 覆盖统计不得为 0；否则报告 `frontmatter_check_not_applied`。

修改 Python/JS `semantic_review_checker`：

1. 增加量化事实一致性规则。
2. 增加外部 endpoint / API key / 上传数据识别。
3. 增加 README 定位词与 generation plan 文档安排的覆盖检查。
4. 增加“手动 Prompt 模式”和“直接外部 API 调用”混淆检测。
5. 增加 app/service/test/dependency 等常见事实的跨段落一致性检测。

### 7.3 测试补充

新增测试 fixture：

1. `phase1_summary_validator_missing_fixture`
   - `_analysis` 三件套缺少 `title/keywords/scope`。
   - 期望 Phase 1 gate 失败。

2. `phase1_progress_conflict_fixture`
   - `checker_status_matrix=NOT_RUN`，`machine_checks=PASS`。
   - 期望 doc health 报 blocker。

3. `phase1_metric_drift_fixture`
   - 同一文档中同时写 `65 files` 和 `68 files`。
   - 期望 semantic review 报 metric conflict。

4. `external_ai_boundary_fixture`
   - README 写 offline/privacy-first。
   - 代码包含 `fetch`、`FormData`、`apiKey`。
   - 文档写“无任何外部 API 调用”。
   - 期望 semantic review 报 P0。

5. `project_vision_coverage_fixture`
   - README 写 PWA/TWA/offline。
   - generation plan 未安排平台和隐私文档。
   - 期望 semantic review 报缺失。

## 8. 边界问题和取舍

### 8.1 文件数是否必须完全稳定

文件数可能因为生成 `dev_docs`、链接框架目录、临时文件而变化。AICC 不应要求所有文件数永久相等，而应要求：

- 每个文件数声明必须记录扫描范围。
- 扫描范围必须排除框架、依赖、生成文档和构建产物。
- 同一文档内同一范围的文件数不能互相矛盾。
- 如果 scanner 当前值变化，文档应写“截至本轮扫描”并记录命令。

### 8.2 服务数口径可能有合理差异

“6 个服务实例”和“7 个服务文件”可能都正确，前提是文档明确口径。例如：

- `EchoTalkApp` 构造或初始化中注入 6 个运行时服务实例。
- `src/services/` 下有 7 个 `.ts` 文件，其中 `prompts.service.ts` 是 prompt 生成辅助服务。

AICC 应避免把所有口径差异都当作错误；但必须要求文档解释差异。

### 8.3 外部 endpoint 不一定是 AI Provider

EchoTalk 的发音分析 endpoint 未必是 LLM Provider，也可能是项目作者托管的服务。但只要涉及录音上传、API key 或智能分析，它就属于 AI/外部数据处理边界，必须进入隐私和数据流文档。

### 8.4 README 愿景可能与代码不完全一致

如果 README 写 privacy-first/offline，但代码存在外部上传，不应简单判定项目违背愿景。正确处理是：

- 将核心路径标记为 offline-first。
- 将在线分析标记为可选能力。
- 明确上传数据、触发条件和用户配置。
- 将“是否需要更严格隐私说明”列为待用户确认。

### 8.5 检查器不能替代架构师复核

工具可以拦截常见错误，但项目愿景和架构边界仍需要 AI 进行系统性判断。AICC 应通过模板和 hard gates 逼迫 AI 做这类判断，而不是指望正则完全覆盖。

## 9. 建议实施顺序

### Phase A：先补流程和模板硬约束

1. 更新 `AI_ENTRY_POINT.md` 的方案复查意图路由。
2. 更新 `workflows/path_a_first_generation.md` 的 Phase 1 review hard gates。
3. 更新 `templates/PROGRESS_TEMPLATE.md` 的 `machine_checks` 和 verdict。
4. 更新 `templates/GENERATION_PLAN_TEMPLATE.md` 的证据图、项目定位、外部服务边界。

这一步优先级最高，因为它能立即改善自然指令下 AI 的行为。

### Phase B：补契约和检查器

1. 更新 `run_record_contract.yaml`。
2. 增强 doc health 的进度一致性检查。
3. 增强 semantic review 的 metric consistency 和外部服务边界检查。
4. 增加 Python/JS 双实现一致性测试。

### Phase C：用 EchoTalk 回放验证

在 EchoTalk 上使用同一自然指令重跑：

```text
请根据 AI-Coding-Context/AI_ENTRY_POINT.md，对生成方案进行复查和优化
```

验收条件：

1. AI 必须运行并回写 `summary_validator --strict`。
2. 若 `_analysis` frontmatter 不合规，必须先修正并复跑。
3. `generation_progress.md` 不得同时出现 `NOT_RUN` 和 `PASS` 冲突。
4. AI 必须识别 `GetAccuracyFromRecordedAudio`、`spellApiKey`、`FormData` 上传。
5. AI 必须把 privacy-first/offline PWA、Android TWA 写入正式文档计划。
6. 修正前 verdict 必须为 `BLOCKED_NEEDS_FIX`；全部通过后只能为 `READY_FOR_USER_REVIEW`，等待用户确认。

## 10. 验收标准

完成本方案后，AICC 应满足：

1. EchoTalk 的 `_analysis` 三件套在复查后通过 `summary_validator --strict`。
2. `generation_progress.md` 的状态、机器检查、verdict、时间戳一致。
3. 任何 required checker 失败时，AI 不会建议进入正式文档生成。
4. 量化事实不会在同一文档或跨 `_analysis` 文档中出现未解释冲突。
5. AI 能区分手动 Prompt、外部发音分析 API、本地离线能力。
6. privacy-first/offline/no-server/PWA/TWA 等项目定位能进入文档计划和 AI Rules 规划。
7. 使用简短自然指令触发复查时，AI 仍能完整执行 Phase 1 review hard gates。

## 11. 当前建议

本轮 EchoTalk 测试不需要立即修改示例项目正式文档，因为正式文档尚未生成。当前应先完善 AICC 框架，让下一次复查能自动发现并修正：

- `_analysis` frontmatter 契约失败。
- 进度记录内部冲突。
- 量化事实漂移。
- 外部 AI/音频分析边界误判。
- 项目愿景没有进入正式文档计划。

在这些框架改动完成前，EchoTalk 的 Phase 1 不应通过，正式文档生成也不应启动。
