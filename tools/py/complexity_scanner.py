"""
复杂度扫描工具 - 用于监控项目复杂度增长
作为 005 优化点的核心实施工具

功能说明：
- 调用 git_diff_analyzer.py 分析代码变更
- 调用 git_inspector.py 检查仓库状态
- 分析依赖关系和代码质量
- 计算复杂度评分
- 输出标准化 JSON 格式数据

使用方法：
    python tools/py/complexity_scanner.py [--path PATH] [--output OUTPUT] [--since SINCE] [--config CONFIG]

参数说明：
    --path PATH              扫描路径（默认：当前目录）
    --output OUTPUT          输出文件路径（默认：stdout）
    --since SINCE            分析时间窗口（默认：1 day ago）
                            支持格式：
                            - 绝对时间："2026-04-12"
                            - 相对时间："1 day ago"、"7 days ago"、"24 hours ago"
    --config CONFIG          配置文件路径（默认：dev_docs/complexity/config.yaml）

输出格式：
    {
      "data": {
        "code_size": {
          "new_lines": 450,
          "total_lines": 19850,
          "files": 120,
          "growth_percentage": 2.3
        },
        "dependencies": {
          "new": 3,
          "duplicate": 2,
          "depth": 4
        },
        "code_quality": {
          "todo_count": 8,
          "fixme_count": 3,
          "duplicate_code": 8,
          "quality_score": 72
        },
        "architecture": {
          "core_files_changed": 2,
          "coupling_score": 22,
          "domain_boundary_score": 7
        },
        "risk_assessment": {
          "overall_score": 75,
          "risks": [
            {"level": "high", "indicator": "growth_rate", "message": "代码增长过快"}
          ]
        }
      },
      "metadata": {
        "elapsed_seconds": 1.2,
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }

使用示例：
    # 扫描当前项目（输出到文件）
    python tools/py/complexity_scanner.py --path . --output data.json

    # 分析最近 7 天的复杂度增长
    python tools/py/complexity_scanner.py --since "7 days ago"

    # 使用自定义配置
    python tools/py/complexity_scanner.py --config custom_config.yaml

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
"""

import subprocess
import json
import sys
import time
import argparse
# yaml 解析（简单实现，避免依赖）
def parse_yaml(text):
    """简单的 YAML 解析，只支持单层结构"""
    try:
        result = {}
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ':' in line and not line.endswith(':'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # 尝试解析数值
                if value.isdigit():
                    result[key] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    result[key] = float(value)
                elif value.lower() in ['true', 'false']:
                    result[key] = value.lower() == 'true'
                else:
                    result[key] = value

        return result
    except Exception as e:
        print(f"YAML parse error: {e}")
        return None
import os
import re


def run_command(cmd):
    """执行命令并返回结果"""
    try:
        # 找到项目根目录
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(script_dir)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
            cwd=project_root
        )
        return result.stdout.strip()
    except Exception as e:
        return None


def call_git_diff_analyzer(since):
    """调用 git_diff_analyzer.py 获取代码变更数据"""
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "git_diff_analyzer.py"
    )
    cmd = [
        "python3" if sys.executable else "python",
        script_path,
        "--since", since
    ]

    output = run_command(cmd)
    if output:
        try:
            return json.loads(output)
        except:
            return None
    return None


def call_git_inspector():
    """调用 git_inspector.py 检查仓库状态"""
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "git_inspector.py"
    )
    cmd = [
        "python3" if sys.executable else "python",
        script_path,
        "--mode", "status"
    ]

    output = run_command(cmd)
    if output:
        try:
            return json.loads(output)
        except:
            return None
    return None


def analyze_dependencies(path):
    """分析依赖关系"""
    dependencies = {
        "new": 0,
        "duplicate": 0,
        "depth": 0
    }

    # 简单的依赖分析（MVP 版本）
    if os.path.exists(os.path.join(path, "package.json")):
        try:
            with open(os.path.join(path, "package.json"), "r", encoding="utf-8") as f:
                package_data = json.load(f)
                dependencies["depth"] = 1  # 简化处理
                # 检查是否有重复依赖（简化）
                if "dependencies" in package_data:
                    dependencies["new"] = len(package_data["dependencies"])
        except:
            pass

    if os.path.exists(os.path.join(path, "requirements.txt")):
        try:
            with open(os.path.join(path, "requirements.txt"), "r", encoding="utf-8") as f:
                requirements = [line.strip() for line in f if line.strip()]
                dependencies["depth"] = max(dependencies["depth"], 1)
                if dependencies["new"] == 0:
                    dependencies["new"] = len(requirements)
        except:
            pass

    return dependencies


def analyze_code_quality(path):
    """分析代码质量"""
    quality = {
        "todo_count": 0,
        "fixme_count": 0,
        "duplicate_code": 0,
        "quality_score": 100
    }

    todo_pattern = re.compile(r"TODO|todo|Todo")
    fixme_pattern = re.compile(r"FIXME|fixme|Fixme")

    # 扫描常见源代码目录
    src_dirs = ["src", "lib", "app", "components"]

    for root, dirs, files in os.walk(path):
        # 排除不需要扫描的目录
        if ".git" in root or "node_modules" in root or "dist" in root or "build" in root:
            continue

        # 只检查源代码文件
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        quality["todo_count"] += len(todo_pattern.findall(content))
                        quality["fixme_count"] += len(fixme_pattern.findall(content))
                except:
                    continue

    # 简单的质量评分计算
    quality["quality_score"] = max(0, min(100, 100 - quality["todo_count"] * 2 - quality["fixme_count"] * 3))

    return quality


def analyze_review_data(path, git_data):
    """分析代码审查数据"""
    review_data = {
        "changes": {
            "added_lines": 0,
            "removed_lines": 0,
            "changed_files": 0,
            "core_files_changed": 0
        },
        "todo_changes": {
            "added": 0,
            "removed": 0
        },
        "dangerous_patterns": [],
        "api_changes": [],
        "risk_level": "low"
    }

    # 获取 git 变更数据
    if git_data and "data" in git_data:
        changed_files = git_data["data"].get("changed_files", [])
        review_data["changes"]["changed_files"] = len(changed_files)

        # 统计新增/删除代码行数（简化计算）
        for file in changed_files:
            if "lines_changed" in file:
                review_data["changes"]["added_lines"] += file["lines_changed"]

        # 识别核心文件变更
        core_files = ["package.json", "requirements.txt", "README.md", "tsconfig.json"]
        for file in changed_files:
            if any(core_file in file["path"] for core_file in core_files):
                review_data["changes"]["core_files_changed"] += 1

    # 分析危险模式
    review_data["dangerous_patterns"] = analyze_dangerous_patterns(path, git_data)

    # 分析 TODO 标记变化
    review_data["todo_changes"] = analyze_todo_changes(path)

    # 计算风险级别
    review_data["risk_level"] = calculate_review_risk(review_data)

    return review_data


def analyze_dangerous_patterns(path, git_data):
    """分析危险模式"""
    dangerous_patterns = []
    config = load_config("")

    # 危险函数模式匹配
    dangerous_functions = config.get("review", {}).get("dangerous_functions", [])
    function_patterns = [re.compile(rf"{func}\s*\(") for func in dangerous_functions]

    # 扫描源代码文件
    for root, dirs, files in os.walk(path):
        if ".git" in root or "node_modules" in root or "dist" in root or "build" in root:
            continue

        for file in files:
            if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()

                        for func, pattern in zip(dangerous_functions, function_patterns):
                            if pattern.search(content):
                                dangerous_patterns.append({
                                    "type": "dangerous_function",
                                    "function": func,
                                    "file": os.path.join(root, file),
                                    "severity": "critical"
                                })
                except:
                    continue

    # 检查大文件变更
    large_file_threshold = config.get("review", {}).get("large_file_threshold", 500)
    if git_data and "data" in git_data:
        for file in git_data["data"].get("changed_files", []):
            if "lines_changed" in file and file["lines_changed"] > large_file_threshold:
                dangerous_patterns.append({
                    "type": "large_file_change",
                    "file": file["path"],
                    "lines_changed": file["lines_changed"],
                    "severity": "warning"
                })

    return dangerous_patterns


def analyze_todo_changes(path):
    """分析 TODO 标记变化"""
    todo_changes = {
        "added": 0,
        "removed": 0
    }

    # 获取git diff分析TODO变化
    try:
        # 获取上次提交和当前的diff
        git_diff = run_command(["git", "diff", "HEAD~1", "HEAD"])
        if git_diff:
            # 解析diff中的TODO变化
            todo_pattern = re.compile(r"[+-].*?(TODO|todo|Todo)")
            lines = git_diff.split('\n')
            for line in lines:
                if line.startswith('+') and todo_pattern.search(line):
                    todo_changes["added"] += 1
                elif line.startswith('-') and todo_pattern.search(line):
                    todo_changes["removed"] += 1
    except:
        pass

    return todo_changes


def calculate_review_risk(review_data):
    """计算审查风险级别"""
    config = load_config("")
    risk_level = "low"

    # 检查危险函数
    if any(p["severity"] == "critical" for p in review_data["dangerous_patterns"]):
        risk_level = "critical"
    # 检查 TODO 标记过多
    elif review_data["todo_changes"]["added"] > config.get("review", {}).get("todo_warning_threshold", 3):
        risk_level = "warning"
    # 检查大文件变更
    elif any(p["lines_changed"] > config.get("review", {}).get("large_file_threshold", 500) for p in review_data["dangerous_patterns"]):
        risk_level = "warning"
    # 检查核心文件变更
    elif review_data["changes"]["core_files_changed"] > 0:
        risk_level = "medium"

    return risk_level


def analyze_architecture(path, git_data):
    """分析架构健康度"""
    architecture = {
        "core_files_changed": 0,
        "coupling_score": 0,
        "domain_boundary_score": 7
    }

    core_files = ["package.json", "requirements.txt", "README.md", "tsconfig.json"]

    if git_data and "data" in git_data and "changed_files" in git_data["data"]:
        for file in git_data["data"]["changed_files"]:
            if any(core_file in file["path"] for core_file in core_files):
                architecture["core_files_changed"] += 1

    return architecture


def calculate_risk_assessment(data, config):
    """计算风险评估"""
    risk_assessment = {
        "overall_score": 0,
        "risks": []
    }

    # 综合评分（简单加权）
    overall_score = (
        data["code_size"].get("growth_percentage", 0) * 0.3 +
        data["dependencies"].get("depth", 0) * 0.2 +
        (100 - data["code_quality"].get("quality_score", 0)) * 0.3 +
        data["architecture"].get("coupling_score", 0) * 0.2
    )

    risk_assessment["overall_score"] = max(0, min(100, 100 - overall_score))

    # 风险识别
    if data["code_size"].get("growth_percentage", 0) > config.get("warning_threshold", {}).get("daily_growth", 5):
        risk_assessment["risks"].append({
            "level": "high" if data["code_size"]["growth_percentage"] > 10 else "medium",
            "indicator": "growth_rate",
            "message": f"代码增长过快 ({data['code_size']['growth_percentage']:.1f}%, 建议 <{config['warning_threshold']['daily_growth']}%)"
        })

    if data["dependencies"].get("depth", 0) > config.get("warning_threshold", {}).get("dependency_depth", 3):
        risk_assessment["risks"].append({
            "level": "medium",
            "indicator": "dependency_depth",
            "message": f"依赖深度超标 ({data['dependencies']['depth']}, 建议 <{config['warning_threshold']['dependency_depth']})"
        })

    if data["code_quality"].get("quality_score", 100) < config.get("warning_threshold", {}).get("quality_score", 70):
        risk_assessment["risks"].append({
            "level": "medium" if data["code_quality"]["quality_score"] > 60 else "high",
            "indicator": "code_quality",
            "message": f"代码质量评分低 ({data['code_quality']['quality_score']}, 建议 >{config['warning_threshold']['quality_score']})"
        })

    if data["architecture"].get("coupling_score", 0) > config.get("warning_threshold", {}).get("coupling_score", 20):
        risk_assessment["risks"].append({
            "level": "medium",
            "indicator": "coupling_score",
            "message": f"代码耦合度过高 ({data['architecture']['coupling_score']}, 建议 <{config['warning_threshold']['coupling_score']})"
        })

    return risk_assessment


def load_config(config_path):
    """加载配置文件"""
    # 默认配置
    default_config = {
        "warning_threshold": {
            "daily_growth": 5,
            "file_count": 150,
            "dependency_depth": 3,
            "quality_score": 70,
            "coupling_score": 20
        },
        "critical_threshold": {
            "daily_growth": 10,
            "file_count": 200,
            "dependency_depth": 5,
            "quality_score": 60,
            "coupling_score": 30
        },
        "crisis_threshold": {
            "daily_growth": 15,
            "file_count": 300,
            "dependency_depth": 7,
            "quality_score": 50,
            "coupling_score": 40
        },
        "review": {
            "dangerous_functions": [
                "eval",
                "exec",
                "Function"
            ],
            "large_file_threshold": 500,
            "todo_warning_threshold": 3,
            "todo_critical_threshold": 5,
            "notification": {
                "level": "warning",
                "channels": [
                    "slack",
                    "email"
                ]
            }
        }
    }

    # 尝试从配置文件加载
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 使用简单的YAML解析
                parsed_config = parse_yaml(content)
                if parsed_config:
                    # 合并配置（用户配置覆盖默认配置）
                    def merge_configs(default, user):
                        result = default.copy()
                        for key, value in user.items():
                            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                                result[key] = merge_configs(result[key], value)
                            else:
                                result[key] = value
                        return result
                    return merge_configs(default_config, parsed_config)
        except Exception as e:
            print(f"Warning: 无法加载配置文件 {config_path}, 使用默认配置: {e}")

    return default_config


def main():
    start_time = time.time()

    parser = argparse.ArgumentParser(description="复杂度扫描工具")
    parser.add_argument("--path", default=".", help="扫描路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--since", default="1 day ago", help="分析时间窗口")
    parser.add_argument("--config", default="dev_docs/complexity/config.yaml", help="配置文件路径")

    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)

    # 调用现有工具获取数据
    git_diff_data = call_git_diff_analyzer(args.since)
    git_inspector_data = call_git_inspector()

    # 初始化结果
    complexity_data = {
        "code_size": {
            "new_lines": 0,
            "total_lines": 0,
            "files": 0,
            "growth_percentage": 0
        },
        "dependencies": analyze_dependencies(args.path),
        "code_quality": analyze_code_quality(args.path),
        "architecture": analyze_architecture(args.path, git_diff_data),
        "review_data": analyze_review_data(args.path, git_diff_data),  # 新增代码审查数据
        "risk_assessment": {}
    }

    # 处理 git 变更数据
    if git_diff_data and "data" in git_diff_data:
        # 统计新增行数（简化计算）
        new_lines = 0
        total_files_changed = len(git_diff_data["data"].get("changed_files", []))

        for file in git_diff_data["data"].get("changed_files", []):
            if "lines_changed" in file:
                new_lines += file["lines_changed"]

        # 计算代码增长百分比（简化）
        growth_percentage = new_lines / 20000 * 100 if new_lines > 0 else 0

        complexity_data["code_size"] = {
            "new_lines": new_lines,
            "total_lines": 20000,  # 简化：使用估计值
            "files": total_files_changed,
            "growth_percentage": min(growth_percentage, 20)  # 上限保护
        }

    # 计算风险评估
    complexity_data["risk_assessment"] = calculate_risk_assessment(complexity_data, config)

    elapsed_time = round(time.time() - start_time, 2)

    result = {
        "data": complexity_data,
        "metadata": {
            "elapsed_seconds": elapsed_time,
            "timeout_threshold": 10,
            "version": "1.0.0",
            "git_available": git_inspector_data is not None
        }
    }

    # 输出结果
    if args.output:
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing output to {args.output}: {e}")
            return
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
