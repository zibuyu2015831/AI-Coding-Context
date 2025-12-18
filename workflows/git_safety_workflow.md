# Git 安全工作流

> **版本**: v1.0  
> **创建日期**: 2025-12-11  
> **用途**: 定义 AI 操作 Git 的安全规范和推荐工作流

---

## 📋 概述

Git 安全工作流明确定义了 AI 在操作 Git 时的安全边界,通过多层防护机制保护主分支和生产环境,避免误操作导致的代码丢失、历史污染或绕过审核流程。

**核心价值**:

- ✅ **保护主分支**: 绝对禁止 AI 直接操作 main/master 分支
- ✅ **防止历史重写**: 禁止危险的 `git reset --hard` 和 `git push --force`
- ✅ **强制人工审核**: 所有 merge 操作必须由用户手动执行
- ✅ **多层防护**: AI 规则 + 工具检查 + 互审机制 + Pre-commit Hook

---

## 🛡️ 安全红线定义

### 绝对禁止区 (RED ZONE) ⛔

**AI 绝对不能执行的 Git 操作**:

#### 1. 保护分支操作

```bash
# ⛔ 禁止在保护分支commit
git checkout main
git commit -m "..."  # 绝对禁止

# ⛔ 禁止在保护分支push
git push origin main  # 绝对禁止

# ⛔ 禁止从保护分支直接创建feature分支
git checkout main
git checkout -b feature/xxx  # 绝对禁止(应从dev创建)
```

**保护分支列表**:

- `main`
- `master`
- `production`
- `release/*` (所有 release 分支)

#### 2. 危险的历史重写

```bash
# ⛔ 禁止硬重置
git reset --hard HEAD~1  # 绝对禁止

# ⛔ 禁止变基
git rebase main  # 绝对禁止

# ⛔ 禁止强制推送
git push --force  # 绝对禁止
git push -f  # 绝对禁止
```

**例外**: `git reset --soft` 在 feature 分支可以使用(需明确授权)

#### 3. 合并操作

```bash
# ⛔ 禁止merge
git merge dev  # 绝对禁止

# ✅ 允许: 中止merge
git merge --abort  # 允许(恢复操作)
```

**原则**: 所有 merge 必须由用户手动执行,AI 不能代替用户做合并决策

#### 4. 分支删除和标签操作

```bash
# ⛔ 禁止强制删除分支
git branch -D feature/xxx  # 绝对禁止

# ⚠️ 受限: 普通删除(需确认)
git branch -d feature/xxx  # 需用户确认

# ⛔ 禁止标签操作
git tag v1.0.0  # 绝对禁止
git tag -d v1.0.0  # 绝对禁止
git push --tags  # 绝对禁止
```

---

### 受限操作区 (YELLOW ZONE) ⚠️

**需明确授权的操作**:

#### 1. 创建分支

```bash
# ⚠️ 需确认分支名
git checkout -b feature/user-points-system
```

**检查项**:

- [ ] 分支名符合命名规范 (feature/\*, bugfix/\*, hotfix/\*)
- [ ] 从正确的基准分支创建 (通常是 dev,而非 main)
- [ ] 用户已确认分支名

**AI 提示**:

```markdown
建议创建 feature 分支: feature/user-points-system

基准分支: dev
命名规范: ✅ 符合 feature/\* 格式

是否创建? (Y/n)
```

#### 2. 提交代码

```bash
# ⚠️ 需审核commit message
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: ..."
```

**检查项**:

- [ ] Commit message 格式规范
- [ ] 当前分支不是保护分支
- [ ] Commit 粒度合理 (单次 commit <500 行)

**AI 提示**:

```markdown
准备提交代码:

分支: feature/user-points-system ✅
文件: src/models/user.py, src/api/points.py
变更: +135 行, -2 行

Commit message:
prompt(feature): 新增用户积分系统
WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度
HOW: User 模型新增 points 字段,API 端点/api/points

质量评分: 85/100 ✅

是否提交? (Y/n/e)
```

#### 3. 推送代码

```bash
# ⚠️ 需确认推送分支
git push origin feature/user-points-system
```

**检查项**:

- [ ] 推送的是 feature 分支,而非保护分支
- [ ] 没有使用 `--force` 参数
- [ ] 用户已确认推送操作

**AI 提示**:

```markdown
准备推送代码:

本地分支: feature/user-points-system
远程分支: origin/feature/user-points-system
Commits: 3 个新提交

✅ Git 安全检查通过: feature 分支,允许 push

是否推送? (Y/n)
```

---

### 安全操作区 (GREEN ZONE) ✅

**无需授权,可自动执行的操作**:

```bash
# ✅ 查看状态
git status
git log
git diff

# ✅ 切换分支(非保护分支)
git checkout feature/xxx

# ✅ 暂存文件
git add src/models/user.py

# ✅ 拉取代码
git pull origin dev

# ✅ 查看分支
git branch
git branch -r

# ✅ 中止操作
git merge --abort
git rebase --abort
```

---

## 📊 Git 安全分级策略

### 配置模式

框架提供三种安全模式: **strict** / **standard** / **permissive**

```yaml
git_safety:
  mode: "standard" # 默认模式

  # strict规则: 绝对不可覆盖
  strict_rules:
    block_force_push: true # 无override
    block_merge: true # AI绝不可merge
    block_protected_branch_operations: true # 保护分支绝对禁止
    block_history_rewrite: true # 历史重写绝对禁止

  # standard规则: 默认阻止,可通过明确授权
  standard_rules:
    protected_branches: ["main", "master", "production", "release/*"]
    require_branch_naming: true # 强制分支命名规范
    warn_on_large_commit: true # 单commit超过500行警告
    require_commit_message_format: false # 不强制prompt:格式

  # permissive规则: 仅警告,不阻止
  permissive_rules:
    check_commit_message: false # 不检查commit格式
    allow_direct_push_to_dev: true # 允许直接push到dev
    warn_on_branch_divergence: true # 分支分叉时警告
```

### 模式对比

| 规则类别     | strict 模式 | standard 模式 | permissive 模式 |
| ------------ | ----------- | ------------- | --------------- |
| 保护分支操作 | ⛔ 绝对禁止 | ⛔ 绝对禁止   | ⛔ 绝对禁止     |
| 强制推送     | ⛔ 绝对禁止 | ⛔ 绝对禁止   | ⛔ 绝对禁止     |
| Merge 操作   | ⛔ 绝对禁止 | ⛔ 绝对禁止   | ⛔ 绝对禁止     |
| 分支命名规范 | ⛔ 强制     | ⚠️ 警告       | ✅ 不检查       |
| Commit 格式  | ⛔ 强制     | ⚠️ 建议       | ✅ 不检查       |
| 大 Commit    | ⛔ 阻止     | ⚠️ 警告       | ✅ 允许         |

**关键原则**:

- **Strict 规则不可配置** - 保护核心安全底线,无论哪种模式都强制执行
- **Standard 规则可授权** - 明确授权后放行,留审计记录
- **Permissive 规则可关闭** - 用户自主选择

---

## 🔄 推荐 Git 工作流

### Feature Branch Workflow (推荐)

**标准流程**:

```
main/master (保护) → dev → feature/xxx (AI开发) → PR (用户合并) → dev → main
```

**职责分工**:

| 操作              | AI  | 用户 |
| ----------------- | --- | ---- |
| 创建 feature 分支 | ✅  | ✅   |
| 开发代码          | ✅  | ✅   |
| Commit 和 Push    | ✅  | ✅   |
| 创建 PR           | ❌  | ✅   |
| Code Review       | ✅  | ✅   |
| 合并 PR           | ❌  | ✅   |
| 解决冲突          | ⚠️  | ✅   |
| 发布 Tag          | ❌  | ✅   |
| 操作保护分支      | ❌  | ✅   |

**完整工作流示例**:

```bash
# ========== AI 操作部分 ==========

# Step 0: AI评估并推荐分支名
AI: "建议创建feature分支: feature/user-points-system
     基准分支: dev
     是否创建? (Y/n)"

# Step 1: AI创建feature分支
git checkout dev
git pull origin dev
git checkout -b feature/user-points-system
✅ Git安全检查通过: 从dev创建feature分支

# Step 2: AI开发代码
# ... 编码 ...

# Step 3: AI使用Commit-as-Prompt提交
git add src/models/user.py src/api/points.py
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW: User模型新增points字段,API端点/api/points,使用乐观锁避免并发问题"
✅ Git安全检查通过: feature分支,允许commit

# Step 4: AI推送到feature分支
git push origin feature/user-points-system
✅ Git安全检查通过: feature分支,允许push

# Step 5: AI自动检测文档更新需求
AI: "📝 检测到以下文档需要更新:
     - dev_docs/api_layer.md
     - dev_docs/database_schema.md
     生成更新草稿? (Y/n)"

# Step 6: AI提示用户创建PR
AI: "代码已推送到 feature/user-points-system
     请在GitHub/GitLab创建PR并合并到dev"

# ========== 用户操作部分 ==========

# Step 7: 用户在GitHub/GitLab创建PR
# (Web界面操作)

# Step 8: 用户或团队进行Code Review
# (Web界面操作)

# Step 9: 用户手动合并PR
# (Web界面操作,点击"Merge"按钮)
# ⚠️ 必须由用户自己执行,AI绝不可代替

# Step 10: 用户删除feature分支(可选)
git branch -d feature/user-points-system
git push origin --delete feature/user-points-system
```

---

### Hotfix Workflow (紧急修复)

**场景**: 生产环境紧急 bug 修复

**流程**:

```
main → hotfix/xxx (AI开发) → PR → main + dev
```

**示例**:

```bash
# Step 1: 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/fix-payment-bug
✅ Git安全检查通过: hotfix分支允许从main创建

# Step 2: AI修复bug
# ... 修复代码 ...

# Step 3: AI提交
git commit -m "prompt(hotfix): 修复支付金额计算错误" \
  -m "WHAT: 修复支付金额四舍五入导致的精度丢失
WHY: 生产环境发现部分订单金额不准确,影响财务对账
HOW: 使用Decimal类型替代float,保留2位小数"

# Step 4: AI推送
git push origin hotfix/fix-payment-bug

# Step 5: 用户创建PR,合并到main和dev
# (必须由用户手动操作)
```

---

## 🛠️ Git 安全检查工具

### tools/py/git_safety.py

**功能**:

1. 检查当前分支是否为保护分支
2. 验证 Git 命令是否安全
3. 建议符合规范的分支名

**使用方式**:

```bash
# 检查当前分支
python tools/py/git_safety.py --check-branch

# 验证Git命令
python tools/py/git_safety.py --validate-command "git push origin main"

# 建议分支名
python tools/py/git_safety.py --suggest-branch-name "用户积分系统"
```

**输出示例**:

```json
{
  "command": "git push origin main",
  "safety_level": "RED",
  "allowed": false,
  "reason": "禁止推送到保护分支main",
  "suggestion": "请创建feature分支: git checkout -b feature/user-points"
}
```

### 集成到 AI 工作流

**在执行 Git 操作前自动检查**:

```python
# AI内部逻辑(伪代码)
def execute_git_command(command):
    # 1. 安全检查
    result = git_safety.validate_command(command)

    if result['safety_level'] == 'RED':
        # 绝对禁止
        return f"⛔ 操作被拒绝: {result['reason']}"

    elif result['safety_level'] == 'YELLOW':
        # 需要用户确认
        user_confirm = ask_user(f"⚠️ {result['reason']}\n是否继续? (Y/n)")
        if not user_confirm:
            return "操作已取消"

    # 2. 执行命令
    return subprocess.run(command, shell=True)
```

---

## 🔒 多层防护机制

### Layer 1: AI_RULES.md (AI 自律)

**位置**: `templates/AI_RULES_TEMPLATE.md`

**内容**:

```markdown
## Git 操作安全规范

### 绝对禁止 (RED ZONE)

- ⛔ 在 main/master/production 分支 commit 或 push
- ⛔ 执行 git reset --hard
- ⛔ 执行 git push --force
- ⛔ 执行 git merge (除了 git merge --abort)

### 推荐工作流

1. 从 dev 创建 feature 分支
2. 在 feature 分支开发和提交
3. 推送到远程 feature 分支
4. 提示用户创建 PR
5. 用户手动合并 PR
```

### Layer 2: git_safety.py (工具检查)

**自动拦截**:

```bash
# AI尝试执行危险命令
git push --force origin main

# 工具自动拦截
⛔ 操作被拒绝: 禁止强制推送到保护分支
建议: 请创建feature分支并通过PR合并
```

### Layer 3: 013 互审机制 (二次验证)

**Reviewer 审查维度**:

- ✅ Git 操作是否安全?
- ✅ 是否遵循推荐工作流?
- ✅ Commit 质量是否达标?

### Layer 4: Pre-commit Hook (可选本地拦截)

**安装**:

```bash
python tools/py/install_hooks.py
```

**Hook 功能**:

1. 检测当前分支是否为保护分支
2. 验证 commit message 格式
3. 检查 commit 大小 (>500 行警告)

**示例**:

```bash
# 用户在main分支尝试commit
git commit -m "fix bug"

# Hook拦截
⛔ 错误: 禁止在保护分支main上commit
建议: git checkout -b feature/fix-xxx
```

---

## ⚠️ 常见错误处理

### 错误 1: 在保护分支 commit

**场景**:

```bash
git checkout main
git commit -m "fix bug"
```

**拦截**:

```
⛔ 操作被拒绝: 禁止在保护分支main上commit

建议:
1. 创建feature分支: git checkout -b feature/fix-xxx
2. 在feature分支commit
3. 推送并创建PR
```

### 错误 2: 尝试强制推送

**场景**:

```bash
git push --force origin feature/xxx
```

**拦截**:

```
⛔ 操作被拒绝: 禁止使用--force推送

原因: 强制推送会覆盖远程历史,可能导致团队成员代码丢失

建议:
1. 如果需要修改commit,使用git commit --amend
2. 如果分支分叉,使用git pull --rebase
3. 如果确实需要强制推送,请用户手动执行
```

### 错误 3: 尝试 merge

**场景**:

```bash
git merge dev
```

**拦截**:

```
⛔ 操作被拒绝: AI不能执行merge操作

原因: 合并代码是关键决策点,必须由用户手动执行

建议:
1. 推送代码到feature分支
2. 在GitHub/GitLab创建PR
3. 用户审核后手动合并
```

### 错误 4: 分支命名不规范

**场景**:

```bash
git checkout -b my-feature
```

**警告**:

```
⚠️ 分支命名不符合规范

当前: my-feature
建议: feature/my-feature

是否使用建议的分支名? (Y/n)
```

---

## 📊 安全审计

### 审计日志

**记录所有 Git 操作**:

```json
{
  "timestamp": "2025-12-11T10:00:00Z",
  "operation": "git push origin feature/user-points",
  "safety_level": "YELLOW",
  "user_confirmed": true,
  "result": "success"
}
```

### 定期审计

**检查项**:

- [ ] 是否有 AI 直接操作保护分支的记录
- [ ] 是否有强制推送的记录
- [ ] 是否有 merge 操作的记录
- [ ] 分支命名规范遵守率

**工具**:

```bash
# 审计最近30天的Git操作
python tools/py/git_audit.py --since "30 days ago"
```

---

## 🔗 相关文档

- [workflows/commit_guided_update.md](./commit_guided_update.md) - Commit 引导文档更新
- [templates/AI_RULES_TEMPLATE.md](../templates/AI_RULES_TEMPLATE.md) - AI 规则模板
- [workflows/013-review-workflow.md](./013-review-workflow.md) - AI 互审工作流

---

## 💡 快速参考

### 安全检查清单

```markdown
执行 Git 操作前检查:

- [ ] 当前分支不是保护分支
- [ ] 没有使用--force 参数
- [ ] 没有执行 merge 操作
- [ ] 分支命名符合规范
- [ ] Commit message 格式规范
- [ ] Commit 大小合理 (<500 行)
```

### CLI 工具速查

```bash
# 检查当前分支
python tools/py/git_safety.py --check-branch

# 验证命令
python tools/py/git_safety.py --validate-command "git push origin main"

# 建议分支名
python tools/py/git_safety.py --suggest-branch-name "用户积分系统"

# 安装Pre-commit Hook
python tools/py/install_hooks.py

# 审计Git操作
python tools/py/git_audit.py --since "30 days ago"
```

### 决策流程

```
准备执行Git操作
  ↓
检查安全级别
  ↓
RED → 拒绝执行,提示建议
YELLOW → 请求用户确认
GREEN → 直接执行
```

---

**版本**: v1.0  
**最后更新**: 2025-12-11  
**路径**: `workflows/git_safety_workflow.md`
