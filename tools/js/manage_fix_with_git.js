/**
 * Git 集成修复管理器 - 使用 Git 版本控制管理文档修复流程
 *
 * 功能说明:
 *     - 检查 Git 工作区状态
 *     - 创建修复分支进行隔离修复
 *     - 执行修复操作并自动提交
 *     - 支持修复历史记录和回滚
 *     - 提供安全机制防止数据丢失
 *
 * 使用方法:
 *     // 检查 Git 状态
 *     node tools/js/manage_fix_with_git.js --check-status
 *
 *     // 开始修复流程（创建分支并切换）
 *     node tools/js/manage_fix_with_git.js --start --branch-name "doc-fix-001"
 *
 *     // 提交修复
 *     node tools/js/manage_fix_with_git.js --commit --message "修复 API 函数名错误"
 *
 *     // 查看修复历史
 *     node tools/js/manage_fix_with_git.js --history
 *
 *     // 查看特定提交详细信息
 *     node tools/js/manage_fix_with_git.js --show-commit "a1b2c3d"
 *
 *     // 回滚到修复前状态
 *     node tools/js/manage_fix_with_git.js --rollback --commit-hash "a1b2c3d"
 *
 *     // 完成修复（合并到主分支）
 *     node tools/js/manage_fix_with_git.js --finish
 *
 * 参数说明:
 *     --check-status          检查 Git 工作区状态
 *     --start                 开始修复流程（创建分支）
 *     --branch-name NAME      修复分支名称（默认: doc-fix-YYYYMMDD）
 *     --commit                提交修复
 *     --message MSG           提交信息
 *     --history               查看修复历史
 *     --show-commit HASH      查看特定提交详细信息
 *     --rollback              回滚到指定提交
 *     --commit-hash HASH      目标提交哈希
 *     --finish                完成修复（合并到主分支）
 *     --main-branch NAME      主分支名称（默认: main）
 *     --doc-dir PATH          文档目录（默认: dev_docs/）
 *     --verbose               输出详细信息
 *
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-13
 *     Purpose: Support 011-Document Error Fix Workflow
 */

const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { EOL } = require('os');

const VERSION = "1.0.0";
const DEFAULT_DOC_DIR = "dev_docs";
const DEFAULT_MAIN_BRANCH = "main";

function runGitCommand(cmd, cwd = process.cwd()) {
    /**
     * 执行 Git 命令
     *
     * Args:
     *     cmd: Git 命令列表
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 包含 success, output, error 的结果
     */
    try {
        const command = `git ${cmd.join(' ')}`;
        const output = execSync(command, { cwd, encoding: 'utf-8' });
        return {
            success: true,
            output: output.trim(),
            error: '',
            returncode: 0
        };
    } catch (err) {
        return {
            success: false,
            output: err.stdout?.toString().trim() || '',
            error: err.stderr?.toString().trim() || '',
            returncode: err.status || -1
        };
    }
}

function checkGitStatus(cwd = process.cwd()) {
    /**
     * 检查 Git 工作区状态
     *
     * Args:
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: Git 状态信息
     */
    // 检查是否为 Git 仓库
    const result = runGitCommand(['rev-parse', '--is-inside-work-tree'], cwd);
    if (!result.success) {
        return {
            isGitRepo: false,
            isClean: false,
            currentBranch: null,
            status: 'not_a_git_repo',
            error: result.error
        };
    }

    // 获取当前分支
    const branchResult = runGitCommand(['branch', '--show-current'], cwd);
    const currentBranch = branchResult.success ? branchResult.output : null;

    // 检查工作区状态
    const statusResult = runGitCommand(['status', '--porcelain'], cwd);
    const isClean = statusResult.output.trim().length === 0;

    return {
        isGitRepo: true,
        isClean: isClean,
        currentBranch: currentBranch,
        status: isClean ? 'clean' : 'dirty',
        statusOutput: statusResult.output
    };
}

function createFixBranch(branchName = null, cwd = process.cwd()) {
    /**
     * 创建修复分支
     *
     * Args:
     *     branchName: 分支名称
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 分支创建结果
     */
    if (!branchName) {
        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/[-T:]/g, '') + now.getMilliseconds();
        branchName = `doc-fix-${timestamp}`;
    }

    // 检查当前分支
    const status = checkGitStatus(cwd);
    if (!status.isGitRepo) {
        return { success: false, error: 'Not a Git repository' };
    }

    // 创建并切换到新分支
    const result = runGitCommand(['checkout', '-b', branchName], cwd);

    if (result.success) {
        return {
            success: true,
            branchName: branchName,
            message: `Created and switched to branch: ${branchName}`
        };
    } else {
        return {
            success: false,
            error: result.error
        };
    }
}

function commitFix(message, cwd = process.cwd()) {
    /**
     * 提交修复
     *
     * Args:
     *     message: 提交信息
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 提交结果
     */
    // 添加所有变更
    const addResult = runGitCommand(['add', '.'], cwd);
    if (!addResult.success) {
        return { success: false, error: `Failed to add files: ${addResult.error}` };
    }

    // 提交
    const commitResult = runGitCommand(['commit', '-m', message], cwd);

    if (commitResult.success) {
        // 获取提交哈希
        const hashResult = runGitCommand(['rev-parse', 'HEAD'], cwd);
        const commitHash = hashResult.success ? hashResult.output : null;

        return {
            success: true,
            commitHash: commitHash,
            message: message,
            output: commitResult.output
        };
    } else {
        return {
            success: false,
            error: commitResult.error
        };
    }
}

function getFixHistory(limit = 20, cwd = process.cwd()) {
    /**
     * 获取修复历史
     *
     * Args:
     *     limit: 历史记录数量限制
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 修复历史
     */
    // 获取提交历史（只包含文档提交）
    const cmd = ['log', `-${limit}`, '--pretty=format:%H|%an|%ae|%at|%s', '--', '*.md'];
    const result = runGitCommand(cmd, cwd);

    if (!result.success) {
        return { success: false, error: result.error };
    }

    const history = [];
    const lines = result.output.split('\n');

    for (const line of lines) {
        if (!line.trim()) {
            continue;
        }
        const parts = line.split('|', 5);
        if (parts.length === 5) {
            const [commitHash, authorName, authorEmail, timestamp, subject] = parts;
            let dateStr;

            try {
                const dt = new Date(parseInt(timestamp) * 1000);
                dateStr = dt.toISOString().slice(0, 19).replace('T', ' ');
            } catch {
                dateStr = timestamp;
            }

            history.push({
                commitHash: commitHash,
                authorName: authorName,
                authorEmail: authorEmail,
                date: dateStr,
                timestamp: parseInt(timestamp) || null,
                subject: subject
            });
        }
    }

    return {
        success: true,
        history: history,
        total: history.length
    };
}

function showCommit(commitHash, cwd = process.cwd()) {
    /**
     * 显示特定提交的详细信息
     *
     * Args:
     *     commitHash: 提交哈希
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 提交详细信息
     */
    // 获取提交信息
    const infoResult = runGitCommand(['show', '--stat', commitHash], cwd);
    if (!infoResult.success) {
        return { success: false, error: infoResult.error };
    }

    // 获取提交差异
    const diffResult = runGitCommand(['show', '--no-patch', commitHash], cwd);

    return {
        success: true,
        commitHash: commitHash,
        info: infoResult.output,
        summary: diffResult.success ? diffResult.output : null
    };
}

function rollbackToCommit(commitHash, cwd = process.cwd(), createBranch = true) {
    /**
     * 回滚到指定提交
     *
     * Args:
     *     commitHash: 目标提交哈希
     *     cwd: 工作目录
     *     createBranch: 是否创建回滚分支
     *
     * Returns:
     *     dict: 回滚结果
     */
    // 验证提交是否有效
    const result = runGitCommand(['cat-file', '-e', commitHash], cwd);
    if (!result.success) {
        return { success: false, error: `Invalid commit: ${commitHash}` };
    }

    let rollbackBranch = null;
    if (createBranch) {
        // 创建回滚分支
        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/[-T:]/g, '') + now.getMilliseconds();
        rollbackBranch = `rollback-${timestamp}`;

        const branchResult = runGitCommand(['checkout', '-b', rollbackBranch], cwd);
        if (!branchResult.success) {
            return { success: false, error: `Failed to create rollback branch: ${branchResult.error}` };
        }
    }

    // 执行回滚
    const resetResult = runGitCommand(['reset', '--hard', commitHash], cwd);

    if (resetResult.success) {
        return {
            success: true,
            commitHash: commitHash,
            rollbackBranch: rollbackBranch,
            message: `Successfully rolled back to commit: ${commitHash}`
        };
    } else {
        return {
            success: false,
            error: resetResult.error
        };
    }
}

function finishFix(mainBranch = DEFAULT_MAIN_BRANCH, cwd = process.cwd()) {
    /**
     * 完成修复，合并到主分支
     *
     * Args:
     *     mainBranch: 主分支名称
     *     cwd: 工作目录
     *
     * Returns:
     *     dict: 完成结果
     */
    const status = checkGitStatus(cwd);
    if (!status.isGitRepo) {
        return { success: false, error: 'Not a Git repository' };
    }

    const currentBranch = status.currentBranch;
    if (currentBranch === mainBranch) {
        return { success: false, error: `Already on ${mainBranch} branch` };
    }

    // 切换到主分支
    const checkoutResult = runGitCommand(['checkout', mainBranch], cwd);
    if (!checkoutResult.success) {
        return { success: false, error: `Failed to checkout ${mainBranch}: ${checkoutResult.error}` };
    }

    // 合并修复分支
    const mergeResult = runGitCommand(['merge', '--no-ff', currentBranch], cwd);

    if (mergeResult.success) {
        return {
            success: true,
            message: `Successfully merged ${currentBranch} into ${mainBranch}`,
            sourceBranch: currentBranch,
            targetBranch: mainBranch
        };
    } else {
        // 如果合并失败，尝试回退
        runGitCommand(['merge', '--abort'], cwd);
        runGitCommand(['checkout', currentBranch], cwd);
        return {
            success: false,
            error: `Merge failed: ${mergeResult.error}`
        };
    }
}

function printHelp() {
    console.log(`
Git 集成修复管理器 - 使用 Git 版本控制管理文档修复流程

使用方法:
    node tools/js/manage_fix_with_git.js --check-status
    node tools/js/manage_fix_with_git.js --start --branch-name "doc-fix-001"
    node tools/js/manage_fix_with_git.js --commit --message "修复 API 函数名错误"
    node tools/js/manage_fix_with_git.js --history
    node tools/js/manage_fix_with_git.js --show-commit "a1b2c3d"
    node tools/js/manage_fix_with_git.js --rollback --commit-hash "a1b2c3d"
    node tools/js/manage_fix_with_git.js --finish

选项:
    --check-status          检查 Git 工作区状态
    --start                 开始修复流程（创建分支）
    --branch-name NAME      修复分支名称（默认: doc-fix-YYYYMMDD）
    --commit                提交修复
    --message MSG           提交信息
    --history               查看修复历史
    --show-commit HASH      查看特定提交详细信息
    --rollback              回滚到指定提交
    --commit-hash HASH      目标提交哈希
    --finish                完成修复（合并到主分支）
    --main-branch NAME      主分支名称（默认: main）
    --doc-dir PATH          文档目录（默认: dev_docs/）
    --verbose               输出详细信息
    --help, -h              显示此帮助信息
`);
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        checkStatus: false,
        start: false,
        branchName: null,
        commit: false,
        message: null,
        history: false,
        showCommit: null,
        rollback: false,
        targetCommit: null,
        finish: false,
        mainBranch: DEFAULT_MAIN_BRANCH,
        docDir: DEFAULT_DOC_DIR,
        verbose: false,
        help: false
    };

    let i = 0;
    while (i < args.length) {
        switch (args[i]) {
            case '--help':
            case '-h':
                options.help = true;
                i++;
                break;
            case '--check-status':
                options.checkStatus = true;
                i++;
                break;
            case '--start':
                options.start = true;
                i++;
                break;
            case '--branch-name':
                options.branchName = args[++i];
                i++;
                break;
            case '--commit':
                options.commit = true;
                i++;
                break;
            case '--message':
                options.message = args[++i];
                i++;
                break;
            case '--history':
                options.history = true;
                i++;
                break;
            case '--show-commit':
                options.showCommit = args[++i];
                i++;
                break;
            case '--rollback':
                options.rollback = true;
                i++;
                break;
            case '--commit-hash':
                options.targetCommit = args[++i];
                i++;
                break;
            case '--finish':
                options.finish = true;
                i++;
                break;
            case '--main-branch':
                options.mainBranch = args[++i];
                i++;
                break;
            case '--doc-dir':
                options.docDir = args[++i];
                i++;
                break;
            case '--verbose':
                options.verbose = true;
                i++;
                break;
            default:
                console.error(`Unknown option: ${args[i]}`);
                process.exit(1);
        }
    }

    // 显示帮助
    if (options.help) {
        printHelp();
        process.exit(0);
    }

    const result = {
        success: true,
        data: {},
        metadata: {
            version: VERSION
        }
    };

    try {
        // 确定工作目录
        const cwd = process.cwd();

        if (options.checkStatus) {
            // 检查 Git 状态
            const status = checkGitStatus(cwd);
            result.data = {
                action: "check_status",
                result: status
            };
        } else if (options.start) {
            // 开始修复流程
            const branchResult = createFixBranch(options.branchName, cwd);
            result.data = {
                action: "start_fix",
                result: branchResult
            };
            if (!branchResult.success) {
                result.success = false;
                result.error = branchResult.error;
            }
        } else if (options.commit) {
            // 提交修复
            if (!options.message) {
                result.success = false;
                result.error = "提交信息不能为空，请使用 --message 参数";
            } else {
                const commitResult = commitFix(options.message, cwd);
                result.data = {
                    action: "commit_fix",
                    result: commitResult
                };
                if (!commitResult.success) {
                    result.success = false;
                    result.error = commitResult.error;
                }
            }
        } else if (options.history) {
            // 查看修复历史
            const historyResult = getFixHistory(20, cwd);
            result.data = {
                action: "get_history",
                result: historyResult
            };
            if (!historyResult.success) {
                result.success = false;
                result.error = historyResult.error;
            }
        } else if (options.showCommit) {
            // 显示提交详情
            const showResult = showCommit(options.showCommit, cwd);
            result.data = {
                action: "show_commit",
                result: showResult
            };
            if (!showResult.success) {
                result.success = false;
                result.error = showResult.error;
            }
        } else if (options.rollback) {
            // 回滚
            if (!options.targetCommit) {
                result.success = false;
                result.error = "请指定目标提交哈希，使用 --commit-hash 参数";
            } else {
                const rollbackResult = rollbackToCommit(options.targetCommit, cwd);
                result.data = {
                    action: "rollback",
                    result: rollbackResult
                };
                if (!rollbackResult.success) {
                    result.success = false;
                    result.error = rollbackResult.error;
                }
            }
        } else if (options.finish) {
            // 完成修复
            const finishResult = finishFix(options.mainBranch, cwd);
            result.data = {
                action: "finish_fix",
                result: finishResult
            };
            if (!finishResult.success) {
                result.success = false;
                result.error = finishResult.error;
            }
        } else {
            // 无操作
            result.success = false;
            result.error = "请指定操作: --check-status, --start, --commit, --history, --show-commit, --rollback, 或 --finish";
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }

    // 输出 JSON
    console.log(JSON.stringify(result, null, 2));
}

main();
