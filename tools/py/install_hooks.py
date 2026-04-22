#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Hooks 安装脚本 (Git Hooks Installer)

功能说明:
1. 自动检测 Git 仓库根目录
2. 安装 pre-commit hook (提交前检查)
3. 安装 post-commit hook (提交后生成复杂度报告)
4. 设置正确的执行权限
5. 提供卸载选项和备份恢复机制

使用方法:
    # 安装所有 hooks
    python tools/py/install_hooks.py

    # 仅安装 pre-commit hook
    python tools/py/install_hooks.py --pre-commit

    # 仅安装 post-commit hook
    python tools/py/install_hooks.py --post-commit

    # 卸载所有 hooks
    python tools/py/install_hooks.py --uninstall

    # 显示帮助信息
    python tools/py/install_hooks.py --help

参数说明:
    --pre-commit    仅安装 pre-commit hook
    --post-commit   仅安装 post-commit hook
    --uninstall, -u 卸载所有 hooks (支持备份恢复)
    --help, -h      显示详细使用说明

输出格式:
    文本输出，包含以下信息:
    - Git 仓库路径
    - 安装/卸载操作结果
    - 备份文件路径 (如适用)
    - 错误提示和解决方案

使用示例:
    # 示例 1: 首次安装 hooks
    python tools/py/install_hooks.py

    # 示例 2: 重新安装 pre-commit hook
    python tools/py/install_hooks.py --pre-commit

    # 示例 3: 卸载 hooks 并恢复备份
    python tools/py/install_hooks.py --uninstall
    # 然后根据提示选择是否恢复备份

Hook 功能说明:

pre-commit Hook:
    - Commit message 格式检查
    - WHAT/WHY/HOW 字段验证
    - 保护分支检测
    - 分支命名规范检查
    - Commit 质量评分
    - 复杂度增量检查 (拦截高风险变更)

post-commit Hook:
    - 自动扫描项目复杂度
    - 生成 Markdown 报告到 dev_docs/complexity/reports/
    - 可选生成 HTML 仪表盘
    - 数据文件保存到 dev_docs/complexity/data/

跳过 Hook (紧急情况):
    git commit --no-verify  # 跳过所有 pre-commit 检查

版本信息:
    版本: 1.0.0
    更新日期: 2026-04-12
"""

import os
import sys
import shutil
import stat
from pathlib import Path


def find_git_root():
    """查找 Git 仓库根目录"""
    current = Path.cwd()

    while current != current.parent:
        git_dir = current / '.git'
        if git_dir.exists():
            return current
        current = current.parent

    return None


def install_hook(git_root, hook_name):
    """安装指定的 hook"""
    hooks_dir = git_root / '.git' / 'hooks'
    hooks_dir.mkdir(parents=True, exist_ok=True)

    source_hook = git_root / 'tools' / 'git-hooks' / hook_name
    target_hook = hooks_dir / hook_name

    if not source_hook.exists():
        print(f"❌ 源文件不存在: {source_hook}")
        return False

    # 检查是否已存在
    if target_hook.exists():
        response = input(f"⚠️ {target_hook} 已存在,是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print(f"❌ 取消安装 {hook_name}")
            return False

        # 备份现有 hook
        backup = target_hook.with_suffix('.backup')
        shutil.copy2(target_hook, backup)
        print(f"📦 已备份现有 hook 到: {backup}")

    # 复制文件
    shutil.copy2(source_hook, target_hook)

    # 设置执行权限 (Unix/Linux/macOS)
    if os.name != 'nt':  # 非 Windows
        target_hook.chmod(target_hook.stat().st_mode | stat.S_IEXEC)

    print(f"✅ {hook_name} 已安装到: {target_hook}")
    return True


def install_pre_commit_hook(git_root):
    """安装 pre-commit hook"""
    return install_hook(git_root, 'pre-commit')


def install_post_commit_hook(git_root):
    """安装 post-commit hook"""
    return install_hook(git_root, 'post-commit')


def uninstall_hook(git_root, hook_name):
    """卸载指定的 hook"""
    target_hook = git_root / '.git' / 'hooks' / hook_name

    if not target_hook.exists():
        print(f"ℹ️ {hook_name} 未安装")
        return True

    # 检查是否有备份
    backup = target_hook.with_suffix('.backup')
    if backup.exists():
        response = input(f"📦 发现 {hook_name} 备份文件,是否恢复? (y/N): ")
        if response.lower() == 'y':
            shutil.copy2(backup, target_hook)
            backup.unlink()
            print(f"✅ 已恢复备份: {target_hook}")
            return True

    # 删除 hook
    target_hook.unlink()
    print(f"✅ {hook_name} 已卸载: {target_hook}")
    return True


def uninstall_pre_commit_hook(git_root):
    """卸载 pre-commit hook"""
    return uninstall_hook(git_root, 'pre-commit')


def uninstall_post_commit_hook(git_root):
    """卸载 post-commit hook"""
    return uninstall_hook(git_root, 'post-commit')


def show_usage():
    """显示使用说明"""
    print("""
╔══════════════════════════════════════════════════════════╗
║  Git Hooks 安装工具                                      ║
╚══════════════════════════════════════════════════════════╝

功能:
  • 自动安装 pre-commit hook
  • 在 commit 前检查 message 格式
  • 验证 Git 安全规范
  • 提供质量评分和改进建议
  • 安装 post-commit hook 自动生成复杂度报告

使用方式:
  python tools/py/install_hooks.py              # 安装所有 hooks
  python tools/py/install_hooks.py --pre-commit  # 仅安装 pre-commit
  python tools/py/install_hooks.py --post-commit # 仅安装 post-commit
  python tools/py/install_hooks.py --uninstall   # 卸载所有 hooks

Pre-commit Hook 功能:
  ✓ Commit message 格式检查
  ✓ WHAT/WHY/HOW 字段验证
  ✓ 保护分支检测
  ✓ 分支命名规范检查
  ✓ Commit 质量评分
  ✓ 复杂度增量检查 (拦截高风险变更)

Post-commit Hook 功能:
  ✓ 自动扫描项目复杂度
  ✓ 生成 Markdown 报告
  ✓ 生成 HTML 仪表盘
  ✓ 数据保存到 dev_docs/complexity/

跳过 Hook:
  git commit --no-verify  # 紧急情况下跳过检查
""")


def main():
    """主函数"""
    # 解析参数
    uninstall = '--uninstall' in sys.argv or '-u' in sys.argv
    show_help = '--help' in sys.argv or '-h' in sys.argv
    install_pre = '--pre-commit' in sys.argv
    install_post = '--post-commit' in sys.argv

    if show_help:
        show_usage()
        return 0

    # 查找 Git 仓库
    git_root = find_git_root()
    if not git_root:
        print("❌ 错误: 未找到 Git 仓库")
        print("   请在 Git 仓库根目录或子目录中运行此脚本")
        return 1

    print(f"📂 Git 仓库: {git_root}")

    # 执行安装或卸载
    success = True

    if uninstall:
        print("🛠️ 卸载所有 hooks...")
        success = uninstall_pre_commit_hook(git_root) and uninstall_post_commit_hook(git_root)
    else:
        # 确定要安装的 hooks
        install_all = not (install_pre or install_post)

        if install_all or install_pre:
            print("🛠️ 安装 pre-commit hook...")
            success = success and install_pre_commit_hook(git_root)

        if (install_all or install_post) and success:
            print("\n🛠️ 安装 post-commit hook...")
            success = success and install_post_commit_hook(git_root)

    if success:
        if not uninstall:
            print("\n💡 提示:")
            print("   • Hook 已激活,下次 commit 时自动检查和报告")
            print("   • 紧急情况可使用: git commit --no-verify")
            print("   • 卸载 hook: python tools/py/install_hooks.py --uninstall")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
