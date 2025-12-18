/**
 * Git 安全检查工具 - 检查 Git 操作的安全性
 * 
 * 功能说明：
 * - 检查当前分支是否为保护分支
 * - 验证 Git 命令是否安全
 * - 建议符合规范的分支名
 * 
 * 使用方法：
 *   node tools/js/git_safety.js [--mode MODE] [--command COMMAND]
 * 
 * 参数说明：
 *   --mode MODE              检查模式（默认：check-branch）
 *   --command COMMAND        要验证的Git命令
 *   --branch-name NAME       要生成的分支名
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-11
 */

const { execSync } = require('child_process');

const DEFAULT_PROTECTED_BRANCHES = ['main', 'master', 'production', 'release', 'develop'];

const DANGEROUS_COMMANDS = [
    /git\s+reset\s+--hard/i,
    /git\s+push\s+--force/i,
    /git\s+push\s+-f\b/i,
    /git\s+rebase/i,
    /git\s+merge\b(?!.*--abort)/i,
    /git\s+branch\s+-D/i
];

const RESTRICTED_COMMANDS = [
    /git\s+checkout\s+-b/i,
    /git\s+commit/i,
    /git\s+push\s+origin/i
];

function getCurrentBranch() {
    try {
        const branch = execSync('git branch --show-current', { encoding: 'utf8' }).trim();
        return branch;
    } catch {
        return null;
    }
}

function checkCurrentBranch(protectedBranches = DEFAULT_PROTECTED_BRANCHES) {
    const currentBranch = getCurrentBranch();
    
    if (!currentBranch) {
        return {
            safe: false,
            current_branch: null,
            reason: 'Not a git repository or git not found',
            suggestion: 'Ensure you are in a git repository and git is installed'
        };
    }
    
    const isProtected = protectedBranches.includes(currentBranch);
    
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
    
    // Check dangerous commands
    for (const pattern of DANGEROUS_COMMANDS) {
        if (pattern.test(command)) {
            return {
                safe: false,
                command: command,
                reason: `Command matches dangerous pattern`,
                suggestion: 'This command is in the RED ZONE and should never be executed by AI',
                zone: 'RED'
            };
        }
    }
    
    // Check restricted commands
    for (const pattern of RESTRICTED_COMMANDS) {
        if (pattern.test(command)) {
            return {
                safe: false,
                command: command,
                reason: `Command matches restricted pattern`,
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
            reason: 'No description provided'
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
    let mode = 'check-branch';
    let command = null;
    let branchName = null;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--mode') mode = args[i + 1];
        if (args[i] === '--command') command = args[i + 1];
        if (args[i] === '--branch-name') branchName = args[i + 1];
    }
    
    let resultData;
    if (mode === 'check-branch') {
        resultData = checkCurrentBranch();
    } else if (mode === 'validate-command') {
        resultData = validateGitCommand(command);
    } else if (mode === 'suggest-branch') {
        resultData = suggestSafeBranchName(branchName);
    } else {
        resultData = { error: `Unknown mode: ${mode}` };
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    const result = {
        data: resultData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: '1.0.0'
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

main();
