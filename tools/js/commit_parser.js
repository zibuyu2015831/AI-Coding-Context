/**
 * Commit 解析工具 - 解析 Git commit 信息
 * 
 * 功能说明：
 * - 解析结构化 commit (prompt:格式)
 * - 解析传统 commit (降级处理)
 * - 聚合多个 commit，生成摘要
 * - 分析合并请求 (Merge Analysis)
 * 
 * 使用方法：
 *   node tools/js/commit_parser.js [--mode MODE] [--max-count N] [--since DATE] [--branch NAME]
 * 
 * 参数说明：
 *   --mode MODE              解析模式（默认：parse）
 *                           可选值：
 *                             parse          解析 Git 历史 commits
 *                             aggregate      聚合 commits 并生成统计
 *                             analyze-merge  分析两个分支间的差异
 *   --max-count N           最多解析 N 个 commit（默认：100）
 *   --since DATE            解析 DATE 之后的 commit (如 "2023-01-01")
 *   --branch NAME           解析指定分支的 commit
 *   --source-branch NAME    合并分析的源分支 (analyze-merge 模式)
 *   --target-branch NAME    合并分析的目标分支 (analyze-merge 模式)
 *   --format FORMAT         输出格式（json/summary）
 * 
 * 输出格式：
 *   {
 *     "data": { ... },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2026-04-22
 */

const { execSync } = require('child_process');

const SUBJECT_PATTERN = /^(prompt|ai|doc|feat|fix|arch)\(([^)]+)\):\s*(.+)$/i;
const CONVENTIONAL_PATTERN = /^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)\(([^)]*)\):\s*(.+)$/i;

/**
 * 解析 prompt 格式 commit
 */
function parsePromptCommit(message) {
    const lines = message.split('\n');
    const match = lines[0].match(SUBJECT_PATTERN);
    
    if (!match) return null;
    
    const [, prefix, type, whatShort] = match;
    const result = {
        prefix: prefix.toLowerCase(),
        type: type.toLowerCase(),
        what: whatShort.trim(),
        why: null,
        how: [],
        is_structured: true
    };
    
    const body = lines.slice(1).join('\n');
    
    // 提取 WHAT (如果 Body 中有更详细的)
    const whatMatch = body.match(/WHAT:\s*(.+?)(?=\nWHY:|\nHOW:|$)/is);
    if (whatMatch) result.what = whatMatch[1].trim();
    
    // 提取 WHY
    const whyMatch = body.match(/WHY:\s*(.+?)(?=\nHOW:|$)/is);
    if (whyMatch) result.why = whyMatch[1].trim();
    
    // 提取 HOW
    const howMatch = body.match(/HOW:\s*\n((?:[-*]\s*.+\n?)+)/im);
    if (howMatch) {
        result.how = howMatch[1].split('\n')
            .filter(line => line.trim() && /^[-*]/.test(line.trim()))
            .map(line => line.trim().substring(2).trim());
    }
    
    return result;
}

/**
 * 解析 Conventional Commit 格式
 */
function parseConventionalCommit(message) {
    const lines = message.split('\n');
    const match = lines[0].match(CONVENTIONAL_PATTERN);
    
    if (!match) return null;
    
    const [, type, scope, description] = match;
    const body = lines.slice(1).join('\n').trim();
    
    return {
        prefix: 'conventional',
        type: type.toLowerCase(),
        scope: scope ? scope.trim() : null,
        what: description.trim(),
        why: body || '(未提供)',
        how: ['(需分析diff)'],
        is_structured: false,
        is_conventional: true
    };
}

/**
 * 解析传统 commit (降级处理)
 */
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

/**
 * 智能解析 commit message
 */
function parseCommitMessage(message) {
    return parsePromptCommit(message) || 
           parseConventionalCommit(message) || 
           parseTraditionalCommit(message);
}

/**
 * 获取 Git commits
 */
function getCommits(maxCount = 100, since = null, branch = null) {
    try {
        let cmd = `git log --max-count=${maxCount} --pretty=format:"%H|%an|%ae|%ad|%s|%b" --date=iso`;
        
        if (since) cmd += ` --since="${since}"`;
        if (branch) cmd += ` ${branch}`;
        
        const output = execSync(cmd, { encoding: 'utf8' });
        if (!output.trim()) return [];
        
        const commits = [];
        const lines = output.split('\n');
        
        for (const line of lines) {
            if (!line.trim()) continue;
            
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
    } catch (e) {
        return [];
    }
}

/**
 * 聚合 commits
 */
function aggregateCommits(commits) {
    if (!commits || commits.length === 0) {
        return {
            summary: 'No commits to aggregate',
            total: 0,
            structured_count: 0,
            traditional_count: 0,
            by_type: {}
        };
    }
    
    const structured = commits.filter(c => c.is_structured);
    const traditionalCount = commits.length - structured.length;
    
    const byType = {};
    structured.forEach(c => {
        const type = c.type || 'unknown';
        byType[type] = (byType[type] || 0) + 1;
    });
    
    return {
        summary: `Aggregated ${commits.length} commits`,
        total: commits.length,
        structured_count: structured.length,
        traditional_count: traditionalCount,
        by_type: byType
    };
}

/**
 * 分析合并变更
 */
function analyzeMergeCommits(sourceBranch, targetBranch) {
    try {
        const cmd = `git log ${targetBranch}..${sourceBranch} --pretty=format:"%H|%s"`;
        const output = execSync(cmd, { encoding: 'utf8' });
        
        if (!output.trim()) {
            return {
                source: sourceBranch,
                target: targetBranch,
                commits: [],
                count: 0,
                message: 'No commits to merge'
            };
        }
        
        const commits = output.split('\n').map(line => {
            const [hash, subject] = line.split('|');
            return { hash, subject };
        });
        
        return {
            source: sourceBranch,
            target: targetBranch,
            commits: commits,
            count: commits.length,
            message: `Found ${commits.length} commits to merge`
        };
    } catch (e) {
        return {
            error: `Failed to analyze merge from ${sourceBranch} to ${targetBranch}: ${e.message}`
        };
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        mode: 'parse',
        maxCount: 100,
        since: null,
        branch: null,
        sourceBranch: null,
        targetBranch: null,
        format: 'json'
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--mode': options.mode = args[++i]; break;
            case '--max-count': options.maxCount = parseInt(args[++i]); break;
            case '--since': options.since = args[++i]; break;
            case '--branch': options.branch = args[++i]; break;
            case '--source-branch': options.sourceBranch = args[++i]; break;
            case '--target-branch': options.targetBranch = args[++i]; break;
            case '--format': options.format = args[++i]; break;
        }
    }
    
    let resultData;
    if (options.mode === 'parse') {
        const commits = getCommits(options.maxCount, options.since, options.branch);
        const structuredCount = commits.filter(c => c.is_structured).length;
        resultData = {
            commits,
            total: commits.length,
            structured_count: structuredCount,
            traditional_count: commits.length - structuredCount
        };
    } else if (options.mode === 'aggregate') {
        const commits = getCommits(options.maxCount, options.since, options.branch);
        resultData = aggregateCommits(commits);
    } else if (options.mode === 'analyze-merge') {
        if (!options.sourceBranch || !options.targetBranch) {
            resultData = { error: 'Source and target branches required for merge analysis' };
        } else {
            resultData = analyzeMergeCommits(options.sourceBranch, options.targetBranch);
        }
    } else {
        resultData = { error: `Unknown mode: ${options.mode}` };
    }
    
    if (options.format === 'summary' && !resultData.error) {
        console.log(`Total commits: ${resultData.total || resultData.count || 0}`);
        if (resultData.structured_count !== undefined) {
            console.log(`Structured: ${resultData.structured_count}`);
            console.log(`Traditional: ${resultData.traditional_count}`);
        }
    } else {
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
        const result = {
            data: resultData,
            metadata: {
                elapsed_seconds: parseFloat(elapsedTime),
                version: '1.1.0'
            }
        };
        console.log(JSON.stringify(result, null, 2));
    }
}

if (require.main === module) {
    main();
}
