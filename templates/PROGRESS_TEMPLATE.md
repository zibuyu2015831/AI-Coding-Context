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
> **流程阶段进度**: [Step X/Y，当前处于某 gate]
> **产物完成度**: [已完成 X/Y 个产物，说明 _analysis / 正式文档 / 规则文件状态]
> **当前 gate**: [Phase 1 人工审核/正式生成/首版质量验收/无]
> **下一步动作**: [下一步动作]
> **阻塞原因**: [如无则填写“无”]
> **正式生成授权**: [未授权/用户确认/用户明确要求跳过审核；如已授权，记录用户原话摘要]

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

**流程阶段进度**: 0/8 (0%)，表示工作流步骤推进情况，不代表文档产物完成度。

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

**产物完成度**: 0/3 (0%)，表示本阶段文档产物完成情况。

---

### 阶段 4: 中优先级子文档

- [ ] `dev_docs/routing_guide.md` ⏸️ 未开始
- [ ] `dev_docs/component_guide.md` ⏸️ 未开始
- [ ] `dev_docs/error_handling.md` ⏸️ 未开始

**产物完成度**: 0/3 (0%)，表示本阶段文档产物完成情况。

---

### 阶段 5: 低优先级子文档

- [ ] `dev_docs/styling_guide.md` ⏸️ 未开始
- [ ] `dev_docs/form_validation.md` ⏸️ 未开始

**产物完成度**: 0/2 (0%)，表示本阶段文档产物完成情况。

---

### 阶段 6: 目录结构

- [ ] `dev_docs/plans/` 目录创建 ⏸️ 未开始
- [ ] `dev_docs/plans/README.md` ⏸️ 未开始
- [ ] `dev_docs/knowledge/` 目录创建 ⏸️ 未开始
- [ ] `dev_docs/knowledge/README.md` ⏸️ 未开始
- [ ] `dev_docs/rules/combined/AI_RULES.md` ⏸️ 未开始

**产物完成度**: 0/5 (0%)，表示本阶段目录与规则产物完成情况。

---

## 🧪 验收进度

- [ ] `summary_validator` 已执行（仅代表元数据/摘要格式检查）
- [ ] `doc_health_checker` 已执行
- [ ] Python/JS 两套 `doc_health_checker` 均已执行
- [ ] 必需章节检查通过
- [ ] 运行记录完整性检查通过
- [ ] 模板残留/占位符检查通过
- [ ] Python/JS 两套 `semantic_review_checker` 均已执行
- [ ] `health_check_report.md` 已落盘并通过自身检查
- [ ] 最终 verdict = PASS 或 PASS_WITH_ACCEPTED_ISSUES

### checker_status_matrix

| stage | tool | implementation | status | meaning | required_before_pass |
| --- | --- | --- | --- | --- | --- |
| metadata | summary_validator | python/js | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 只证明 frontmatter/summary 格式 | no |
| structure | doc_health_checker | python | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 结构、模板残留、运行记录和首版验收契约 | yes |
| structure | doc_health_checker | js | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 与 Python checker 交叉验证 | yes |
| semantic | semantic_review_checker | python | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 事实一致性、测试拓扑和审核门语义 | yes |
| semantic | semantic_review_checker | js | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 与 Python checker 交叉验证 | yes |
| acceptance | health_check_report | markdown | [PASS/FAIL/NOT_RUN/UNAVAILABLE/WAIVED_WITH_REASON] | 首版验收报告已落盘且自身通过检查 | yes |

> 禁止把 `summary_validator PASS` 单独表述为“验证通过”或“首版验收通过”。任一首版必需项为 `FAIL`、`NOT_RUN` 或未结构化豁免时，最终 verdict 只能是 `FAIL`。

---

## 🔎 Phase 1 方案复查记录

> 本节只记录方案阶段复查，不替代首版质量验收。用户确认前只能写“建议通过，等待用户确认”，不得写“可进入正式文档生成”。

- **review_trigger**: [首次生成自检/用户要求审核 _analysis/其他]
- **review_started_at**: YYYY-MM-DD HH:mm
- **review_completed_at**: YYYY-MM-DD HH:mm
- **reviewed_files**: `generation_plan.md`, `project_analysis_report.md`, `generation_progress.md`
- **manual_review_summary**: [人工语义复查结论，包含事实、证据、待确认边界和项目定位覆盖]
- **writeback_summary**: [已回写文件；无需回写的文件必须写明“已检查，无需回写”及原因]
- **blocker_count**: [数量]
- **warning_count**: [数量]
- **waived_issue_count**: [数量，含豁免理由]
- **phase1_recommendation**: [需修正，已回写 _analysis/建议通过，等待用户确认/需人工确认，禁止正式生成]
- **user_confirmation_status**: [pending/confirmed/rejected]
- **formal_generation_authorization**: [none/user_confirmed/user_explicit_skip_review]
- **authorization_source_summary**: [用户确认或授权原话摘要；未授权时写“未授权”]

### machine_checks

| round | tool | implementation | command | exit_code | issue_count | status | disposition |
| ----- | ---- | -------------- | ------- | --------- | ----------- | ------ | ----------- |
| 1 | doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [fixed/accepted/waived/原因] |
| 1 | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [fixed/accepted/waived/原因] |

### 复查输出协议

- `需修正，已回写 _analysis`: 仍有 blocker 或三件套不一致，禁止请求用户通过。
- `建议通过，等待用户确认`: 无 blocker，但正式生成仍需用户明确确认。
- `需人工确认，禁止正式生成`: 存在代码和仓库文档无法回答的策略/业务问题。

## 🔎 首版质量验收记录

> 本节只记录正式文档首版生成后的质量验收。工具失败、健康报告缺失、健康报告自身未通过检查、AI Rules 与源码事实冲突、敏感值泄露或核心架构事实冲突时，不得写“已完成”。

- **review_trigger**: 全部正式文档生成完成，进入首版验收
- **review_started_at**: YYYY-MM-DD HH:mm
- **review_completed_at**: YYYY-MM-DD HH:mm
- **reviewed_files**: 全部正式文档 + `_analysis` 运行记录
- **health_report**: `dev_docs/_analysis/health_check_report.md`
- **final_verdict**: PASS / PASS_WITH_ACCEPTED_ISSUES / FAIL
- **blocker_count**: [数量]
- **accepted_issue_count**: [数量]
- **writeback_summary**: [已回写文件；无需回写的文件必须写明原因]
- **user_confirmation_status**: pending / confirmed / rejected

### machine_checks

| round | tool | implementation | command | exit_code | issue_count | status | disposition |
| ----- | ---- | -------------- | ------- | --------- | ----------- | ------ | ----------- |
| 1 | doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [verified/fixed/accepted/原因] |
| 1 | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [verified/fixed/accepted/原因] |
| 1 | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [verified/fixed/accepted/原因] |
| 1 | semantic_review_checker | js | `node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .` | [0/1/2/124] | [数量] | [PASS/FAIL/UNAVAILABLE] | [verified/fixed/accepted/原因] |

### accepted_issues

无 accepted issue

如存在 accepted issue，必须逐项记录 issue_id、tool、implementation、file、issue_type、original_status、accepted_reason、residual_risk 和 follow_up；不得豁免敏感值泄露、AI Rules 冲突、核心运行架构冲突、必需文档缺失或健康报告自身失败。

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
