---
title: AICC V3.x Comprehensive Review — 问题分类统计与系统性诊断
summary: 35 项 Issue 按视角/严重级别/类型/集群多维统计；揭示 5 大系统性问题集群及其根因
keywords: issue-analysis | clusters | systemic-issues | aicc | v3.x
scope: 本轮 35 项 Issue 的横切分析
verified_at: 2026-04-25
---

# AICC V3.x Comprehensive Review — 问题分类统计与系统性诊断

## 📊 多维统计

### 按严重级别

| 级别 | 数量 | 占比 | Issue ID |
|---|:-:|:-:|---|
| 严重 | 2 | 5.7% | 028（quick_start 错乱）/ 034（frontmatter 14%）|
| 主要 | 11 | 31.4% | 001/002/005/006/011/016/017/019/022/029/030/031 |
| 次要 | 14 | 40.0% | 003/004/007/008/009/012/013/018/020/023/024/026/032/033 |
| 建议 | 8 | 22.9% | 010/014/015/021/025/027/035 + 1 跨级 |

### 按视角分布

| 视角 | 数量 | 占比 | 主要议题 |
|---|:-:|:-:|---|
| A 用户 | 12 | 34% | 用户旅程 / 命名一致性 / 路径承诺 |
| B 完整性 | 18 | 51% | 实现-文档-PROGRESS 三角漂移 |
| C dev/ 卫生 | 6 | 17% | confirmed 命名 / 孤儿文件 / 悬空引用 |

注：部分 Issue 跨视角统计含交叉。

### 按类型

| 类型 | 数量 | 关键样本 |
|---|:-:|---|
| 文档问题 | 22 | quick_start 错乱、命名不一致、路径承诺、frontmatter 缺失 |
| 设计问题 | 9 | 工作流缺失、SOP 过度承诺、孤儿文件、目录命名 |
| 集成问题 | 3 | doc_health_checker 缺失、architecture_analyzer 缺失、--check-doc-errors 参数缺 |
| 代码问题 | 1 | aac_validator.js 头部 docstring |

### 按修复成本

| 成本档位 | 数量 | 累计人天 |
|---|:-:|:-:|
| < 0.5 人天 | 14 | ~5 |
| 0.5-2 人天 | 14 | ~16 |
| 2-5 人天 | 5 | ~17 |
| > 5 人天 | 2 | ~26（含 034 P1+P2 阶段累计 38 人天）|

---

## 🌐 五大系统性问题集群

### 集群 1：V3.0 命名一致性系统漂移

**成员**：016 / 029 / 032

**症状**：
- AI_RULES.md 在 path_a 用小写，其他用大写
- AI_RULES.md 路径在 README/templates/path_a 共 4 处给出 3 个不同位置
- 主文档名 ai_coding_context.md vs AI_Coding_Context.md 大小写矛盾

**根因分析**：

- AICC v3.0 P0 阶段产出多份关键文档（AI_ENTRY_POINT、path_a、templates、guides），但**缺乏单一真相源约束**
- 后续修订各文档独立演进，命名漂移悄然发生
- Linux 文件系统区分大小写，但开发环境（macOS APFS / Windows NTFS 默认）不区分 → 漂移难被早期发现

**治理方向**：
- 短期：以 AI_ENTRY_POINT 术语表为权威源，全仓库 grep 统一
- 长期：在 `core/framework_spec.md` 增设"标准产物路径"章节作为 SSOT，CI 加入命名规范扫描

### 集群 2：FRAMEWORK_CONTEXT vs PROGRESS 漂移

**成员**：001 / 011 / 012 / 014 / 015

**症状**：
- 顶部"V3.0 已完成"两文档不一致
- 底部章节漏 011 / 014
- "(10/17)" vs "18 个" 总数不一致
- 019 已完成但未在 PROGRESS 18 项清单登记

**根因分析**：

- V3.0 进入 P1 阶段（004/005/006/011/014）时，PROGRESS.md 持续更新，但 FRAMEWORK_CONTEXT.md 顶部摘要未同步
- 缺乏"PROGRESS 变更触发 FRAMEWORK_CONTEXT 刷新"机制
- 同一文档内部矛盾（PROGRESS L18 vs L88）说明审校流程不严

**治理方向**：
- 短期：以 PROGRESS 为 SSOT，FRAMEWORK_CONTEXT 顶部加 verified_at 字段
- 长期：考虑 commit-guided-update（018）扩展，PROGRESS 变更自动提示同步 FRAMEWORK_CONTEXT

### 集群 3：dogfood 自指失败

**成员**：034（严重）/ 014（联动）/ 027

**症状**：
- 012-强制文档摘要 0% 自指（顶层入口 + agents/ + guides/ + config/ 全 0%）
- 014 智能推荐依赖 frontmatter，但 frontmatter 14% → 014 实际不可用
- 005 设计完整含 walkthrough，但仅留在 dev/V3.0/confirmed/，未提升至 Public

**根因分析**：

- 工程红线（双脚本 / 零依赖）有自动化校验（双脚本 diff、import 扫描）→ 100% 落地
- 文档红线（frontmatter / 命名一致 / 跨文档同步）**没有自动化校验** → 0%-14% 落地
- "声称已完成"未与"自指落地"挂钩，导致 PROGRESS 的 ✅ 标识失真
- 设计文档（walkthrough）与发布文档（Public workflows）的转换未制度化

**治理方向**：
- 短期：CI 集成 summary_validator 强制门禁（治理-1）
- 短期：将 PROGRESS ✅ 标准从"实体存在"升级为"实体存在 + 自指落地 + Public 发布"
- 长期：每个 confirmed/NNN 优化点须有 release checklist，包括"提升至 Public"步骤

### 集群 4：实体缺失但被引用

**成员**：017（doc_health_checker）/ 020（complexity --check-doc-errors）/ 026（architecture_analyzer）

**症状**：
- 6 处工作流引用 doc_health_checker.py/.js 但实体不存在
- complexity_scanner.py 实际无 --check-doc-errors 参数
- 005 walkthrough 声称工具链含 architecture_analyzer.py，实际不存在

**根因分析**：

- 文档先于实施完成 — 工作流先写"应该用 X 工具"，但工具尚未实施
- 缺乏"文档命令 → 实际可执行"的回归校验
- 设计文档（walkthrough）与实施现状脱节

**治理方向**：
- 短期：选项 A 补全实体（017 推荐）或选项 B 删除引用（020 推荐）
- 长期：CI 加入"文档中的命令是否可执行"扫描（grep `python tools/...py` 后验证文件存在性）

### 集群 5：用户旅程断点（README + quick_start 系列）

**成员**：028（严重）/ 030 / 031 / 033

**症状**：
- README "3 步" 与正文 4 步不符
- quick_start 步骤跳号 + 未闭合代码块 + 末尾计数矛盾
- quick_start 4 处过时框架名 ai_documentation_framework
- quick_start 推荐 find/cloc 而非 V3.0 project_scanner

**根因分析**：

- README 持续更新（已用 ai_coding_context），但 guides/ 在框架更名时未同步
- guides/ 维护者与 README 维护者似为不同流程，缺乏一致性检查
- quick_start 是用户首份操作文档，但 V3.0 P0 阶段更新核心规范时未联动更新此文档
- 文档审校未做"完整步骤跑通"测试

**治理方向**：
- 短期：完整重写 quick_start 与 README 顶层呼应
- 长期：版本发布前必须有"新用户旅程实测"环节，30 分钟跑通才能发布

---

## 🔍 横切诊断

### 横切 1：工程能力 vs 文档能力的两极分化

**数据**：

| 维度 | 完成率 | 主导角色 |
|---|:-:|:-:|
| 双脚本对称 | 100% | 工程师 |
| 零依赖红线 | 100% | 工程师 |
| 工具 docstring | 99% | 工程师 |
| frontmatter（自指）| 14% | 文档作者 |
| 命名一致性 | ~70% | 文档作者 |
| 用户旅程顺畅度 | 不达标 | 文档作者 |

**洞察**：当工程红线有自动化校验（CI / 静态扫描）时执行力极强；当规则只靠"人工自觉遵守"时执行力崩溃。**自动化是文档治理的唯一出路**。

### 横切 2：dogfood 是 V3.0 最大的设计缺位

V3.0 提倡"AICC 用自己的方法论审 AICC 自己"（quality/README.md L11），但实际 dogfood 仅在 quality 体系层面（B0 完成 v2.0 自审），未在功能产物层面落地。

具体表现：
- 012-强制摘要：框架强制规则自己 0% 落地
- 013-AI 互审：实施了，但 AICC 文档自己未走互审（PROGRESS 漂移、FRAMEWORK_CONTEXT 多处不一致都是缺审校的证据）
- 014-文档阅读习惯引导：依赖 012 frontmatter，但前者无可用基础数据

**建议**：把 dogfood 升级为强制原则，每项功能"已完成"标识需附自指验证证据。

### 横切 3：发布最后一里的系统性缺失

多个 Issue 揭示同一模式："设计完整但未发布到 Public"：

- 027：005 walkthrough 完整但未提升至 workflows/
- 015：019 已完成但未登记 PROGRESS
- 023：agents/_templates/ 实存但 README 未索引

**模式**：内部档案丰富，对外发布稀薄。新用户看不到的能力等于不存在。

**建议**：每个 V3.0 优化点 release 时强制走 4 步：实体 → 文档 → Public 提升 → README 索引。

---

## 📈 风险演化预测

### 不修复的中长期风险

- **3 个月内**：用户流失加剧，社区信任受损（quick_start 是首次接触点）
- **6 个月内**：014/018 等依赖 frontmatter 的功能持续无效；PROGRESS 漂移加重
- **12 个月内**：framework 与 dev/V3.0 双轨偏差越来越大，重构成本指数上升

### 按本路线图修复后的预期

- **P0 完成（2 周）**：用户旅程恢复，30 分钟预算实测通过
- **P1 完成（2 月）**：所有"主要"级别 Issue 修复，doc_health_checker 上线
- **P2 完成（3 月）**：frontmatter 全量合规，dogfood 自指生效
- **长期治理（持续）**：CI 防回归，跨平台覆盖

---

## 🎯 关键成功指标（KSI）

复审时必查的 5 项关键指标：

| KSI | 当前 | P0 后 | P1 后 | P2 后 | 目标 |
|---|:-:|:-:|:-:|:-:|:-:|
| Public frontmatter 合规率 | 14% | 30% | 60% | 95% | ≥ 95% |
| 30 分钟新用户旅程通过率 | ❌ 不通过 | ✅ 通过 | ✅ | ✅ | 100% |
| Issue 严重级别数 | 2 | 0 | 0 | 0 | 0 |
| Issue 主要级别数 | 11 | 4 | 0 | 0 | 0 |
| dogfood 自指落地数 | 1/12 | 5/12 | 9/12 | 12/12 | 12/12 |

---

**版本**: v1.0
**创建日期**: 2026-04-25
**审查者**: Claude Opus 4.7
