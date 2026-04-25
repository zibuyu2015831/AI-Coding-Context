---
title: V3.x Comprehensive Review — Issue Tracking
summary: 本轮审查发现的全部问题清单，按 PROJ-YYYYMMDD-XXX 编号；含 Phase 0 基线快照阶段已识别的 F-1~F-8 与后续批次新增问题。每条问题记录均包含描述、影响范围、文件路径、具体位置、复查方法、修复方案
keywords: issue-tracking | aicc | v3.x-review | findings
scope: 整轮审查的问题汇总单
verified_at: 2026-04-25
---

# V3.x Comprehensive Review — Issue Tracking

> **格式规范**：见 [`../../Issue_Recording_Standard.md`](../../Issue_Recording_Standard.md)
> **编号规则**：PROJ-YYYYMMDD-XXX；本轮统一前缀 `AICC-20260425-NNN`
> **状态**：🔴 待修复 / 🟡 修复中 / 🟢 已修复 / ⚪ 已确认非问题 / 🟣 已转化为长期改进
> **本轮工作目录**：所有命令均假设在仓库根 `/home2/wenbo/Videos/ai-coding-context/` 下执行

---

## 📊 统计概览

| 严重级别 | 数量 |
|---|---|
| 严重 | 2 |
| 主要 | 11 |
| 次要 | 14 |
| 建议 | 8 |
| **合计** | **35**（B0 基线 8 + B1 新增 2 + B2 新增 5 + B3 新增 6 + B4 新增 6 + B5 新增 6 + B6 新增 2；后续批次将追加） |

| 视角分布 | 数量 |
|---|---|
| 视角 A（用户） | 12 |
| 视角 B（完整性） | 18 |
| 视角 C（dev 卫生） | 6 |

| 修复状态 | 数量 |
|---|---|
| 🟢 已修复（Phase 0 顺手处理） | 4 |
| 🔴 待修复 | 31 |

---

## 问题 ID: AICC-20260425-001

- **类型**: 文档问题（漂移）
- **严重级别**: 主要
- **优先级**: 中
- **归属视角**: B（完整性）
- **关联任务/ADR**: 无（此 Issue 后由 011 进一步细化，两条同时保留）
- **状态**: 🔴 待修复

### 问题描述

`dev/FRAMEWORK_CONTEXT.md` 与 `dev/V3.0/PROGRESS.md` 对"V3.0 已完成"的清单与计数不一致。问题表现为多处：

- FRAMEWORK_CONTEXT.md L14-23 顶部摘要列出 8 项 P0 + 019（共 9 项），但漏列 P1 已完成的 004 / 005 / 006 / 011 / 014
- FRAMEWORK_CONTEXT.md L703-714 V3.0 章节列 11 项，但仍漏 011 / 014，且数字写"(10/17)"与列举的 11 项矛盾
- PROGRESS.md L18 列 11 项含 014，但不含 011（与 L88 011 ✅ 矛盾）

两份文档对"已完成"的定义和清单都不一致。

> **后续修订**：本 Issue 的精确细分见 AICC-20260425-011（FRAMEWORK_CONTEXT 顶部摘要）和 AICC-20260425-012（PROGRESS 自身）。本条作为统领性记录保留。

### 影响范围

- AI 或人类按 FRAMEWORK_CONTEXT 评估 V3.0 进度时会得出错误结论
- R2（V3.0 落地一致性）风险维度的核心表象
- 顶部摘要错误会让新读者误判项目阶段（"P1 仍在规划"）

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`
- `dev/V3.0/PROGRESS.md`

### 相关文件路径

- `dev/V3.0/confirmed/`（各优化点完成档案的真相源）
- `dev/V3.0/README.md`

### 具体位置

- `dev/FRAMEWORK_CONTEXT.md` L11-L29 顶部摘要
- `dev/FRAMEWORK_CONTEXT.md` L702-L716 V3.0 演进章节
- `dev/V3.0/PROGRESS.md` L18 顶部统计面板
- `dev/V3.0/PROGRESS.md` L82-L88 P1 milestone 任务清单

### 复查方法（验证修复）

```bash
# 1. 提取 FRAMEWORK_CONTEXT.md 中 V3.0 章节涉及的所有优化点编号
sed -n '14,30p;700,720p' dev/FRAMEWORK_CONTEXT.md \
  | grep -oE '\b0[0-1][0-9]\b' | sort -u > /tmp/fwctx.txt

# 2. 提取 PROGRESS.md 已完成清单的优化点编号
sed -n '14,45p;82,95p' dev/V3.0/PROGRESS.md \
  | grep -oE '\b0[0-1][0-9]\b' | sort -u > /tmp/progress.txt

# 3. diff 应为空（两份文档"已完成"集合一致）
diff /tmp/fwctx.txt /tmp/progress.txt
```

预期：两份文件提取的"已完成优化点编号集合"完全相同。修复后 diff 应返回空。

### 建议修复方案

- 以 `dev/V3.0/PROGRESS.md` 为单一真相源（single source of truth）
- 将 FRAMEWORK_CONTEXT 中的"已完成"清单更新为含 004/005/006/011/014 的完整 12 项
- 长期：在 FRAMEWORK_CONTEXT 顶部增加 `verified_at: <date>` 字段并约定"PROGRESS 变更时同步刷新"规则

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-002

- **类型**: 文档问题（边界泄漏）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

Public 层文件中存在指向 `dev/` 路径的相对引用，违反 `.gitattributes export-ignore` 边界约束。这些引用在 GitHub release tarball / `git archive` 中将变为死链，对终端用户表现为"无法点击的链接"。

确认的真泄漏（视角 A 缺陷）：

1. `core/design_decisions.md` L256：`**V3.0 规划中** (详见 dev/V3.0/)`
2. `core/design_decisions.md` L492：`(设计记录详见框架开发分支中的 dev/V3.0/ 目录)`
3. `core/SUMMARY_FORMAT_SPEC.md` L403：`**反馈**: 如有疑问请在 dev/discussions/ 提出`
4. `agents/_progress/implementation_progress.md` L5：`(../../dev/V3.0/confirmed/001-ai-agent-library/implementation.md)` ← **相对路径直链 dev/，发布版必死**
5. `workflows/doc_error_fix_workflow.md` L507-509：3 处直链 `(../dev/V3.0/confirmed/011-doc-error-fix-workflow/...)` ← **同上，必死**

确认的故意保留（不算缺陷，但应明确标注）：

6. `CONTRIBUTING.md` L1202-1208 整段引用 dev/quality/ —— 因 CONTRIBUTING 面向贡献者，是合理的，但建议在该段开头明确标注"以下路径仅在 dev 分支可见"
7. `CONTRIBUTING.md` L904：`(详见开发分支中的 dev/V3.0/ 目录)` —— 与 #6 同性质

### 影响范围

- 视角 A 用户体验严重受损（链接断裂）
- 模板 / 脚本工具内 0 处 dev/ 引用 —— 用户产品边界封闭（B1 已确认）
- agents/_progress/ 与 workflows/doc_error_fix_workflow.md 中的相对链接最严重，为标准 markdown 链接语法 `[text](path)`，会被 GitHub UI 渲染为失效

### 主要文件路径

- `core/design_decisions.md`
- `core/SUMMARY_FORMAT_SPEC.md`
- `agents/_progress/implementation_progress.md`
- `workflows/doc_error_fix_workflow.md`
- `CONTRIBUTING.md`（仅故意保留段落，需明示）

### 相关文件路径

- `.gitattributes`（dev/ export-ignore 规则定义处）
- `dev/README.md`（边界规则说明文档）

### 具体位置

- `core/design_decisions.md` L256 / L492（文字描述类，影响小）
- `core/SUMMARY_FORMAT_SPEC.md` L403（文字描述类）
- `agents/_progress/implementation_progress.md` L5（markdown 链接，必死）
- `workflows/doc_error_fix_workflow.md` L507 / L508 / L509（3 个 markdown 链接，必死）
- `CONTRIBUTING.md` L904 / L1202-1208（贡献者向，需明示边界）

### 复查方法（验证修复）

```bash
# A. 全仓库 grep dev/ 真引用（剔除 /dev/null shell 假阳性、字符串字面量）
grep -rn --include='*.md' \
  -E '\]\(\.{0,2}/?dev/|\(dev/V[0-9]+\.[0-9]+/' \
  -- core/ workflows/ agents/ templates/ tools/ guides/ config/ \
  AI_ENTRY_POINT.md README.md 2>&1 | grep -v '/dev/null'

# B. 修复后预期：除 CONTRIBUTING.md 段落外，应返回 0 行
# C. 模板 / 工具内泄漏应保持 0 处（B1 已确认基线）
grep -rn --include='*.md' --include='*.py' --include='*.js' \
  -E 'dev/(V[0-9]|quality|architecture|complexity)' \
  -- templates/ tools/ 2>&1 | grep -v '/dev/null' | wc -l
# 预期：0
```

### 建议修复方案

**对于真泄漏 #4 #5（必死链接）**：

- 选项 A：改为指向 ADR 或工作流自身（如指向 `dev/architecture/decisions/004-...md` 的设计意图，但这仍在 dev/ 下，不彻底）
- 选项 B：移除链接，改为纯文字描述（"详见 dev 分支中的 011 设计文档"）
- 选项 C：将 011/001 等关键文档的"用户可见摘要"提取到 Public 层（如 `core/v3-features.md`），并指向该摘要
- **推荐 B**：成本最低，与 `core/design_decisions.md` 已采用的措辞一致

**对于 #1 #2 #3**：

- 已是文字描述非链接，影响小，但建议补充"（仅 dev 分支可见）"明示

**对于 #6 #7**：

- 在该段开头一次性声明"本节涉及框架开发流程，以下 dev/ 路径仅在 dev 分支可见"

### 审查阶段

B0 基线快照（B1 已穷尽性扫描确认无新增）

---

## 问题 ID: AICC-20260425-003

- **类型**: 设计问题（孤儿文件）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）+ A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

仓库根目录存在 `audit_metadata.py`（约 9KB），从命名看应属于 `tools/` 或 `dev/quality/` 下的审查辅助工具，但孤立在仓库根。视角 A 用户克隆仓库后会看到一个用途不明的 .py 文件出现在根级目录，与 README、AI_ENTRY_POINT 等用户入口并列。

### 影响范围

- 视角 A：用户首次浏览仓库时会困惑这个 .py 文件的位置
- 视角 C：违反"工具脚本归位 tools/，开发辅助归位 dev/"的目录约定
- 若该脚本无被引用 → 长期残留死代码

### 主要文件路径

- `audit_metadata.py`（仓库根）

### 相关文件路径

- `tools/py/`（若属通用工具应迁入）
- `dev/quality/`（若仅服务于审查工作流应迁入）

### 具体位置

- 仓库根 `/home2/wenbo/Videos/ai-coding-context/audit_metadata.py`

### 复查方法（验证修复）

```bash
# 1. 确认根目录无孤儿 .py（修复后预期返回空）
ls /home2/wenbo/Videos/ai-coding-context/*.py 2>&1

# 2. 确认是否有任何文件引用它
grep -rn 'audit_metadata' --include='*.md' --include='*.py' --include='*.js' .

# 3. 若已迁入新位置，应在新位置可访问
# ls tools/py/audit_metadata.py 或 ls dev/quality/audit_metadata.py
```

### 建议修复方案

- 阅读 `audit_metadata.py` 内容判断真实用途
- 选项 A：迁入 `tools/py/`（若是通用工具，需补 .js 双脚本对称版本）
- 选项 B：迁入 `dev/quality/`（若仅服务于审查工作流）
- 选项 C：若无明确用途且无引用 → 删除

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-004

- **类型**: 文档问题（编码乱码）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **关联任务/ADR**: Phase 0 commit `3edfbe2`
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/Issue_Recording_Standard.md` 末尾出现 `2025-12-18�更新`（U+FFFD 替换字符）；`dev/quality/Progress_Tracking_Standard.md` 末尾同类乱码 + 出现重复段落（编辑/恢复粘贴痕迹）。

### 影响范围

- AI 解析含 U+FFFD 的文档时可能误判内容
- 文档专业度受损

### 主要文件路径

- `dev/quality/Issue_Recording_Standard.md`
- `dev/quality/Progress_Tracking_Standard.md`

### 相关文件路径

- AICC-20260425-008（同性质，PROGRESS.md 末尾，未修）

### 具体位置

- `dev/quality/Issue_Recording_Standard.md` 末尾（修复前 L99 附近）
- `dev/quality/Progress_Tracking_Standard.md` 末尾（修复前 L150+ 附近）

### 复查方法（验证修复）

```bash
# 1. grep U+FFFD 应返回空
grep -rP '[\x{FFFD}]' dev/quality/*.md

# 2. tail 检查末尾完整性
tail -10 dev/quality/Issue_Recording_Standard.md
tail -10 dev/quality/Progress_Tracking_Standard.md

# 3. 确认 Phase 0 commit 修复
git log --oneline -- dev/quality/Issue_Recording_Standard.md \
  dev/quality/Progress_Tracking_Standard.md | head -5
```

预期：grep 返回空；tail 末尾整洁无乱码；commit `3edfbe2` 包含修复。

### 建议修复方案

Phase 0 commit `3edfbe2` 中已直接修复。无遗留。

**长期防御**：建议加入预提交 hook 检查 U+FFFD 字符：

```bash
# .git/hooks/pre-commit 片段
if git diff --cached --name-only | xargs grep -lP '[\x{FFFD}]' 2>/dev/null; then
  echo "ERROR: U+FFFD character detected. Fix before commit."
  exit 1
fi
```

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-005

- **类型**: 设计问题（自相矛盾）
- **严重级别**: 主要
- **优先级**: 中
- **归属视角**: B（完整性）
- **关联任务/ADR**: Phase 0 commit `3edfbe2`
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/Framework_Review_Guidelines.md` 在多处（L24-26 / L107 / L489-509）声明"跳过 dev/ 目录"，但同时在审查范围中包含 `dev/quality/audits/`、ADR 系统（位于 `dev/architecture/`）、复杂度仪表盘（位于 `dev/complexity/`）等 dev/ 下内容。政策与实际审查范围矛盾。

### 影响范围

- AI 按旧 Guidelines 审查时会跳过 dev/quality 自审环节，使 R5（自指一致性）维度无法落地
- 审查范围声明与实际可执行项割裂，导致 SOP 长期"理论可用、实操不可用"

### 主要文件路径

- `dev/quality/Framework_Review_Guidelines.md`

### 相关文件路径

- `dev/quality/Start_Review.md`（同步使用旧政策的入口）
- `dev/quality/AUDIT_WORKFLOW.md`

### 具体位置

- 修复前 L24-L26（"审查范围"中"跳过 dev/"）
- 修复前 L107（重复声明）
- 修复前 L489-L509（自指审查段落与跳过政策互斥）

### 复查方法（验证修复）

```bash
# 1. 不应再出现"跳过 dev/"等矛盾措辞
grep -nE '跳过 ?dev/|排除 ?dev/' dev/quality/Framework_Review_Guidelines.md

# 2. 应包含三视角分层章节
grep -nE '视角 ?[ABC]|三视角' dev/quality/Framework_Review_Guidelines.md | head -10

# 3. 验证 v1.2 版本号已更新
grep -nE '版本.*1\.2|v1\.2' dev/quality/Framework_Review_Guidelines.md | head
```

预期：grep 1 返回空；grep 2 返回多行（A/B/C 三视角章节）；grep 3 命中 v1.2。

### 建议修复方案

Phase 0 commit `3edfbe2` 中重写为"审核视角分层"机制（A/B/C），统一三视角并存而非二元排除。

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-006

- **类型**: 设计问题（基础设施长期缺失）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: B+C
- **关联任务/ADR**: Phase 0 commit `3edfbe2`
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/` 体系建立以来：

- `contexts/` 目录除 `_template.md` 外**实际为空**，但方法论文档反复声明应有 30+ 文档的 context
- `audits/` 目录在多处 SOP 中被引用为唯一归档位置，**物理上从未创建**
- 这两项使整套审查体系长期处于"理论可用、实操不可用"状态

### 影响范围

- 任何尝试启动审查的 AI 或人类都会卡在"找不到 contexts/"或"audits/ 不存在"
- AICC 的 dogfood（自审）能力被冻结
- F-5 / F-6 共同导致 quality/ 体系成熟度极低

### 主要文件路径

- `dev/quality/contexts/`
- `dev/quality/audits/`

### 相关文件路径

- `dev/quality/README.md`（旧版索引）
- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md`（"应有 30+ contexts"声明源）

### 具体位置

- `dev/quality/contexts/` 修复前仅有 `_template.md`
- `dev/quality/audits/` 修复前不存在

### 复查方法（验证修复）

```bash
# 1. audits/ 目录及 README 已存在
ls dev/quality/audits/README.md

# 2. 本轮 round 目录与 5 件套已存在
ls dev/quality/audits/2026-04-25_V3.x_Comprehensive/
# 预期含：Review_Plan.md / Issue_Tracking.md / Progress_Tracking.md
#         Review_Log.md / Review_Checklist.md

# 3. contexts/ 改为按需策略，README v2.0 应说明三级优先级
grep -nE '🔴|🟡|⚪' dev/quality/README.md | head -10
```

### 建议修复方案

Phase 0 commit `3edfbe2` 中：

- 创建 `audits/` 目录及 README（命名规范、5 件套结构）
- 创建本轮 round 目录 `2026-04-25_V3.x_Comprehensive/`
- contexts/ 改为 v2.0 的"按需生成"策略（🔴 优先级独立 context、🟡 同类批审、⚪ 仅合规扫描），不再要求每个文件都有

**教训**：长期未创建的目录暗示"sop 写完就没人真的用"——应配合 dogfood 机制周期性触发使用。

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-007

- **类型**: 文档问题（被引用但缺失）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B
- **关联任务/ADR**: Phase 0 commit `3edfbe2`
- **状态**: 🟢 已修复（Phase 0 处理）

### 问题描述

`dev/quality/standards/BY_DOCUMENT_TYPE.md` 在多处被引用：

- `HOW_TO_GENERATE_CONTEXTS.md` L725、L282
- `standards/COMMON_STANDARDS.md` L268
- `standards/QUALITY_CHECKLIST.md` L171

但实际**文件不存在**。属于"标准被宣告但未实现"的设计漏洞。

### 影响范围

- 任何沿引用链查找该文件的 AI/人类会得到 404
- 失去"按文档类型分项审查"的能力（10 类专项标准缺位）

### 主要文件路径

- `dev/quality/standards/BY_DOCUMENT_TYPE.md`

### 相关文件路径

- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md`
- `dev/quality/standards/COMMON_STANDARDS.md`
- `dev/quality/standards/QUALITY_CHECKLIST.md`

### 具体位置

- `HOW_TO_GENERATE_CONTEXTS.md` L725、L282
- `standards/COMMON_STANDARDS.md` L268
- `standards/QUALITY_CHECKLIST.md` L171

### 复查方法（验证修复）

```bash
# 1. 文件已存在
ls dev/quality/standards/BY_DOCUMENT_TYPE.md

# 2. 内容覆盖 10 类（入口/core/workflows/agents/tools/templates/guides/config/ADR/quality）
grep -E '^##' dev/quality/standards/BY_DOCUMENT_TYPE.md | head -15

# 3. 所有引用方仍能定位
grep -rn 'BY_DOCUMENT_TYPE' dev/quality/ --include='*.md'
```

预期：文件存在；至少 10 个二级标题覆盖各类型；引用方均能解析。

### 建议修复方案

Phase 0 commit `3edfbe2` 中创建该文件，覆盖入口/core/workflows/agents/tools/templates/guides/config/ADR/quality 自身共 10 类专项标准。每节含：必需章节 / 特定检查项 / 常见反模式 / V3.0 双版本+零依赖合规扫描命令。

### 审查阶段

B0 基线快照（修复时间相同）

---

## 问题 ID: AICC-20260425-008

- **类型**: 文档问题（编码乱码 + 末尾重复）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C
- **关联任务/ADR**: 同 AICC-20260425-004（同性质）
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/PROGRESS.md` L290-L312 末尾存在数据损坏：

```
**最后更新**: 2026-04-22
发布
```

（"发布"是孤字，紧接一个未闭合的 ``` 代码块）

随后 L294-L312 整段重复了 `## 🔗 相关链接` / `## 状态图例` / `**最后更新**` 三个块。与 AICC-20260425-004 同性质（编辑事故残留）。

### 影响范围

- 解析 PROGRESS.md 的 AI 可能因未闭合代码块而误判后续内容
- 重复段落使文档臃肿、降低阅读体验

### 主要文件路径

- `dev/V3.0/PROGRESS.md`

### 相关文件路径

- 无（独立问题）

### 具体位置

- L289-L312（含未闭合代码块、孤字"发布"、重复段落）

### 复查方法（验证修复）

```bash
# 1. 文件末尾应整洁，无孤字"发布"
tail -25 dev/V3.0/PROGRESS.md

# 2. 未闭合 ``` 检查（开闭对应数应为偶数）
grep -c '^```' dev/V3.0/PROGRESS.md
# 修复前为奇数；修复后应为偶数

# 3. "## 🔗 相关链接" 应只出现一次
grep -c '^## 🔗 相关链接' dev/V3.0/PROGRESS.md
# 预期：1（修复前为 2）

# 4. "状态图例"应只出现一次
grep -c '^\*\*状态图例\*\*' dev/V3.0/PROGRESS.md
# 预期：1
```

### 建议修复方案

- 删除 L290-L312 中的重复段落与孤字"发布"
- 保留单份"状态图例 / 最后更新"
- 与 AICC-20260425-004 一并加入 pre-commit hook 检查 U+FFFD 与未闭合代码块

### 审查阶段

B0 基线快照

---

## 问题 ID: AICC-20260425-009

- **类型**: 文档问题（dev/ 内部悬空引用）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/reference/commit_as_prompt_analysis.md` L699 引用 `dev/V3.0/pending/018-commit-guided-documentation.md`，但 `pending/` 目录已不存在（018 已迁移至 `dev/V3.0/confirmed/018-commit-guided-documentation/`）。属于历史迁移残留的悬空引用。

### 影响范围

- dev 分支内部读者沿引用查找会得到 404
- 视角 C 完整性受损（小范围）

### 主要文件路径

- `dev/V3.0/reference/commit_as_prompt_analysis.md`

### 相关文件路径

- `dev/V3.0/confirmed/018-commit-guided-documentation/`（应替换的目标）
- `dev/V3.0/pending/`（已不存在）

### 具体位置

- L699: `1. **创建优化点文档**: \`dev/V3.0/pending/018-commit-guided-documentation.md\``

### 复查方法（验证修复）

```bash
# 1. 不应再出现 V3.0/pending/ 引用
grep -rn 'V3\.0/pending/' dev/V3.0/ --include='*.md'

# 2. 全 dev/ 下 pending/ 引用扫描
grep -rn 'pending/' dev/ --include='*.md' | grep -v 'archived\|confirmed/.*pending'

# 3. confirmed/018 目标应存在
ls dev/V3.0/confirmed/018-commit-guided-documentation/
```

### 建议修复方案

- 改为：`dev/V3.0/confirmed/018-commit-guided-documentation/`
- 或加注："（注：本文档为历史分析，018 已 confirmed，详见 confirmed/018-...）"
- 同步检查 dev/V3.0/reference/ 下其他历史分析文档是否有类似悬空引用

### 审查阶段

B1 R3 引用与边界扫描

---

## 问题 ID: AICC-20260425-010

- **类型**: 设计问题（文件位置疑似错误）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/archived/advanced-audit-report.md` 不符合该目录命名规范 `NNN-name.md`（其他归档项均为 `002-...md` / `007-...md` 等优化点编号）。`PROGRESS.md` 中列出的归档优化点为 5 项（002 / 007 / 008 / 009 / 015），不含 advanced-audit-report，说明这不是被归档的优化点，可能是一份审查报告被错放。

### 影响范围

- 视角 C：archived/ 目录命名一致性受损
- 可能与 V3.0 优化点档案混淆，干扰后续审查者

### 主要文件路径

- `dev/V3.0/archived/advanced-audit-report.md`

### 相关文件路径

- `dev/quality/audits/`（若是审查报告应迁此）
- `dev/V3.0/reference/`（若是分析报告应迁此）

### 具体位置

- `dev/V3.0/archived/advanced-audit-report.md`（整文件）

### 复查方法（验证修复）

```bash
# 1. archived/ 下应仅含 NNN-name.md 形式（修复后预期不含 advanced-audit-report）
ls dev/V3.0/archived/

# 2. 确认每个文件名匹配 NNN-... 模式
ls dev/V3.0/archived/ | grep -vE '^[0-9]{3}-' | grep -v '^README'
# 预期：返回空

# 3. 若迁入 reference/ 或 audits/，新位置应可访问
ls dev/V3.0/reference/advanced-audit-report.md 2>/dev/null \
  || ls dev/quality/audits/*advanced-audit*  2>/dev/null
```

### 建议修复方案

- 阅读其内容判断真实属性
- 选项 A：迁入 `dev/V3.0/reference/`（若是分析报告）
- 选项 B：迁入 `dev/quality/audits/` 历史归档区（若是审查报告）
- 不应留在 archived/

### 审查阶段

B1 R3 引用与边界扫描（附带观察）

---

## 问题 ID: AICC-20260425-011

- **类型**: 文档问题（顶部摘要严重过时）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: B（完整性）+ A（用户）
- **关联任务/ADR**: 与 AICC-20260425-001 同主题，本条更精确定位
- **状态**: 🔴 待修复

### 问题描述

`dev/FRAMEWORK_CONTEXT.md` L14-L23 顶部"V3.0 已完成模块"清单严重过时：

**当前列出（8 项）**：001 / 003 / 012 / 013 / 016 / 017 / 018 / 019

**实际已完成（PROGRESS.md 验证 12 项）**：001 / 003 / 004 / 005 / 006 / 011 / 012 / 013 / 014 / 016 / 017 / 018

**漏列**：004（ADR）/ 005（复杂度仪表盘）/ 006（自动审查报告）/ 011（文档谬误修复）/ 014（文档阅读习惯）—— 共 5 项 P1 已完成功能未在顶部摘要体现。

文档底部 L703-L714 的"V3.0 章节"列出了 11 项（含 004/005/006/019），但仍漏 011 和 014；且写"(10/17)"，与列举的 11 项数字不符。

### 影响范围

- AI 或新读者读完 L14-L23 后会得出"V3.0 P1 仍在规划中"的错误结论
- L25-L28 "剩余关键能力（规划中）"列"ADR 系统、复杂度仪表盘、自动审查报告"会进一步加深这个错误印象
- R2（V3.0 落地一致性）的核心风险体现

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`

### 相关文件路径

- `dev/V3.0/PROGRESS.md`（权威源）
- `dev/V3.0/confirmed/`（实体档案）

### 具体位置

- L11-L29：顶部"已完成模块 / 剩余关键能力"
- L25-L28：P1/P2 状态标注与 L712-L714 实际状态矛盾
- L703-L714：V3.0 章节列举漏 011/014，且数字 "(10/17)" 与列出的 11 项矛盾

### 复查方法（验证修复）

```bash
# 1. 顶部摘要应包含全部 12 项已完成编号
sed -n '14,30p' dev/FRAMEWORK_CONTEXT.md \
  | grep -oE '\b0[0-1][0-9]\b' | sort -u
# 预期：001 003 004 005 006 011 012 013 014 016 017 018

# 2. 文档底部数字应一致
grep -nE '\(10/17\)|\(11/17\)|\(12/18\)' dev/FRAMEWORK_CONTEXT.md
# 修复后预期仅命中 (12/18)

# 3. 与 PROGRESS.md L18 的 12 项交叉验证
sed -n '18p' dev/V3.0/PROGRESS.md
# 预期含 011 / 014 等全部 12 项编号
```

### 建议修复方案

- 将顶部"V3.0 已完成模块"清单同步到 12 项（含 004/005/006/011/014）
- 删除 L25-L28 中 P1 已完成项的"规划中"措辞
- L703 改为 "(12/18)"，列出全部 12 项
- 长期：约定 PROGRESS.md 为单一真相源，FRAMEWORK_CONTEXT 仅做"快照引用"+ verified_at 时间戳要求

### 审查阶段

B2 R2 V3.0 一致性核查

---

## 问题 ID: AICC-20260425-012

- **类型**: 文档问题（自身内部不一致）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/PROGRESS.md` 自身内部不一致：

- L18：列出已完成 11 项 `(001, 003, 004, 005, 006, 012, 013, 016, 017, 018, 014)`，**漏 011**
- L88：011-文档谬误修复工作流标记为 `[x] ✅`
- L34：P1 计数 `(5个 (004 ✅, 005 ✅, 006 ✅, 011 🟢, 014 ✅))` 中 011 用 🟢（开发中），与 L88 的 ✅（完成）不一致

L18 是顶部统计面板，文档第一眼可见；遗漏 011 让"已完成"的人类可读数字与详细任务清单不一致。

### 影响范围

- 直接读 PROGRESS.md 的人会被 L18 误导
- AI 解析"已完成 11 个"会与 L88 的 12 个 [x] 计数不一致

### 主要文件路径

- `dev/V3.0/PROGRESS.md`

### 相关文件路径

- 无（自指问题）

### 具体位置

- L18：`已完成: 11个 (001, 003, 004, 005, 006, 012, 013, 016, 017, 018, 014)` 应改为 12 项含 011
- L34：P1 计数中 011 状态符号 🟢 应改为 ✅
- L88：（正确） `[x] 实现文档谬误修复工作流 (011) ✅`

### 复查方法（验证修复）

```bash
# 1. 已完成项应为 12 个
grep -oE '已完成: ?[0-9]+个' dev/V3.0/PROGRESS.md | head -1
# 预期："已完成: 12个"

# 2. L18 编号集合应含 011
sed -n '18p' dev/V3.0/PROGRESS.md | grep -oE '\b0[0-1][0-9]\b' | sort -u
# 预期含 011

# 3. P1 中 011 状态应为 ✅
grep -E '011 ?[✅🟢]' dev/V3.0/PROGRESS.md
# 预期所有匹配均为 ✅
```

### 建议修复方案

- L18 改为：`已完成: 12个 (001, 003, 004, 005, 006, 011, 012, 013, 014, 016, 017, 018)`
- L34 中 011 的 🟢 改为 ✅
- 同步检查 P1 计数 `(5个)` 是否对应（应为 5 项 P1 已完成 = 004/005/006/011/014）

### 审查阶段

B2 R2 V3.0 一致性核查

---

## 问题 ID: AICC-20260425-013

- **类型**: 文档问题（路径引用错误）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B+C
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/FRAMEWORK_CONTEXT.md` 同一文档中对相同文件给出两处不同路径：

- L539：`查阅 reference/SUMMARY_FORMAT_SPEC.md`
- L540：`查阅 reference/design_decisions.md`
- L744-L745（正确）：`core/design_decisions.md` / `core/SUMMARY_FORMAT_SPEC.md`

实际文件位置在 `core/`（已通过 `ls /home2/wenbo/Videos/ai-coding-context/core/` 验证）。

L539-L540 是面向 AI 在审查工作流中的指引，会直接误导 AI 去 `reference/` 下找文件。

### 影响范围

- AI 按 L539-L540 索引会失败找不到文件
- 同一文档自相矛盾，影响可信度

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`

### 相关文件路径

- `core/SUMMARY_FORMAT_SPEC.md`（实体）
- `core/design_decisions.md`（实体）

### 具体位置

- L539、L540（错误，路径前缀写成 `reference/`）
- L744、L745（正确，前缀 `core/`，可作为修订模板）

### 复查方法（验证修复）

```bash
# 1. 不应再出现 reference/SUMMARY_FORMAT_SPEC 或 reference/design_decisions
grep -nE 'reference/(SUMMARY_FORMAT_SPEC|design_decisions)' dev/FRAMEWORK_CONTEXT.md
# 预期：返回空

# 2. core/ 路径应至少出现 2 次（L539-540 + L744-745 = 4 次）
grep -nE 'core/(SUMMARY_FORMAT_SPEC|design_decisions)' dev/FRAMEWORK_CONTEXT.md
# 预期：>= 4 行

# 3. 文件实体存在性
ls core/SUMMARY_FORMAT_SPEC.md core/design_decisions.md
```

### 建议修复方案

- 将 L539 改为：`查阅 core/SUMMARY_FORMAT_SPEC.md`
- 将 L540 改为：`查阅 core/design_decisions.md`
- 同步审查 dev/FRAMEWORK_CONTEXT.md 内是否还有其他 `reference/` 前缀的错引用

### 审查阶段

B2 R2 V3.0 一致性核查

---

## 问题 ID: AICC-20260425-014

- **类型**: 文档问题（同一文档自相矛盾）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: B
- **关联任务/ADR**: 与 AICC-20260425-011 关联（同一文档不同位置）
- **状态**: 🔴 待修复

### 问题描述

`dev/FRAMEWORK_CONTEXT.md` 同一文档前后矛盾：

- L25-L28："**剩余关键能力（规划中）**：P1：ADR 系统、复杂度仪表盘、自动审查报告"
- L712-L714：将 ADR 系统、复杂度仪表盘、自动审查报告全部列为 "✅" 已完成

L25-L28 在 V3.0 概览章节，会让读者形成"P1 还没完成"的第一印象，但实际三项都已完成。

### 影响范围

- 与 011 联合作用：新读者前 30 行就形成"V3.0 P1 还在规划中"的错误印象
- 文档可信度受损

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`

### 相关文件路径

- `dev/V3.0/PROGRESS.md`（真相源）

### 具体位置

- L25-L28（错误，把已完成项列为"规划中"）
- L703-L714（正确，含 ✅ 标识）

### 复查方法（验证修复）

```bash
# 1. L25-L28 不应再出现 P1 已完成项被列为"规划中"
sed -n '25,30p' dev/FRAMEWORK_CONTEXT.md | grep -E 'ADR|复杂度仪表盘|自动审查'
# 修复后预期：返回空，或明确标注为"已完成"

# 2. L703-L714 V3.0 章节应保持 ADR/复杂度/审查报告的 ✅
sed -n '703,716p' dev/FRAMEWORK_CONTEXT.md | grep -cE '004|005|006'
# 预期：>= 3
```

### 建议修复方案

- L25-L28 改写为："**剩余关键能力**：P1 部分已完成 (004/005/006/011/014)，剩余 015 (质量保证体系集成)；P2 进行中 (010 跨项目知识复用)，规划中 (002/007/008/009)"
- 或合并到 L703-L714 的版本演进章节，删除顶部冗余清单

### 审查阶段

B2 R2 V3.0 一致性核查

---

## 问题 ID: AICC-20260425-015

- **类型**: 设计问题（已完成但未登记）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: B（完整性）+ C（dev 卫生）
- **关联任务/ADR**: B4 自指审查阶段一并讨论
- **状态**: 🔴 待修复

### 问题描述

`019-系统化文档审核框架` 在 `dev/FRAMEWORK_CONTEXT.md` L23 与 L711 被列为"已完成"，但 `dev/V3.0/PROGRESS.md` 的 18 个优化点清单 (L16-L41) 中**没有 019 这一项**：

- 总优化点：18 个
- 已确认 13 个 / 已归档 5 个 / 已完成 11 个
- 11 项已完成中无 019
- 18 个优化点的官方编号到 018 截止

实际 019 的实体存在 (`templates/review/`、`workflows/generation_workflow.md` 等)，是真功能。但其"开发请求"从未在 V3.0 优化点池中正式登记。

可能背景：019 是 V3.0 后期突生需求，源于 `dev/case_skillatlas_review/` 的实践；它不在原 V3.0 18 项规划范围内。

PROGRESS.md L16 总计写 `总优化点: 18个`，FRAMEWORK_CONTEXT.md L703 写 `(10/17)` —— 总数本身也不一致（17 vs 18）。

### 影响范围

- 019 实体存在但无追溯档案，违反"每个优化点须有 confirmed/ 档案"约定
- 视角 B：项目目录治理一致性
- 视角 C：dev/V3.0/ 体系自身的"优化点池"完整性

### 主要文件路径

- `dev/FRAMEWORK_CONTEXT.md`
- `dev/V3.0/PROGRESS.md`

### 相关文件路径

- `dev/V3.0/confirmed/`（应增加 019 档案）
- `dev/V3.0/archived/`（备选位置）
- `dev/case_skillatlas_review/`（019 来源案例）
- `templates/review/`、`workflows/generation_workflow.md`（019 实体产物）

### 具体位置

- `dev/FRAMEWORK_CONTEXT.md` L23：`✅ 019-系统化文档审核框架`
- `dev/FRAMEWORK_CONTEXT.md` L711：`✅ 019-系统化文档审核框架 (2026-04-11)`
- `dev/FRAMEWORK_CONTEXT.md` L703：`已完成 (10/17)` ← 总数 17
- `dev/V3.0/PROGRESS.md` L16：`总优化点: 18个` ← 总数 18
- `dev/V3.0/PROGRESS.md` L16-L41：18 项清单不含 019

### 复查方法（验证修复）

```bash
# 1. 019 应在 PROGRESS 中正式登记（选项 A 修复后）
grep -nE '019|系统化文档审核' dev/V3.0/PROGRESS.md

# 2. confirmed/ 下应有 019 档案
ls dev/V3.0/confirmed/ | grep '^019-'

# 3. 总数一致性
grep -E '总优化点|\([0-9]+/[0-9]+\)' dev/V3.0/PROGRESS.md dev/FRAMEWORK_CONTEXT.md
# 预期：FRAMEWORK_CONTEXT 与 PROGRESS 总分母一致（18 = 18 或 19 = 19）

# 4. 实体仍存在
ls templates/review/ workflows/generation_workflow.md
```

### 建议修复方案

- **选项 A（推荐）**：在 `dev/V3.0/confirmed/019-systematic-review-framework/` 下创建 019 的优化点档案，将其追溯登记入 PROGRESS.md L18（已完成项 +1 = 13 项），并将总数从 18 调整为 19
- 选项 B：承认 019 不属于原 V3.0 优化点池，从 FRAMEWORK_CONTEXT 中移除"019 系统化文档审核框架"，独立成"V3.0+ 后期增益"章节
- 同步统一 FRAMEWORK_CONTEXT L703 与 PROGRESS L16 的总数（推荐 A 后均为 19）

### 审查阶段

B2 R2 V3.0 一致性核查（B4 自指审查时复审）

---

## 问题 ID: AICC-20260425-016

- **类型**: 文档问题（命名大小写不一致）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

AI Rules 文件名在 AICC 框架不同位置存在大小写不一致：

- `workflows/path_a_first_generation.md` L752、L756：使用 **`ai_rules.md`**（小写）
- `AI_ENTRY_POINT.md` L157、术语表 L306：使用 **`AI_RULES.md`**（大写）
- `templates/AI_RULES_TEMPLATE.md` L541：生成目标 **`dev_docs/AI_RULES.md`**（大写）

剧本 1（首次生成 path_a）的关键收尾步骤"Step 8.4 生成 AI Rules 文件"（path_a L754-L770）让 AI 写入 `ai_rules.md`（小写），但其他所有引用都是 `AI_RULES.md`（大写）。

Linux/macOS 文件系统区分大小写：
- 若 AI 按 path_a 生成 `ai_rules.md`，后续 IDE 集成（依赖 `AI_RULES.md`）将失败
- 若 AI 修正为大写，path_a 自身逻辑就跟其他位置错位

### 影响范围

- 剧本 1（首次生成）的最后一步产出格式不确定
- 用户 IDE 集成链路（AI_RULES.md → IDE rules）会断裂
- R1（工作流闭环）核心剧本的产物格式不可信

### 主要文件路径

- `workflows/path_a_first_generation.md`
- `AI_ENTRY_POINT.md`
- `templates/AI_RULES_TEMPLATE.md`

### 相关文件路径

- `core/framework_spec.md`（应权威约定文件名规范）
- `guides/ai_rules_maintenance.md`（AI Rules 维护指南）

### 具体位置

- `workflows/path_a_first_generation.md` L752：`6. **AI Rules 文件** \`ai_rules.md\`（根目录）`
- `workflows/path_a_first_generation.md` L756：`**位置**: 项目根目录 \`ai_rules.md\``
- `AI_ENTRY_POINT.md` L157：`- AI_RULES.md`（在"分析目标"列表中）
- `AI_ENTRY_POINT.md` L306-L307：术语表标准写法 `AI_RULES.md`
- `templates/AI_RULES_TEMPLATE.md` L541：`AI 生成更新后的 rule 到\`dev_docs/AI_RULES.md\``

### 复查方法（验证修复）

```bash
# 1. 全仓库统一为大写 AI_RULES.md
grep -rn '\bai_rules\.md\b' --include='*.md' .
# 修复后预期：返回空（或仅 .gitignore / 历史归档中保留）

# 2. AI_RULES.md 应在所有关键路径被一致引用
grep -rn 'AI_RULES\.md' --include='*.md' \
  workflows/ AI_ENTRY_POINT.md templates/AI_RULES_TEMPLATE.md core/ guides/
# 修复后所有引用大小写一致

# 3. Linux 测试（区分大小写）
test -f templates/AI_RULES_TEMPLATE.md && echo OK  # 模板大写
```

### 建议修复方案

- 以 `AI_ENTRY_POINT.md` 术语表 L306 为权威源（`AI_RULES.md` 大写）
- 修订 `workflows/path_a_first_generation.md` L752、L756 的 `ai_rules.md` → `AI_RULES.md`
- 全仓库 grep 一次确保无遗漏
- 长期：在 `core/framework_spec.md` 中明确"文件名大小写规范"章节

### 审查阶段

B3 R1 工作流端到端闭环（剧本 1）

---

## 问题 ID: AICC-20260425-017

- **类型**: 集成问题（工具实体缺失）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`tools/py/doc_health_checker.py` 与 `tools/js/doc_health_checker.js` 在多处工作流被引用为关键步骤，但**实体均不存在**：

- `workflows/commit_guided_update.md` L372：`python tools/py/doc_health_checker.py --file dev_docs/api_layer.md`（剧本 2 Step 7 验证步骤）
- `workflows/maintenance_workflow.md` L176：`python tools/py/doc_health_checker.py --check-code-samples`
- `workflows/maintenance_workflow.md` L179：`node tools/js/doc_health_checker.js --check-code-samples`
- `workflows/maintenance_workflow.md` L202：`python tools/py/doc_health_checker.py --check-file-paths`
- `workflows/maintenance_workflow.md` L224：`python tools/py/doc_health_checker.py --check-dependencies`
- `workflows/maintenance_workflow.md` L420：`python tools/py/doc_health_checker.py --full-check`

`ls tools/py/ tools/js/` 仅有 `doc_dependency_tracer.py/.js` 与 `doc_fix_executor.py/.js`，**无 doc_health_checker**。

剧本 2（commit-guided）的 Step 7 文档验证、维护工作流的 4 大健康检查命令均无可执行实体。

### 影响范围

- 剧本 2（commit-guided）Step 7 验证环节断裂
- 整个 maintenance 工作流（document health check 路径 B）的核心命令均失效
- 双脚本对称性（Py/JS）在 V3.0 红线下被违反（声称两端都有，实则两端都无）
- AI 按文档执行会因 `command not found` 失败

### 主要文件路径

- `tools/py/doc_health_checker.py`（应存在但不存在）
- `tools/js/doc_health_checker.js`（应存在但不存在）

### 相关文件路径

- `workflows/commit_guided_update.md` L372
- `workflows/maintenance_workflow.md` L176-L420
- `workflows/document_health_check.md`（应统一定义健康检查工具职责）
- `tools/README.md`（工具索引应反映实体状态）

### 具体位置

- 引用方共 6 处（见上文列表）
- 实体应位于 `tools/py/doc_health_checker.py` 与 `tools/js/doc_health_checker.js`

### 复查方法（验证修复）

```bash
# 1. 文件应存在
ls tools/py/doc_health_checker.py tools/js/doc_health_checker.js

# 2. 双脚本应支持文档中调用的所有参数
python tools/py/doc_health_checker.py --help 2>&1 | grep -E '\-\-file|\-\-check-code-samples|\-\-check-file-paths|\-\-check-dependencies|\-\-full-check'
# 预期 5 个参数全部命中

# 3. 双脚本零依赖（V3.0 红线）
grep -nE '^import |^from ' tools/py/doc_health_checker.py | grep -vE 'os|sys|json|re|argparse|pathlib|subprocess|datetime|typing|collections|dataclasses|enum'
# 预期：空（仅标准库）

grep -nE '^const .* = require' tools/js/doc_health_checker.js | grep -vE "'fs'|'path'|'os'|'crypto'|'child_process'|'util'"
# 预期：空（仅原生 Node 模块）

# 4. 全仓库引用方均能解析
grep -rn 'doc_health_checker' workflows/ tools/README.md
```

### 建议修复方案

- **选项 A（推荐）**：实施 `doc_health_checker.py/.js` 双脚本，覆盖 4 项检查能力（code-samples / file-paths / dependencies / full-check）。等同于 005-复杂度仪表盘 + 011-文档谬误工具链的"文档健康检查"分支。
- **选项 B**：删除引用，将 4 项检查能力合并到 `complexity_scanner.py` 或拆入现有 `doc_dependency_tracer.py` + `summary_validator.py`，并修订所有引用方
- 推荐 A：当前 6 处文档引用都假设这是独立工具；修补成本低于重写工作流

### 审查阶段

B3 R1 工作流端到端闭环（剧本 2）

---

## 问题 ID: AICC-20260425-018

- **类型**: 文档问题（路径假设错误）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`workflows/doc_error_fix_workflow.md` L488-L491 的测试命令假定仓库根存在 `tests/` 目录，但**实际不存在**：

```bash
# L488
python -m pytest tests/ -v -k "doc_error"

# L491
python -m pytest tests/integration/ -v -k "doc_fix"
```

仓库实际测试位置：

- `tools/py/tests/`（仅 `test_commit_integrity_validator.py` + `test_git_safety.py`）
- `tools/js/`（含 `commit_template_cli.test.js` / `install_hooks.test.js` / `integration.test.js`）

无任何 `tests/` 或 `tests/integration/` 在仓库根。AI 按 doc_error_fix L488-L491 的命令执行会得到 `ERROR: file or directory not found: tests/`。

### 影响范围

- 剧本 3（文档谬误修复）的"测试和验证"章节命令不可执行
- 用户/AI 调试时会困惑"为什么文档说有 tests/"
- 文档假设与实际测试组织方式脱节

### 主要文件路径

- `workflows/doc_error_fix_workflow.md`

### 相关文件路径

- `tools/py/tests/`（实际位置）
- `tools/js/`（含 *.test.js）

### 具体位置

- L484-L491 测试和验证章节：

```bash
# 运行工具测试
python -m pytest tests/ -v -k "doc_error"

# 集成测试
python -m pytest tests/integration/ -v -k "doc_fix"
```

### 复查方法（验证修复）

```bash
# 1. 修复后命令应能定位实际测试目录
ls tools/py/tests/ tools/js/*.test.js

# 2. 文档命令应改为指向实际位置
grep -nE 'pytest tests/|pytest tools/py/tests/' workflows/doc_error_fix_workflow.md
# 修复后预期仅命中 tools/py/tests/

# 3. AI 按文档执行命令应不报错
cd /home2/wenbo/Videos/ai-coding-context && python -m pytest tools/py/tests/ -v -k "test_" --collect-only 2>&1 | head -5
```

### 建议修复方案

- 将 L488 改为：`python -m pytest tools/py/tests/ -v -k "doc_error"`
- 将 L491 改为：`# 当前无 doc_fix 集成测试；建议补充 tools/py/tests/integration/doc_fix_test.py`
- 同步审查 doc_error_fix_workflow.md 内是否还有其他类似根级路径假设

### 审查阶段

B3 R1 工作流端到端闭环（剧本 3）

---

## 问题 ID: AICC-20260425-019

- **类型**: 设计问题（端到端工作流缺失）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 005 复杂度仪表盘
- **状态**: 🔴 待修复

### 问题描述

剧本 4（复杂度告警 → 决策）**没有任何工作流文档定义端到端流程**：

- ✅ 实体存在：
  - `tools/py/complexity_scanner.py` + `tools/js/complexity_scanner.js`
  - `tools/py/report_generator.py` + `tools/js/report_generator.js`
  - `dev/complexity/config.yaml`（阈值定义：warning / critical / crisis）
  - `dev/complexity/dashboard/` + `dev/complexity/data/`

- 🔴 流程文档缺失：
  - `AI_ENTRY_POINT.md` 文件索引中**完全无 complexity_scanner**（不在"实用工具库"段、不在"路由索引"）
  - `workflows/path_d_specific_tasks.md` 的 `@think` / `@review` 等显式指令清单中**无 @complexity 或类似指令**
  - 无 `workflows/complexity_alert_workflow.md` 或类似文档定义"扫描 → 阈值判断 → 告警 → 决策建议 → 用户响应"完整闭环
  - 仅 `tools/README.md` L42 一行简单描述

工具完整但缺触发路径，导致 AI 不知道何时主动调用 complexity_scanner，用户也不清楚如何启用此能力。

### 影响范围

- R1（工作流闭环）维度的 4 大剧本中只有这一个无文档定义
- 005-复杂度仪表盘虽实体已落地，但用户感知不到 → 实际价值未释放
- 与 R4（新用户旅程）相关：B5 阶段会再确认"用户能否被引导到这能力"

### 主要文件路径

- `workflows/`（应新增 `complexity_alert_workflow.md`）
- `AI_ENTRY_POINT.md`（应增加 @complexity 路由）
- `workflows/path_d_specific_tasks.md`（应增加 @complexity 段落）

### 相关文件路径

- `tools/py/complexity_scanner.py`
- `tools/py/report_generator.py`
- `dev/complexity/config.yaml`
- `dev/V3.0/confirmed/005-complexity-dashboard/`（应有完整设计可参考）

### 具体位置

- `AI_ENTRY_POINT.md` L488-L510 实用工具库 / 路由索引（应增加复杂度入口）
- `workflows/path_d_specific_tasks.md` L21-L40 显式指令清单（应增加 @complexity）

### 复查方法（验证修复）

```bash
# 1. AI_ENTRY_POINT 应索引复杂度工具
grep -nE 'complexity_scanner|@complexity|complexity_alert' AI_ENTRY_POINT.md

# 2. path_d 应有 @complexity 指令章节
grep -nE '@complexity' workflows/path_d_specific_tasks.md
# 预期：有专门一节

# 3. 新工作流文档应存在
ls workflows/complexity_alert_workflow.md

# 4. 端到端剧本可演练
python tools/py/complexity_scanner.py --since "1 day ago" --output /tmp/c.json && \
python tools/py/report_generator.py --data /tmp/c.json --output /tmp/c.md
ls /tmp/c.md  # 应存在
```

### 建议修复方案

1. 新建 `workflows/complexity_alert_workflow.md`，定义：
   - 触发条件（@complexity 指令 / commit hook / 周期定时）
   - 7 步流程：扫描 → 解析 → 阈值判定（参考 dev/complexity/config.yaml）→ 风险归类 → 报告生成 → 用户决策选项 → 执行/记录
   - 与 005-complexity-dashboard 设计文档对齐
2. 在 `AI_ENTRY_POINT.md` 文件索引中补充复杂度工具行
3. 在 `workflows/path_d_specific_tasks.md` 增加 `@complexity` 指令章节
4. 在 `tools/README.md` 中扩充 complexity_scanner 用法示例与触发场景

### 审查阶段

B3 R1 工作流端到端闭环（剧本 4）

---

## 问题 ID: AICC-20260425-020

- **类型**: 文档问题（命令参数不存在）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`workflows/document_health_check.md` L418 给出命令：

```bash
python tools/py/complexity_scanner.py --path . --check-doc-errors
```

但 `tools/py/complexity_scanner.py` 实际仅支持 4 个参数：

- `--path PATH`
- `--output OUTPUT`
- `--since SINCE`
- `--config CONFIG`

**`--check-doc-errors` 不存在**。AI 按文档执行此命令会得到 argparse 错误：`unrecognized arguments: --check-doc-errors`。

### 影响范围

- 剧本 4（复杂度告警）与"文档健康检查"路径的衔接失效
- AI 可能尝试调用并失败，导致用户体验受损

### 主要文件路径

- `workflows/document_health_check.md`

### 相关文件路径

- `tools/py/complexity_scanner.py` L592-L595 argparse 定义处
- `dev/V3.0/confirmed/005-complexity-dashboard/`（设计文档应说明扩展点）

### 具体位置

- `workflows/document_health_check.md` L418

### 复查方法（验证修复）

```bash
# 1. complexity_scanner 是否真的支持 --check-doc-errors
python tools/py/complexity_scanner.py --check-doc-errors --path . 2>&1 | head -5
# 修复前：unrecognized arguments
# 修复后选项 A（实现参数）：正常运行
# 修复后选项 B（删除引用）：文档不再含此命令

# 2. 文档与工具同步
grep -n 'check-doc-errors' workflows/ tools/py/complexity_scanner.py -r
# 预期：要么两边都有，要么两边都无
```

### 建议修复方案

- **选项 A**：在 `complexity_scanner.py` 中实施 `--check-doc-errors` 子命令，支持文档错误扫描
- **选项 B（推荐）**：从 `document_health_check.md` L418 删除该命令，改为引用 011-文档谬误修复工具链的现有命令（`doc_dependency_tracer.py` + `summary_validator.py`）
- 选项 B 与 AICC-20260425-017（doc_health_checker 缺失）联合处置：合并健康检查命令到统一工具入口

### 审查阶段

B3 R1 工作流端到端闭环（剧本 4）

---

## 问题 ID: AICC-20260425-021

- **类型**: 设计问题（默认配置路径假设需明示）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: B（完整性）+ C（dev 卫生）
- **关联任务/ADR**: 与 AICC-20260425-019 关联（同剧本 4）
- **状态**: 🔴 待修复

### 问题描述

`tools/py/complexity_scanner.py` L595 默认配置路径：

```python
parser.add_argument("--config", default="dev_docs/complexity/config.yaml", ...)
```

但 AICC 框架自身的复杂度配置位于 `dev/complexity/config.yaml`（dev/，非 dev_docs/）。

`dev_docs/` 是**用户项目运行时**的目录约定（参见 AI_ENTRY_POINT.md L154-L158）；用户复制 AICC 后会在自己项目下产生 `dev_docs/complexity/`。

未明示这一假设会导致：

- 在框架自身仓库直接运行 `python tools/py/complexity_scanner.py`（无 --config 参数）→ 找不到 `dev_docs/complexity/config.yaml` → fallback 行为不明确
- 如果 AI 在 dogfood（自审）时调用此工具，需手动指定 `--config dev/complexity/config.yaml`
- 文档未提及此差异

### 影响范围

- AICC 自身使用复杂度仪表盘（dogfood）时需额外参数
- 用户复制框架后能正常运行（dev_docs/ 由用户项目创建）
- 仅"框架开发者在 framework 仓库直接跑"场景下有困扰

### 主要文件路径

- `tools/py/complexity_scanner.py`
- `tools/js/complexity_scanner.js`（应同步检查）

### 相关文件路径

- `dev/complexity/config.yaml`（框架自身位置）
- `dev_docs/complexity/config.yaml`（用户项目运行时位置，由 default 指向）
- `tools/README.md`（应说明此差异）

### 具体位置

- `tools/py/complexity_scanner.py` L595：`default="dev_docs/complexity/config.yaml"`

### 复查方法（验证修复）

```bash
# 1. 在 framework 仓库根直接运行（无 --config）
python tools/py/complexity_scanner.py --since "1 day ago" 2>&1 | head -10
# 修复前：可能找不到 dev_docs/complexity/config.yaml
# 修复后：要么提供清晰错误提示，要么自动 fallback 到 dev/complexity/config.yaml

# 2. 工具的 --help 应明示用户项目 vs 框架自身的差异
python tools/py/complexity_scanner.py --help | grep -A 2 '\-\-config'
# 预期：明示路径假设和 fallback 策略

# 3. tools/README.md 应有"在框架自身上运行"说明
grep -nE 'dogfood|framework self|框架自身|自审' tools/README.md
```

### 建议修复方案

- **选项 A**：保留 default `dev_docs/complexity/config.yaml`，在 `--help` 与 `tools/README.md` 中明示"框架开发者自审时需指定 `--config dev/complexity/config.yaml`"
- **选项 B**：增加 fallback 逻辑：先找 `dev_docs/complexity/config.yaml`，找不到则尝试 `dev/complexity/config.yaml`，再找不到则使用工具内置默认
- 推荐 A（成本低，符合"用户项目优先"的框架定位）

### 审查阶段

B3 R1 工作流端到端闭环（剧本 4，附带观察）

---

## 问题 ID: AICC-20260425-022

- **类型**: 设计问题（目录命名规范不一致）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: B（完整性）+ C（dev 卫生）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/confirmed/` 下的优化点档案命名规范不统一：

- **目录名带 `.md` 后缀**（异常，3 个）：
  - `004-adr-system.md/`（目录）
  - `005-complexity-dashboard.md/`（目录）
  - `006-auto-review-report.md/`（目录）

- **目录名无后缀**（正常，10 个）：
  - `001-ai-agent-library/` / `003-design-thinking-guide/` / `010-cross-project-knowledge/` / `011-doc-error-fix-workflow/` / `012-mandatory-doc-summary/` / `013-ai-mutual-review/` / `014-doc-reading-habit-guide/` / `016-unified-config-system/` / `017-utility-script-library/` / `018-commit-guided-documentation/`

- **单文件 `.md`**（合理，1 个）：
  - `019-systematic-review-framework.md`

`Read` 工具直接打开 `004-adr-system.md`、`005-complexity-dashboard.md`、`006-auto-review-report.md` 会因 EISDIR 报错。视觉上无法区分文件 vs 目录。AI 写代码生成内部链接易错。

### 影响范围

- AI 工具读取 confirmed/ 档案易报错（EISDIR）
- ADR 链接、内部交叉引用易混淆
- B4 自指审查中实际遇到此问题（Read 工具直接报 EISDIR）
- 视角 C（dev/ 卫生）核心缺陷

### 主要文件路径

- `dev/V3.0/confirmed/004-adr-system.md/`
- `dev/V3.0/confirmed/005-complexity-dashboard.md/`
- `dev/V3.0/confirmed/006-auto-review-report.md/`

### 相关文件路径

- `dev/V3.0/PROGRESS.md`（如内含相对链接需同步更新）
- `dev/quality/README.md` L264（文档引用方式）

### 具体位置

```
dev/V3.0/confirmed/004-adr-system.md/         ← 应为 004-adr-system/
   ├── 004-adr-system.md
   ├── implementation_plan.md
   └── walkthrough.md

dev/V3.0/confirmed/005-complexity-dashboard.md/   ← 应为 005-complexity-dashboard/
   ├── 005-complexity-dashboard.md
   ├── implementation_plan.md
   └── walkthrough.md

dev/V3.0/confirmed/006-auto-review-report.md/    ← 应为 006-auto-review-report/
   ├── 006-auto-review-report.md
   ├── implementation_plan.md
   ├── walkthrough.md
   ├── 修复记录.md
   └── 资深用户审核报告.md
```

### 复查方法（验证修复）

```bash
# 1. confirmed/ 下应只有目录无 .md 后缀，或单文件 .md（如 019）
ls -d dev/V3.0/confirmed/*/ 2>/dev/null | grep '\.md/$'
# 修复后预期：返回空

# 2. 旧目录名引用方应同步更新
grep -rn '004-adr-system\.md/\|005-complexity-dashboard\.md/\|006-auto-review-report\.md/' \
  --include='*.md' dev/ | grep -v '/\.git'
# 修复后预期：返回空

# 3. Read 工具不再报 EISDIR
test -d dev/V3.0/confirmed/004-adr-system && echo OK
test -d dev/V3.0/confirmed/005-complexity-dashboard && echo OK
test -d dev/V3.0/confirmed/006-auto-review-report && echo OK
```

### 建议修复方案

```bash
git mv dev/V3.0/confirmed/004-adr-system.md dev/V3.0/confirmed/004-adr-system
git mv dev/V3.0/confirmed/005-complexity-dashboard.md dev/V3.0/confirmed/005-complexity-dashboard
git mv dev/V3.0/confirmed/006-auto-review-report.md dev/V3.0/confirmed/006-auto-review-report
# 然后 grep 全仓库更新引用
```

长期：在 `dev/V3.0/README.md` 中明确"优化点目录命名规范：单文件用 `NNN-name.md`，多文件用 `NNN-name/` 目录无后缀"。

### 审查阶段

B4 R5 自指审查（confirmed/ 命名审查）

---

## 问题 ID: AICC-20260425-023

- **类型**: 文档问题（README 索引覆盖率缺口）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: B+C
- **关联任务/ADR**: 与 AICC-20260425-006（README v2.0 重写）同源
- **状态**: 🔴 待修复

### 问题描述

`dev/quality/README.md` v2.0 在 agents/ 索引段（L153-L173）存在多处差异：

1. **遗漏 `agents/_templates/` 子目录**：实际含 `agent_template.md` 与 `quality_checklist.md`，但 README 完全未列
2. **examples 计数偏差**：README L171 写"21 个"，实际为 18 个（含 1 个 `design_thinking/` 子目录 + 1 个 `README.md` + 16 个 `*_examples.md`）
3. **language_specific 计数偏差**：README L163 写"7 个"，需复核（仓库实际 5 项 + base/ 子目录）

这些差距不会破坏使用，但作为"完整索引 200+ 公共文档"的 v2.0 定位，索引精度应保证。

### 影响范围

- 读 README 后建立的"agents 总览"心智模型存在偏差
- 索引覆盖率作为 v2.0 主要卖点，部分失真

### 主要文件路径

- `dev/quality/README.md`

### 相关文件路径

- `agents/_templates/`（实际存在但未索引）
- `agents/examples/`（实际数量与索引不符）
- `agents/language_specific/`（实际数量与索引不符）

### 具体位置

- `dev/quality/README.md` L153-L173 agents/ 索引段
- L169：`**custom/（1 个，⚪ 仅合规）**：\`_template.md\``（应增加 _templates/ 索引）
- L171：`**examples/（21 个，🟡 批审...）**`（应改为实际数量）

### 复查方法（验证修复）

```bash
# 1. README 应包含 _templates 索引
grep -nE '_templates' dev/quality/README.md

# 2. 数量复核
echo "examples actual:" && ls agents/examples/ | wc -l
echo "language_specific actual:" && ls agents/language_specific/ | wc -l
echo "personas actual:" && ls agents/personas/ | wc -l

# 3. 索引声明数 vs 实际数
grep -oE 'examples/（[0-9]+ ?个|language_specific/（[0-9]+ ?个|personas/（[0-9]+ ?个' \
  dev/quality/README.md
```

### 建议修复方案

- 在 L169 后增加：`**_templates/（2 个，⚪ 仅合规）**：\`agent_template.md\`、\`quality_checklist.md\``
- L171 改为：`**examples/（实际 18 个含 1 个子目录，🟡 批审...）**`
- 同步检查 language_specific 与 personas 数字

### 审查阶段

B4 R5 自指审查（README 索引覆盖率验证）

---

## 问题 ID: AICC-20260425-024

- **类型**: 设计问题（SOP 过度承诺）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: B（完整性）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`dev/quality/Framework_Review_Guidelines.md` v1.2 L443-L504 的"审查交付物清单模板"列出 10 项，但其中 2 项**从未在历史或本轮审查中实际产出**：

- 第 5 项 `Review_Data.zip`：声称"原始审查数据、测试日志、代码分析结果、性能测试报告"
- 第 6 项 `Assessment_Dashboard.html`：声称"HTML 交互式仪表板，可视化呈现框架各维度评估结果"

实际审查（含本轮）仅产出 5 件套（Review_Plan / Issue_Tracking / Progress_Tracking / Review_Log / Review_Checklist）+ 可选附加（Comprehensive_Review_Report / Improvement_Roadmap / Issue_Analysis）。

`Review_Data.zip` 与 `Assessment_Dashboard.html` 是 SOP 写得太大、实践无人执行的虚标项。AI 按 SOP 执行会浪费精力寻找如何产出，或在最终报告中遗憾解释"未产出"。

### 影响范围

- 视角 B：SOP 与实践不一致
- 后续审查者会困惑"为什么没人做这俩"
- 体系成熟度评估时会扣分

### 主要文件路径

- `dev/quality/Framework_Review_Guidelines.md`

### 相关文件路径

- `dev/quality/audits/README.md`（5 件套规范）
- `dev/quality/README.md` L62-L73（5 件套实际清单）

### 具体位置

- `dev/quality/Framework_Review_Guidelines.md` L471-L480：
  - L471-L474 第 5 项 `Review_Data.zip`
  - L476-L480 第 6 项 `Assessment_Dashboard.html`

### 复查方法（验证修复）

```bash
# 1. SOP 清单应与 audits/README.md 5 件套一致
grep -nE 'Review_Data\.zip|Assessment_Dashboard\.html' dev/quality/Framework_Review_Guidelines.md
# 修复后预期：要么删除（推荐），要么标注"可选附加，本框架尚未自动化产出"

# 2. 实际历史轮次产出应与 SOP 一致
ls dev/quality/audits/2026-04-25_V3.x_Comprehensive/
# 预期：5 件套 + 可选附加
```

### 建议修复方案

- **选项 A（推荐）**：从 SOP 删除第 5 项 `Review_Data.zip` 与第 6 项 `Assessment_Dashboard.html`，将 10 项交付物精简为 8 项
- 选项 B：保留两项，但明确标注"可选附加，仅当审查复杂度达 Critical 级别才需产出，且需先实施自动化生成工具"
- 推荐 A，与"务实而非膨胀"的 quality 体系定位一致

### 审查阶段

B4 R5 自指审查（Guidelines 内部一致性）

---

## 问题 ID: AICC-20260425-025

- **类型**: 文档问题（措辞与策略不一致）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: B
- **关联任务/ADR**: 与 AICC-20260425-006（contexts/ 改按需生成）同源
- **状态**: 🔴 待修复

### 问题描述

`dev/quality/README.md` v2.0 L44-L58 contexts/ 章节措辞与"按需生成"新策略有张力：

- L46：`每个 🔴 优先级文档对应一份 context`（旧表述：每个文档→一份 context）
- L48-56：使用方式仍引导读者"发送 contexts/[文档名].md"
- L58：`contexts/_template.md 是模板。具体清单见下方"📊 完整文档索引"`

但实际 contexts/ 目录仅含 `_template.md`，**所有 🔴 优先级文档对应的 context 均未生成**。

L46 与 L48-56 措辞会让新读者期待 contexts/ 下有完整文件集，开箱却为空，导致困惑。

虽然 AICC-20260425-006 已"修复"（标记为按需生成），但 README 表述未同步调整。

### 影响范围

- README v2.0 的"完整索引"承诺与 contexts/ 的"几乎为空"现状产生张力
- 新读者首次按 README 操作会失败

### 主要文件路径

- `dev/quality/README.md`

### 相关文件路径

- `dev/quality/contexts/`（仅 _template.md）
- `dev/quality/HOW_TO_GENERATE_CONTEXTS.md`（context 生成 SOP）

### 具体位置

- `dev/quality/README.md` L44-L58

### 复查方法（验证修复）

```bash
# 1. 实际 contexts/ 内容
ls dev/quality/contexts/

# 2. README 措辞应与现状一致
grep -nE '每个.*context|contexts/\[' dev/quality/README.md
# 修复后预期：明示"按需生成"，不再承诺每文档一份

# 3. 新读者按 README 操作能否成功
# 模拟操作：尝试 cat dev/quality/contexts/AI_ENTRY_POINT.md
test -f dev/quality/contexts/AI_ENTRY_POINT.md && echo "已生成" || echo "需现场生成（按 HOW_TO_GENERATE_CONTEXTS.md）"
```

### 建议修复方案

- 改写 L44-L58，明确：
  - "contexts/ 采用按需生成策略，仅在审查 🔴 优先级文档时现场生成对应 context"
  - "目录通常仅含 `_template.md`；具体 context 在审查时按 HOW_TO_GENERATE_CONTEXTS.md 现场生成"
- 删除"具体清单见下方"措辞，改为"具体生成 SOP 见 HOW_TO_GENERATE_CONTEXTS.md"
- 与 v2.0 三级优先级（🔴/🟡/⚪）的"按需"原则保持一致

### 审查阶段

B4 R5 自指审查（README 与 contexts 现状对齐）

---

## 问题 ID: AICC-20260425-026

- **类型**: 集成问题（声明工具不存在）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: B（完整性）+ C（dev 卫生）
- **关联任务/ADR**: 005-复杂度仪表盘
- **状态**: 🔴 待修复

### 问题描述

`dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` 的"实施产出摘要"段（L13-L17）声明 005 的工具链包含：

- `complexity_scanner.py` ✅ 存在
- `complexity_scanner.js` ✅ 存在
- `report_generator.py` ✅ 存在
- `notifier.py` ✅ 存在
- **`architecture_analyzer.py`** ❌ 不存在

`tools/py/` 与 `tools/js/` 中均无 `architecture_analyzer.py`/`.js`。

005 walkthrough.md 提供的"工具链 dual-engine"图景含 5 项，实际仅 4 项落地，**1 项虚标**。

### 影响范围

- 005-复杂度仪表盘的"高级架构分析"能力实际缺失
- B2 的"12 项实体核查全部 ✅"结论需打补丁：实体存在，但子工具集不完整
- 视角 B 完整性受损

### 主要文件路径

- `tools/py/architecture_analyzer.py`（应存在但不存在）
- `tools/js/architecture_analyzer.js`（应存在但不存在）

### 相关文件路径

- `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` L17
- `dev/V3.0/confirmed/005-complexity-dashboard.md/implementation_plan.md`（应说明此工具的角色）
- `tools/README.md`（应索引该工具或说明缺失）

### 具体位置

- `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` L17：`**架构分析**: \`architecture_analyzer.py\` - 高级架构分析`

### 复查方法（验证修复）

```bash
# 1. 工具应存在（双脚本对称）
ls tools/py/architecture_analyzer.py tools/js/architecture_analyzer.js

# 2. 文档与实体一致性
grep -rn 'architecture_analyzer' dev/V3.0/confirmed/005-complexity-dashboard.md/ tools/

# 3. 与 complexity_scanner 协同
python tools/py/architecture_analyzer.py --help 2>&1 | head -5
```

### 建议修复方案

- **选项 A（推荐）**：补全 `architecture_analyzer.py/.js` 双脚本（005 P1 完结的最后一里）
- 选项 B：从 walkthrough.md 删除该工具的引用，承认它未实施
- 推荐 A，因 walkthrough.md 已含完整设计意图（高级架构分析），补全成本低于重写文档
- 同步更新 `tools/README.md` 与 005 implementation_plan

### 审查阶段

B4 R5 自指审查（005 实体一致性复审）

---

## 问题 ID: AICC-20260425-027

- **类型**: 设计问题（设计已完成但未提升至 Public）
- **严重级别**: 建议
- **优先级**: 中
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 与 AICC-20260425-019 关联（剧本 4 端到端工作流缺失）的根因诊断
- **状态**: 🔴 待修复

### 问题描述

B3 阶段记录 AICC-20260425-019："剧本 4 复杂度告警端到端工作流文档缺失"。B4 阶段进一步诊断：

- `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` 已含完整端到端流程：
  - 实施产出摘要（目录结构 + 工具链 + Git Hooks）
  - 验证场景 A: 基础数据采集
  - 验证场景 B/C/...（推断含报告生成、阈值告警、决策建议）

- 但该 walkthrough.md 位于 `dev/V3.0/confirmed/`（开发档案区），**未提升到 Public `workflows/` 目录**：
  - `workflows/complexity_alert_workflow.md` 不存在
  - `workflows/path_d_specific_tasks.md` 无 @complexity 路由
  - `AI_ENTRY_POINT.md` 无 complexity_scanner 索引

设计意图已完整规划，仅缺"提升至 Public 工作流"这最后一步。这与 AICC-20260425-019 互为因果：019 是症状，027 是根因。

### 影响范围

- 与 019 联动评估：剧本 4 缺失工作流的根本原因是"设计完整但未发布"
- 005 的"已完成"标识需配 walkthrough → workflows/ 转换才算完整闭环
- 修复 027 即修复 019

### 主要文件路径

- `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md`（设计文档源）
- `workflows/complexity_alert_workflow.md`（应新建的 Public 流程）
- `AI_ENTRY_POINT.md`（应新增索引）
- `workflows/path_d_specific_tasks.md`（应新增 @complexity 路由）

### 相关文件路径

- `dev/V3.0/confirmed/005-complexity-dashboard.md/implementation_plan.md`
- `tools/py/complexity_scanner.py`、`tools/py/report_generator.py`
- `dev/complexity/config.yaml`

### 具体位置

- `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md`（提取源）
- `workflows/`（增补目标）

### 复查方法（验证修复）

```bash
# 1. Public workflows 应有复杂度告警工作流
ls workflows/complexity_alert_workflow.md

# 2. AI_ENTRY_POINT 应有索引
grep -nE 'complexity|complexity_scanner' AI_ENTRY_POINT.md

# 3. path_d 应有 @complexity 路由
grep -nE '@complex' workflows/path_d_specific_tasks.md

# 4. 端到端剧本可演练
python tools/py/complexity_scanner.py --since "1 day ago" --output /tmp/c.json && \
python tools/py/report_generator.py --data /tmp/c.json --output /tmp/c.md && \
test -s /tmp/c.md && echo "剧本 4 可跑通"
```

### 建议修复方案

- 将 `dev/V3.0/confirmed/005-complexity-dashboard.md/walkthrough.md` 中的"实施产出 + 验证场景"段落提取为 `workflows/complexity_alert_workflow.md`（面向 AI 的 SOP，非"开发完成验证"）
- 在 `AI_ENTRY_POINT.md` "实用工具库 (tools/)" 段补充 `tools/py/complexity_scanner.py` 索引
- 在 `workflows/path_d_specific_tasks.md` 新增 `@complexity` 指令章节
- 联动修复 AICC-20260425-019 / 020 / 026

### 审查阶段

B4 R5 自指审查（005 设计-发布 gap 诊断）

---

## 问题 ID: AICC-20260425-028

- **类型**: 文档问题（结构错乱 + 步骤跳号）
- **严重级别**: 严重
- **优先级**: 高
- **归属视角**: A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`guides/quick_start.md` 是新用户旅程的核心入口，但当前结构严重损坏：

1. **步骤编号跳号**：明确列出"步骤 0 / 步骤 1 / 步骤 4 / 步骤 5 / 步骤 6"，**完全缺失步骤 2 和步骤 3**
2. **代码块未闭合**：L54 处 ` ```bash ` 开启代码块后，紧接着 L57 出现 `#### 审核清单` 二级标题，破坏 markdown 结构
3. **末尾自相矛盾**：L235 写 "选择场景 1，严格按照 6 个步骤执行"，但实际只能数到 5 个步骤（0/1/4/5/6）
4. **审核清单段落定位错位**：L57-L109 的"审核清单"内容应在步骤 3 内，但实际嵌入步骤 1 的代码块中

新用户按此文档操作会在步骤 1 后完全迷失：找不到步骤 2、3 在哪，跳到步骤 4 又写"审核通过后..."但前面没"步骤 3：审核"。

### 影响范围

- **R4（新用户旅程）核心断点**：30 分钟时间预算无法兑现
- **视角 A 致命缺陷**：用户旅程在第二个文档就崩溃
- 用户可能直接放弃使用框架

### 主要文件路径

- `guides/quick_start.md`

### 相关文件路径

- `README.md`（首先引导用户来此文档）
- `workflows/path_a_first_generation.md`（与 quick_start 应一致）
- `templates/GENERATION_PLAN_TEMPLATE.md`（应在缺失的步骤 2/3 中提及）

### 具体位置

- L52-L54：步骤 1 起始
- L54：未闭合 ` ```bash ` 代码块
- L57-L109：审核清单（位置错误）
- L113：直接跳到"步骤 4: 执行文档生成"（应有步骤 2、3）
- L235：`严格按照 6 个步骤执行`（计数错误）

### 复查方法（验证修复）

```bash
# 1. 步骤编号应连续完整
grep -nE '^### 步骤 [0-9]' guides/quick_start.md
# 修复后预期：返回连续编号 0/1/2/3/4/5/6 或 1/2/3/4/5/6

# 2. 代码块成对闭合（开闭数应为偶数）
grep -c '^```' guides/quick_start.md
# 修复后预期：偶数

# 3. 末尾计数与实际步骤数一致
grep -nE '步骤数|个步骤|步骤执行' guides/quick_start.md
# 修复后预期：声明的数字 = 实际 ### 步骤 段落数

# 4. 模拟 markdown 渲染（粗略）
python -c "
import re
with open('guides/quick_start.md') as f: c = f.read()
steps = re.findall(r'^### 步骤 (\d+)', c, re.M)
print('步骤序列:', steps)
print('是否连续:', steps == [str(i) for i in range(int(steps[0]), int(steps[-1])+1)])
"
```

### 建议修复方案

- 重写 quick_start.md，确保：
  - 步骤连续：0 → 1 → 2 → 3 → 4 → 5 → 6（或 1-6）
  - 步骤 2：生成分析方案（引用 GENERATION_PLAN_TEMPLATE.md）
  - 步骤 3：审核方案（"审核清单"段落应在此）
  - 所有代码块成对闭合
  - L235 的步骤计数与实际一致
- 与 `workflows/path_a_first_generation.md` 9 步流程对齐（path_a 有完整 8 步：S0-S8）
- 长期：在 CI/pre-commit 中加入 markdown 结构校验

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-029

- **类型**: 文档问题（路径承诺多版本不一致）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 与 AICC-20260425-016（AI_RULES.md 大小写）联动加重
- **状态**: 🔴 待修复

### 问题描述

`AI_RULES.md` 文件最终生成路径在不同文档中有 **4 处不同表述**：

1. `README.md` L168：`📐 Rule文件已生成: dev_docs/rules/combined/AI_RULES.md`（深嵌套路径，大写）
2. `README.md` L173：`打开dev_docs/rules/combined/AI_RULES.md`（同上）
3. `templates/AI_RULES_TEMPLATE.md` L541：`AI 生成更新后的 rule 到\`dev_docs/AI_RULES.md\``（dev_docs/ 直下，大写）
4. `workflows/path_a_first_generation.md` L752/L756：`项目根目录 \`ai_rules.md\``（项目根，**小写**）
5. `AI_ENTRY_POINT.md` L157：`- AI_RULES.md`（仅文件名，未指定位置）

这导致：

- 用户读 README 期待 `dev_docs/rules/combined/AI_RULES.md`
- 但 path_a 让 AI 生成 `项目根/ai_rules.md`（小写）
- 模板说应该到 `dev_docs/AI_RULES.md`
- IDE 集成（Cursor `.cursorrules`）会因位置错位失效

### 影响范围

- **R4 新用户旅程致命断点**：用户找不到生成的 AI_RULES.md
- **R1 工作流闭环致命断点**：剧本 1 path_a 最后一步产物去向不明
- 与 AICC-20260425-016（大小写不一致）耦合放大问题
- IDE 集成失败

### 主要文件路径

- `README.md`
- `templates/AI_RULES_TEMPLATE.md`
- `workflows/path_a_first_generation.md`
- `AI_ENTRY_POINT.md`

### 相关文件路径

- `guides/ai_rules_maintenance.md`（应明示权威路径）
- `core/framework_spec.md`（应权威约定文件位置）

### 具体位置

- `README.md` L168、L173
- `templates/AI_RULES_TEMPLATE.md` L541
- `workflows/path_a_first_generation.md` L752、L756
- `AI_ENTRY_POINT.md` L157、术语表 L306-L307

### 复查方法（验证修复）

```bash
# 1. 全仓库 AI_RULES 路径所有出现处统一
grep -rnE 'AI_RULES\.md|ai_rules\.md' --include='*.md' \
  AI_ENTRY_POINT.md README.md templates/ workflows/ guides/ core/ \
  | grep -oE '[a-zA-Z_/]+(AI_RULES\.md|ai_rules\.md)' | sort -u
# 修复后预期：所有路径前缀完全一致（推荐统一为 `dev_docs/AI_RULES.md`）

# 2. Linux 大小写敏感测试
grep -nE '\bai_rules\.md\b' --include='*.md' .
# 修复后预期：返回空（统一大写）

# 3. AI_ENTRY_POINT 术语表是权威源
grep -nE 'AI_RULES\.md' AI_ENTRY_POINT.md
```

### 建议修复方案

- 以 `AI_ENTRY_POINT.md` 术语表为权威源，统一为 `dev_docs/AI_RULES.md`（大写、dev_docs/ 直下）
- 修订四处：
  - `README.md` L168/L173：路径改为 `dev_docs/AI_RULES.md`
  - `templates/AI_RULES_TEMPLATE.md` L541：保持 `dev_docs/AI_RULES.md`（已正确）
  - `workflows/path_a_first_generation.md` L752/L756：改为 `dev_docs/AI_RULES.md`
- 与 016（大小写）一并修复
- 长期：在 `core/framework_spec.md` 增加"标准产物路径"章节作为单一真相源

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-030

- **类型**: 文档问题（过时框架名残留）
- **严重级别**: 主要
- **优先级**: 高
- **归属视角**: A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`guides/quick_start.md` 多处引用过时框架名 **`ai_documentation_framework`**（应为当前框架名 `ai_coding_context`）：

- L55：`# 克隆或复制 ai_documentation_framework 目录到新项目根目录`
- L146：`rm -rf ai_documentation_framework/`
- L158：`cp -r ai_documentation_framework /path/to/existing_project/`
- L228：`把 \`ai_documentation_framework/\` 维护为独立仓库`

新用户按 README L131 用 `cp -r ai_coding_context your-project/` 复制后，再读 quick_start 看到要操作 `ai_documentation_framework` 会困惑：

- 是否还需要再 cp 一份？
- 框架的真实名字是什么？
- 之前复制的 `ai_coding_context` 用错了吗？

### 影响范围

- **R4 新用户旅程严重断点**：用户对框架身份产生混淆
- 视角 A 用户可信度受损
- 文档一致性维护机制失灵的指示器（README 已升级，guides 未同步）

### 主要文件路径

- `guides/quick_start.md`

### 相关文件路径

- `README.md`（已使用 `ai_coding_context` 正确名称）

### 具体位置

- L55、L146、L158、L228（共 4 处）

### 复查方法（验证修复）

```bash
# 1. 全仓库不应再有 ai_documentation_framework 残留
grep -rn 'ai_documentation_framework' --include='*.md' .
# 修复后预期：返回空（或仅在 dev/V2.x 历史档案中，可豁免）

# 2. 当前框架名应为 ai_coding_context
grep -rn 'ai_coding_context' --include='*.md' \
  README.md AI_ENTRY_POINT.md guides/ workflows/ \
  | head -10

# 3. 历史归档区可保留旧名作为版本演进证据
grep -rn 'ai_documentation_framework' --include='*.md' dev/V2.3/ dev/V2.2/ 2>&1
# 此处出现可接受
```

### 建议修复方案

- 全文替换 `guides/quick_start.md` 中的 `ai_documentation_framework` → `ai_coding_context`
- 同步检查其他 guides/ 文档是否有类似过时名残留
- 长期：在框架更名时加入 grep 检查项到 release checklist

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-031

- **类型**: 文档问题（首页计数错误）
- **严重级别**: 主要
- **优先级**: 中
- **归属视角**: A（用户）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`README.md` L120 标题写 `## 🚀 快速开始（3 步）`，但紧接着 L122-L125 实际列出 **4 步**：

```
1. 完整阅读 README.md（即本文档）了解框架
2. 复制框架到你的项目
3. 让 AI 读取 AI_ENTRY_POINT.md
4. AI 自动生成文档体系
```

后续详细说明又有：
- 步骤 1: 复制框架（L127）
- 步骤 2: 让 AI 自主执行（L134）
- 步骤 3: 审核确认（L152）
- 步骤 4: 配置 AI Rules（L163）

总共 4 个详细步骤，与"3 步"标题不符。L122 第一项"完整阅读 README"也未在详细说明中作为独立步骤展开。

新用户从首页的"3 步"承诺起步，看到 4 步详细说明，会怀疑文档准确性。

### 影响范围

- README 是新用户首次接触的入口，首页计数错误会立即破坏信任
- R4 新用户旅程的"第一印象"断点

### 主要文件路径

- `README.md`

### 相关文件路径

- `guides/quick_start.md`（应与 README 步骤数对齐）
- `AI_ENTRY_POINT.md`（与 README 一致的快速指引）

### 具体位置

- L120：`## 🚀 快速开始（3 步）` 标题
- L122-L125：4 项编号列表（"完整阅读" + 3 个执行步骤）
- L127、L134、L152、L163：详细说明的 4 个步骤

### 复查方法（验证修复）

```bash
# 1. 标题数字与实际步骤数一致
TITLE=$(grep -oE '快速开始（[0-9]+ ?步）' README.md | grep -oE '[0-9]+')
DETAIL=$(grep -cE '^### 步骤 [0-9]+:' README.md)
echo "标题: $TITLE 步; 详细步骤数: $DETAIL"
# 修复后预期：两者相等

# 2. 顶部编号列表项数与详细说明数一致
sed -n '/快速开始/,/### 步骤 1/p' README.md | grep -cE '^[0-9]+\.'
```

### 建议修复方案

- **选项 A**：标题改为 `## 🚀 快速开始（4 步）`，与详细说明匹配
- **选项 B**：将 L122-L125 的"完整阅读 README"合并到正文导言（不作为独立步骤），保持 3 步详细说明
- 推荐 A：保留"完整阅读 README"作为隐含前提，详细说明 4 步保持一致

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-032

- **类型**: 文档问题（主文档名大小写不一致）
- **严重级别**: 次要
- **优先级**: 中
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 与 AICC-20260425-016（AI_RULES 大小写）同性质
- **状态**: 🔴 待修复

### 问题描述

主文档（用户项目根）名称在不同文档存在大小写不一致：

- `AI_ENTRY_POINT.md` 术语表 L307：`dev_docs/AI_Coding_Context.md`（驼峰）
- `guides/quick_start.md` L120：`生成主文档 ai_coding_context.md`（小写）
- `templates/AI_Coding_Context_TEMPLATE.md`（驼峰）

Linux 文件系统区分大小写：

- 若 AI 按 quick_start 生成 `ai_coding_context.md`，与 AI_ENTRY_POINT 术语表的 `AI_Coding_Context.md` 不一致
- 后续 AI 会话查找 `dev_docs/AI_Coding_Context.md` 会失败
- 与项目目录 `ai_coding_context/`（框架本身的目录名）混淆

### 影响范围

- 视角 A：用户在 Linux/macOS 下生成的产物可能与文档预期不一致
- 与 016（AI_RULES.md）+ 029（AI_RULES 路径）形成"V3.0 命名一致性系统问题"集群
- 长期看是框架自动化能力受损

### 主要文件路径

- `AI_ENTRY_POINT.md`
- `guides/quick_start.md`

### 相关文件路径

- `templates/AI_Coding_Context_TEMPLATE.md`
- `core/framework_spec.md`

### 具体位置

- `guides/quick_start.md` L120：`生成主文档 ai_coding_context.md`
- `AI_ENTRY_POINT.md` L307：`dev_docs/AI_Coding_Context.md`

### 复查方法（验证修复）

```bash
# 1. 不应再有小写形式的主文档名
grep -rn '\bai_coding_context\.md\b' --include='*.md' .
# 修复后预期：返回空

# 2. 大写形式应统一
grep -rn 'AI_Coding_Context\.md' --include='*.md' \
  AI_ENTRY_POINT.md guides/ workflows/ templates/ core/ \
  | head -10

# 3. 模板文件名作为权威源
ls templates/AI_Coding_Context_TEMPLATE.md
```

### 建议修复方案

- 以 `AI_ENTRY_POINT.md` 术语表 L307 为权威源（`dev_docs/AI_Coding_Context.md`）
- 修订 `guides/quick_start.md` L120：`生成主文档 ai_coding_context.md` → `生成主文档 dev_docs/AI_Coding_Context.md`
- 与 016 / 029 一并修复，作为"V3.0 命名规范统一"的批次修复

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-033

- **类型**: 设计问题（推荐工具与 V3.0 标准化脱节）
- **严重级别**: 次要
- **优先级**: 低
- **归属视角**: A（用户）
- **关联任务/ADR**: 与 017-实用脚本工具库（已完成）的"消除命令行不确定性"原则相关
- **状态**: 🔴 待修复

### 问题描述

`guides/quick_start.md` 步骤 0（项目规模评估）推荐用户使用：

```bash
# L33-L34
find . -name "*.ts" -o -name "*.js" -o -name "*.vue" | wc -l
cloc . --exclude-dir=node_modules,dist
```

这与 V3.0 强调的"消除 AI 命令行操作不确定性"原则脱节：

- AICC 已有 `tools/py/project_scanner.py`（Python，跨平台）和 `tools/js/project_scanner.js`（双脚本对称）
- AI_ENTRY_POINT.md 工具索引 L320 明确推荐使用 project_scanner
- 但 quick_start 推荐用户用 `find` + `cloc`：
  - `find` 命令在 Windows PowerShell 下行为不同
  - `cloc` 是第三方工具，违反"零依赖"红线
  - 没引导用户走 V3.0 工具链

### 影响范围

- 用户养成"用 shell 命令而非 AICC 工具"的习惯，绕过 V3.0 标准化
- 跨平台一致性受损（Windows 用户运行 find 会失败）
- 017-实用脚本工具库的价值未被引导发掘

### 主要文件路径

- `guides/quick_start.md`

### 相关文件路径

- `tools/py/project_scanner.py`
- `tools/js/project_scanner.js`
- `AI_ENTRY_POINT.md` L320 工具索引

### 具体位置

- `guides/quick_start.md` L31-L36 步骤 0 命令示例

### 复查方法（验证修复）

```bash
# 1. quick_start 应优先推荐 V3.0 工具
grep -nE 'project_scanner|tools/py|tools/js' guides/quick_start.md
# 修复后预期：≥ 1 处明确引导

# 2. find/cloc 等 shell 命令应作为降级方案而非主推
grep -nE 'find \. -name|cloc \.' guides/quick_start.md
# 修复后：要么删除，要么明示"作为 fallback 方案"

# 3. 与 AI_ENTRY_POINT 工具索引一致
grep -nE 'project_scanner' AI_ENTRY_POINT.md guides/quick_start.md
```

### 建议修复方案

- 将 L31-L36 改为：

```bash
# 推荐：使用 AICC 工具（跨平台 + 零依赖）
python tools/py/project_scanner.py . --exclude-standard
# 或 Node.js 版本：
node tools/js/project_scanner.js . --exclude-standard

# 降级（无 Python/Node.js 时）：
find . -name "*.ts" -o -name "*.js" -o -name "*.vue" | wc -l
```

- 引用 `AI_ENTRY_POINT.md` 工具索引段
- 与 V3.0 双脚本对称模式保持一致

### 审查阶段

B5 R4 新用户旅程

---

## 问题 ID: AICC-20260425-034

- **类型**: 设计问题（V3.0 强制规则未自指落地）
- **严重级别**: 严重
- **优先级**: 高
- **归属视角**: A（用户）+ B（完整性）
- **关联任务/ADR**: 012-强制文档摘要机制（V3.0 P0 已完成）
- **状态**: 🔴 待修复

### 问题描述

V3.0-012-强制文档摘要机制声称"已完成"（PROGRESS.md L88 ✅），核心承诺是"所有生成的文档（Artifacts），**必须**在开头包含标准的 YAML Frontmatter 摘要"（path_a L337-L338）。但 B6 批量扫描显示，AICC 框架自身**未自指落地**该规则：

**Public 层 frontmatter 合规率**（138 个 .md 中仅 20 个有 frontmatter）：

| 目录 | 含 frontmatter | 总数 | 合规率 |
|---|:-:|:-:|:-:|
| 顶层入口 | 0 | 3 | **0%** ❌ |
| `core/` | 14 | 21 | 66% |
| `workflows/` | 1 | 26 | **3%** ❌ |
| `guides/` | 0 | 15 | **0%** ❌ |
| `agents/` | 0 | 59 | **0%** ❌ |
| `config/` | 0 | 3 | **0%** ❌ |
| `templates/` | 5 | 29 | 17% |
| **总计** | **20** | **138** | **14%** |

**dev/ 层对照**：

- `dev/V3.0/`: 0 / 60 (**0%**)
- `dev/quality/`: 5 / 17 (29%)

**最关键的失败点**：

- `AI_ENTRY_POINT.md` ❌（AI 唯一入口，应作为 frontmatter 首例）
- `README.md` ❌（人类入口）
- `CONTRIBUTING.md` ❌
- `core/SUMMARY_FORMAT_SPEC.md` —— **规范本身未自带 frontmatter**

这是 R5（自指一致性）的核心崩塌：**框架强制其他人遵守的规则，自己未遵守**。dogfood 缺失。

### 影响范围

- 012-强制文档摘要的"已完成"声明实际为虚标（实体存在但效果为零）
- 用户复制框架后，看到框架自身大量文档无 frontmatter，会困惑"这是真的强制吗"
- 智能文档推荐（014）、自动关联检测（018 commit-guided）依赖 frontmatter，框架自身不可被这些机制使用
- AI 检索框架文档时无法利用 summary 节省 token —— 与 V3.0 "节省 Token 30-50%"承诺直接冲突
- 与 AICC-20260425-028 / 029 / 031 等用户旅程问题叠加，构成"框架对自己不严格"的整体印象

### 主要文件路径

- 全部缺 frontmatter 的 138 - 20 = 118 个 .md 文件
- 关键优先级：
  - `AI_ENTRY_POINT.md`、`README.md`、`CONTRIBUTING.md`
  - `core/SUMMARY_FORMAT_SPEC.md`、`core/framework_spec.md` 等 7 个 core/ 缺失
  - `workflows/path_a-d / commit_guided / git_safety / doc_error_fix` 等 25 个 workflows
  - `agents/runtime/*.md`、`agents/workflows/*.md` 等 59 个 agents
  - `guides/*.md` 全部 15 个

### 相关文件路径

- `core/SUMMARY_FORMAT_SPEC.md`（规范源，应以身作则）
- `tools/py/summary_validator.py`（合规检查工具）
- `tools/py/summary_extractor.py`（自动提取，可用于批量补全）
- `dev/V3.0/confirmed/012-mandatory-doc-summary/`（设计文档）

### 具体位置

- 全仓库 .md 文件，按上表分目录分布

### 复查方法（验证修复）

```bash
# 1. Public 层合规率应 ≥ 95%
total=0; with_fm=0
for f in $(find AI_ENTRY_POINT.md README.md CONTRIBUTING.md core/ workflows/ guides/ templates/ agents/ config/ -name '*.md'); do
  [[ "$f" == *_TEMPLATE* ]] && continue
  total=$((total+1))
  head -1 "$f" 2>/dev/null | grep -q '^---$' && with_fm=$((with_fm+1))
done
echo "Public 合规率: $(( with_fm * 100 / total ))%"
# 修复后预期：≥ 95%

# 2. 顶层入口必须 100% 合规
for f in AI_ENTRY_POINT.md README.md CONTRIBUTING.md core/SUMMARY_FORMAT_SPEC.md; do
  head -1 "$f" 2>/dev/null | grep -q '^---$' && echo "✅ $f" || echo "❌ $f"
done

# 3. summary_validator 批量验证
python tools/py/summary_validator.py --path . --recursive 2>&1 | tail -10

# 4. 各目录合规率
for dir in core workflows guides templates agents config; do
  total=$(find $dir -name '*.md' ! -name '*_TEMPLATE*' | wc -l)
  with_fm=$(for f in $(find $dir -name '*.md' ! -name '*_TEMPLATE*'); do head -1 "$f" 2>/dev/null | grep -q '^---$' && echo 1; done | wc -l)
  printf "%-15s %3d / %3d (%d%%)\n" "$dir" "$with_fm" "$total" "$(( with_fm * 100 / total ))"
done
```

### 建议修复方案

**分阶段批量补全**：

- **P0（紧急，1 周内）**：补全顶层 3 个入口 + core/ 7 个核心规范 + SUMMARY_FORMAT_SPEC（自带示例）= 10 个
- **P1（短期，2 周内）**：补全 workflows/ 25 个 + guides/ 15 个 = 40 个
- **P2（中期，1 月内）**：补全 agents/ 59 个 + templates/ 24 个 + config/ 3 个 = 86 个

**自动化方案**：

- 用 `tools/py/summary_extractor.py` 从已有内容提取草稿摘要
- 人工审校后批量写入
- 加入 pre-commit hook 阻止无 frontmatter 的新 .md 提交

**长期防御**：

- 在 CI 中加入 `summary_validator` 必须通过的 gate
- `core/SUMMARY_FORMAT_SPEC.md` 自身必须含示范级 frontmatter

### 审查阶段

B6 批量合规扫描

---

## 问题 ID: AICC-20260425-035

- **类型**: 文档问题（工具头部 docstring 不规范）
- **严重级别**: 建议
- **优先级**: 低
- **归属视角**: C（dev 卫生）
- **关联任务/ADR**: 无
- **状态**: 🔴 待修复

### 问题描述

`tools/js/aac_validator.js` 头部缺规范的 docstring 注释。前 10 行结构：

```js
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
// Note: Normally we would use a real yaml parser 'js-yaml' through require,
// but for zero-dependency standard, we'll do a simple naive text regex parser
// specifically tuned for the constraints format in ADRs.

function parseArgs() {
    ...
```

虽 L4-L6 有内联注释说明"为零依赖红线自实现 yaml parser"（这是 V3.0 设计决策的良好证据），但缺少标准 docstring 块（用法、参数、输出示例等）。

对照：

- `tools/py/*.py` 全部 33 个文件均有完整 docstring（已验证 ✅）
- `tools/js/*.js` 主脚本 33 个中仅此 1 个缺规范 docstring（合规率 32/33 = 97%）

### 影响范围

- 双脚本对称的"形式对称"满足，但"质量对称"略有偏差
- aac_validator.js 用户读不到标准化用法说明
- V3.0 工具规范（"工具脚本头部需有 docstring + 用法说明"，见 quality/README.md tools/ 扫描项 L252）违反 1 处

### 主要文件路径

- `tools/js/aac_validator.js`

### 相关文件路径

- `tools/py/aac_validator.py`（可作为 docstring 模板）
- `dev/quality/README.md` L246-L253（工具合规扫描项定义）

### 具体位置

- `tools/js/aac_validator.js` L1-L10

### 复查方法（验证修复）

```bash
# 1. JS 主脚本头部 docstring 100% 合规
total=0; missing=0
for f in tools/js/*.js; do
  [[ "$f" == *.test.js ]] && continue
  total=$((total+1))
  if ! head -3 "$f" | grep -qE '^/\*|^//|^/\*\*'; then
    echo "MISSING: $f"
    missing=$((missing+1))
  fi
done
echo "JS 主脚本头部 docstring: $(( (total-missing) * 100 / total ))%"
# 修复后预期：100%

# 2. aac_validator.js 应有完整 JSDoc 头部
head -20 tools/js/aac_validator.js | grep -cE '^/\*\*|^ \*'
# 修复后预期：≥ 5（一个完整 JSDoc 块）
```

### 建议修复方案

- 参考 `tools/py/aac_validator.py` 头部 docstring 内容
- 在 `tools/js/aac_validator.js` L1（shebang 之后）添加 JSDoc 块：

```js
#!/usr/bin/env node
/**
 * aac_validator.js - 架构断言验证工具（004-ADR 系统）
 *
 * 用途：验证代码是否违背 ADR 中声明的架构约束
 *
 * 使用：
 *   node tools/js/aac_validator.js [--path PATH] [--adr ADR_DIR]
 *
 * 参数：
 *   --path PATH   待验证的代码路径
 *   --adr DIR     ADR 目录（默认 dev/architecture/decisions/）
 *
 * 输出：JSON 格式的违规清单
 *
 * 零依赖：自实现 YAML 解析（不引入 js-yaml）
 */
const fs = require('fs');
const path = require('path');
...
```

### 审查阶段

B6 批量合规扫描

---

## 📈 后续批次将追加的问题段落

B7 执行后将在此追加（如有），编号继续：AICC-20260425-036 起。

---

**版本**：v1.6
**创建日期**：2026-04-25
**最后更新**：2026-04-25（B6 完成；新增 034 严重 + 035 建议；累计 35 项 Issue）
