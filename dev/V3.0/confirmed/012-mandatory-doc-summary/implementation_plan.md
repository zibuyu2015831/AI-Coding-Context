# 012-强制文档摘要机制 实施方案

**优先级**: P0  
**预估工作量**: 4-5 天  
**开始日期**: TBD  
**负责人**: TBD  
**当前状态**: 🟢 已确认，待实施

---

## 📋 实施目标

为框架建立标准化的文档摘要机制，通过 YAML Frontmatter 格式在所有文档开头添加摘要，实现：

1. 快速判断文档相关性（节省 68% Token）
2. 建立文档与代码的关联（通过 related_files 字段）
3. 自动检测需要更新的文档（代码变更时）
4. 提供摘要提取、验证和监控工具

---

## 🎯 核心产出物

### 文档类

1. **格式规范文档**

   - `reference/SUMMARY_FORMAT_SPEC.md`（框架 reference/ 目录）
   - 详细说明摘要格式、字段要求、示例
   - 与现有的 `framework_spec.md` 和 `design_decisions.md` 同级

2. **摘要示例集**
   - `reference/examples/summary_examples/`（reference/ 下的子目录）
   - 包含 5 种不同类型文档的摘要示例
   - 每个示例单独一个 .md 文件

### 工具类

> **开发规范**: 所有工具必须严格遵循 `tools/README.md` 中定义的脚本开发规范

1. **摘要提取工具**

   - `tools/py/summary_extractor.py`
   - `tools/js/summary_extractor.js`
   - 从文档提取摘要供 AI 快速预览
   - 遵循零依赖、JSON 输出、超时机制等规范

2. **摘要验证工具**

   - `tools/py/summary_validator.py`
   - `tools/js/summary_validator.js`
   - 验证格式、必填字段、文件存在性
   - 遵循统一错误处理格式

3. **文档更新检测工具**

   - `tools/py/summary_related_checker.py`
   - `tools/js/summary_related_checker.js`
   - 检测哪些文档的 related_files 包含已变更的代码
   - 与 git_diff_analyzer.py 接口兼容

4. **摘要索引生成器（可选）**
   - `tools/py/summary_index_generator.py`
   - `tools/js/summary_index_generator.js`
   - 生成文档摘要索引页（暂不启用）
   - 在脚本注释中说明暂不启用

### 更新的文档

1. **工作流文档**

   - `workflows/generation_workflow.md` - 新增步骤 2.5（摘要生成规范）
   - `workflows/incremental_update_workflow.md` - 新增文档更新检测步骤
   - `workflows/document_health_check.md` - 新增摘要健康度检查

2. **模板文件**

   - 所有 `templates/*.md` - 添加摘要 YAML Frontmatter 占位符

3. **工具文档**

   - `tools/README.md` - 新增 4 个工具说明
   - `tools/CHANGELOG.md` - 记录工具新增

4. **框架核心文档**（示范）
   - `README.md` - 添加摘要
   - `README.md` - 添加摘要
   - `AI_ENTRY_POINT.md` - 添加摘要

---

## 📅 实施计划

### 阶段 1: 格式规范与示例（1 天）

**任务**:

- [ ] 创建框架文档目录 `reference/`（如果不存在）
- [ ] 编写 `reference/SUMMARY_FORMAT_SPEC.md`
  - [ ] 详细说明 7 个字段定义
  - [ ] 提供字段填写指南
  - [ ] 说明 related_files 的提取规则
- [ ] 创建示例目录 `reference/examples/summary_examples/`
- [ ] 创建 5 个示例文档
  - [ ] `architecture_doc_example.md` - 架构文档示例
  - [ ] `api_doc_example.md` - API 文档示例
  - [ ] `workflow_doc_example.md` - 工作流文档示例
  - [ ] `config_doc_example.md` - 配置文档示例
  - [ ] `tool_doc_example.md` - 工具文档示例

**产出物**:

- [ ] `reference/SUMMARY_FORMAT_SPEC.md`
- [ ] `reference/examples/summary_examples/` 目录（5 个示例文件）

**验收标准**:

- ✅ 格式规范清晰易懂
- ✅ 示例覆盖主要文档类型
- ✅ related_files 格式明确（单行，`|` 分隔）

---

### 阶段 2: 更新模板和工作流（1 天）

**任务**:

- [ ] 更新 `workflows/generation_workflow.md`
  - [ ] 在步骤 2.4 后新增步骤 2.5
  - [ ] 详细说明摘要生成要求
  - [ ] 提供 AI 指令模板
  - [ ] 说明 related_files 的重要性
- [ ] 更新 `workflows/incremental_update_workflow.md`
  - [ ] 新增步骤：检查文档更新
  - [ ] 集成 git_diff_analyzer + summary_related_checker
  - [ ] 说明摘要更新策略
- [ ] 更新 `workflows/document_health_check.md`
  - [ ] 新增摘要完整性检查项
  - [ ] 定义评分影响（-5 to -2 分）
- [ ] 更新所有 `templates/*.md`
  - [ ] 添加 YAML Frontmatter 占位符
  - [ ] 包含所有 7 个字段
  - [ ] 示例格式正确

**产出物**:

- [ ] 更新的 workflow 文档（3 个）
- [ ] 更新的 template 文件（所有模板）

**验收标准**:

- ✅ workflows 指令清晰，AI 可直接遵循
- ✅ 所有模板包含摘要占位符
- ✅ 字段格式一致（related_files 单行格式）

---

### 阶段 3: 工具开发 - 提取和验证（1 天）

**开发规范**: 参考 `tools/README.md` 中的完整规范要求

**任务**:

- [ ] 开发 `tools/py/summary_extractor.py`
  - [ ] 遵循零依赖原则（仅使用标准库）
  - [ ] 实现 YAML Frontmatter 解析
  - [ ] 实现正则备用方案
  - [ ] 支持单文件和批量模式
  - [ ] JSON 输出格式（包含 success、data、metadata）
  - [ ] 错误处理和 10 秒超时机制
  - [ ] 内置文档注释（参考现有工具格式）
  - [ ] 性能监控（elapsed_seconds）
- [ ] 开发 `tools/js/summary_extractor.js`
  - [ ] 与 Python 版本功能一致
  - [ ] 遵循相同规范
- [ ] 开发 `tools/py/summary_validator.py`
  - [ ] 格式验证（YAML 可解析）
  - [ ] 字段验证（必填字段存在）
  - [ ] **文件存在性验证（related_files 和 dependencies）**
  - [ ] 过期检测（verified_at > 90 天）
  - [ ] 详细错误报告（errors/warnings/suggestions 分类）
  - [ ] 遵循统一输出格式
- [ ] 开发 `tools/js/summary_validator.js`
- [ ] 更新 `tools/README.md`
  - [ ] 在工具清单表格中新增 4 个工具
  - [ ] 提供典型用途说明
  - [ ] 使用示例
- [ ] 更新 `tools/CHANGELOG.md`
  - [ ] 按照 Keep a Changelog 格式
  - [ ] 在 [Unreleased] 的 ### Added 下记录新工具

**产出物**:

- [ ] summary_extractor (Python + JS)
- [ ] summary_validator (Python + JS)
- [ ] 更新的工具文档

**验收标准**:

- ✅ 工具遵循 017-工具库规范（零依赖、JSON 输出）
- ✅ Python 和 JS 版本功能一致
- ✅ 错误处理完善
- ✅ 执行时间 < 5 秒

---

### 阶段 4: 工具开发 - 关联检查和索引（1 天）

**任务**:

- [ ] 开发 `tools/py/summary_related_checker.py`
  - [ ] 提取所有文档的 related_files
  - [ ] 对比代码变更文件列表
  - [ ] 输出受影响的文档列表
  - [ ] 支持从 stdin 读取（配合 git_diff_analyzer）
  - [ ] 提供更新建议
  - [ ] 遵循 tools 规范
- [ ] 开发 `tools/js/summary_related_checker.js`
- [ ] 开发 `tools/py/summary_index_generator.py`（可选）
  - [ ] 遍历所有文档
  - [ ] 批量提取摘要
  - [ ] 生成 Markdown 格式索引页
  - [ ] **在文件开头注释中说明：此工具暂不启用，后续根据需要决定是否使用**
- [ ] 开发 `tools/js/summary_index_generator.js`
  - [ ] 同样在注释中说明暂不启用
- [ ] 单元测试
  - [ ] 测试 summary_related_checker 匹配逻辑
  - [ ] 测试边界情况

**产出物**:

- [ ] summary_related_checker (Python + JS)
- [ ] summary_index_generator (Python + JS)

**验收标准**:

- ✅ summary_related_checker 准确检测关联
- ✅ 与 git_diff_analyzer 配合良好
- ✅ summary_index_generator 注释说明状态

---

### 阶段 5: 框架文档迁移与验证（0.5 天）

**任务**:

- [ ] 为框架核心文档添加摘要
  - [ ] `README.md`
  - [ ] `README.md`
  - [ ] `AI_ENTRY_POINT.md`
  - [ ] `CONTRIBUTING.md`
- [ ] 为部分 workflows 添加摘要（2-3 个示例）
  - [ ] `generation_workflow.md`
  - [ ] `incremental_update_workflow.md`
- [ ] 运行 summary_validator 验证
  - [ ] 检查格式正确性
  - [ ] 检查字段完整性
- [ ] 运行 summary_extractor 测试
- [ ] 性能测试
  - [ ] 提取 50 个文档摘要的耗时
  - [ ] 验证 50 个文档的耗时

**产出物**:

- [ ] 带摘要的框架文档

**验收标准**:

- ✅ 框架核心文档包含正确摘要
- ✅ 所有工具验证通过
- ✅ 性能符合要求（< 5 秒）

---

### 阶段 6: 文档更新与发布（0.5 天）

**任务**:

- [ ] 更新 `dev/V3.0/README.md`
  - [ ] 记录 012 优化点状态变更
- [ ] 更新 `dev/V3.0/PROGRESS.md`
  - [ ] 统计更新：已确认 +1
  - [ ] 标记 012 为已确认
  - [ ] 更新最后更新日期
- [ ] 创建实施总结
  - [ ] 记录实施过程
  - [ ] 记录遇到的问题和解决方案
  - [ ] 记录最佳实践
- [ ] Git 提交
  - [ ] 合理的 commit message
  - [ ] 分多次提交（格式规范、工具、文档等）

**产出物**:

- [ ] 更新的 V3.0 文档
- [ ] 实施总结

**验收标准**:

- ✅ 所有文档更新完成
- ✅ Git 历史清晰

---

## 🧪 测试计划

### 单元测试

**summary_extractor.py**:

```bash
# 测试1: 正常提取
python tools/py/summary_extractor.py --file test_doc.md
# 期望：返回完整摘要 JSON

# 测试2: 无摘要文档
python tools/py/summary_extractor.py --file doc_without_summary.md
# 期望：返回 success:false, error:"no_summary_found"

# 测试3: 格式错误
python tools/py/summary_extractor.py --file malformed_summary.md
# 期望：返回 success:false, error:"yaml_parse_error"

# 测试4: 批量提取
python tools/py/summary_extractor.py --batch-mode --dir dev_docs/
# 期望：返回所有文档摘要数组
```

**summary_validator.py**:

```bash
# 测试1: 完整摘要
python tools/py/summary_validator.py --file valid_doc.md
# 期望：valid:true, errors:[], warnings:[]

# 测试2: 缺少字段
python tools/py/summary_validator.py --file missing_field_doc.md
# 期望：errors:["缺少必填字段: related_files"]

# 测试3: 文件不存在
python tools/py/summary_validator.py --file related_file_missing_doc.md
# 期望：warnings:["关联文件不存在: src/api/deleted.ts"]

# 测试4: 过期摘要
python tools/py/summary_validator.py --file outdated_doc.md
# 期望：warnings:["摘要已过期 120 天"]
```

**summary_related_checker.py**:

```bash
# 测试1: 单文件匹配
python tools/py/summary_related_checker.py --changed-files "src/api/user.ts"
# 期望：返回包含 src/api/user.ts 的所有文档

# 测试2: 多文件匹配
python tools/py/summary_related_checker.py --changed-files "src/api/user.ts,src/api/post.ts"
# 期望：返回匹配任一文件的文档

# 测试3: 与 git_diff_analyzer 配合
python tools/py/git_diff_analyzer.py --since "7 days ago" | \
python tools/py/summary_related_checker.py --from-stdin
# 期望：返回受影响的文档列表
```

### 集成测试

**端到端：文档生成**

1. 模拟 AI 按照 generation_workflow 生成文档
2. 文档包含摘要（7 个字段）
3. 运行 summary_validator 验证通过
4. 运行 summary_extractor 成功提取

**端到端：变更检测**

1. 修改代码文件 `src/api/user.ts`
2. 运行 git_diff_analyzer 检测变更
3. 运行 summary_related_checker 查找受影响文档
4. 确认返回包含该文件的文档列表

---

## ⚠️ 风险与应对

### 风险 1: related_files 提取不准确

**可能性**: 中  
**影响**: 高  
**应对**:

- 在 generation_workflow 中明确要求 AI 列出所有提到的代码文件
- summary_validator 验证文件是否存在
- 用户审核时重点检查此字段

### 风险 2: 工具正则提取失败

**可能性**: 低  
**影响**: 中  
**应对**:

- 优先使用 YAML 解析库
- 正则作为备用方案
- 详细的错误提示

### 风险 3: 性能问题

**可能性**: 低  
**影响**: 低  
**应对**:

- 批量处理优化
- 10 秒超时机制
- 性能监控

---

## 📊 验收标准

### 功能完整性

- [ ] 所有 4 个工具开发完成（Python + JS）
- [ ] 所有 workflows 更新完成
- [ ] 所有 templates 更新完成
- [ ] 格式规范文档完整

### 质量标准

- [ ] 工具遵循 tools/README.md 规范
- [ ] 工具执行时间 < 5 秒
- [ ] 错误处理完善
- [ ] 单元测试通过
- [ ] 集成测试通过

### 文档标准

- [ ] workflows 指令清晰
- [ ] 模板格式正确
- [ ] 示例丰富准确
- [ ] 工具文档完整

---

## 🎯 成功指标

1. **Token 节省**: 文档查询 Token 消耗降低 60-70%
2. **定位效率**: 文档定位时间从 5 分钟降至 1 分钟
3. **更新检测**: 能准确检测出 95% 以上需要更新的文档
4. **摘要覆盖**: 框架核心文档 100% 包含摘要

---

**下一步**: 按照阶段计划开始实施
