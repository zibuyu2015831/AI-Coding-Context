---
title: AICC V3.x Comprehensive Review — 改进路线图
summary: 基于本轮 35 项 Issue 拆分的 P0/P1/P2 阶段化修复路线，含责任人、期限、修复成本估算与依赖关系
keywords: improvement | roadmap | aicc | v3.x | p0 | p1 | p2 | fix-plan
scope: 本轮审查后的修复实施计划
verified_at: 2026-04-25
---

# AICC V3.x Comprehensive Review — 改进路线图

> **使用方式**：本路线图按"P0 紧急 / P1 短期 / P2 中期 / 长期治理"四阶段组织。每项含 Issue ID、修复成本、依赖关系、验证命令。
> 修复执行时建议每完成一项即在 Issue_Tracking.md 中状态从 🔴 改为 🟢，并执行 Review_Checklist.md 对应行的复查命令。

---

## 🎯 优先级总览

| 阶段 | 期限 | Issue 数量 | 主要主题 | 总成本 |
|---|---|:-:|---|:-:|
| **P0 紧急** | 1-2 周 | 7 | 命名一致性 + quick_start 重写 + 顶层 frontmatter | ~12 人天 |
| **P1 短期** | 2 周-2 月 | 11 | doc_health_checker 实施 + 剧本 4 工作流 + 体系完善 | ~20 人天 |
| **P2 中期** | 2-3 月 | 13 | frontmatter 全量补全 + 命名规范化 + 边界整理 | ~30 人天 |
| **长期治理** | 持续 | 4 | CI 集成 + dogfood 机制 + 跨平台测试 | ~15 人天 |
| **合计** | | **35** | | **~77 人天** |

---

## 🚨 P0 阶段 — 紧急修复（1-2 周）

### P0-1：重写 quick_start.md

- **Issue**: AICC-20260425-028（**严重**）
- **影响**：R4 新用户旅程核心断点，30 分钟预算失败
- **成本**：1.5 人天
- **依赖**：参照 `workflows/path_a_first_generation.md` 8 步流程对齐
- **修复内容**：
  - 修复步骤跳号（补 步骤 2 / 步骤 3 = 生成方案 + 审核）
  - 闭合所有代码块
  - L235 计数与实际步骤数一致
  - 审核清单段落归入步骤 3
- **验证**：见 Review_Checklist.md L# of AICC-20260425-028
- **责任人**：文档维护者
- **期限**：2026-04-30（1 周内）

### P0-2：统一 V3.0 命名一致性集群

- **Issue**: AICC-20260425-016（AI_RULES 大小写）+ 029（AI_RULES 路径 4 处）+ 032（主文档大小写）
- **影响**：R1 + R4 系统性命名漂移
- **成本**：1.5 人天（全文 grep + 批量改写）
- **依赖**：以 `AI_ENTRY_POINT.md` 术语表 L306-L307 为权威源
- **修复内容**：
  - 全仓库统一 `AI_RULES.md`（大写）
  - 全仓库统一 `dev_docs/AI_RULES.md` 路径
  - 全仓库统一 `dev_docs/AI_Coding_Context.md`（驼峰）
  - 修订 `README.md` L168/L173, `templates/AI_RULES_TEMPLATE.md` L541, `workflows/path_a_first_generation.md` L752/L756, `guides/quick_start.md` L120
- **验证**：`grep -rn 'ai_rules\.md\|ai_coding_context\.md' --include='*.md' .` 应返回空
- **责任人**：文档维护者
- **期限**：2026-04-30

### P0-3：README 步骤计数修正

- **Issue**: AICC-20260425-031
- **影响**：R4 第一印象
- **成本**：0.25 人天
- **修复内容**：L120 `（3 步）` → `（4 步）`，或重组为 3 步
- **责任人**：文档维护者
- **期限**：2026-04-26

### P0-4：guides/quick_start.md 过时框架名清理

- **Issue**: AICC-20260425-030
- **影响**：R4 文档信任
- **成本**：0.25 人天（4 处 sed 替换）
- **修复内容**：`ai_documentation_framework` → `ai_coding_context`（L55、L146、L158、L228）
- **验证**：`grep -rn 'ai_documentation_framework' --include='*.md' . | grep -v dev/V2`
- **责任人**：文档维护者
- **期限**：2026-04-26

### P0-5：顶层 + core/ 关键文档补 frontmatter（034 P0 阶段）

- **Issue**: AICC-20260425-034（**严重**，分阶段修复 P0 部分）
- **影响**：R5 自指 + R2 落地
- **成本**：3 人天（10 个文件，每个含撰写 + 审校）
- **目标列表**：
  - `AI_ENTRY_POINT.md`、`README.md`、`CONTRIBUTING.md`（顶层 3）
  - `core/SUMMARY_FORMAT_SPEC.md`（规范本身必须自带示范）
  - `core/framework_spec.md`、`core/design_decisions.md`、`core/language_rules.md`、`core/security_rules.md`、`core/project_types.md`、`core/update_triggers.md`（core/ 7）
- **工具辅助**：`tools/py/summary_extractor.py` 生成草稿后人工审校
- **验证**：见 Review_Checklist.md
- **责任人**：文档维护者 + AI 辅助
- **期限**：2026-05-07（2 周内）

### P0-6：FRAMEWORK_CONTEXT 顶部重写

- **Issue**: AICC-20260425-001 + 011 + 014
- **影响**：R2 V3.0 落地一致性
- **成本**：1 人天
- **修复内容**：
  - 顶部"V3.0 已完成模块"列出全部 12 项
  - L25-L28 删除"P1 规划中"措辞
  - L703 数字改为 12/18
  - L539-L540 路径修正（reference/ → core/）（同时修 013）
- **责任人**：架构师 + 文档维护者
- **期限**：2026-05-03

### P0-7：PROGRESS.md 内部一致性 + 019 登记

- **Issue**: AICC-20260425-012 + 015 + 008
- **影响**：R2 落地一致性 + dev/ 卫生
- **成本**：0.5 人天
- **修复内容**：
  - L18 加入 011，改为"已完成 12 个"
  - 决定 019 处置：选项 A（创建 confirmed/019-systematic-review-framework/ 目录登记）
  - 删除 L290-L312 末尾乱码与重复段
- **责任人**：架构师
- **期限**：2026-05-07

---

## 📌 P1 阶段 — 短期修复（2 周-2 月）

### P1-1：实施 doc_health_checker.py/.js 双脚本

- **Issue**: AICC-20260425-017（主要）
- **影响**：R1 工作流闭环（剧本 2 + maintenance）
- **成本**：5 人天（设计 + 实施 + 测试 + 文档）
- **依赖**：doc_dependency_tracer.py + summary_validator.py（已存在）
- **修复内容**：
  - 实施 `tools/py/doc_health_checker.py`，参数 `--file` / `--check-code-samples` / `--check-file-paths` / `--check-dependencies` / `--full-check`
  - 实施 `tools/js/doc_health_checker.js`（双脚本对称）
  - 严格遵守零依赖红线
  - 头部完整 docstring
- **验证**：6 处文档引用方均能解析；双脚本对称扫描通过
- **责任人**：工程师
- **期限**：2026-05-15

### P1-2：剧本 4 复杂度告警工作流提升至 Public

- **Issue**: AICC-20260425-019 + 027
- **影响**：R1 工作流闭环（剧本 4 缺失）
- **成本**：2.5 人天
- **依赖**：005 walkthrough.md 已含完整设计
- **修复内容**：
  - 提取 walkthrough.md 内容，重组为 `workflows/complexity_alert_workflow.md`（面向 AI 的 SOP）
  - 在 `AI_ENTRY_POINT.md` 工具索引补充 complexity_scanner 行
  - 在 `workflows/path_d_specific_tasks.md` 增加 `@complexity` 指令章节
  - 在 `tools/README.md` 扩充 complexity_scanner 用法示例
- **责任人**：架构师 + 文档维护者
- **期限**：2026-05-20

### P1-3：dev/V3.0/confirmed/ 命名规范化

- **Issue**: AICC-20260425-022（主要）
- **影响**：C dev 卫生
- **成本**：0.5 人天
- **修复内容**：
  - `git mv dev/V3.0/confirmed/004-adr-system.md dev/V3.0/confirmed/004-adr-system`
  - 同上 005、006
  - grep 全仓库引用方更新
- **责任人**：架构师
- **期限**：2026-05-10

### P1-4：workflows/ + guides/ 补 frontmatter（034 P1 阶段）

- **Issue**: AICC-20260425-034（P1 阶段）
- **成本**：8 人天（40 个文件）
- **修复内容**：补全 25 个 workflows/*.md + 15 个 guides/*.md
- **责任人**：文档维护者
- **期限**：2026-05-30

### P1-5：Public 层 dev/ 真泄漏修复

- **Issue**: AICC-20260425-002（主要）
- **影响**：R3 边界
- **成本**：1 人天
- **修复内容**：
  - `agents/_progress/implementation_progress.md` L5：移除 `(../../dev/V3.0/...)` markdown 链接
  - `workflows/doc_error_fix_workflow.md` L507-509：移除 3 处 `(../dev/V3.0/...)` 链接
  - `core/design_decisions.md` L256/L492、`core/SUMMARY_FORMAT_SPEC.md` L403：补"（仅 dev 分支可见）"明示
  - `CONTRIBUTING.md` L1202-1208 段落开头加边界声明
- **责任人**：文档维护者
- **期限**：2026-05-10

### P1-6：Quality 体系自审收尾（023 + 024 + 025）

- **Issue**: 023（README 索引）+ 024（Guidelines 过度承诺）+ 025（contexts 措辞）
- **成本**：1.5 人天
- **修复内容**：
  - quality/README.md 补 _templates/ 索引、修正 examples 数字
  - Framework_Review_Guidelines.md 删除 Review_Data.zip / Assessment_Dashboard.html
  - quality/README.md L44-L58 contexts/ 措辞改为"按需生成"
- **责任人**：架构师
- **期限**：2026-05-15

### P1-7：剧本 3 测试路径修正

- **Issue**: AICC-20260425-018（次要）
- **成本**：0.25 人天
- **修复内容**：`workflows/doc_error_fix_workflow.md` L488/L491 改为 `tools/py/tests/`
- **责任人**：文档维护者
- **期限**：2026-05-08

### P1-8：仓库根孤儿文件处置

- **Issue**: AICC-20260425-003（次要）
- **成本**：0.5 人天
- **修复内容**：阅读 `audit_metadata.py` 内容；选项 A 迁入 tools/py 或 B 迁入 dev/quality/，必要时删除
- **责任人**：架构师
- **期限**：2026-05-15

### P1-9：dev/ 内部悬空引用 + archived/ 命名

- **Issue**: AICC-20260425-009 + 010（次要 + 建议）
- **成本**：0.5 人天
- **修复内容**：
  - `dev/V3.0/reference/commit_as_prompt_analysis.md` L699 路径修正为 confirmed/018-...
  - `dev/V3.0/archived/advanced-audit-report.md` 阅读后迁出（reference/ 或 quality/audits/）
- **责任人**：架构师
- **期限**：2026-05-12

### P1-10：005 工具链补全 + complexity --check-doc-errors 决策

- **Issue**: AICC-20260425-026（次要）+ 020（次要）+ 021（建议）
- **成本**：3 人天
- **修复内容**：
  - 决策：补全 architecture_analyzer.py/.js 还是从 walkthrough 删除该工具引用
  - 推荐：删除 walkthrough 引用 + 在 P2 路线图中规划补全
  - document_health_check.md L418 删除 `--check-doc-errors` 命令引用
  - complexity_scanner default config 路径加 `--help` 明示
- **责任人**：工程师 + 架构师
- **期限**：2026-05-30

### P1-11：guides/quick_start 工具引导对齐 V3.0

- **Issue**: AICC-20260425-033（次要）
- **成本**：0.5 人天
- **修复内容**：L31-L36 改为优先推荐 `python tools/py/project_scanner.py . --exclude-standard`，将 find/cloc 降为 fallback
- **责任人**：文档维护者
- **期限**：2026-05-12

---

## 🌳 P2 阶段 — 中期治理（2-3 月）

### P2-1：agents/ + templates/ + config/ 全量补 frontmatter（034 P2 阶段）

- **Issue**: AICC-20260425-034（P2 阶段）
- **成本**：18 人天（86 个文件）
- **修复内容**：59 个 agents + 24 个 templates + 3 个 config
- **责任人**：文档维护者
- **期限**：2026-07-30

### P2-2：dev/ 层 frontmatter 补全

- **成本**：12 人天（约 200+ 文件）
- **修复内容**：dev/V3.0、dev/architecture、dev/complexity、dev/quality 等
- **责任人**：架构师
- **期限**：2026-08-30

### P2-3：JS 头部 docstring 完善

- **Issue**: AICC-20260425-035（建议）
- **成本**：0.25 人天
- **修复内容**：tools/js/aac_validator.js 添加 JSDoc 头部
- **期限**：2026-06-15

### P2-4：旧框架名全仓库扫描确认

- **成本**：1 人天
- **修复内容**：grep 整个 dev/ 历史档案，确认 V2.x 时期 ai_documentation_framework 痕迹仅作历史保留，Public 层与 V3.0 已完全清理
- **期限**：2026-06-15

---

## 🛡️ 长期治理 — 持续改进

### 治理-1：CI 集成 frontmatter 强制门禁

- **关联 Issue**: 034 根因解决
- **成本**：3 人天
- **目标**：在 GitHub Actions / pre-commit 中加入 `summary_validator` 强制检查；缺 frontmatter 的新提交自动拒绝
- **里程碑**：2026-06-30 上线

### 治理-2：U+FFFD + 未闭合代码块 pre-commit hook

- **关联 Issue**: 004（已修）+ 008
- **成本**：1 人天
- **目标**：阻止编码乱码与未闭合 markdown 进入仓库

### 治理-3：跨平台兼容性测试

- **关联**：当前仅 Linux 测试
- **成本**：5 人天
- **目标**：在 macOS + Windows PowerShell 上完整跑通新用户旅程

### 治理-4：复审计划

- **时机**：2026-06-06（本轮 6 周后）
- **范围**：Component scope，专项验证 P0 + 50% P1 修复效果
- **执行人**：复用本轮 quality 体系

---

## 📊 修复进度跟踪

修复时请同步更新：

1. `Issue_Tracking.md` — 状态从 🔴 改为 🟢
2. `Review_Checklist.md` — 勾选对应行 + 填写验证人/日期
3. 创建 PR，commit message 格式：`fix(audit-20260425): AICC-NNN 简短描述`

---

## 🎯 成功标准

本路线图执行成功的判定：

- ✅ P0 全部 7 项完成 → AICC 进入"生产就绪 A 级"候选
- ✅ P1 完成 80%+ → 通过 6 周后复审
- ✅ frontmatter Public 合规率 ≥ 80%
- ✅ 30 分钟新用户旅程实测通过
- ✅ doc_health_checker 实体补全且 6 处引用全部可调用

---

**版本**: v1.0
**创建日期**: 2026-04-25
**维护者**: Framework Team
**审查者**: Claude Opus 4.7
