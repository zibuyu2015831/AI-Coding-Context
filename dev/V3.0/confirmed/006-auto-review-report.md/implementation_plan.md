# 006-自动化审查报告实施方案与进度表（整合到005）

本文档旨在落实 V3.0 P1 阶段优化点"006-自动化审查报告"。本优化点将整合到 005-复杂度实时仪表盘 中，通过扩展现有工具链实现功能。

## 核心思路

通过扩展 005 的现有工具链，实现代码审查功能，避免重复开发：
- 复用 005 的数据采集、报告生成、Git Hooks 和通知系统
- 新增轻量级代码审查分析能力
- 在现有复杂度报告中整合审查内容

---

## Proposed Changes

### Phase 1: 扩展数据采集（复用 005 工具）

**目标**：在 `complexity_scanner` 中新增代码审查数据采集功能。

#### [MODIFY] `tools/py/complexity_scanner.py` (Python 版本)
**扩展功能**：
1. **变更分析增强**：
   - 统计新增/删除代码行数
   - 识别核心文件变更
   - 检测 API 变更

2. **轻量级代码质量检查**（新增）：
   - TODO/FIXME 标记增减统计
   - 危险函数检测（eval(), exec() 等）
   - 大文件变更检测（>500行）
   - 敏感信息检测（API Key、密码等）

3. **影响范围分析**：
   - 识别受影响的功能模块
   - 分析变更的传播风险

#### [MODIFY] `tools/js/complexity_scanner.js` (Node.js 版本)
功能与 Python 版本保持一致。

#### [MODIFY] `dev_docs/complexity/config.yaml`
**新增配置项**：
```yaml
# 代码审查配置
review:
  # 危险函数列表
  dangerous_functions:
    - eval
    - exec
    - Function

  # 大文件阈值
  large_file_threshold: 500

  # TODO 警告阈值
  todo_warning_threshold: 3
  todo_critical_threshold: 5
```

---

### Phase 2: 扩展报告生成系统

**目标**：在 `report_generator` 中新增审查报告生成功能。

#### [MODIFY] `tools/py/report_generator.py`
**扩展功能**：
1. **审查报告章节**（新增）：
   - 📝 变更概述（文件数、代码增减）
   - 🚨 紧急问题（立即修复）
   - 🟡 重要问题（尽快处理）
   - 📚 需要更新的文档
   - 🎯 影响分析

2. **统一报告格式**：
   - 将复杂度报告和审查报告整合为统一的"质量报告"
   - 支持分别生成复杂度报告或审查报告
   - 支持生成完整的综合报告

3. **行动建议增强**：
   - 为每个问题提供具体的修复建议
   - 链接相关文档和参考
   - 提供修复优先级

#### [MODIFY] `tools/js/report_generator.js`
功能与 Python 版本保持一致。

#### [MODIFY] `dev_docs/complexity/template.html`
**新增审查报告可视化区域**：
- 变更统计图表
- 问题严重度矩阵
- 行动建议列表

---

### Phase 3: 更新 Git Hooks 集成

**目标**：在 Git Hooks 中添加审查检查功能。

#### [MODIFY] `tools/git-hooks/pre-commit`
**新增审查检查**：
```python
def check_code_review():
    """检查代码变更质量"""
    issues = analyze_changes()

    if issues["critical"]:
        print_critical_issues(issues["critical"])
        return False, "发现严重问题，阻止提交"

    if issues["warning"]:
        print_warnings(issues["warning"])
        # 不阻止，但给出警告

    return True, "审查通过"
```

#### [MODIFY] `tools/git-hooks/post-commit`
**新增审查报告生成**：
```python
def generate_review_report():
    """生成代码审查报告"""
    data = load_scan_data()
    report = generate_quality_report(data, include_review=True)
    save_report(report)
```

---

### Phase 4: 高级功能（可选）

**目标**：增强审查能力，提供更深度的分析。

#### [NEW] `tools/py/review_analyzer.py` (可选)
**功能**：
1. **LLM 辅助分析**：
   - 使用 AI 分析变更影响范围
   - 识别需要更新的文档
   - 检测架构违规

2. **ADR 集成**：
   - 与 004-ADR 系统集成
   - 自动检测架构决策违反情况

---

## 验证计划

详见同目录下的 `walkthrough.md`。

---

## 依赖关系

该优化点依赖以下已完成的功能：
- ✅ **005-复杂度实时仪表盘** - 提供基础工具链
- ✅ **017-实用脚本工具库** - 提供基础工具架构
- ✅ **004-ADR 架构决策记录** - 用于架构合规性检查（可选）

---

## 进度安排

| 阶段 | 任务 | 预估时间 | 状态 |
|------|------|---------|------|
| Phase 1 | 扩展数据采集工具 | 0.5 天 | ✅ 已完成 |
| Phase 2 | 扩展报告生成器 | 0.5 天 | ✅ 已完成 |
| Phase 3 | 更新 Git Hooks | 0.5 天 | ✅ 已完成 |
| Phase 4 | 测试与验证 | 0.5 天 | ✅ 已完成 |
| **总计** | | **2 天** | ✅ 已完成 |

---

**版本**: v1.0
**维护者**: Framework Team
**创建日期**: 2026-04-12
