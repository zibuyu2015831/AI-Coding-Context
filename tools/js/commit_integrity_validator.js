/**
 * Commit 诚信验证工具 - 对比 Commit Message 与物理代码变更的一致性
 * 
 * 功能说明：
 * - 解析拟提交的 Commit Message (WHAT/WHY/HOW 结构)
 * - 获取当前 Git 暂存区 (staged) 或未暂存 (unstaged) 的文件变更
 * - 对比 HOW 字段中提到的文件与实际变更文件是否匹配
 * - 输出诚信分 (Integrity Score) 和改进建议
 * 
 * 使用方法：
 *     node tools/js/commit_integrity_validator.js --message "COMMIT_MESSAGE" [--staged]
 */

const { execSync } = require('child_process');
const path = require('path');

/**
 * 获取 Git 变更的文件列表
 */
function getGitDiffFiles(staged = true) {
    const cmd = staged ? 'git diff --name-only --staged' : 'git diff --name-only';
    try {
        const output = execSync(cmd, { encoding: 'utf8', timeout: 5000 });
        return new Set(output.split('\n').map(line => line.trim()).filter(line => line.length > 0));
    } catch (error) {
        return new Set();
    }
}

/**
 * 从 Commit Message 的 HOW 字段中提取提到的文件路径
 */
function parseHowFiles(message) {
    let howSection = "";
    // 查找 HOW: 之后的所有内容, 直到下一个大写关键字 (如 WHY, WHAT) 或结束
    const howMatch = message.match(/HOW:\s*([\s\S]*?)(?=\s*[A-Z]{3,}:|$)/);
    if (howMatch) {
        howSection = howMatch[1];
    }

    const foundPaths = new Set();
    // 路径匹配正则: 匹配包含斜杠的文件名, 或者带常见扩展名的文件名
    const patterns = [
        /[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+/g, // 标准路径或带扩展名文件
        /\.[a-zA-Z0-9_\-]+/g                // 隐藏文件如 .gitignore
    ];

    patterns.forEach(pattern => {
        const matches = howSection.match(pattern);
        if (matches) {
            matches.forEach(m => {
                // 清理标点
                let p = m.replace(/[.,:;()\[\]{} "']+$/, '').replace(/^[.,:;()\[\]{} "']+/, '');
                // 统一处理 ./ 前缀
                if (p.startsWith('./')) {
                    p = p.substring(2);
                }
                if (p) {
                    foundPaths.add(p);
                }
            });
        }
    });

    return foundPaths;
}

/**
 * 计算诚信分并生成报告
 */
function calculateIntegrity(msgFiles, actualFiles) {
    const matched = new Set([...msgFiles].filter(x => actualFiles.has(x)));
    const overReported = new Set([...msgFiles].filter(x => !actualFiles.has(x)));
    const underReported = new Set([...actualFiles].filter(x => !msgFiles.has(x)));

    let score = 100;
    const underReportedPenalty = underReported.size * 15;
    const overReportedPenalty = overReported.size * 5;

    score -= (underReportedPenalty + overReportedPenalty);
    score = Math.max(0, score);

    const suggestions = [];
    if (underReported.size > 0) {
        suggestions.append(`⚠️ 以下文件已修改但未在 HOW 中说明: ${Array.from(underReported).join(', ')}`);
    }
    if (overReported.size > 0) {
        suggestions.append(`ℹ️ HOW 中提到的以下文件似乎未发生变更: ${Array.from(overReported).join(', ')}`);
    }

    let status = "NEEDS_IMPROVEMENT";
    if (score >= 90) status = "EXCELLENT";
    else if (score >= 80) status = "GOOD";

    return {
        score,
        status,
        matched_count: matched.size,
        under_reported: Array.from(underReported),
        over_reported: Array.from(overReported),
        suggestions
    };
}

// 简单的参数解析
const args = process.argv.slice(2);
let message = "";
let staged = true;
let isJson = false;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--message' && args[i + 1]) {
        message = args[i + 1];
        i++;
    } else if (args[i] === '--unstaged') {
        staged = false;
    } else if (args[i] === '--format' && args[i + 1] === 'json') {
        isJson = true;
        i++;
    }
}

if (!message) {
    console.error("错误: 必须通过 --message 提供 Commit 信息");
    process.exit(1);
}

const actualFiles = getGitDiffFiles(staged);
const msgFiles = parseHowFiles(message);
const report = calculateIntegrity(msgFiles, actualFiles);

if (isJson) {
    console.log(JSON.stringify(report, null, 2));
} else {
    console.log("--- Commit 诚信审计报告 (Node.js) ---");
    console.log(`得分: ${report.score} [${report.status}]`);
    console.log(`匹配文件数: ${report.matched_count}`);

    if (report.suggestions.length > 0) {
        console.log("\n建议:");
        report.suggestions.forEach(s => console.log(`  ${s}`));
    } else {
        console.log("\n✅ 意图与物理变更完美匹配！");
    }
}
