# 018 - Commit-Guided Documentation (基于 Commit 的文档更新)

**优先级**: P0 ⭐ (已升级,整合 Git 安全规范)  
**状态**: � 已确认  
**确认日期**: 2025-12-11  
**预估工作量**: 8-12 天 (含新增内容)  
**来源**: 用户提议 + `dev/reference/高效提交git.md` + Git 安全需求  
**依赖**: 001 (AI 角色库) - 需要 `commit_analyst` 角色

---

## 📋 问题描述

### 核心痛点

**当前框架的变更检测机制**:

1. ✅ 已依赖 Git 历史检测代码变更 (`core/update_triggers.md`)
2. ✅ 已定义 P0/P1/P2 更新触发条件
3. ❌ **但**: 未充分利用 commit message 中的意图信息
4. ❌ **导致**: 用户需要手动向 AI 解释"改了什么、为什么改"

**传统文档更新流程**:

```
用户提交代码 → AI检测到变更 → AI问:"这次改了什么?为什么改?"
           → 用户手动解释(10min) → AI更新文档
```

**用户负担**:

- 需要重复解释变更意图
- 解释可能不准确或遗漏关键信息
- 增加文档更新的认知负荷

### Git 安全痛点 🆕

**AI 编程的 Git 风险**:

1. ❌ AI 可能误操作保护分支(main/master)
2. ❌ AI 可能执行危险的历史重写(`git reset --hard`, `git push --force`)
3. ❌ AI 可能自动合并代码,绕过人工审核
4. ❌ 缺少明确的 AI Git 操作安全红线

**后果**:

- 主分支污染
- 代码误删
- 绕过 Code Review 流程
- 生产环境风险

---

## 💡 解决方案

### 核心理念 1: Commit-as-Prompt

**参考**: `dev/reference/高效提交git.md`

将 Git 提交信息转化为结构化的 AI 上下文,通过**WHAT/WHY/HOW**三段式结构记录变更意图:

- **WHAT** (做什么): 一句话描述变更的核心动作和目标对象
- **WHY** (为什么做): 深入阐述动机(业务需求、技术债、架构决策)
- **HOW** (怎么做): 概述实现策略、风险点、影响范围

**示例 commit**:

```bash
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW: User模型新增points字段,API端点/api/points,使用乐观锁避免并发问题"
```

### 核心理念 2: Git 安全规范 🆕

**明确 AI 操作 Git 的安全红线**,保护主分支和生产环境。

---

## 🛡️ Git 安全规范与工作流

### 安全红线定义

#### 绝对禁止区 (RED ZONE) ⛔

**AI 绝对不能执行的 Git 操作**:

1. **保护分支操作**:

   - ⛔ 在 `main`, `master`, `production`, `release/*` 分支 commit/push
   - ⛔ 从保护分支直接创建 feature 分支

2. **危险的历史重写**:

   - ⛔ `git reset --hard`
   - ⛔ `git rebase`
   - ⛔ `git push --force`

3. **合并操作**:

   - ⛔ `git merge` (除了 `git merge --abort`)
   - ⛔ 用户必须手动处理所有合并

4. **分支删除和标签操作**:
   - ⛔ `git branch -D` (强制删除)
   - ⛔ 创建/删除/修改标签

#### 受限操作区 (YELLOW ZONE) ⚠️

**需明确授权的操作**:

- `git checkout -b [feature-branch]` - 需确认分支名
- `git commit` - 需审核 commit message
- `git push origin [feature-branch]` - 需确认推送分支

### Git 安全分级策略 🆕

**配置模式**: strict / standard / permissive

```yaml
git_safety:
  mode: "standard" # 默认模式

  # strict规则: 绝对不可覆盖
  strict_rules:
    block_force_push: true # 无override
    block_merge: true # AI绝不可merge

  # standard规则: 默认阻止，可通过明确授权
  standard_rules:
    protected_branches: ["main", "master"]
    require_branch_naming: true
    warn_on_large_commit: true # 单commit超过500行警告

  # permissive规则: 仅警告，不阻止
  permissive_rules:
    check_commit_message: false # 不强制prompt:格式
    allow_direct_push_to_dev: true

# Token优化配置 🆕
commit_guided_documentation:
  enabled: true

  # Commit-as-Prompt配置
  commit_format:
    prefix_aliases: ["prompt", "ai", "doc"] # 任一前缀即可触发，默认prompt
    require_what: true
    require_why: true
    require_how: true

  # Token优化配置
  token_optimization:
    time_window_days: 7 # 默认分析最近7天commit
    max_commits_per_batch: 50 # 单批次最多分析commit数
    enable_aggregation: true # 启用同类commit聚合
    skip_doc_only_commits: true # 跳过纯文档commit

  # 自动文档更新
  auto_detect_updates: true
  auto_generate_draft: true
  require_user_confirmation: true
```

**关键原则**:

- **Strict 规则不可配置** - 保护核心安全底线
- **Standard 规则可授权** - 明确授权后放行（留审计记录）
- **Permissive 规则可关闭** - 用户自主选择

### 推荐 Git 工作流示例 🆕

#### Feature Branch Workflow

**标准流程**:

```
main/master (保护) → dev → feature/xxx (AI开发) → PR (用户合并) → dev → main
```

**职责分工**:

- **AI**: 创建 feature 分支、开发代码、提交和推送
- **用户**: 合并 PR、解决冲突、发布 tag

**完整工作流示例** (整合 Commit-as-Prompt):

```bash
# Step 0: AI根据任务描述，评估创建分支的必要性并给出推荐
AI: "建议创建feature分支: feature/user-points-system (Y/n)?"

# Step 1: AI创建feature分支
git checkout -b feature/user-points-system

# Step 2: AI开发代码
# ... 编码 ...

# Step 3: AI使用Commit-as-Prompt提交
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW: User模型新增points字段,API端点/api/points,使用乐观锁避免并发问题"

# Step 4: AI推送到feature分支
git push origin feature/user-points-system
✅ Git安全检查通过: feature分支，允许push

# Step 5: AI自动检测文档更新需求
AI: "📝 检测到以下文档需要更新:
- dev_docs/api_layer.md
- dev_docs/database_schema.md
生成更新草稿? (Y/n)"

# Step 6: 提示用户创建PR
AI: "代码已推送到 feature/user-points-system
请在GitHub创建PR并合并到dev"

# Step 7: 用户手动合并
# 在GitHub/GitLab创建PR并审核
# 必须由用户自己执行Merge操作
```

---

## 📊 Commit 类型处理策略 🆕

### 1. 结构化 Commit (prompt: 前缀)

**优先级**: 最高

**处理**: 自动解析 WHAT/WHY/HOW，精准定位文档更新需求

**前缀别名支持**:

```yaml
commit_guided:
  prefix_aliases: ["prompt", "ai", "doc"] # 任一前缀即可触发，默认prompt
  compatible_with_conventional: true # 兼容feat/fix格式
```

**示例**:

```bash
# 方式1: 原始提议
git commit -m "prompt(feature): 新增积分系统"

# 方式2: 中文友好
git commit -m "ai(feature): 新增积分系统"

# 方式3: 兼容Conventional Commits
git commit -m "feat: 新增积分系统 [ai-doc]"
```

### 2. 传统 Commit (无特殊标识) 🆕

**降级策略**: 基于 diff + commit message 关键词分析

**触发条件**: 符合`core/update_triggers.md`的 P0/P1 条件

**处理流程**:

1. Git diff 分析影响范围
2. 提示用户补充变更意图
3. 生成简化版更新建议

### 3. 混合场景 🆕

**场景**: 同一 PR 包含多个 commit（部分结构化、部分传统）

**处理**: 聚合所有 commit 信息，优先使用结构化信息

---

## 📏 Commit 粒度最佳实践 🆕

### 推荐粒度

- **单一职责**: 一个 commit = 一个完整的逻辑变更
- **可独立回滚**: 该 commit 可以安全地被 revert
- **时间范围**: 1-4 小时的开发工作

### 不推荐的做法

- ❌ **Super Commit**: 一个 commit 包含多个功能模块
- ❌ **Micro Commit**: 过于细碎（如"修改空格"、"调整缩进"）
- ❌ **WIP Commit**: "work in progress"等占位提交

### 特殊场景

- **Monorepo**: 可跨 package，但需在 HOW 中明确影响范围
  ```
  HOW:
  - Affected Packages: @workspace/web-app, @workspace/shared-utils
  - User模型新增points字段
  ```
- **大型重构**: 拆分为多阶段 commit，每个阶段独立可测

---

## 🔄 合并冲突后的文档更新流程 🆕

### 场景

用户手动解决冲突并完成 merge 后

### 检测机制

1. AI 检测到新的 merge commit
2. 识别合并的 source branch 和 target branch
3. 扫描 source branch 的所有`prompt:`提交

### 处理流程

1. 聚合 source branch 的所有结构化 commit
2. 生成"合并后文档更新清单"
3. 提示用户确认并执行更新

### CLI 支持

```bash
python tools/py/commit_parser.py --merge-summary \
  --source feature/user-points \
  --target main
```

---

## 🎯 自动化程度边界定义 🆕

| 操作                            | 自动化级别        | 理由                       |
| ------------------------------- | ----------------- | -------------------------- |
| 解析 commit 提取 WHAT/WHY/HOW   | ✅ 完全自动       | 纯解析操作，无风险         |
| 分析 diff 确定影响文件          | ✅ 完全自动       | 只读操作                   |
| 生成文档更新草稿                | ✅ 完全自动       | 草稿不写入文件             |
| **确认文档更新并执行**          | ⚠️ **需人工确认** | **关键决策点**             |
| 在 feature 分支 commit          | ⚠️ 需审核 message | 预审核 commit 质量         |
| 在 feature 分支 push            | ⚠️ 需确认分支名   | 防止误 push                |
| 创建 feature 分支               | ⚠️ 需确认命名     | 分支命名影响团队协作       |
| **在 main/master 任何操作**     | ⛔ **绝对禁止**   | **红线**                   |
| **执行 merge 操作**             | ⛔ **绝对禁止**   | **必须用户手动**           |
| 生成 ADR 草稿（识别到架构决策） | ✅ 自动生成草稿   | 草稿不是正式文档，可自动化 |

**关键决策点示例**:

```markdown
📝 基于 commit 信息,检测到以下文档需要更新:

✅ 自动分析结果:

- dev_docs/api_layer.md (新增积分 API 章节)
- dev_docs/database_schema.md (User 表增加 points 字段)
- dev_docs/AI_Coding_Context.md (更新功能清单)

📋 生成的更新草稿:
[显示 diff preview 或 summary]

是否执行更新? (Y/n/e)

- Y: 执行更新
- n: 取消
- e: 编辑草稿后再执行
```

---

## 🔗 与 core/update_triggers.md 的关系 🆕

### 定位

Commit-Guided 是 Update Triggers 的"自动化增强层"

### 层级关系

```
Layer 3: Commit-Guided (智能层) ← 本优化点
  ↓ 基于
Layer 2: Update Triggers (规则层) ← 现有core/update_triggers.md
  ↓ 依赖
Layer 1: Git Diff (检测层) ← Git原生能力
```

### 协作模式

**1. 有 prompt:提交时**:

- 优先使用 WHAT/WHY/HOW 自动分类
- 自动映射到 P0/P1/P2 级别
- 精准定位受影响文档

**2. 无 prompt:提交时**:

- 降级到 update_triggers.md 的传统检测
- 基于 diff 分析+关键词匹配
- 可能需要用户补充信息

**3. 优先级继承**:

- Commit-Guided 不改变 P0/P1/P2 的定义
- 只是提供了"自动分类"能力

---

## 📊 Commit 质量评分机制 🆕

### 评分维度 (满分 100)

- **WHAT 清晰度** (30 分): 是否一句话说清楚做了什么
- **WHY 深度** (30 分): 是否说明了业务动机或技术原因
- **HOW 完整性** (20 分): 是否说明了实现策略和风险
- **粒度合理性** (10 分): commit 大小是否适中
- **可测试性** (10 分): 是否说明了如何验证

### 评分示例

```yaml
commit: abc123
score: 85/100
breakdown:
  what: 30/30 ✅
  why: 25/30 ⚠️ (缺少业务价值说明)
  how: 18/20 ✅
  granularity: 10/10 ✅
  testability: 2/10 ❌ (未说明测试方法)
suggestion: "建议补充验收标准"
```

### 应用

- 分数<60: AI 主动建议改进
- 分数 60-80: 给出优化建议但不阻塞
- 分数>80: 优质 commit，加入最佳实践示例库

---

## 🪝 Pre-commit Hook 集成 🆕

### 可选功能

用户可选择安装 pre-commit hook

### 安装方式

```bash
# 自动化安装脚本
python tools/py/install_hooks.py

# 手动安装
cp tools/git-hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Hook 功能

1. **格式检查**: 检查是否符合 prompt:格式（如果配置要求）
2. **结构验证**: 验证 WHAT/WHY/HOW 是否完整
3. **Git 安全检查**: 检测当前分支是否为保护分支
4. **友好提示**: 不合规时提供修复建议

### 关键设计

- ⚠️ Hook 不应阻塞紧急提交，提供`--no-verify`跳过
- ✅ Hook 应提供辅助命令自动生成合规 commit
- ✅ Hook 应可配置（团队 vs 个人）

---

## �️ CLI 工具使用示例 🆕

### 交互式 Commit 生成

**命令**:

```bash
python tools/py/commit_template_cli.py
```

**交互流程**:

```
📝 Commit-as-Prompt向导

[1/4] 变更类型:
  1. 新功能 (feature)
  2. Bug修复 (fix)
  3. 架构调整 (architecture)
  4. 其他

选择: 1

[2/4] WHAT - 做什么? (一句话描述)
> 新增用户积分系统

[3/4] WHY - 为什么做? (业务动机、需求编号)
> 提升用户活跃度,对应需求PRD-2024-156

[4/4] HOW - 怎么做? (实现策略、风险点)
> - User模型新增points字段
> - API端点: /api/points
> - 使用乐观锁避免并发

✅ 生成的commit:
--------------------
prompt(feature): 新增用户积分系统

WHAT: 新增用户积分系统
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW:
- User模型新增points字段
- API端点: /api/points
- 使用乐观锁避免并发
--------------------

💯 质量评分: 85/100 ✅
  - WHAT清晰度: 30/30
  - WHY深度: 25/30 (建议补充业务指标)
  - HOW完整性: 20/20
  - 粒度合理性: 10/10

执行? (Y/n)
```

### 快速模式

```bash
# 快速生成（跳过交互）
python tools/py/commit_template_cli.py --quick \
  --type feature \
  --what "新增用户积分系统" \
  --why "提升用户活跃度,对应需求PRD-2024-156" \
  --how "User模型新增points字段,API端点/api/points"
```

---

## �🔗 与其他 V3.0 功能的协同

### 与 003-设计思维引导 的闭环 ⭐⭐⭐⭐⭐

**增强 003 的 Step 5 输出**:

````markdown
## Step 5 - 最终决策

[... 现有内容 ...]

## 下一步行动

### Task List

1. [ ] 创建 feature 分支: feature/user-points-system
2. [ ] 实现 User 模型 points 字段（含 migration）
3. [ ] 实现 API 端点 /api/points

### Commit 指导 🆕

**建议 Commit 策略**: 分 3 个 commit 提交

Commit 1 - 数据模型:

```bash
prompt(feature): User模型新增积分字段

WHAT: 在User模型添加points字段,支持积分记录
WHY: 对应需求PRD-2024-156第1阶段,建立积分数据基础
HOW:
- 新增points字段(Integer, default=0)
- 生成migration文件
- 单元测试覆盖积分初始化和累加
```
````

````

**价值**: 无缝衔接，用户完成Step 5后立即知道如何规范提交

### 与 012-强制文档摘要 的协同 ⭐⭐⭐⭐

**自动填充摘要**:

```yaml
---
summary: "新增用户积分系统" (来自WHAT)
keywords: [积分, API, 乐观锁] (来自HOW)
related_files: [user.py, api_layer.md] (来自diff+HOW分析)
last_updated: 2025-12-03 (来自commit date)
---
````

### 与 013-AI 互审机制 的协同 ⭐⭐⭐⭐

**Reviewer 审查维度扩展**:

- ✅ WHY 是否充分? (不能是"需求要求")
- ✅ HOW 是否考虑了风险?
- ✅ 是否需要升级为 P0 更新?
- ✅ Git 操作是否安全? 🆕
- ✅ Commit 质量评分是否达标? 🆕

### 与 004-ADR 系统 的协同 ⭐⭐⭐⭐⭐

**架构决策自动记录**:

识别架构决策类 commit (WHY 提到"架构") → 自动生成 ADR 草稿

---

## 🛣️ 实施计划

### 阶段 0: 前置准备 (Week 0, 2 天) 🆕

- [ ] 确认 001 的 commit_analyst 角色可用性
- [ ] 与 003/012/013/004 的接口对齐会议
- [ ] 技术预研: Git API 在 Python/Node.js 中的最佳实践

### 阶段 1: 核心工具开发 (Week 1-3)

- [ ] `tools/py/git_safety.py` - Git 安全检查工具
- [ ] `tools/py/commit_parser.py` - Commit 解析器
- [ ] `tools/py/commit_template_cli.py` - 交互式 CLI
- [ ] `tools/py/commit_quality_scorer.py` - Commit 质量评分 🆕
- [ ] `tools/py/commit_aggregator.py` - 批量聚合，Token 优化 🆕
- [ ] 单元测试

### 阶段 2: 工作流集成 (Week 4-5)

- [ ] 创建 `workflows/commit_guided_update.md`
- [ ] 创建 `workflows/git_safety_workflow.md`
- [ ] 更新 `core/update_triggers.md` (新增 Commit-Guided 章节) 🆕
- [ ] 更新 `workflows/document_health_check.md` (适配 Commit-Guided 模式) 🆕
- [ ] 更新 `workflows/monorepo_workflow.md` (跨 package 影响分析) 🆕

### 阶段 3: AI 角色与规则 (Week 6)

- [ ] 创建 `agents/runtime/commit_analyst.md`
- [ ] 更新 `templates/AI_RULES_TEMPLATE.md` (添加 Git 安全规范)
- [ ] 更新 `agents/runtime/design_facilitator.md` (Step 5 增加 Commit 指导) 🆕
- [ ] 更新 `workflows/review-workflow.md` (新增 commit 质量审查维度) 🆕
- [ ] 更新 `workflows/review_standards/*.md` (新增 Git 安全检查点) 🆕

### 阶段 4: 配置、文档与集成测试 (Week 7-8)

- [ ] 更新 `config/CONFIG_TEMPLATE.md` (添加 git_safety 配置)
- [ ] 用户指南
- [ ] 最佳实践示例
- [ ] Pre-commit Hook 模板 🆕
- [ ] 集成测试用例设计 🆕
- [ ] 迁移指南 🆕

### 阶段 5: Beta 测试与迭代 (Week 9) 🆕

- [ ] 在 1-2 个真实项目试点
- [ ] 收集用户反馈
- [ ] 迭代优化 CLI 体验
- [ ] 调整配置默认值

---

## ⚠️ 风险与挑战

### 1. 用户习惯培养 ⭐⭐⭐

**挑战**: 开发者习惯简短 commit

**应对**:

- CLI 工具降低编写门槛
- 展示即时价值（"本次节省 10 分钟解释工作"）
- 作为可选功能,不强制
- 渐进式推广（阶段 1 可选 → 阶段 2 建议 → 阶段 3 规范）

**量化目标**: 3 个月内达到 30%团队采用率即视为成功

### 2. Commit 质量控制 ⭐⭐

**挑战**: WHAT/WHY/HOW 质量参差不齐

**应对**:

- 质量评分机制 🆕
- AI 审查 commit quality
- Pre-commit hook 🆕
- 团队 Code Review

### 3. 多语言兼容 ⭐

**挑战**: commit 可能是中文或英文

**应对**:

- 自动语言检测
- 支持中英文解析

### 4. Git 安全强制执行 ⭐⭐

**挑战**: 如何确保 AI 严格遵守 Git 安全规范

**应对（多层防护）**:

- Layer 1: AI_RULES.md (AI 自律)
- Layer 2: git_safety.py (工具检查)
- Layer 3: 013 互审 (二次验证)
- Layer 4: Pre-commit Hook (可选本地拦截)

### 5. Token 消耗过大 ⭐ 🆕

**挑战**: 大量 commit 的 WHAT/WHY/HOW 文本可能导致 Token 消耗过大

**应对**:

- 批量聚合同类变更
- 默认只分析最近 7 天的 commit（可配置）
- 智能过滤纯文档 commit

---

## 📊 价值评估

### 用户体验改善

**工作量减少**:

- 传统: 提交(2min) + 解释变更(10min) + 等待文档更新(15min) = 27min
- Commit-Guided: 结构化提交(3min) + 确认更新(2min) = 5min
- **节省**: 约 80% 的解释工作

### Git 安全保障

**风险降低**:

- 主分支污染风险: **-95%**
- 代码误删风险: **-70%**
- 绕过 Code Review 风险: **-100%**

### 知识沉淀

**形成闭环**: commit → 文档 → ADR → 知识库

---

## 📝 需要用户确认的设计选择

1. ❓ Commit 前缀: 使用`prompt`还是`ai`?是否需要兼容 Conventional Commits?

   - **建议**: 支持多种前缀别名，默认`prompt`

2. ❓ 强制程度: 是否提供 Pre-commit Hook?默认是警告还是阻塞?

   - **建议**: 提供可选 Hook，默认警告模式

3. ❓ 评分严格度: Commit 质量评分阈值设为多少?

   - **建议**: 60 分（低于 60 分 AI 主动建议改进）

4. ❓ 时间窗口: 默认分析最近多少天的 commit?

   - **建议**: 7 天（可配置 1 天/7 天/30 天/全部）

5. ❓ Git 安全模式: 默认使用 strict/standard/permissive?
   - **建议**: standard 模式（平衡安全性和灵活性）

---

## 📚 与 002 的关系说明

**本优化点整合了原 002-危险指令拦截系统 中的 Git 安全规范部分**

**整合原因**:

1. **天然契合**: Git 工作流本身就是 018 的核心组成部分
2. **避免重复**: 002 的自然语言拦截存在通用性问题,但 Git 安全是明确可验证的
3. **简化系统**: 减少优化点数量,降低系统复杂度

**002 取消决策**:

- 基于固定关键词的"危险指令拦截"无法适应不同团队习惯
- 已有足够防护机制(AI_RULES + 013 互审 + 003 设计思维)
- Git 安全部分有明确价值,故整合到 018

---

**创建日期**: 2025-12-03  
**重大更新**: 2025-12-11 (整合评估报告优化建议,新增 5 个 P0 章节和 5 个 P1 章节)  
**确认日期**: 2025-12-11  
**参考文档**: `dev/reference/高效提交git.md`  
**评估报告**: `C:\Users\zibuyu\.gemini\antigravity\brain\03ecf7bd-645e-4c14-8a58-2d64bce70c10\018_evaluation_report.md`  
**最终检查**: `C:\Users\zibuyu\.gemini\antigravity\brain\03ecf7bd-645e-4c14-8a58-2d64bce70c10\018_final_review.md`  
**讨论进度**: 100% (已确认)
