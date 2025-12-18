/**
 * Commit 聚合工具 - 批量聚合和Token优化
 * 
 * 功能说明：
 * - 同类 commit 聚合
 * - Token 优化
 * 
 * 使用方法：
 *   node tools/js/commit_aggregator.js [--max-count N] [--optimize-token]
 * 
 * 参数说明：
 *   --max-count N           最多聚合N个commit（默认：50）
 *   --optimize-token        启用Token优化
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-11
 */

const { execSync } = require('child_process');

function getCommits(maxCount) {
    try {
        const output = execSync(
            `git log --max-count=${maxCount} --pretty=format:%H|%s`,
            { encoding: 'utf8' }
        );
        
        return output.split('\n')
            .filter(line => line)
            .map(line => {
                const [hash, subject] = line.split('|');
                return { hash, what: subject, type: 'unknown' };
            });
    } catch {
        return [];
    }
}

function optimizeTokens(commits) {
    const originalTokens = commits.reduce((sum, c) => sum + (c.what || '').length, 0);
    
    const byType = {};
    commits.forEach(c => {
        const type = c.type || 'unknown';
        if (!byType[type]) byType[type] = [];
        byType[type].push(c);
    });
    
    const summaries = Object.entries(byType).map(([type, typeCommits]) => ({
        type,
        count: typeCommits.length,
        changes: typeCommits.slice(0, 5).map(c => c.what)
    }));
    
    const optimizedTokens = summaries.reduce(
        (sum, s) => sum + s.type.length + s.changes.reduce((s2, c) => s2 + c.length, 0), 
        0
    );
    
    const reduction = originalTokens > 0 
        ? ((originalTokens - optimizedTokens) / originalTokens * 100).toFixed(2)
        : 0;
    
    return {
        summaries,
        original_tokens: originalTokens,
        optimized_tokens: optimizedTokens,
        reduction_percent: parseFloat(reduction)
    };
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let maxCount = 50;
    let optimizeToken = false;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--max-count') maxCount = parseInt(args[i + 1]);
        if (args[i] === '--optimize-token') optimizeToken = true;
    }
    
    const commits = getCommits(maxCount);
    const resultData = optimizeToken ? optimizeTokens(commits) : { commits };
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    const result = {
        data: resultData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            version: '1.0.0'
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

main();
