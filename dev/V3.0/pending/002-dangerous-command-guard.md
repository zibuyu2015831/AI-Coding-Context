# 002 - 危险指令拦截系统 (含 Git 安全规范)

**优先级**: P0  
**状态**: 🟡 待讨论  
**预估工作量**: 1-2 周  
**来源**: 《AI 编程的现状.md》洞察 + 《AI_PROGRAMMING_ANALYSIS.md》 + 用户 Git 安全需求  
**依赖**: 001 (AI 角色库) - 需要安全审查相关角色

---

## 📋 问题描述

### 原文关键洞察

> "人类自身发出的危险指令才是整个开发过程中最容易让 AI 越界的元凶（比如不管三七二十一让 AI 去实现一个功能或者修复某个错误）。"

### 核心痛点

**典型危险指令**:

1. "不管三七二十一，实现这个功能"
2. "快速修复这个 bug，不用管其他"
3. "直接复制那段代码就行"
4. "不用写文档，先让功能跑起来"
5. "跳过方案，直接开始写代码"

**后果**:

- 绕过框架规范
- 积累技术债
- 引入复杂性
- 文档不同步

---

## 💡 解决方案

### 危险模式库

```python
DANGEROUS_PATTERNS = [
    {
        "pattern": r"不管.*实现",
        "risk": "high",
        "message": "检测到跳过设计指令。建议先创建方案文档(plans/)。",
        "suggestion": "让我先为你生成一个方案，讨论技术选型和实施步骤。"
    },
    {
        "pattern": r"快速修复.*不用管",
        "risk": "high",
        "message": "检测到临时修复指令。建议评估长期影响。",
        "suggestion": "这个修复可能影响其他模块，让我先做影响分析。"
    },
    {
        "pattern": r"直接复制.*就行",
        "risk": "medium",
        "message": "检测到代码复制指令。建议提取公共函数。",
        "suggestion": "考虑提取为可复用函数，避免代码重复。"
    },
    {
        "pattern": r"不用.*(文档|更新)",
        "risk": "high",
        "message": "检测到跳过文档指令。违反框架规范。",
        "suggestion": "文档同步是框架规范，我会在编码后自动更新相关文档。"
    },
    {
        "pattern": r"跳过.*直接",
        "risk": "high",
        "message": "检测到跳过流程指令。",
        "suggestion": "遵循框架流程能减少50%的返工，让我们按标准流程来。"
    }
]
```

### 工作流程

```mermaid
graph TD
    A[用户输入] --> B{危险模式匹配?}
    B -->|否| C[正常执行]
    B -->|是| D[拦截并警告]
    D --> E[显示风险说明]
    E --> F[提供替代方案]
    F --> G{用户选择}
    G -->|接受建议| H[执行替代方案]
    G -->|坚持原指令| I[记录Override]
    I --> J[要求输入理由]
    J --> K[执行原指令]
    K --> L[记录到audit log]
```

### 拦截响应模板

```markdown
⚠️ **危险指令检测**

我注意到您的指令可能绕过框架规范:
"{用户原始指令}"

**风险**: {风险等级} - {风险说明}

**建议替代方案**:
{具体建议}

**如果您坚持**:
请输入 override 理由，我会记录到 audit log 并执行。
但这可能导致:

- 技术债累积
- 文档不同步
- 未来难以维护

您的选择: [接受建议] / [坚持原指令+理由]
```

---

## 📊 价值评估

**解决的痛点**:

- 阻止最大风险源（人为失误）
- 强制遵守框架规范
- 引导战略式思维

**预期效果**:

- 危险指令拦截率: 80%+
- 技术债减少: 30-40%
- 文档同步率: 从 75% → 95%

---

## ⚠️ 风险与疑问

1. ❓ 如何避免"狼来了"效应（拦截过于频繁）?
2. ❓ Override 理由是否需要人工审核?
3. ❓ 模式库如何持续更新?
4. ❓ 是否支持用户自定义危险模式?

---

## 🛡️ Git 操作安全规范 (新增)

### 背景

AI 编程具有危险性,可能误删代码或引入 bug。需要制定 AI 操作 Git 的安全红线。

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

### 推荐 Git 工作流

#### Feature Branch Workflow

**标准流程**:

```
main/master (保护) → dev → feature/xxx (AI开发) → PR (用户合并) → dev → main
```

**职责分工**:

- **AI**: 创建 feature 分支、开发代码、提交和推送
- **用户**: 合并 PR、解决冲突、发布 tag

**示例流程**:

```bash
# Step 1: AI创建feature分支
git checkout -b feature/user-points-system

# Step 2: AI开发并提交
git commit -m "prompt(feature): 新增用户积分系统"
git push origin feature/user-points-system

# Step 3: 用户手动合并 (关键!)
# 在GitHub/GitLab创建PR并审核
# 由用户点击Merge按钮
```

### 技术实现

**新增工具**:

- `tools/py/git_safety.py` - 分支检测和安全检查
- `tools/py/dangerous_git_ops.py` - 危险操作拦截

**AI Rules 集成**:

```markdown
## Git 操作安全规范

你**绝对不能**执行以下操作:

1. 在保护分支(main/master/production)操作
2. git reset --hard, git rebase, git push --force
3. git merge (用户必须手动合并)
4. 删除分支或标签

推荐工作流:

- 创建 feature 分支进行开发
- 在 feature 分支 commit 和 push
- 提醒用户手动创建 PR 并合并
```

### 与 018 的协同

**完美闭环**:

```
用户需求 → AI创建feature分支 → AI开发
    → AI使用Commit-as-Prompt提交(WHAT/WHY/HOW)
    → AI推送并自动检测文档更新
    → 提示用户创建PR → 用户手动合并
```

---

## 📊 价值评估 (更新)

**解决的痛点**:

- 阻止最大风险源（人为失误 + Git 误操作）
- 强制遵守框架规范
- 引导战略式思维
- **保护主分支和生产环境** ⭐ 新增

**预期效果**:

- 危险指令拦截率: 80%+
- 技术债减少: 30-40%
- 文档同步率: 从 75% → 95%
- **主分支污染风险: -95%** ⭐ 新增
- **代码误删风险: -70%** ⭐ 新增

---

**创建日期**: 2025-11-29  
**更新日期**: 2025-12-03 (补充 Git 安全规范)  
**参考文档**: `dev/V3.0/reference/git_safety_workflow_design.md`  
**讨论进度**: 0%
