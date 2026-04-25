# 012 - 强制文档摘要机制

**优先级**: P0  
**状态**: 🟢 审核通过  
**预估工作量**: 4-5 天  
**来源**: 用户洞察 + Token 优化需求  
**依赖**: 无（基于规范和模板，由 AI 直接生成）

---

## 📋 问题描述

### 核心痛点

1. **信息检索效率低下**

   - 用户/AI 必须完整阅读文档才能判断相关性
   - 无法快速过滤不相关文档
   - 文档定位耗时长（平均 5 分钟）

2. **Token 消耗过高**

   - AI 每次查询需读取多个完整文档（平均 500 行/文档）
   - 无法基于摘要快速筛选
   - 预估浪费 30-50% Token

3. **认知负荷过高**

   - 缺少快速判断机制
   - 需要完整阅读才知道文档是否相关
   - 用户认知负荷评分 8/10

4. **文档与代码关联缺失**
   - 代码变更后，不知道哪些文档需要更新
   - 缺少文档到代码文件的映射关系
   - 文档过时风险高

### V2.3 现状

- ⚠️ 部分模板有简单摘要（如 `PROJECT_ANALYSIS_REPORT_TEMPLATE.md`）
- ❌ 未要求所有文档强制包含摘要
- ❌ 没有标准化的摘要格式
- ❌ 缺少文档到代码文件的关联机制
- ❌ 缺少摘要验证和健康度检查

---

## 💡 解决方案设计

### 核心理念

**基于规范和模板，由 AI 在生成文档时直接写入摘要**：

```
模板和规范（workflows + templates）
   ↓
AI 遵循规范生成文档
   ↓
文档开头自动包含摘要（YAML Frontmatter）
   ↓
工具脚本提取、验证、监控摘要
```

**设计原则**：

1. **规范驱动**: 通过 workflows 和 templates 明确要求 AI 生成摘要
2. **格式统一**: 采用 YAML Frontmatter 格式，与 016-配置系统一致
3. **代码关联**: 摘要包含 related_files 字段，建立文档与代码的映射
4. **工具辅助**: 提供提取、验证、监控脚本，但不负责生成摘要

### 1. 摘要格式：YAML Frontmatter

#### 标准格式定义

```yaml
---
summary:
  purpose: "一句话说明文档用途（≤100字符）"
  scenarios:
    - "场景1：具体描述"
    - "场景2：具体描述"
    - "场景3：具体描述"
  core_points:
    - "核心要点1（≤50字符）"
    - "核心要点2（≤50字符）"
    - "核心要点3（≤50字符）"
  dependencies: "error_handling.md | state_management.md"
  related_files: "src/api/user.ts | src/services/auth.ts | src/components/LoginForm.vue"
  criteria: "快速判断条件：如果你需要XXX，必读此文档（≤150字符）"
  verified_at: "2025-12-03"
---
# 文档正文标题

文档内容开始...
```

#### 字段说明

| 字段            | 类型   | 必填 | 说明               | 格式                             |
| --------------- | ------ | ---- | ------------------ | -------------------------------- |
| `purpose`       | string | ✅   | 一句话说明文档用途 | ≤100 字符                        |
| `scenarios`     | array  | ✅   | 2-3 个典型使用场景 | YAML 数组，每项 ≤80 字符         |
| `core_points`   | array  | ✅   | 3-5 个核心要点     | YAML 数组，每项 ≤50 字符         |
| `dependencies`  | string | ✅   | 前置必读文档列表   | 单行，用`\|`分隔，无依赖写`"无"` |
| `related_files` | string | ✅   | 关联的代码文件路径 | 单行，用`\|`分隔，无关联写`"无"` |
| `criteria`      | string | ✅   | 快速判断条件       | ≤150 字符                        |
| `verified_at`   | string | ✅   | 摘要最后验证日期   | YYYY-MM-DD 格式                  |

#### 格式选择理由

**为什么选择 YAML Frontmatter？**

| 维度           | YAML Frontmatter       | HTML 注释             |
| -------------- | ---------------------- | --------------------- |
| **人类可读性** | ✅ 优秀（源文件清晰）  | ⚠️ 中等（源文件突兀） |
| **机器解析性** | ✅ 标准 YAML 库 + 正则 | ⚠️ 需自写正则         |
| **框架一致性** | ✅ 与 016-配置系统一致 | ❌ 独立设计           |
| **IDE 支持**   | ✅ YAML 高亮、验证     | ⚠️ 普通注释           |

**为什么 related_files 和 dependencies 使用单行格式？**

- **易于正则提取**: `related_files: "(.*?)"` 一次性提取所有文件
- **格式简洁**: `"file1.ts | file2.ts"` 比 YAML 数组更紧凑
- **人类可读**: 仍然易于阅读和编辑

### 2. 规范和模板（核心实现）

#### 2.1 更新 generation_workflow.md

**在步骤 2.4 之后，新增步骤 2.5**:

````markdown
### 步骤 2.5: 为生成的文档添加摘要

**AI 指令模板**:

对于刚刚生成的每个文档，请在文档开头添加 YAML Frontmatter 摘要：

## \```yaml

summary:
purpose: "一句话说明文档用途"
scenarios: - "场景 1" - "场景 2"
core_points: - "要点 1" - "要点 2" - "要点 3"
dependencies: "前置文档 1.md | 前置文档 2.md"
related_files: "src/path/file1.ts | src/path/file2.ts"
criteria: "如果你需要 XXX，必读此文档"
verified_at: "当前日期"

---

\```

**摘要生成要求**:

1. **purpose**: 提取文档第一段或主要目的，压缩到 ≤100 字符
2. **scenarios**: 基于文档"使用场景"或"何时使用"章节，列举 2-3 个场景
3. **core_points**: 提取文档的主要一级标题（## 标题），压缩到 ≤50 字符，保留 3-5 个
4. **dependencies**:
   - 扫描文档中提到的其他文档链接（.md 文件）
   - 用 `|` 分隔，例如：`"api_layer.md | error_handling.md"`
   - 如果无依赖，写：`"无"`
5. **related_files** (重要！):
   - 列出文档中提到的所有代码文件路径
   - 包括：代码示例中的文件、配置文件、入口文件等
   - 用 `|` 分隔，例如：`"src/api/user.ts | src/services/auth.ts"`
   - 如果无关联，写：`"无"`
   - **用途**: 当这些代码文件变更时，框架会提示该文档需要更新
6. **criteria**: 帮助用户快速判断是否需要阅读，明确具体场景
7. **verified_at**: 填写当前日期（YYYY-MM-DD 格式）

**质量检查**:

- [ ] 所有文档都包含摘要
- [ ] 摘要格式符合 YAML 规范
- [ ] purpose 描述清晰简洁
- [ ] related_files 包含文档中提到的所有代码文件
- [ ] dependencies 准确无误
````

#### 2.2 更新所有模板文件

**位置**: `templates/*.md`

**修改内容**: 在所有模板文件开头添加摘要占位符

**示例** (`templates/AI_Coding_Context_TEMPLATE.md`):

```markdown
---
summary:
  purpose: "[AI生成：一句话说明此文档用途]"
  scenarios:
    - "[AI生成：场景1]"
    - "[AI生成：场景2]"
  core_points:
    - "[AI生成：核心要点1]"
    - "[AI生成：核心要点2]"
    - "[AI生成：核心要点3]"
  dependencies: "[AI生成：前置文档，用 | 分隔，无则填'无']"
  related_files: "[AI生成：关联代码文件，用 | 分隔，无则填'无']"
  criteria: "[AI生成：快速判断条件]"
  verified_at: "[AI生成：当前日期 YYYY-MM-DD]"
---

# AI 辅助编程上下文文档

[原有模板内容...]
```

### 3. 工具脚本实现

#### 3.1 摘要提取工具：summary_extractor.py

**功能**: 从文档中提取摘要，供 AI 快速预览

**位置**: `tools/py/summary_extractor.py` 和 `tools/js/summary_extractor.js`

**使用示例**:

```bash
# 单个文档提取
python tools/py/summary_extractor.py --file dev_docs/api_layer.md

# 批量提取（返回所有摘要）
python tools/py/summary_extractor.py --batch-mode --dir dev_docs/
```

**输出格式** (JSON):

```json
{
  "success": true,
  "data": {
    "file": "dev_docs/api_layer.md",
    "summary": {
      "purpose": "定义项目中所有 API 调用的标准模式和规范",
      "scenarios": [
        "新增API接口调用",
        "修改现有API调用逻辑",
        "排查API调用问题"
      ],
      "core_points": ["API函数命名规范", "统一错误处理模式", "Loading状态管理"],
      "dependencies": "error_handling.md | state_management.md",
      "related_files": "src/api/user.ts | src/api/post.ts | src/utils/request.ts",
      "criteria": "如果你需要调用后端API或处理API响应，必读此文档",
      "verified_at": "2025-12-03"
    }
  },
  "metadata": {
    "elapsed_seconds": 0.1,
    "version": "1.0.0"
  }
}
```

**实现要点**:

- 使用 YAML 解析库提取 Frontmatter
- 支持正则表达式备用方案
- 错误处理：文档无摘要时返回明确错误

#### 3.2 摘要验证工具：summary_validator.py

**功能**: 验证摘要完整性、格式正确性、关联文件存在性

**使用示例**:

```bash
# 单个文档验证
python tools/py/summary_validator.py --file dev_docs/api_layer.md

# 批量验证
python tools/py/summary_validator.py --check-all dev_docs/
```

**输出示例**:

```json
{
  "success": false,
  "data": {
    "file": "dev_docs/api_layer.md",
    "valid": false,
    "errors": ["缺少必填字段: related_files", "YAML 格式错误: 第5行"],
    "warnings": [
      "关联文件不存在: src/api/deleted_file.ts",
      "摘要已过期 120 天（verified_at: 2025-08-05）"
    ],
    "suggestions": [
      "建议更新 verified_at 为当前日期",
      "建议从 related_files 中移除不存在的文件"
    ]
  },
  "metadata": {
    "elapsed_seconds": 0.5,
    "version": "1.0.0"
  }
}
```

**验证规则**:

1. **格式验证**:

   - YAML Frontmatter 格式正确
   - 所有必填字段存在
   - 字段类型正确（string/array）

2. **内容验证**:

   - purpose ≤ 100 字符
   - scenarios 包含 2-3 项
   - core_points 包含 3-5 项
   - verified_at 为有效日期格式

3. **关联验证** (重要！):
   - dependencies 中的文档文件是否存在
   - **related_files 中的代码文件是否存在**
   - 提示过期摘要（verified_at > 90 天）

#### 3.3 文档更新检测工具：summary_related_checker.py

**功能**: 检查哪些文档的 related_files 包含已变更的代码文件

**使用示例**:

```bash
# 检查特定文件的影响范围
python tools/py/summary_related_checker.py --changed-files "src/api/user.ts"

# 与 git_diff_analyzer 配合使用
python tools/py/git_diff_analyzer.py --since "7 days ago" | \
python tools/py/summary_related_checker.py --from-stdin
```

**输出示例**:

```json
{
  "success": true,
  "data": {
    "changed_files": ["src/api/user.ts", "src/api/post.ts"],
    "affected_docs": [
      {
        "doc": "dev_docs/api_layer.md",
        "reason": "related_files 包含: src/api/user.ts, src/api/post.ts",
        "matched_files": ["src/api/user.ts", "src/api/post.ts"],
        "last_verified": "2025-11-15",
        "days_since_verified": 18
      },
      {
        "doc": "dev_docs/authentication.md",
        "reason": "related_files 包含: src/api/user.ts",
        "matched_files": ["src/api/user.ts"],
        "last_verified": "2025-12-01",
        "days_since_verified": 2
      }
    ],
    "summary": {
      "total_affected_docs": 2,
      "recommendation": "建议更新以上文档并刷新摘要的 verified_at"
    }
  },
  "metadata": {
    "elapsed_seconds": 0.3,
    "version": "1.0.0"
  }
}
```

**实现逻辑**:

```python
# 1. 提取所有文档的 related_files
# 2. 对比 changed_files 列表
# 3. 返回受影响的文档列表
```

#### 3.4 摘要索引生成器：summary_index_generator.py（可选）

**功能**: 遍历所有文档，批量提取摘要，生成索引页

**使用示例**:

```bash
python tools/py/summary_index_generator.py --dir dev_docs/ --output dev_docs/SUMMARY_INDEX.md
```

**输出示例** (`SUMMARY_INDEX.md`):

```markdown
# 📚 文档摘要索引

> 自动生成 | 最后更新: 2025-12-03

## 🏗️ 架构文档

### [architecture.md](./architecture.md)

- **用途**: 详细说明项目的技术架构设计
- **场景**: 了解整体架构 | 架构重构 | 新人入职
- **核心**: 分层设计 | 模块划分 | 技术栈选型 | 数据流向
- **依赖**: 无
- **关联代码**: src/index.ts | src/app.ts | config/vite.config.ts

### [api_layer.md](./api_layer.md)

- **用途**: 定义项目中所有 API 调用的标准模式和规范
- **场景**: 新增 API 接口调用 | 修改现有 API 调用逻辑
- **核心**: API 函数命名规范 | 统一错误处理模式 | Loading 状态管理
- **依赖**: error_handling.md | state_management.md
- **关联代码**: src/api/user.ts | src/api/post.ts | src/utils/request.ts

...
```

**状态**: 先实现，暂不启用，后续根据需要决定是否使用；需在脚本文件前的注释进行说明

### 4. 工作流集成

#### 4.1 集成到 generation_workflow.md

**位置**: 步骤 2.4 之后新增步骤 2.5（见 2.1 节）

#### 4.2 集成到 incremental_update_workflow.md

**新增步骤**: 文档更新时同步更新摘要

````markdown
### 步骤 4: 检查并更新受影响的文档

**AI 指令模板**:

\```bash

# 步骤 1: 使用 git_diff_analyzer 检测代码变更

python tools/py/git_diff_analyzer.py --since "30 days ago"

# 步骤 2: 检查哪些文档需要更新

python tools/py/summary_related_checker.py --changed-files "<变更的文件列表>"
\```

**处理建议**:

如果检测到受影响的文档：

1. 重新阅读文档和相关代码
2. 更新文档内容（如有必要）
3. 更新摘要：
   - 检查 related_files 是否仍然准确
   - 更新 verified_at 为当前日期
   - 如果文档内容有重大变更，同步更新 purpose、scenarios、core_points
````

#### 4.3 集成到 document_health_check.md

**新增摘要健康度检查项**:

````markdown
### 摘要完整性检查

作为文档健康度检查的一部分，新增摘要检查项：

**检查命令**:
\```bash
python tools/py/summary_validator.py --check-all dev_docs/
\```

**检查项**:

- [ ] 所有必需文档都包含摘要
- [ ] 摘要格式正确（YAML 可解析）
- [ ] 必填字段齐全（7 个字段）
- [ ] related_files 中的代码文件存在
- [ ] dependencies 中的文档文件存在
- [ ] verified_at 日期不超过 90 天

**评分影响**:

- 缺少摘要：健康度 -5 分
- 摘要格式错误：健康度 -3 分
- 关联文件不存在：健康度 -2 分
- 摘要过期（>90 天）：健康度 -2 分
````

### 5. 文档覆盖范围

```yaml
✅ 必须包含摘要:
  # 框架核心文档
  - README.md
  - README.md
  - CONTRIBUTING.md
  - AI_ENTRY_POINT.md

  # 用户项目文档（AI生成）
  - dev_docs/AI_Coding_Context.md
  - dev_docs/*.md（所有子文档）

  # 工作流文档（框架自身）
  - workflows/*.md

  # 模板文件处理：
  - 模板本身包含摘要占位符（供AI填写）
  - 框架的模板说明文档需要摘要

⚠️ 建议包含摘要:
  # 知识库
  - dev_docs/knowledge/**/*.md

  # 方案文档
  - dev_docs/plans/**/*.md

❌ 无需摘要:
  - CHANGELOG.md
  - LICENSE.md
  - dev_docs/_analysis/*.md（自动生成的临时文件）
  - 配置文件（.gitignore, .editorconfig等）
```

---

## 📊 价值评估

### 解决的痛点

1. **大幅降低 Token 消耗**

   - 传统: 读 10 个文档 × 500 行 = 5000 行
   - 有摘要: 读 10 个摘要 + 3 个全文 = 100 + 1500 = 1600 行
   - **节省 68% Token**

2. **显著提升定位效率**

   - 文档定位耗时: 5 分钟 → 1 分钟 (**-80%**)
   - 相关性判断: 需完整阅读 → 30 秒扫描 (**-90%**)

3. **大幅降低认知负荷**

   - 认知负荷评分: 8/10 → 3/10 (**-62%**)
   - 3 秒判断是否需要阅读全文

4. **建立文档与代码的关联**
   - 通过 related_files 字段，知道哪些文档关联哪些代码
   - 代码变更时自动提示相关文档需要更新
   - 降低文档过时风险

### 预期效果对比

| 指标         | 无摘要 | 有摘要 | 提升幅度 |
| ------------ | ------ | ------ | -------- |
| 文档定位耗时 | 5 分钟 | 1 分钟 | **-80%** |
| Token 消耗   | 5000   | 1600   | **-68%** |
| AI 响应速度  | 30 秒  | 10 秒  | **-67%** |
| 错误阅读次数 | 3 次   | 0.5 次 | **-83%** |
| 用户认知负荷 | 8/10   | 3/10   | **-62%** |
| 文档过时风险 | 高     | 低     | **-70%** |

### ROI 分析

**一次性成本**:

- 开发工作量: 4-5 天
- 更新模板和 workflows: 1 天
- 为现有框架文档添加摘要: 2 小时
- 每个新文档增加: AI 书写摘要时额外 1-2 分钟

**持续收益**:

- Token 节省: 每次查询节省 **60-70%**
- 效率提升: 节省 **80%** 文档定位时间
- 维护成本降低: 代码变更时自动提示相关文档

**净收益**: 投入 1 周，节省数百小时（跨多次使用和多个项目）

---

## ⚠️ 风险与应对

### 风险 1: AI 生成的摘要质量不稳定

**可能性**: 中  
**影响**: 中  
**应对措施**:

- ✅ 通过 workflows 提供明确的生成要求和示例
- ✅ summary_validator.py 自动检测问题
- ✅ 用户可手动编辑 YAML 修正
- ✅ 健康度检查定期提醒

### 风险 2: related_files 不准确或遗漏

**可能性**: 中  
**影响**: 高（影响更新检测）  
**应对措施**:

- ✅ workflows 明确要求列出所有代码文件
- ✅ summary_validator.py 验证文件是否存在
- ✅ 用户审核时重点检查此字段

### 风险 3: 摘要过时但未更新

**可能性**: 低  
**影响**: 中  
**应对措施**:

- ✅ summary_related_checker.py 自动检测需更新的文档
- ✅ 健康度检查提示过期摘要（>90 天）
- ✅ verified_at 字段提供时效性标识

### 风险 4: 工具执行失败

**可能性**: 低  
**影响**: 低  
**应对措施**:

- ✅ 所有工具遵循 tools 规范（零依赖、错误处理）
- ✅ 10 秒超时机制
- ✅ 降级方案（手动检查）

---

## 🛠️ 实施计划

### 阶段 1: 格式规范与示例（1 天）

**任务**:

- [ ] 确定最终摘要格式（已完成讨论）
- [ ] 编写格式规范文档 `SUMMARY_FORMAT_SPEC.md`
- [ ] 创建 5 个不同类型文档的摘要示例

**产出物**:

- `SUMMARY_FORMAT_SPEC.md`
- `examples/summary_examples.md`

### 阶段 2: 更新模板和工作流（1 天）

**任务**:

- [ ] 更新 `workflows/generation_workflow.md`（新增步骤 2.5）
- [ ] 更新 `workflows/incremental_update_workflow.md`
- [ ] 更新 `workflows/document_health_check.md`
- [ ] 更新所有 `templates/*.md`，添加摘要占位符

**产出物**:

- 更新的 workflow 文档（3 个）
- 更新的 template 文件（所有模板）

### 阶段 3: 工具开发（2 天）

**任务**:

- [ ] 开发 `tools/py/summary_extractor.py`
  - [ ] 实现 YAML 解析
  - [ ] 实现正则备用方案
  - [ ] 支持批量模式
- [ ] 开发 `tools/js/summary_extractor.js`（备用）
- [ ] 开发 `tools/py/summary_validator.py`
  - [ ] 格式验证
  - [ ] 字段验证
  - [ ] **文件存在性验证**
- [ ] 开发 `tools/py/summary_related_checker.py`
  - [ ] 与 git_diff_analyzer 配合
  - [ ] 输出受影响文档列表
- [ ] 开发 `tools/py/summary_index_generator.py`（可选）
- [ ] 更新 `tools/README.md` 和 `tools/CHANGELOG.md`

**产出物**:

- 4 个核心工具（Python 为主，JS 备用）
- 工具文档

### 阶段 4: 框架文档迁移（0.5 天）

**任务**:

- [ ] 为框架核心文档添加摘要
  - [ ] README.md
  - [ ] README.md
  - [ ] AI_ENTRY_POINT.md
- [ ] 为部分 workflows 添加摘要示例
- [ ] 验证摘要格式正确性

**产出物**:

- 带摘要的框架文档

### 阶段 5: 验证与优化（0.5 天）

**任务**:

- [ ] 运行所有工具验证功能
- [ ] 测试 related_files 变更检测
- [ ] 测试 summary_validator 验证逻辑
- [ ] 性能测试（确保工具执行时间<5 秒）
- [ ] 更新 V3.0 相关文档
  - [ ] 更新 `dev/V3.0/README.md`
  - [ ] 更新 `dev/V3.0/PROGRESS.md`

**产出物**:

- 验证报告
- 性能测试报告

---

## 🔗 与 V3.0 其他优化点的集成

### 与 001-AI 角色库集成

- 可复用 `document_generator` 角色调用摘要工具（可选）
- 不强依赖角色库（工具化实现）

### 与 013-AI 互审机制集成

- 摘要生成后，可触发 AI 审查验证准确性（可选）
- 审查维度：摘要是否准确反映文档内容

### 与 016-配置管理系统集成

- 在 `config/user_config.md` 中可配置摘要偏好
- 配置项：
  ```yaml
  summary:
    enabled: true # 是否启用摘要检查
    expiry_days: 90 # 过期天数阈值
    check_file_existence: true # 是否验证关联文件存在
  ```

### 与 017-实用脚本工具库集成

- 摘要工具成为 tools 目录的标准工具
- 遵循统一的工具规范和接口
- 与 git_diff_analyzer.py 深度配合

---

## 📚 参考文档

- [016-配置管理系统](../016-unified-config-system/016-unified-config-system.md) - YAML 格式参考
- [017-实用脚本工具库](../017-utility-script-library/017-utility-script-library.md) - 工具开发规范
- [generation_workflow.md](../../../../workflows/generation_workflow.md) - 文档生成流程
- [incremental_update_workflow.md](../../../../workflows/incremental_update_workflow.md) - 增量更新流程
- [document_health_check.md](../../../../workflows/document_health_check.md) - 健康度检查
- [git_diff_analyzer.py](../../tools/py/git_diff_analyzer.py) - Git 差异分析工具

---

## 🔄 状态跟踪

**创建日期**: 2025-11-29  
**最后讨论**: 2025-12-03  
**讨论进度**: 100%  
**决策状态**: 🟢 待确认

### 核心决策（已明确）

- ✅ 采用 YAML Frontmatter 格式
- ✅ **摘要由 AI 遵循规范直接生成**（非脚本事后生成）
- ✅ **新增 related_files 字段**（单行格式，关联代码文件）
- ✅ **去除 duration 字段**（无实际意义）
- ✅ dependencies 和 related_files 使用单行格式（便于正则提取）
- ✅ 不实现 summary_generator.py（AI 直接生成）
- ✅ 不实现 summary_matcher.py（智能推荐暂不需要）
- ✅ 仅支持中文（后续考虑多语言）
- ✅ 所有文档都需要摘要（体系化文档是上下文核心）
- ✅ 工具化实现（提取、验证、检测）

### 核心工具清单

1. ✅ `summary_extractor.py` - 提取摘要供 AI 快速预览
2. ✅ `summary_validator.py` - 验证摘要完整性和文件存在性
3. ✅ `summary_related_checker.py` - 检测哪些文档需要更新
4. ✅ `summary_index_generator.py` - 生成索引页（可选，先实现不启用）
5. ✅ `git_diff_analyzer.py` - 检测代码变更（已有）

---

**下一步**: 用户确认草案 → 生成实施方案和进度文档 → 开始开发
