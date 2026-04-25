# 005-复杂度实时仪表盘实施方案与进度表

本文档旨在落实 V3.0 P1 阶段核心优化点"005-复杂度实时仪表盘"。系统的核心目标是在 AI 辅助编程模式下，实时监控项目复杂度的增长，防止技术债隐性累积，提供"复杂度刹车"机制。

## 执行优先级与灰度策略

遵循"先基础数据采集，再报告生成，最后自动化集成"的路线，分阶段逐步落地。

---

## Proposed Changes

### Phase 1: 基础数据采集 (MVP)

**目标**：开发核心数据采集工具，充分复用现有 git 工具功能，支持对代码规模、依赖关系、代码质量和架构健康度的基础统计。

#### [NEW] `tools/py/complexity_scanner.py` (Python 版本)
**工具拆解任务**：
1. **输入解析**：处理命令行参数，支持指定扫描范围
2. **依赖调用**：
   - 调用 `git_diff_analyzer.py` 获取代码变更数据（新增行数、变更类型统计）
   - 调用 `git_inspector.py` 检查仓库状态
3. **代码规模计算**：基于 git 分析结果计算总代码量、文件数
4. **依赖关系分析**：
   - Node.js：分析 package.json + 解析 require/import
   - Python：分析 requirements.txt + 解析 imports
5. **代码质量评估**：
   - 统计 TODO/FIXME 标记
   - 检查重复代码（简单字符串匹配）
6. **架构健康度**：统计核心文件变更、分析代码耦合度
7. **数据整合**：将各来源数据整合为统一 JSON 格式
8. **风险评估**：根据配置计算风险评分

#### [NEW] `tools/js/complexity_scanner.js` (Node.js 版本)
功能与 Python 版本保持一致，使用 Node.js 实现，调用相应的 js 工具。

#### [NEW] `dev_docs/complexity/config.yaml`
复杂度阈值配置文件，包含：
- 警告阈值（建议改进）
- 严重警告阈值（必须改进）
- 危机阈值（立即重构）
- 可配置的指标权重

#### 复用现有功能
**核心优势**：
- 避免重复实现 git 操作
- 利用现有稳定的 `git_diff_analyzer.py` 和 `git_inspector.py`
- 保持与 AICC 工具架构的一致性

---

### Phase 2: 报告生成系统

**目标**：将原始数据转化为人类可读的报告，支持多种格式输出。

#### [NEW] `tools/py/report_generator.py`
**功能**：
1. **Markdown 报告生成**：创建格式化的每日复杂度报告
2. **HTML 报告生成**：基于模板生成可视化页面
3. **数据可视化**：
   - 集成 Mermaid 图表
   - 支持趋势对比
4. **风险警示**：根据阈值自动标识高风险指标
5. **行动建议**：为每个风险提供具体的改进建议

#### [NEW] `dev_docs/complexity/template.html`
通用 HTML 报告模板，包含：
- 响应式布局
- Mermaid 图表支持
- 风险警示矩阵
- 行动建议区域

#### [NEW] `dev_docs/complexity/` 目录结构
建立复杂度报告存储目录：
```
dev_docs/complexity/
├── config.yaml          # 配置文件
├── data/                # 原始数据存储
│   ├── 2026-04-12.json
│   └── history.json
├── reports/             # Markdown 报告
│   ├── 2026-04-12.md
│   └── index.md         # 报告索引
└── dashboard/           # HTML 可视化
    ├── template.html
    ├── style.css
    └── dashboard.html
```

---

### Phase 3: 自动化集成

**目标**：实现自动化扫描和通知机制，确保监控的连续性。

#### [MODIFY] `tools/install_hooks.py`
**修改内容**：添加复杂度扫描的 Git Hooks 支持
- pre-commit 钩子：提交前检查复杂度增量
- post-commit 钩子：提交后生成报告

#### [NEW] `tools/py/notifier.py`
**功能**：
1. **Slack 通知**：严重警告级别的实时通知
2. **Email 通知**：每日报告和严重警告邮件
3. **集成支持**：与 CI/CD 系统集成（GitHub Actions/GitLab CI）

---

### Phase 4: 高级功能优化（设计阶段，未实施）

**状态**：🔜 **未实施** — 设计完整规划，但**不在 005 P1 范围内**。如需推进，应作为独立优化点立项（候选条目登记于 `dev/V3.0/PROGRESS.md` "V3.0+ 后期增益"段）。

**目标**：增强系统功能，提供更深度的复杂度分析。

#### [PLANNED] `tools/py/architecture_analyzer.py`（待实施）
**功能**：
1. **领域边界分析**：基于目录结构和代码内容识别领域边界
2. **架构腐化检测**：检测跨领域耦合和架构边界侵蚀
3. **技术债评估**：综合评分系统，量化技术债严重程度

#### [PLANNED] `tools/py/trend_analyzer.py`（待实施）
**功能**：
1. **历史趋势分析**：对比不同时间段的复杂度变化
2. **预测模型**：基于历史数据预测未来复杂度增长
3. **优化建议**：根据趋势提供架构优化建议

---

## 验证计划

详见同目录下的 `walkthrough.md`。

---

## 依赖关系

该优化点依赖以下已完成的功能：
- ✅ **实用脚本工具库** (017) - 提供基础工具架构
- ✅ **Git 信息检查工具** (017) - 用于增量计算
- ✅ **配置管理系统** (016) - 用于阈值配置管理

---

**版本**: v1.0
**维护者**: Framework Team
**创建日期**: 2026-04-12
