---
title: [项目名称] 文档生成进度记录
summary: [100-200字概述：文档生成过程的进度追踪文件，记录各阶段完成状态，支持中断后继续生成]
keywords: 进度记录 | 文档生成 | 任务追踪 | 中断恢复
scope: 文档生成进度追踪 (dev_docs/_analysis/)
related_files: 无
dependencies: templates/GENERATION_PLAN_TEMPLATE.md | workflows/generation_workflow.md
verified_at: [YYYY-MM-DD 格式日期]
---

# 文档生成进度记录

> **项目**: [项目名称]  
> **开始时间**: YYYY-MM-DD HH:mm  
> **最后更新**: YYYY-MM-DD HH:mm  
> **当前状态**: [进行中/已完成/已中断]

---

## 🎯 总体进度

- [ ] 步骤 1: 项目检测 ⏸️ 未开始
- [ ] 步骤 2: 策略决策 ⏸️ 未开始
- [ ] 步骤 3: 确定子文档清单 ⏸️ 未开始
- [ ] 步骤 4: 生成分析方案 ⏸️ 未开始
- [ ] 步骤 5: 方案审核通过 ⏸️ 未开始
- [ ] 步骤 6: 执行文档生成 ⏸️ 未开始

**进度**: 0/6 (0%)

---

## 📝 详细进度

### 阶段 1: 分析方案生成

#### 分析文档

- [ ] `dev_docs/_analysis/generation_plan.md` ⏸️ 未开始
- [ ] `dev_docs/_analysis/project_analysis_report.md` ⏸️ 未开始

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

**进度**: 0/4 (0%)

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
- **已完成**: [数量]
- **进行中**: [数量]
- **未开始**: [数量]
- **整体进度**: [百分比]

---

**状态图例**:

- ⏸️ 未开始
- 🔄 进行中
- ✅ 已完成
- ❌ 已跳过
- ⚠️ 有问题

---

**最后更新**: YYYY-MM-DD HH:mm
