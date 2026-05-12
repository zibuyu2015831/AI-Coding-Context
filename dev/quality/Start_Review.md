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
- **框架版本**：V2.3 稳定版 + V3.0（P0 完成、P1 进行中）
- **审查范围**：
  - Comprehensive（全面审查）
  - Strategic（战略式编程合规性审查 - V3.0 重点）
  - P1/P2（特定优化点审查）
  - Component（组件专项审查：如 agents, tools, config, adr 等）
  - Security/Performance（安全/性能专项审查）
- **审核视角**（v1.2 起必填）：
  - A 用户视角（仅 Public 层）
  - B 完整性视角（Public + dev/）
  - C dev/ 卫生视角（仅 dev/）
  - Comprehensive round 默认 A+B+C 全部，专项审查可省略部分但需在 Review_Plan 显式声明

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

在审查大型或复杂组件时，应优先委派子代理以节省主上下文。可用的角色分两类：

**A. AICC 内置 runtime 角色**（位于 `agents/runtime/`）：
- **深度代码审查**：委派 `code_reviewer.md` 评估代码质量、重构建议
- **安全红线检查**：委派 `security_auditor.md` 验证 `core/security_rules.md` 的执行
- **文档-代码一致性**：委派 `understanding_guardian.md` 抽样验证文档对实现的描述
- **Commit 历史审计**：委派 `commit_analyst.md` 验证 Commit-Guided Documentation (018) 是否真实运行
- **架构审计**：委派 `agents/development/architecture_analyst.md` 对比代码依赖图与 `dev/architecture/decisions/` 中的 ADR

**B. 宿主 IDE 通用子代理**（Claude Code Explore / Cursor Search 等）：
- **批量合规性扫描**：遍历 `tools/py/` 与 `tools/js/`，检查双版本对称性、零依赖约束、头部 docstring
- **YAML 摘要扫描**：扫描所有 Markdown 文件验证 `core/SUMMARY_FORMAT_SPEC.md` 合规性
- **死链/悬空引用扫描**：全仓库 grep 失效引用
- **AI_RULES 加载模拟**：评估 `templates/AI_RULES_TEMPLATE.md` 在 IDE 环境中的提示质量

详见 [Framework_Review_Guidelines.md §子代理委派策略](./Framework_Review_Guidelines.md#子代理委派策略-sub-agents-strategy)。

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

1. **视角驱动而非排除驱动**：v1.2 起不再统一"排除 dev/"，按所选视角决定可见范围（详见 Framework_Review_Guidelines.md §审核视角分层）。
2. **路径准确性**：使用相对于项目根目录的路径，严禁使用硬编码绝对路径。
3. **V3.0 核心约束**：必须验证"双脚本模式"和"架构探针（ADR）"的集成有效性。
4. **证据链**：所有发现的问题应附带代码片段或文档路径作为证据，并标注归属视角。
5. **基线快照先行**：制定 Review_Plan 前，应先做一次基线快照（实际文件清单、当前 dev/V3.0/PROGRESS 状态、recent commits），避免计划与现实脱节。

---

**文档版本**：1.2
**更新日期**：2026-04-25
**v1.2 变更**：对齐 Framework_Review_Guidelines v1.2 的三视角分层；修正 sub-agent 名称（generalist/codebase_investigator → 实际 agents/runtime/ 角色）；新增"基线快照先行"原则
**状态**：就绪（已适配 V3.0+ 与三视角审查模型）
