/**
 * Commit 解析工具 - 解析 Git commit 信息
 * 
 * 功能说明：
 * - 解析结构化 commit (prompt:格式)
 * - 解析传统 commit (降级处理)
 * - 聚合多个 commit
 * 
 * 使用方法：
 *   node tools/js/commit_parser.js [--mode MODE] [--max-count N]
 * 
 * 参数说明：
 *   --mode MODE              解析模式（默认：parse）
 *   --max-count N           最多解析N个commit（默认：100）
 *   --format FORMAT         输出格式（json/summary）
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-11
 */

const { execSync } = require('child_process');

const SUBJECT_PATTERN = /^(prompt|ai|doc)\(([^)]+)\):\s*(.+)$/;
const CONVENTIONAL_PATTERN = /^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)\(([^)]*)\):\s*(.+)$/;

function parsePromptCommit(message) {
    const lines = message.split('\n');
    const match = lines[0].match(SUBJECT_PATTERN);
    
    if (!match) return null;
    
    const [, prefix, type, whatShort] = match;
    const result = {
        prefix,
        type,
        what: whatShort.trim(),
        why: null,
        how: [],
        is_structured: true
    };
    
    if (lines.length > 1) {
        const body = lines.slice(1).join('\n');
        
        const whatMatch = body.match(/WHAT:\s*(.+?)(?=\nWHY:|\nHOW:|$)/s);
        if (whatMatch) result.what = whatMatch[1].trim();
        
        const whyMatch = body.match(/WHY:\s*(.+?)(?=\nHOW:|$)/s);
        if (whyMatch) result.why = whyMatch[1].trim();
        
        const howMatch = body.match(/HOW:\s*\n((?:[-*]\s*.+\n?)+)/m);
        if (howMatch) {
            result.how = howMatch[1].split('\n')
                .filter(line => line.trim() && /^[-*]/.test(line.trim()))
                .map(line => line.trim().substring(2).trim());
        }
    }
    
    return result;
}

function parseConventionalCommit(message) {
    const lines = message.split('\n');
    const match = lines[0].match(CONVENTIONAL_PATTERN);
    
    if (!match) return null;
    
    const [, type, scope, description] = match;
    const body = lines.slice(1).join('\n').trim();
    
    return {
        prefix: 'conventional',
        type,
        what: description.trim(),
        why: body || '(未提供)',
        how: ['(需分析diff)'],
        is_structured: false,
        is_conventional: true
    };
}

function parseTraditionalCommit(message) {
    const lines = message.split('\n');
    const subject = lines[0].trim();
    const body = lines.slice(1).join('\n').trim();
    
    return {
        prefix: 'traditional',
        type: 'unknown',
        what: subject,
        why: body || '(未提供)',
        how: ['(需分析diff)'],
        is_structured: false,
        is_conventional: false
    };
}

function parseCommitMessage(message) {
    return parsePromptCommit(message) || 
           parseConventionalCommit(message) || 
           parseTraditionalCommit(message);
}

function getCommits(maxCount = 100) {
    try {
        const output = execSync(
            `git log --max-count=${maxCount} --pretty=format:%H|%an|%ae|%ad|%s|%b --date=iso`,
            { encoding: 'utf8' }
        );
        
        const commits = [];
        const lines = output.split('\n');
        
        for (const line of lines) {
            if (!line) continue;
            
            const parts = line.split('|');
            if (parts.length < 5) continue;
            
            const [hash, author, email, date, subject, ...bodyParts] = parts;
            const body = bodyParts.join('|');
            const fullMessage = body ? `${subject}\n${body}` : subject;
            
            const parsed = parseCommitMessage(fullMessage);
            parsed.hash = hash;
            parsed.author = author;
            parsed.email = email;
            parsed.date = date;
            
            commits.push(parsed);
        }
        
        return commits;
    } catch {
        return [];
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let mode = 'parse';
    let maxCount = 100;
    let format = 'json';
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--mode') mode = args[i + 1];
        if (args[i] === '--max-count') maxCount = parseInt(args[i + 1]);
        if (args[i] === '--format') format = args[i + 1];
    }
    
    const commits = getCommits(maxCount);
    const structuredCount = commits.filter(c => c.is_structured).length;
    const traditionalCount = commits.length - structuredCount;
    
    const resultData = {
        commits,
        total: commits.length,
        structured_count: structuredCount,
        traditional_count: traditionalCount
    };
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    
    if (format === 'summary') {
        console.log(`Total commits: ${resultData.total}`);
        console.log(`Structured: ${resultData.structured_count}`);
        console.log(`Traditional: ${resultData.traditional_count}`);
    } else {
        const result = {
            data: resultData,
            metadata: {
                elapsed_seconds: parseFloat(elapsedTime),
                version: '1.0.0'
            }
        };
        console.log(JSON.stringify(result, null, 2));
    }
}

main();
