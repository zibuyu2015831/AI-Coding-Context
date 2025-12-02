# AI Rules - [项目名称]

> **用途**: 项目级 AI 规则，在 IDE 中配置后每次 AI 交互都会自动应用  
> **生成时间**: YYYY-MM-DD  
> **最后更新**: YYYY-MM-DD  
> **对应文档**: `dev_docs/AI_Coding_Context.md`

---

## 📚 文档体系入口

**主文档**: `dev_docs/AI_Coding_Context.md`  
开始任何工作前，请先阅读此文档了解项目全貌。

---

## 🎯 核心规范（必须遵守）

### 1. [技术栈]规范

- **语言**: [主要编程语言+版本]
- **框架**: [主要框架+版本]
- **包管理**: [npm/pip/maven 等]

### 2. API 调用规范

- [具体规范，例如: 使用`src/api/`下的封装，禁止直接使用 axios]
- 详见 → `dev_docs/api_layer.md`

### 3. 状态管理规范

- [具体规范，例如: 使用 Pinia，store 命名`use[Name]Store`]
- 详见 → `dev_docs/state_management.md`

### 4. 组件/模块开发规范

- [具体规范，例如: Composition API + TypeScript]
- 详见 → `dev_docs/component_guide.md`

### 5. 错误处理规范

- [具体规范，例如: 统一使用`useErrorHandler`]
- 详见 → `dev_docs/error_handling.md`

### 6. 命名规范

- **文件**: [kebab-case/snake_case/camelCase]
- **组件/类**: [PascalCase/camelCase]
- **函数/方法**: [camelCase/snake_case]
- **常量**: [UPPER_SNAKE_CASE]

---

## 🚦 文档阅读触发器

**根据任务类型，自动阅读对应文档**:

| 任务类型     | 阅读文档                              | 时机               |
| ------------ | ------------------------------------- | ------------------ |
| API 调用相关 | `dev_docs/api_layer.md`               | 编写 API 调用前    |
| 状态管理相关 | `dev_docs/state_management.md`        | 使用 store 前      |
| 组件开发相关 | `dev_docs/component_guide.md`         | 创建组件前         |
| 路由配置相关 | `dev_docs/routing_guide.md`           | 修改路由前         |
| 样式编写相关 | `dev_docs/styling_guide.md`           | 编写样式前         |
| 表单处理相关 | `dev_docs/form_validation.md`         | 处理表单前         |
| 遇到复杂问题 | `dev_docs/knowledge/troubleshooting/` | 问题无法快速解决时 |
| 性能优化相关 | `dev_docs/knowledge/performance/`     | 优化性能时         |

---

## 🤖 Agent 自动推荐规则

**当检测到以下场景时，AI 应主动向用户推荐使用对应的专业角色**:

| 场景           | 推荐角色                | 触发关键词                            |
| -------------- | ----------------------- | ------------------------------------- |
| **方案审查**   | `plan_reviewer`         | "审查方案", "review plan", "设计评审" |
| **代码审查**   | `code_reviewer`         | "审查代码", "review code", "CR"       |
| **测试生成**   | `test_engineer`         | "写测试", "生成用例", "test case"     |
| **性能优化**   | `performance_optimizer` | "优化性能", "太慢了", "optimize"      |
| **安全检查**   | `security_auditor`      | "安全检查", "漏洞", "security"        |
| **架构设计**   | `architecture_analyst`  | "设计架构", "新增模块", "重构"        |
| **数据库设计** | `database_designer`     | "建表", "设计数据库", "ER 图"         |
| **API 设计**   | `api_designer`          | "设计接口", "API 定义", "RESTful"     |

**推荐话术**:

> "检测到您正在进行[场景]，建议使用 **[角色名]** (agents/runtime/[角色名].md) 来辅助完成此任务，它拥有更专业的检查清单和输出规范。"

---

## 🔄 工作流程规范

### 新功能开发

1. **先创建方案**: `dev_docs/plans/features/YYYY-MM-DD_功能描述.md`
2. **等待用户审核** - 方案通过后再开始编码
3. **按规范实施** - 参考对应的子文档
4. **完成后沉淀** - 提取关键要点到`dev_docs/knowledge/`

### Bug 修复

1. **先创建方案**: `dev_docs/plans/bugfixes/YYYY-MM-DD_bug描述.md`（复杂 bug）
2. **分析根因** - 检查`dev_docs/knowledge/troubleshooting/`
3. **按规范修复** - 遵守项目规范
4. **记录经验** - 难题沉淀到 knowledge/

### 代码修改

1. **识别影响范围** - 确定涉及哪些模块
2. **阅读相关文档** - 根据触发器阅读对应文档
3. **遵守规范修改** - 保持一致性
4. **更新文档**（如有必要） - 保持文档与代码同步

---

## 🛡️ AI 互审机制 (v3.0)

**所有方案生成任务必须遵守以下互审规则**:

### 1. 指令识别

- **`@review:skip`**: 跳过审查，直接输出方案
- **`@review:standard`**: 强制执行 1 轮标准审查
- **`@review:deep`**: 强制执行 2 轮深度审查
- **`@urgent`**: 紧急模式，跳过审查但标记为未审核

### 2. 方案元数据 (必需)

生成方案时，必须在 Frontmatter 中包含以下元数据：

```yaml
plan_metadata:
  reliability: [0-100] # 可靠度自评
  complexity_score: [0-100] # 复杂度分数
  risk_level: [low/medium/high]
  breaking_change: [true/false]
```

### 3. 审核报告元数据 (必需)

生成审核报告时，必须在 Frontmatter 中包含以下元数据：

```yaml
review_metadata:
  improvement_potential: [0-100] # 提升潜力
  confidence_level: [0.0-1.0] # 置信度
  p0_issues: [count] # P0问题数量
  has_controversial_suggestions: [true/false] # 是否有争议
```

### 4. 自动审查逻辑

- 若用户未指定指令，根据**复杂度**自动决定审查模式
- 若方案可靠度 < 60 或 审查提升度 ≥ 20，**自动触发优化**
- 详细逻辑参考: `workflows/013-review-workflow.md`

---

## 🧠 设计思维引导规则 (v3.0)

**重要功能或架构设计任务必须遵守以下设计思维引导规则**:

### 1. 触发条件

**自动触发** (基于复杂度评估):

- **复杂度 ≥ 60 分**: 主动提议启动设计思维引导
  - 涉及核心模块 (Auth, Payment, Order 等)
  - 架构重构或技术栈变更
  - 关键技术选型 (数据库、缓存方案等)
- **复杂度 < 60 分**: 默认跳过
- **Trivial 任务** (Fix typo, 调整样式): 强制跳过

**用户显式指令** (优先级高于自动判断):

- `@think` / `@think:standard`: 启动标准引导 (完整 5 步)
- `@think:deep`: 启动深度辩论 (多轮专家对话)
- `@think:quick`: 快速对齐 (仅确认目标、方案、验收)
- `@think:skip`: 强制跳过引导

### 2. 必须遵守的引導流程

当触发设计思维引导时,AI 必须按以下 5 步流程进行:

**Step 1 - 问题本质 (ProductManager)**:

- 通过 5 Why 分析挖掘业务价值
- 明确目标用户和使用场景
- 定义初步成功标准

**Step 2 - 方案探索 (ArchitectureAnalyst)**:

- 提出 **至少 2-3 种** 可行方案
- 进行优缺点对比分析
- 明确边界 (做什么/不做什么)

**Step 3 - 风险与测试 (Architect & QA)**:

- 识别主要技术风险并给出应对措施
- 制定测试策略和验收标准

**Step 4 - 反思与整合 (Facilitator)**:

- 全局反思,识别知识空白和观点冲突
- 若发现问题,回溯到 Step 2 深化分析

**Step 5 - 最终决策 (Facilitator)**:

- 输出结构化决策方案
- 包含: 背景、推荐方案、风险、验收标准、下一步行动

### 3. 禁止行为

- ❌ **禁止直接跳到代码**: 未经设计思维引导流程,不得直接输出代码实现
- ❌ **禁止单一方案**: Step 2 必须提供多方案对比,不得只给一个方案
- ❌ **禁止忽略风险**: 必须识别并应对主要技术风险
- ❌ **禁止模糊的验收标准**: 验收标准必须具体可测试

### 4. 输出格式要求

最终决策方案必须包含以下章节:

```markdown
## 1. 背景与目标

- 业务价值
- 核心需求
- 目标用户与使用场景

## 2. 技术方案

- 推荐方案 (技术选型 + 关键设计点)
- 备选方案 (如适用)

## 3. 实现边界

- 本次实现
- 本次不实现

## 4. 风险与应对

| 风险 | 影响 | 应对措施 |

## 5. 验收标准

- 功能性标准
- 非功能性标准 (性能、安全、可用性)

## 6. 下一步行动
```

### 5. 配置参考

用户可在 `config/user_config.md` 中配置设计思维引导行为:

- `auto_trigger_threshold`: 自动触发阈值 (默认 60)
- `default_mode`: 默认模式 (standard/deep/quick)
- `skip_trivial_tasks`: 是否跳过简单任务 (默认 true)

详细说明: `config/CONFIG_TEMPLATE.md` 设计思维引导章节

---

## ⚠️ 禁止事项

1. ❌ **不要臆测规范** - 不确定时先阅读文档或询问用户
2. ❌ **不要跳过方案** - 重要功能/修复必须先写方案
3. ❌ **不要直接修改核心配置** - 配置变更需要用户确认
4. ❌ **不要引入新依赖未讨论** - 新依赖需要评估和确认
5. ❌ **不要忽略错误处理** - 所有 API 调用都要处理错误
6. ❌ **不要使用占位符** - 代码示例必须完整可用

---

## 💡 最佳实践

1. ✅ **优先查阅 knowledge/** - 类似问题可能已有解决方案
2. ✅ **保持代码一致性** - 遵循现有代码风格
3. ✅ **完善的错误提示** - 用户友好的错误信息
4. ✅ **注释关键逻辑** - 复杂逻辑必须注释
5. ✅ **及时更新文档** - 规范变更时同步更新

---

## 🔧 特殊场景处理

### 多租户/多品牌（如适用）

- [特殊处理规则]
- 详见 → `dev_docs/[相关文档]`

### 实时通讯（如适用）

- [WebSocket/SSE 等规则]
- 详见 → `dev_docs/[相关文档]`

### 国际化（如适用）

- [i18n 规则]
- 详见 → `dev_docs/[相关文档]`

---

## 📅 Rule 更新触发条件

**何时需要更新此 Rule 文件**:

1. 技术栈升级（框架、语言版本变更）
2. 核心规范调整（API 调用方式、状态管理方案变更）
3. 新增重要子文档
4. 命名规范变更
5. 开发流程调整

**更新流程**:

1. AI 生成更新后的 rule 到`dev_docs/AI_RULES.md`
2. 提醒用户手动更新 IDE 的 rule 配置
3. 记录更新日期

---

## 🎓 使用说明

### 如何在 IDE 中配置

**Cursor**:

1. 将此文件内容复制到项目根目录的`.cursorrules`文件
2. 重启 Cursor 或重新加载项目

**Windsurf**:

1. 在项目设置中找到"Custom Rules"
2. 粘贴此文件内容
3. 保存配置

**VS Code + GitHub Copilot**:

1. 在`.vscode/settings.json`中配置
2. 或使用 workspace settings

**其他 IDE**:

- 参考 IDE 文档配置项目级 AI 规则
- 本质是让 AI 在每次交互时都读取这些规则

---

**最后更新**: YYYY-MM-DD
