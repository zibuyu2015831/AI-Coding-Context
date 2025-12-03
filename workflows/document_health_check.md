# 文档健康度检查流程

> **版本**: v2.3  
> **创建日期**: 2025-11-28  
> **用途**: 评估现有文档的健康度，决定是否需要更新

---

## 📋 概述

本文档详细说明如何检查已生成文档的健康度，帮助 AI 和用户判断文档是否需要更新。

### 适用场景

- 项目已有`dev_docs/`文档体系
- 距上次文档生成已有一段时间
- 用户不确定文档是否仍然准确
- 希望低成本评估文档状态

> 注意：本文记录的 tokens 消耗数量仅作为量级参考，并非实际消耗。

### 核心价值

- **节省 Token**: 快速扫描仅需~50 tokens（vs 重新生成的~5000 tokens）
- **科学评估**: 基于百分制的量化评分标准
- **灵活选择**: 提供 3 种检查模式，适应不同需求
  **检查内容**:

- 读取文档元数据（生成日期、覆盖文件列表）
- 统计当前代码文件数
- 对比文件数差异
- 计算时间差异
- 基础覆盖率评估

**执行时间**: ~1 分钟  
**Token 消耗**: ~50 tokens  
**输出**: 简化评估卡片

**输出示例**:

```markdown
📊 文档快速扫描结果

- 文档生成日期: 2025-09-15（74 天前）
- 文档记录文件: 148 个
- 当前代码文件: 156 个
- 差异: +8 个文件（+5.4%）

💡 初步评估: 文档可能部分过时
```

---

### 模式 2: 标准检查 ⭐（推荐）

**适用场景**: 常规文档评估，平衡准确度和成本

**检查内容**:

- 快速扫描所有项
- Git 变更历史分析（如可用）
- 核心文件采样检查（10-15 个关键文件）
- 变更影响分类（高/中/低风险）
- 健康度评分计算
- 详细更新建议

**执行时间**: 3-5 分钟  
**Token 消耗**: ~200-300 tokens  
**输出**: 标准健康度报告

**输出示例**:

```markdown
📄 文档健康度报告

## 📊 整体评估

- 健康度: 65 分（一般）
- 评级: 🟠 建议增量更新

## 📈 变更统计

- 文档最后更新: 2025-09-15
- 距今: 74 天
- 新增文件: 5 个
- 修改文件: 12 个（其中核心文件 3 个）
- 删除文件: 1 个

## 🎯 风险评估

### 🔴 高风险区域

- src/core/api.ts (核心模块重构)

### 🟡 中风险区域

- src/features/auth/ (新增模块)

### 🟢 低风险区域

- src/utils/ (轻微修改)

## 💡 更新建议

推荐方案: 增量更新
预计工作量: 2-3 小时
预计 token 消耗: 原生成量的 25%
```

---

### 模式 3: 深度分析 🔍

**适用场景**: 长期未更新或重大变更后的全面评估

**检查内容**:

- 标准检查所有项
- 完整 Git diff 分析（所有提交）
- 所有文件逐一对比
- 架构变更检测
- 依赖项变化分析
- 技术栈升级检测
- 精确影响评估
- 逐文件更新建议

**执行时间**: 10-15 分钟  
**Token 消耗**: ~800-1000 tokens  
**输出**: 详细分析报告 + 精确更新清单

**输出示例**:

```markdown
📄 文档深度分析报告

[包含标准报告所有内容，plus:]

## 📋 详细更新清单

### 必须更新（P0）

1. architecture_overview.md

   - 原因: src/core/重构，架构变化
   - 影响: 高
   - 预计工作量: 1 小时

2. 新增 authentication.md
   - 原因: src/features/auth/新增
   - 影响: 高
   - 预计工作量: 1.5 小时

### 建议更新（P1）

3. utilities.md
   - 原因: src/utils/部分修改
   - 影响: 中
   - 预计工作量: 30 分钟

### 可选更新（P2）

4. styling_guide.md
   - 原因: 样式文件轻微调整
   - 影响: 低
   - 预计工作量: 15 分钟
```

---

## 📊 健康度评分标准

### 评分模型（百分制）

```
健康度总分 = 100分 - 各类扣分项总和
```

**设计原则**:

- 初始满分 100 分
- 根据不同影响因素扣分
- 最终得分反映文档新鲜度和准确度

---

### 扣分项分类

#### A. 时间衰减因子（最多-30 分）

文档年龄越大，过时风险越高

| 文档年龄  | 扣分   | 说明                   |
| --------- | ------ | ---------------------- |
| 0-1 个月  | 0 分   | 极新鲜，通常无需更新   |
| 1-2 个月  | -5 分  | 新鲜，可能有小变化     |
| 2-3 个月  | -10 分 | 良好，建议检查         |
| 3-6 个月  | -20 分 | 需关注，可能有中等变化 |
| 6-12 个月 | -30 分 | 建议检查更新           |
| >12 个月  | -30 分 | 强烈建议更新           |

**计算公式**:

```python
age_months = (today - doc_date) / 30  # 天数转月数

if age_months <= 1:
    score_deduct = 0
elif age_months <= 2:
    score_deduct = 5
elif age_months <= 3:
    score_deduct = 10
elif age_months <= 6:
    score_deduct = 20
else:
    score_deduct = 30  # 上限30分
```

---

#### B. 代码变更影响（最多-50 分）

不同类型文件的变更对文档的影响不同

**文件变更权重表**:

| 文件类型 | 新增   | 修改   | 删除   | 示例文件                      |
| -------- | ------ | ------ | ------ | ----------------------------- |
| 核心入口 | -15 分 | -20 分 | -10 分 | index.ts, main.py, app.js     |
| 核心模块 | -10 分 | -15 分 | -8 分  | src/core/, src/api/, src/lib/ |
| 业务模块 | -5 分  | -8 分  | -5 分  | src/features/, src/services/  |
| 工具类   | -3 分  | -5 分  | -3 分  | src/utils/, src/helpers/      |
| 配置文件 | -8 分  | -10 分 | -5 分  | package.json, tsconfig.json   |
| 测试文件 | -2 分  | -3 分  | -2 分  | _.test.ts, _.spec.js          |
| 样式文件 | -1 分  | -2 分  | -1 分  | _.css, _.scss, \*.less        |

**核心文件识别规则**:

```markdown
核心入口文件:

- index.{js,ts,jsx,tsx,py,go,rs,java}
- main.{js,ts,py,go,rs,java,cpp}
- app.{js,ts,py,rb}
- server.{js,ts,py}

核心模块目录:

- src/core/
- src/api/
- src/lib/
- src/engine/
- src/server/
- core/
- api/
- lib/

配置文件:

- package.json
- requirements.txt
- go.mod
- Cargo.toml
- pom.xml
- build.gradle
- tsconfig.json
- webpack.config.\*
- vite.config.\*
```

**扣分计算**:

```python
total_deduct = 0

for file in changed_files:
    file_type = classify_file(file)  # 识别文件类型
    change_type = get_change_type(file)  # 新增/修改/删除

    deduct = WEIGHT_TABLE[file_type][change_type]
    total_deduct += deduct

# 上限50分
total_deduct = min(total_deduct, 50)
```

---

#### C. 覆盖率变化（最多-20 分）

新增代码未被文档覆盖会降低文档完整性

| 覆盖率变化             | 扣分   | 说明             |
| ---------------------- | ------ | ---------------- |
| 增加>20 个未文档化文件 | -20 分 | 大量新代码       |
| 增加 10-20 个          | -15 分 | 较多新代码       |
| 增加 5-10 个           | -10 分 | 中等新代码       |
| 增加<5 个              | -5 分  | 少量新代码       |
| 无变化或减少           | 0 分   | 覆盖率稳定或提升 |

**计算方法**:

```python
# 统计当前代码文件
current_files = count_code_files(src_dir)

# 从文档中提取记录的文件数
documented_files = extract_file_count_from_doc()

# 计算未覆盖文件数
uncovered = current_files - documented_files

if uncovered >= 20:
    score_deduct = 20
elif uncovered >= 10:
    score_deduct = 15
elif uncovered >= 5:
    score_deduct = 10
elif uncovered > 0:
    score_deduct = 5
else:
    score_deduct = 0
```

---

#### D. 摘要健康度检查（最多-5 分）⭐ (V3.0)

文档摘要的完整性和时效性影响自动化更新检测能力

| 摘要问题                 | 扣分  | 说明                 |
| ------------------------ | ----- | -------------------- |
| 所有文档缺少摘要         | -5 分 | 无法自动检测更新需求 |
| 部分文档缺少摘要         | -3 分 | 自动检测能力受限     |
| 摘要格式错误             | -2 分 | 工具无法解析         |
| verified_at 过期 > 90 天 | -2 分 | 摘要过时             |
| related_files 不准确     | -3 分 | 关联检测失效         |
| 所有文档摘要完整且准确   | 0 分  | 理想状态             |

**检查方法**:

```bash
# 使用摘要验证工具批量检查
python tools/py/summary_validator.py --batch-mode --dir dev_docs/
```

输出示例：

```json
{
  "total_documents": 15,
  "documents_with_summary": 12,
  "documents_without_summary": 3,
  "format_errors": 1,
  "expired_summaries": 5,
  "file_not_found_errors": 2,
  "overall_health": "中等"
}
```

**扣分计算**:

```python
total_deduct = 0

# 1. 缺少摘要
missing_rate = missing_count / total_docs
if missing_rate >= 0.8:  # 80%+文档缺少摘要
    total_deduct += 5
elif missing_rate >= 0.3:  # 30%+文档缺少摘要
    total_deduct += 3

# 2. 格式错误
if format_error_count > 0:
    total_deduct += 2

# 3. 过期摘要
expired_rate = expired_count / docs_with_summary
if expired_rate >= 0.5:  # 50%+摘要过期
    total_deduct += 2

# 4. related_files 不准确
if file_not_found_errors >= 3:
    total_deduct += 3

# 上限5分
total_deduct = min(total_deduct, 5)
```

**为什么重要**:

- ✅ **自动化检测**: 准确的摘要支持自动检测需要更新的文档
- ✅ **节省时间**: 无需人工逐个分析文档
- ✅ **时效性追踪**: `verified_at` 字段监控文档健康度

**注意事项**:

- 如果文档是 V3.0 之前生成的，缺少摘要是正常的，不应扣分
- 可以通过检查文档生成日期来判断是否应该有摘要
- 建议在更新文档时同步添加摘要

---

### 健康度等级划分

| 分数范围  | 等级    | 评价             | 建议操作                   |
| --------- | ------- | ---------------- | -------------------------- |
| 90-100 分 | 🟢 优秀 | 文档非常新鲜准确 | 无需更新，继续使用         |
| 70-89 分  | 🟡 良好 | 文档基本准确     | 建议选择性更新高影响区域   |
| 50-69 分  | 🟠 一般 | 文档部分过时     | 建议执行增量更新           |
| 30-49 分  | 🔴 较差 | 文档明显过时     | 强烈建议全量更新或重新生成 |
| <30 分    | ⛔ 极差 | 文档严重过时     | 必须重新生成文档           |

---

### 综合评分示例

**场景**: 项目文档生成于 3 个月前

**计算过程**:

```
初始分数: 100分

A. 时间衰减:
- 文档年龄: 3个月
- 扣分: -10分

B. 代码变更:
- 修改 src/core/api.ts (核心模块): -15分
- 新增 src/features/auth/login.ts (业务模块): -5分
- 新增 src/features/auth/register.ts (业务模块): -5分
- 新增 src/features/auth/index.ts (业务模块): -5分
- 修改 package.json (配置文件): -10分
- 修改 src/utils/helper.ts (工具类): -5分
- 小计: -45分

C. 覆盖率变化:
- 当前文件: 156个
- 文档记录: 148个
- 未覆盖: 8个
- 扣分: -10分

总分: 100 - 10 - 45 - 10 = 35分
等级: 🔴 较差
建议: 强烈建议全量更新或重新生成
```

---

### 特殊情况处理

#### 情况 1: 无 Git 历史的项目

**问题**: 无法使用 Git diff 分析变更

**降级评分方案**:

1. 仅使用"时间衰减因子"（最多-30 分）
2. 使用"文件修改时间对比"估算变更影响

```bash
# 查找比文档新的文件
find src -type f -newer dev_docs/AI_Coding_Context.md

# 根据数量估算扣分
modified_count = count(newer_files)

if modified_count > 50:
    score_deduct = 40
elif modified_count > 20:
    score_deduct = 30
elif modified_count > 10:
    score_deduct = 20
else:
    score_deduct = modified_count * 2
```

3. 总分 = 100 - 时间衰减 - 修改时间估算扣分

---

#### 情况 2: 文档元数据缺失

**问题**: 无法确定文档生成时间

**处理方式**:

1. 尝试从文档内容推断生成时间

   ```markdown
   # 查找文档中的日期信息

   grep -E "生成日期|Generated|Created" dev_docs/AI_Coding_Context.md
   ```

2. 查看 dev_docs/目录创建时间

   ```bash
   stat dev_docs/ | grep "Birth\|Created"
   ```

3. 如果完全无法确定，询问用户

   ```markdown
   ⚠️ 无法确定文档生成时间

   请问您是否记得大约何时生成的文档？
   A. 最近 1 个月内
   B. 1-3 个月前
   C. 3-6 个月前
   D. 6 个月以上
   E. 不记得了
   ```

---

#### 情况 3: 代码文件比文档更旧 ⭐

**场景**: 用户打开历史项目，代码自文档生成后未修改

**识别方法**:

```bash
# 获取文档修改时间
doc_mtime=$(stat -c %Y dev_docs/AI_Coding_Context.md 2>/dev/null)

# 获取代码文件的最新修改时间
latest_code_mtime=$(find src -type f -exec stat -c %Y {} \; | sort -rn | head -1)

# 对比
if [ $latest_code_mtime -lt $doc_mtime ]; then
    echo "代码比文档旧，文档仍然有效"
fi
```

**输出**:

```markdown
✅ 检测到代码文件均早于文档生成时间

- 文档生成: 2025-09-15 14:30:00
- 最新代码修改: 2025-08-20 10:15:00
- 结论: 代码自文档生成后未修改

健康度: 100 分（优秀）
建议: 文档仍然准确，无需更新
```

**重要性**: 这避免了对历史项目的误判

---

## 🔄 降级策略详解

当理想的检查方法不可用时，自动降级到次优方案

### 优先级 1: Git diff 分析 ⭐⭐⭐⭐⭐

**适用**: Git 仓库且有提交历史

**检测 Git 可用性**:

```bash
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Git可用"
    use_git=true
else
    echo "Git不可用，降级到方案2"
    use_git=false
fi
```

**Git 分析方法**:

```bash
# 1. 获取文档生成时间
doc_date="2025-09-15"

# 2. 获取该日期以来的所有变更
git log --since="$doc_date" --name-status --oneline

# 3. 统计变更
git diff HEAD@{$(date -d "$doc_date" +%s)}..HEAD --stat

# 4. 识别关键变更（feat/refactor/breaking）
git log --since="$doc_date" --grep="feat|refactor|breaking" --oneline

# 5. 按文件类型分类变更
git log --since="$doc_date" --name-status --oneline | \
  awk '{print $NF}' | \
  sort | uniq -c
```

**优点**:

- ✅ 最准确
- ✅ 可追溯每个变更
- ✅ 可识别变更类型

---

### 优先级 2: 文件修改时间对比 ⭐⭐⭐⭐

**适用**: Git 不可用时

**关键改进**: 双向时间对比

**为什么需要双向对比**:

- 单向对比（只看文档年龄）会误判历史项目
- 双向对比（文档 vs 代码时间）能识别代码未变的情况

**实现方法**:

```bash
# 1. 获取文档修改时间
doc_mtime=$(stat -c %Y dev_docs/AI_Coding_Context.md 2>/dev/null)  # Linux
doc_mtime=$(stat -f %m dev_docs/AI_Coding_Context.md 2>/dev/null)  # Mac
doc_mtime=$(Get-Item dev_docs/AI_Coding_Context.md).LastWriteTime.ToFileTime()  # Windows

# 2. 获取代码文件的最新修改时间
latest_code_mtime=$(find src -type f -exec stat -c %Y {} \; 2>/dev/null | sort -rn | head -1)

# 3. 双向对比
if [ $latest_code_mtime -lt $doc_mtime ]; then
    echo "✅ 代码比文档旧，文档仍然有效"
    health_score=100

elif [ $latest_code_mtime -gt $doc_mtime ]; then
    echo "⚠️ 有代码在文档生成后被修改"

    # 统计修改过的文件数
    newer_files=$(find src -type f -newer dev_docs/AI_Coding_Context.md 2>/dev/null)
    newer_count=$(echo "$newer_files" | wc -l)

    echo "修改的文件数: $newer_count"

    # 根据数量估算影响
    if [ $newer_count -gt 50 ]; then
        echo "影响评估: 高（建议重新生成）"
        health_score=30
    elif [ $newer_count -gt 20 ]; then
        echo "影响评估: 中高（建议全量更新）"
        health_score=45
    elif [ $newer_count -gt 10 ]; then
        echo "影响评估: 中（建议增量更新）"
        health_score=60
    else
        echo "影响评估: 低（建议选择性更新）"
        health_score=75
    fi

    # 尝试识别核心文件
    core_files=$(echo "$newer_files" | grep -E "src/(core|api|lib)/|index\.|main\.")
    core_count=$(echo "$core_files" | grep -v "^$" | wc -l)

    if [ $core_count -gt 0 ]; then
        echo "⚠️ 包含 $core_count 个核心文件变更"
        health_score=$((health_score - 10))
    fi
else
    echo "ℹ️ 文档和代码修改时间相同"
    health_score=90
fi
```

**输出示例**:

```markdown
📊 基于文件修改时间的评估结果

🕐 时间对比:

- 文档最后修改: 2025-09-15 10:30:00
- 代码最新修改: 2025-11-01 15:45:00
- 时间差: 47 天

📝 变更统计:

- 文档生成后修改的文件: 23 个
- 其中核心文件: 5 个（基于目录和文件名分析）

💡 影响评估: 中高

- 健康度估算: 45 分（较差）
- 建议操作: 全量更新或重新生成

⚠️ 注意: 此评估基于文件修改时间，准确度有限
建议: 如项目使用 Git，建议初始化 Git 仓库以获得更精确的分析
```

**优点**:

- ✅ 无需 Git
- ✅ 能识别历史项目（代码未变）
- ✅ 快速执行

**缺点**:

- ⚠️ 无法识别变更类型
- ⚠️ 无法追溯变更历史
- ⚠️ 准确度中等

---

### 优先级 3: 用户提供信息 ⭐⭐⭐

**适用**: 文件修改时间也不可用或不可靠时

**询问模板**:

```markdown
⚠️ 无法自动评估文档健康度

原因: Git 不可用且文件修改时间不可靠

💬 请您协助回答以下问题（可选）:

**问题 1**: 距离上次文档生成，项目代码是否有变化？
A. 没有变化
B. 有轻微变化（几个文件）
C. 有中等变化（10-20 个文件）
D. 有较大变化（>20 个文件或架构调整）
E. 不确定

**问题 2**: 如果有变化，主要是哪些方面？（可多选）
[ ] 新增了功能模块
[ ] 重构了现有代码
[ ] 修改了 API 设计
[ ] 更新了技术栈/框架
[ ] 修复了一些 bug
[ ] 调整了配置文件
[ ] 其他: \***\*\_\_\_\*\***

**问题 3**: 您希望如何处理？
A. 让我执行基础评估（仅基于文件统计）
B. 直接执行增量更新
C. 重新生成文档
D. 保持现有文档

请回复问题编号和选项，例如:
1-C, 2-新增了功能模块+修改了 API 设计, 3-B
```

**基于回答的处理**:

```markdown
# 用户回答示例: 1-C, 2-新增了功能模块, 3-B

✅ 收到，根据您的反馈:

- 代码变化程度: 中等（10-20 个文件）
- 主要变更: 新增功能模块
- 期望操作: 执行增量更新

💡 建议更新范围:

1. architecture_overview.md
   - 补充新增模块的架构说明
2. 创建新模块的专项文档
   - 例如: new_feature.md
3. 更新主文档中的模块索引
   - AI_Coding_Context.md 中添加新模块引用

📊 预估:

- 工作量: 2-3 小时
- Token 消耗: 原生成量的 30%左右

是否开始执行增量更新? (是/否)
```

**优点**:

- ✅ 最灵活
- ✅ 用户可提供准确信息

**缺点**:

- ⚠️ 需要用户参与
- ⚠️ 依赖用户记忆

---

### 优先级 4: 仅基于时间判断 ⭐⭐

**适用**: 所有其他方法都不可用时的最后手段

**简化判断**:

```markdown
📊 基于文档年龄的评估

- 文档生成日期: 2025-09-15
- 距今: 74 天（约 2.5 个月）

💡 基于经验规则:

- <1 个月: 通常仍然准确，无需更新
- 1-3 个月: 可能有中等变化，建议检查
- 3-6 个月: 建议执行健康度检查或更新
- > 6 个月: 强烈建议更新

当前评估: 可能有中等变化
建议: 执行健康度检查或增量更新

⚠️ 此评估非常粗略，建议:

1. 手动检查代码变更
2. 如不确定，建议重新生成文档
3. 考虑为项目初始化 Git 仓库
```

**优点**:

- ✅ 总能给出建议

**缺点**:

- ⚠️ 准确度最低
- ⚠️ 仅供参考

---

## 🤖 AI 标准工作流

当检测到现有文档时，AI 应按以下流程执行：

### 第 1 步: 自动快速扫描（无需询问用户）

**执行内容**:

```bash
# 1. 检测文档元数据
读取 dev_docs/AI_Coding_Context.md 开头的元数据或注释
提取: 生成日期、覆盖文件列表

# 2. 统计当前代码文件
count_current = find src -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) | wc -l

# 3. 对比统计
count_documented = 从文档中提取的文件数
diff = count_current - count_documented
diff_percent = (diff / count_documented) * 100

# 4. 计算时间差异
days_old = (today - doc_date) / 1天
months_old = days_old / 30
```

**输出快速评估卡片**:

```markdown
📊 文档快速扫描结果

- 文档生成日期: 2025-09-15（74 天前）
- 文档记录文件: 148 个
- 当前代码文件: 156 个
- 差异: +8 个文件（+5.4%）

💡 初步评估: 文档可能部分过时

📋 可用选项:
A. 执行标准健康度检查（推荐，3-5 分钟）

- 详细评估文档状态
- 精确识别需要更新的部分
- 给出具体更新方案

B. 执行深度分析（全面，10-15 分钟）

- 完整的变更分析
- 架构级影响评估
- 逐文件对比

C. 直接执行增量更新

- 如果您已知道需要更新哪些部分
- 跳过评估，直接开始更新

D. 重新生成文档

- 如果项目有重大变更
- 完全重建文档体系

E. 保持现有文档

- 如果确认文档仍然准确
- 不做任何更新

请选择: A / B / C / D / E
```

---

### 第 2 步: 根据用户选择执行

#### 用户选 A: 执行标准检查

```markdown
✅ 开始执行标准健康度检查...

[执行 Git 分析或文件时间对比]
[采样检查核心文件]
[计算健康度评分]

📄 健康度报告已生成

## 📊 整体评估

- 健康度: 65 分（一般）
- 评级: 🟠 建议增量更新

[详细报告内容见上文标准检查输出示例]

💡 下一步建议:

1. 执行增量更新（推荐）
2. 执行深度分析（如需更详细评估）
3. 重新生成文档（如项目变化太大）

请选择下一步操作: 1 / 2 / 3
```

#### 用户选 B: 执行深度分析

```markdown
✅ 开始执行深度分析...

这将需要 10-15 分钟，请稍候...

[执行完整 Git diff 分析]
[逐文件对比]
[架构变更检测]

📄 详细分析报告已生成

[详细报告内容见上文深度分析输出示例]

💡 下一步建议:
[根据分析结果给出具体建议]
```

#### 用户选 C: 直接增量更新

```markdown
✅ 开始执行增量更新...

请告知需要更新的内容:

选项 1: 我来告诉你具体变更内容

- 请描述主要变更（例如: 新增了认证模块，重构了 API 层）

选项 2: 让 AI 自动检测变更并更新

- AI 将执行标准检查，识别变更，然后自动更新

请选择: 1 / 2
```

#### 用户选 D: 重新生成文档

```markdown
✅ 将重新生成文档

⚠️ 提醒: 这将消耗较多 token（预计~5000 tokens）

确认重新生成? (是/否)

如确认，将进入首次生成流程...
```

#### 用户选 E: 保持现有文档

```markdown
✅ 已确认保持现有文档

文档路径: dev_docs/

💡 建议:

- 定期检查文档健康度（建议每 1-3 个月）
- 重大变更后及时更新文档
- 可使用增量更新减少 token 消耗

如需帮助，随时告知！
```

---

## 📋 健康度报告模板

### 简化版（模式 1 输出）

```markdown
📊 文档快速扫描结果

- 文档生成日期: YYYY-MM-DD（XX 天前）
- 文档记录文件: XXX 个
- 当前代码文件: XXX 个
- 差异: ±XX 个文件（±X.X%）

💡 初步评估: [状态描述]
```

---

### 标准版（模式 2 输出）

```markdown
📄 文档健康度报告

## 📊 整体评估

- 健康度: XX 分（[等级]）
- 评级: [emoji] [建议]

## 📈 变更统计

- 文档最后更新: YYYY-MM-DD
- 距今: XX 天
- 新增文件: XX 个
- 修改文件: XX 个（其中核心文件 XX 个）
- 删除文件: XX 个

## 🎯 风险评估

### 🔴 高风险区域

[列出高影响变更]

### 🟡 中风险区域

[列出中等影响变更]

### 🟢 低风险区域

[列出低影响变更]

## 💡 更新建议

- 推荐方案: [增量更新/全量更新/重新生成]
- 预计工作量: XX 小时
- 预计 token 消耗: 原生成量的 XX%

## 📋 建议更新清单

1. [文档名] - [原因]
2. [文档名] - [原因]
   ...
```

---

### 详细版（模式 3 输出）

```markdown
📄 文档深度分析报告

[包含标准版所有内容]

## 📋 详细更新清单

### 必须更新（P0）

1. [文档名]
   - 原因: [详细说明]
   - 影响: [高/中/低]
   - 相关文件: [列表]
   - 预计工作量: XX 小时
   - 预计 token: ~XXX tokens

### 建议更新（P1）

[同上格式]

### 可选更新（P2）

[同上格式]

## 🏗️ 架构变更检测

[如有架构变更，详细说明]

## 📦 依赖项变化

[如有依赖变化，列出]

## 🔧 技术栈升级

[如有技术栈变化，说明]

## 📊 详细评分明细

- 时间衰减: -XX 分
- 代码变更影响: -XX 分
  - 核心文件: -XX 分
  - 业务文件: -XX 分
  - 配置文件: -XX 分
  - 其他: -XX 分
- 覆盖率变化: -XX 分

总分: XX 分
```

---

## ❓ 常见问题

### Q1: 如何选择检查模式？

**A**: 根据情况选择：

- **快速扫描**: 只想快速了解状态
- **标准检查**: 常规评估（推荐）
- **深度分析**: 长期未更新或重大变更后

### Q2: 健康度评分是否绝对准确？

**A**: 不是。评分是基于量化规则的估算，实际情况可能有偏差。建议：

- 90-100 分: 可信度高
- 70-89 分: 可信度较高
- 50-69 分: 仅供参考
- <50 分: 建议人工确认

### Q3: Git 不可用时准确度如何？

**A**: 降级到文件时间对比，准确度约 70-80%。建议：

- 为项目初始化 Git 仓库
- 或使用深度分析模式
- 或结合用户提供信息

### Q4: 文档元数据从哪里读取？

**A**: 优先级：

1. 文档开头的 YAML frontmatter
2. 文档开头的注释（`<!-- Generated: YYYY-MM-DD -->`）
3. 文档内容中的"生成日期"等关键词
4. dev_docs/目录创建时间
5. 询问用户

### Q5: 如何处理 Monorepo 项目？

**A**:

- 如果是全局文档：正常检查
- 如果是独立文档：分别检查各子项目
- 参见: [Monorepo 工作流](./monorepo_workflow.md)

### Q6: 检查会修改任何文件吗？

**A**: 不会。健康度检查是只读操作，不会修改任何文件。

### Q7: 可以自动定期检查吗？

**A**: 目前需要手动触发。未来可考虑：

- Git hooks 集成
- CI/CD 集成
- 定时任务

---

## 🔗 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md#场景4-文档健康度检查) - 智能工作流分流
- [incremental_update_workflow.md](./incremental_update_workflow.md) - 增量更新流程
- [core/update_triggers.md](../core/update_triggers.md) - 文档更新触发机制

---

**版本**: v2.3  
**路径**: `workflows/document_health_check.md`
