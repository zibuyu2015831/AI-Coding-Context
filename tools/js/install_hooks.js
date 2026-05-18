#!/usr/bin/env node
/**
 * Git Hooks 安装脚本 - Node.js 版本
 * 
 * 功能说明：
 * - 自动检测 Git 仓库根目录
 * - 安装 pre-commit hook (提交前检查)
 * - 安装 post-commit hook (提交后生成复杂度报告)
 * - 设置正确的执行权限（Unix/Linux/macOS）
 * - 提供卸载选项，支持备份恢复
 * - 跨平台兼容（Windows, macOS, Linux）
 * 
 * 使用方法：
 *   node tools/js/install_hooks.js              # 安装所有 hooks
 *   node tools/js/install_hooks.js --pre-commit  # 仅安装 pre-commit
 *   node tools/js/install_hooks.js --post-commit # 仅安装 post-commit
 *   node tools/js/install_hooks.js --uninstall  # 卸载 hooks
 *   node tools/js/install_hooks.js --help       # 显示帮助
 * 
 * 参数说明：
 *   --help, -h        显示使用说明
 *   --uninstall, -u   卸载已安装的 hook
 *   --pre-commit      仅安装 pre-commit hook
 *   --post-commit     仅安装 post-commit hook
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2026-04-22
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const os = require('os');
const { execSync } = require('child_process');

/**
 * 查找 Git 仓库根目录
 */
function findGitRoot() {
    let current = process.cwd();
    while (true) {
        const gitDir = path.join(current, '.git');
        if (fs.existsSync(gitDir)) return current;
        const parent = path.dirname(current);
        if (parent === current) return null;
        current = parent;
    }
}

/**
 * 询问用户确认
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
 * 设置文件为可执行
 */
function setExecutable(filePath) {
    if (os.platform() !== 'win32') {
        try {
            const stats = fs.statSync(filePath);
            fs.chmodSync(filePath, stats.mode | 0o111);
        } catch (error) {
            console.log(`⚠️  警告: 无法设置执行权限: ${error.message}`);
        }
    }
}

/**
 * 安装指定的 hook
 */
async function installHook(gitRoot, hookName) {
    const hooksDir = path.join(gitRoot, '.git', 'hooks');
    const sourceHook = path.join(gitRoot, 'tools', 'git-hooks', hookName);
    const targetHook = path.join(hooksDir, hookName);
    
    if (!fs.existsSync(sourceHook)) {
        console.log(`❌ 源文件不存在: ${sourceHook}`);
        return false;
    }
    
    if (!fs.existsSync(hooksDir)) {
        fs.mkdirSync(hooksDir, { recursive: true });
    }
    
    if (fs.existsSync(targetHook)) {
        const confirmed = await askConfirmation(`⚠️  ${targetHook} 已存在,是否覆盖? (y/N): `);
        if (!confirmed) {
            console.log(`❌ 取消安装 ${hookName}`);
            return false;
        }
        
        const backup = targetHook + '.backup';
        try {
            fs.copyFileSync(targetHook, backup);
            console.log(`📦 已备份现有 hook 到: ${backup}`);
        } catch (error) {
            console.log(`⚠️  警告: 无法创建备份: ${error.message}`);
        }
    }
    
    try {
        fs.copyFileSync(sourceHook, targetHook);
        setExecutable(targetHook);
        console.log(`✅ ${hookName} 已安装到: ${targetHook}`);
        return true;
    } catch (error) {
        console.log(`❌ 安装失败: ${error.message}`);
        return false;
    }
}

/**
 * 卸载指定的 hook
 */
async function uninstallHook(gitRoot, hookName) {
    const targetHook = path.join(gitRoot, '.git', 'hooks', hookName);
    if (!fs.existsSync(targetHook)) {
        console.log(`ℹ️  ${hookName} 未安装`);
        return true;
    }
    
    const backup = targetHook + '.backup';
    if (fs.existsSync(backup)) {
        const confirmed = await askConfirmation(`📦 发现 ${hookName} 备份文件,是否恢复? (y/N): `);
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
    
    try {
        fs.unlinkSync(targetHook);
        console.log(`✅ ${hookName} 已卸载`);
        return true;
    } catch (error) {
        console.log(`❌ 卸载失败: ${error.message}`);
        return false;
    }
}

function showUsage() {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║  Git Hooks 安装工具 (Node.js)                            ║
╚══════════════════════════════════════════════════════════╝

Hook 功能:
  • 自动安装 pre-commit / post-commit hooks
  • 在 commit 前检查 message 格式和代码合规性
  • 在 commit 后自动触发复杂度报告生成
  • 跨平台支持

使用方式:
  node tools/js/install_hooks.js              # 安装所有 hooks
  node tools/js/install_hooks.js --pre-commit  # 仅安装 pre-commit
  node tools/js/install_hooks.js --post-commit # 仅安装 post-commit
  node tools/js/install_hooks.js --uninstall   # 卸载所有 hooks

跳过 Hook:
  git commit --no-verify  # 紧急情况下跳过检查
`);
}

async function main() {
    const args = process.argv.slice(2);
    const uninstall = args.includes('--uninstall') || args.includes('-u');
    const showHelp = args.includes('--help') || args.includes('-h');
    const installPre = args.includes('--pre-commit');
    const installPost = args.includes('--post-commit');
    const installAll = !uninstall && !installPre && !installPost;

    if (showHelp) {
        showUsage();
        process.exit(0);
    }

    const gitRoot = findGitRoot();
    if (!gitRoot) {
        console.log('❌ 错误: 未找到 Git 仓库');
        process.exit(1);
    }

    console.log(`📂 Git 仓库: ${gitRoot}`);

    let success = true;
    if (uninstall) {
        console.log('🛠️ 卸载所有 hooks...');
        success = await uninstallHook(gitRoot, 'pre-commit') && await uninstallHook(gitRoot, 'post-commit');
    } else {
        if (installAll || installPre) {
            console.log('🛠️ 安装 pre-commit hook...');
            success = await installHook(gitRoot, 'pre-commit');
        }
        if ((installAll || installPost) && success) {
            console.log('\n🛠️ 安装 post-commit hook...');
            success = await installHook(gitRoot, 'post-commit');
        }
    }

    if (success && !uninstall) {
        console.log('\n💡 提示:');
        console.log('   • Hooks 已激活');
        console.log('   • 卸载: node tools/js/install_hooks.js --uninstall');
    }
    process.exit(success ? 0 : 1);
}

if (require.main === module) {
    main().catch(e => {
        console.error('❌ 发生错误:', e.message);
        process.exit(1);
    });
}

module.exports = {
    findGitRoot,
    setExecutable,
    installHook,
    uninstallHook,
};
