---
title: 文档生成进度记录模板
summary: 提供文档生成过程的进度追踪模板，用于记录各阶段状态、支持中断恢复并向用户展示当前执行进展。
keywords: template | progress | tracking | generation | aicc
scope: 文档生成进度记录模板
related_files: 无
dependencies: templates/GENERATION_PLAN_TEMPLATE.md | workflows/generation_workflow.md
verified_at: 2026-05-05
---

# 文档生成进度记录

> **项目**: [项目名称]  
> **开始时间**: YYYY-MM-DD HH:mm  
> **最后更新**: YYYY-MM-DD HH:mm  
> **当前状态**: [等待人工审核/已获用户确认/生成中/首版验收中/已完成/已阻塞]
> **下一步**: [下一步动作]
> **阻塞原因**: [如无则填写“无”]

---

## 🎯 总体步骤进度

- [ ] 步骤 1: 项目检测 ⏸️ 未开始
- [ ] 步骤 2: 策略决策 ⏸️ 未开始
- [ ] 步骤 3: 确定子文档清单 ⏸️ 未开始
- [ ] 步骤 4: 生成分析方案 ⏸️ 未开始
- [ ] 步骤 5: 等待人工审核 ⏸️ 未开始
- [ ] 步骤 6: 已获用户确认 ⏸️ 未开始
- [ ] 步骤 7: 执行文档生成 ⏸️ 未开始
- [ ] 步骤 8: 首版质量验收 ⏸️ 未开始

**进度**: 0/8 (0%)

---

## 📝 逐文档完成状态

### 阶段 1: 分析方案生成

#### 分析文档

- [ ] `dev_docs/_analysis/generation_plan.md` ⏸️ 未开始
- [ ] `dev_docs/_analysis/project_analysis_report.md` ⏸️ 未开始
- [ ] `dev_docs/_analysis/generation_progress.md` 🔄 进行中

---

### 阶段 2: 主文档生成

- [ ] `dev_docs/AI_Coding_Context.md` ⏸️ 未开始

---

### 阶段 3: 高优先级子文档

- [ ] `dev_docs/architecture_overview.md` ⏸️ 未开始
- [ ] `dev_docs/api_layer.md` ⏸️ 未开始
- [ ] `dev_docs/state_management.md` ⏸️ 未开始

**进度**: 0/3 (0%)

---

### 阶段 4: 中优先级子文档

- [ ] `dev_docs/routing_guide.md` ⏸️ 未开始
- [ ] `dev_docs/component_guide.md` ⏸️ 未开始
- [ ] `dev_docs/error_handling.md` ⏸️ 未开始

**进度**: 0/3 (0%)

---

### 阶段 5: 低优先级子文档

- [ ] `dev_docs/styling_guide.md` ⏸️ 未开始
- [ ] `dev_docs/form_validation.md` ⏸️ 未开始

**进度**: 0/2 (0%)

---

### 阶段 6: 目录结构

- [ ] `dev_docs/plans/` 目录创建 ⏸️ 未开始
- [ ] `dev_docs/plans/README.md` ⏸️ 未开始
- [ ] `dev_docs/knowledge/` 目录创建 ⏸️ 未开始
- [ ] `dev_docs/knowledge/README.md` ⏸️ 未开始
- [ ] `dev_docs/rules/combined/AI_RULES.md` ⏸️ 未开始

**进度**: 0/5 (0%)

---

## 🧪 验收进度

- [ ] `doc_health_checker` 已执行
- [ ] 必需章节检查通过
- [ ] 运行记录完整性检查通过
- [ ] 模板残留/占位符检查通过
- [ ] `health_check_report.md` 已落盘
- [ ] 最终 verdict = PASS

---

## 📌 状态变更记录

| 时间 | 当前状态 | 本步结果 | 下一步 | 备注 |
| ---- | -------- | -------- | ------ | ---- |
| YYYY-MM-DD HH:mm | 等待人工审核 | 已生成方案文档 | 等待用户确认 | [说明] |
| YYYY-MM-DD HH:mm | 已获用户确认 | 可以开始生成 | 生成主文档 | [说明] |
| YYYY-MM-DD HH:mm | 首版验收中 | 文档已生成，开始跑检查 | 生成健康报告 | [说明] |

---

## 🔄 如果中断，如何继续？

### 恢复步骤

1. **打开此文件** 查看"详细进度"部分
2. **找到未完成的任务** - 查找第一个状态为 ⏸️ 的任务
3. **告诉 AI**: "继续从 [未完成任务名称] 开始生成"
4. **AI 将跳过已完成部分** 继续生成未完成的文档

### 示例

```
用户: "继续生成文档"

AI会:
1. 读取此进度文件
2. 识别: "已完成主文档和2个子文档,还有1个高优先级子文档未完成"
3. 输出: "检测到进度记录,上次完成到api_layer.md,现在开始生成state_management.md"
4. 继续生成剩余部分
```

---

## 📌 备注

### 生成过程中的问题

[记录遇到的问题和解决方式]

---

### 特殊说明

[任何需要注意的特殊情况]

---

## 📊 统计信息

- **总任务数**: [由 AI 自动填写]
- **已完成数**: [数量]
- **进行中**: [数量]
- **未开始**: [数量]
- **已阻塞**: [数量]
- **整体进度**: [百分比]

---

**状态图例**:

- ⏸️ 未开始
- 🔄 进行中
- ✅ 已完成
- ❌ 已跳过
- ⚠️ 有问题
- ⏳ 等待人工审核
- 👤 已获用户确认
- 🧪 首版验收中
- 🚫 已阻塞

---

**最后更新**: YYYY-MM-DD HH:mm
