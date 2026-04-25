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

## 📊 复审结论汇总（动态更新）

> 待 5 批次完成后填写。

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

> 待启动。

---

## 🔹 Batch 5：用户旅程 + 已修复回放 + 卫生

> 待启动。

---

## 🌐 系统性发现（跨批次）

> 待 5 批次完成后撰写：原审核 5 大集群分析的复核结论 + 新发现的横切问题。

---

## 🎯 修复优先级建议（架构师视角）

> 待全部完成后输出：基于复审后的最优方案重排修复优先级。

---

**文档版本**：v0.1（骨架）
**创建日期**：2026-04-26
**维护者**：复审主审（Claude Opus 4.7）
