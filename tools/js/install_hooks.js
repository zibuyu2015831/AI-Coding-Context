#!/usr/bin/env node
/**
 * Git Hooks 安装脚本 - Node.js 版本
 * 
 * 功能说明：
 * - 自动检测 Git 仓库根目录
 * - 安装 pre-commit hook 到 .git/hooks/
 * - 设置正确的执行权限（Unix/Linux/macOS）
 * - 提供卸载选项，支持备份恢复
 * - 跨平台兼容（Windows, macOS, Linux）
 * 
 * 使用方法：
 *   node tools/js/install_hooks.js              # 安装 hooks
 *   node tools/js/install_hooks.js --uninstall  # 卸载 hooks
 *   node tools/js/install_hooks.js --help       # 显示帮助
 * 
 * 参数说明：
 *   --help, -h        显示使用说明
 *   --uninstall, -u   卸载已安装的 hook
 * 
 * 使用示例：
 *   # 示例 1: 安装 pre-commit hook
 *   node tools/js/install_hooks.js
 * 
 *   # 示例 2: 卸载 hook
 *   node tools/js/install_hooks.js --uninstall
 * 
 *   # 示例 3: 查看帮助信息
 *   node tools/js/install_hooks.js --help
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-19
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const os = require('os');

/**
 * 查找 Git 仓库根目录
 * @returns {string|null} Git 仓库根目录路径，未找到返回 null
 */
function findGitRoot() {
    let current = process.cwd();
    
    while (true) {
        const gitDir = path.join(current, '.git');
        if (fs.existsSync(gitDir)) {
            return current;
        }
        
        const parent = path.dirname(current);
        if (parent === current) {
            // 已到达根目录
            return null;
        }
        current = parent;
    }
}

/**
 * 询问用户确认
 * @param {string} question - 问题文本
 * @returns {Promise<boolean>} 用户是否确认（输入 'y' 返回 true）
 */
function askConfirmation(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer.trim().toLowerCase() === 'y');
        });
    });
}

/**
 * 设置文件为可执行（仅 Unix/Linux/macOS）
 * @param {string} filePath - 文件路径
 */
function setExecutable(filePath) {
    if (os.platform() !== 'win32') {
        try {
            const stats = fs.statSync(filePath);
            fs.chmodSync(filePath, stats.mode | 0o111); // +x for user, group, others
        } catch (error) {
            console.log(`⚠️  警告: 无法设置执行权限: ${error.message}`);
        }
    }
}

/**
 * 安装 pre-commit hook
 * @param {string} gitRoot - Git 仓库根目录
 * @returns {Promise<boolean>} 安装是否成功
 */
async function installPreCommitHook(gitRoot) {
    const hooksDir = path.join(gitRoot, '.git', 'hooks');
    const sourceHook = path.join(gitRoot, 'tools', 'git-hooks', 'pre-commit');
    const targetHook = path.join(hooksDir, 'pre-commit');
    
    // 检查源文件是否存在
    if (!fs.existsSync(sourceHook)) {
        console.log(`❌ 源文件不存在: ${sourceHook}`);
        return false;
    }
    
    // 确保 hooks 目录存在
    if (!fs.existsSync(hooksDir)) {
        fs.mkdirSync(hooksDir, { recursive: true });
    }
    
    // 检查目标文件是否已存在
    if (fs.existsSync(targetHook)) {
        const confirmed = await askConfirmation(`⚠️  ${targetHook} 已存在,是否覆盖? (y/N): `);
        if (!confirmed) {
            console.log('❌ 取消安装');
            return false;
        }
        
        // 备份现有 hook
        const backup = targetHook + '.backup';
        try {
            fs.copyFileSync(targetHook, backup);
            console.log(`📦 已备份现有 hook 到: ${backup}`);
        } catch (error) {
            console.log(`⚠️  警告: 无法创建备份: ${error.message}`);
        }
    }
    
    // 复制文件
    try {
        fs.copyFileSync(sourceHook, targetHook);
    } catch (error) {
        console.log(`❌ 复制文件失败: ${error.message}`);
        return false;
    }
    
    // 设置执行权限
    setExecutable(targetHook);
    
    console.log(`✅ Pre-commit hook 已安装到: ${targetHook}`);
    return true;
}

/**
 * 卸载 pre-commit hook
 * @param {string} gitRoot - Git 仓库根目录
 * @returns {Promise<boolean>} 卸载是否成功
 */
async function uninstallPreCommitHook(gitRoot) {
    const targetHook = path.join(gitRoot, '.git', 'hooks', 'pre-commit');
    
    if (!fs.existsSync(targetHook)) {
        console.log('ℹ️  Pre-commit hook 未安装');
        return true;
    }
    
    // 检查是否有备份
    const backup = targetHook + '.backup';
    if (fs.existsSync(backup)) {
        const confirmed = await askConfirmation('📦 发现备份文件,是否恢复? (y/N): ');
        if (confirmed) {
            try {
                fs.copyFileSync(backup, targetHook);
                fs.unlinkSync(backup);
                console.log(`✅ 已恢复备份: ${targetHook}`);
                return true;
            } catch (error) {
                console.log(`❌ 恢复备份失败: ${error.message}`);
                return false;
            }
        }
    }
    
    // 删除 hook
    try {
        fs.unlinkSync(targetHook);
        console.log(`✅ Pre-commit hook 已卸载: ${targetHook}`);
        return true;
    } catch (error) {
        console.log(`❌ 删除文件失败: ${error.message}`);
        return false;
    }
}

/**
 * 显示使用说明
 */
function showUsage() {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║  Git Hooks 安装工具                                       ║
╚══════════════════════════════════════════════════════════╝

功能:
  • 自动安装 pre-commit hook
  • 在 commit 前检查 message 格式
  • 验证 Git 安全规范
  • 提供质量评分和改进建议

使用方式:
  node tools/js/install_hooks.js           # 安装
  node tools/js/install_hooks.js --uninstall  # 卸载

Hook 功能:
  ✓ Commit message 格式检查
  ✓ WHAT/WHY/HOW 字段验证
  ✓ 保护分支检测
  ✓ 分支命名规范检查
  ✓ Commit 质量评分

跳过 Hook:
  git commit --no-verify  # 紧急情况下跳过检查
`);
}

/**
 * 主函数
 */
async function main() {
    // 解析参数
    const args = process.argv.slice(2);
    const uninstall = args.includes('--uninstall') || args.includes('-u');
    const showHelp = args.includes('--help') || args.includes('-h');
    
    if (showHelp) {
        showUsage();
        process.exit(0);
    }
    
    // 查找 Git 仓库
    const gitRoot = findGitRoot();
    if (!gitRoot) {
        console.log('❌ 错误: 未找到 Git 仓库');
        console.log('   请在 Git 仓库根目录或子目录中运行此脚本');
        process.exit(1);
    }
    
    console.log(`📂 Git 仓库: ${gitRoot}`);
    
    // 执行安装或卸载
    let success;
    if (uninstall) {
        success = await uninstallPreCommitHook(gitRoot);
    } else {
        success = await installPreCommitHook(gitRoot);
    }
    
    if (success) {
        if (!uninstall) {
            console.log('\n💡 提示:');
            console.log('   • Hook 已激活,下次 commit 时自动检查');
            console.log('   • 紧急情况可使用: git commit --no-verify');
            console.log('   • 卸载 hook: node tools/js/install_hooks.js --uninstall');
        }
        process.exit(0);
    } else {
        process.exit(1);
    }
}

// 执行主函数
if (require.main === module) {
    main().catch((error) => {
        console.error('❌ 发生错误:', error.message);
        process.exit(1);
    });
}

// 导出函数供测试使用
module.exports = {
    findGitRoot,
    installPreCommitHook,
    uninstallPreCommitHook,
    askConfirmation,
    setExecutable
};
