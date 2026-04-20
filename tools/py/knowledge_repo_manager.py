#!/usr/bin/env python3
"""
知识库仓库管理器 - 管理跨项目知识库的创建、同步和版本控制

功能说明:
    - 初始化知识库仓库结构
    - 管理知识库版本控制
    - 同步远程知识库
    - 生成知识库索引

使用方法:
    # 初始化知识库
    python tools/py/knowledge_repo_manager.py --init --path .knowledge

    # 添加知识条目
    python tools/py/knowledge_repo_manager.py --add --type pattern --title "Repository Pattern"

    # 同步远程知识库
    python tools/py/knowledge_repo_manager.py --sync --remote-url https://github.com/org/shared-knowledge.git

版本信息:
    Version: 1.0.0
    Created: 2026-04-20
    Purpose: Support 010-Cross Project Knowledge Reuse
"""

import os
import re
import json
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
DEFAULT_KNOWLEDGE_DIR = ".knowledge"


def init_knowledge_repo(path: str, remote_url: str = "") -> dict:
    """初始化知识库仓库"""
    try:
        os.makedirs(path, exist_ok=True)

        # 创建目录结构
        categories = [
            "fundamentals",
            "languages",
            "frameworks",
            "platforms",
            "databases",
            "case-studies"
        ]

        for cat in categories:
            os.makedirs(os.path.join(path, cat), exist_ok=True)

        # 创建 .aicc 配置目录
        aicc_dir = os.path.join(path, ".aicc")
        os.makedirs(aicc_dir, exist_ok=True)

        # 创建 metadata.json
        metadata = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "remote_url": remote_url,
            "branch": "main",
            "total_entries": 0,
            "categories": categories
        }

        with open(os.path.join(aicc_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # 创建 README.md
        readme_content = f"""# 共享知识库

**版本**: {metadata['version']}
**创建时间**: {metadata['created_at']}

## 目录结构

```
{path}/
├── fundamentals/      # 基础知识（语言无关、通用原则）
├── languages/         # 编程语言特定知识
├── frameworks/        # 框架特定知识
├── platforms/         # 平台特定知识
├── databases/         # 数据库特定知识
└── case-studies/      # 完整案例研究
```

## 知识类型

- **规范性知识**: 架构模式、编码规范、流程规范
- **问题解决型知识**: 常见错误、调试方法、性能优化
- **决策型知识**: 技术选型、架构决策、权衡分析
- **经验型知识**: 最佳实践、反模式、经验教训

## 使用说明

1. 知识条目使用 YAML Frontmatter 格式
2. 确保添加正确的分类和标签
3. 定期同步远程仓库获取更新
"""

        with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

        # 初始化 Git 仓库
        try:
            subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path, check=True, capture_output=True)
        except Exception as e:
            print(f"Git 初始化警告: {e}", file=sys.stderr)

        return {
            "success": True,
            "path": path,
            "categories": categories,
            "metadata": metadata
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def sync_knowledge_repo(local_path: str, remote_url: str = "", branch: str = "main") -> dict:
    """同步知识库"""
    try:
        if not os.path.exists(os.path.join(local_path, ".git")):
            return {
                "success": False,
                "error": "本地知识库不是 Git 仓库"
            }

        # 检查是否有远程仓库配置
        if remote_url:
            # 添加或更新远程仓库
            try:
                subprocess.run(
                    ["git", "remote", "add", "origin", remote_url],
                    cwd=local_path, check=True, capture_output=True
                )
            except subprocess.CalledProcessError:
                # 远程已存在，更新 URL
                subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    cwd=local_path, check=True, capture_output=True
                )

        # 拉取远程更新
        try:
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=local_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "merge", f"origin/{branch}"],
                cwd=local_path, check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"同步失败: {e.stderr.decode() if e.stderr else str(e)}"
            }

        # 更新 metadata
        metadata_path = os.path.join(local_path, ".aicc", "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            metadata["updated_at"] = datetime.now().isoformat()
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "message": "同步成功",
            "branch": branch
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_index(path: str) -> dict:
    """生成知识库索引"""
    try:
        index = {
            "generated_at": datetime.now().isoformat(),
            "entries": []
        }

        for root, dirs, files in os.walk(path):
            # 跳过 .git 和 .aicc 目录
            dirs[:] = [d for d in dirs if d not in {".git", ".aicc"}]

            for file in files:
                if file.endswith(".md") and file != "README.md":
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)

                    # 提取 Frontmatter
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 简单解析 Frontmatter
                        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                        if match:
                            yaml_content = match.group(1)
                            # 简单解析 YAML
                            entry = {"file": rel_path}
                            for line in yaml_content.split("\n"):
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    key = key.strip()
                                    value = value.strip().strip('"\'')
                                    if key in ["title", "category", "tags", "description", "created_at"]:
                                        entry[key] = value
                            index["entries"].append(entry)
                    except Exception as e:
                        print(f"解析 {file_path} 失败: {e}", file=sys.stderr)

        # 保存索引
        index_path = os.path.join(path, ".aicc", "index.json")
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "total_entries": len(index["entries"]),
            "index_path": index_path
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description="知识库仓库管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--init", action="store_true", help="初始化知识库")
    parser.add_argument("--sync", action="store_true", help="同步知识库")
    parser.add_argument("--generate-index", action="store_true", help="生成索引")
    parser.add_argument("--path", default=DEFAULT_KNOWLEDGE_DIR, help=f"知识库路径, 默认 {DEFAULT_KNOWLEDGE_DIR}")
    parser.add_argument("--remote-url", default="", help="远程仓库 URL")
    parser.add_argument("--branch", default="main", help="分支名称")

    args = parser.parse_args()

    result = {"success": False, "action": None}

    if args.init:
        result = init_knowledge_repo(args.path, args.remote_url)
        result["action"] = "init"
    elif args.sync:
        result = sync_knowledge_repo(args.path, args.remote_url, args.branch)
        result["action"] = "sync"
    elif args.generate_index:
        result = generate_index(args.path)
        result["action"] = "generate_index"
    else:
        result["error"] = "请指定操作: --init, --sync, 或 --generate-index"

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
