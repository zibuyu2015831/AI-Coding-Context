# Commit-Guided Documentation 迁移指南

**版本**: v1.0  
**最后更新**: 2025-12-11  
**适用对象**: 现有项目迁移到 Commit-Guided 模式

---

## 📋 迁移概述

### 迁移目标

将现有项目从**传统文档更新模式**迁移到**Commit-Guided 自动化模式**。

### 迁移收益

- ⏱️ **节省时间**: 减少 80%的变更解释工作
- 📝 **文档同步**: 自动检测并推荐文档更新
- 🛡️ **Git 安全**: 防止误操作保护分支
- 💯 **质量提升**: Commit 质量评分和改进建议

### 迁移原则

1. **渐进式**: 不需要一次性迁移所有内容
2. **向后兼容**: 传统 commit 仍然可用
3. **团队友好**: 提供工具降低学习成本
4. **可回退**: 随时可以禁用功能

---

## 🗺️ 迁移路线图

### 阶段 1: 准备阶段 (1-2 天)

**目标**: 了解功能,配置环境

#### 1.1 学习基础概念

- [ ] 阅读[快速开始指南](./commit_guided_quick_start.md)
- [ ] 了解 WHAT/WHY/HOW 三段式结构
- [ ] 熟悉 Git 安全规范

#### 1.2 配置框架

编辑 `config/user_config.md`:

```yaml
# 启用 Commit-Guided (默认已启用)
commit_guided_documentation:
  enabled: true

  # 初期可以放宽要求
  commit_format:
    require_what: false # 先不强制
    require_why: false
    require_how: false

  # Token 优化
  token_optimization:
    time_window_days: 7
    enable_aggregation: true

# Git 安全配置
git_safety:
  mode: standard # 标准模式
  protected_branches: ["main", "master"]
```

#### 1.3 安装工具 (可选)

```bash
# 安装 pre-commit hook (可选,建议先不装)
# python tools/py/install_hooks.py
```

**建议**: 初期不安装 hook,先熟悉流程

---

### 阶段 2: 试点阶段 (1 周)

**目标**: 在新功能开发中试用

#### 2.1 选择试点场景

**推荐试点**:

- ✅ 新功能开发 (feature)
- ✅ 小型重构
- ❌ 紧急 Hotfix (暂不试点)
- ❌ 大型架构调整 (暂不试点)

#### 2.2 使用 CLI 工具

```bash
# 开发新功能时
git checkout -b feature/new-feature

# 完成开发后,使用 CLI 生成 commit
python tools/py/commit_template_cli.py
```

#### 2.3 观察 AI 行为

提交后观察 AI 是否:

- ✅ 正确解析 commit
- ✅ 推荐合理的文档更新
- ✅ 生成准确的更新草稿

#### 2.4 收集反馈

记录问题:

- CLI 工具是否易用?
- AI 推荐是否准确?
- 文档更新是否合理?

---

### 阶段 3: 推广阶段 (2-4 周)

**目标**: 团队逐步采用

#### 3.1 团队培训

**培训内容** (30 分钟):

1. **演示 CLI 工具** (10 分钟)

   - 现场演示生成一个 commit
   - 展示质量评分功能

2. **讲解格式规范** (10 分钟)

   - WHAT/WHY/HOW 的含义
   - 好的示例 vs 不好的示例

3. **Git 安全规范** (10 分钟)
   - 保护分支规则
   - 推荐工作流

**培训材料**:

- [快速开始指南](./commit_guided_quick_start.md)
- [完整规范文档](../../dev_docs/architecture/decisions/003-commit-guided-documentation.md)

#### 3.2 制定团队规范

**示例规范**:

```markdown
## 团队 Commit 规范 (v1.0)

### 必须遵守

- ⛔ 禁止在 main/master 分支直接 commit
- ⛔ 禁止使用 git push --force

### 强烈推荐

- ✅ 新功能使用 prompt(feature): 格式
- ✅ Bug 修复使用 prompt(fix): 格式
- ✅ 使用 CLI 工具生成 commit

### 可选

- 📝 安装 pre-commit hook
- 📝 Commit 质量评分 > 60 分
```

#### 3.3 设置 Code Review 检查点

在 PR 模板中添加:

```markdown
## Commit 质量检查

- [ ] Commit message 清晰描述了变更内容
- [ ] 使用了 prompt: 格式 (推荐)
- [ ] 包含 WHAT/WHY/HOW (如适用)
- [ ] 没有在保护分支直接 commit
```

#### 3.4 渐进式强制

**Week 1-2**: 鼓励使用,不强制

```yaml
commit_format:
  require_what: false
  require_why: false
  require_how: false
```

**Week 3-4**: 新功能强制使用

```yaml
commit_format:
  require_what: true # 开始要求 WHAT
  require_why: false
  require_how: false
```

**Week 5+**: 全面要求

```yaml
commit_format:
  require_what: true
  require_why: true
  require_how: true
```

---

### 阶段 4: 优化阶段 (持续)

**目标**: 根据反馈持续优化

#### 4.1 监控指标

**采用率**:

```bash
# 统计使用 prompt: 格式的 commit 比例
python tools/py/commit_parser.py --since "30 days ago" | grep "Structured:"
```

**质量评分**:

```bash
# 统计平均质量评分
python tools/py/commit_quality_scorer.py --batch --since "30 days ago"
```

#### 4.2 调整配置

根据团队反馈调整:

```yaml
# 如果团队觉得太严格
commit_format:
  require_how: false # 放宽 HOW 要求

# 如果 Token 消耗过大
token_optimization:
  time_window_days: 3 # 缩短时间窗口
  max_commits_per_batch: 30 # 减少批次大小
```

#### 4.3 建立最佳实践库

收集优质 commit 示例:

````markdown
## 团队优质 Commit 示例

### 新功能开发

```bash
prompt(feature): 新增用户积分系统

WHAT: 实现积分累积、消耗和过期功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW:
- User模型新增points字段
- API端点: /api/points
- 使用Redis乐观锁避免并发
- 单元测试覆盖并发场景
```
````

````

---

## 🔧 常见迁移场景

### 场景 1: 小型团队 (2-5人)

**推荐策略**: 快速迁移

```yaml
# Week 1: 全员培训 + 试用
# Week 2: 全面启用

git_safety:
  mode: standard
  enable_pre_commit_hook: true  # 安装 hook

commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: true
    require_why: true
    require_how: true
````

### 场景 2: 中型团队 (6-20 人)

**推荐策略**: 分批迁移

```markdown
Week 1-2: 核心开发组试点
Week 3-4: 扩展到所有开发
Week 5+: 全面要求
```

**配置**:

```yaml
git_safety:
  mode: standard
  protected_branches: ["main", "master", "develop"]

commit_guided_documentation:
  enabled: true
  commit_format:
    require_what: true
    require_why: false # 初期不强制 WHY
    require_how: false
```

### 场景 3: 大型团队 (20+人)

**推荐策略**: 渐进式推广

```markdown
Month 1: 1-2 个小组试点
Month 2: 扩展到 5-10 个小组
Month 3: 全面推广
Month 4+: 优化和调整
```

**配置**:

```yaml
git_safety:
  mode: strict # 严格模式
  protected_branches: ["main", "master", "production", "release/*"]
  require_branch_naming: true
  enable_pre_commit_hook: true

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

## ❓ 迁移常见问题

### Q1: 需要修改历史 commit 吗?

**A**: 不需要。

- ✅ 只需从现在开始使用新格式
- ✅ 历史 commit 保持不变
- ✅ AI 会自动处理混合场景

### Q2: 团队成员不配合怎么办?

**A**: 渐进式推广 + 展示价值

1. **展示价值**: 演示节省的时间
2. **降低门槛**: 提供 CLI 工具
3. **领导示范**: Leader 先用
4. **Code Review**: 在 PR 中温和提醒
5. **不强制**: 初期作为推荐,不强制

### Q3: 如何处理紧急 Hotfix?

**A**: 允许跳过

```bash
# 方式1: 跳过 hook
git commit --no-verify -m "hotfix: 紧急修复"

# 方式2: 使用简化格式
git commit -m "prompt(fix): 紧急修复生产问题

WHAT: 修复支付接口崩溃
WHY: 生产环境紧急修复
HOW: 增加null检查"
```

### Q4: 如何说服管理层?

**A**: 量化收益

**传统方式**:

- 提交代码: 2 分钟
- 解释变更: 10 分钟
- 等待文档更新: 15 分钟
- **总计**: 27 分钟

**Commit-Guided**:

- 结构化提交: 3 分钟 (使用 CLI)
- 确认更新: 2 分钟
- **总计**: 5 分钟

**节省**: 22 分钟/次 × 10 次/天 = 220 分钟/天 = **3.7 小时/天**

### Q5: 多语言项目如何处理?

**A**: 支持中英文

```yaml
commit_guided_documentation:
  commit_format:
    prefix_aliases: ["prompt", "ai", "智能"] # 支持中文
```

**示例**:

```bash
# 英文
prompt(feature): Add user points system

# 中文
prompt(feature): 新增用户积分系统

# 混合
prompt(feature): 新增用户积分系统

WHAT: Add user points system
WHY: Improve user engagement
HOW: ...
```

---

## 📊 迁移检查清单

### 准备阶段

- [ ] 团队成员阅读快速开始指南
- [ ] 配置 `config/user_config.md`
- [ ] 测试 CLI 工具
- [ ] 制定团队规范

### 试点阶段

- [ ] 选择 1-2 个试点项目
- [ ] 试点成员培训
- [ ] 收集反馈
- [ ] 调整配置

### 推广阶段

- [ ] 全员培训
- [ ] 更新 Code Review 流程
- [ ] 安装 pre-commit hook (可选)
- [ ] 监控采用率

### 优化阶段

- [ ] 收集优质示例
- [ ] 调整配置参数
- [ ] 持续改进流程

---

## 🆘 获取帮助

### 文档资源

- [快速开始指南](./commit_guided_quick_start.md)
- [完整规范](../../dev_docs/architecture/decisions/003-commit-guided-documentation.md)
- [Git 安全工作流](../../workflows/git_safety_workflow.md)
- [工具使用文档](../../tools/README.md)

### 常见问题

如遇到问题,请检查:

1. 配置文件是否正确
2. 工具是否正常运行
3. Git 仓库状态是否正常

---

**版本**: v1.0  
**维护者**: Framework Team  
**反馈渠道**: 欢迎提出改进建议
