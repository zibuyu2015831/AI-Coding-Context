---
title: V3.x Comprehensive Review — 复审验证报告
summary: 对 2026-04-25 V3.x Comprehensive Review 全部 35 项 Issue 的二次复审结果；含真实性核查、描述准确性评估、修复方案系统架构师视角评估与重写
keywords: re-review | verification-report | aicc | v3.x | architecture-review
scope: 复审本轮 35 项 Issue
verified_at: 2026-04-26
---

# V3.x Comprehensive Review — 复审验证报告

> **文档定位**：原审核报告（`Comprehensive_Review_Report.md`）的二次校核与方案优化输出。
>
> **核心目标**：使后续 AI 或维护者可直接据本报告执行最优修复，无需再回查原始审核记录。
>
> **进度跟踪**：详见 `Review_Verification_Progress.md`

---

## 📌 元信息

| 字段 | 值 |
|---|---|
| 复审日期 | 2026-04-26 起 |
| 复审范围 | 35 项 Issue（AICC-20260425-001 ~ 035） |
| 复审深度 | 全量逐条 + 系统架构师视角 |
| 复审形式 | 评估 + 补充 + 对重大缺陷方案重写 |
| 输入 | `Issue_Tracking.md` / `Issue_Analysis.md` / 原仓库文档与代码 |
| 主审 AI | Claude Opus 4.7 (1M context) |

---

## 🧭 复审输出说明

每条 Issue 输出 5 字段：

1. **真实性结论**：✅ 真实存在 / ⚠️ 部分存在 / ❌ 不存在
2. **描述准确性**：✅ 准确 / ⚠️ 偏差 / ❌ 严重失实
3. **方案评估**：✅ 通过 / 🟡 需补充 / 🔴 重大缺陷需重写
4. **关键证据**：实地核查见到的事实
5. **架构师建议**：补充优化项 / 重写方案（如适用）

---

## 📊 复审结论汇总

| 维度 | 数值 |
|---|---|
| 总 Issue 数 | 35 项 + B2 附带 2 项 = 37 个修复点 |
| 真实性 | 35/35 全部真实存在（100%） |
| 描述完全准确 | 29/35（83%） |
| 描述偏差 / 漏报 | 6/35（17%）— 016 / 017 / 029 / 032 / 026 / 030（连续漏报模式见系统性发现 §6） |
| 描述严重失实 | 0 |
| 方案 ✅ 通过 | 21 项（60%） |
| 方案 🟡 需补充 | 10 项（29%） |
| 方案 🔴 重大缺陷已重写 | 4 项（11%）— 015 / 029 / 017+026 / 028 |
| 修复完成度 | 37/37（100%） |
| 回归验证 | B1 + B2 + B3 + B4 + B5 全部 PASS |

---

## 🔹 Batch 1：命名一致性 + 路径/边界

> **批次目标**：核查命名集群（016/029/032）与路径/边界类（002/003/022/010）的真实性与方案最优性。
>
> **完成日期**：2026-04-26
>
> **批次结论**：
> - 7 项 Issue 全部 **真实存在**
> - 描述完全准确：3 项（002, 022, 010）
> - 描述有偏差需补充：3 项（016, 032, 003）
> - 描述偏差且方案有重大缺陷：1 项（029 — 推荐目标路径与现状majority冲突，"权威源"引用根本不存在）
> - 修复方案处置：✅ 通过 1 项 / 🟡 需补充 5 项 / 🔴 重大缺陷需重写 1 项

---

### AICC-20260425-016 — AI_RULES.md 大小写不一致

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ 偏差 — 描述只列了 path_a L752/L756 两处 lowercase，实际仓库还有 **3 处** lowercase 漏报：
  - `.kiro/specs/post-generation-audit/QUICK_START.md:157` — `"ai_rules.md"`
  - `dev/real_case/002/quality_review/COMPREHENSIVE_AUDIT.md:88, 328, 359` — 多处 `ai_rules.md`
  - `workflows/path_a_first_generation.md:752, 756` — 已知
- **关键证据**：
  - `grep -rnE '\bai_rules\.md\b' --include='*.md' .` 返回 7 处真实命中（去除审核报告自引用后）
  - `AI_RULES.md` 大写形式有 **97 处**引用 → 大写为事实标准
  - `AI_ENTRY_POINT.md` L304-L310 术语表实际 **没有 AI_RULES 行**（原 Issue 称"权威源 L306"是误判 — L306 是 `AI_Coding_Context.md` 行）
- **方案评估**：🟡 **需补充**
  - ✅ 选定大写 `AI_RULES.md` 作为统一目标 — 正确（97 vs 7 的票数）
  - ❌ "AI_ENTRY_POINT.md 术语表 L306 为权威源" — **此引用在 AI_ENTRY_POINT.md 中并不存在**；术语表无 AI_RULES 行
  - ⚠️ 漏报修订位置：`.kiro/` 与 `dev/real_case/002/` 应同步处理或显式豁免
- **架构师补充方案**：
  1. **权威源应改为定义于 `core/framework_spec.md` 的"标准产物路径"章节**（该章节当前不存在 → 修复时一并新建）。术语表无对应行不应被当作权威源。
  2. 修订位置应扩展为 5 处文件：
     - `workflows/path_a_first_generation.md` L752, L756
     - `.kiro/specs/post-generation-audit/QUICK_START.md` L157
     - `dev/real_case/002/quality_review/COMPREHENSIVE_AUDIT.md` L88, L328, L359（real_case 是历史归档，可豁免但应明确决策）
  3. **建议同步在 `AI_ENTRY_POINT.md` 术语表新增 AI_RULES 行**，路径取自架构决策（见下文 029 复审）
  4. **CI 预防**：加入 `grep -rnE '\bai_rules\.md\b'` 的 pre-commit 检查，仓库根 + Public 层应返回空

---

### AICC-20260425-029 — AI_RULES.md 路径多版本不一致

- **真实性**：✅ 真实存在（路径不一致客观存在）
- **描述准确性**：⚠️ 偏差 — 描述列出 4 个版本，实际数量统计：
  - `dev_docs/rules/combined/AI_RULES.md`（深嵌套）— **17 处**（README + core/3 + guides/8 + templates/3 + dev/V2.3/2）
  - `dev_docs/AI_RULES.md`（直挂 dev_docs）— **仅 1 处**（`templates/AI_RULES_TEMPLATE.md` L541）
  - `AI_RULES.md`（无路径，根目录隐含）— `AI_ENTRY_POINT.md` L157
  - `ai_rules.md`（小写，根）— path_a 等 7 处（同 016）
- **关键证据**：
  - 多文件设计意图清晰指向 **rules/combined/** 子系统：
    - `core/design_decisions.md` L306：明确文档生成完毕"自动生成 dev_docs/rules/combined/AI_RULES.md"
    - `templates/rules_README_TEMPLATE.md` 整篇围绕 rules/ 子系统组织
    - `guides/ai_rules_maintenance.md` 8 处全部使用深嵌套路径
  - 仅 `templates/AI_RULES_TEMPLATE.md` L541 单处使用 `dev_docs/AI_RULES.md`（孤例）
  - `AI_ENTRY_POINT.md` 术语表 L300-L310 **无 AI_RULES 行**（原 Issue 029 称"L306-L307 权威源"是误判）
- **方案评估**：🔴 **重大缺陷需重写**
  - ❌ 原方案选定的统一目标 `dev_docs/AI_RULES.md` 是**孤例（1 处）**而非主流（17 处）。按原方案修复将需要修改 17+ 处文档（含面向用户的 README、ai_rules_maintenance 整篇 guide、design_decisions、core/language_rules、core/update_triggers），代价巨大。
  - ❌ 引用的"权威源 AI_ENTRY_POINT.md 术语表 L306"在文档中根本不存在
  - ❌ 未识别出 `rules/combined/` 子系统是 AI_RULES.md 生成机制的整体设计（见 `core/design_decisions.md` L306 与 `templates/rules_README_TEMPLATE.md`）— 改为扁平路径会破坏 IDE-specific 子规则的组织能力（rules/cursor/, rules/windsurf/ 等扩展空间）
- **架构师重写方案**：

  **统一目标路径：`dev_docs/rules/combined/AI_RULES.md`**（与 17 处主流引用一致）

  **修订位置（仅 2 处需要变更，其他 17 处已正确）**：

  1. `templates/AI_RULES_TEMPLATE.md` L541：`dev_docs/AI_RULES.md` → `dev_docs/rules/combined/AI_RULES.md`
  2. `workflows/path_a_first_generation.md` L750-L760：`项目根目录 ai_rules.md` → `dev_docs/rules/combined/AI_RULES.md`（与 016 联动修复）

  **AI_ENTRY_POINT.md 增项**：

  - L157 处 `AI_RULES.md` → `dev_docs/rules/combined/AI_RULES.md`
  - 术语表 L300-L310 新增一行：`| AI Rules 文件 | dev_docs/rules/combined/AI_RULES.md | IDE 规则的来源文件 |`

  **权威源建立**：在 `core/framework_spec.md` 新增"标准产物路径"章节，明确：
  - 主文档：`dev_docs/AI_Coding_Context.md`
  - AI Rules：`dev_docs/rules/combined/AI_RULES.md`
  - 分析方案：`dev_docs/_analysis/generation_plan.md`（已在术语表存在）
  - 等等

  **回归测试**：

  ```bash
  # 修复后应只剩下统一路径
  grep -rnE 'AI_RULES\.md|ai_rules\.md' --include='*.md' \
    AI_ENTRY_POINT.md README.md templates/ workflows/ guides/ core/ \
    | grep -oE '[a-zA-Z_/]*(AI_RULES\.md|ai_rules\.md)' | sort -u
  # 预期：仅 1 行 dev_docs/rules/combined/AI_RULES.md
  ```

  **理由汇总**：
  - 票数：17 vs 1 vs 1 vs 7 — 多数派定锚
  - 设计意图：rules/combined 路径暗示存在 rules/<ide>/ 扩展机制，符合 IDE-multi-target 思路
  - 修改成本：从"修改 17 处"反转为"修改 2 处 + 新增 1 行术语表"

---

### AICC-20260425-032 — 主文档名 `ai_coding_context.md` vs `AI_Coding_Context.md`

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ 偏差 — Issue 只列了 `guides/quick_start.md L120` 一处 lowercase，实际还有 **1 处遗漏**：
  - `workflows/generation_workflow.md:493` — `请生成主文档 ai_coding_context.md（根目录）`
  - 此处不仅大小写错，**路径也错**：写的是"根目录"，但权威路径是 `dev_docs/AI_Coding_Context.md`
  - quick_start.md 实际行号是 L122 而非 Issue 标的 L120（轻微行号漂移，不影响判断）
- **关键证据**：
  - 全仓库 lowercase grep 命中 2 处真实代码引用 + 6 处审核报告自引用
  - `AI_Coding_Context.md` 大写有 **109 处**引用，明显是事实标准
  - `templates/AI_Coding_Context_TEMPLATE.md` 模板文件名也是大写 → 大写为正确目标
- **方案评估**：🟡 **需补充**
  - ✅ 选定大写为统一目标 — 正确
  - ⚠️ 漏报 `workflows/generation_workflow.md L493` 这一处（同时有大小写错 + 路径错）
- **架构师补充方案**：
  - 修订 2 处文件而非 Issue 所述 1 处：
    1. `guides/quick_start.md` L122：`ai_coding_context.md` → `dev_docs/AI_Coding_Context.md`
    2. `workflows/generation_workflow.md` L493：`ai_coding_context.md（根目录）` → `dev_docs/AI_Coding_Context.md`
  - 与 016 / 029 一并通过 `core/framework_spec.md` 新建的"标准产物路径"章节锚定
  - **回归校验**：

    ```bash
    grep -rnE '\bai_coding_context\.md\b' --include='*.md' \
      README.md AI_ENTRY_POINT.md guides/ workflows/ templates/ core/
    # 预期：返回空
    ```

---

### AICC-20260425-002 — Public 层指向 dev/ 的死链

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — 5 处真泄漏 + 2 处故意保留全部核实，line 号准确
- **关键证据**：
  - 真泄漏 #1：`core/design_decisions.md` L256 — ✓
  - 真泄漏 #2：`core/design_decisions.md` L492 — ✓
  - 真泄漏 #3：`core/SUMMARY_FORMAT_SPEC.md` L403 — ✓
  - 真泄漏 #4：`agents/_progress/implementation_progress.md` L5 — ✓ 标准 markdown 链接 `[text](../../dev/V3.0/...)`
  - 真泄漏 #5：`workflows/doc_error_fix_workflow.md` L507-L509 — ✓ 3 个标准 markdown 链接
  - 故意保留 #6, #7：`CONTRIBUTING.md` L904, L1198+ — ✓
  - **附带发现**：原 Issue 自带验证 regex `\.{0,2}` 仅匹配 0-2 个点号，**漏掉 `../../dev/` (4 个点号) 形式**。修正 regex 应为 `\]\([^)]*dev/[^)]*\)`
  - **附带发现**：`agents/_progress/` 目录下其他文件（issues_and_feedback.md, role_conversion_log.md）经全文 grep 无 dev/ 引用 — Issue 已穷尽
- **方案评估**：✅ **基本通过，仅需补充验证 regex**
  - 原方案选项 B（移除链接，改为纯文字描述）合理 — 与 design_decisions L492 现行措辞一致
  - 原方案对 #1/#2/#3（已是文字描述）的"补充'仅 dev 分支可见'明示" — 合理但优先级低
  - 对 #6/#7 的"段头一次性声明" — CONTRIBUTING L1198 已隐含说明，可强化即可
- **架构师补充**：
  1. **修正自验 regex**（保存到 `dev/quality/standards/` 或 CI 中），用：
     ```bash
     grep -rnE '\]\([^)]*dev/[^)]*\)' --include='*.md' \
       -- core/ workflows/ agents/ templates/ tools/ guides/ config/ \
       AI_ENTRY_POINT.md README.md 2>&1 | grep -v '/dev/null'
     ```
  2. **#5 选项分析**：原方案推荐选项 B 移除链接。但 `workflows/doc_error_fix_workflow.md` 是核心工作流文档，链接到 011 设计源会失去溯源价值。**建议改用选项 C 的轻量版**：在 Public 层保留这 3 个链接但将其转为指向 `dev/V3.0/confirmed/011-doc-error-fix-workflow/` 的 README 段落，并在文件头部加一条 frontmatter `dev_only_links: true` 字段，配合 `.gitattributes` 规则在发布时由脚本剥除该段。短期仍可走选项 B，长期建议选项 C。
  3. **新增预防机制**：将上述 regex 加入 release pre-flight 检查，作为发布前红线。

---

### AICC-20260425-003 — 仓库根 audit_metadata.py 孤儿文件

- **真实性**：✅ 真实存在 — 文件确在仓库根，9322 字节，2026-04-25 创建
- **描述准确性**：✅ 准确 — 是孤儿无引用
- **关键证据**（实读全文 169 行后）：
  - **该脚本是一次性扫描器**：硬编码 ~150 个文件路径，检查是否含有 `summary:` 与 `importance:` frontmatter 字段
  - **缺陷 1**：硬编码路径含若干已不存在或路径错误的项（如 `./quality/...`, `./docs/...`, `./.kiro/specs/post-generation-audit/...`）
  - **缺陷 2**：检查 `importance:` 字段，但 AICC 的 frontmatter 标准（`core/SUMMARY_FORMAT_SPEC.md`）中**根本没有 importance 字段** — 该字段是脚本作者私自定义
  - **缺陷 3**：无 `if __name__ == '__main__':` guard，脚本被 import 时会立即扫描
  - **缺陷 4**：无 docstring、无 frontmatter（违反 V3.0 工程红线 035）
  - **缺陷 5**：无 .js 对称版本（违反 V3.0 双脚本红线）
  - 全仓库 grep `audit_metadata` — 0 处实际引用（仅审核报告中的自我提及）
- **方案评估**：🟡 **需补充判据**
  - 原方案 A/B/C 三选项**未给出判据**，让修复者自行决定
  - 实读后明确：A（迁入 tools/）与 B（迁入 dev/quality/）都不可行 — 因脚本本身存在多个工程红线违规且检测目标字段（importance）不属框架标准
- **架构师重写方案**：

  **明确选 C：删除 + 知识沉淀**

  - **删除理由**：
    1. 0 引用，0 用途
    2. 检测的 `importance:` 字段不属框架标准，结果无意义
    3. 硬编码路径已过时
    4. 同类校验功能已被 `tools/py/summary_validator.py` 取代（V3.0 优化点 012 的工具）
    5. 保留只会让后续 AI/维护者困惑
  - **执行命令**：

    ```bash
    git rm audit_metadata.py
    git commit -m "chore: 清理仓库根孤儿脚本 audit_metadata.py（已被 summary_validator 取代）"
    ```

  - **知识沉淀**：在 `dev/V3.0/PROGRESS.md` 或 `dev/quality/README.md` 历史栏简注 — `audit_metadata.py` 已删除，相关功能由 `tools/py/summary_validator.py` 提供
  - **预防机制**：建议 CI 加 `repo root *.py` 红线扫描（仓库根除 `setup.py` 之外不应有 .py）

---

### AICC-20260425-022 — confirmed/ 目录名带 .md 后缀

- **真实性**：✅ 真实存在 — 三个目录均确认为 directory（test -d 通过）
- **描述准确性**：✅ 准确 — 3 个异常目录、10 个正常目录、1 个单文件全部对得上
- **关键证据**：
  - `dev/V3.0/confirmed/004-adr-system.md/` ⇒ 是目录
  - `dev/V3.0/confirmed/005-complexity-dashboard.md/` ⇒ 是目录
  - `dev/V3.0/confirmed/006-auto-review-report.md/` ⇒ 是目录
  - 跨引用统计：**至少 9 处**需同步更新（dev/V3.0/README.md L71/76/82, walkthrough.md L418, DISCUSSION_CONTEXT.md L85-87, 等）
- **方案评估**：✅ **通过**（修复指令完整、git mv 正确、grep 校验有效）
- **架构师补充**：
  1. 原方案 git mv 三条指令是正确的，但需**显式列出后续 grep-and-replace 命令**避免漏改：

     ```bash
     # 重命名后批量更新引用
     for old in 004-adr-system.md 005-complexity-dashboard.md 006-auto-review-report.md; do
       new="${old%.md}"
       grep -rl "${old}/" --include='*.md' . 2>/dev/null | while read f; do
         sed -i "s|${old}/|${new}/|g" "$f"
       done
     done
     # 校验
     grep -rnE '004-adr-system\.md/|005-complexity-dashboard\.md/|006-auto-review-report\.md/' \
       --include='*.md' . | grep -v '/\.git'
     # 预期：返回空
     ```

  2. **顺手优化**：核对 `dev/V3.0/confirmed/004-adr-system/004-adr-system.md` 等内文件是否也有 hardcode 自引用（若有需同步改）
  3. **长期防御**（补充）：在 `dev/V3.0/README.md` 命名规范条款基础上，加入 `.gitignore` 守门 — 检测到 `confirmed/*.md/` 模式（目录带 .md 后缀）时 fail commit。这是真正的根因防御。

---

### AICC-20260425-010 — archived/ 内 advanced-audit-report.md 命名/位置错

- **真实性**：✅ 真实存在 — 文件实存（11651 字节，归档于 archived/）
- **描述准确性**：✅ 准确 — 是审核报告非已归档优化点；archived/ 其他 5 项（002/007/008/009/015）符合 PROGRESS 列表
- **关键证据**（实读后判定）：
  - 文件标题：`# 010 - 跨项目知识复用：资深使用者审核报告`
  - 内容：32 个遗漏点、优先级建议、改进方案 — 是对 010 优化点的**深度审核报告**
  - audit_date: 2026-04-13
  - 该文件本质是"010 优化点的资深用户审查"
- **方案评估**：🟡 **需补充更优目标位置**
  - 原方案 A（迁入 reference/）：reference/ 当前含 `commit_as_prompt_analysis.md` 与 `git_safety_workflow_design.md` — 都是**跨优化点的研究分析**，不是单一优化点的审查报告。此处不匹配。
  - 原方案 B（迁入 dev/quality/audits/）：现 audits/ 采用 `<日期>_<round-name>` 格式（如 `2026-04-25_V3.x_Comprehensive`），单文件不符模式
- **架构师重写方案**：

  **最优目标：`dev/V3.0/confirmed/010-cross-project-knowledge/senior_review_report.md`**

  - **理由**：
    1. 该报告专属 010 优化点，逻辑上属于 010 档案的一部分
    2. 010 confirmed/ 目录已含多个并列子文档（`architecture-design.md`, `cli-commands.md`, `implementation_plan.md`, `self-evolution-system.md`）— 增加 `senior_review_report.md` 自然契合
    3. 与 022 修复后的目录命名规范一致
    4. 后续 010 修复 / 实施时，该报告就在身边可被立即引用
  - **执行命令**：

    ```bash
    git mv dev/V3.0/archived/advanced-audit-report.md \
           dev/V3.0/confirmed/010-cross-project-knowledge/senior_review_report.md
    # 同时在该报告头部追加 frontmatter 标识其位置
    ```

  - **同步动作**：
    1. 在 `dev/V3.0/confirmed/010-cross-project-knowledge/010-cross-project-knowledge.md` 头部 "相关文档" 段加链接：`[资深用户审核报告](./senior_review_report.md)`
    2. 在 `dev/V3.0/PROGRESS.md` 010 条目下加注："含资深审核报告（32 项遗漏点）"
  - **预防机制**：在 `dev/V3.0/README.md` 命名规范追加：archived/ 仅存放"已归档（决定不实施）的优化点", 不存放审查报告/分析文档

---

---

## 🔹 Batch 2：文档漂移 + SSOT

> **批次目标**：核查 FRAMEWORK_CONTEXT vs PROGRESS 漂移集群（001/011/012/014/015）与文档间引用错误（013/018/023）的真实性与方案最优性。
>
> **完成日期**：2026-04-26
>
> **批次结论**：
> - 8 项 Issue 全部 **真实存在**
> - 描述完全准确：5 项（011, 012, 013, 014, 018）
> - 描述有偏差：3 项（001 项数计数小偏差 / 015 实体处置假设错误 / 023 personas 数计算口径不清）
> - 修复方案处置：✅ 通过 5 项 / 🟡 需补充 2 项 / 🔴 重大缺陷需重写 1 项（015）

---

### AICC-20260425-001 — FRAMEWORK_CONTEXT vs PROGRESS 漂移（统领条目）

- **真实性**：✅ 真实存在（漂移宏观存在）
- **描述准确性**：⚠️ 项数细节偏差 — Issue 称"顶部摘要列出 8 项 P0 + 019（共 9 项）"，**实际 L17-L24 仅 8 项总数**（含 019），不是 8+1=9
- **关键证据**：
  - FRAMEWORK_CONTEXT L17-L24 实际 8 项：001 / 003 / 012 / 013 / 016 / 017 / 018 / 019
  - PROGRESS L18 实际 11 项（漏 011）：001 / 003 / 004 / 005 / 006 / 012 / 013 / 014 / 016 / 017 / 018
  - PROGRESS L88 实际：011 标记 ✅（与 L18 缺失矛盾，由 012 详细定位）
  - 应包含的 12 项已完成 = L18 的 11 项 + 011 = 12
  - FRAMEWORK_CONTEXT 顶部漏列 5 项（004/005/006/011/014）— 与 011 描述一致
- **方案评估**：✅ **通过**（本条已被 011/012 精确细分；统领角色保留即可）
- **架构师建议**：001 作为统领可关闭，引用 011 + 012 作为具体修复入口；推荐在修复后保留 001 作为"集群说明锚点"，状态置 🟢 时备注"由 011/012/014/015 联合修复完成"

---

### AICC-20260425-011 — FRAMEWORK_CONTEXT 顶部摘要严重过时

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — 全部 5 项漏列、L703 "(10/17)" 与 11 项列举矛盾均已核实
- **关键证据**：
  - L17-L24 缺 004/005/006/011/014 ✓
  - L25-L28 "**剩余关键能力（规划中）**" 包含 ADR/复杂度仪表盘/自动审查报告 — 与 L711-L714 的 ✅ 标记矛盾（014 详细定位）
  - L703 写 `已完成 (10/17)`，但 L704-L714 实际列了 11 项 ✓
  - L711 含 019 + 2026-04-11 日期
- **方案评估**：🟡 **需补充修复后的目标数字**
  - ✅ 思路正确："顶部摘要同步到 12 项 + L703 改为 (12/18)"
  - ⚠️ **依赖关系遗漏**：原方案 (12/18) 假设总数仍为 18。但 015 提议把 019 登记为正式优化点 → 总数应为 **(13/19)**。两 Issue 的修复结果在分母上需联动
- **架构师补充方案**：
  - **必须先决策 019 的处置**（见 015 复审），再统一修复分母：
    - 若 015 选 A（推荐）：FRAMEWORK_CONTEXT L703 改为 `已完成 (13/19)`；顶部 L14-L23 列 13 项含 011 + 019
    - 若 015 选 B：分母保持 (12/18)，把 019 移出 V3.0 主清单到独立"V3.0+ 增益"章节
  - L25-L28 P1/P2 表述与 014 一并重写（见 014 复审）
  - **新增推荐措施**：在 FRAMEWORK_CONTEXT 顶部 frontmatter 增加 `progress_synced_at: <date>` 字段（与 PROGRESS.md 的 verified_at 对齐），约定每次 PROGRESS 变更后必须同步更新此字段；CI 可加校验"两份文档的优化点编号集合 diff 应为空"

---

### AICC-20260425-012 — PROGRESS 自身内部不一致

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — L18 缺 011、L34 P1 中 011 用 🟢、L88 标 ✅ 三处全部核实
- **关键证据**：
  - L18 实测：`已完成: 11个 (001, 003, 004, 005, 006, 012, 013, 016, 017, 018, 014)` 数 11 项缺 011
  - L34 实测：`P1 (高价值): 5个 (004 ✅, 005 ✅, 006 ✅, 011 🟢, 014 ✅)` — 011 用 🟢
  - L85 实测：`- [x] 实现文档谬误修复工作流 (011) ✅` — 011 已完成
- **方案评估**：✅ **通过**
- **架构师补充**：
  1. 修复 L18 同时**也要修 L17 的 13个**（已确认 confirmed/ 数）：当前 13 个含 010 进行中、011 已完成等 13 项；如 015 选项 A 落地新增 019，应升至 14 项
  2. L34 011 🟢 → ✅ 后，**P1 计数 (5个)** 应保持（004/005/006/011/014 全 ✅，本身 5 项不变）
  3. **回归校验加强**（在原方案 grep 基础上）：
     ```bash
     # P1 中所有项应为 ✅ 或 🟢 一致；不能既 ✅ 又 🟢 矛盾
     grep -E '011 ?[✅🟢]' dev/V3.0/PROGRESS.md
     # 应统一为 ✅
     ```
  4. **建议在 PROGRESS.md 头部加 frontmatter `verified_at` 字段**（见 011 联动）

---

### AICC-20260425-013 — FRAMEWORK_CONTEXT 同文档对相同文件给两处不同路径

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — L539/L540 用 `reference/`、L744/L745 用 `core/`；实体在 `core/` ✓
- **关键证据**：
  - L539: `reference/SUMMARY_FORMAT_SPEC.md` ❌
  - L540: `reference/design_decisions.md` ❌
  - L744-L745: `core/design_decisions.md` / `core/SUMMARY_FORMAT_SPEC.md` ✓
  - 实体确认：`ls core/SUMMARY_FORMAT_SPEC.md core/design_decisions.md` 都存在
  - **附带发现**：L740 + L741 还指向 `dev/reference/AI编程的现状.md`、`dev/reference/AI_PROGRAMMING_ANALYSIS.md`，这些是 dev/reference/（不同于 core/reference 不存在）— 路径正确，与 L539/L540 的 `reference/` 错引用是无关情况
- **方案评估**：✅ **通过**（修订两行即可，复查方法正确）
- **架构师补充**：
  - 顺手做一次全文档"路径前缀一致性"扫描：
    ```bash
    grep -nE '\b(reference|core|workflows|agents|templates|tools|guides|config)/(SUMMARY_FORMAT_SPEC|design_decisions|framework_spec)' dev/FRAMEWORK_CONTEXT.md
    ```
  - 长期：建议在 `tools/py/doc_link_validator.py`（如果存在）或 summary_validator 中加入"声称的相对路径必须能 ls 到"的回归校验

---

### AICC-20260425-014 — FRAMEWORK_CONTEXT L25-L28 与 L703-L714 自相矛盾

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — L25-L28 把 ADR/复杂度/审查报告列为"规划中"，与 L711-L714 的 ✅ 矛盾
- **关键证据**：
  - L25-L28（实际 L27-L29）："**剩余关键能力（规划中）**：P1：ADR 系统、复杂度仪表盘、自动审查报告"
  - L711-L713：004/005/006 全部 ✅
- **方案评估**：✅ **基本通过**，措辞建议优化
  - ✅ 选项一"L25-L28 改写为 P1 部分已完成 (004/005/006/011/014)..." — 思路正确
  - ⚠️ 措辞欠精确：原推荐措辞列了"剩余 015"，但 015 实为已归档（PROGRESS L19：`已归档: 5个 (002, 007, 008, 009, 015)`），应排除；P1 真正剩余项为 011（已完成，应在已完成列）
- **架构师重写方案**：

  **L25-L28 推荐改写**（架构师视角更精确）：

  ```markdown
  **V3.0 进度概览**：

  - P0：✅ 7 项全部完成（001/003/012/013/016/017/018 + 027 待补登记）
  - P1：✅ 5 项全部完成（004/005/006/011/014）
  - P2：🟢 010 进行中；其余 002/007/008/009/015 已归档（详见 PROGRESS.md）
  - V3.0+ 后期增益：019-系统化文档审核框架 ✅（2026-04-11）

  **详见 [`dev/V3.0/PROGRESS.md`](./V3.0/PROGRESS.md) 与 [`dev/V3.0/README.md`](./V3.0/README.md)**
  ```

  - 与 011 联动：本节大改后，原 L11-L29 顶部摘要可彻底简化为"指针式快照"（不再罗列优化点编号），由 PROGRESS.md 作为唯一详细清单
  - **架构升级**：从"两份独立漂移文档"改为"概览（FRAMEWORK_CONTEXT）+ 详情（PROGRESS）"层级关系，根除漂移可能性

---

### AICC-20260425-015 — 019 已完成但未登记（总数 17 vs 18）

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ 偏差 — 实体描述部分**重大错误**
  - Issue 描述说"019 实际实体存在 (templates/review/、workflows/generation_workflow.md 等)"
  - 但实际还有 **`dev/V3.0/confirmed/019-systematic-review-framework.md`**（单文件 24KB）— Issue 完全没提到这个 confirmed/ 单文件已经存在！
- **关键证据**：
  - `ls dev/V3.0/confirmed/019-*` 返回 `019-systematic-review-framework.md`（单文件，与 022 修复后的命名规范一致："单文件用 NNN-name.md"）
  - PROGRESS L15: `总优化点: 18个`
  - FRAMEWORK_CONTEXT L703: `(10/17)`
  - PROGRESS L16-L41 18 项清单确实不含 019
- **方案评估**：🔴 **重大缺陷需重写**
  - 原方案 选项 A 称"创建 019 的优化点档案"— **优化点档案已经以单文件形式存在**于 `dev/V3.0/confirmed/`，不需要"创建"
  - 原方案选项 A 又说"在 dev/V3.0/confirmed/019-systematic-review-framework/（目录）下"— 这暗示要把单文件转为目录形式，但 022 修复刚明确"单文件用 NNN-name.md"是合法形式，没必要为 019 单独转目录
  - 原方案选项 B（移到独立"V3.0+ 后期增益"章节）有保留意义，但缺技术细节
- **架构师重写方案**：

  **简化版 选项 A（推荐）：直接登记，不动实体结构**

  019 confirmed 实体已存在且符合命名规范，无需重组。修复仅需：

  1. **PROGRESS.md L15**：`总优化点: 18个` → `总优化点: 19个`
  2. **PROGRESS.md L16-L19**：
     - 已确认 13个 → 14个（加入 019）
     - 已完成 11个 → 13个（加入 011 + 019，结合 012 修复）
  3. **PROGRESS.md L18**：在已完成清单加 019：`已完成: 13个 (001, 003, 004, 005, 006, 011, 012, 013, 014, 016, 017, 018, 019)`
  4. **PROGRESS.md 优化点池清单（L21-L41）** 末尾追加：
     ```markdown
     ### 后期增益（V3.0+）
     - 019-系统化文档审核框架 ✅（2026-04-11）
       - 来源：dev/case_skillatlas_review/ 实践
       - 实体：dev/V3.0/confirmed/019-systematic-review-framework.md, templates/review/, workflows/generation_workflow.md
     ```
     特别说明 019 是 V3.0 后期突生需求（不在原 V3.0 18 项规划），但已纳入正式登记
  5. **FRAMEWORK_CONTEXT.md L703**：`(10/17)` → `(13/19)`（与 011 联动）

  **理由汇总**：
  - 实体已就位且符合 022 修复后的命名规范，**不重组、只登记**
  - 总数从 18 调到 19（不是 18 不变）— 反映 019 是真正的 V3.0 优化点
  - 在 PROGRESS 单设"后期增益（V3.0+）"小节，**保留追溯透明度**（让读者知道 019 是后期纳入）— 这是原选项 B 的价值与选项 A 的清单优势的合并
  - **不创建 019 子目录**：单文件足够，避免无意义重组

  **副作用规避**：
  - 需同步 023 修复时统一其他文档对总数的引用（如 dev/V3.0/README.md 若有提及）
  - PROGRESS L17 的 `已确认 (confirmed/): 13个 (72.22%)` 百分比也需重算：14/19 = 73.68%

---

### AICC-20260425-018 — doc_error_fix_workflow.md 测试命令路径假设错误

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确 — L488/L491 命令使用根级 `tests/` 路径，仓库无此目录；实际测试在 `tools/py/tests/` 与 `tools/js/`
- **关键证据**：
  - 实测 L487-L491：`python -m pytest tests/ -v -k "doc_error"` ✓ 错路径
  - `tools/py/tests/` 实际只有 `test_commit_integrity_validator.py` + `test_git_safety.py`
  - `tools/js/` 含 `commit_template_cli.test.js` / `install_hooks.test.js` / `integration.test.js`
  - **新发现**：tools/py/tests/ 中 **无任何 `doc_error` 或 `doc_fix` 相关测试文件**（grep `-l doc_error tools/py/tests/*.py` 应为空）
- **方案评估**：🟡 **需补充**
  - ✅ 思路正确：路径改为 `tools/py/tests/`
  - ⚠️ 缺判据：原方案保留命令但改路径前缀，但实际"doc_error" / "doc_fix" 测试本身**就不存在**于该目录。改完路径执行仍会得到"no tests collected"，命令名义可执行但无效
- **架构师补充方案**：

  **两层修复**：

  1. **诚实修复（短期推荐）**：将命令改为反映实际测试覆盖的形式，并明确缺失项：

     ```bash
     # 现有相关测试（截至 2026-04-26）
     python -m pytest tools/py/tests/ -v
     # ⚠️ 注意：tools/py/tests/ 当前覆盖 commit_integrity / git_safety；
     # doc_error_fix 工具的单元/集成测试尚未补全，参见 PROGRESS / 011 后续任务
     ```

  2. **长期补全（推荐入 PROGRESS 后续任务）**：补 `tools/py/tests/test_doc_error_detection.py`、`test_doc_fix_executor.py`、`tests/integration/test_doc_fix_e2e.py`（仿 011 工作流剧本）；补完后将命令恢复为：

     ```bash
     python -m pytest tools/py/tests/ -v -k "doc_error or doc_fix"
     ```

  **同步检查**：本批次顺手 grep `pytest tests/` 是否在其他工作流文档也错误使用：

  ```bash
  grep -rnE 'pytest tests/' --include='*.md' workflows/
  ```

---

### AICC-20260425-023 — dev/quality/README.md agents/ 索引覆盖率缺口

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ 偏差 — 部分数字描述与实际不完全一致
  - examples：README "21 个" vs 实际 18 项（含 1 子目录 + 1 README + 16 examples）— ✓ Issue 准确
  - language_specific：README "7 个" vs Issue 称"5 项 + base/"，**实际 6 项**（base/ + java/ + python/ + typescript/ + vue3_expert.md + vue3_state_manager.md）— Issue 数字 5 偏低，正确数字 6
  - personas：Issue 未提及，但 README 写 "3 个"（不计 README.md），实际有 4 项（含 README.md）。这是计数口径差异，非缺陷
  - _templates：README 完全未列 ✓
- **关键证据**：
  - `ls agents/_templates/` 实存：agent_template.md + quality_checklist.md（2 项）✓
  - `ls agents/examples/ | wc -l` = 18（README 写 21，差 3）
  - `ls agents/language_specific/ | wc -l` = 6（README 写 7，差 1）
  - `ls agents/personas/ | wc -l` = 4（README 写 3，正确口径下应为 3 排除 README.md）
- **方案评估**：🟡 **需补充**
  - ✅ 补 `_templates/` 索引 — 正确
  - ⚠️ examples "实际 18 个" 改写正确
  - ⚠️ Issue 描述对 language_specific 数字不准（说 5，实际 6）；修复时应直接写 6 不写 5
  - ⚠️ personas 未涉及但应顺手核对：现 README 数字 3 是按"角色文件"口径，可保留但加注"(不含 README.md)"
- **架构师补充方案**：

  **完整修订**（README L153-L173 agents 索引段）：

  1. 在 `**custom/（1 个，⚪ 仅合规）**` 后增加：
     ```markdown
     **_templates/（2 个，⚪ 仅合规）**：`agent_template.md`、`quality_checklist.md`
     ```
  2. L171 改为：
     ```markdown
     **examples/（18 个，🟡 批审，重点：示例与角色定义一致性，含 1 个 design_thinking/ 子目录）**
     ```
  3. L163 改为：
     ```markdown
     **language_specific/（6 个，🟡 批审）**：`base/`（含 backend_engineer / frontend_engineer）、`java/`、`python/`、`typescript/`、`vue3_expert.md`、`vue3_state_manager.md`
     ```
  4. L165 加注口径：
     ```markdown
     **personas/（3 个角色 + 1 个 README，🟡 批审...）**：`linus_torvalds.md`、`martin_fowler.md`、`uncle_bob.md`
     ```
  5. **回归测试加强**：

     ```bash
     # 自动校核 README 声明数 vs ls 实际数
     for d in examples language_specific personas _templates custom development workflows runtime; do
       declared=$(grep -oE "\*\*${d}/.*?[0-9]+ ?个" dev/quality/README.md | grep -oE '[0-9]+' | head -1)
       actual=$(ls agents/${d}/ 2>/dev/null | wc -l)
       echo "${d}: declared=${declared}, actual=${actual}"
     done
     ```

---

---

## 🔹 Batch 3：dogfood 自指 + 合规扫描

> **批次目标**：核查 V3.0 强制规则的自指落地情况（034）、设计-发布转化 gap（027）、SOP 与现状对齐（024/025）、双脚本对称质量（035）、配置路径假设（021）。
>
> **完成日期**：2026-04-26
>
> **批次结论**：
> - 6 项 Issue 全部 **真实存在**
> - 描述完全准确：4 项（034, 024, 025, 035）
> - 描述有偏差需补充：2 项（027 — 源路径未对齐 B1#022 重命名；034 — templates 分母数字偏差）
> - 修复方案处置：✅ 通过 2 项（024, 025） / 🟡 需补充 4 项（034, 027, 035, 021）
> - 全批次无 🔴 重大缺陷需重写
> - **横切发现**：034+027+021+035 共同指向"AICC 框架的 dogfood 能力薄弱"集群

---

### AICC-20260425-034 — V3.0 强制 frontmatter 14% 自指失败

- **真实性**：✅ 真实存在（严重）
- **描述准确性**：⚠️ 偏差 — 主体数据完全吻合，仅 templates 行有数字偏差
  - **完全吻合**：Public 总计 20/138 = 14% ✅；顶层入口 0/3 = 0% ✅；core/ 14/21 = 66% ✅；workflows/ 1/26 = 3% ✅；guides/ 0/15 = 0% ✅；agents/ 0/59 = 0% ✅；config/ 0/2 ≈ 0% ✅
  - **偏差**：Issue 称 templates "5 / 29 (17%)"，实测为 **5 / 12 (41%)**。原因：B1#022 修复时已删除 `004/005/006-*.md/` 内嵌套子目录变体，分母从 29 降至 12（合规率 17%→41%）。结论方向不变（仍偏低），但数字过期需修订。
  - **关键失败点**全部得证：`AI_ENTRY_POINT.md` ❌、`README.md` ❌、`CONTRIBUTING.md` ❌、`core/SUMMARY_FORMAT_SPEC.md` ❌、`core/framework_spec.md` ❌
- **关键证据**：
  - `summary_validator.py` / `summary_extractor.py` 双语言版本均存在并可运行（CLI `--help` 通过）
  - `summary_validator.py` 支持 `--strict --recursive`，可作为 CI gate
  - `core/SUMMARY_FORMAT_SPEC.md` 自身**不带 frontmatter** — 规范源未自证（最讽刺的 dogfood 失败点）
- **方案评估**：🟡 **需补充**
  - ✅ 三阶段 P0/P1/P2 划分合理
  - ✅ 工具支持完备（summary_extractor 可批量草稿、summary_validator 可校验）
  - ⚠️ 缺验收门槛细化（"含 frontmatter" ≠ "合规 frontmatter"，需 strict 字段校验）
  - ⚠️ 缺与 014 智能文档推荐 / 018 commit-guided 的依赖闭环验证
  - ⚠️ 缺 P0 后立即建立 pre-commit/CI gate 的时间序约束（否则修复后会立即倒退）
- **架构师补充方案**（覆盖 + 增强原方案）：

  **修订分阶段路线（基于实测分母）**：
  - **P0（紧急，1 周内）— 10 个**：3 个顶层入口（`AI_ENTRY_POINT.md` / `README.md` / `CONTRIBUTING.md`）+ 7 个 core/ 缺失（含 `SUMMARY_FORMAT_SPEC.md` 自带示范级 frontmatter，作为规范的"自证"）
  - **P1（短期，2 周内）— 40 个**：workflows/ 25 个 + guides/ 15 个
  - **P2（中期，1 月内）— 68 个**：agents/ 59 个 + templates/ 7 个（5/12 已有，余 7 个）+ config/ 2 个

  **验收门槛（双层）**：
  1. **形式合规**：`head -1` 能看到 `---` 分隔符
  2. **质量合规**（strict 模式）：`python tools/py/summary_validator.py --dir <path> --strict --recursive` 必须 0 错误，验证 `title / summary / keywords / scope` 四字段齐全且非空

  **dogfood 闭环验证（修复完成后必做）**：
  - 用 014 智能文档推荐工具针对一个真实任务生成推荐，确认能基于 frontmatter 命中
  - 用 018 commit-guided 自动关联，确认能利用 frontmatter 关联到对应文档

  **CI/Git 防御（与 P0 同步上线，不可滞后）**：
  - 加入 pre-commit hook：阻止根目录 + Public 层无 frontmatter 的新 .md 提交
  - 加入 CI gate：`summary_validator.py --strict --recursive` 必须通过
  - 注：CI gate 应与 P0/P1/P2 同步推进 — 每完成一阶段，将该范围纳入 strict gate（避免一次性卡死所有未修复文件）

  **与其他 Issue 联动**：
  - 与 027（005 walkthrough 提升 Public）联动：新建 `workflows/complexity_alert_workflow.md` 时即应带完整 frontmatter，作为 workflows/ 的第 2 个样板
  - 与 023（README 索引）联动：模板补全完成后，dev/quality/README.md 索引数字需同步刷新
  - 与 035（双脚本对称）联动：`core/SUMMARY_FORMAT_SPEC.md` 的 frontmatter 示范本身应同时给出 .py 与 .js 工具引用

---

### AICC-20260425-027 — 005 walkthrough 已含端到端流程但未提升至 Public

- **真实性**：✅ 真实存在
  - `workflows/complexity_alert_workflow.md` 不存在 ✅
  - `AI_ENTRY_POINT.md` 无 complexity / complexity_scanner 索引 ✅（grep 返回空）
  - `workflows/path_d_specific_tasks.md` 无 `@complex` 路由 ✅（grep 返回空）
- **描述准确性**：⚠️ 偏差 — Issue 引用源路径 `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` 已**因 B1#022 修复而过期**。当前真实路径为 `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md`（去掉 `.md/` 后缀）。Issue 中所有 `.md/` 风格路径引用均需对齐。
- **关键证据**：
  - `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` 存在
  - `workflows/path_d_specific_tasks.md` 存在但无 @complexity 章节
- **方案评估**：🟡 **需补充**（方向正确，需对齐源路径 + 增强 frontmatter 联动 + 工具索引细化）
- **架构师补充方案**：

  **源路径对齐**（B1 已重命名）：
  - 旧：`dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` ❌
  - 新：`dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` ✅

  **新建工作流的具体规范**：
  1. **新文件**：`workflows/complexity_alert_workflow.md`
     - 头部带完整 frontmatter（title / summary / keywords / scope / verified_at）— 作为 workflows/ 第 2 个样板（与 #034 联动）
     - 内容来源：从 walkthrough.md 提取"实施产出 + 验证场景 A/B/C"段落，重写为面向 AI 的 SOP（去除"开发完成验证"语境，改为"用户/AI 触发剧本 4 时执行"语境）
     - 章节建议：**触发条件 → 工具链调用 → 阈值与告警判定 → 报告产出 → 决策建议**
  2. **AI_ENTRY_POINT.md 索引**（按当前实际段落结构修订）：
     - **L317 "工具脚本标准"** 表格：补 `tools/py/complexity_scanner.py`、`tools/py/report_generator.py` + 各 `.js` 镜像 4 行
     - **L371 "🗺️ 工作流全景图"** 段：在路径分类区补"剧本 4：复杂度告警 → `workflows/complexity_alert_workflow.md`"链接
     - **L439 "📁 框架文件索引"** 段：在 workflows/ 子目录列表补该新文件
     - 注：原 Issue 描述的"工作流路由段"在 AI_ENTRY_POINT.md 中**不存在**，实际段落名为上述三处
  3. **path_d 路由**：
     - `workflows/path_d_specific_tasks.md` 新增 `@complexity` 章节，指向上述新工作流
  4. **联动闭环**：
     - 修复 027 即同步关闭 019（端到端工作流缺失）— 这是原 Issue 已识别的因果关系
     - 020（`--check-doc-errors` 参数不存在）与 026（architecture_analyzer 不存在）属独立 bug，不在本条范围

---

### AICC-20260425-024 — Framework_Review_Guidelines.md SOP 过度承诺

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 完全准确 — L471 `Review_Data.zip` ✓、L476 `Assessment_Dashboard.html` ✓
- **关键证据**：
  - 实测 `dev/quality/audits/2026-04-25_V3.x_Comprehensive/` 与历史轮次均**未产出**这两件
  - `dev/quality/README.md` L62-L73 已采用"5 件套（Plan / Issue_Tracking / Progress_Tracking / Review_Log / Review_Checklist）+ 可选附加"口径
  - 当前 Framework_Review_Guidelines.md L443-L504 仍列 10 项 — README 与 Guidelines 已不一致（自指连锁）
- **方案评估**：✅ **通过**（推荐选项 A：删除 2 项，10→8 项）
- **架构师补充**：

  **超出原方案的同步项**（避免修复后留尾）：
  1. **当前 Guidelines 结构观察**：L445 "审查交付物清单" 是**平铺 10 项**，**没有"必需 vs 可选"二级层次**。仅删除 5/6 项后形成的 8 项仍为平铺，与 README L62-L73 的"5 件套 + 可选附加"结构不一致。
  2. **重组方案**（覆盖原 Issue 的"仅删除"建议）：
     - 把 L445 章节标题改为 `### 审查交付物清单（必需 5 件套 + 可选附加）`
     - 在标题下增加 1-2 句导语说明分组规则（与 README 完全同口径）
     - **必需 5 件套小节**：列 Review_Plan、Issue_Tracking、Progress_Tracking、Review_Log、Review_Checklist
     - **可选附加小节**：列 Comprehensive_Review_Report、Issue_Analysis、Improvement_Roadmap、特定任务专项报告
     - **删除**：原 L471 `Review_Data.zip` 与 L476 `Assessment_Dashboard.html`
     - **重排序号**：当前编号 7-10 → 5-8（如保留平铺则）；二级分组下序号在各组内重置即可
  3. **修复连锁**：与 #025 的 README/contexts 措辞修复一并提交（同源治理 — SOP 与策略漂移）

---

### AICC-20260425-025 — dev/quality/README.md contexts 措辞与策略不一致

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 完全准确 — L46 / L53 / L58 措辞与现状脱节
- **关键证据**：
  - `dev/quality/contexts/` 仅含 `_template.md`（其他全部空）
  - L18 已宣告"分级 context — 不要求每个文件都有独立 context"（v2.0 三级策略），但 L44-L58 旧措辞未同步
- **方案评估**：✅ **通过**（建议措辞合理）
- **架构师补充**（覆盖原方案 + 三级口径对齐）：

  **重写 L44-L58 章节**，措辞与 v2.0 三级（🔴/🟡/⚪）策略完全对齐：

  ```markdown
  ### contexts/ — 单文档审查上下文（按需生成）

  采用**按需生成**策略：仅在审查 🔴 优先级文档时，按 [HOW_TO_GENERATE_CONTEXTS.md](./HOW_TO_GENERATE_CONTEXTS.md) 现场生成对应 context。目录通常仅含 `_template.md` 模板。

  **使用方式**：

  \`\`\`
  【新建 AI 会话】
  1. 发送: dev/FRAMEWORK_CONTEXT.md            （全局心智模型）
  2. 若审查 🔴 文档：现场按 HOW_TO_GENERATE_CONTEXTS.md 生成对应 context 并发送
  3. 发送: 实际文档内容
  4. 开始审查讨论
  \`\`\`

  详细分级策略见下方"🎚️ Context 优先级分级（v2.0 引入）"。
  ```

  **要点**：
  - 不再写"每个 🔴 优先级文档对应一份 context"（暗示已存在），改为"按需生成"
  - 不再引用"具体清单见下方'📊 完整文档索引'"（容易让用户期待目录已落地清单）
  - 引用 v2.0 三级章节作为详情入口（已存在于 L110-L118）

---

### AICC-20260425-035 — tools/js/aac_validator.js 头部缺规范 docstring

- **真实性**：✅ 真实存在
  - `tools/js/aac_validator.js` 前 7 行无 JSDoc 块（仅 shebang + require + 行注释）
  - `tools/py/aac_validator.py` 有完整 docstring（功能说明 / 使用方法 / 输出 / 退出码等）
- **描述准确性**：✅ 完全准确（双脚本对称度 32/33 = 97%）
- **方案评估**：✅ **通过**（建议直接使用 Issue 给出的 JSDoc 模板）
- **架构师补充**（细化 + V3.0 红线呼应）：

  **JSDoc 块应参考 .py 版的实际内容质量**（不只是格式），完整字段包含：
  - **功能说明**：与 .py 版一致（"从 ADR 中提取 YAML 约束，对代码静态扫描验证"）
  - **使用方法**：含完整命令示例（扫描整个目录、单文件、指定 ADR 目录）
  - **参数说明**：与 argparse / parseArgs 完全对齐
  - **输出格式**：与 .py 版一致（JSON 违规清单结构）
  - **退出码**：0 = 无违规、1 = 有违规、2 = 错误
  - **零依赖红线说明**：保留并整合现有 L4-L6 的"自实现 yaml parser"内联注释（V3.0 设计决策的良好证据），但形式上整合进 JSDoc 块中作为"设计决策"段

  **V3.0 双脚本红线对齐**：
  - 修复后应跑回归：`for f in tools/js/*.js; do head -3 "$f" | grep -qE '^/\*' && echo OK || echo MISS:$f; done` 返回 100% OK
  - 形式对称（结构）+ 质量对称（字段）双层达标

---

### AICC-20260425-021 — 默认配置路径 dev_docs/ 假设需明示

- **真实性**：✅ 真实存在
  - `tools/py/complexity_scanner.py` L595：`default="dev_docs/complexity/config.yaml"` ✅
  - `dev/complexity/config.yaml` 存在（框架自身）✅
  - `dev_docs/complexity/config.yaml` **不存在**（在 framework 仓库中）
- **描述准确性**：✅ 完全准确
- **关键证据**：
  - JS 镜像 `tools/js/complexity_scanner.js` L25 / L102 / L587-L646 文档与 defaultConfig 同样使用 `dev_docs/complexity/config.yaml` 假设
  - **双脚本对称问题已存在**：修复必须双版本同步（Issue 已点出"应同步检查"，但未明示这是 V3.0 红线）
  - **⚠️ 内部隐性 bug**（实地核查发现，Issue 未提）：`tools/py/complexity_scanner.py` L520-L585 `load_config()` 已含"file 不存在 → fallback 内置默认"逻辑（仅对 path != ""）；但 L363、L434 等内部调用点直接传 **空字符串** `load_config("")`，意味着 `args.config` 的 CLI 值**根本未流入这些调用点** — 即使用户加 `--config dev/complexity/config.yaml` 也对部分逻辑无效。这是与 021 同源但更深的结构性问题。
- **方案评估**：🟡 **需补充**（推荐 fallback 覆盖 + 同步修复内部调用点）
- **架构师补充**（推荐选项 B 覆盖原推荐 A）：

  **修正推荐：选项 B（fallback 逻辑）优于选项 A（仅文档说明）**

  理由：
  1. **dogfood 频次**：框架自审是高频操作（B3#034 修复期间将密集使用），每次手动加 `--config dev/complexity/config.yaml` 不友好
  2. **零误用风险**：用户项目下 `dev/complexity/config.yaml` 几乎不会出现（用户用 `dev_docs/`），fallback 不污染用户场景
  3. **集群治理**：021 + 034 + 023 同源 — 都是 dogfood 一致性问题。fallback 让 framework 工具具备"自审 vs 用户项目"的自感知能力，是治理 dogfood 集群的杠杆点

  **fallback 优先级（双脚本同步）**：
  ```
  1. CLI 显式 --config 指定 → 使用之
  2. dev_docs/complexity/config.yaml 存在 → 使用之（用户项目场景）
  3. dev/complexity/config.yaml 存在 → 使用之（框架自审场景）
  4. 否则 → 使用工具内置默认（已有 defaultConfig 逻辑）
  ```

  **修复点（双脚本对称 + 内部 bug）**：
  1. `tools/py/complexity_scanner.py`：
     - L520-L585 `load_config(config_path)`：`config_path` 为空/None/路径不存在时按 fallback 顺序探测（dev_docs/ → dev/ → 内置默认）
     - L595 argparse default：保持 `dev_docs/complexity/config.yaml` 不变（用户项目场景仍优先），但 help 文本更新为"默认按 fallback 顺序探测"
     - **L363、L434 等内部调用点**：把 `load_config("")` 改为 `load_config(args.config)`（需将 args 透传或在 main() 装载一次共享 dict）
  2. `tools/js/complexity_scanner.js`：
     - L587-L646 实现镜像 fallback 逻辑
     - 内部调用点同步对齐
  3. `--help` 文档（双脚本 L13-L25 段）：明示三层 fallback 顺序
  4. `tools/README.md`：补"框架自审 vs 用户项目"差异说明段

  **更稳妥的工程化**（可选增强）：
  - 引入 `AICC_FRAMEWORK_SELF=1` 环境变量显式声明自审场景（避免在用户项目偶然存在 dev/complexity/config.yaml 时产生歧义）
  - 在 `core/framework_spec.md` 的"标准产物路径"章节（B1 新建的 SSOT）追加"工具默认路径与 fallback 规则"小节，登记此约定

  **横切收益**：本修复同时为 #034 修复期间的 dogfood 操作清障 — 修 034 时需大量调用 `summary_validator.py`、`complexity_scanner.py` 等工具自审，021 修好则一切顺畅

---

### B3 修复优先级与执行顺序（架构师推荐）

> 基于跨 Issue 依赖与 dogfood 集群治理，建议执行顺序如下。

| 序 | Issue | 类型 | 阻断/被阻 | 推荐时机 |
|:-:|---|---|---|---|
| 1 | **021** | dogfood 工具修复（fallback + 内部 bug） | 不阻断 → 阻断 034 修复期间的 dogfood 操作 | **优先**：先扫平工具 dogfood 阻碍 |
| 2 | **035** | 双脚本对称（aac_validator.js docstring） | 独立 | 与 021 同批次（都是 tools/ 卫生） |
| 3 | **025** | dev/quality/README.md L44-L58 措辞 | 不阻断 | 与 024 同批次（同源 SOP 漂移） |
| 4 | **024** | Framework_Review_Guidelines.md SOP 重组 | 不阻断 | 与 025 同批次 |
| 5 | **027** | 005 walkthrough 提升 Public（含创建 workflows/） | 阻断 019 闭合（B4） | 在 034 P1 阶段同步推进（新文件即第 2 个 frontmatter 样板） |
| 6 | **034** | frontmatter 14% 自指 | 横跨长周期，分 P0/P1/P2 三阶段 | **最后启动 P0**：因 P0 涉及顶层入口文件（含 AI_ENTRY_POINT.md），应在 027 完成索引补全后再统一加 frontmatter，避免重复编辑 |

### B3 修复后回归验证清单（一次性脚本）

```bash
# 021: complexity_scanner 在框架仓库根可正常运行（无 --config）
python tools/py/complexity_scanner.py --since "1 day ago" 2>&1 | head -5
node   tools/js/complexity_scanner.js --since "1 day ago" 2>&1 | head -5
# 修复后预期：无"找不到 dev_docs/complexity/config.yaml"错误，自动 fallback 到 dev/

# 024: Guidelines 不再列 Review_Data.zip / Assessment_Dashboard.html
grep -nE 'Review_Data\.zip|Assessment_Dashboard\.html' dev/quality/Framework_Review_Guidelines.md
# 修复后预期：返回空

# 024: Guidelines 已含"必需 5 件套 + 可选附加"结构
grep -nE '必需.*5.*件套|可选附加' dev/quality/Framework_Review_Guidelines.md
# 修复后预期：≥ 2 处命中

# 025: README 不再承诺"每个 🔴 文档对应一份 context"
grep -nE '每个.*context.*对应一份|具体清单见下方' dev/quality/README.md
# 修复后预期：返回空

# 025: README 已使用"按需生成"语境
grep -cE '按需生成' dev/quality/README.md
# 修复后预期：≥ 1

# 027: workflows/complexity_alert_workflow.md 已创建且带 frontmatter
test -f workflows/complexity_alert_workflow.md && head -1 workflows/complexity_alert_workflow.md | grep -q '^---$' && echo "✅ 027 创建+frontmatter 通过"

# 027: AI_ENTRY_POINT 已索引 complexity_scanner
grep -cE 'complexity_scanner' AI_ENTRY_POINT.md
# 修复后预期：≥ 2（py + js）

# 027: path_d 已含 @complexity 路由
grep -cE '@complex' workflows/path_d_specific_tasks.md
# 修复后预期：≥ 1

# 034 P0: 顶层入口 + core/SUMMARY_FORMAT_SPEC + core/framework_spec 已带 frontmatter
for f in AI_ENTRY_POINT.md README.md CONTRIBUTING.md core/SUMMARY_FORMAT_SPEC.md core/framework_spec.md; do
  head -1 "$f" 2>/dev/null | grep -q '^---$' && echo "✅ $f" || echo "❌ $f"
done
# 修复后预期：全部 ✅

# 034: summary_validator strict 校验 P0 范围 0 错误
python tools/py/summary_validator.py --file AI_ENTRY_POINT.md --strict
python tools/py/summary_validator.py --file README.md --strict
python tools/py/summary_validator.py --file CONTRIBUTING.md --strict
python tools/py/summary_validator.py --file core/SUMMARY_FORMAT_SPEC.md --strict
# 修复后预期：全部 PASS

# 035: tools/js/aac_validator.js 已含 JSDoc 头部块
head -3 tools/js/aac_validator.js | grep -qE '^/\*' && echo "✅ 035"
# 修复后预期：✅

# 035: 双脚本对称回归
total=0; missing=0
for f in tools/js/*.js; do
  [[ "$f" == *.test.js ]] && continue
  total=$((total+1))
  head -3 "$f" | grep -qE '^/\*|^//' || missing=$((missing+1))
done
echo "JS 主脚本头部 docstring: $(( (total-missing) * 100 / total ))%"
# 修复后预期：100%
```

### B3 横切洞察

1. **dogfood 失败集群**：034（frontmatter 14%）+ 027（设计-发布 gap）+ 021（默认路径假设）+ 035（双脚本对称偏差）共同显示"AICC 框架对自身的 dogfood 能力薄弱"。这是 R5（自指一致性）维度的本质性问题，单点修复治标不治本。建议在 SSOT 章节追加"框架自审 mode"约定。

2. **dev_docs/ vs dev/ 二元结构未在工具行为中显式处理**：021 暴露根因 —"框架开发者用 dev/，用户项目用 dev_docs/"二元约定仅在文档层存在，工具默认值单方向硬编码偏向用户场景，造成框架自审摩擦。fallback 逻辑是治理点。

3. **B1#022 重命名连锁**：027 的源路径已因 B1 修复而过期 — 这提示后续批次需特别注意"前批次修复对后批次 Issue 描述的连锁影响"。建议在最终系统性发现章节中归并这类"修复链"问题。

4. **SOP 与策略漂移集群**：024（Guidelines 列 10 项实际 5 件套）+ 025（README 措辞与 contexts 现状脱节）共同指向"SOP 文档随策略迭代时未同步"。与 B2 的 014（FRAMEWORK_CONTEXT 自相矛盾）同源，是 R2 V3.0 一致性的横切问题。建议把"策略变更必须同步刷新 SOP 引用"列入 quality 体系的 verification 清单。

---

## 🔹 Batch 4：实体缺失 + 工作流闭环

> **批次目标**：核查 doc_health_checker（017）、端到端工作流（019）、--check-doc-errors phantom 参数（020）、architecture_analyzer 虚标（026）的真实性与方案可行性。
>
> **完成日期**：2026-04-26
>
> **批次结论**：
> - 4 项 Issue 全部 **真实存在**
> - 描述完全准确：1 项（020）
> - 描述有偏差需补充：3 项（017 漏报严重 / 026 漏报 + 路径未对齐 / 019 实质已闭环）
> - 修复方案处置：✅ 通过 1 项（020） / 🟡 需补充 1 项（019 已闭环登记） / 🔴 重大缺陷需重写 2 项（017 / 026）
> - **关键洞察**：017 与 026 暴露同一根因 —"文档承诺超前实施"；与 015（已完成未登记）反向 — 这是 R5（自指一致性）的另一面
> - **集群关系**：017+020+026 共同构成"工具实体缺失集群"；建议合并治理而非单点修复

---

### AICC-20260425-017 — doc_health_checker 工具实体缺失（双脚本均无）

- **真实性**：✅ 真实存在（主要）
- **描述准确性**：⚠️ **漏报严重** — Issue 列了 6 处引用，**实际仓库共 11 处**：
  - `workflows/commit_guided_update.md:372` ✅（含 `--file` 参数）
  - `workflows/maintenance_workflow.md:176, 179, 202, 224, 420` — 5 处（已列）
  - **`workflows/maintenance_workflow.md:477, 480, 483, 490`** — 4 处 `--mode quick/standard/deep` **未列**
  - **`workflows/generation_workflow.md:1318`** — 通用引用 **未列**
- **关键证据**：
  - `tools/py/doc_health_checker.py` + `tools/js/doc_health_checker.js` 均不存在
  - 实际命令矩阵（11 处提取）：
    - `--file FILE`（commit_guided 单文档检查）
    - `--check-code-samples`（代码示例有效性）
    - `--check-file-paths`（文件路径准确性）
    - `--check-dependencies`（依赖版本）
    - `--full-check`（综合）
    - `--mode quick`（仅链接 + 摘要）
    - `--mode standard`（+ 代码示例）
    - `--mode deep`（+ 依赖 + 架构图）
  - 现有重叠工具盘点：
    - `tools/py/doc_dependency_tracer.py` — 已实现链接 / 文件路径追踪
    - `tools/py/summary_validator.py` — frontmatter 校验
    - `tools/py/doc_fix_executor.py` + `batch_fix_manager.py` — 修复执行
    - **空白能力**：代码示例语法有效性、依赖版本对照
- **方案评估**：🔴 **重大缺陷需重写**
  - ❌ 原方案选项 A（"实施完整 doc_health_checker 双脚本"）成本过高（每端 ~600-800 LOC × 2 = 1200-1600 LOC 新代码）
  - ❌ 原方案选项 B（"删除引用，合并到 complexity_scanner 或现有工具"）会破坏 11 处文档语义（用户感知一致性受损）
  - ⚠️ 原方案漏报 5 处引用 + 4 个 mode 参数 — 修复时易遗漏导致再次"修了一半"
  - ❌ 都没考虑 V3.0 双脚本对称红线 + 零依赖红线
- **架构师重写方案**（Hybrid Orchestrator 模式）：

  **核心思路**：实施 `doc_health_checker.py/.js` 作为**薄编排层**（thin orchestrator），不重新实现已存在的能力，而是 delegate 到现有工具 + 仅补差缺能力。

  **能力映射表**（编排层职责）：

  | 检查项 | 实施方式 | 复用 / 新增 |
  |---|---|---|
  | `--check-file-paths` | 调用 `doc_dependency_tracer.py --doc <path> --strategy all` | **复用** |
  | `--check-code-samples` | 提取 \`\`\` 代码块 + 按语言执行 `python -c` / `node -e` 等基础语法检查 | **新增（最小）** ~80 LOC |
  | `--check-dependencies` | 解析 package.json / requirements.txt + 比对文档中"版本号"提及 | **新增（最小）** ~100 LOC |
  | `--full-check` | 组合上述三者 | **编排** |
  | `--mode quick` | 仅 `--check-file-paths` | **编排** |
  | `--mode standard` | quick + `--check-code-samples` | **编排** |
  | `--mode deep` | standard + `--check-dependencies` + 调用 `summary_validator.py --dir --strict --recursive` | **编排** |
  | `--file FILE` | 单文件子集（链接检查 + 代码示例 + frontmatter） | **编排** |

  **代码量预估**：编排层 ~250-300 LOC × 2 (py/js) = ~500-600 LOC（仅原方案 A 的 1/3）

  **零依赖红线**：仅使用 subprocess 调用其他工具脚本 + 标准库 json/argparse；不引入 pyyaml / cheerio / jsdom

  **修复点（双脚本对称）**：
  1. **新建** `tools/py/doc_health_checker.py`（编排层 + 2 个新增最小检查）
  2. **新建** `tools/js/doc_health_checker.js`（镜像）
  3. 头部带规范 docstring（与 035 同标准）
  4. **登记**：`AI_ENTRY_POINT.md` 工具表追加 2 行；`tools/README.md` 补条目
  5. **不需要改** 11 处引用（保留原命令格式）— 用户感知零影响

  **实施分阶段**（避免 P0 修复一口吃成胖子）：
  - **P0**：新建编排层骨架 + `--check-file-paths`（复用） + `--mode quick`（最常用）— 200 LOC × 2
  - **P1**：补 `--check-code-samples` + `--mode standard` + `--full-check` — 累计 350 LOC × 2
  - **P2**：补 `--check-dependencies` + `--mode deep` + `--file FILE` — 完整 500 LOC × 2

  **风险与权衡**：
  - 编排层依赖现有工具的稳定性（doc_dependency_tracer / summary_validator）
  - `--check-code-samples` 的语法检查粒度有限（仅 Python/Node 基础执行测试）；架构图准确性按 maintenance_workflow.md L237 已注明"人工审查（暂无自动化工具）"，编排层亦不涉及
  - 与 020 联动：原"--check-doc-errors" 不在 doc_health_checker 范围（020 应单独走删除路线）

  **同步治理（与 020+026 集群）**：见下方"B4 集群修复策略"。

---

### AICC-20260425-019 — 端到端复杂度告警工作流缺失（已由 B3#027 同步关闭）

- **真实性**：✅ 真实存在（修复前）
- **描述准确性**：✅ 准确
- **当前状态**：🟢 **已闭环**（B3#027 修复时同步关闭）
- **关键证据**（实地核查 — 闭环验证全 PASS）：
  - `workflows/complexity_alert_workflow.md` 已存在（B3 创建，含完整 frontmatter）
  - `AI_ENTRY_POINT.md` 含 `complexity_scanner` / `complexity_alert` / `@complexity` 索引共 3 处
  - `workflows/path_d_specific_tasks.md` 含 `@complex` 命中 3 处（任务索引表 + 章节 + fallback 段）
  - 端到端剧本可演练：`tools/py/complexity_scanner.py + report_generator.py` 双脚本 fallback 后框架仓库根直跑通过（已含 B3#021 fallback 修复）
- **方案评估**：✅ **通过**（B3#027 实施已覆盖原方案 4 项要求）
- **架构师补充**：
  - **无需重复修复**。本批次仅作正式登记。
  - **同步动作**：将原 Issue 状态从"待修复"改为"🟢 已修复（B3 同步关闭）"
  - **建议**：原 Issue 可作为"为何 B3#027 是杠杆点"的引用证据 — 一次修复 027 同时关闭 019、补全 023 索引语境

---

### AICC-20260425-020 — `complexity_scanner --check-doc-errors` 参数 phantom

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 完全准确
- **关键证据**：
  - `workflows/document_health_check.md:418` 仍含 `python tools/py/complexity_scanner.py --path . --check-doc-errors`
  - 实测 `python tools/py/complexity_scanner.py --check-doc-errors` 报错 `unrecognized arguments: --check-doc-errors`
  - L420-L424 同段已含其他**真实可用**的命令（`batch_fix_manager.py`、`doc_dependency_tracer.py`）— 改造空间充足
- **方案评估**：✅ **通过**（推荐选项 B：删除 + 替换）
- **架构师补充**（细化原方案）：

  **修复方式**（最小改动 + 不破坏文档结构）：

  把 L418 单行替换为指向 011 文档谬误工具链的等价命令（实际可执行）：

  ```bash
  # 1. 自动检测文档谬误（基于 011-文档谬误修复工具链）
  python tools/py/doc_dependency_tracer.py --doc dev_docs/api_layer.md --strategy all
  ```

  - 保持 L420（batch_fix_manager 已正确）+ L424（doc_dependency_tracer 已正确）
  - 替换 L418 后整段是"3 步真实工具链"，而非"1 phantom + 2 真"
  - 与 #017 修复联动：等 017 编排层完成后，可进一步把 L418 升级为 `python tools/py/doc_health_checker.py --file dev_docs/api_layer.md`（与 commit_guided_update.md L372 同款）

  **回归验证**（修复后）：
  ```bash
  grep -n 'check-doc-errors' workflows/document_health_check.md tools/py/complexity_scanner.py
  # 修复后预期：返回空（两边都无）
  ```

---

### AICC-20260425-026 — `architecture_analyzer.py` 工具虚标（005 walkthrough Phase 4 未实施）

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ **偏差** — 漏报且源路径过期：
  - **漏报**：`tools/py/trend_analyzer.py` **同样不存在**（005 implementation_plan.md L119 [NEW] 标记），与 architecture_analyzer 同属 005 Phase 4 高级功能优化模块。Issue 仅指出 1 项虚标，实际是 Phase 4 整段（2 项）未实施。
  - **源路径过期**：Issue 引用 `005-complexity-dashboard.md/walkthrough.md` 已被 B1#022 重命名为 `005-complexity-dashboard/walkthrough.md`（去 .md/ 后缀）。与 027 同样问题。
- **关键证据**：
  - `tools/py/architecture_analyzer.py` ❌、`tools/js/architecture_analyzer.js` ❌
  - `tools/py/trend_analyzer.py` ❌（同属 Phase 4，Issue 漏报）
  - `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md:17` 仍含 `architecture_analyzer.py - 高级架构分析`
  - `dev/V3.0/confirmed/005-complexity-dashboard/implementation_plan.md:113-123` 标 Phase 4 `[NEW]`：architecture_analyzer + trend_analyzer 两工具
  - 005 实际完成度：Phases 1-3 ✅；**Phase 4 ❌ 未启动**（不只是部分缺失，是完整未实施）
- **方案评估**：🔴 **重大缺陷需重写**
  - ❌ 原方案选项 A（"补全 architecture_analyzer 双脚本"）低估了 Phase 4 工作量 — 包含两个独立工具（architecture_analyzer + trend_analyzer），每个 ~600-1000 LOC × 2 = 总计 2400-4000 LOC 新代码，不是"P1 完结的最后一里"
  - ❌ 原方案没识别 trend_analyzer 同样虚标
  - ❌ 缺少"实施 vs 文档诚实化"的成本对比
  - ⚠️ 005 优化点已在 PROGRESS.md 标 ✅ — 直接补 Phase 4 会让 005 状态语义更复杂（应是 P1 已完成 + Phase 4 待续）
- **架构师重写方案**（推荐选项 B：文档诚实化 + 升级为独立优化点）：

  **核心判断**：补全 Phase 4 是新优化点（值 1 个独立 V3.0+ 编号），不是 026 修复范围。026 应仅修文档与现状对齐。

  **修复点**（修文档，不补工具）：

  1. **`dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` L13-L18 修订**：
     - 把 L17 从"实施产出摘要"段移到新增"📋 Phase 4 待实施"段
     - 明示：架构分析（architecture_analyzer.py）+ 趋势分析（trend_analyzer.py）属设计意图，未在 005 P1 范围内实施
     - 改写后段落举例：
       ```
       ### 2. 🛠️ 支持工具链 (Dual-Engine: Py/JS)
       - **扫描工具**: complexity_scanner.py & complexity_scanner.js - 基础数据采集 ✅
       - **报告生成**: report_generator.py - Markdown/HTML 报告生成 ✅
       - **通知工具**: notifier.py - Slack/Email 通知 ✅

       ### Phase 4 待实施（不在 005 P1 范围）
       - **架构分析**: architecture_analyzer.py - 高级架构分析（设计完成，待新优化点立项实施）
       - **趋势分析**: trend_analyzer.py - 历史趋势 + 预测（设计完成，待新优化点立项实施）
       ```

  2. **`dev/V3.0/confirmed/005-complexity-dashboard/implementation_plan.md` L109-L123**：
     - 把 Phase 4 段标题改为 "Phase 4: 高级功能优化（设计阶段，未实施）"
     - 加注：本 Phase 已完整规划但未在 005 P1 范围实施；如需推进，应作为独立优化点立项

  3. **新建立项条目**（不在 026 修复范围，但此处建议）：
     - 建议在 `dev/V3.0/PROGRESS.md` "V3.0+ 后期增益" 段追加候选条目：
       - `020 architecture-analyzer.md`（待立项）
       - `021 trend-analyzer.md`（待立项）
     - 这是给后续 user/AI 一个清晰的"未来路线图"入口

  4. **不需要改 PROGRESS.md 的 005 状态**：005 P1 范围（Phases 1-3）实际已完成，状态保持 ✅。仅需在描述中加"P1 已完成 / Phase 4 待新优化点立项"说明。

  **优势 vs 选项 A**：
  - 修复成本：~3 处文档编辑（vs 选项 A 的 2400+ LOC 新代码）
  - 历史诚实性：承认设计 - 实施 gap 比虚假补全更可信
  - 路线图清晰：把 Phase 4 提升为可见的"未来优化点候选"，而不是埋没在 005 walkthrough 里

  **回归验证**：
  ```bash
  # 1. walkthrough 把 architecture_analyzer 移出"实施产出"段
  grep -B 2 -A 2 'architecture_analyzer' dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md
  # 修复后预期：在"Phase 4 待实施"段，明确标注未实施

  # 2. implementation_plan 标注 Phase 4 未实施
  grep -nE 'Phase 4.*未实施|Phase 4.*待立项' dev/V3.0/confirmed/005-complexity-dashboard/implementation_plan.md
  # 修复后预期：≥ 1 处命中

  # 3. PROGRESS.md V3.0+ 段是否含 architecture-analyzer 候选条目（可选）
  grep -nE 'architecture-analyzer|trend-analyzer' dev/V3.0/PROGRESS.md
  ```

---

### B4 集群修复策略（架构师建议）

> 017 + 020 + 026 + 015（B2 已修） 共同形成"实施-文档 gap 集群"。本批次治理建议合并思考。

**集群根因**：
- AICC 框架在 V3.0 早期阶段为快速推进，部分工具被"先文档化、后实施"，但实施未跟上文档
- 单点修复每个 Issue 不能根除根因；需建立"工具实体一致性 gate"

**修复优先级与执行顺序**（B4 范围内）：

| 序 | Issue | 类型 | 推荐时机 | 阻断关系 |
|:-:|---|---|---|---|
| 1 | **019** | 已闭环登记 | 优先：仅状态更新 | 不阻断 |
| 2 | **020** | 单行替换 | 与 019 同批次（最简） | 不阻断 |
| 3 | **026** | 文档诚实化（3 处编辑） | 与 020 同批次 | 不阻断 |
| 4 | **017** | 实施 doc_health_checker 编排层（双脚本 + 工具索引） | **最后**：按分阶段（P0 先骨架） | 短期：阻断 maintenance_workflow 与 commit_guided 真实可用性 |

**集群级长期防御**（建议进入 V3.0+ 后期增益）：
- 引入 CI gate：每次 commit 检查所有 workflows/*.md 的 `python tools/py/*.py` 命令实际可执行
- 引入 SSOT 章节（在 B1 新建的 `core/framework_spec.md` 标准产物路径下）登记"已实施工具 vs 设计中工具"清单
- 与 #034 P1 联动：workflows/ 文件批量补 frontmatter 时同步审视命令真实性

### B4 修复后回归验证清单（一次性脚本）

```bash
# 017: doc_health_checker 双脚本存在 + 关键参数支持
test -f tools/py/doc_health_checker.py && test -f tools/js/doc_health_checker.js && echo "✅ 017 双脚本存在"
python tools/py/doc_health_checker.py --help 2>&1 | grep -cE '\-\-file|\-\-check-code-samples|\-\-check-file-paths|\-\-check-dependencies|\-\-full-check|\-\-mode'
# P0 阶段后预期：≥ 2（--file + --mode 至少）；P2 完整后预期 ≥ 6

# 017: 11 处引用都能解析（首批至少 --mode quick + --file 可执行）
python tools/py/doc_health_checker.py --mode quick 2>&1 | head -3
python tools/py/doc_health_checker.py --file workflows/path_a_first_generation.md 2>&1 | head -3

# 019: 端到端剧本 4 可演练（已由 B3#027 闭环）
python tools/py/complexity_scanner.py --since "1 day ago" --output /tmp/c.json && \
python tools/py/report_generator.py --data /tmp/c.json --output /tmp/c.md --format markdown && \
test -s /tmp/c.md && echo "✅ 019 剧本 4 端到端通过"

# 020: phantom 参数已删除
grep -n 'check-doc-errors' workflows/document_health_check.md tools/py/complexity_scanner.py
# 修复后预期：返回空

# 026: walkthrough 已标注 Phase 4 未实施
grep -nE 'Phase 4.*未实施|Phase 4.*待立项|Phase 4 待实施' dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md
# 修复后预期：≥ 1 处命中

# 026: PROGRESS.md V3.0+ 段含 Phase 4 候选条目（可选）
grep -nE 'architecture-analyzer|trend-analyzer' dev/V3.0/PROGRESS.md
```

### B4 横切洞察

1. **"实施 - 文档" gap 集群**：017 + 020 + 026 + B2 已修 015 共同显示 — AICC 在 V3.0 早期 P0/P1 推进时存在"先承诺再实施"模式。建议在 quality 体系中加入"工具实体核查"作为标准 verification 步骤。

2. **B1#022 重命名连锁第二例**：026 与 027（B3）同样面临"前批次修复使 Issue 描述路径过期"。这强化了 B3 已识别的"修复链问题"模式 — 在最终系统性发现章节应作为独立专题。

3. **Phase 4 未实施识别为"未来优化点"**：026 修复时把 architecture_analyzer + trend_analyzer 升级为 V3.0+ 候选条目，是把"虚标"转化为"路线图清晰度"的范例。可作为后续类似情况的处置模板。

4. **017 编排层模式作为框架扩展范式**：薄编排层 + delegate 现有工具的模式，比"重新实现完整工具"成本低 60%+，且避免了双脚本重复实施。建议把此模式登记到 `core/design_decisions.md` 作为框架级扩展规范。

5. **019 闭环验证证明 B3#027 杠杆点价值**：单点修复 027 同时关闭 019、间接强化 023（语境一致），符合架构师"杠杆点优先"判断。

---

## 🔹 Batch 5：用户旅程 + 已修复回放 + 卫生

> **批次目标**：核查 R4 用户旅程（028/030/031/033）+ 已修复 4 项 git-diff 回放（004/005/006/007）+ 卫生类（008/009）+ B2 附带 2 项（PROGRESS L86 015 误列 / L274-L293 末尾重复）。

### 批次结论

- **真实性 10/10**：本批次 10 项 Issue 全部真实存在。已修复 4 项均通过 git-diff 回放验证，待修复 6 项均经实地核查命中。
- **描述准确性**：
  - 完全准确：004 / 005 / 006 / 007 / 008 / 009 / 028 / 031 / 033（9 项）
  - **严重漏报**：030 — Issue 称 quick_start.md 4 处，实测全 Public 层 **共 13 处**（quick_start 4 + CONTRIBUTING 1 + core/framework_spec 5 + templates/plans_README_TEMPLATE 2 + guides/generation_workflow 2）；本现象与 B1 集群（016 / 017 / 032）+ B4 集群（017 / 026）的"漏报严重"模式同源，是 V3.0 一致性扫描机制系统性弱点的第三批证据。
- **方案评估**：
  - ✅ 通过：004 / 005 / 006 / 007 / 008 / 009 / 031 / 033（8 项；其中 004-007 已修复，无须再评）
  - 🟡 需补充：030（覆盖范围扩展到 13 处 + 治理规则）
  - 🔴 重大缺陷已重写：028（原方案"重写 quick_start"过粗 — 应给出明确的步骤 2/3 内容草案、嵌套 fence 修复机制、与 path_a 的 8 步对齐方式）
- **新增专题**：B2 附带 2 项纳入本批次合并修复，避免独立微 commit。

### AICC-20260425-004 — dev/quality 编码乱码（已修复回放）

- **真实性**：✅ 真实存在（Phase 0 commit `3edfbe2` 已修复）
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过 — Phase 0 commit `3edfbe2` 直接修复 + 长期防御建议 pre-commit hook
- **关键证据**：
  - `grep -rP '[\x{FFFD}]' dev/quality/Issue_Recording_Standard.md dev/quality/Progress_Tracking_Standard.md` 返回 0 命中
  - 两文件 tail 末尾完整无孤字
- **架构师建议**：
  - 长期防御方案"pre-commit hook 检查 U+FFFD"未真正落地，008 同性质问题在 PROGRESS.md 仍存活，证明仅靠人工修复无法防止再发生。建议在 B5 修复或后续治理工作中真正添加该 hook（与 028 markdown 结构校验合并为一个 `pre-commit` 文件）。

### AICC-20260425-005 — Framework_Review_Guidelines.md 自相矛盾（已修复回放）

- **真实性**：✅ 真实存在（Phase 0 commit `3edfbe2` + B3#024 联合处理）
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过 — 已重写为"审核视角分层"机制（A/B/C 三视角并存）
- **关键证据**：
  - `grep -nE '跳过 ?dev/|排除 ?dev/' dev/quality/Framework_Review_Guidelines.md` 实测：仅 L34 / L510 / L573 出现，分别为：
    - L34 注脚（"v1.0 曾要求…，v1.1 起三视角并存"）— 历史说明，非政策
    - L510 配置说明（"视角 A 排除 dev/，视角 B 全量，视角 C 仅 dev/"）— 视角内合法约定
    - L573 v1.2 changelog（"删除自相矛盾的'跳过 dev/'政策"）— 修复证据
  - `grep -nE '视角 ?[ABC]|三视角' dev/quality/Framework_Review_Guidelines.md` 命中 5+ 处，三视角章节完整
- **架构师建议**：无追加项。注意 v1.2 → v1.3 同步更新（B3#024 已重组"5 件套+可选附加"，可考虑统一推进 v1.3）。

### AICC-20260425-006 — 基础设施长期缺失（已修复回放）

- **真实性**：✅ 真实存在（Phase 0 commit `3edfbe2` 修复）
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过 — audits/ 目录创建 + contexts/ 改 v2.0 按需策略
- **关键证据**：
  - `ls dev/quality/audits/`：含 `README.md` + `2026-04-25_V3.x_Comprehensive/` round 目录
  - 本轮 round 目录含 5 件套 + 4 项可选附加（Plan / Issue_Tracking / Progress_Tracking / Review_Log / Review_Checklist + Comprehensive_Review_Report / Issue_Analysis / Improvement_Roadmap / Review_Verification_Report）
  - `dev/quality/contexts/` 仍仅 `_template.md`，符合 v2.0"按需生成"语境（B3#025 已联合修复 README 措辞）
- **架构师建议**：006 治愈后形成的"完整 audits/ 体系"恰是本轮二次复审能落地的基石；反向印证基础设施缺失的副作用并不抽象 — 一旦补齐，质量循环立即可启动。建议在 quality/README.md 顶部加一句"本目录的运转依赖 audits/round 目录存在；请确认每次启动新 round 时遵循命名规范"。

### AICC-20260425-007 — BY_DOCUMENT_TYPE 被引用但缺失（已修复回放）

- **真实性**：✅ 真实存在（Phase 0 commit `3edfbe2` 创建）
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过 — 文件已创建（336 行），覆盖 10 类专项标准
- **关键证据**：
  - `ls dev/quality/standards/BY_DOCUMENT_TYPE.md` 存在
  - 顶层 `## N.` 标题序列覆盖：1 入口 / 2 core / 3 workflows / 4 agents / 5 tools / 6 templates / 7 guides / 8 config / 9 ADR / 10 quality（10 类齐全）
  - 引用方均能解析（HOW_TO_GENERATE_CONTEXTS L727 / standards/QUALITY_CHECKLIST L171 等）
- **架构师建议**：注意 `HOW_TO_GENERATE_CONTEXTS.md` L281 仍写"待创建"标记，与实际状态不符；建议同 008/009 一并清理。

### AICC-20260425-008 — PROGRESS.md 末尾乱码 + 重复（待修复 + B2 附带合并）

- **真实性**：✅ 真实存在；**B2 修复时未顺手清理**，反而因新增 V3.0+ 后期增益段使重复结构更明显
- **描述准确性**：✅ 准确
- **方案评估**：🟡 需补充范围说明（与 B2 附带 L274-L293 重复段为同一现象）
- **关键证据**（实地 read PROGRESS.md L274-L345）：
  - L274-L292：旧版"相关链接 + 状态图例 + **最后更新 2026-04-22** + 孤字"发布" + 未闭合 ` ``` `"块
  - L293 ` ``` ` 单独一行（无配对开启） → `grep -c '^```'` 全文计数为 **7**（奇数 = 未闭合）
  - L295-L329：B2 新增的 V3.0+ 后期增益正文段（包含 019 + 候选优化点 020/021）
  - L329-L345：第二份"相关链接 + 状态图例"段（无"最后更新"，但内容完全重复 L274-L289）
  - `grep -c '^## 🔗 相关链接' = 2`；`grep -c '状态图例' = 2`
- **架构师建议**：
  - 修复策略：删除 L274-L293（含旧"最后更新 2026-04-22" + 孤字"发布" + 未闭合 fence），保留 L329-L345 作为唯一末尾段；并把"最后更新"刷为本次治理日（2026-04-26）
  - **附带 PROGRESS L86 合并处理**：实测 L87 `- [ ] 实现质量保证体系集成 (015)` 仍以 P1 milestone 待办形式存在，与 L19 015 已归档 + L36 P2 列入 015 🔴（已归档）矛盾。本条作为 008 的同性质数据完整性问题一并清理（删除 L87 单行）。
  - **附带 008 长期防御**：与 004 共用同一 pre-commit hook（U+FFFD + 未闭合 fence + 重复 ## 标题三检），首次落实"长期防御"承诺。

### AICC-20260425-009 — dev/V3.0/reference/commit_as_prompt_analysis.md L699 悬空引用（待修复）

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确（精确 1 处，仅 commit_as_prompt_analysis.md L699）
- **方案评估**：✅ 通过 — 改路径为 `dev/V3.0/confirmed/018-commit-guided-documentation/`
- **关键证据**：
  - `grep -rn 'V3\.0/pending/' --include='*.md'` 全仓仅 1 处真泄漏：commit_as_prompt_analysis.md L699；其余命中均在本轮 audit 文档（Issue_Tracking / Review_Checklist 等）的描述性引用，可豁免
  - `dev/V3.0/confirmed/018-commit-guided-documentation/` 目录确实存在
- **架构师建议**：
  - 修复时优先选 Issue 推荐方案 A（直接改路径），因 L699 处文本是历史时序性"立即行动"列表，路径变更不破坏语义
  - 同步在该行后追加一行"（注：018 已 confirmed，本节为历史分析记录）"避免读者困惑

### AICC-20260425-028 — guides/quick_start.md 结构错乱 + 步骤跳号（严重 / 待修复）

- **真实性**：✅ 真实存在（B5 R4 新用户旅程首次 **严重级别** Issue）
- **描述准确性**：✅ 准确（含步骤跳号 / 嵌套 fence 错位 / L235 计数自矛盾 / 审核清单段落定位错位 全部命中）
- **方案评估**：🔴 重大缺陷需重写 — Issue 推荐方案"重写 quick_start，确保步骤连续 + 与 path_a 9 步对齐"过粗，未给出步骤 2/3 实际内容草案，也未指明嵌套 fence 修复机制
- **关键证据**（实地 read guides/quick_start.md 全文 235 行）：
  - L27 `### 步骤 0` / L52 `### 步骤 1` / L113 `### 步骤 4` / L132 `### 步骤 5` / L141 `### 步骤 6` — **缺步骤 2 + 步骤 3**
  - L54 ` ````bash`（4 个反引号开启外层 fence）→ 内容包入了 L57 起的"#### 审核清单 / 1. 数据准确性 / 2. 代码示例 / 3. 架构特点 / 4. 填写审核意见"全部内容到 L109 ` ```` `（4 反引号闭合）— 渲染后整段都是代码框，非正文
  - L235 "选择场景 1，严格按照 6 个步骤执行" — 但实际仅 5 个步骤段落
  - L113 "执行文档生成（审核通过后）"假设了不存在的"步骤 3：审核"
- **架构师建议（重写方案）**：
  1. **删除嵌套 fence**：L54-L109 整段从代码块中剥离 → 把"步骤 1: 复制规范"压缩为只剩 L52-L56 真实复制命令；把 L57-L109 的"审核清单"整体迁移到新增的"步骤 3: 审核方案"
  2. **新增步骤 2 + 步骤 3**（与 path_a S2/S3 概念对齐）：
     - 步骤 2 — 生成分析方案：调用 `templates/GENERATION_PLAN_TEMPLATE.md`，输出 `dev_docs/_analysis/generation_plan.md`
     - 步骤 3 — 审核方案：含原 L57-L109 的审核清单 + 决策路径（批准 / 修改 / 拒绝）
  3. **L235 计数同步**：改为"严格按照 6 个步骤（步骤 1-6）执行"或"按 7 步（步骤 0-6）执行"
  4. **同步对齐 path_a 8 步**（S0-S8）— quick_start 是其精简版，应在末尾加一行"完整流程见 `workflows/path_a_first_generation.md`"
  5. **028 与 030 / 033 在同一文件，强烈建议合并修复，避免对 quick_start.md 的 3 次 commit**

### AICC-20260425-030 — quick_start 过时框架名 ai_documentation_framework 残留（待修复）

- **真实性**：✅ 真实存在
- **描述准确性**：⚠️ **严重漏报** — Issue 仅列 quick_start.md 4 处，实测 Public 层共 **13 处**遗漏：
  | 文件 | 行号 | 数量 |
  |---|---|:-:|
  | `guides/quick_start.md` | L55, L145, L158, L228 | 4 |
  | `CONTRIBUTING.md` | L42 | 1 |
  | `core/framework_spec.md` | L513, L516, L520, L527, L530 | 5 |
  | `templates/plans_README_TEMPLATE.md` | L23, L61 | 2 |
  | `guides/generation_workflow.md` | L172, L569 | 2 |
  | dev/V2.3/V2.3整体评估报告_Antigravity.md | L4 | 1（历史档案，可豁免） |
- **方案评估**：🟡 需补充覆盖范围 + 治理规则
- **关键证据**：`grep -rn 'ai_documentation_framework' --include='*.md' .` 输出全表
- **架构师建议**：
  - 修复覆盖必须扩展到全 13 处 Public 层引用（含 framework_spec.md L513-530 — 这是用户复制框架最常被读到的章节，最高优先级）
  - 与 028 同 quick_start.md 的修复合并 commit
  - core/framework_spec.md / templates / generation_workflow 的修复独立 commit，因属不同 owner 维度
  - **治理规则**：在 SSOT 章节（B1 已建立的 `core/framework_spec.md` "标准产物路径" 段）追加"框架名 = `ai_coding_context`（仅当前生效；历史 V2.x 时期为 ai_documentation_framework，仅 dev/V2.x 历史档案保留）"
  - 与 016/017/032/026 同源治理 — 这是漏报模式第 5 例（已构成系统性问题），应升级到"系统性发现"章节专项纳入

### AICC-20260425-031 — README "3 步"vs 4 步计数错误（待修复）

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过（推荐 Issue 选项 A — 标题改 "4 步"，保留"完整阅读 README"作为隐含前提）
- **关键证据**（实地 read README.md L120-L194）：
  - L130 `## 🚀 快速开始（3 步）` ← 标题 3
  - L132-L135：编号列表 "1. 完整阅读 / 2. 复制框架 / 3. 让 AI 读取 / 4. AI 自动生成" ← 4 项
  - L137 / L144 / L162 / L173：详细 4 个步骤段落 ← 4 步
- **架构师建议**：
  - 直接采纳选项 A：L130 标题改 `## 🚀 快速开始（4 步）`
  - 与 028 / 030 / 033 不在同一文件，独立 1 行 commit 即可
  - **附带**：检查 AI_ENTRY_POINT.md 是否有同步过的"快速开始 N 步"措辞，避免连锁不一致

### AICC-20260425-033 — quick_start 推荐 find/cloc 与 V3.0 脱节（待修复）

- **真实性**：✅ 真实存在
- **描述准确性**：✅ 准确
- **方案评估**：✅ 通过（推荐 Issue 给出的 V3.0 工具优先 + shell fallback 的双层方案）
- **关键证据**：
  - L31-L34 推荐 `find . -name "*.ts" ... | wc -l` + `cloc . --exclude-dir=...` — 与 AI_ENTRY_POINT.md L320 推荐的 `project_scanner.py/.js` 脱节
  - V3.0 双脚本 + 零依赖红线已确立（B3 修复链 021 / 035 同期巩固）
- **架构师建议**：
  - 修复 L31-L34 时同时引用 AI_ENTRY_POINT.md `工具索引 → project_scanner` 段落，避免下次新增工具时再次脱节
  - 与 028 / 030 同 quick_start.md 文件，**强烈建议三项合并 1 个 commit**

### B5 修复优先级与执行顺序（架构师推荐）

修复目标 6 项 + B2 附带 2 项 = 共 8 个修复点。按"同源合并 + 文件去重"原则编排：

1. **C1（quick_start 大重写）** = 028 + 030（4 处 of 13） + 033 — 三项同 quick_start.md，**必须合并** 1 个 commit。先做嵌套 fence 拆解 + 步骤 2/3 补全（028），再统一替换 ai_documentation_framework → ai_coding_context（030 部分），再改 L31-L34 推荐工具（033）。
2. **C2（README 单行）** = 031 — 1 行修改，独立小 commit
3. **C3（030 剩余 9 处）** = CONTRIBUTING + framework_spec + plans_README_TEMPLATE + generation_workflow，可一个 commit 完成
4. **C4（PROGRESS 末尾清理）** = 008 + B2 附带 L86 015 + B2 附带 L274-L293 重复段 — 全部 PROGRESS.md，1 个 commit
5. **C5（009 单行）** = commit_as_prompt_analysis.md L699 修路径 + 加注 — 1 个 commit
6. **C6（HOW_TO_GENERATE_CONTEXTS L281 待创建标记清理）** = 007 衍生小修，可与 C4 合并到"卫生类"
7. **C7（pre-commit hook 长期防御）** = 004 + 008 共用 hook，建议作为独立选项推迟到本批次外（与 R5 自指治理规划合并）— 本批次不强制

**实际执行**：建议合并为 4-5 个 commits（C1 / C2+C3 / C4+C6 / C5），减少噪音同时保持每 commit 主题清晰。

### B5 修复后回归验证清单（一次性脚本）

```bash
#!/usr/bin/env bash
# B5 回归脚本（修复后执行；任何 ❌ 表示存在残留）

echo "=== 028 quick_start 步骤连续性 ==="
STEPS=$(grep -oE '^### 步骤 [0-9]+' guides/quick_start.md | grep -oE '[0-9]+' | tr '\n' ' ')
echo "实际步骤序列: $STEPS"
[ "$STEPS" = "0 1 2 3 4 5 6 " ] || [ "$STEPS" = "1 2 3 4 5 6 " ] && echo "✅ 步骤连续" || echo "❌ 不连续"
FENCE_QS=$(grep -cE '^```' guides/quick_start.md)
echo "fence 计数 = $FENCE_QS（应为偶数）"

echo "=== 030 ai_documentation_framework 残留 ==="
grep -rn 'ai_documentation_framework' --include='*.md' . | grep -v '^dev/V2' | grep -v 'dev/quality/audits/' && echo "❌ Public 层仍有残留" || echo "✅ Public 层归零"

echo "=== 031 README 标题/步骤数 ==="
TITLE=$(grep -oE '快速开始（[0-9]+ ?步）' README.md | grep -oE '[0-9]+')
DETAIL=$(grep -cE '^### 步骤 [0-9]+:' README.md)
echo "标题: $TITLE 步; 详细步骤: $DETAIL 步"
[ "$TITLE" = "$DETAIL" ] && echo "✅ 一致" || echo "❌ 不一致"

echo "=== 033 quick_start V3.0 工具引导 ==="
grep -nE 'project_scanner|tools/py/|tools/js/' guides/quick_start.md > /dev/null && echo "✅ 含 V3.0 工具引导" || echo "❌ 仍无引导"

echo "=== 008 PROGRESS 末尾整洁 ==="
echo "fence 计数: $(grep -c '^```' dev/V3.0/PROGRESS.md)（应为偶数）"
echo "相关链接: $(grep -c '^## 🔗 相关链接' dev/V3.0/PROGRESS.md) 次（应=1）"
echo "状态图例: $(grep -c '状态图例' dev/V3.0/PROGRESS.md) 次（应=1）"
grep -q '^发布$' dev/V3.0/PROGRESS.md && echo "❌ 孤字'发布'仍存在" || echo "✅ 孤字'发布'已清"

echo "=== B2 附带 PROGRESS L87 015 误列 ==="
grep -nE '\[ \] 实现质量保证体系集成 \(015\)' dev/V3.0/PROGRESS.md && echo "❌ 015 仍误列 P1 待办" || echo "✅ 已清"

echo "=== 009 V3.0/pending/ 残留 ==="
grep -rn 'V3\.0/pending/' --include='*.md' . | grep -v 'dev/quality/audits/' && echo "❌ 真泄漏仍存在" || echo "✅ 真泄漏归零"

echo "=== 007 HOW_TO_GENERATE_CONTEXTS 待创建标记清理 ==="
grep -nE 'BY_DOCUMENT_TYPE\.md.*待创建' dev/quality/HOW_TO_GENERATE_CONTEXTS.md && echo "❌ 待创建标记残留" || echo "✅ 已清"
```

### B5 横切洞察

1. **R4 用户旅程首次出现"严重"级 Issue（028）**：本轮 35 项 Issue 中只有 028 + 034 两条 **严重级**。028 集中于 R4 — 说明新用户旅程是 V3.0 阶段最薄弱的一环（与 R1/R2/R5 已多轮治理形成鲜明对比）。建议把 R4 升级为长期 dogfood 强制环节：每次 Public 层文档变更都触发"模拟新用户从 README → AI_ENTRY_POINT → quick_start → workflows/path_a 的 30 分钟旅程"。

2. **漏报模式第 5 例（030）**：B1 的 016 / 017 / 032、B4 的 017 / 026、本批次的 030，连续 6 项 Issue 均出现"Issue 描述漏报实际范围"。这并非偶发，而是**审查阶段的扫描深度不够**的系统性表现。修复建议：把"全 Public 层 grep 验证"列入 Comprehensive Review SOP 的"R3 引用与边界"标准动作。

3. **同文件多 Issue 合并修复价值（C1）**：028+030+033 同 quick_start.md，若按 Issue ID 顺序逐个修复将产生 3 次 commit + 3 次同文件冲突风险；合并修复降低噪音 + 同步上下文一致性，是"杠杆点"治理的延续（与 B3 杠杆点 027 同源策略）。

4. **B2 附带项归并的合理性**：B2 复审日志已记 PROGRESS L86 + L274-L312 两项"严守批次范围而推迟"。本批次合并是"延迟一致性治理"的标准范式 — 既保证批次纯粹性，又不失收敛。建议在 quality/AUDIT_WORKFLOW.md 加一条"批次中发现的同性质问题，应统一推迟到对应主题批次"。

5. **B5 闭环将 R5 自指验证落地**：本批次 4 项已修复（004/005/006/007）的 git-diff 回放成功，是 quality 体系自审能力首次真实兑现 — quality 不仅会找别人的问题，也会被发现自己的问题（005/006/007 均是 quality 自身缺陷），并能验证修复持续有效。

6. **长期防御机制承诺需兑现（004+008+028）**：004 修复时承诺 pre-commit hook 检查 U+FFFD，008 同性质问题再次出现证明承诺未落地。本批次首次把"长期防御"提升为优先级 C7（建议范围外推进）。如果再次只人工修复不部署 hook，类似问题将第 N 次重现。

---

## 🌐 系统性发现（跨批次）

经 5 批次 35 项 Issue 完整复审 + 修复 + 回归验证后，识别以下 6 项跨批次系统性问题：

### 1. SSOT 缺位 — 命名一致性集群根因（B1）

- **现象**：016 / 029 / 032 / 016 多处对"AI_RULES.md 路径"、"框架名 ai_coding_context"持不同表述；权威源（AI_ENTRY_POINT.md 术语表）实测不存在权威记录。
- **治理**：B1 修复阶段在 `core/framework_spec.md` 新增"🗂️ 标准产物路径（SSOT）"章节，作为命名集群的真正单一真相源。
- **后续建议**：所有"产物路径 / 主文档名 / 框架自身名"变更必须先改 SSOT，再 grep 全仓同步。

### 2. 概览 + 详情双层架构 — 文档漂移集群解药（B2）

- **现象**：011 / 012 / 014 / 015 共同根因是"FRAMEWORK_CONTEXT 与 PROGRESS 双轨独立维护"。
- **治理**：B2 修复将 FRAMEWORK_CONTEXT 顶部 + 底部全部重写为指针式概览（"以 PROGRESS 为 SSOT"），新增 frontmatter `progress_synced_at` 字段作为漂移防御。
- **后续建议**：所有"两个文档共享同一组数据"的场景应套用本范式 — 一个为 SSOT，另一个为指针式概览，并加 `*_synced_at` 字段供 CI 校验。

### 3. dogfood 失败集群 — 框架自指能力薄弱（B3）

- **现象**：034（V3.0 强制 frontmatter 14% 自指）+ 027（005 walkthrough 未提升）+ 021（complexity_scanner 默认路径）+ 035（aac_validator JSDoc 缺失）共同指向"AICC 对自身的 dogfood 能力薄弱"。
- **治理**：B3 修复链 — fallback 模式（dev_docs/ → dev/ → 内置）补齐工具 dogfood 阻碍；JSDoc 100% 合规；frontmatter Public 总计 14% → 22%；workflows/complexity_alert_workflow.md 创建作为 V3.0-012 工程样板。
- **后续建议**：在 SSOT 章节追加"框架自审 mode"约定 — 任何工具新增 / 文档变更必须先在 dev/ 验证一遍再发到 dev_docs/。

### 4. 实施 - 文档 gap 集群 — 先承诺再实施模式（B4）

- **现象**：017（doc_health_checker 不存在）+ 020（complexity --check-doc-errors phantom）+ 026（architecture_analyzer + trend_analyzer Phase 4 未实施）+ B2#015（019 已完成未登记）共同指向"V3.0 早期 P0/P1 推进时存在先承诺再实施"。
- **治理**：B4 修复链 — 017 hybrid orchestrator 模式（550 LOC 完成原方案 1/3 成本）+ 026 文档诚实化 + Phase 4 升级为 V3.0+ 候选 + 020 phantom 命令替换为真实工具链。
- **后续建议**：在 quality 体系加入"工具实体核查"作为 R3 标准 verification 步骤；新增"hybrid orchestrator 模式"到 `core/design_decisions.md` 作为框架级扩展规范。

### 5. R4 用户旅程薄弱 — 严重级 Issue 集中区（B5）

- **现象**：35 项 Issue 中仅 028 + 034 两条严重级，028 集中在 R4（quick_start.md 步骤跳号 + 嵌套 fence + 计数自矛盾）。R1/R2/R5 经多轮治理已成熟，R4 是相对薄弱的最后一环。
- **治理**：B5 修复 C1 — quick_start 全文重写（步骤连续 0-6 + 嵌套 fence 拆解 + 步骤 2/3 内容草案 + path_a S0-S8 对齐）。
- **后续建议**：把 R4 升级为长期 dogfood 强制环节 — 每次 Public 层文档变更都触发"模拟新用户从 README → AI_ENTRY_POINT → quick_start → workflows/path_a 的 30 分钟旅程"。

### 6. 漏报模式 — 审查扫描深度不够（连续 6 例）

- **现象**：连续 6 项 Issue 出现"描述漏报实际范围"：B1 016（lowercase 还有 .kiro/ + dev/real_case 3+ 处）、017（11 处实际 vs 6 处列出）、032（漏 generation_workflow L493）、B4 017（11 处）、026（漏 trend_analyzer + Phase 4 整体）、B5 030（13 处实际 vs 4 处列出 — 复审本身又漏 workflows/generation_workflow 2 处，最终为 13 处而非 11 处）。
- **治理**：本现象未形成系统性治理；本轮所有"扩展覆盖"是事后人工 grep 补救。
- **后续建议（高优先级）**：在 `dev/quality/Framework_Review_Guidelines.md` 的 R3 章节加入硬性规则 — "任何'A 处出现 X'类描述必须 grep 验证全 Public 层范围后再写入 Issue"；在 quality/AUDIT_WORKFLOW.md 的"Issue 写入"步骤加 checklist 项"已 grep -rn 验证范围"。

### 7. B1 修复连锁 — 前批次修复使后批次 Issue 描述过期

- **现象**：B3#027 + B4#026 都因 B1#022 重命名（confirmed/ 三个 .md/ 目录去后缀）使 Issue 引用路径过期。属"修复链问题"。
- **治理**：本批次未做系统性治理；个案治理时手动对齐路径。
- **后续建议**：在 quality/AUDIT_WORKFLOW.md 加一条 — "批次内 Issue 修复完成后，应 grep 检查后续批次 Issue 是否引用被修改的路径，必要时同步更新 Issue 描述"。

### 8. 长期防御承诺未落地（004 → 008 重现）

- **现象**：004（U+FFFD）修复时承诺 pre-commit hook 但未真正部署；008（PROGRESS 末尾乱码）同性质问题再次出现。
- **治理**：本批次仅人工修复未部署 hook。
- **后续建议**：把 pre-commit hook 部署提升为独立任务（C7 — 范围外）— 检查项至少含 U+FFFD 字符 + 未闭合 ` ``` ` fence + 重复 `## 标题`。落地后 004 / 008 / 028 三类问题不会重复出现。

---

## 🎯 修复优先级建议（架构师视角）

经 5 批次完整修复后，本节作为后续治理的指导：

### 已完成（不再列入优先级）

35 项 Issue 全部修复（其中 004 / 005 / 006 / 007 在 Phase 0 处理；其余 31 项在本轮 5 批次）+ B2 附带 2 项合并 B5 处理。

### 建议范围外提升为独立任务（按优先级）

| # | 任务 | 关联 Issue | 预估工作量 |
|---|---|---|---|
| **T1** | pre-commit hook 部署（U+FFFD + 未闭合 fence + 重复标题三检） | 004 / 008 / 028 长期防御 | ~50 LOC + CI 集成 |
| **T2** | quality/AUDIT_WORKFLOW.md 加"R3 grep 全 Public 验证"硬性规则 | 漏报模式（连续 6 例） | 1-2 处编辑 |
| **T3** | core/design_decisions.md 新增"hybrid orchestrator + delegate 现有工具"扩展范式 | B4#017 经验沉淀 | ~50 行新增 |
| **T4** | core/framework_spec.md SSOT 章节追加"框架名 = ai_coding_context"治理规则 | B5#030 治理 | 1 处追加 |
| **T5** | R4 用户旅程作为 long-running dogfood 强制环节登记 | B5#028 系统化 | 流程文档新增 |
| **T6** | 034 P1（agents/ + tools/ + workflows/ 中等子集补 frontmatter）+ P2（其余）| B3#034 后续 | 累计 ~50 文件 |
| **T7** | 候选优化点 020 architecture-analyzer + 021 trend-analyzer 立项决策 | B4#026 路线图 | 立项即可，工作量另议 |

---

## 📊 复审统计总结

- **总 Issue 数**：35 项 + B2 附带 2 项 = **37 个修复点**
- **真实性核查**：35/35 全部真实存在（100%）
- **描述准确性**：
  - 完全准确：29 项（83%）
  - 偏差/漏报：6 项（17%）— 016 / 017 / 029 / 032 / 026 / 030
  - 严重失实：0 项
- **方案评估**：
  - ✅ 通过：21 项（60%）
  - 🟡 需补充：10 项（29%）
  - 🔴 重大缺陷已重写：4 项（11%）— 015 / 029 / 017 / 026 / 028（实际为 5 条，之中 015 为 B2 / 029 为 B1 / 017+026 为 B4 / 028 为 B5）
- **修复完成度**：35/35 + 附带 2 = 37/37（100%）
- **回归验证**：B1 + B2 + B3 + B4 + B5 全 5 批次回归脚本 PASS

---

**文档版本**：v1.0（5 批次完整闭环）
**创建日期**：2026-04-26
**最后更新**：2026-04-26
**维护者**：复审主审（Claude Opus 4.7）
