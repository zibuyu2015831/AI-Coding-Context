---
title: 快速开始指南 — 方案优先 6 步流程
summary: 5-10 分钟快速上手 AICC 框架；遵循"方案优先"原则，先生成审核方案再生成文档；与 workflows/path_a_first_generation.md 的 S0-S8 完整流程对齐
keywords: quick start | 方案优先 | 新用户旅程 | aicc
scope: 新用户首个 AICC 项目的入门路径；不涵盖中后期维护流程（见 workflows/maintenance_workflow.md）
related_files:
  - workflows/path_a_first_generation.md
  - templates/GENERATION_PLAN_TEMPLATE.md
  - AI_ENTRY_POINT.md
  - README.md
dependencies:
  - tools/py/project_scanner.py
  - tools/js/project_scanner.js
verified_at: 2026-04-26
---

# 快速开始指南

> **重要**: 本指南采用"方案优先"流程，确保文档基于实际代码
> 5-10 分钟快速上手：如何在新项目中使用这套文档体系规范

---

## ⚠️ 核心原则：方案优先

**不要直接让 AI 生成文档！** 必须先生成并审核方案。

```mermaid
graph LR
    A[复制规范] --> B[生成方案]
    B --> C[人工审核]
    C -->|批准| D[执行生成]
    C -->|修改| B

    style B fill:#f99,stroke:#f00,stroke-width:2px
    style C fill:#f99,stroke:#f00,stroke-width:2px
```

> 完整 8 步流程见 [`workflows/path_a_first_generation.md`](../workflows/path_a_first_generation.md)（S0-S8）。本指南是其精简的 6 步入门版（步骤 1-6，前置步骤 0 用于规模评估）。

---

## 🚀 场景 1: 新项目从零开始

### 步骤 0: 评估项目规模 🆕

**重要**: 先评估项目规模，选择合适的策略。**优先使用 AICC 工具**（跨平台 + 零依赖红线）：

```bash
# 推荐：使用 AICC 工具（与 V3.0 双脚本对称模式一致）
python tools/py/project_scanner.py . --exclude-standard
# 或 Node.js 版本：
node tools/js/project_scanner.js . --exclude-standard

# 降级 fallback（无 Python/Node.js 环境时）：
find . -name "*.ts" -o -name "*.js" -o -name "*.vue" | wc -l   # 文件数
# cloc 为第三方工具，违反零依赖红线，仅供应急参考
```

> 工具索引详见 [`AI_ENTRY_POINT.md` → 工具脚本标准段](../AI_ENTRY_POINT.md)。

**规模判断**:

- 🟢 **小型** (< 50 文件, < 5K 行): 一次性完成，约 2-4 小时
- 🟡 **中型** (50-200 文件, 5K-20K 行): 分 2-3 批，约 8-12 小时
- 🔴 **大型** (200-500 文件, 20K-50K 行): 分 5-8 批，约 1-2 天
- 🟣 **超大型** (> 500 文件, > 50K 行): 分 10+批，约 2-3 天

**⚠️ 大型/超大型项目必读**:

- 使用 `templates/PROGRESS_TRACKING_TEMPLATE.md` 跟踪进度
- 分批次执行，避免 AI 上下文溢出
- 每批次结束后记录进度和问题

---

### 步骤 1: 复制规范到新项目

```bash
# 克隆或复制 ai_coding_context 目录到新项目根目录
cp -r ai_coding_context/ /path/to/your_project/
cd /path/to/your_project/
```

---

### 步骤 2: 生成分析方案

发送给 AI（使用 [`templates/GENERATION_PLAN_TEMPLATE.md`](../templates/GENERATION_PLAN_TEMPLATE.md)）：

```
请阅读 ai_coding_context/AI_ENTRY_POINT.md，然后基于
ai_coding_context/templates/GENERATION_PLAN_TEMPLATE.md
为本项目生成文档分析方案，输出到 dev_docs/_analysis/generation_plan.md。

注意：本步骤只生成方案，不生成正式文档。等我审核通过后再继续。
```

AI 会自动完成：

1. 项目检测（语言 / 类型 / 规模）
2. 主文档结构规划（章节 / 子文档清单）
3. 数据采样（用于审核数据准确性）
4. 输出 `dev_docs/_analysis/generation_plan.md`

---

### 步骤 3: 审核方案

打开 `dev_docs/_analysis/generation_plan.md`，按以下清单逐项核对：

#### 审核清单

**1. 数据准确性审核**

- [ ] 项目规模数据
  - [ ] 运行 AI 提供的统计命令，验证文件数
  - [ ] 抽查几个目录，验证代码量
  - [ ] 技术栈描述准确
- [ ] 目录结构描述
  - [ ] 核心目录无遗漏
  - [ ] 目录用途描述准确
- [ ] 业务模块识别
  - [ ] 模块划分合理
  - [ ] 无重要模块遗漏

**2. 代码示例审核**

- [ ] 每个代码示例都有实际文件路径
- [ ] 打开文件验证代码存在
- [ ] 代码可直接复制使用
- [ ] 无敏感信息泄露

**3. 架构特点审核**

- [ ] 每个架构特点都有代码依据
- [ ] 无 AI 臆测的内容
- [ ] 描述与实际一致

**4. 填写审核意见**

在 `dev_docs/_analysis/generation_plan.md` 末尾追加：

```markdown
## 审核意见

### 需要修改的部分

1. [如果有]
2. [如果有]

### 批准意见

- [✓] 批准，可以开始生成文档
- [ ] 需要修改后重新提交
- [ ] 拒绝

签名: [your name]
日期: 2026-04-26
```

---

### 步骤 4: 执行文档生成（审核通过后）

**只有审核批准后，才发送此指令给 AI**:

```
方案已审核通过（见 dev_docs/_analysis/generation_plan.md）

请严格按照审核通过的方案生成完整文档：

1. 生成主文档 dev_docs/AI_Coding_Context.md
2. 生成高优先级子文档（按方案中列出的清单）
3. 创建 plans/ 和 knowledge/ 目录
4. 确保所有数据来自方案中标注的实际代码

注意：不要偏离方案，如需调整请先说明。
```

---

### 步骤 5: 验证和优化

- [ ] 检查生成的文档与方案一致
- [ ] 测试代码示例可运行
- [ ] 补充人工确认的特殊内容
- [ ] 测试文档可用性（模拟几个开发场景）

---

### 步骤 6: 清理（可选）

```bash
# 确认文档完成后，可删除规范和分析目录
rm -rf ai_coding_context/
rm -rf dev_docs/_analysis/
```

**完成！** ✅ 现在可以使用高质量文档辅助 AI 开发了。

---

## 📚 场景 2: 已有项目补充文档

### 步骤 1: 添加规范到项目

```bash
cp -r ai_coding_context /path/to/existing_project/
```

### 步骤 2-6: 同场景 1

同样遵循"方案优先"原则，先生成审查和补充方案，按场景 1 步骤 2-6 推进。

---

## 💡 最佳实践

### 推荐工作流

1. **项目启动时**: 立即生成完整文档体系（遵循方案优先）
2. **开发过程中**: 严格执行"方案驱动开发"
3. **遇到难题后**: 及时沉淀到 knowledge/
4. **定期维护**: 每月审查一次文档

### 团队协作

1. **Code Review 时**: 同时检查文档更新
2. **新成员入职**: 先阅读主文档和架构总览
3. **技术分享**: 将分享内容沉淀到 knowledge/

---

## ⚠️ 常见错误

### ❌ 错误做法

```
"请为我的项目生成完整的 AI 文档体系"
```

**问题**: 直接生成，没有方案审核环节，容易出现：

- 数据不准确
- 代码示例虚构
- 架构特点臆测

### ✅ 正确做法

```
"请先生成文档分析方案（使用 GENERATION_PLAN_TEMPLATE.md）
我审核通过后再生成文档"
```

**优势**:

- 数据有依据
- 可提前发现问题
- 质量有保障

---

## 📞 常见问题

### Q: 方案优先会不会太繁琐？

A: 虽然多花 1-2 小时，但避免了大量返工。实践证明，方案优先让准确率从 70% 提升到 95%+，返工率从 30% 降到 5%，总体更高效。

### Q: 如果方案审核发现问题怎么办？

A: 这正是方案优先的价值！在生成前发现问题，让 AI 修改方案即可。如果生成后才发现，整个文档可能需要重写。

### Q: 能跳过方案直接生成吗？

A: **强烈不建议**。除非是非常小的项目（<10 个文件），否则直接生成的文档质量难以保证。

### Q: 如何在多个项目间复用？

A: 把 `ai_coding_context/` 维护为独立仓库，每个新项目 clone 即可。

---

## 🎉 开始使用

选择场景 1，严格按照 6 个步骤（步骤 1-6，含前置步骤 0 评估）执行，确保方案优先！

> 完整 8 步流程（S0-S8，含 finalize / publish 阶段）见 [`workflows/path_a_first_generation.md`](../workflows/path_a_first_generation.md)。
