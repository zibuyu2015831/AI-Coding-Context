---
title: 框架边界问题改进方案
date: 2025-12-21
status: 待审核
priority: P0
author: AI Assistant
reviewer: zibuyu
---

# 框架边界问题改进方案

## 📋 问题描述

### 当前问题

在实际使用中发现，AI 有时会将 AICC 框架本身当做用户项目的一部分进行分析，导致：

1. **文档内容污染**：生成的项目文档中包含了框架自身的文件（如 `core/language_rules.md`、`templates/*.md` 等）
2. **分析范围错误**：项目代码统计、结构分析等包含了框架文件，导致数据不准确
3. **认知混淆**：AI 无法清晰区分"工具"（框架）和"目标"（用户业务代码）

### 根源分析

通过分析 `AI_ENTRY_POINT.md` 和相关工作流文档，发现以下根本原因：

1. **缺少边界声明**

   - `AI_ENTRY_POINT.md` 中没有明确告知 AI 框架自身的位置和边界
   - 没有排除规则的明确定义

2. **物理位置混淆**

   - 框架被拷贝到项目根目录后（如 `user_project/ai_coding_context/`）
   - AI 容易将其视为项目的一个子模块

3. **工作流缺少防护**

   - 项目检测、扫描等步骤没有强制要求排除框架目录
   - 工具使用文档中没有默认排除参数

4. **术语不够明确**
   - "框架"与"项目"的边界在文档中表述模糊
   - 没有使用"元数据"、"工具"等更清晰的概念区分

## 🎯 解决方案设计

### 设计原则

1. **显式优于隐式**：明确声明框架边界，不依赖 AI 自行推断
2. **多层防护**：在入口文档、工作流、工具层面都增加防护
3. **易于识别**：提供简单的框架识别方法
4. **零歧义**：使用清晰的术语和示例

### 总体方案

采用"三层防护"策略：

```
第一层：入口文档声明（AI_ENTRY_POINT.md）
   ↓ 明确框架边界和排除规则
第二层：工作流强化（path_a, detection_workflow等）
   ↓ 在关键步骤重复提醒
第三层：工具默认排除（tools/README.md, 工具脚本）
   ↓ 工具层面自动过滤
```

## 📝 具体改进点

### 改进点 1：AI_ENTRY_POINT.md 增加框架边界声明

**位置**：在"术语表"之前（第 29 行之前），紧跟"重要说明"之后

**新增章节**：`## ⚠️ 框架边界声明 (CRITICAL: Framework Boundary)`

**内容要点**：

1. **框架位置识别**

   - 明确框架名称：`ai_coding_context`
   - 常见位置：`<项目根>/ai_coding_context/`、`<项目根>/.ai/` 等
   - 识别标志：包含 `AI_ENTRY_POINT.md` 的目录

2. **排除规则（MUST EXCLUDE）**

   - 框架目录本身及所有子目录
   - `dev_docs/_analysis/` 分析临时文件
   - 其他元数据目录（`.git/`、`node_modules/` 等）

3. **分析目标（MUST ANALYZE）**

   - 业务代码目录：`src/`、`lib/`、`app/` 等
   - 项目配置文件
   - 项目已有文档（非框架生成）

4. **操作指南**
   - 提供检测框架位置的命令
   - 提供正确/错误做法的对比示例
   - 建议不确定时询问用户确认

**预期效果**：

- AI 在开始任何分析前必读此章节
- 清晰理解"工具"与"目标"的边界
- 减少 90% 的边界混淆问题

---

### 改进点 2：工作流文档强化边界意识

#### 2.1 path_a_first_generation.md

**位置**：Step 3 "项目扫描/获取结构化数据" 部分

**新增内容**：

````markdown
### ⚠️ 框架边界检查（必需步骤）

在执行项目扫描前，必须：

1. **确定框架位置**

   ```bash
   # 检查框架目录
   Test-Path ai_coding_context/   # 或其他用户指定位置
   ```

2. **在所有扫描命令中添加排除参数**

   ```bash
   # 错误示例 ❌
   python tools/py/project_scanner.py .

   # 正确示例 ✅
   python tools/py/project_scanner.py . --exclude ai_coding_context --exclude node_modules --exclude .git
   ```

3. **验证扫描结果**
   - 检查输出中是否包含框架文件
   - 如包含框架文件，立即停止并重新扫描
````

#### 2.2 detection_workflow.md

**位置**：在"环境预检"之后，"项目结构分析"之前

**新增章节**：`### 框架边界确定`

**内容**：详细步骤说明如何确定并标记框架位置

---

### 改进点 3：工具层面增加默认排除

#### 3.1 现状分析

**好消息**：两个工具脚本都已经实现了以下功能：

✅ **自动读取 `.gitignore`**：

- `project_scanner.py` (第 57-70 行): `load_gitignore_patterns()`
- `project_scanner.js` (第 52-69 行): `loadGitignorePatterns()`

✅ **硬编码排除 `.git`**：

- 始终排除 `.git/` 目录

✅ **支持手动排除**：

- 通过 `--ignore` 参数支持逗号分隔的排除模式
- 示例：`--ignore "ai_coding_context,node_modules,.vscode"`

**需要增强的部分**：

1. 缺少 `--exclude-standard` 快捷参数（需要手动列举）
2. ~~缺少框架目录自动检测~~（**已通过脚本位置反推解决**）✅
3. 输出中没有显示已排除的目录（不透明）

**优化亮点**：

- ⭐ **支持框架任意重命名**：通过脚本位置（`__file__`/`__filename`）反推框架根目录
- 即使用户将框架重命名为 `my_custom_ai_tools`，工具也能自动识别并排除

---

#### 3.2 tools/README.md 更新

**新增章节**：`## 项目扫描工具的排除机制`

**内容**：

`````markdown
## 项目扫描工具的排除机制

### 自动排除机制

项目扫描工具会自动排除以下内容：

1.  **`.gitignore` 文件中的所有模式**

    - 工具会自动读取项目根目录的 `.gitignore` 文件
    - 所有 gitignore 规则都会被尊重

2.  **`.git/` 目录**
    - 硬编码排除，无法关闭

### 手动排除（方式 1）

使用 `--ignore` 参数手动指定排除模式：

```bash
# 单个排除
python tools/py/project_scanner.py . --ignore ai_coding_context

# 多个排除（逗号分隔）
python tools/py/project_scanner.py . --ignore "ai_coding_context,node_modules,.vscode"

# Node.js 版本同理
node tools/js/project_scanner.js . --ignore "ai_coding_context,node_modules"
```

### 标准排除（方式 2 - 推荐）⭐

使用 `--exclude-standard` 参数一键排除所有标准模式：

```bash
# Python 版本
python tools/py/project_scanner.py . --exclude-standard

# Node.js 版本
node tools/js/project_scanner.js . --exclude-standard
```

**标准排除列表包括**：

**框架文件**（最高优先级）：

- **自动检测的框架目录**⭐（包含 `AI_ENTRY_POINT.md` 的目录）
  - 检测策略 1：通过脚本自身位置反推（最可靠，支持任意重命名）
  - 检测策略 2：检查常见位置（`ai_coding_context/`、`.ai/`、`docs/ai_context/`）
  - 检测策略 3：遍历项目根目录查找
- `ai_coding_context/`（fallback）
- `.ai/`（fallback）
- `docs/ai_context/`（fallback）

**依赖与构建产物**：

- `node_modules/`、`package-lock.json`
- `venv/`、`env/`、`.env/`、`__pycache__/`
- `dist/`、`build/`、`.next/`
- `target/`（Java/Rust）

**版本控制**：

- `.git/`（已硬编码）
- `.svn/`

**IDE 配置**：

- `.vscode/`、`.idea/`
- `*.swp`、`*.swo`

### 组合使用

`--exclude-standard` 和 `--ignore` 可以组合使用：

```bash
# 标准排除 + 自定义排除
python tools/py/project_scanner.py . --exclude-standard --ignore "custom_temp,*.tmp"
```

### 输出说明

启用排除后，输出会显示已排除的目录：

```json
{
  "data": { ... },
  "metadata": {
    "excluded_patterns": [
      "ai_coding_context/ (framework auto-detected)",
      "node_modules/",
      ".git/",
      "..."
    ],
    "excluded_dirs_count": 5
  }
}
```

#### 3.3 修改 `tools/py/project_scanner.py`

**修改策略**：添加 3 个新函数 + 修改 2 个现有函数

**修改 1：添加框架检测和标准排除函数**（在 `load_gitignore_patterns` 之后插入）

```python
def detect_framework_dir(root_dir, script_file=None):
    """
    检测框架目录位置（支持任意重命名）

    检测策略（优先级从高到低）：
    1. 通过脚本自身位置反推（最可靠，支持任意重命名）
    2. 检查常见位置名称
    3. 遍历根目录查找 AI_ENTRY_POINT.md

    参数：
        root_dir: 项目根目录
        script_file: 脚本文件路径（__file__），用于反推框架位置

    返回：框架相对路径（如 'my_custom_framework'）或 None
    """

    # 策略 1：通过脚本位置反推框架根目录（最可靠）⭐
    if script_file:
        try:
            # 脚本路径：<框架根>/tools/py/project_scanner.py
            # 向上两级即为框架根
            script_abs = os.path.abspath(script_file)
            framework_root = os.path.dirname(os.path.dirname(os.path.dirname(script_abs)))

            # 验证：框架根应该包含 AI_ENTRY_POINT.md
            entry_point = os.path.join(framework_root, 'AI_ENTRY_POINT.md')
            if os.path.exists(entry_point):
                # 计算相对于项目根的路径
                framework_rel = os.path.relpath(framework_root, root_dir)
                # 规范化路径分隔符
                framework_rel = framework_rel.replace(os.sep, '/')

                # 如果框架不在项目根目录之外，返回相对路径
                if not framework_rel.startswith('..'):
                    return framework_rel
        except Exception:
            pass

    # 策略 2：检查常见位置名称
    common_names = ['ai_coding_context', '.ai', 'docs/ai_context']
    for name in common_names:
        entry_point = os.path.join(root_dir, name, 'AI_ENTRY_POINT.md')
        if os.path.exists(entry_point):
            return name

    # 策略 3：遍历根目录，查找包含 AI_ENTRY_POINT.md 的目录
    try:
        for item in os.listdir(root_dir):
            item_path = os.path.join(root_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                entry_point = os.path.join(item_path, 'AI_ENTRY_POINT.md')
                if os.path.exists(entry_point):
                    return item
    except Exception:
        pass

    return None

def get_standard_exclude_patterns(root_dir, script_file=None):
    """
    获取标准排除模式列表
    返回：[(pattern, label), ...] 或 [pattern, ...]
    """
    patterns = []

    # 1. 框架目录（自动检测，支持任意重命名）
    framework_dir = detect_framework_dir(root_dir, script_file)
    if framework_dir:
        patterns.append((f"{framework_dir}/", f'framework auto-detected: {framework_dir}'))
    else:
        # Fallback 模式
        patterns.extend(['ai_coding_context/', '.ai/', 'docs/ai_context/'])

    # 2. 依赖与构建产物
    patterns.extend([
        'node_modules/', 'package-lock.json',
        'venv/', 'env/', '.env/', '__pycache__/',
        'dist/', 'build/', '.next/', 'out/',
        'target/',  # Java/Rust
        '*.egg-info/', '.pytest_cache/',
    ])

    # 3. 版本控制（.git 已硬编码）
    patterns.append('.svn/')

    # 4. IDE 配置
    patterns.extend(['.vscode/', '.idea/', '*.swp', '*.swo'])

    return patterns
```

**修改 2：更新 `scan_project` 函数签名和逻辑**

需要添加 `exclude_standard` 参数和 `excluded_info` 返回值：

```python
def scan_project(root_dir, ignore_patterns, follow_symlinks, max_files_per_dir, max_depth, exclude_standard=False, script_file=None):
    structure = {}
    stats = {"files": 0, "dirs": 0}
    excluded_info = []  # 新增：记录排除信息

    # Base ignore patterns (always ignore .git)
    all_patterns = ignore_patterns + ['.git']
    excluded_info.append('.git/ (hardcoded)')

    # 添加标准排除模式
    if exclude_standard:
        standard_patterns = get_standard_exclude_patterns(root_dir, script_file)  # 传入 script_file
        for p in standard_patterns:
            if isinstance(p, tuple):
                pattern, label = p
                all_patterns.append(pattern)
                excluded_info.append(f"{pattern} ({label})")
            else:
                all_patterns.append(p)
                excluded_info.append(p)

    # 添加用户手动指定的排除
    for p in ignore_patterns:
        excluded_info.append(f"{p} (manual)")

    # 加载 gitignore
    gitignore_patterns = load_gitignore_patterns(root_dir)
    all_patterns.extend(gitignore_patterns)
    if gitignore_patterns:
        excluded_info.append(f".gitignore ({len(gitignore_patterns)} patterns)")

    # ... 原始扫描逻辑保持不变 ...

    return structure, stats, excluded_info  # 修改返回值
```

**修改 3：更新 `main` 函数**

添加参数解析和输出格式：

```python
def main():
    start_time = time.time()

    parser = argparse.ArgumentParser(description="Project Structure Scanner")
    parser.add_argument("--path", default=".", help="Root directory to scan")
    parser.add_argument("--ignore", help="Comma-separated glob patterns to ignore")
    parser.add_argument("--exclude-standard", action="store_true",
                        help="Exclude standard patterns (framework, deps, IDE)")  # 新增
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    parser.add_argument("--max-files", type=int, default=1000, help="Max files per directory")
    parser.add_argument("--depth", type=int, help="Max scan depth")
    parser.add_argument("--format", choices=["json", "tree"], default="json", help="Output format")

    args = parser.parse_args()

    root_dir = os.path.abspath(args.path)
    ignore_patterns = args.ignore.split(",") if args.ignore else []

    structure, stats, excluded_info = scan_project(  # 修改：接收 excluded_info
        root_dir,
        ignore_patterns,
        args.follow_symlinks,
        args.max_files,
        args.depth,
        args.exclude_standard,  # 新增参数
        __file__  # 传入脚本自身路径，用于反推框架位置
    )

    elapsed_time = round(time.time() - start_time, 2)

    if args.format == "json":
        result = {
            "data": {"structure": structure, "stats": stats},
            "metadata": {
                "elapsed_seconds": elapsed_time,
                "timeout_threshold": 10,
                "version": "1.2.0",  # 版本升级
                "excluded_patterns": excluded_info,  # 新增
                "excluded_count": len(excluded_info)  # 新增
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        tree_lines = generate_tree(structure)
        print("\n".join(tree_lines))
        print(f"\nStats: {stats['files']} files, {stats['dirs']} directories")
        print(f"Excluded: {len(excluded_info)} patterns")  # 新增
        print(f"Elapsed: {elapsed_time}s")
```

---

#### 3.4 修改 `tools/js/project_scanner.js`

**修改逻辑与 Python 版本完全一致**，关键代码片段：

```javascript
// 添加框架检测函数（支持任意重命名）
function detectFrameworkDir(rootDir, scriptFile = null) {
    // 策略 1：通过脚本位置反推框架根目录（最可靠）⭐
    if (scriptFile) {
        try {
            // 脚本路径：<框架根>/tools/js/project_scanner.js
            // 向上两级即为框架根
            const scriptAbs = path.resolve(scriptFile);
            const frameworkRoot = path.dirname(path.dirname(path.dirname(scriptAbs)));

            // 验证：框架根应该包含 AI_ENTRY_POINT.md
            const entryPoint = path.join(frameworkRoot, 'AI_ENTRY_POINT.md');
            if (fs.existsSync(entryPoint)) {
                // 计算相对于项目根的路径
                let frameworkRel = path.relative(rootDir, frameworkRoot);
                // 规范化路径分隔符
                frameworkRel = frameworkRel.split(path.sep).join('/');

                // 如果框架不在项目根目录之外，返回相对路径
                if (!frameworkRel.startsWith('..')) {
                    return frameworkRel;
                }
            }
        } catch (e) {}
    }

    // 策略 2：检查常见位置名称
    const commonNames = ['ai_coding_context', '.ai', 'docs/ai_context'];
    for (const name of commonNames) {
        const entryPoint = path.join(rootDir, name, 'AI_ENTRY_POINT.md');
        if (fs.existsSync(entryPoint)) return name;
    }

    // 策略 3：遍历根目录查找
    try {
        const items = fs.readdirSync(rootDir);
        for (const item of items) {
            if (!item.startsWith('.')) {
                const itemPath = path.join(rootDir, item);
                try {
                    if (fs.statSync(itemPath).isDirectory()) {
                        const entryPoint = path.join(itemPath, 'AI_ENTRY_POINT.md');
                        if (fs.existsSync(entryPoint)) return item;
                    }
                } catch (e) {}
            }
        }
    } catch (e) {}

    return null;
}

// 添加标准排除模式函数
function getStandardExcludePatterns(rootDir, scriptFile = null) {
    const patterns = [];

    // 1. 框架目录（自动检测，支持任意重命名）
    const frameworkDir = detectFrameworkDir(rootDir, scriptFile);
    if (frameworkDir) {
        patterns.push([`${frameworkDir}/`, `framework auto-detected: ${frameworkDir}`]);
    } else {
        patterns.push('ai_coding_context/', '.ai/', 'docs/ai_context/');
    }

    patterns.push(
        'node_modules/', 'package-lock.json',
        'venv/', 'env/', '.env/', '__pycache__/',
        'dist/', 'build/', '.next/', 'out/',
        'target/',
        '.svn/', '.vscode/', '.idea/', '*.swp', '*.swo'
    );

    return patterns;
}

// 修改 scanProject 函数签名
function scanProject(rootDir, ignorePatterns, followSymlinks, maxFilesPerDir, maxDepth, excludeStandard = false, scriptFile = null) {
    const structure = {};
    const stats = { files: 0, dirs: 0 };
    const excludedInfo = [];  // 新增

    // Base patterns
    const allPatterns = [...ignorePatterns, '.git'];
    excludedInfo.push('.git/ (hardcoded)');

    // 添加标准排除
    if (excludeStandard) {
        const standardPatterns = getStandardExcludePatterns(rootDir, scriptFile);
        for (const p of standardPatterns) {
            if (Array.isArray(p)) {
                const [pattern, label] = p;
                allPatterns.push(pattern);
                excludedInfo.push(`${pattern} (${label})`);
            } else {
                allPatterns.push(p);
                excludedInfo.push(p);
            }
        }
    }

    // ... 与 Python 版本相同的逻辑 ...

    return { structure, stats, excludedInfo };  // 修改返回值
}

// 在 main() 中修改调用
const result = scanProject(
    rootDir,
    options.ignore,
    options.followSymlinks,
    options.maxFiles,
    options.depth,
    options.excludeStandard,
    __filename  // 传入脚本自身路径
);

// 在 main() 中添加参数解析
case '--exclude-standard': options.excludeStandard = true; break;
```

**完整修改内容**参见 Python 版本，结构完全对应。

---

### 改进点 4：术语优化

在 `AI_ENTRY_POINT.md` 的术语表中新增：

| 术语       | 标准写法             | 说明                                  |
| ---------- | -------------------- | ------------------------------------- |
| 框架边界   | Framework Boundary   | AICC 框架与用户项目的物理边界         |
| 框架根目录 | Framework Root       | 包含 `AI_ENTRY_POINT.md` 的目录       |
| 项目根目录 | Project Root         | 用户业务项目的根目录（通常是 Git 根） |
| 分析目标   | Analysis Target      | 需要分析的用户业务代码                |
| 排除目录   | Excluded Directories | 不应被分析的目录（框架、依赖等）      |

---

## 📐 实施计划

### 阶段 1：核心文档修改（优先级 P0）

| 文件                | 修改内容               | 预估行数 | 复杂度 |
| ------------------- | ---------------------- | -------- | ------ |
| `AI_ENTRY_POINT.md` | 新增"框架边界声明"章节 | +80 行   | 中     |
| `AI_ENTRY_POINT.md` | 优化术语表             | +5 行    | 低     |

### 阶段 2：工作流文档强化（优先级 P0）

| 文件                                   | 修改内容               | 预估行数 | 复杂度 |
| -------------------------------------- | ---------------------- | -------- | ------ |
| `workflows/path_a_first_generation.md` | Step 3 增加边界检查    | +30 行   | 低     |
| `workflows/detection_workflow.md`      | 新增"框架边界确定"章节 | +40 行   | 中     |

### 阶段 3：工具优化（优先级 P0）⭐

| 文件                          | 修改内容                      | 预估行数 | 复杂度 |
| ----------------------------- | ----------------------------- | -------- | ------ |
| `tools/README.md`             | 新增"排除机制"完整说明        | +80 行   | 低     |
| `tools/py/project_scanner.py` | 添加 3 个函数 + 修改 2 个函数 | +70 行   | 中     |
| `tools/js/project_scanner.js` | 同 Python 版本                | +70 行   | 中     |

### 执行顺序

```

1. 修改 AI_ENTRY_POINT.md（核心）
   ↓
2. 修改 path_a_first_generation.md（最常用路径）
   ↓
3. 修改 detection_workflow.md（底层流程）
   ↓
4. 修改 tools/README.md（工具指南）
   ↓
5. 修改工具脚本（可选，增强防护）

```

**总预估**：

- 文档修改：约 230 行新增内容
- 工具脚本：约 140 行代码（Python + JS）
- 总耗时：2-3 小时

---

## ⚠️ 风险评估

### 风险 1：过度强调导致冗余

**描述**：在多个地方重复强调边界问题，可能导致文档冗余

**缓解措施**：

- 入口文档详细说明，其他文档简要提醒+链接引用
- 使用"详见 AI_ENTRY_POINT.md#框架边界声明"等引用方式

**影响等级**：低

---

### 风险 2：现有用户习惯改变

**描述**：如果有用户将框架放在非标准位置，可能需要额外配置

**缓解措施**：

- 支持用户手动指定框架位置
- 提供自动检测 + 用户确认的模式
- 在文档中说明自定义位置的处理方法

**影响等级**：中

---

### 风险 3：工具脚本修改可能引入 Bug

**描述**：修改扫描工具的排除逻辑，可能误排除用户代码

**缓解措施**：

- 使用白名单+黑名单双重机制
- 在输出中明确显示已排除的目录
- 提供 `--no-exclude-standard` 参数供高级用户完全控制

**影响等级**：中

---

## 🎯 预期效果

### 定量目标

1. **边界混淆率下降 90%**

   - 当前估计：AI 在 30-40% 的首次生成中会包含框架文件
   - 改进后目标：< 5%

2. **文档准确性提升**

   - 项目统计数据（文件数、代码行数）准确率达到 95%+
   - 子文档推荐准确率提升 20%

3. **用户干预减少**
   - 减少 80% 的"AI 分析错误需要重新生成"情况

### 定性目标

1. **AI 认知清晰**

   - AI 能清晰区分"工具"（框架）与"目标"（业务代码）
   - 减少因边界不清导致的错误决策

2. **用户体验提升**

   - 用户无需手动指出"这些不是我的代码"
   - 首次生成成功率提升，减少返工

3. **框架鲁棒性增强**
   - 即使用户将框架放在非标准位置，也能正确识别
   - 降低对用户操作的依赖

---

## 📚 附录

### 附录 A：框架边界声明章节完整内容

详见下方代码块（完整的 Markdown 内容，可直接插入）：

````markdown
---

## ⚠️ 框架边界声明 (CRITICAL: Framework Boundary)

> **本节对 AI 至关重要，必须在开始任何分析前阅读并遵守**

### 什么是框架边界？

**AI Coding Context (AICC)** 是一个辅助工具框架，用于帮助生成项目文档。
**框架本身不是用户的业务代码**，在分析项目时必须将其排除。

**类比**：

- 框架 = 医生的听诊器（工具）
- 用户项目 = 病人（分析目标）
- AI 的任务 = 诊断病人，而不是研究听诊器

### 框架位置与识别

**典型位置**：

- `<项目根目录>/ai_coding_context/`（最常见）
- `<项目根目录>/.ai/`（点开头目录）
- `<项目根目录>/docs/ai_context/`（文档子目录）
- 用户自定义的其他位置

**识别标志**：

- 包含本文件 `AI_ENTRY_POINT.md` 的目录即为框架根目录
- 该目录下通常包含 `core/`、`workflows/`、`templates/`、`agents/`、`tools/` 等子目录

**检测命令**：

```bash
# Windows PowerShell
Test-Path ai_coding_context/AI_ENTRY_POINT.md

# Linux/Mac
test -f ai_coding_context/AI_ENTRY_POINT.md && echo "框架位于: ai_coding_context/" || echo "未检测到标准位置"
```
````
`````

### 🚫 排除规则 (MUST EXCLUDE)

在执行以下操作时，**必须排除**这些内容：

#### 1. 框架目录（最高优先级）

```
❌ 不得分析、统计、引用的内容：
- 整个框架目录（ai_coding_context/ 或其他名称）
  - core/
  - workflows/
  - templates/
  - agents/
  - tools/
  - guides/
  - reference/
  - config/（框架配置，不是项目配置）

✅ 唯一例外：
- 可以读取框架文件以理解工作流和规范
- 但不得将框架文件内容纳入项目分析结果
```

#### 2. 框架生成的临时文件

```
❌ dev_docs/_analysis/（分析过程文件）
  - generation_plan.md
  - project_analysis_report.md
  - generation_progress.md
```

#### 3. 其他标准排除目录

```
❌ 依赖与构建产物：
  - node_modules/
  - venv/, env/, .env/
  - dist/, build/
  - target/（Java）
  - __pycache__/

❌ 版本控制：
  - .git/
  - .svn/

❌ IDE 配置：
  - .vscode/
  - .idea/
  - *.swp
```

### ✅ 分析目标 (MUST ANALYZE)

**用户的业务代码**，通常包括：

```
✅ 源代码目录：
  - src/
  - lib/
  - app/
  - components/
  - pages/
  - api/
  - services/
  - utils/
  - （根据项目类型可能有不同命名）

✅ 配置文件：
  - package.json
  - tsconfig.json
  - requirements.txt
  - pom.xml
  - Cargo.toml
  - .env.example（示例配置）

✅ 项目文档：
  - README.md（项目的说明文档）
  - docs/（项目自己的文档，非框架生成）
  - CONTRIBUTING.md
  - CHANGELOG.md

✅ 框架已生成的文档体系（如果存在）：
  - dev_docs/AI_Coding_Context.md（主文档）
  - dev_docs/*.md（生成的子文档）
  - dev_docs/knowledge/（知识库）
  - AI_RULES.md
```

### 实际操作示例

#### ❌ 错误做法

**场景**：扫描项目文档时包含了框架文件

```bash
# 错误命令（未排除框架）
python tools/py/project_scanner.py .

# 错误结果
项目文档列表：
- README.md
- ai_coding_context/core/language_rules.md  ← 这是框架文件！
- ai_coding_context/templates/GENERATION_PLAN_TEMPLATE.md  ← 这是框架文件！
- src/README.md

→ 导致：生成的文档中包含了框架自身的说明
```

#### ✅ 正确做法

**场景**：明确排除框架目录

```bash
# 正确命令（排除框架）
python tools/py/project_scanner.py . --exclude ai_coding_context --exclude node_modules

# 正确结果
项目文档列表：
- README.md
- src/README.md

已排除目录：
- ai_coding_context/（框架）
- node_modules/（依赖）

→ 结果：只分析用户的业务代码和文档
```

### 不确定时的处理原则

如果无法确定框架位置或分析边界，**必须**：

1. **列出候选目录**

   ```
   检测到以下可能是框架的目录：
   - ai_coding_context/（包含 AI_ENTRY_POINT.md）
   - .ai/（名称模式匹配）
   ```

2. **询问用户确认**

   ```
   我将在分析时排除以上目录，这样对吗？
   如果框架位于其他位置，请告知。
   ```

3. **记录决策**
   在 `dev_docs/_analysis/generation_plan.md` 中记录：

   ```markdown
   ## 框架边界确认

   - 框架位置: `ai_coding_context/`
   - 排除目录: `ai_coding_context/`, `node_modules/`, `.git/`
   - 确认方式: 自动检测到 AI_ENTRY_POINT.md
   ```

### 特殊场景处理

#### 场景 1：框架在非标准位置

**用户可能的操作**：

```bash
# 用户将框架重命名或移动
mv ai_coding_context .my_ai_tools
```

**AI 的处理**：

1. 搜索 `AI_ENTRY_POINT.md` 文件位置
2. 确定框架根目录
3. 询问用户确认

#### 场景 2：多个项目共享一个框架

**结构示例**：

```
workspace/
├── ai_coding_context/（共享框架）
├── project_a/
└── project_b/
```

**AI 的处理**：

1. 识别当前工作目录（如 `project_a/`）
2. 排除框架目录（`../ai_coding_context/`）
3. 只分析当前项目

#### 场景 3：框架已被版本管理

**用户操作**：

```bash
# 用户将框架加入 Git
git add ai_coding_context/
```

**AI 的处理**：

- 依然排除框架目录
- 在生成的 `.gitignore` 建议中，不建议忽略框架
- 在文档中说明："框架已纳入版本管理，这符合预期"

---

### 检查清单

在开始任何分析或生成任务前，AI 应完成以下检查：

- [ ] 已确定框架根目录位置
- [ ] 已在所有扫描/统计命令中添加框架排除参数
- [ ] 已验证扫描结果不包含框架文件
- [ ] 如有疑问，已询问用户确认

**完成此清单后，方可继续后续步骤。**

---

### 附录 B：相关文档修改清单

**需要同步更新的文档**：

1. `workflows/path_a_first_generation.md` - Step 3 增加边界检查
2. `workflows/detection_workflow.md` - 新增"框架边界确定"章节
3. `tools/README.md` - 新增"默认排除模式"章节
4. `tools/py/project_scanner.py` - 代码修改
5. `tools/js/project_scanner.js` - 代码修改

**交叉引用**：

- 所有工作流文档在涉及项目扫描时，都应引用 `AI_ENTRY_POINT.md#框架边界声明`
- 工具文档应明确说明默认排除行为

---

**文档版本**：v2.1（添加基于脚本位置的智能检测，支持框架任意重命名）  
**创建时间**：2025-12-21 12:56  
**最后更新**：2025-12-21 15:28  
**下次更新**：根据审核意见修订
