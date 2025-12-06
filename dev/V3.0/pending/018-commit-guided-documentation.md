# 018 - Commit-Guided Documentation (基于 Commit 的文档更新)

**优先级**: P1  
**状态**: 🟡 待讨论  
**预估工作量**: 8-10 天  
**来源**: 用户提议 + `dev/reference/高效提交git.md`  
**依赖**:

- 001 (AI 角色库) - 需要 `commit_analyst` 角色
- **002 (Dangerous Command Guard)** - 必须先于 018 实施(Git 工作流基础)
  **协同**: 003, 012, 013, 004 (可选)

---

## 📋 问题描述

### 核心痛点

**当前框架的变更检测机制**:

1. ✅ 已有 `core/update_triggers.md` 定义 P0/P1/P2 更新触发条件
2. ✅ 已有 `workflows/incremental_update_workflow.md` 增量更新流程
3. ✅ 已有 012-强制文档摘要 提供 `related_files` 自动检测
4. ❌ **但**: 未充分利用 commit message 中的**意图信息**
5. ❌ **导致**: 用户需要手动向 AI 解释"改了什么、为什么改"

**传统文档更新流程**:

```
用户提交代码 → AI检测到变更 → AI问:"这次改了什么?为什么改?"
           → 用户手动解释(10min) → AI更新文档
```

**用户负担**:

- 需要重复解释变更意图(已在 commit 中写过一次)
- 解释可能不准确或遗漏关键信息
- 增加文档更新的认知负荷

---

## 💡 解决方案

### 核心理念: Commit-as-Prompt

**理论基础**: `dev/reference/高效提交git.md`

将 Git 提交信息转化为结构化的 AI 上下文，通过 **WHAT/WHY/HOW** 三段式结构记录变更意图:

- **WHAT** (做什么): 一句话描述变更的核心动作和目标对象
- **WHY** (为什么做): 深入阐述动机(业务需求、技术债、架构决策)
- **HOW** (怎么做): 概述实现策略、风险点、影响范围

**示例 commit**:

```bash
git commit -m "feat(feature): 新增用户积分系统" \
  -m "WHAT: 实现积分累积和兑换功能
WHY: 提升用户活跃度,对应需求PRD-2024-156
HOW: User模型新增points字段,API端点/api/points,使用乐观锁避免并发问题"
```

### 方案设计

#### 设计原则 🆕

**与现有框架的分工**:

```
core/update_triggers.md (规则库):
- 定义"什么类型的变更对应什么优先级"的标准规则表

018 commit_parser (识别器):
- 从 WHAT/WHY/HOW 分析"本次变更属于什么类型"

018 priority_mapper (执行器):
- 调用 update_triggers 规则表进行优先级映射
```

**关键点**: 018 **不重新定义优先级规则**，而是**使用现有的 update_triggers 规则**

#### 1. Commit Parser (工具层)

**新增工具**: `tools/py/commit_parser.py`, `tools/js/commit_parser.js`

**核心功能**:

```python
def parse_structured_commits(repo_path, since=None):
    """
    解析包含 WHAT/WHY/HOW 结构的 commit
    支持检测模式:
      - 方案A: 检测 -m 第二段是否包含 WHAT:/WHY:/HOW: 关键字
      - 方案B: (可选) 检测特定前缀如 prompt:

    返回: List[{
        'hash': 'abc123',
        'date': '2025-12-03',
        'what': '...',
        'why': '...',
        'how': '...',
        'files': ['src/auth.py', ...]
    }]
    """

def classify_change_type(what, why, how):
    """
    基于 WHAT/WHY/HOW 分析变更类型
    - 使用 LLM 语义理解,而非简单关键词匹配
    - 返回: 新增模块 | API变更 | 架构调整 | Bug修复 | 重构
    """

def map_to_priority(change_type):
    """
    根据 core/update_triggers.md 规则映射优先级
    - 输入: 变更类型
    - 输出: P0 | P1 | P2
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

#### 2. Commit Quality Validator (质量控制) 🆕

**质量标准**: `config/commit_quality_standard.yaml`

```yaml
# Commit 质量标准

what_requirements:
  min_length: 10
  required_pattern: "^(新增|修改|删除|重构|优化|实现).*"

why_requirements:
  min_length: 20
  required_keywords:
    - must_contain_one: [业务需求, 技术债, 架构决策, 用户反馈, Bug修复]
  optional_references:
    - pattern: "PRD-\\d+|ISSUE-\\d+|#\\d+"
    - example: "对应需求PRD-2024-156"

how_requirements:
  min_length: 30
  should_include:
    - at_least_one: [实现策略, 影响范围, 风险点, 技术选型]
  required_info:
    - 必须说明"做了什么改动"(不能只说"修改了代码")

quality_enforcement:
  mode: soft # soft: 警告但允许 | strict: 拒绝提交
  soft_action: "allow_commit_but_mark_as_low_quality"
  strict_action: "reject_commit_until_fixed"
```

**验证工具**:

```python
# tools/py/commit_quality_validator.py

def validate_commit_quality(what, why, how):
    """
    验证 commit 质量
    返回: {
        'is_valid': bool,
        'quality_score': 0-100,
        'warnings': [...],
        'suggestions': [...]
    }
    """
```

#### 3. Commit-Guided Update Workflow (流程层)

**新增工作流**: `workflows/commit_guided_update.md`

**自动化流程** (基于 002-Git 安全工作流):

```
用户在 feature/* 分支提交(含WHAT/WHY/HOW)
  ↓
AI检测到结构化 commit (WHAT:/WHY:/HOW: 关键字)
  ↓
[质量验证] 检查 commit 质量是否达标
  ↓ (通过)
自动解析WHAT/WHY/HOW
  ↓
[变更分类] 使用 LLM 语义理解分类变更类型
  ↓
[优先级映射] 调用 update_triggers.md 规则确定 P0/P1/P2
  ↓
[文档定位] 调用 012-summary_related_checker 精准定位受影响文档
  ↓
[文档更新] 基于 WHY/HOW 上下文生成更新草稿
  ↓
提示用户确认并更新
```

**与 incremental_update_workflow 的集成点**:

```
现有步骤 1: 分析变更内容 (手动)
  ↓
018 增强步骤 1.5: 自动解析 commit (WHAT/WHY/HOW)
  ↓
现有步骤 1.5 (V3.0): 自动检测受影响文档 (012)
  ↓
018 增强: 基于 WHY/HOW 提供更新上下文
  ↓
现有步骤 2-5: 准备更新方案 → 执行 → 验证 → 更新摘要
```

#### 4. 降级策略: 无 Commit 场景处理 🆕

**边界情况**:

1. **用户直接告诉 AI 变更内容**: "我刚加了一个支付模块，更新文档"
2. **非 commit 触发的更新**: 手动修改配置文件，未提交
3. **批量 commit 统一更新**: 用户不想每次 commit 都触发

**降级策略**:

```python
def detect_update_trigger():
    """
    检测文档更新触发方式
    """
    if has_structured_commit():
        return "commit_guided"  # 优先使用 018
    elif user_manual_request():
        return "traditional"    # 降级到传统流程(AI 询问)
    elif batch_commit_mode():
        return "batch_analysis" # 聚合分析模式
```

**批量分析模式**:

```bash
# 分析最近 N 个结构化 commits 并聚合
python tools/py/commit_parser.py --since "7 days ago" --aggregate
```

#### 5. Lazy Mode (懒人模式) 🆕

**目标**: 降低用户编写 WHAT/WHY/HOW 的门槛

**工作流程**:

```
用户提交普通 commit: "添加支付功能"
  ↓
AI 检测到变更但无 WHAT/WHY/HOW 结构
  ↓
AI 分析 git diff 自动生成 WHAT/HOW 草稿:
  - WHAT: 新增支付模块 (基于新增文件 src/payment/)
  - HOW: 实现支付宝SDK集成、新增Payment模型 (基于 diff 分析)
  ↓
AI 询问用户: "我推测这次变更的 WHY 是..., 对吗?"
  ↓
用户确认/修改 WHY
  ↓
AI 使用完整的 WHAT/WHY/HOW 触发文档更新
```

**配置**:

```yaml
# config/config.yaml

commit_mode:
  mode: strict # strict: 强制手写 | lazy: AI 辅助生成
  lazy_mode_settings:
    auto_generate_what: true
    auto_generate_how: true
    require_user_confirm_why: true # WHY 必须用户提供
    mark_as_ai_generated: true # 标注为 AI 推测
```

#### 6. 增强 Update Triggers (规则层)

**更新**: `core/update_triggers.md`

**新增章节**: "Commit-Guided 自动触发"

**优先级映射示例**:

```markdown
### Commit-Guided 自动触发 (V3.0)

当检测到结构化 commit (WHAT/WHY/HOW) 时，根据以下规则自动映射优先级:

**P0 触发条件**:

- WHAT 包含: "新增核心模块"、"数据库 schema 变更"、"API 接口变更"
- WHY 提到: "架构决策"、"breaking change"
- HOW 提到: "影响所有模块"、"不兼容旧版"

**P1 触发条件**:

- WHAT 包含: "重大 Bug 修复"、"新增配置项"
- WHY 提到: "提升性能"、"优化用户体验"

**P2 触发条件**:

- WHAT 包含: "代码重构(无功能变更)"、"文档错误修正"

**注**: 具体判断由 `tools/py/commit_parser.py` 的 `classify_change_type()` 函数执行
```

#### 7. 交互式 CLI 工具 (可选)

**新增工具**: `tools/py/commit_template_cli.py`

> **注**: 此工具为可选功能，Phase 1 (MVP) 可暂不实现

---

## 🔗 与其他功能的协同

### 与 002-Dangerous Commander Guard 的强耦合 ⭐⭐⭐⭐⭐

**关键依赖**: 018 **必须等待 002 确认后实施**

**原因**:

1. 002 定义 Git 工作流(在哪个分支提交、何时触发)
2. 018 的文档更新触发点取决于 002 的分支策略:
   - 如果 AI 只能在 `feature/*` 分支提交，何时触发主文档更新?
   - 答案: **合并到 dev 后**触发，而非 feature 分支推送时

**协同流程**:

```
002 (Git Safety):
- AI 在 feature/* 分支提交
- 推送到远程 feature 分支
- 用户手动合并 PR 到 dev
  ↓
018 (Commit-Guided):
- 检测到 dev 分支新 commit (来自 feature 合并)
- 解析 WHAT/WHY/HOW
- 触发文档更新
```

### 与 003-设计思维引导 的闭环 ⭐⭐⭐⭐⭐

```
设计前 (003): AI引导 → 5 Why → 方案对比 → implementation_plan.md
          ↓
实施中: 用户编码(在 feature 分支)
          ↓
提交时 (018): WHAT/WHY/HOW → AI验证 → 对比设计方案
          ↓
更新时: AI检测偏差 → 提醒用户 → 更新 ADR(如果需要)
```

**价值**: 形成"设计 → 实施 → 验证"完整闭环

### 与 012-强制文档摘要 的协同 ⭐⭐⭐⭐

**自动填充摘要**:

```yaml
---
summary: "新增用户积分系统" # ← 来自 WHAT
keywords: [积分, API, 乐观锁] # ← 来自 HOW 提取
related_files: [user.py, api_layer.md] # ← 来自 diff + HOW 分析
last_updated: 2025-12-03 # ← 来自 commit date
verified_at: 2025-12-03 # ← 自动更新
---
```

### 与 013-AI 互审机制 的协同 ⭐⭐⭐⭐

**Reviewer 审查维度扩展**:

- ✅ WHY 是否充分? (不能是"需求要求"这种敷衍回答)
- ✅ HOW 是否考虑了风险?
- ✅ Commit 质量评分是否达标?
- ✅ 是否需要升级为 P0 更新?

### 与 004-ADR System 的协同 (待确认) ⭐⭐⭐⭐⭐

**架构决策自动记录**:

识别架构决策类 commit:

- WHY 包含关键词: "架构决策"、"设计权衡"、"技术选型"
- WHAT 包含: "引入...框架"、"切换...方案"

自动提示:

```
检测到架构决策 commit:
[WHAT] 切换状态管理从 Vuex 到 Pinia
[WHY] 架构决策: Pinia 提供更好的 TypeScript 支持和更简洁的 API

是否生成 ADR 草稿? (Y/n)
-> 基于 WHY/HOW 预填充 ADR 模板
```

**注**: 此功能依赖 004 确认并包含"自动生成 ADR"功能

---

## 🚧 边界问题与特殊场景

### 1. 多人协作场景 🆕

**问题**: 团队项目，多人提交结构化 commit

**处理策略**:

```yaml
团队协作模式:
  commit_ownership:
    - 每个成员的 commit 触发独立的文档更新建议
    - 文档更新采用"追加"而非"覆盖"模式

  conflict_resolution:
    - 如果 A 和 B 的 commit 影响同一文档
    - AI 汇总两者的 WHY/HOW
    - 生成综合更新方案

  aggregation:
    - 每周/每月汇总所有结构化 commits
    - 生成团队级别的文档更新报告
```

### 2. Commit 前缀方案 🆕

**推荐方案**: **不强制前缀，通过检测关键字识别**

**检测逻辑**:

```python
def is_structured_commit(commit_message):
    """
    检测 commit message 第二段(-m)是否包含 WHAT:/WHY:/HOW:

    兼容性:
    - ✅ 标准 Conventional Commits: feat:, fix:, docs:
    - ✅ 可选 prompt: 前缀(向后兼容高效提交git.md)
    - ✅ 任意前缀,只要 -m 第二段有结构即可
    """
    second_message = extract_second_message(commit_message)
    return has_what_why_how_keywords(second_message)
```

**示例**:

```bash
# 方式1: 使用 feat: (推荐)
git commit -m "feat(payment): 新增支付模块" \
  -m "WHAT: 实现支付宝SDK集成
WHY: 支持用户在线支付,对应PRD-2024-156
HOW: 新增Payment模型、API端点/api/payments"

# 方式2: 使用 prompt: (兼容高效提交git.md)
git commit -m "prompt(payment): 新增支付模块" \
  -m "WHAT: ...
WHY: ...
HOW: ..."

# 两者都可以被识别
```

### 3. Commit 与 "基于代码" 原则的兼容性 🆕

**V2.3 核心原则**: AI 不能臆测，必须基于实际代码

**Lazy Mode 的限制**:

```yaml
lazy_mode_constraints:
  ai_can_generate:
    - WHAT: 基于文件路径和 diff 推测(低风险)
    - HOW: 基于代码变更分析(中风险)

  user_must_provide:
    - WHY: 必须由用户提供(业务动机无法推测)

  safety:
    - 所有 AI 生成的内容标注为"待验证"
    - 用户必须确认后才触发文档更新
    - 严格模式(strict)禁用 Lazy Mode
```

---

## 💰 Token 成本分析 🆕

### 单次 Commit 成本

```
单个结构化 commit 处理:
- WHAT: 50 tokens
- WHY: 150 tokens
- HOW: 200 tokens
- 变更类型分析: 100 tokens (LLM)
- 优先级映射: 50 tokens
- 文档更新建议: 300 tokens (LLM)
──────────────────────────────
每次提交总计: ~850 tokens
```

### 月度成本估算

```
假设:
- 每天 5 个结构化 commits
- 30 天 = 150 commits
- 150 × 850 = 127,500 tokens/月

成本: ~$0.15 - $0.30 (GPT-4 Turbo)

ROI:
- 节省: 每次 10 分钟解释时间 × 150 次 = 25 小时/月
- 价值: 远超 token 成本
```

### 批量聚合优化

```
批量分析 90 天 commits:
- 仅聚合 WHAT: 50 tokens × 90 = 4,500 tokens
- 生成综合摘要: 500 tokens
- 总计: 5,000 tokens

相比逐个分析节省: 93% (127,500 - 5,000)
```

---

## 🔧 CI/CD 集成 (可选) 🆕

### Pre-commit Hook (推荐)

**安装 Git hook 验证 commit 格式**:

```bash
# .git/hooks/commit-msg
#!/usr/bin/env python3
import sys
from tools.py.commit_quality_validator import validate_commit_file

if __name__ == "__main__":
    commit_msg_file = sys.argv[1]
    result = validate_commit_file(commit_msg_file)

    if not result['is_valid']:
        print("❌ Commit 质量不达标:")
        for warning in result['warnings']:
            print(f"  - {warning}")
        print("\n建议:")
        for suggestion in result['suggestions']:
            print(f"  - {suggestion}")
        sys.exit(1)  # 拒绝提交
```

### CI 自动检查

**在 PR CI 流程中**:

```yaml
# .github/workflows/doc-sync-check.yml

name: 文档同步检查

on:
  pull_request:
    branches: [dev, main]

jobs:
  check-doc-sync:
    runs-on: ubuntu-latest
    steps:
      - name: 检测结构化 commits
        run: python tools/py/commit_parser.py --pr ${{ github.event.pull_request.number }}

      - name: 验证文档已更新
        run: |
          python tools/py/doc_sync_validator.py \
            --commits-file commits.json \
            --doc-dir dev_docs/

      - name: 标记 PR 状态
        if: failure()
        run: echo "::warning::检测到 P0 变更但文档未同步,请更新相关文档"
```

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
- 自动分类减少人为判断错误

### 知识沉淀

**多层沉淀**:

1. **Git 历史**: commit message 本身
2. **文档**: 自动更新的技术文档
3. **ADR**: 架构决策记录 (如果适用)

**形成闭环**: commit → 文档 → ADR → 知识库

### 自动化程度

- 变更检测: 手动 → 自动
- 影响分析: 人工推测 → AI 精准分析 (基于 WHY/HOW)
- 文档更新: 需解释 → 直接基于 commit

---

## 🛣️ 实施计划

### Phase 1: MVP (Week 1-3) - 核心功能

- [ ] `tools/py/commit_parser.py` - Commit 解析器
  - 支持检测 WHAT:/WHY:/HOW: 关键字
  - 变更类型分类(调用 LLM)
  - 优先级映射(调用 update_triggers 规则)
- [ ] `tools/py/commit_quality_validator.py` - 质量验证器
- [ ] `workflows/commit_guided_update.md` - 工作流文档
- [ ] 更新 `core/update_triggers.md` - 新增 Commit-Guided 章节
- [ ] 集成到 `workflows/incremental_update_workflow.md`
- [ ] 单元测试

**不包含**: CLI 工具、Pre-commit hook、ADR 集成

### Phase 2: 增强功能 (Week 4-5) - 可选

- [ ] `tools/py/commit_template_cli.py` - 交互式 CLI
- [ ] Lazy Mode 实现
- [ ] Pre-commit hook
- [ ] CI/CD 集成脚本

### Phase 3: 高级功能 (Week 6+) - 需 004 确认

- [ ] ADR 自动生成集成
- [ ] Commit 知识图谱
- [ ] 历史 commit 溯源分析工具

### Phase 4: AI 角色与规则 (Week 3-4)

- [ ] 创建 `agents/runtime/commit_analyst.md`
- [ ] 更新 `templates/AI_RULES_TEMPLATE.md`

### Phase 5: 文档与示例 (Week 5)

- [ ] 用户指南
- [ ] 最佳实践示例
- [ ] 更新框架 README

---

## ⚠️ 风险与挑战

### 1. 用户习惯培养 ⭐⭐⭐

**挑战**: 开发者习惯简短 commit

**应对**:

- ✅ CLI 工具降低编写门槛
- ✅ Lazy Mode 降低心理负担
- ✅ 展示价值(减少后续解释工作)
- ✅ 作为可选功能,不强制
- 🆕 提供真实 Before/After 对比案例

### 2. Commit 质量控制 ⭐⭐

**挑战**: WHAT/WHY/HOW 质量参差不齐

**应对**:

- ✅ 质量标准配置文件
- ✅ Pre-commit hook 验证
- ✅ 013-AI 审查 commit quality
- ✅ 团队 Code Review

### 3. 多语言兼容 ⭐

**挑战**: commit 可能是中文或英文

**应对**:

- Phase 1: 仅支持中文或英文(不混合)
- Phase 2: 自动语言检测 + 翻译
- 建议: 统一使用英文关键词 `WHAT:`/`WHY:`/`HOW:`

### 4. Git Hooks 跨平台兼容性 ⭐⭐

**挑战**: Windows/Mac/Linux 的 hook 执行可能不一致

**应对**:

- 使用 Python 实现 hook 逻辑(跨平台)
- 提供安装脚本自动配置

### 5. 依赖 002 未确认 ⭐⭐⭐⭐

**风险**: 如果 002 最终不包含 Git 工作流设计，018 需调整触发点

**应对**:

- 明确实施顺序: **002 必须先于 018**
- 如果 002 不包含 Git 工作流，018 降级为"仅检测 dev 分支 commit"

---

## 📝 讨论问题

### 必须确认 (MUST)

1. ❓ **依赖 002**: 是否等待 002-Dangerous Command Guard 确认后再实施?

   - 建议: 是，018 的触发点依赖 002 的 Git 工作流设计

2. ❓ **Commit 前缀**: 使用哪种识别方案?

   - 建议: 方案 C (不强制前缀，检测 WHAT:/WHY:/HOW: 关键字)

3. ❓ **质量强制模式**: 默认使用 soft 还是 strict?

   - 建议: soft (警告但允许)，团队可配置为 strict

4. ❓ **与 update_triggers 分工**: 是否同意 018 使用现有规则而非重新定义?
   - 建议: 同意，避免维护两套规则

### 建议讨论 (SHOULD)

5. ❓ **Lazy Mode**: 是否包含在 Phase 1?

   - 建议: Phase 2，先验证核心功能

6. ❓ **与 004 协同**: 是否一起规划形成知识沉淀闭环?

   - 建议: 联合讨论，但 018 可以先实施(不依赖 004)

7. ❓ **CLI 工具**: 是否必要?

   - 建议: Phase 2 可选功能

8. ❓ **无 commit 场景**: 降级策略是否合理?
   - 建议: 合理，但需明确文档

---

## 🔄 与现有框架的集成清单

### 需要更新的文档

1. ✅ `core/update_triggers.md` - 新增 Commit-Guided 章节
2. ✅ `workflows/incremental_update_workflow.md` - 集成步骤 1.5 增强
3. ✅ `templates/AI_RULES_TEMPLATE.md` - 新增 Commit 质量规则
4. ✅ `config/CONFIG_TEMPLATE.md` - 新增 commit_mode 配置

### 需要创建的目录/文件

1. `tools/py/commit_parser.py`
2. `tools/py/commit_quality_validator.py`
3. `tools/py/commit_template_cli.py` (Phase 2)
4. `workflows/commit_guided_update.md`
5. `agents/runtime/commit_analyst.md`
6. `config/commit_quality_standard.yaml`

---

**创建日期**: 2025-11-29  
**更新日期**: 2025-12-04  
**参考文档**:

- `dev/reference/高效提交git.md` - Commit-as-Prompt 理论
- `dev/V3.0/reference/git_safety_workflow_design.md` - Git 安全工作流  
  **讨论进度**: 100% (初稿完成，等待用户审核)
