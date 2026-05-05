---
title: 文档更新审核标准
summary: 定义文档更新场景的审核维度、权重与检查项，帮助在准确性、清晰度和完整性三个层面判断文档修改是否达到可接受质量。
keywords: doc-review | standard | documentation | checklist | quality | aicc
scope: 文档更新场景下的审核标准
related_files: 无
dependencies: workflows/review-workflow.md | workflows/shared/ai_checklist.md | core/SUMMARY_FORMAT_SPEC.md
verified_at: 2026-05-05
---

# 文档更新审核标准

## 审核清单 (权重分配)

### 1. 准确性 (权重: 30%)

- [ ] 文档内容是否与代码完全一致？
- [ ] 代码示例是否经过验证？
- [ ] 路径引用是否正确？

### 2. 清晰度 (权重: 25%)

- [ ] 语言是否通顺易懂？
- [ ] 结构是否逻辑清晰？
- [ ] 是否使用了适当的图表辅助？

### 3. 完整性 (权重: 20%)

- [ ] 是否覆盖了所有关键信息？
- [ ] 是否包含必要的上下文？
- [ ] 是否有相关的参考链接？

### 4. 格式规范 (权重: 15%)

- [ ] 是否符合 Markdown 规范？
- [ ] 是否符合框架的文档格式要求？
- [ ] 目录结构是否正确？

### 5. 一致性 (权重: 10%)

- [ ] 术语使用是否统一？
- [ ] 风格是否与现有文档保持一致？
- [ ] 是否更新了所有相关联的文档？

### 6. Commit 质量 (权重: 10%) 🆕

- [ ] Commit message 是否清晰说明文档更新内容？
- [ ] WHAT 是否说明更新了哪些文档？
- [ ] WHY 是否说明文档更新的触发原因（代码变更/需求变更）？
- [ ] 是否使用 prompt(doc): 前缀？

## 合格标准

- **合格线**: ≥ 75 分
- **优秀线**: ≥ 90 分

## 参考

- Commit 质量评分: `tools/py/commit_quality_scorer.py`
- Commit 引导更新: `workflows/commit_guided_update.md`
