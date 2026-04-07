# Git 安全工作流

> **版本**: v1.1  
> **更新日期**: 2026-04-07  
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
# ⚠️ 需进行诚信审计并审核 commit message
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: ..."
```

**检查项**:

- [ ] **诚信审计**: 运行 `commit_integrity_validator.py` 确保意图与物理变更匹配
- [ ] Commit message 格式规范
- [ ] 当前分支不是保护分支
- [ ] Commit 粒度合理 (单次 commit <500 行)

**AI 提示**:

```markdown
准备提交代码:

分支: feature/user-points-system ✅
文件: src/models/user.py, src/api/points.py
变更: +135 行, -2 行

🔍 **Commit 诚信审计**:
得分: 95 [EXCELLENT] ✅
意图与物理变更完美匹配。

Commit message:
prompt(feature): 新增用户积分系统
WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度
HOW: User 模型新增 points 字段,API 端点/api/points

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

# Step 3: AI使用Commit-as-Prompt提交并执行诚信审计
git add src/models/user.py src/api/points.py
# AI 内部调用: python tools/py/commit_integrity_validator.py --message "..."
AI: "🔍 Commit 诚信审计分数: 95/100 [EXCELLENT]
     拟提交: prompt(feature): 新增用户积分系统
     WHAT: 实现积分累积和兑换功能
     WHY: 提升用户活跃度
     HOW: User模型新增points字段,API端点/api/points
     是否执行提交? (Y/n)"

# Step 4: AI推送到feature分支
git push origin feature/user-points-system
✅ Git安全检查通过: feature分支,允许push

# Step 5: AI自动启动 Path C (增量文档更新)
AI: "✅ Commit 成功: abc123
     🚀 正在启动 Path C: 增量文档更新检测...
     检测到以下文档需要更新:
     - dev_docs/api_layer.md
     - dev_docs/database_schema.md
     是否生成更新草稿? (Y/n)"

# Step 6: AI提示用户创建PR
AI: "代码已推送到 feature/user-points-system
     请在GitHub/GitLab创建PR并合并到dev"
```

---

## 🛠️ Git 安全检查工具

### tools/py/git_safety.py

**功能**:

1. 检查当前分支是否为保护分支
2. 验证 Git 命令是否安全
3. 建议符合规范的分支名

### tools/py/commit_integrity_validator.py

**功能**:

1. 对比拟提交信息与实际代码变更
2. 识别“漏报”或“虚报”的文件
3. 输出诚信评分和修正建议

**使用方式**:

```bash
# 执行诚信审计
python tools/py/commit_integrity_validator.py --message "[COMMIT_MESSAGE]"
```

---

## 🔒 多层防护机制

### Layer 1: AI_RULES.md (AI 自律)

**位置**: `templates/AI_RULES_TEMPLATE.md`

**内容**: 包含 `Commit-Intent-Consistency` (意图一致性) 检查规范。

### Layer 2: 自动化审计工具 (自查)

- **`git_safety.py`**: 拦截危险命令和保护分支操作。
- **`commit_integrity_validator.py`**: 确保提交意图与物理变更一致。

### Layer 3: 013 互审机制 (二次验证)

**Reviewer 审查维度**:

- ✅ Git 操作是否安全?
- ✅ Commit 诚信评分是否达标?
- ✅ 是否遵循推荐工作流?

### Layer 4: Pre-commit Hook (可选本地拦截)

**安装**:

```bash
python tools/py/install_hooks.py
```

**Hook 功能**:

1. 检测当前分支是否为保护分支
2. 验证 commit message 格式
3. 检查 commit 大小 (>500 行警告)

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

---

## 🔗 相关文档

- [workflows/commit_guided_update.md](./commit_guided_update.md) - Commit 引导文档更新
- [templates/AI_RULES_TEMPLATE.md](../templates/AI_RULES_TEMPLATE.md) - AI 规则模板
- [workflows/review-workflow.md](./review-workflow.md) - AI 互审工作流

---

## 💡 快速参考

### 安全检查清单

```markdown
执行 Git 操作前检查:

- [ ] 当前分支不是保护分支
- [ ] **诚信审计**: Commit 信息准确反映了代码变更
- [ ] 没有使用 --force 参数
- [ ] 没有执行 merge 操作
- [ ] 分支命名符合规范
- [ ] Commit message 格式规范
- [ ] Commit 大小合理 (<500 行)
```

### CLI 工具速查

```bash
# 检查当前分支
python tools/py/git_safety.py --check-branch

# 验证 Git 命令
python tools/py/git_safety.py --validate-command "git push origin main"

# 诚信审计 (NEW)
python tools/py/commit_integrity_validator.py --message "..."

# 建议分支名
python tools/py/git_safety.py --suggest-branch-name "用户积分系统"
```

---

**版本**: v1.1  
**最后更新**: 2026-04-07  
**路径**: `workflows/git_safety_workflow.md`
