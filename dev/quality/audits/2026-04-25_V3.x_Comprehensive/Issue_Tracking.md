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
| 严重 | 0 |
| 主要 | 7 |
| 次要 | 9 |
| 建议 | 5 |
| **合计** | **21**（B0 基线 8 + B1 新增 2 + B2 新增 5 + B3 新增 6；后续批次将追加） |

| 视角分布 | 数量 |
|---|---|
| 视角 A（用户） | 5 |
| 视角 B（完整性） | 12 |
| 视角 C（dev 卫生） | 4 |

| 修复状态 | 数量 |
|---|---|
| 🟢 已修复（Phase 0 顺手处理） | 4 |
| 🔴 待修复 | 17 |

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

## 📈 后续批次将追加的问题段落

每个批次（B4-B7）执行后将在此追加问题，编号继续：AICC-20260425-022 起。

---

**版本**：v1.3
**创建日期**：2026-04-25
**最后更新**：2026-04-25（B3 完成；新增 016-021，全部含完整六大要素）
