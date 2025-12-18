# AI Coding Context 框架审查文档索引

本目录存放所有框架审查相关的文档，每次审查创建一个独立的子目录，便于追踪框架的演进过程和审查历史。

## 📚 审查指南与标准

- [启动框架审查](./Start_Review.md) - AI助手启动审查的入口点和指令模板
- [框架审查指南](./Framework_Review_Guidelines.md) - 所有审查活动的标准化指南和方法论
- [问题记录标准与模板](./Issue_Recording_Standard.md) - 问题记录的标准格式和模板
- [进度跟踪标准](./Progress_Tracking_Standard.md) - 审查进度跟踪的标准与规范

## 📋 审查目录使用规范

### 目录结构
```
dev/reviews/
├── README.md                           # 本文件，审查文档索引
├── Framework_Review_Guidelines.md       # 框架审查标准化指南
├── Issue_Recording_Standard.md           # 问题记录标准与模板
└── YYYY-MM-DD_Version_Scope/             # 每次审查的专用目录
    ├── Review_Plan_Specific.md           # 本次审查的专项计划
    ├── Comprehensive_Review_Report.md     # 全面审查报告
    ├── Issue_Tracking.md                 # 问题跟踪表
    ├── Issue_Analysis.md                 # 问题分类统计报告
    ├── Progress_Tracking.md              # 审查进度跟踪表
    ├── Review_Data.zip                   # 审查数据与证据
    ├── Assessment_Dashboard.html          # 框架评估仪表板
    ├── Improvement_Roadmap.md            # 改进路线图
    ├── [Task_Name]_Assessment_Report.md  # 特定任务专项报告
    ├── Review_Log.md                    # 审查日志
    └── Review_Checklist.md              # 问题复查清单
```

### 审查目录命名规范
- **格式**：`YYYY-MM-DD_Version_Scope`
- **示例**：`2025-12-18_V3.0_Comprehensive`
- **说明**：
  - `YYYY-MM-DD`：审查启动日期
  - `Version`：框架版本号
  - `Scope`：审查范围（Comprehensive=全面，P0=P0任务，Component=组件专项等）

### 审查交付物标准
每次审查应包含以下标准交付物：

| 交付物 | 文件名 | 说明 |
|--------|--------|------|
| 审查计划 | Review_Plan_Specific.md | 本次审查的专项计划，基于标准指南制定 |
| 审查报告 | Comprehensive_Review_Report.md | 按照标准大纲编写的全面审查报告 |
| 问题跟踪 | Issue_Tracking.md | 详细记录所有发现的问题，包含文件路径 |
| 问题分析 | Issue_Analysis.md | 按类型、严重级别等维度分析问题 |
| 进度跟踪 | Progress_Tracking.md | 审查进度跟踪表，支持断点续审 |
| 审查数据 | Review_Data.zip | 原始审查数据、测试日志、代码分析结果等 |
| 评估仪表板 | Assessment_Dashboard.html | 可视化呈现框架评估结果 |
| 改进路线图 | Improvement_Roadmap.md | 基于审查结果的改进计划 |
| 专项报告 | [Task_Name]_Assessment_Report.md | 特定任务或组件的专项评估报告 |
| 审查日志 | Review_Log.md | 审查过程中的每日记录 |
| 复查清单 | Review_Checklist.md | 基于问题跟踪表生成的复查指南 |

## 🔄 审查流程

1. **准备阶段**
   - 创建审查目录 `YYYY-MM-DD_Version_Scope/`
   - 基于标准指南制定专项审查计划
   - 准备审查环境和工具

2. **执行阶段**
   - 按照标准审查方法执行各项审查活动
   - 实时记录问题到问题跟踪表
   - 每日更新审查日志

3. **报告阶段**
   - 生成全面审查报告
   - 进行问题分析和统计
   - 创建改进路线图和复查清单

4. **归档阶段**
   - 所有交付物归档到审查目录
   - 更新本索引文件的审查历史
   - 基于问题跟踪表进行问题复查和跟踪

## 📊 审查历史

审查历史将按时间顺序记录在此处，每次审查完成后更新。每次审查条目包含：
- 审查日期、版本和范围
- 审查状态（进行中/已完成）
- 审查描述和特色
- 交付物链接

---

*本索引文件将在每次审查完成后更新，保持审查历史的完整性和可追溯性*

## 当前审查状态

### 2025-12-18_V3.0_Comprehensive
- **状态**：✅ 已完成
- **审查范围**：全面审查（架构、组件、文档、集成、质量、体验）
- **审查时长**：约2小时
- **发现问题**：4个（2个集成问题，2个文档问题）
- **总体评价**：良好
- **专项计划**：[Review_Plan_Specific.md](./2025-12-18_V3.0_Comprehensive/Review_Plan_Specific.md)
- **全面报告**：[Comprehensive_Review_Report.md](./2025-12-18_V3.0_Comprehensive/Comprehensive_Review_Report.md)
- **问题跟踪**：[Issue_Tracking.md](./2025-12-18_V3.0_Comprehensive/Issue_Tracking.md)
- **改进路线图**：[Issue_Analysis_and_Roadmap.md](./2025-12-18_V3.0_Comprehensive/Issue_Analysis_and_Roadmap.md)
- **进度跟踪**：[Progress_Tracking.md](./2025-12-18_V3.0_Comprehensive/Progress_Tracking.md)
- **审查日志**：[Review_Log.md](./2025-12-18_V3.0_Comprehensive/Review_Log.md)

**审查特色**：
- 首次对V3.0版本进行系统性全面审查
- 重点关注V3.0新功能（AI角色库、配置系统、工具库）的集成质量
- 采用分阶段、标准化的审查方法
- 生成详细的改进路线图和问题分析报告

---

*本索引文件将在每次审查完成后更新*