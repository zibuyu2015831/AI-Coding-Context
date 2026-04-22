#!/usr/bin/env python3
"""
AICC 知识库管理 CLI 工具 (Python 版本)

功能说明:
- status: 查看知识库状态
- config: 配置共享知识库
- enable-shared: 启用共享知识库
- disable-shared: 禁用共享知识库
- update-shared: 从远程更新共享知识库
- strategy: 设置匹配策略
- init: 初始化本地知识库为共享知识库
- publish: 发布本地共享知识库到云端

使用方法:
    # 查看知识库状态
    python tools/py/knowledge_cli.py status

    # 配置共享知识库
    python tools/py/knowledge_cli.py config --shared https://github.com/org/shared-knowledge.git

    # 启用/禁用共享知识库
    python tools/py/knowledge_cli.py enable-shared
    python tools/py/knowledge_cli.py disable-shared

    # 更新共享知识库
    python tools/py/knowledge_cli.py update-shared [--force]

    # 设置匹配策略
    python tools/py/knowledge_cli.py strategy --mode [local-first|shared-first|hybrid]

    # 初始化本地知识库为共享仓库
    python tools/py/knowledge_cli.py init --as-shared [--force]

    # 发布本地知识库到云端
    python tools/py/knowledge_cli.py publish --remote https://github.com/org/shared-knowledge.git

参数说明:
    status              查看知识库配置和同步状态
    config              配置共享知识库
      --shared URL      共享知识库 Git 地址
      --branch NAME     分支名称 (默认: main)
      --depth N         克隆深度 (可选)
      --force           强制重新配置
    enable-shared       启用共享知识库
    disable-shared      禁用共享知识库
    update-shared       从远程更新共享知识库
      --force           强制更新，忽略本地变更
    strategy            设置知识匹配策略
      --mode STRATEGY   策略模式: local-first, shared-first, hybrid
    init                初始化本地知识库为共享仓库
      --as-shared       标记为共享知识库 (必需)
      --force           强制重新初始化
    publish             发布本地知识库到云端
      --remote URL      远程仓库地址
      --branch NAME     分支名称 (默认: main)
      --force           强制推送

输出格式:
    文本输出，包含以下信息:
    - 知识库状态 (本地/共享/启用/禁用)
    - 仓库地址和分支信息
    - 最近更新时间
    - 匹配策略配置
    - 操作结果 (成功/失败)

使用示例:
    # 示例 1: 配置并启用共享知识库
    python tools/py/knowledge_cli.py config --shared https://github.com/org/knowledge.git
    python tools/py/knowledge_cli.py enable-shared
    python tools/py/knowledge_cli.py update-shared

    # 示例 2: 初始化项目知识库
    python tools/py/knowledge_cli.py init --as-shared
    python tools/py/knowledge_cli.py publish --remote https://github.com/org/my-knowledge.git

    # 示例 3: 切换匹配策略
    python tools/py/knowledge_cli.py strategy --mode shared-first

版本信息:
    版本: 1.0.0
    更新日期: 2026-04-16
"""

import os
import sys
import json
import subprocess
import argparse
import time
import datetime
from typing import Dict, Any, Optional, List

# --- 配置常量 ---
CONFIG_DIR = ".aicc"
CONFIG_FILE = os.path.join(CONFIG_DIR, "knowledge_config.json")  # 使用 JSON 保证零依赖兼容性
CACHE_DIR = ".aicc-cache"
SHARED_KNOWLEDGE_DIR = os.path.join(CACHE_DIR, "shared-knowledge")
DEFAULT_LOCAL_PATH = "dev_docs/knowledge"

# --- 辅助函数 ---
def print_success(msg: str):
    print(f"✅ {msg}")

def print_error(msg: str):
    print(f"❌ {msg}", file=sys.stderr)

def print_warning(msg: str):
    print(f"⚠️ {msg}")

def print_info(msg: str):
    print(f"ℹ️ {msg}")

def run_command(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except FileNotFoundError:
        print_error(f"找不到命令: {cmd[0]}")
        sys.exit(1)

# --- 核心类 ---

class ConfigManager:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FILE):
            return {
                "knowledge": {
                    "local_path": DEFAULT_LOCAL_PATH,
                    "shared": {
                        "enabled": False,
                        "repo_url": "",
                        "branch": "main",
                        "cache_path": SHARED_KNOWLEDGE_DIR,
                        "last_updated": ""
                    },
                    "match_strategy": "local-first",
                    "match_threshold": 0.6
                }
            }
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print_warning(f"无法读取配置文件: {e}，使用默认配置。")
            return ConfigManager.load_config()

    @staticmethod
    def save_config(config: Dict[str, Any]):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    @staticmethod
    def update_gitignore():
        gitignore_path = ".gitignore"
        entry = f"{CACHE_DIR}/"
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if entry not in content:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n# AICC 知识库缓存\n{entry}\n")
                print_info(f"已将 {entry} 添加到 .gitignore")
        else:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(f"# AICC 知识库缓存\n{entry}\n")
            print_info(f"已创建 .gitignore 并添加 {entry}")

class GitRepository:
    def __init__(self, repo_url: str, cache_path: str, branch: str = 'main'):
        self.repo_url = repo_url
        self.cache_path = cache_path
        self.branch = branch

    def clone_or_update(self, force: bool = False, depth: Optional[int] = None):
        if os.path.exists(self.cache_path) and os.path.exists(os.path.join(self.cache_path, ".git")):
            if force:
                print_info("正在强制更新共享知识库...")
                res = run_command(["git", "fetch", "--all"], cwd=self.cache_path)
                res = run_command(["git", "reset", "--hard", f"origin/{self.branch}"], cwd=self.cache_path)
            else:
                print_info("正在同步共享知识库...")
                res = run_command(["git", "pull", "origin", self.branch], cwd=self.cache_path)

            if res.returncode != 0:
                print_error(f"更新失败: {res.stderr}")
                return False
            return True
        else:
            print_info(f"正在克隆共享知识库到 {self.cache_path}...")
            if not os.path.exists(os.path.dirname(self.cache_path)):
                os.makedirs(os.path.dirname(self.cache_path))

            cmd = ["git", "clone", self.repo_url, self.cache_path, "--branch", self.branch]
            if depth:
                cmd.extend(["--depth", str(depth)])

            res = run_command(cmd)
            if res.returncode != 0:
                print_error(f"克隆失败: {res.stderr}")
                return False
            return True

class KnowledgeCLI:
    def __init__(self):
        self.config = ConfigManager.load_config()

    def status(self):
        print("\n📚 知识库配置状态")
        local_path = self.config["knowledge"].get("local_path", DEFAULT_LOCAL_PATH)
        local_exists = os.path.exists(local_path)
        print(f"  本地知识库: {'✅' if local_exists else '❌'} {local_path}")

        shared = self.config["knowledge"]["shared"]
        if shared["repo_url"]:
            enabled = shared.get("enabled", False)
            print(f"  共享知识库: {'✅ 已启用' if enabled else '⚠️ 已禁用'}")
            print(f"    仓库地址: {shared['repo_url']}")
            print(f"    分支: {shared['branch']}")
            print(f"    最近更新: {shared.get('last_updated', '从不')}")
        else:
            print("  共享知识库: ❌ 未配置")

        print(f"  匹配策略: {self.config['knowledge'].get('match_strategy', 'local-first')}")
        print("")

    def config_shared(self, repo_url: str, branch: str = 'main', depth: Optional[int] = None, force: bool = False):
        self.config["knowledge"]["shared"]["repo_url"] = repo_url
        self.config["knowledge"]["shared"]["branch"] = branch
        self.config["knowledge"]["shared"]["enabled"] = True

        repo = GitRepository(repo_url, SHARED_KNOWLEDGE_DIR, branch)
        if repo.clone_or_update(force=force, depth=depth):
            self.config["knowledge"]["shared"]["last_updated"] = datetime.datetime.now().isoformat()
            ConfigManager.save_config(self.config)
            ConfigManager.update_gitignore()
            print_success("共享知识库配置成功！")
        else:
            print_error("共享知识库配置失败。")

    def enable_shared(self):
        if not self.config["knowledge"]["shared"]["repo_url"]:
            print_error("未配置共享知识库，请先运行 config 命令。")
            return
        self.config["knowledge"]["shared"]["enabled"] = True
        ConfigManager.save_config(self.config)
        print_success("共享知识库已启用")

    def disable_shared(self):
        self.config["knowledge"]["shared"]["enabled"] = False
        ConfigManager.save_config(self.config)
        print_warning("共享知识库已禁用")

    def update_shared(self, force: bool = False):
        shared = self.config["knowledge"]["shared"]
        if not shared["repo_url"]:
            print_error("未配置共享知识库。")
            return

        repo = GitRepository(shared["repo_url"], SHARED_KNOWLEDGE_DIR, shared["branch"])
        if repo.clone_or_update(force=force):
            self.config["knowledge"]["shared"]["last_updated"] = datetime.datetime.now().isoformat()
            ConfigManager.save_config(self.config)
            print_success("共享知识库已更新")
        else:
            print_error("更新失败。")

    def set_strategy(self, mode: str):
        valid_modes = ["local-first", "shared-first", "hybrid"]
        if mode not in valid_modes:
            print_error(f"无效的策略模式。可选值: {', '.join(valid_modes)}")
            return
        self.config["knowledge"]["match_strategy"] = mode
        ConfigManager.save_config(self.config)
        print_success(f"知识匹配策略已切换为: {mode}")

    def init_shared(self, force: bool = False):
        local_path = self.config["knowledge"].get("local_path", DEFAULT_LOCAL_PATH)
        if not os.path.exists(local_path):
            os.makedirs(local_path)
            print_info(f"已创建目录: {local_path}")

        # 标准结构
        subdirs = ["fundamentals", "languages", "frameworks", "platforms", "databases", "case-studies"]
        for sd in subdirs:
            path = os.path.join(local_path, sd)
            if not os.path.exists(path):
                os.makedirs(path)

        # .aicc 目录在 local_path 下用于元数据
        meta_dir = os.path.join(local_path, ".aicc")
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)

        meta_file = os.path.join(meta_dir, "metadata.json")
        if not os.path.exists(meta_file) or force:
            metadata = {
                "name": os.path.basename(os.getcwd()),
                "version": "1.0.0",
                "description": "Shared Knowledge Repository",
                "author": "",
                "created_at": datetime.datetime.now().isoformat()
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        # git init
        if not os.path.exists(os.path.join(local_path, ".git")):
            run_command(["git", "init"], cwd=local_path)
            print_info("已在本地知识库目录初始化 Git 仓库")

        print_success(f"本地知识库已初始化为共享知识库标准结构: {local_path}")

    def publish(self, remote_url: str, branch: str = 'main', force: bool = False):
        local_path = self.config["knowledge"].get("local_path", DEFAULT_LOCAL_PATH)
        if not os.path.exists(os.path.join(local_path, ".git")):
            print_error("本地知识库未初始化为 Git 仓库，请先运行 init 命令。")
            return

        # 检查是否有提交
        res = run_command(["git", "status", "--porcelain"], cwd=local_path)
        if res.stdout.strip():
            print_warning("检测到未提交的变更，正在自动提交...")
            run_command(["git", "add", "."], cwd=local_path)
            run_command(["git", "commit", "-m", "chore: sync knowledge repository"], cwd=local_path)

        # 检查远程
        res = run_command(["git", "remote", "get-url", "origin"], cwd=local_path)
        if res.returncode != 0:
            run_command(["git", "remote", "add", "origin", remote_url], cwd=local_path)
        else:
            old_url = res.stdout.strip()
            if old_url != remote_url:
                run_command(["git", "remote", "set-url", "origin", remote_url], cwd=local_path)

        # 推送
        print_info(f"正在发布到 {remote_url} [{branch}]...")
        cmd = ["git", "push", "-u", "origin", branch]
        if force:
            cmd.append("-f")
        res = run_command(cmd, cwd=local_path)

        if res.returncode == 0:
            print_success("知识库发布成功！")
        else:
            print_error(f"发布失败: {res.stderr}")

def main():
    cli = KnowledgeCLI()
    parser = argparse.ArgumentParser(description="📚 AICC 知识库管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # Status
    subparsers.add_parser("status", help="查看知识库配置状态")

    # Config
    parser_config = subparsers.add_parser("config", help="配置共享知识库")
    parser_config.add_argument("--shared", required=True, help="Git 仓库地址")
    parser_config.add_argument("--branch", default="main", help="分支 (默认: main)")
    parser_config.add_argument("--depth", type=int, help="克隆深度")
    parser_config.add_argument("--force", action="store_true", help="强制重新配置")

    # Enable/Disable
    subparsers.add_parser("enable-shared", help="启用共享知识库")
    subparsers.add_parser("disable-shared", help="禁用共享知识库")

    # Update
    parser_update = subparsers.add_parser("update-shared", help="从远程更新共享知识库")
    parser_update.add_argument("--force", action="store_true", help="强制更新，忽略本地变更")

    # Strategy
    parser_strategy = subparsers.add_parser("strategy", help="配置知识匹配策略")
    parser_strategy.add_argument("--mode", required=True, choices=["local-first", "shared-first", "hybrid"], help="策略模式")

    # Init
    parser_init = subparsers.add_parser("init", help="初始化本地知识库为共享仓库")
    parser_init.add_argument("--as-shared", action="store_true", required=True, help="标记为共享知识库")
    parser_init.add_argument("--force", action="store_true", help="强制重新初始化")

    # Publish
    parser_publish = subparsers.add_parser("publish", help="发布本地共享知识库到云端")
    parser_publish.add_argument("--remote", required=True, help="远程仓库地址")
    parser_publish.add_argument("--branch", default="main", help="分支 (默认: main)")
    parser_publish.add_argument("--force", action="store_true", help="强制推送")

    args = parser.parse_args()

    if args.command == "status":
        cli.status()
    elif args.command == "config":
        cli.config_shared(args.shared, args.branch, args.depth, args.force)
    elif args.command == "enable-shared":
        cli.enable_shared()
    elif args.command == "disable-shared":
        cli.disable_shared()
    elif args.command == "update-shared":
        cli.update_shared(args.force)
    elif args.command == "strategy":
        cli.set_strategy(args.mode)
    elif args.command == "init":
        cli.init_shared(args.force)
    elif args.command == "publish":
        cli.publish(args.remote, args.branch, args.force)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
