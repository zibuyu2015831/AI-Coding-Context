---
title: AICC Skill 化 — 实施路线图（Phase 0a-5）
summary: 将 skill 化迁移拆解为 8 个独立可发布或可验收的阶段（Phase 0a、0b、1、1.5、2、3、4、5），每阶段包含目标、交付物、验收标准、依赖、估算工作量与风险。Phase 之间以"独立可发布/可验证"为门槛，避免一次性大爆炸式迁移。
keywords: aicc | implementation | roadmap | phases | gates
scope: dev/plan/skill-migration 子项目（路线图阶段）
related_files: 01-feasibility-and-architecture.md | 02-component-mapping.md | 04-edge-cases-and-risks.md | README.md
dependencies: 01-feasibility-and-architecture.md | 02-component-mapping.md
verified_at: 2026-04-26
---

# 03 — 实施路线图

## 一、设计原则

1. **每个 Phase 独立可发布**：完成 Phase N 即可发布一个可用的 plugin 版本，不依赖 Phase N+1。
2. **Phase Gate 严格执行**：上一阶段未通过验收，下一阶段不开始。
3. **MVP 优先**：Phase 1 只做"能让用户跑通主流程"的最小集，不追求完整 V3.0 能力。
4. **dogfood 触发点**：从 Phase 2 起，AICC 框架团队自身可选择性地用 plugin 维护框架仓库（验证可用性）。
5. **clone 模式不阻塞**：所有 Phase 都不破坏 clone 模式，clone 用户在 Phase 5 之前不受影响。

## 二、Phase 总览

| Phase | 名称 | 主要交付物 | 估算 | 累计耗时 | 关键里程碑 |
|---|---|---|---|---|---|
| **Phase 0a** | 技术验证 + 决策闭环 | plugin schema、skill frontmatter、namespace、bin、互调用、发布渠道验证 | 0.25 人月 | 0.25 人月 | "关键假设已实测，不再靠推断" |
| **Phase 0b** | 真实资产清单 + plugin 骨架 | plugin.json、短名 skills 目录、bin/scripts、CI、资产清单、打包规则 | 0.5 人月 | 0.75 人月 | "可装一个空 plugin，且资产映射可信" |
| **Phase 1** | 两个低风险核心 skill MVP | `init` / `health-check` | 1.5 人月 | 2.25 人月 | "用户可完成首次生成和文档健康检查" |
| **Phase 1.5** | 增量更新 skill | `incremental-update` + commit-guided + git-safety | 0.75 人月 | 3.0 人月 | "Git 变更驱动文档更新可控可回滚" |
| **Phase 2** | V3.0 高价值 skill | `design-thinking` / `mutual-review` / `adr` | 1.5 人月 | 4.5 人月 | "V3.0 P0/P1 核心思维能力 skill 化" |
| **Phase 3** | V3.0 剩余 skill + 知识复用 | `complexity-dashboard` / `doc-fallacy-fix` / `systematic-review` / `doc-reading-habit` / `knowledge-reuse` | 2.0 人月 | 6.5 人月 | "V3.0 全部已落地能力 skill 化" |
| **Phase 4** | 多平台扩展 | gemini-extension.json + flat skill repackage + tool name 翻译表 + 测试 | 0.5 人月 | 7.0 人月 | "Gemini / flat skill 用户有可用包" |
| **Phase 5** | 迁移指南 + clone 归档 | migrate-from-clone.md + 兼容测试 + 清理 | 0.5 人月 | 7.5 人月 | "现有 clone 用户有迁移路径" |

---

## 三、Phase 0a：技术验证 + 决策闭环（0.25 人月）

### 3.1 目标

在创建正式骨架前，先把所有依赖 Claude Code plugin 行为的关键假设实测闭环。此阶段不迁移业务内容，不写正式 skill，只回答"方案能否按设计运行"。

### 3.2 交付物

- 最小测试 plugin：验证 `.claude-plugin/plugin.json` schema、skill frontmatter、短名 skill 显式调用形式（如 `/aicc:init`）
- `bin/` 验证：确认 `bin/aicc-smoke-test` 是否进入 Bash PATH；若可用，确定为脚本调用主路径
- 跨引用验证：确认 skill 是否可读取 plugin 顶级 `references/`
- 互调用验证：确认一个 skill 是否能稳定引导加载另一个 skill
- 发布渠道验证：本地 `--plugin-dir`、git URL、zip artifact 至少确认开发期和 alpha 期路径
- 决策记录：把 Q1-Q5 的结果写回 `05-open-questions.md`

### 3.3 验收标准

- [ ] 明确 Claude Code skill frontmatter 是否需要 `name` 字段；CI 规则随实测结果确定
- [ ] 明确短名 skill 的用户可见形式，确认是否采用 `/aicc:init`
- [ ] 明确 `bin/` 是否可作为主调用路径；不可用时定义 `AICC_PLUGIN_ROOT` fallback
- [ ] 明确 plugin 顶级 `references/` 是否可被 skill 直接读取
- [ ] 明确 Phase 1 是否允许 skill 互调用；不可用则保留内嵌简版策略

### 3.4 风险

| # | 风险 | 缓解 |
|---|---|---|
| P0a-1 | Claude Code plugin 行为与规划不一致 | 在进入骨架前调整命名、目录、CI，不迁移业务内容 |
| P0a-2 | `bin/` 不可用 | 回退到 `AICC_PLUGIN_ROOT` + direct scripts 调用 |
| P0a-3 | 互调用不可用 | Phase 1/2 使用 handoff 文案或内嵌简版，不阻塞 MVP |

---

## 四、Phase 0b：真实资产清单 + plugin 骨架（0.5 人月）

### 4.1 目标

建立 plugin 的物理骨架、发布管线和真实资产清单，让框架可以"长出 skill"而不影响 clone 模式。此阶段必须纠正初版计划中 agents/templates/workflows 的映射偏差。

### 4.2 交付物

**目录骨架**（在 `plugin/` 下）：

```
plugin/
├── .claude-plugin/
│   └── plugin.json                  ← name, version, description, author 等
├── README.md                        ← plugin 用户文档（占位版）
├── CLAUDE.md                        ← 跨 skill 共识（占位版）
├── references/                      ← build-time copy 生成的共享 references
├── skills/                          ← 空目录，预留
├── agents/                          ← 空目录，预留
├── bin/                             ← 包装命令，优先调用入口
├── scripts/
│   ├── py/                          ← 从根目录 tools/py/ build-time copy
│   ├── js/                          ← 同上
│   └── fallback/                    ← 同上
├── hooks/                           ← 空目录，预留
├── tests/                           ← plugin 级 evaluation 体系
│   └── README.md                    ← 测试方法说明
└── plugin-manifest.generated.json   ← 资产清单，CI 校验引用完整性
```

**发布机制**：
- GitHub / Gitee Release：`v0.1.0-skill-mvp` 等 tag → 自动打包 plugin/ 目录为 release artifact
- plugin marketplace 或 git URL 安装方式选定（见 `05-open-questions.md` Q4）
- CI 自动检查清单（每次 PR + main push 触发）：
  - [ ] `plugin.json` schema 合法（必填字段 / 字符限制）
  - [ ] 每个 `skills/*/SKILL.md` 有合法 frontmatter（字段以 Phase 0a 实测为准；`description` ≤ 1024 字符；description 用第三人称且包含 "Use when"）
  - [ ] 每个 SKILL.md body 行数 < 500（`wc -l` 检查）
  - [ ] references 不存在嵌套引用（grep `references/.*\.md` 内是否再有 `..` 或 `references/` 引用）
  - [ ] 所有路径用 forward slash（grep `\\\\` 反斜杠）
  - [ ] skill 中脚本调用优先使用 `bin/aicc-*` 包装命令
  - [ ] 跨 skill 引用（`references/`）目标存在
  - [ ] `plugin-manifest.generated.json` 中的引用目标全部存在
  - [ ] release artifact 排除 `__pycache__/`、测试缓存、开发审计文件
  - [ ] frontmatter `verified_at` 不超过 N 天（防陈旧）
  - [ ] description 中没有时间敏感信息（"after 2025"、"before August" 等正则检查）

**核心规范文档**（`dev/plan/skill-migration/standards/` 下，规划期辅助产物）：
- `skill-naming-convention.md`：命名细则（Claude Code 短名 / flat repackage 前缀 / 大小写 / 连字符）
- `skill-md-template.md`：SKILL.md 标准模板（含 frontmatter、章节结构）
- `description-style-guide.md`：description 写法规范（"Use when..." 起头、第三人称、不总结 workflow、< 1024 字符）
- `references-layout.md`：references 目录组织规范（1 层深、命名约定）
- `scripts-call-convention.md`：脚本调用约定（`bin/` 包装命令优先，环境变量路径兜底）

### 4.3 验收标准

- [ ] 运行 `/plugin install <git-url>` 成功，列出 0 个 skill 但 plugin 已加载
- [ ] CI 在 PR 上自动跑 plugin.json validation 与 skill frontmatter lint
- [ ] 框架仓库的 `tools/` 与 `plugin/scripts/` build-time copy 机制通过测试
- [ ] 所有 `core/` 共享文件已在 `plugin/references/` 建立构建副本
- [ ] 真实资产清单覆盖 workflows / agents / templates / tools，并标记哪些不进入 release
- [ ] 5 份 standards 文档完成，并被 `01-feasibility-and-architecture.md` 引用

### 4.4 依赖与前置

- Phase 0a 全部完成
- 已选定 plugin 发布渠道（验证开放问题 Q4）

### 4.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P0b-1 | 真实资产清单暴露更多漏项 | 先修映射，不进入业务迁移 |
| P0b-2 | build-time copy 与源码漂移 | CI 校验 manifest；release 前强制重新生成 |
| P0b-3 | plugin marketplace 政策变化 | 同时支持 git URL / zip / 本地 path 作为兜底 |

---

## 五、Phase 1：两个低风险核心 skill MVP（1.5 人月）

### 5.1 目标

先覆盖 clone 模式下风险较低、用户感知最强的两个流程：**首次生成 / 健康检查**。增量更新涉及 Git 安全、commit-guided、hooks 与回滚，单独放入 Phase 1.5。

### 5.2 交付物

#### Skill 1：`init`（首次生成）

- SKILL.md（≈ 250 行）+ 14 个 references
- 嵌入：design_facilitator、summary_generator runtime agents 引用
- 调用脚本：env_diagnosis、project_scanner、summary_extractor
- 调用共享 references：language_rules、security_rules、project_types、summary_format_spec
- **互调用占位**：Step 5.5 暂用"内嵌简版 design-thinking"，Step 7 暂用"内嵌简版 mutual-review"。等 Phase 2 落地后改为调用对应 skill。

#### Skill 2：`health-check`

- SKILL.md（≈ 220 行）+ mode 1/2/3 references + checklist references
- 调用脚本：doc_health_checker、summary_related_checker、doc_dependency_tracer
- handoff 提示：检测到 drift → 建议 Phase 1.5 的 `incremental-update`；检测到错误 → 建议 Phase 3 的 `doc-fallacy-fix`

#### baseline 测试集（writing-skills 推荐）

- 为每个 skill 编写至少 3 个 evaluation：
  - 应触发场景（positive case）
  - 不应触发场景（negative case）
  - 边界场景（ambiguous case）
- 测试用 `tests/<skill-name>/eval-N.json` 格式
- 验证 description 准确率（应触发但没触发、不应触发但触发了的比例）

### 5.3 验收标准

**功能**：
- [ ] 全新项目（无 dev_docs/）+ 用户说"set up AI docs" → 自动触发 `init`，走完 8 步生成完整 dev_docs/
- [ ] 已有 dev_docs/ + 用户说"check docs health" → 自动触发 `health-check`，输出健康报告
- [ ] 用户说 "@commit" 或 "update docs after commit" 时，Phase 1 不直接执行 Git 更新，而是明确提示该能力属于 Phase 1.5
- [ ] 两个 skill 在同一项目 lifecycle 内可顺序使用（init → 用一阵 → health-check）

**质量**：
- [ ] description 触发准确率 > 85%（baseline 测试）
- [ ] 每个 SKILL.md < 500 行
- [ ] 没有 reference 嵌套引用
- [ ] 所有路径用 forward slash
- [ ] Python 与 Node 降级路径都验证通过

**对比 clone 模式**：
- [ ] 同一份测试项目，clone 模式与 plugin 模式产出的 dev_docs/ 在结构上完全一致（差异 < 5%）

### 5.4 依赖与前置

- Phase 0a / 0b 全部完成
- 测试项目（至少 3 个：纯前端 React、纯后端 Python、Monorepo）准备就绪

### 5.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P1-1 | 触发准确率达不到 85% | Phase 1 中预留 1 周专门优化 description；引入 negative cases 防止过度触发 |
| P1-2 | health-check 与后续 incremental-update 边界不清 | description 写明 health-check 只诊断与建议，不执行 Git 更新；测试覆盖 "@commit" 场景 |
| P1-3 | `init` 内嵌的"简版 design-thinking"质量低于独立 skill | 文档中标注 "Phase 2 升级"；不阻塞 Phase 1 发布 |
| P1-4 | 用户已有 dev_docs/ 但格式与 plugin 期望不一致 | 加入"格式检测"逻辑，不一致时退化为 health-check |

### 5.6 里程碑产出

发布 `aicc@0.1.0` plugin，附带 release notes 包括：
- 已支持的 2 个 skill：`init`、`health-check`
- 与 clone 模式的对比文档
- 已知限制（增量更新与 V3.0 进阶能力暂未 skill 化）

---

## 六、Phase 1.5：增量更新 skill（0.75 人月）

### 6.1 目标

单独迁移 `incremental-update`，覆盖提交前的结构化 commit 生成、Git 变更分析、commit-guided 文档更新、Git 安全检查和局部文档修改。此阶段单独拆出，是因为它包含写文件、读 Git 历史、可能安装 hooks，风险明显高于 `init` / `health-check`。

### 6.2 交付物

#### Skill 3：`incremental-update`

- SKILL.md（≈ 320 行）+ commit_authoring / commit_analysis / git_safety / smart_partial_update references
- 嵌入：commit_analyst runtime agent
- 调用脚本：git_diff_analyzer、git_safety、manage_fix_with_git、commit_template_cli、commit_parser、commit_quality_scorer、commit_integrity_validator
- `bin/` 包装命令：`aicc-commit-message`、`aicc-commit-score`、`aicc-git-diff`、`aicc-git-safety`、`aicc-doc-update`

### 6.3 验收标准

- [ ] 用户说 "commit these changes" / "提交当前改动" / "prepare commit message" → 自动触发 `incremental-update` 的 commit-authoring 子流程
- [ ] 方案、架构、功能、修复、迁移类提交默认生成 `prompt(type)` + `WHAT/WHY/HOW` 结构化 commit message
- [ ] 小型机械修改可降级为普通 Conventional Commit，并在输出中说明原因
- [ ] 用户 commit 后说 "@commit" 或 "update docs" → 自动触发 `incremental-update`
- [ ] 所有写入 dev_docs/ 的操作先输出计划，再执行局部更新
- [ ] Git 安全检查能识别 dirty worktree、未跟踪文件、危险分支和 hook 安装风险
- [ ] 同一测试项目中，clone 模式和 plugin 模式的增量更新差异 < 5%
- [ ] baseline eval 通过率 > 85%，且覆盖 merge commit / revert / cherry-pick 边界

### 6.4 依赖与前置

- Phase 1 完全完成
- `bin/` 包装命令与 Git 相关脚本已在 Phase 0a/0b 验证

### 6.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P1.5-1 | Git 操作误伤用户工作区 | 强制 dry-run / plan-first / 人工确认；不自动执行 destructive 命令 |
| P1.5-2 | commit-authoring、commit-guided 与普通增量更新边界不清 | description 中明确提交前请求进入 commit-authoring；@commit / commit hash / recent changes 进入 commit-guided |
| P1.5-3 | hook 安装触发权限或信任问题 | hook 安装永远显式确认，默认只给说明和脚本路径 |

### 8.6 里程碑产出

`aicc@0.1.5`，支持 `init` / `health-check` / `incremental-update` 三个主流程。

---

## 七、Phase 2：V3.0 高价值 skill（1.5 人月）

### 7.1 目标

将 V3.0 P0/P1 中的"思维能力"（设计思维、AI 互审、ADR）独立成 skill，让用户能脱离 init 流程直接调用。

### 7.2 交付物

#### Skill 4：`design-thinking`

- SKILL.md（≈ 200 行）+ 5 step references + 4 expert team references + 2 examples
- 验证可被 `init` Step 5.5 通过 `/aicc:design-thinking` 调用（替换 Phase 1 的内嵌简版）
- 验证可被用户直接 `@think` 触发

#### Skill 5：`mutual-review`

- SKILL.md（≈ 220 行）+ severity classification + reviewer persona + 4 类 checklist
- 嵌入 plan_reviewer / code_reviewer runtime agents
- 验证可被 `init` Step 7 调用，替换 Phase 1 的内嵌简版

#### Skill 6：`adr`

- SKILL.md（≈ 200 行）+ ADR 生命周期 + 模板 + why_tool / aac_validator usage
- 调用脚本：why_tool、aac_validator
- 验证：用户在编写新功能时说"create ADR for this decision" → 自动触发并生成符合规范的 ADR 文档

#### Phase 1 互调用闭环

- 修改 `init` SKILL.md，将 Step 5.5/Step 7 的"内嵌简版"改为显式 skill handoff
- 验证互调用机制工作（如不可行，回退方案见 `01-feasibility-and-architecture.md §4.5`）

### 7.3 验收标准

- [ ] 用户在任意上下文说"5 Why 分析这个决策"→ 触发 `design-thinking`
- [ ] 用户说"Review my plan"→ 触发 `mutual-review`
- [ ] 用户说"Create ADR for X"→ 触发 `adr` 并生成符合 dev/architecture/adr-template 格式的文档
- [ ] `init` 内的 Step 5.5/7 无缝调用三个新 skill
- [ ] baseline eval 通过率 > 85%

### 7.4 依赖与前置

- Phase 1.5 完全完成
- skill 互调用机制已确认可行（开放问题 Q5 已闭环）

### 7.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P2-1 | skill 互调用不被 Claude Code 支持 | 降级为 subagent 调度（已有 superpowers 模式参考）或继续内嵌简版 |
| P2-2 | `adr` 与 dev/architecture 的 dogfood ADR 体系冲突 | plugin 的 `adr` 面向用户项目；dev/architecture 是框架自身。明确双轨边界 |
| P2-3 | `mutual-review` 与 superpowers:requesting-code-review 触发优先级冲突 | description 加 "for AICC-generated plans/docs" 限定；不与 superpowers 抢 code review 场景 |

### 7.6 里程碑产出

`aicc@0.2.0`，6 个 skill 完整支持。release notes 包含三大新 skill 的使用示例。

---

## 八、Phase 3：V3.0 剩余 skill（2.0 人月）

### 6.1 目标

把 V3.0 已落地但还未 skill 化的能力全部补齐：复杂度仪表盘、文档谬误修复、系统化文档审核、文档阅读习惯、跨项目知识复用。

### 6.2 交付物

#### Skill 7-11（5 个 skill 工作量并不均匀，详见下表）

| skill | SKILL.md 行数估算 | 主要 references | 主要脚本依赖 | 估算工作量 |
|---|---|---|---|---|
| `complexity-dashboard` | 180 | scanner_usage / report_format / threshold_config / alert_rules | complexity_scanner, report_generator, notifier | **0.4 人月**（已有完整脚本） |
| `doc-fallacy-fix` | 220 | dependency_tracing / impact_analysis / batch_fix / history_management / git_branch_strategy | doc_dependency_tracer, semantic_related_detector, batch_fix_manager, fix_history_manager, manage_fix_with_git, doc_fix_executor | **0.6 人月**（6 个脚本 + 复杂工作流 + git 分支策略） |
| `systematic-review` | 220 | review_plan_template / review_principles / round_lifecycle / progress_index_template | timestamp_analyzer（verified_at 校验） | **0.4 人月**（纯方法论，无重型脚本，但需要从 dev/case_skillatlas_review 提取通用范式） |
| `doc-reading-habit` | 200 | detection_heuristics / recommendation_workflow + document_recommender / understanding_guardian agents | summary_related_checker, summary_index_generator, file_reader | **0.3 人月**（小） |
| `knowledge-reuse` | 180 | kb_config / reference_resolution + multi_project_setup example | knowledge_cli, knowledge_matcher, knowledge_repo_manager | **0.3 人月**（仅在 V3.0 010 落地后启动；如 010 推迟则此项移到 Phase 3.5） |
| **Phase 3 合计** | — | — | — | **2.0 人月** |

#### handoff 网络完善

- `health-check` 检测到错误 → 推荐 `doc-fallacy-fix`
- `init` 检测到大型项目 → 推荐 `complexity-dashboard`
- `systematic-review` 在每轮 review 中可调用 `mutual-review`、`doc-fallacy-fix`

### 6.3 验收标准

- [ ] 11 个 skill 全部发布且 baseline eval 通过率 > 85%
- [ ] handoff 网络在测试场景中按预期触发
- [ ] plugin 总文档行数 < 25k（控制规模）
- [ ] `knowledge-reuse` 与 V3.0 010 实施同步（如 010 仍在进行，此 skill 等 010 落地）

### 6.4 依赖与前置

- Phase 2 完全完成
- V3.0 010 (跨项目知识复用) 落地（影响 `knowledge-reuse`）

### 6.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P3-1 | 太多 skill 命名空间污染 | Claude Code 内依赖 `/aicc:*` namespace；flat 包才使用 `aicc-*` 前缀；监测用户反馈"找不到要的 skill" |
| P3-2 | `systematic-review` 与 dev/quality/ 体系混淆 | 在 SKILL.md 明确 "for user projects, not for AICC framework itself" |
| P3-3 | `knowledge-reuse` 依赖的 010 推迟 | 此 skill 推后到 Phase 3.5 单独发布，不阻塞其他 |

### 6.6 里程碑产出

`aicc@0.5.0`，11 个 skill 完整支持。release notes 包含 V3.0 全部能力的 skill 化映射表。

---

## 九、Phase 4：多平台扩展（0.5 人月）

### 9.1 目标

让 plugin 在 Gemini CLI 上可用；为 Codex / Copilot CLI 留好兼容钩子。

### 9.2 交付物

- `plugin/gemini-extension.json`：Gemini CLI 加载清单
- `plugin/references/platform_compat/`：tool name 翻译表（Claude Code → Gemini）
- `plugin/CLAUDE.md` 与 `plugin/GEMINI.md` 双文件（参考 superpowers 模式）
- 每个 skill 的 SKILL.md 在工具调用处使用平台无关的语义（如 "use the file-edit tool" 而非 "use Edit"），并在 references 里给出平台映射

### 9.3 验收标准

- [ ] 在 Gemini CLI 中安装 plugin 并触发任意 skill 成功
- [ ] 同一个 skill 在 Claude Code 与 Gemini CLI 上输出对齐（差异 < 10%）
- [ ] tool name 翻译表覆盖至少：Read / Edit / Write / Bash / Grep / Glob

### 9.4 依赖与前置

- Phase 3 完成
- Gemini CLI plugin 加载机制稳定

### 9.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P4-1 | Gemini 不支持 plugin hooks/ 或 flat skill repackage | 这些功能在 Gemini 平台降级为不可用，文档说明 |
| P4-2 | tool 行为差异（Edit 在两平台语义不同） | 在每个 skill 的 SKILL.md 用语义描述而非工具名，避免硬编码 |

---

## 十、Phase 5：迁移指南 + clone 模式归档（0.5 人月）

### 10.1 目标

让现有 clone 用户有清晰的迁移路径；把 clone 模式降级为兜底维护级别。

### 10.2 交付物

- `dev/plan/skill-migration/migrate-from-clone.md`：手把手迁移指南
  - 现有 dev_docs/ 兼容性说明（哪些保留、哪些升级）
  - 迁移检查清单
  - 常见问题
- `tools/py/migrate_to_skill.py`：自动化迁移辅助脚本
  - 检测现有 dev_docs/ 是否兼容 plugin 期望的格式
  - 提示需手动处理的差异
  - 备份 + 升级
- 框架仓库 `README.md` 更新：plugin 模式置顶；clone 模式降至"高级用户/兜底"
- `dev/plan/skill-migration/clone-mode-deprecation-policy.md`：clone 模式的维护承诺
  - 维护到何时
  - 哪些 P0 bug 仍然修复
  - 何时停止

### 10.3 验收标准

- [ ] 至少 3 个真实 clone 用户项目完成迁移并验证 plugin 模式工作正常
- [ ] migrate_to_skill.py 通过测试集
- [ ] 框架仓库的 README 已更新，plugin-first 在前
- [ ] clone 模式 deprecation policy 明确（即便决定"长期保留"也要明文写出）

### 10.4 依赖与前置

- Phase 4 完成
- 至少 1 个 alpha 用户群完成 Phase 1-3 试用

### 10.5 风险

| # | 风险 | 缓解 |
|---|---|---|
| P5-1 | 现有 clone 用户拒绝迁移 | 明确"clone 不停止维护"；迁移完全自愿 |
| P5-2 | 迁移脚本破坏现有 dev_docs/ | 迁移前自动 git commit + 备份；提供 rollback |

### 10.6 里程碑产出

`aicc@1.0.0`：plugin 模式正式 GA，clone 模式归位为兜底。

---

## 十一、Phase Gate 与决策点

### 9.1 Phase 间决策点

| 决策点 | 触发条件 | 决策内容 |
|---|---|---|
| Phase 0a → 0b | 技术验证完成 | 是否需要改 plugin 结构、frontmatter、bin 或命名规则？ |
| Phase 0b → 1 | 骨架与资产清单完成 | 是否需要补 standards 文档？真实资产映射是否可信？ |
| Phase 1 → 1.5 | init / health-check 验收完成 | 是否启动 Git 增量更新，还是继续优化触发准确率？ |
| Phase 1.5 → 2 | incremental-update 验收完成 | Git safety 与 commit-guided 是否足够稳定？ |
| Phase 2 → 3 | 6 skill 验收完成 | 互调用机制是否稳定？是否需要回退方案？ |
| Phase 3 → 4 | 11 skill 验收完成 | 是否暂缓多平台、专注 plugin 优化？ |
| Phase 4 → 5 | Gemini CLI 测试通过 | 是否启动 clone 归档？还是再等用户反馈？ |

### 9.2 紧急回退预案

如某 Phase 验收无法通过，可走以下回退：
- **Phase 0a 失败**：暂停骨架搭建，回到架构设计修订
- **Phase 1 失败**：保留 plugin 骨架，skill 内容回退到"半成品"，发布 alpha-only release
- **Phase 1.5 失败**：暂缓增量更新，Phase 2 仍可继续推进思维类 skill
- **Phase 2 失败（互调用不可行）**：永久使用内嵌简版策略；记入 `04-edge-cases-and-risks.md`
- **Phase 3 失败（某 skill 难以独立）**：合并相关 skill；如 systematic-review 难以独立，并入 health-check 作为 mode 4
- **Phase 4 失败（Gemini 不兼容）**：plugin 维持 Claude Code-only；不阻塞 Phase 5
- **Phase 5 失败（用户拒绝迁移）**：plugin 与 clone 长期双轨；维护成本翻倍但用户体验不受损

---

## 十二、监控与反馈

### 12.1 持续指标

| 指标 | 测量方法 | 阈值 |
|---|---|---|
| skill 触发准确率 | baseline eval 自动化 | > 85% |
| 用户首次接入耗时 | 用户反馈调研 | < 10 分钟 |
| plugin 加载 token 开销 | session 启动后系统提示 size | < 5k token |
| skill 互调用成功率 | Phase 2 测试 | > 95% |
| clone vs plugin 输出一致性 | 同项目对比测试 | 差异 < 5% |

### 12.2 反馈渠道

- GitHub Issues（plugin 仓库）
- 框架仓库 `dev/discussions/`（保留）
- alpha 用户群（Phase 1 之后建立）

---

## 十三、本章小结

| 维度 | 值 |
|---|---|
| Phase 数 | 8（Phase 0a、0b、1、1.5、2、3、4、5） |
| 总耗时估算 | 7.5 人月 |
| 独立可发布次数 | 8 次（每 Phase 一次 release / checkpoint） |
| Phase Gate 数 | 7 |
| 紧急回退预案 | 6 套（覆盖技术验证、核心 skill、增量更新、多平台等） |

**关键判断**：每个 Phase 都设计为**独立可发布**，意味着即使 Phase 4/5 永远不进行，Phase 0-3 完成后用户已能 90% 替代 clone 模式。**这降低了总规划的"全有或全无"风险**。

**下一文档**：[`04-edge-cases-and-risks.md`](./04-edge-cases-and-risks.md) —— 边界条件与风险全景。
