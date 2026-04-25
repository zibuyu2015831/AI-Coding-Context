# Commit-Guided Documentation 快速开始

**版本**: v1.0  
**最后更新**: 2025-12-11

---

## 📖 什么是 Commit-Guided Documentation?

Commit-Guided Documentation 是一种**将 Git 提交信息转化为 AI 上下文**的自动化文档更新方法。

### 核心理念

**传统方式**:

```
提交代码 → AI问"改了什么?" → 手动解释(10分钟) → AI更新文档
```

**Commit-Guided 方式**:

```
结构化提交 → AI自动解析 → 推荐文档更新 → 确认执行(2分钟)
```

**节省时间**: ~80%

---

## 🚀 5 分钟快速上手

### Step 1: 使用 CLI 工具生成 Commit

```bash
# 进入项目目录
cd your-project

# 运行交互式 CLI
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

执行? (Y/n)
```

### Step 2: AI 自动检测文档更新需求

提交后,AI 会自动:

1. **解析 commit** - 提取 WHAT/WHY/HOW
2. **分析影响** - 确定需要更新的文档
3. **生成草稿** - 创建文档更新建议

**示例输出**:

```markdown
📝 检测到以下文档需要更新:

✅ 自动分析结果:

- dev_docs/api_layer.md (新增积分 API 章节)
- dev_docs/database_schema.md (User 表增加 points 字段)
- dev_docs/AI_Coding_Context.md (更新功能清单)

📋 生成的更新草稿:
[显示 diff preview]

是否执行更新? (Y/n/e)

- Y: 执行更新
- n: 取消
- e: 编辑草稿后再执行
```

### Step 3: 确认并执行

选择 `Y` 后,AI 自动更新文档并生成新的 commit:

```bash
prompt(doc): 更新积分系统文档

WHAT: 更新API文档和数据库Schema文档
WHY: 保持文档与代码同步
HOW:
- api_layer.md新增积分API章节
- database_schema.md更新User表结构
```

---

## 🎯 Commit 格式规范

### 基本格式

```
prompt(type): 一句话描述

WHAT: 做了什么
WHY: 为什么做
HOW: 怎么做的
```

### Type 类型

| Type       | 说明     | 示例             |
| ---------- | -------- | ---------------- |
| `feature`  | 新功能   | 新增用户积分系统 |
| `fix`      | Bug 修复 | 修复登录超时问题 |
| `refactor` | 重构     | 重构支付模块架构 |
| `doc`      | 文档更新 | 更新 API 文档    |
| `perf`     | 性能优化 | 优化数据库查询   |
| `test`     | 测试     | 新增单元测试     |

### 前缀别名

支持多种前缀,任选其一:

```bash
prompt(feature): ...  # 推荐
ai(feature): ...      # 简短
doc(feature): ...     # 文档友好
```

### 完整示例

```bash
git commit -m "prompt(feature): 新增用户积分系统" \
  -m "WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW:
- User模型新增points字段(Integer, default=0)
- API端点: GET /api/points/:userId, POST /api/points/deduct
- 使用Redis乐观锁避免并发扣减问题
- 单元测试覆盖并发场景"
```

---

## 🛠️ 工具使用

### 1. 交互式 CLI (推荐)

```bash
python tools/py/commit_template_cli.py
```

**优点**:

- 🎯 引导式填写,不会遗漏字段
- 💯 实时质量评分
- ✅ 自动格式化

### 2. 快速模式

```bash
python tools/py/commit_template_cli.py --quick \
  --type feature \
  --what "新增用户积分系统" \
  --why "提升用户活跃度,对应需求PRD-2024-156" \
  --how "User模型新增points字段,API端点/api/points"
```

### 3. 质量评分工具

```bash
# 评分当前 commit message
python tools/py/commit_quality_scorer.py

# 评分指定 commit
python tools/py/commit_quality_scorer.py abc123
```

### 4. Commit 解析工具

```bash
# 解析最近5个 commit
python tools/py/commit_parser.py --max-count 5

# 解析最近7天的 commit
python tools/py/commit_parser.py --since "7 days ago"

# 聚合同类 commit
python tools/py/commit_aggregator.py --max-count 10
```

---

## 🛡️ Git 安全规范

### 安全红线 (绝对禁止)

AI **绝对不能**执行:

- ⛔ 在 `main/master/production` 分支直接 commit
- ⛔ `git reset --hard`
- ⛔ `git push --force`
- ⛔ `git merge` (除了 `git merge --abort`)

### 推荐工作流

```bash
# 1. 创建 feature 分支
git checkout -b feature/user-points-system

# 2. 开发代码
# ... 编码 ...

# 3. 使用 CLI 提交
python tools/py/commit_template_cli.py

# 4. 推送到远程
git push origin feature/user-points-system

# 5. 创建 PR (由用户手动操作)
# 在 GitHub/GitLab 创建 Pull Request

# 6. 合并 (由用户手动操作)
# 在 GitHub/GitLab 点击 Merge
```

### 安全检查工具

```bash
# 检查当前分支是否安全
python tools/py/git_safety.py check-branch

# 验证 Git 命令是否安全
python tools/py/git_safety.py validate-command "git push origin main"
```

---

## 🔧 可选配置

### 安装 Pre-commit Hook

```bash
# 安装 hook
python tools/py/install_hooks.py

# 卸载 hook
python tools/py/install_hooks.py --uninstall
```

**Hook 功能**:

- ✅ Commit message 格式检查
- ✅ WHAT/WHY/HOW 字段验证
- ✅ 保护分支检测
- ✅ 质量评分

**跳过 Hook** (紧急情况):

```bash
git commit --no-verify
```

### 配置文件

编辑 `config/user_config.md`:

```yaml
# Git 安全配置
git_safety:
  mode: standard # strict|standard|permissive
  protected_branches: ["main", "master", "production"]
  require_branch_naming: true

# Commit-Guided 配置
commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: true
    require_why: true
    require_how: true
  token_optimization:
    time_window_days: 7
    enable_aggregation: true
```

---

## 💡 最佳实践

### 1. Commit 粒度

**推荐**:

- ✅ 一个 commit = 一个完整的逻辑变更
- ✅ 可独立回滚
- ✅ 1-4 小时的开发工作

**不推荐**:

- ❌ Super Commit (一个 commit 包含多个功能)
- ❌ Micro Commit (过于细碎,如"修改空格")
- ❌ WIP Commit ("work in progress"占位)

### 2. WHAT 字段

**好的示例**:

- ✅ "新增用户积分系统"
- ✅ "修复登录超时导致的会话丢失"
- ✅ "重构支付模块为微服务架构"

**不好的示例**:

- ❌ "更新代码" (太模糊)
- ❌ "fix bug" (没说明什么 bug)
- ❌ "完成需求" (没说明什么需求)

### 3. WHY 字段

**好的示例**:

- ✅ "提升用户活跃度,对应需求 PRD-2024-156"
- ✅ "解决生产环境高并发下的数据不一致问题"
- ✅ "降低系统耦合度,便于未来扩展"

**不好的示例**:

- ❌ "需求要求" (没说明业务价值)
- ❌ "老板让改的" (没说明原因)

### 4. HOW 字段

**好的示例**:

```
HOW:
- User模型新增points字段(Integer, default=0)
- API端点: GET /api/points/:userId
- 使用Redis乐观锁避免并发问题
- 单元测试覆盖并发扣减场景
```

**不好的示例**:

```
HOW:
- 改了代码  # 太模糊
```

---

## ❓ 常见问题

### Q1: 必须使用 prompt: 格式吗?

**A**: 不是必须的。

- **推荐使用**: 可获得最佳的文档自动化支持
- **传统格式**: 仍然可用,但需要手动解释变更

### Q2: 如何处理紧急 Hotfix?

**A**: 紧急情况可跳过格式要求:

```bash
# 方式1: 跳过 pre-commit hook
git commit --no-verify -m "hotfix: 修复生产环境崩溃"

# 方式2: 使用简化格式
git commit -m "prompt(fix): 修复生产环境崩溃

WHAT: 修复支付接口空指针异常
WHY: 生产环境紧急修复
HOW: 增加null检查"
```

### Q3: 如何处理多人协作?

**A**: 团队协作建议:

1. **统一规范**: 团队约定使用 prompt: 格式
2. **安装 Hook**: 所有成员安装 pre-commit hook
3. **Code Review**: 在 PR 中检查 commit 质量
4. **培训**: 使用 CLI 工具降低学习成本

### Q4: Token 消耗会很大吗?

**A**: 不会,已优化:

- **聚合功能**: 同类 commit 聚合,减少 85%+ token
- **时间窗口**: 默认只分析最近 7 天
- **智能过滤**: 跳过纯文档 commit

### Q5: 如何迁移现有项目?

**A**: 渐进式迁移:

1. **阶段 1**: 新功能使用 prompt: 格式
2. **阶段 2**: Bug 修复也使用
3. **阶段 3**: 所有 commit 统一格式

不需要修改历史 commit。

---

## 📚 相关文档

- [Git 安全工作流](../workflows/git_safety_workflow.md)
- [Commit 引导更新工作流](../workflows/commit_guided_update.md)
- [工具使用文档](../tools/README.md)

---

**版本**: v1.0  
**维护者**: Framework Team  
**反馈**: 欢迎提出改进建议
