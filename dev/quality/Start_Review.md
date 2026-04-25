# 启动框架审查

本文档是启动 AI Coding Context 框架审查的入口点，包含 AI 助手执行审查所需的全部上下文信息和使用指南。

## 📋 审查指令模板

当你被要求对 AI Coding Context 框架进行审查时，请遵循以下步骤：

### 1. 初始化审查
```bash
# 读取审查入口文档
read_file dev/quality/Start_Review.md

# 读取标准指南
read_file dev/quality/Framework_Review_Guidelines.md

# 读取问题记录标准
read_file dev/quality/Issue_Recording_Standard.md

# 读取进度跟踪标准
read_file dev/quality/Progress_Tracking_Standard.md
```

### 2. 确定审查参数
根据用户提供的审查要求，确定以下参数：
- **审查日期**：当前日期，格式为 YYYY-MM-DD
- **框架版本**：V3.0（当前稳定版）
- **审查范围**：
  - Comprehensive（全面审查）
  - Strategic（战略式编程合规性审查 - V3.0 重点）
  - P1/P2（特定优化点审查）
  - Component（组件专项审查：如 agents, tools, config, adr 等）
  - Security/Performance（安全/性能专项审查）

### 3. 创建审查目录
```bash
# 创建审查目录（替换 YYYY-MM-DD、Version 和 Scope 为实际值）
mkdir -p dev/quality/audits/YYYY-MM-DD_Version_Scope
```

### 4. 制定专项审查计划
```bash
# 读取框架审查指南（包含专项审查计划模板）
read_file dev/quality/Framework_Review_Guidelines.md

# 基于指南中的模板创建新的专项审查计划
write_file dev/quality/audits/YYYY-MM-DD_Version_Scope/Review_Plan_Specific.md
```

## 📊 审查执行流程

### 准备阶段
1. 创建问题跟踪表 (`Issue_Tracking.md`)
2. 创建审查进度跟踪表 (`Progress_Tracking.md`)
3. 创建审查日志 (`Review_Log.md`)
4. **V3.0 特色准备**：运行 `tools/complexity_scanner.py` 获取基准数据

### 💡 效率建议：子代理委派 (Sub-agents)
在审查大型或复杂组件时，应优先委派子代理以节省主上下文：
- **批量合规性检查**：委派 `generalist` 遍历 `tools/` 或 `docs/`，检查双版本对称性、零依赖约束及 YAML 摘要。
- **架构一致性审计**：委派 `codebase_investigator` 分析代码依赖图，验证是否符合 ADR 记录。
- **规则集成验证**：委派 `generalist` 模拟 IDE 加载 `AI_RULES.md`，检测规则冲突。

### 执行阶段
1. 按照 `Framework_Review_Guidelines.md` 执行各项审查活动
2. **战略式合规性检查**：验证 ADR、Commit-Guided 流程是否得到执行
3. **技术质量检查**：验证脚本工具是否符合双版本（Py/JS）且零依赖要求
4. 实时记录问题并每日更新审查日志

### 报告阶段
1. 生成全面审查报告
2. 进行问题分析和统计
3. 创建改进路线图和复查清单

### 归档阶段
1. 更新审查状态
2. 完成所有交付物归档
3. 更新 `dev/quality/README.md` 的审查历史

## 🚀 快速启动代码示例

如果你是 AI 助手，收到审查指令后，可以参考以下逻辑（路径以项目根目录为准）：

```python
# 1. 确定审查参数
review_date = "2026-04-17"
version = "V3.0"
scope = "Comprehensive"

# 2. 创建目录
review_dir = f"dev/quality/audits/{review_date}_{version}_{scope}"

# 3. 初始化文件（基于模板）
# ... 逻辑执行 ...
```

## 📝 审查请求示例

1. "请对 V3.0 版本进行战略式编程合规性专项审查"
   - 解析：范围=Strategic，重点检查 ADR、设计思维引导和 Commit 驱动同步。

2. "检查 V3.0 实用工具库的脚本规范"
   - 解析：范围=Component，重点检查 `tools/` 目录下的双脚本实现与零依赖约束。

## ⚠️ 重要注意事项

1. **排除 dev 目录**：审查时应跳过 `dev/` 目录下的开发中文件（除本审查文档目录外）。
2. **路径准确性**：使用相对于项目根目录的路径，严禁使用硬编码绝对路径。
3. **V3.0 核心约束**：必须验证“双脚本模式”和“架构探针（ADR）”的集成有效性。
4. **证据链**：所有发现的问题应附带代码片段或文档路径作为证据。

---

**文档版本**：1.1  
**更新日期**：2026-04-17  
**状态**：就绪（已适配 V3.0）