/**
 * Git 安全检查工具 - 检查 Git 操作的安全性
 * 
 * 功能说明：
 * - 检查当前分支是否为保护分支
 * - 验证 Git 命令是否安全
 * - 建议符合规范的分支名
 * - 支持自定义保护分支配置
 * 
 * 使用方法：
 *   node tools/js/git_safety.js [--mode MODE] [--command COMMAND] [--branch-name NAME]
 * 
 * 参数说明：
 *   --mode MODE              检查模式（默认：check-branch）
 *                           可选值：
 *                             check-branch    检查当前分支是否安全
 *                             validate-command 验证Git命令是否安全
 *                             suggest-branch   建议分支名
 *   --command COMMAND        要验证的Git命令（仅在validate-command模式下使用）
 *   --branch-name NAME       要生成的分支名（仅在suggest-branch模式下使用）
 *   --protected-branches     自定义保护分支列表（逗号分隔，支持 * 通配符）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "safe": 是否安全(bool),
 *       "current_branch": "当前分支名",
 *       "reason": "原因说明",
 *       "suggestion": "建议"
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   # 检查当前分支
 *   node tools/js/git_safety.js --mode check-branch
 *   
 *   # 验证Git命令
 *   node tools/js/git_safety.js --mode validate-command --command "git push --force"
 *   
 *   # 建议分支名
 *   node tools/js/git_safety.js --mode suggest-branch --branch-name "user points"
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2026-04-22
 */

const { execSync } = require('child_process');

const DEFAULT_PROTECTED_BRANCHES = ['main', 'master', 'production', 'release/*', 'develop'];

const DANGEROUS_COMMANDS = [
    /git\s+reset\s+--hard/i,
    /git\s+push\s+--force/i,
    /git\s+push\s+-f\b/i,
    /git\s+rebase/i,
    /git\s+merge\b(?!.*--abort)/i,
    /git\s+branch\s+-D/i,
    /git\s+tag\s+-d/i,
    /git\s+tag\s+--delete/i
];

const RESTRICTED_COMMANDS = [
    /git\s+checkout\s+-b/i,
    /git\s+commit/i,
    /git\s+push\s+origin/i
];

function getCurrentBranch() {
    try {
        return execSync('git branch --show-current', { encoding: 'utf8' }).trim();
    } catch {
        return null;
    }
}

function matchBranch(branch, pattern) {
    if (pattern.includes('*')) {
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return regex.test(branch);
    }
    return branch === pattern;
}

function checkCurrentBranch(protectedBranches = DEFAULT_PROTECTED_BRANCHES) {
    const currentBranch = getCurrentBranch();
    
    if (currentBranch === null || currentBranch === '') {
        return {
            safe: false,
            current_branch: null,
            reason: 'Not a git repository or git not found',
            suggestion: 'Ensure you are in a git repository and git is installed'
        };
    }
    
    const isProtected = protectedBranches.some(pattern => matchBranch(currentBranch, pattern));
    
    if (isProtected) {
        return {
            safe: false,
            current_branch: currentBranch,
            reason: `Current branch "${currentBranch}" is a protected branch`,
            suggestion: `Create a feature branch: git checkout -b feature/your-feature-name`
        };
    }
    
    return {
        safe: true,
        current_branch: currentBranch,
        reason: `Current branch "${currentBranch}" is safe to work on`,
        suggestion: null
    };
}

function validateGitCommand(command) {
    if (!command) {
        return {
            safe: false,
            command: command,
            reason: 'No command provided',
            suggestion: 'Provide a git command to validate'
        };
    }
    
    for (const pattern of DANGEROUS_COMMANDS) {
        if (pattern.test(command)) {
            return {
                safe: false,
                command: command,
                reason: `Command matches dangerous pattern: ${pattern.source}`,
                suggestion: 'This command is in the RED ZONE and should never be executed by AI',
                zone: 'RED'
            };
        }
    }
    
    for (const pattern of RESTRICTED_COMMANDS) {
        if (pattern.test(command)) {
            return {
                safe: false,
                command: command,
                reason: `Command matches restricted pattern: ${pattern.source}`,
                suggestion: 'This command requires explicit user authorization',
                zone: 'YELLOW'
            };
        }
    }
    
    return {
        safe: true,
        command: command,
        reason: 'Command is safe to execute',
        suggestion: null,
        zone: 'GREEN'
    };
}

function suggestSafeBranchName(description) {
    if (!description) {
        return {
            safe: true,
            original: description,
            suggested: null,
            reason: 'No description provided',
            suggestion: 'Provide a description for branch name suggestion'
        };
    }
    
    let name = description.toLowerCase();
    name = name.replace(/[^\w\s-]/g, '');
    name = name.replace(/[\s_]+/g, '-');
    name = name.replace(/^-+|-+$/g, '');
    
    let prefix = 'feature';
    if (/fix|bug|issue/i.test(description)) {
        prefix = 'bugfix';
    } else if (/refactor|cleanup|improve/i.test(description)) {
        prefix = 'refactor';
    } else if (/doc|documentation/i.test(description)) {
        prefix = 'docs';
    }
    
    const suggestedName = `${prefix}/${name}`;
    
    return {
        safe: true,
        original: description,
        suggested: suggestedName,
        reason: 'Generated branch name based on description',
        suggestion: `Use: git checkout -b ${suggestedName}`
    };
}

function main() {
    const startTime = Date.now();
    const args = process.argv.slice(2);
    const options = {
        mode: 'check-branch',
        command: null,
        branchName: null,
        protectedBranches: DEFAULT_PROTECTED_BRANCHES
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--mode': options.mode = args[++i]; break;
            case '--command': options.command = args[++i]; break;
            case '--branch-name': options.branchName = args[++i]; break;
            case '--protected-branches': 
                options.protectedBranches = args[++i].split(',').map(b => b.trim()); 
                break;
        }
    }
    
    let resultData;
    switch (options.mode) {
        case 'check-branch':
            resultData = checkCurrentBranch(options.protectedBranches);
            break;
        case 'validate-command':
            resultData = validateGitCommand(options.command);
            break;
        case 'suggest-branch':
            resultData = suggestSafeBranchName(options.branchName);
            break;
        default:
            resultData = { error: `Unknown mode: ${options.mode}` };
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    const result = {
        data: resultData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: '1.1.0'
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
    main();
}
