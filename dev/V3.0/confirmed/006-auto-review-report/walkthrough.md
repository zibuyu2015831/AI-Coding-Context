# 006-自动化审查报告 - 实施产出与验证指南（整合到005）

本文档总结了 006-自动化审查报告的实施成果，并提供标准化的验证场景以确保功能的正确性。本优化点已整合到 005-复杂度实时仪表盘中。

## 🎯 实施产出摘要

### 1. 📂 目录结构与规范（复用 005）
- **配置区**: `dev_docs/complexity/config.yaml` - 新增审查相关配置
- **数据区**: `dev_docs/complexity/data/` - 原始数据存储（包含审查数据）
- **报告区**: `dev_docs/complexity/reports/` - Markdown 报告（整合审查内容）
- **可视化**: `dev_docs/complexity/dashboard/` - HTML 可视化页面

### 2. 🛠️ 支持工具链 (Dual-Engine: Py/JS - 扩展 005)
- **扫描工具**: `complexity_scanner.py` & `complexity_scanner.js` - 新增审查数据采集
- **报告生成**: `report_generator.py` & `report_generator.js` - 新增审查报告生成
- **通知工具**: `notifier.py` & `notifier.js` - 支持发送审查通知
- **Git Hooks**: `pre-commit` & `post-commit` - 新增审查检查

---

## 🔍 验证场景

### 场景 A: 基础审查数据采集验证

**操作**: 运行扩展后的复杂度扫描工具，验证是否采集到审查数据。

**示例命令**:
```bash
python tools/py/complexity_scanner.py --output dev_docs/complexity/data/test-review.json
```

**预期结果**:
1. 工具成功执行，无错误输出
2. 内部自动调用 `git_diff_analyzer.py` 获取变更数据
3. 生成的 JSON 文件包含以下新增数据:
   - `review_data` 字段：变更概述、影响分析、问题识别
   - `todo_changes`：新增/删除的 TODO/FIXME 标记
   - `dangerous_patterns`：检测到的危险函数
   - `api_changes`：API 变更

---

### 场景 B: 审查报告生成验证

**操作**: 生成包含审查内容的综合报告。

**示例命令**:
```bash
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/test-review.json \
  --output dev_docs/complexity/reports/test-review.md \
  --format markdown
```

**预期结果**:
1. 工具成功执行，无错误输出
2. 生成的 Markdown 文件包含新增"代码审查"章节：
   - 📝 变更概述（文件数、代码增减）
   - 🚨 紧急问题（危险函数、敏感信息）
   - 🟡 重要问题（TODO 标记过多）
   - 📚 需要更新的文档
   - 🎯 影响分析

---

### 场景 C: 审查报告可视化验证

**操作**: 生成包含审查内容的 HTML 仪表盘。

**示例命令**:
```bash
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/test-review.json \
  --template dev_docs/complexity/template.html \
  --output dev_docs/complexity/dashboard/test-dashboard.html \
  --format html
```

**预期结果**:
1. 工具成功执行，无错误输出
2. 生成的 HTML 文件包含新增审查可视化区域：
   - 变更统计图表
   - 问题严重度矩阵（🔴/🟡/🟢 标记）
   - 行动建议列表
3. 在浏览器中打开 HTML 文件，所有功能正常显示

---

### 场景 D: 轻量级代码检查验证

**操作**: 测试轻量级检查功能。

**示例操作**:
1. 创建一个包含危险函数的测试文件
2. 运行扫描工具
3. 检查是否检测到问题

**预期结果**:
1. 扫描工具检测到危险函数（如 eval()）
2. 报告中标记为 🔴 高风险
3. 给出明确的修复建议

---

### 场景 E: Git Hooks 审查检查验证

**操作**: 安装 Git Hooks 并进行一次包含问题代码的提交测试。

**示例命令**:
```bash
python tools/install_hooks.py --enable-complexity-check
# 创建一个包含 TODO 标记的测试文件
echo "# TODO: 待实现功能" > test-review-file.txt
git add test-review-file.txt
git commit -m "test: 添加包含 TODO 的测试文件"
```

**预期结果**:
1. pre-commit 钩子成功触发审查检查
2. 检测到 TODO 标记
3. 如果数量超过阈值，阻止提交
4. 提供友好的风险提示

---

### 场景 F: 通知系统验证

**操作**: 测试通知系统是否支持发送审查报告。

**示例命令**:
```bash
python tools/py/notifier.py --data dev_docs/complexity/data/test-review.json --level critical --email dev@example.com
```

**预期结果**:
1. 工具成功执行，无错误输出
2. 显示通知预览（包含审查内容）
3. 如果配置了 Email 或 Slack，发送实际通知

---

## 验证记录表

| 场景 | 修改日期 | 结果 | 备注 |
| :--- | :--- | :--- | :--- |
| A: 基础审查数据采集 | 待执行 | 🔴 未开始 | Python 和 Node.js 版本均需验证 |
| B: 审查报告生成 | 待执行 | 🔴 未开始 | 需验证 Markdown 和 HTML 格式 |
| C: 审查报告可视化 | 待执行 | 🔴 未开始 | 需验证 HTML 模板渲染 |
| D: 轻量级代码检查 | 待执行 | 🔴 未开始 | 需测试危险函数和 TODO 检测 |
| E: Git Hooks 集成 | 待执行 | 🔴 未开始 | 需测试提交前拦截功能 |
| F: 通知系统 | 待执行 | 🔴 未开始 | 需验证通知预览和发送 |

---

## 使用指南

### 快速开始

#### 1. 生成包含审查内容的报告

```bash
# 扫描项目（包含审查数据）
python tools/py/complexity_scanner.py --output dev_docs/complexity/data/$(date +%Y-%m-%d).json

# 生成综合报告（包含复杂度和审查）
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/$(date +%Y-%m-%d).json \
  --output dev_docs/complexity/reports/$(date +%Y-%m-%d).md \
  --format markdown

# 生成包含审查的 HTML 仪表盘
python tools/py/report_generator.py \
  --data dev_docs/complexity/data/$(date +%Y-%m-%d).json \
  --template dev_docs/complexity/template.html \
  --output dev_docs/complexity/dashboard/dashboard.html \
  --format html
```

#### 2. 启用审查检查的 Git Hooks

```bash
python tools/install_hooks.py --enable-complexity-check
```

#### 3. 查看报告

- **Markdown**: 打开 `dev_docs/complexity/reports/$(date +%Y-%m-%d).md`
- **HTML**: 在浏览器中打开 `dev_docs/complexity/dashboard/dashboard.html`

---

## 配置说明

### 审查相关配置

编辑 `dev_docs/complexity/config.yaml`，新增或修改以下配置：

```yaml
# 代码审查配置
review:
  # 危险函数列表
  dangerous_functions:
    - eval
    - exec
    - Function
    - setTimeout
    - setInterval

  # 大文件变更阈值（行数）
  large_file_threshold: 500

  # TODO 警告阈值（新增数量）
  todo_warning_threshold: 3
  todo_critical_threshold: 5

  # 通知配置
  notification:
    level: warning
    channels:
      - slack
      - email
```

---

**版本**: v1.0
**维护者**: Framework Team
**创建日期**: 2026-04-12
