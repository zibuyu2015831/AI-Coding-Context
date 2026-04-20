# 问题追踪表 - 2026-04-17_V3.0_Final_Check

| 问题ID | 类型 | 严重级别 | 关联 ADR/Commit | 问题描述 | 涉及文件路径 | 复查方法 | 验证结果 | 修复方案 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PROJ-20260417-001** | 设计问题 | **非问题 (N/A)** | ADR 012 | 误报：ADR 012 是规范 AI 生成文档的行为，templates/ 模板已落实，非框架自身文档要求。 | `templates/` | 检查 templates/ 模板是否含 frontmatter。 | ✅ **已核实验证** - templates/ 下模板已全部集成 YAML frontmatter，ADR 012 已正确落实 | 无需修复。 |
| **PROJ-20260417-002** | 合规问题 | **主要 (P1)** | V3.0 Redlines | JS 侧多个核心脚本引用了第三方 NPM 库 `glob`，违反零依赖红线。 | `tools/js/batch_fix_manager.js`, `tools/js/semantic_related_detector.js` | 检查 `package.json` 依赖及脚本中的 `require('glob')` 语句。 | ✅ **确认** - 3个文件确认：`batch_fix_manager.js:57`、`semantic_related_detector.js:48`、`fix_history_manager.js:54` | 使用 Node.js 原生 `fs.readdirSync` 配合正则递归实现轻量级文件匹配。 |
| **PROJ-20260417-003** | 设计问题 | **主要 (P1)** | ADR 004 | 已确认的 ADR (004, 005, 018) 未迁移至 `dev_docs/` 正式目录。 | `dev/V3.0/confirmed/`, `dev_docs/architecture/decisions/` | 核对 `dev_docs/` 目录下是否存在 004, 005, 018 号文件。 | ✅ **确认** - `dev_docs/architecture/decisions/` 仅有 001/002，ADR 004/005/018 仍在 `dev/V3.0/confirmed/` | 执行文件物理迁移，并同步更新全局文档中的链接引用。 |
| **PROJ-20260417-004** | 设计问题 | **主要 (P1)** | ADR 018 | Git Safety Red Zones 逻辑缺失在 `core/` 规约中的定义，仅存在于提案中。 | `core/security_rules.md` | 对比 `core/security_rules.md` (v2.3) 与 ADR 018 的条文。 | ⚠️ **部分确认** - `core/security_rules.md`(v2.3) 确实无红区定义，但 ADR 018 本身也未明确定义红区规则 | 将 ADR 018 的安全红区定义提取并合并至 `core/security_rules.md`，升级规约至 v3.0。 |
| **PROJ-20260417-005** | 逻辑问题 | **严重 (P0)** | 对称性约束 | `complexity_scanner.js` 中的 `parseYaml` 函数被硬编码为返回 `null`，导致配置失效。 | `tools/js/complexity_scanner.js` | 查阅脚本源码中的 `parseYaml` 函数实现。 | ✅ **确认** - `tools/js/complexity_scanner.js:112-121` 明确返回 `null` | 实现一个零依赖的简易 YAML 解析逻辑（基于正则）以对齐 Python 版本的行为。 |
| **PROJ-20260417-006** | 系统集成 | **主要 (P1)** | ADR 018 | `commit_guided_update.md` 脚本缺乏对"红区"提交的机械式硬性阻断。 | `workflows/commit_guided_update.md`, `tools/js/git_safety.js` | 验证工作流脚本是否在执行 Git 操作前调用并校验 `git_safety` 的返回结果。 | ✅ **确认** - 工作流仅引用 `git_safety_workflow.md`，无机械式阻断逻辑 | 在工作流脚本中集成 `git_safety` 校验步骤，并设置非零退出码阻断执行。 |
| **PROJ-20260417-007** | 元数据问题 | **建议 (P3)** | ADR 命名空间 | ADR 编号 `002` 可能在`dev/`目录外存在历史归档。 | `dev_docs/architecture/decisions/002-layered-documentation.md` | 检索 ADR 历史记录中的编号重复情况。 | ⚠️ **不确认** - `dev/`下无原002归档记录，当前002无冲突标记，建议降级为P3观察项 | 保持当前编号，建议在 ADR 演进文档中标注版本演进路径以便追溯。 |
| **PROJ-20260417-008** | 测试问题 | **次要 (P2)** | 质量模型 | `complexity_scanner.py` 对 Markdown 为主的项目产出 0 分质量评分，算法不兼容。 | `tools/py/complexity_scanner.py` | 在 MD 项目中运行扫描器并检查 `quality_score` 输出。 | ✅ **确认** - 运行扫描器输出 `quality_score: 0` | 优化扫描器的质量评估算法，针对 Markdown 的结构化特征（如摘要、层级）进行权重调整。 |

---

## 问题统计

- **总问题数**：8
- **非问题 (N/A)**：1 (问题001 - 误报)
- **严重问题 (P0)**：1 (问题005)
- **主要问题 (P1)**：4 (问题002, 问题003, 问题004, 问题006)
- **次要问题 (P2)**：1 (问题008)
- **建议 (P3)**：1 (问题007)

### 有效问题数：7

### 复审结论
- 问题002: ✅ 确认 - V3.0零依赖红线真实存在
- 问题003: ✅ 确认 - ADR 004/005/018未迁移真实
- 问题004: ✅ 确认 - 红区定义缺失真实
- 问题005: ✅ 确认 - Py/JS功能不对称真实
- 问题006: ✅ 确认 - 工作流无阻断逻辑真实
- 问题007: ⚠️ 需历史记录确认
- 问题008: ✅ 确认 - quality_score为0真实

### 问题类型分布
- 设计问题：1 (问题004)
- 合规问题：1 (问题002)
- 逻辑问题：1 (问题005)
- 系统集成：1 (问题006)
- 元数据问题：1 (问题007)
- 测试问题：1 (问题008)

---

## 修复优先级

### 第一批次 (立即修复)
1. **PROJ-20260417-005** - parseYaml 空心化（P0，严重影响功能）
2. **PROJ-20260417-002** - glob 依赖违规（P1，破坏零依赖红线）

### 第二批次 (高优先级)
3. **PROJ-20260417-003** - ADR 未迁移
4. **PROJ-20260417-006** - 红区阻断缺失

### 第三批次 (优化改进)
5. **PROJ-20260417-004** - 红区定义缺失
6. **PROJ-20260417-008** - quality_score 算法

### 观察项 (P3)
7. **PROJ-20260417-007** - ADR 编号碰撞（需进一步确认历史记录）

### 已排除
- **PROJ-20260417-001** - 误报，ADR 012 已正确落实

---

**文档版本**：1.2  
**更新日期**：2026-04-20  
**状态**：复审完成，等待项目完善