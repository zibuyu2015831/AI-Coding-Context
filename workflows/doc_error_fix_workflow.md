---
title: 文档谬误修复工作流
summary: 定义当用户报告文档谬误时，AI 如何验证问题真实性、定位关联文档、选择修复策略并记录修复过程，以降低文档错误扩散风险。
keywords: doc-error-fix | workflow | documentation | validation | repair | aicc
scope: 用户报告文档错误后的标准化处理流程
related_files: tools/py/doc_dependency_tracer.py | tools/js/doc_dependency_tracer.js | tools/py/doc_health_checker.py | tools/js/doc_health_checker.js
dependencies: workflows/document_health_check.md | workflows/commit_guided_update.md | core/SUMMARY_FORMAT_SPEC.md
verified_at: 2026-05-05
---

# 文档谬误修复工作流

> **版本**: v3.0
> **创建日期**: 2026-04-13
> **用途**: 指导 AI 如何处理用户报告的文档谬误，使用 011 优化点开发的工具链

---

## 📋 概述

本文档详细说明当用户报告文档谬误时，AI 应该遵循的标准工作流程。该流程集成了 011 优化点开发的工具链，包括：

- 自动关联文档检测
- 分级修复策略
- Git 集成的修复管理
- 修复历史记录和回滚

### 适用场景

- 用户发现文档中的错误并报告
- 用户不确定是否真的是文档错误，需要验证
- 文档内容与代码实现不一致
- 术语定义不统一
- 示例代码错误

### 特殊场景：不确定的谬误验证

**场景描述**：用户感觉某个文档可能有问题，但不确定是不是真的错误。

**处理流程**：
1. AI 帮助用户验证可能存在的问题
2. 使用对比分析工具检查文档与代码
3. 提供验证结果和建议
4. 用户确认后再决定是否执行修复

**标准回复模板**（用于不确定场景）：
```markdown
✅ 我理解您对文档有疑问。让我帮您验证一下。

## 🔍 正在验证

[执行验证步骤...]

## 📋 验证结果

### 文档内容
[摘录相关文档内容]

### 代码依据（如有）
[摘录相关代码内容]

### 分析结论
A. ✅ 确认这是文档谬误 - 建议修复
B. ⚠️ 部分不一致 - 需要确认
C. ✅ 文档是正确的 - 建议保留原样

请选择下一步操作：
1. 确认是谬误，执行修复
2. 进一步讨论，澄清理解
3. 确认文档正确，无需修复
```


---

## 🤖 AI 标准工作流

### 第 1 步: 接收和理解用户报告

**核心要求**: 确认用户报告的谬误内容和上下文

```markdown
# 标准回复模板

✅ 我理解您发现了文档谬误。为了更好地帮您修复，请提供以下信息（如适用）：

**文档路径**: {{用户提到的文档路径}}
**错误位置**: {{章节/行数/代码块}}
**错误内容**: {{错误的内容}}
**正确内容**: {{预期的正确内容}}（可选）
**代码依据**: {{关联的代码文件/行数}}（可选）
**严重程度**: {{P0/P1/P2/P3}}（可选，默认 P1）

---

## 📝 我发现的谬误：

[用户提供的详细信息]
```

### 第 2 步: 验证谬误的真实性

**任务**: 确认用户报告的错误确实存在

```bash
# 执行步骤：

# 1. 检查文档是否存在
python tools/py/env_diagnosis.py
python tools/py/file_reader.py --file "{{文档路径}}" --limit 20  # 读取相关部分

# 2. 验证错误内容
# 直接对比用户描述与文档内容

# 3. 检查代码依据（如果提供）
python tools/py/file_reader.py --file "{{代码文件}}" --offset {{行数}} --limit 10
```

**输出示例**:
```markdown
✅ 已验证谬误的真实性：

**文档**: dev_docs/api_layer.md
**位置**: "API 调用"章节，第 45 行
**错误**: 使用了 `getUserInfo()`
**代码依据**: src/api/user.ts:L23 显示实际函数为 `fetchUserProfile()`
**严重程度**: P0 (API 函数名错误)
```

### 第 3 步: 分析影响范围（关联文档检测）

**核心工具**: `doc_dependency_tracer.py` / `doc_dependency_tracer.js`

```bash
# 使用文档依赖追踪器检测关联文档

python tools/py/doc_dependency_tracer.py --doc "{{文档路径}}" --strategy all
```

**输出示例**:
```json
{
  "data": {
    "targetDoc": "dev_docs/api_layer.md",
    "strategy": "all",
    "relatedDocs": {
      "direct": [
        {
          "file": "dev_docs/state_management.md",
          "type": "direct",
          "reason": "dependencies 字段中引用"
        }
      ],
      "reverse": [
        {
          "file": "dev_docs/user_profile.md",
          "type": "reverse",
          "reason": "被该文档的 dependencies 字段引用"
        }
      ],
      "semantic": [
        {
          "file": "dev_docs/authentication.md",
          "type": "semantic",
          "reason": "关键词重叠度: 2 (用户, 认证)"
        }
      ]
    },
    "totalRelated": 3,
    "totalDocsScanned": 15
  }
}
```

### 第 4 步: 生成修复方案

**任务**: 生成详细的修复方案，包括：
- 需要修改的文档列表
- 具体修改位置
- 修改内容
- 风险评估

```markdown
# 修复方案模板

## 📋 修复方案

### 🔍 影响分析

- 发现关联文档: {{totalRelated}} 个
  - {{direct.length}} 个直接关联
  - {{reverse.length}} 个反向关联
  - {{semantic.length}} 个语义关联

### 🎯 修复清单

{{#each relatedDocs}}
- [ ] {{file}}: {{reason}}
{{/each}}

### 🛠️ 修复内容

**目标文档修改**:
```diff
--- a/{{文档路径}}
+++ b/{{文档路径}}
@@ -{{行号-3}},{{行号+3}} +{{行号-3}},{{行号+3}} @@
 {{上下文内容}}
-{{错误内容}}
+{{正确内容}}
 {{上下文内容}}
```

### ⚠️ 风险评估

- 严重程度: {{严重程度}}
- 影响范围: {{totalRelated}} 个文档
- 修复复杂度: {{复杂度}}
- 回滚难度: 低（基于 Git）
```

### 第 5 步: 用户审核修复方案

**核心要求**: 获得用户对修复方案的批准

```markdown
# 审核模板

✅ 修复方案已生成，请审核：

{{修复方案内容}}

---

## 📋 修复选项

A. 执行完整修复（包括所有关联文档）
B. 只修复目标文档（忽略关联文档）
C. 调整修复方案（修改范围/内容）
D. 取消修复

请选择: A / B / C / D
```

### 第 6 步: 执行修复（Git 集成）

**核心工具**: `manage_fix_with_git.py` / `manage_fix_with_git.js`

```bash
# 1. 检查 Git 状态
python tools/py/manage_fix_with_git.py --check-status

# 2. 创建修复分支（如果需要）
python tools/py/manage_fix_with_git.py --start --branch-name "doc-fix-{{错误描述}}"

# 3. 执行修复操作
python tools/py/batch_fix_manager.py --generate --pattern "{{错误内容}}" --replacement "{{正确内容}}"
python tools/py/batch_fix_manager.py --execute --plan "dev_docs/_analysis/doc_fix_plan_{{timestamp}}.md"

# 4. 记录修复历史
python tools/py/fix_history_manager.py --record --commit "$(git rev-parse HEAD)" --target-docs "{{所有受影响的文档}}"

# 5. 提交修复
python tools/py/manage_fix_with_git.py --commit --message "fix: {{错误描述}}"
```

### 第 7 步: 验证修复结果

**任务**: 确认修复是否成功

```bash
# 检查修复后的文档
python tools/py/file_reader.py --file "{{文档路径}}" --offset {{行号-3}} --limit 10

# 验证关联文档也已修复
for doc in {{关联文档列表}}; do
  python tools/py/file_reader.py --file "$doc" | grep -q "{{正确内容}}" && echo "✅ $doc 已修复" || echo "❌ $doc 修复失败"
done

# 验证修复历史记录
python tools/py/fix_history_manager.py --query --commit "$(git rev-parse HEAD)"
```

### 第 8 步: 完成和总结

**标准回复**:
```markdown
✅ 修复完成！

## 📋 修复详情

- **提交**: {{commit_hash}}
- **分支**: {{branch_name}}
- **修复的文档**: {{修复的文档列表}}
- **修复内容**: {{错误内容}} → {{正确内容}}

## 📊 修复统计

- 目标文档: {{targetDoc}}
- 关联文档: {{totalRelated}} 个
- 总修改: {{修改次数}} 处

## 🔄 回滚选项

如需回滚修复，请执行：
```bash
python tools/py/manage_fix_with_git.py --rollback --commit-hash {{commit_hash}}
```

---

💡 文档健康度已更新。该修复将在下次文档健康检查中记录。
```

---

## 🔍 分级修复策略

根据严重程度自动选择修复策略：

### P0 - 严重错误（强制关联检测）

**场景**: API 函数名错误、代码示例错误、配置错误

**策略**:
- 自动检测所有关联文档
- 强制创建修复分支
- 执行完整修复
- 记录详细修复历史

```bash
python tools/py/doc_dependency_tracer.py --doc "{{文档路径}}" --strategy all
python tools/py/manage_fix_with_git.py --start --branch-name "doc-fix-p0-{{错误描述}}"
python tools/py/batch_fix_manager.py --execute --plan "{{plan_path}}"
```

### P1 - 重要错误（建议关联检测）

**场景**: 概念解释错误、流程描述错误、术语不一致

**策略**:
- 建议检测关联文档
- 可选择是否创建修复分支
- 支持快速修复模式

```bash
python tools/py/doc_dependency_tracer.py --doc "{{文档路径}}" --strategy dependencies  # 只检测直接关联
python tools/py/batch_fix_manager.py --execute --plan "{{plan_path}}" --auto  # 自动批准低风险部分
```

### P2/P3 - 轻微错误（简化流程）

**场景**: 格式问题、拼写错误、标点符号

**策略**:
- 忽略关联检测（除非明确要求）
- 直接在当前分支修改
- 简化修复流程

```bash
python tools/py/file_reader.py --file "{{文档路径}}" --limit 20
# 直接修改文档内容
python tools/py/manage_fix_with_git.py --commit --message "fix: {{错误描述}}"
```

---

## 📈 性能优化建议

### 1. 快速模式（跳过关联检测）

```bash
# 使用 --auto 选项跳过关联检测（仅 P2/P3）
python tools/py/batch_fix_manager.py --generate --pattern "{{错误内容}}" --replacement "{{正确内容}}" --strategy quick
python tools/py/batch_fix_manager.py --execute --plan "{{plan_path}}" --auto
```

### 2. 增量修复（只修复变更部分）

```bash
# 使用 --incremental 选项
python tools/py/batch_fix_manager.py --execute --plan "{{plan_path}}" --incremental
```

### 3. 并发执行（大规模修复）

```bash
# 使用 --parallel 选项（最多 5 个文档并发）
python tools/py/batch_fix_manager.py --execute --plan "{{plan_path}}" --parallel 5
```

---

## 🚫 错误处理和回滚

### 修复过程中出错

```bash
# 1. 检查错误
python tools/py/env_diagnosis.py
git status

# 2. 回滚到修复前状态
python tools/py/manage_fix_with_git.py --rollback --commit-hash {{original_commit}}

# 3. 删除临时分支
git branch -D {{branch_name}}
```

### 修复后发现问题

```bash
# 1. 回滚到修复前
python tools/py/manage_fix_with_git.py --rollback --commit-hash {{fix_commit}}

# 2. 或创建回滚分支
python tools/py/manage_fix_with_git.py --start --branch-name "rollback-{{fix_commit}}"
python tools/py/manage_fix_with_git.py --rollback --commit-hash {{original_commit}}
python tools/py/manage_fix_with_git.py --commit --message "revert: 回滚 {{错误描述}} 的修复"
```

---

## 🔗 系统集成

### 与其他优化点的关联

#### 006 - 自动审查报告

```bash
# 自动检测并报告文档谬误
python tools/py/complexity_scanner.py --path . --since "1 day ago"
python tools/py/commit_quality_scorer.py --since "{{文档生成日期}}"
```

#### 018 - Commit-Guided 更新

```bash
# 将修复与 commit 关联
python tools/py/commit_parser.py --parse "{{修复内容}}"
python tools/py/commit_template_cli.py --message "fix: {{错误描述}}"
```

---

## 📊 修复质量指标

### 核心指标

| 指标 | 目标值 | 计算公式 |
|------|--------|----------|
| 修复成功率 | 98% | 成功修复次数 / 总修复次数 |
| 关联文档检测率 | 95% | 正确检测的关联文档数 / 实际关联文档数 |
| 修复时间 | <15 分钟 | 平均修复时间 |
| 回滚率 | <2% | 回滚次数 / 总修复次数 |

### 报告格式

```markdown
# 文档谬误修复报告 - {{日期}}

## 📈 修复统计

- 总修复次数: {{总次数}}
- 成功修复: {{成功次数}} ({{成功率}}%)
- 关联文档检测: {{检测次数}} ({{检测率}}%)
- 平均修复时间: {{平均时间}} 分钟

## 🏷️ 严重程度分布

- P0: {{P0数量}} 个 ({{P0占比}}%)
- P1: {{P1数量}} 个 ({{P1占比}}%)
- P2: {{P2数量}} 个 ({{P2占比}}%)
- P3: {{P3数量}} 个 ({{P3占比}}%)

## 🔍 常见错误类型

1. **API 函数名错误**: {{次数}} 次
2. **代码示例错误**: {{次数}} 次
3. **术语不一致**: {{次数}} 次
4. **格式问题**: {{次数}} 次

## 💡 改进建议

- {{高风险区域}}
- {{常见错误模式}}
- {{优化建议}}
```

---

## 🧪 测试和验证

### 单元测试

```bash
# 现有工具测试（截至 2026-04-26 实测覆盖范围）
python -m pytest tools/py/tests/ -v
```

> ⚠️ **测试覆盖现状**：`tools/py/tests/` 当前仅覆盖 commit_integrity / git_safety；
> doc_error_fix 工具链（detection / fix_executor / dependency_tracer）的单元测试与集成测试**尚未补全**。
> 后续补全任务建议入 `dev/V3.0/PROGRESS.md` 011 后续清单：
>
> - `tools/py/tests/test_doc_error_detection.py`
> - `tools/py/tests/test_doc_fix_executor.py`
> - `tools/py/tests/integration/test_doc_fix_e2e.py`
>
> 补全后命令恢复为 `python -m pytest tools/py/tests/ -v -k "doc_error or doc_fix"`

### 模拟测试场景

```bash
# 模拟用户报告和修复过程
python tools/py/doc_dependency_tracer.py --doc "dev_docs/api_layer.md" --strategy all
python tools/py/batch_fix_manager.py --generate --pattern "getUserInfo" --replacement "fetchUserProfile"
python tools/py/batch_fix_manager.py --preview --plan "dev_docs/_analysis/doc_fix_plan_{{timestamp}}.md"
```

---

## 📚 相关文档

- [工具清单](../tools/README.md)
- 设计源（仅 dev 分支可见）：`dev/V3.0/confirmed/011-doc-error-fix-workflow/` —— 含 011 设计方案、实施方案、使用指南

---

**版本**: v3.0
**最后更新**: 2026-04-13
**适用工具版本**: tools/py v1.4.6+
