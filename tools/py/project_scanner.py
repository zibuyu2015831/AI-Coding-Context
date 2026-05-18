"""
项目结构扫描工具 - 生成项目目录树的 JSON 或文本表示

功能说明：
- 扫描指定目录，生成完整的目录树结构
- 自动读取并尊重 .gitignore 规则
- 支持限制扫描深度和每目录文件数
- 支持输出 JSON 格式（供 AI 解析）或树形文本格式（供人类阅读）
- 支持标准排除模式（框架、依赖、IDE 配置等）⭐

使用方法：
    python tools/py/project_scanner.py [路径] [选项]

参数说明：
    路径                     要扫描的根目录路径（可选，默认：当前目录）
    --ignore PATTERNS        逗号分隔的忽略模式（会自动叠加 .gitignore）
    --exclude-standard       一键排除标准模式（框架、依赖、IDE）⭐
    --follow-symlinks        跟随符号链接（默认：否）
    --max-files NUM          每个目录最多显示的文件数（默认：1000）
    --depth NUM              最大扫描深度（默认：无限制）
    --format FORMAT          输出格式：json 或 tree（默认：json）

输出格式（JSON模式）：
    {
      "data": {
        "structure": {目录树对象},
        "stats": {"files": 文件数, "dirs": 目录数}
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.2.0",
        "excluded_patterns": [排除的模式列表],
        "excluded_count": 排除模式数量
      }
    }

使用示例：
    # 扫描当前项目（JSON 格式，使用标准排除）
    python tools/py/project_scanner.py --path . --exclude-standard

    # 扫描 src 目录（限制深度为 3）
    python tools/py/project_scanner.py --path ./src --depth 3

    # 生成人类可读的树形结构
    python tools/py/project_scanner.py --format tree

版本信息：
    版本：1.2.0
    更新日期：2025-12-21
"""

import os
import json
import argparse
import fnmatch
import sys
import time
import re
from collections import deque

# ==================== 重要文件优先级系统 ====================
# 识别项目类型、语言、规模等特征

IMPORTANT_FILES = {
    # 优先级 1 (最高)
    'README.md': 1, 'README.rst': 1, 'LICENSE': 1, 'LICENSE.md': 1,
    'package.json': 1, 'setup.py': 1, 'pyproject.toml': 1,
    'pom.xml': 1, 'build.gradle': 1, 'go.mod': 1, 'Cargo.toml': 1,
    'Dockerfile': 1,
    
    # 优先级 2 (高)
    'tsconfig.json': 2, 'jsconfig.json': 2,
    'requirements.txt': 2, 'Pipfile': 2,
    '.gitignore': 2, 'CHANGELOG.md': 2,
    'docker-compose.yml': 2,
    
    # 优先级 3 (中)
    'webpack.config.js': 3, 'vite.config.ts': 3, 'vite.config.js': 3,
    'next.config.js': 3, 'nuxt.config.js': 3,
    '.eslintrc.js': 3, '.eslintrc.json': 3, '.prettierrc': 3,
    'jest.config.js': 3, 'vitest.config.ts': 3,
}

IMPORTANT_PATTERNS = [
    r'^index\.(js|ts|jsx|tsx|py|php)$',
    r'^main\.(js|ts|go|rs|c|cpp)$',
    r'^app\.(js|ts|jsx|tsx|py)$',
    r'^App\.(tsx|jsx)$',
    r'^__init__\.py$',
    r'^__main__\.py$',
    r'\.config\.(js|ts)$',
    r'^\.env',
]

IMPORTANT_DIRS = {
    'src': 1,
    'lib': 2,
    'app': 2,
    'components': 3,
    'pages': 3,
    'utils': 3,
    'api': 3,
    'config': 3,
    'tests': 10,
}

def get_file_priority(filename):
    """获取文件优先级 (数字越小优先级越高)"""
    if filename in IMPORTANT_FILES:
        return (IMPORTANT_FILES[filename], filename)
    
    for pattern in IMPORTANT_PATTERNS:
        if re.match(pattern, filename):
            return (2, filename)
    
    return (100, filename.lower())

def sort_files_by_importance(files):
    """按重要性排序文件列表"""
    return sorted(files, key=get_file_priority)

def sort_dirs_by_importance(dirs):
    """按重要性排序目录列表"""
    def get_dir_priority(dirname):
        clean_name = dirname.rstrip('/')
        if clean_name in IMPORTANT_DIRS:
            return (IMPORTANT_DIRS[clean_name], clean_name.lower())
        return (100, clean_name.lower())
    
    return sorted(dirs, key=get_dir_priority)

def load_gitignore_patterns(root_dir):
    patterns = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    patterns.append(line)
        except Exception as e:
            sys.stderr.write(f"Warning: Could not read .gitignore: {e}\n")
    return patterns

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
    common_names = ['AI-Coding-Context', 'ai_coding_context', 'ai-coding-context', '.ai', 'docs/ai_context']
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
        patterns.extend(['AI-Coding-Context/', 'ai_coding_context/', 'ai-coding-context/', '.ai/', 'docs/ai_context/'])
    
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

def is_ignored(path, patterns, root_dir):
    rel_path = os.path.relpath(path, root_dir)
    if rel_path == '.':
        return False
    
    # Normalize path separators to /
    rel_path = rel_path.replace(os.sep, '/')
    name = os.path.basename(path)
    
    for pattern in patterns:
        # Handle directory-specific patterns (ending with /)
        if pattern.endswith('/'):
            if fnmatch.fnmatch(rel_path + '/', pattern) or fnmatch.fnmatch(name + '/', pattern):
                return True
        # Handle standard patterns
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False

def generate_tree(structure, prefix=""):
    lines = []
    keys = sorted(structure.keys())
    for i, key in enumerate(keys):
        is_last = (i == len(keys) - 1)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{key}")
        
        if isinstance(structure[key], dict):
            extension = "    " if is_last else "│   "
            lines.extend(generate_tree(structure[key], prefix + extension))
    return lines

def scan_summary(root_dir, ignore_patterns, follow_symlinks, exclude_standard, script_file):
    """
    快速扫描生成项目摘要（第一遍扫描）
    返回: {
        "total_files": int,
        "total_dirs": int,
        "max_depth": int,
        "empty_dirs": [...]
    }
    """
    stats = {"files": 0, "dirs": 0, "max_depth": 0}
    empty_dirs = []
    
    # 构建排除模式
    all_patterns = ignore_patterns + ['.git']
    if exclude_standard:
        standard_patterns = get_standard_exclude_patterns(root_dir, script_file)
        for p in standard_patterns:
            if isinstance(p, tuple):
                all_patterns.append(p[0])
            else:
                all_patterns.append(p)
    
    gitignore_patterns = load_gitignore_patterns(root_dir)
    all_patterns.extend(gitignore_patterns)
    
    processed_dirs = set()
    queue = deque([(root_dir, 0)])
    
    while queue:
        current_path, depth = queue.popleft()
        
        if not follow_symlinks and os.path.islink(current_path):
            continue
        
        real_path = os.path.realpath(current_path)
        if real_path in processed_dirs:
            continue
        processed_dirs.add(real_path)
        
        stats["max_depth"] = max(stats["max_depth"], depth)
        
        try:
            entries = os.listdir(current_path)
        except (PermissionError, Exception):
            continue
        
        # 检查是否为空目录
        has_content = False
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if is_ignored(full_path, all_patterns, root_dir):
                continue
            has_content = True
            
            if os.path.isdir(full_path):
                stats["dirs"] += 1
                queue.append((full_path, depth + 1))
            else:
                stats["files"] += 1
        
        # 记录空目录
        if not has_content and current_path != root_dir:
            rel_path = os.path.relpath(current_path, root_dir)
            empty_dirs.append(rel_path.replace(os.sep, '/') + '/')
    
    # 返回统一键名的结果
    return {
        "total_files": stats["files"],
        "total_dirs": stats["dirs"],
        "max_depth": stats["max_depth"],
        "empty_dirs": empty_dirs
    }

def assess_complexity(summary):
    """
    根据摘要评估项目复杂度
    返回: "basic" | "medium" | "advanced"
    """
    total_files = summary["total_files"]
    
    if total_files <= 500:
        return "basic"
    elif total_files <= 2000:
        return "medium"
    else:
        return "advanced"

def scan_project(root_dir, ignore_patterns, follow_symlinks, max_files_per_dir, max_depth, 
                 exclude_standard=False, script_file=None, limit_dirs=None, advanced_dir_threshold=20):
    """
    扫描项目目录树
    
    参数:
        limit_dirs: 每目录最多显示的子目录数（None表示无限制）
        advanced_dir_threshold: 高级模式智能判断阈值，当子目录数≤此值时保留所有目录名
    """
    structure = {}
    stats = {"files": 0, "dirs": 0}
    excluded_info = []  # 新增：记录排除信息
    
    # Queue for BFS: (current_path, current_depth, parent_structure_dict)
    queue = deque([(root_dir, 0, structure)])
    
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

    processed_dirs = set()

    while queue:
        current_path, depth, parent_dict = queue.popleft()
        
        if max_depth is not None and depth > max_depth:
            continue
            
        if not follow_symlinks and os.path.islink(current_path):
            continue
            
        real_path = os.path.realpath(current_path)
        if real_path in processed_dirs:
            continue
        processed_dirs.add(real_path)

        try:
            # 获取所有条目
            entries = os.listdir(current_path)
        except PermissionError:
            sys.stderr.write(f"Warning: Permission denied accessing {current_path}\n")
            continue
        except Exception as e:
            sys.stderr.write(f"Warning: Error accessing {current_path}: {e}\n")
            continue

        # 分离文件和目录
        files = []
        dirs = []
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if is_ignored(full_path, all_patterns, root_dir):
                continue
            
            if os.path.isdir(full_path):
                if not follow_symlinks and os.path.islink(full_path):
                    files.append(entry)  # Symlink dir treated as file
                else:
                    dirs.append(entry)
            else:
                files.append(entry)
        
        # 智能排序
        sorted_files = sort_files_by_importance(files)
        sorted_dirs = sort_dirs_by_importance(dirs)
        
        # ===== 处理目录（应用智能子判断）=====
        dir_limit = limit_dirs if limit_dirs is not None else float('inf')
        
        # 智能子判断：如果子目录数量≤阈值，保留所有目录名但不展开
        if limit_dirs is not None and len(sorted_dirs) <= advanced_dir_threshold and len(sorted_dirs) > 0:
            # 保留所有目录名，但只显示文件数量统计，不展开子目录
            for entry in sorted_dirs:
                full_path = os.path.join(current_path, entry)
                # 快速统计该目录的文件数
                try:
                    subdir_files = [f for f in os.listdir(full_path) 
                                   if os.path.isfile(os.path.join(full_path, f)) 
                                   and not is_ignored(os.path.join(full_path, f), all_patterns, root_dir)]
                    parent_dict[entry] = f"({len(subdir_files)} files)"
                    stats["dirs"] += 1
                except:
                    parent_dict[entry] = "(无法访问)"
                    stats["dirs"] += 1
        else:
            # 正常处理：应用限制
            for i, entry in enumerate(sorted_dirs):
                full_path = os.path.join(current_path, entry)
                
                if i < dir_limit:
                    new_dict = {}
                    parent_dict[entry] = new_dict
                    stats["dirs"] += 1
                    queue.append((full_path, depth + 1, new_dict))
                elif i == dir_limit:
                    # 添加省略提示（包含使用建议）
                    rel_path = os.path.relpath(current_path, root_dir).replace(os.sep, '/')
                    if rel_path == '.':
                        rel_path = ''
                    omitted_count = len(sorted_dirs) - dir_limit
                    suggestion = f"使用 --path ./{rel_path} --limit-dirs {len(sorted_dirs)} 查看更多" if rel_path else f"使用 --limit-dirs {len(sorted_dirs)} 查看更多"
                    parent_dict[f"... (省略 {omitted_count} 个子目录, {suggestion})"] = None
                    break
        
        # 处理文件（应用限制）
        for i, entry in enumerate(sorted_files):
            full_path = os.path.join(current_path, entry)
            
            if i < max_files_per_dir:
                # 检查是否为symlink目录
                if os.path.isdir(full_path) and os.path.islink(full_path):
                    parent_dict[entry] = "[Symlink Dir]"
                else:
                    parent_dict[entry] = None  # 普通文件
                stats["files"] += 1
            elif i == max_files_per_dir:
                # 添加省略提示（包含使用建议）
                rel_path = os.path.relpath(current_path, root_dir).replace(os.sep, '/')
                omitted_count = len(sorted_files) - max_files_per_dir
                suggestion = f"使用 --path ./{rel_path} --no-adaptive 查看完整列表"
                parent_dict[f"... (省略 {omitted_count} 个文件, {suggestion})"] = None
                break

    return structure, stats, excluded_info  # 修改返回值

def collect_xcode_project_metadata(root_dir):
    """收集 Swift/Xcode 项目中容易被浅层目录扫描漏掉的关键文件。"""
    dependency_manifest_candidates = []
    xcode_project_files = []
    platform_config_files = []

    for current_root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        rel_root = os.path.relpath(current_root, root_dir).replace(os.sep, "/")
        if rel_root == ".":
            rel_root = ""
        for filename in files:
            rel_path = f"{rel_root}/{filename}" if rel_root else filename
            if filename == "Package.resolved" and "/xcshareddata/swiftpm/" in f"/{rel_path}":
                dependency_manifest_candidates.append(rel_path)
            elif filename == "project.pbxproj" and ".xcodeproj/" in f"{rel_path}/":
                xcode_project_files.append(rel_path)
            elif filename == "Info.plist" or filename.endswith(".entitlements"):
                platform_config_files.append(rel_path)

    return {
        "dependency_manifest_candidates": sorted(dependency_manifest_candidates),
        "xcode_project_files": sorted(xcode_project_files),
        "platform_config_files": sorted(platform_config_files),
    }

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Project Structure Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan (default: current directory)")
    
    # 输出模式
    parser.add_argument("--mode", choices=["tree", "summary", "auto"], default="auto",
                        help="Output mode: tree(file tree), summary(summary only), auto(adaptive)")
    
    # 复杂度控制
    parser.add_argument("--complexity-override", choices=["basic", "medium", "advanced"],
                        help="Manually specify complexity level, override auto-detection")
    
    # 限制参数
    parser.add_argument("--limit-files", type=int, default=10,
                        help="Max files to display per directory in medium/advanced mode (default: 10)")
    parser.add_argument("--limit-dirs", type=int, default=10,
                        help="Max subdirectories to display per directory in advanced mode (default: 10)")
    
    # 自适应控制
    parser.add_argument("--no-adaptive", action="store_true",
                        help="Disable adaptive mechanism, always output full tree")
    parser.add_argument("--advanced-dir-threshold", type=int, default=20,
                        help="Subdirectory count threshold in advanced mode (default: 20)")
    
    # 原有参数
    parser.add_argument("--ignore", help="Comma-separated glob patterns to ignore")
    parser.add_argument("--exclude-standard", action="store_true",
                        help="Exclude standard patterns (framework, deps, IDE)")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    parser.add_argument("--max-files", type=int, default=1000, help="Max files per directory (legacy, use --limit-files)")
    parser.add_argument("--depth", type=int, help="Max scan depth")
    parser.add_argument("--format", choices=["json", "tree"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.path)
    ignore_patterns = args.ignore.split(",") if args.ignore else []
    
    # ===== 参数优先级处理 =====
    # 1. --no-adaptive 最高优先级
    if args.no_adaptive:
        if args.complexity_override or args.limit_files != 10 or args.limit_dirs != 10:
            sys.stderr.write("Warning: --no-adaptive is enabled, other limit parameters will be ignored\n")
        complexity = 'basic'
        limit_files = float('inf')
        limit_dirs = float('inf')
    else:
        # 2. 执行摘要扫描（第一遍）
        summary = scan_summary(root_dir, ignore_patterns, args.follow_symlinks, 
                              args.exclude_standard, __file__)
        
        # 3. 评估复杂度或使用手动指定
        complexity = args.complexity_override or assess_complexity(summary)
        
        # 4. 根据复杂度确定限制参数
        if complexity == 'basic':
            limit_files = float('inf')
            limit_dirs = float('inf')
        elif complexity == 'medium':
            limit_files = args.limit_files
            limit_dirs = float('inf')  # 中级不限制目录
        else:  # advanced
            limit_files = args.limit_files
            limit_dirs = args.limit_dirs
    
    # ===== 根据模式输出 =====
    if args.mode == "summary":
        # 只输出摘要
        if args.no_adaptive:
            # 如果--no-adaptive，需要完整扫描获取准确摘要
            summary = scan_summary(root_dir, ignore_patterns, args.follow_symlinks,
                                  args.exclude_standard, __file__)
        
        elapsed_time = round(time.time() - start_time, 2)
        xcode_metadata = collect_xcode_project_metadata(root_dir)
        result = {
            "data": {
                "summary": {
                    "total_files": summary["total_files"],
                    "total_dirs": summary["total_dirs"],
                    "max_depth": summary["max_depth"],
                    "complexity_level": complexity,
                    "empty_dirs_count": len(summary.get("empty_dirs", [])),
                    "empty_dirs": summary.get("empty_dirs", [])
                },
                **xcode_metadata,
            },
            "metadata": {
                "mode": "summary",
                "elapsed_seconds": elapsed_time,
                "version": "1.3.0"
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:  # tree 或 auto 模式
        # 执行第二遍扫描生成树结构
        structure, stats, excluded_info = scan_project(
            root_dir,
            ignore_patterns,
            args.follow_symlinks,
            int(limit_files) if limit_files != float('inf') else args.max_files,
            args.depth,
            args.exclude_standard,
            __file__,
            limit_dirs=int(limit_dirs) if limit_dirs != float('inf') else None,
            advanced_dir_threshold=args.advanced_dir_threshold
        )
        
        elapsed_time = round(time.time() - start_time, 2)
        xcode_metadata = collect_xcode_project_metadata(root_dir)
        
        # 获取摘要（用于metadata）
        if not args.no_adaptive and 'summary' in locals():
            empty_dirs = summary.get("empty_dirs", [])
            empty_dirs_count = len(empty_dirs)
        else:
            empty_dirs = []
            empty_dirs_count = 0
        
        if args.format == "json":
            # 构建输出策略描述
            if args.no_adaptive:
                output_strategy = "full_tree"
            elif complexity == 'basic':
                output_strategy = "full_tree"
            elif complexity == 'medium':
                output_strategy = "limited_files_with_smart_sort"
            else:
                output_strategy = "limited_dirs_and_files_with_smart_judgment"
            
            result = {
                "data": {"structure": structure, "stats": stats, **xcode_metadata},
                "metadata": {
                    "mode": "tree",
                    "complexity_level": complexity,
                    "output_strategy": output_strategy,
                    "limit_files": args.limit_files if not args.no_adaptive else None,
                    "limit_dirs": args.limit_dirs if not args.no_adaptive and complexity == 'advanced' else None,
                    "empty_dirs_count": empty_dirs_count,
                    "empty_dirs": empty_dirs[:10] if len(empty_dirs) > 10 else empty_dirs,  # 最多显示10个
                    "elapsed_seconds": elapsed_time,
                    "timeout_threshold": 10,
                    "version": "1.3.0",
                    "excluded_patterns": excluded_info,
                    "excluded_count": len(excluded_info)
                }
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:  # tree format
            tree_lines = generate_tree(structure)
            print("\n".join(tree_lines))
            print(f"\nStats: {stats['files']} files, {stats['dirs']} directories")
            print(f"Complexity: {complexity}")
            if empty_dirs_count > 0:
                print(f"Empty directories: {empty_dirs_count}")
            print(f"Excluded: {len(excluded_info)} patterns")
            print(f"Elapsed: {elapsed_time}s")

if __name__ == "__main__":
    main()
