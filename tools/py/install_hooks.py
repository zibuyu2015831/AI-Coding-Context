#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Hooks 安装脚本

功能:
1. 自动检测 Git 仓库
2. 安装 pre-commit hook
3. 设置正确的执行权限
4. 提供卸载选项

使用方式:
  python tools/py/install_hooks.py          # 安装 hooks
  python tools/py/install_hooks.py --uninstall  # 卸载 hooks
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


def install_pre_commit_hook(git_root):
    """安装 pre-commit hook"""
    hooks_dir = git_root / '.git' / 'hooks'
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    source_hook = git_root / 'tools' / 'git-hooks' / 'pre-commit'
    target_hook = hooks_dir / 'pre-commit'
    
    if not source_hook.exists():
        print(f"❌ 源文件不存在: {source_hook}")
        return False
    
    # 检查是否已存在
    if target_hook.exists():
        response = input(f"⚠️ {target_hook} 已存在,是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("❌ 取消安装")
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
    
    print(f"✅ Pre-commit hook 已安装到: {target_hook}")
    return True


def uninstall_pre_commit_hook(git_root):
    """卸载 pre-commit hook"""
    target_hook = git_root / '.git' / 'hooks' / 'pre-commit'
    
    if not target_hook.exists():
        print("ℹ️ Pre-commit hook 未安装")
        return True
    
    # 检查是否有备份
    backup = target_hook.with_suffix('.backup')
    if backup.exists():
        response = input("📦 发现备份文件,是否恢复? (y/N): ")
        if response.lower() == 'y':
            shutil.copy2(backup, target_hook)
            backup.unlink()
            print(f"✅ 已恢复备份: {target_hook}")
            return True
    
    # 删除 hook
    target_hook.unlink()
    print(f"✅ Pre-commit hook 已卸载: {target_hook}")
    return True


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

使用方式:
  python tools/py/install_hooks.py           # 安装
  python tools/py/install_hooks.py --uninstall  # 卸载

Hook 功能:
  ✓ Commit message 格式检查
  ✓ WHAT/WHY/HOW 字段验证
  ✓ 保护分支检测
  ✓ 分支命名规范检查
  ✓ Commit 质量评分

跳过 Hook:
  git commit --no-verify  # 紧急情况下跳过检查
""")


def main():
    """主函数"""
    # 解析参数
    uninstall = '--uninstall' in sys.argv or '-u' in sys.argv
    show_help = '--help' in sys.argv or '-h' in sys.argv
    
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
    if uninstall:
        success = uninstall_pre_commit_hook(git_root)
    else:
        success = install_pre_commit_hook(git_root)
    
    if success:
        if not uninstall:
            print("\n💡 提示:")
            print("   • Hook 已激活,下次 commit 时自动检查")
            print("   • 紧急情况可使用: git commit --no-verify")
            print("   • 卸载 hook: python tools/py/install_hooks.py --uninstall")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
