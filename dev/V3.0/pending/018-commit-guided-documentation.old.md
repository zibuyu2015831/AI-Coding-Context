# 018 - Commit-Guided Documentation (基于 Commit 的文档更新)

**优先级**: P1  
**状态**: 🟡 待讨论  
**预估工作量**: 5-7 天  
**来源**: 用户提议 + `dev/reference/高效提交git.md`  
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

---

## 💡 解决方案

### 核心理念: Commit-as-Prompt

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

### 方案设计

#### 1. Commit Parser (工具层)

**新增工具**: `tools/py/commit_parser.py`, `tools/js/commit_parser.js`

**核心功能**:

```python
def parse_prompt_commits(repo_path, since=None):
    """
    解析 prompt: 类型的commit
    返回: List[{
        'hash': 'abc123',
        'date': '2025-12-03',
        'what': '...',
        'why': '...',
        'how': '...',
        'files': ['src/auth.py', ...]
    }]
    """

def aggregate_commits_to_context(commits):
    """
    聚合多个commits为<Context>格式
    <Context>
    1. [WHAT] ...
       [WHY] ...
       [HOW] ...
    </Context>
    """
```

#### 2. Commit-Guided Update Workflow (流程层)

**新增工作流**: `workflows/commit_guided_update.md`

**自动化流程**:

```
用户提交代码(含WHAT/WHY/HOW)
  ↓
AI检测到 prompt: 提交
  ↓
自动解析WHAT/WHY/HOW
  ↓
智能分类变更类型(新增模块/API变更/架构调整)
  ↓
精准定位需更新的文档(基于HOW+diff分析)
  ↓
生成文档更新草稿
  ↓
提示用户确认
```

#### 3. 增强 Update Triggers (规则层)

**更新**: `core/update_triggers.md`

**新增章节**: "Commit-Guided 自动触发"

**优先级映射**:

- WHAT 包含"新增模块" → P0
- WHAT 包含"数据库" → P0
- WHY 提到"架构决策" → P0 + 生成 ADR
- HOW 提到"breaking change" → P0

#### 4. 智能 Commit 模板生成器 (交互层)

**新增 CLI 工具**: `tools/py/commit_template_cli.py`

**交互式引导**:

```bash
$ python tools/py/commit_template_cli.py

📝 Commit-as-Prompt 向导

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

执行? (Y/n)
```

---

## 🔗 与其他功能的协同

### 与 003-设计思维引导 的闭环 ⭐⭐⭐⭐⭐

```
设计前 (003): AI引导 → 5 Why → 方案对比 → implementation_plan.md
          ↓
实施中: 用户编码
          ↓
提交时 (018): WHAT/WHY/HOW → AI验证 → 对比设计方案
          ↓
更新时: AI检测偏差 → 提醒用户
```

**价值**: 形成"设计 → 实施 → 验证"完整闭环

### 与 012-强制文档摘要 的协同 ⭐⭐⭐⭐

**自动填充摘要**:

```yaml
---
summary: "新增用户积分系统" (来自WHAT)
keywords: [积分, API, 乐观锁] (来自HOW)
related_files: [user.py, api_layer.md] (来自diff+HOW分析)
last_updated: 2025-12-03 (来自commit date)
---
```

### 与 013-AI 互审机制 的协同 ⭐⭐⭐⭐

**Reviewer 审查维度扩展**:

- ✅ WHY 是否充分? (不能是"需求要求")
- ✅ HOW 是否考虑了风险?
- ✅ 是否需要升级为 P0 更新?

### 与 004-ADR 系统 的协同 (待确认) ⭐⭐⭐⭐⭐

**架构决策自动记录**:

识别架构决策类 commit (WHY 提到"架构") → 自动生成 ADR 草稿

---

## 📊 价值评估

### 用户体验改善

**工作量减少**:

- 传统: 提交(2min) + 解释变更(10min) + 等待文档更新(15min) = 27min
- Commit-Guided: 结构化提交(3min) + 确认更新(2min) = 5min
- **节省**: 约 80% 的解释工作

**准确性提升**:

- 减少理解偏差 (用户口头解释 vs 结构化文本)
- commit 永久保存,可追溯

### 知识沉淀

**多层沉淀**:

1. **Git 历史**: commit message 本身
2. **文档**: 自动更新的技术文档
3. **ADR**: 架构决策记录 (如果适用)

**形成闭环**: commit → 文档 → ADR → 知识库

### 自动化程度

- 变更检测: 手动 → 自动
- 影响分析: 人工推测 → AI 精准分析
- 文档更新: 需解释 → 直接基于 commit

---

## 🛣️ 实施计划

### 阶段 1: 核心工具开发 (Week 1-2)

- [ ] `tools/py/commit_parser.py` - Commit 解析器
- [ ] `tools/py/commit_template_cli.py` - 交互式 CLI
- [ ] 单元测试

### 阶段 2: 工作流集成 (Week 3-4)

- [ ] 创建 `workflows/commit_guided_update.md`
- [ ] 更新 `core/update_triggers.md`
- [ ] 集成到 `workflows/incremental_update_workflow.md`

### 阶段 3: AI 角色与规则 (Week 5)

- [ ] 创建 `agents/runtime/commit_analyst.md`
- [ ] 更新 `templates/AI_RULES_TEMPLATE.md`

### 阶段 4: 文档与示例 (Week 6)

- [ ] 用户指南
- [ ] 最佳实践示例
- [ ] 更新框架 README

---

## ⚠️ 风险与挑战

### 1. 用户习惯培养 ⭐⭐⭐

**挑战**: 开发者习惯简短 commit

**应对**:

- CLI 工具降低编写门槛
- 展示价值(减少后续解释工作)
- 作为可选功能,不强制

### 2. Commit 质量控制 ⭐⭐

**挑战**: WHAT/WHY/HOW 质量参差不齐

**应对**:

- 模板验证
- AI 审查 commit quality
- 团队 Code Review

### 3. 多语言兼容 ⭐

**挑战**: commit 可能是中文或英文

**应对**:

- 自动语言检测
- 支持中英文解析

---

## 📝 讨论问题

1. ❓ `prompt:` 前缀是否合适?还是用其他标识?
2. ❓ 是否需要 Git hooks 强制检查 commit 格式?
3. ❓ 如何处理不使用 commit-as-prompt 的团队?(向后兼容)
4. ❓ CLI 工具是 Python 还是 Node.js 优先?
5. ❓ 是否需要与 GitHub/GitLab 集成(通过 API)?

---

**创建日期**: 2025-12-03  
**参考文档**: `dev/reference/高效提交git.md`  
**分析文档**: `dev/V3.0/reference/commit_as_prompt_analysis.md`  
**讨论进度**: 0%
