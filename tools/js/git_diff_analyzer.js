/**
 * Git 差异分析工具 - 分析代码变更供 AI 判断文档更新需求
 * 
 * 用法:
 *   node tools/js/git_diff_analyzer.js [--since "2025-11-10" | --since "7 days ago"]
 * 
 * 输出:
 *   {
 *     "data": {
 *       "reference_commit": "abc123",
 *       "changed_files": [{"path": "src/api/user.ts", "change_type": "modified", "lines_changed": 45}],
 *       "summary": {"total_files_changed": 2, "files_by_type": {"modified": 1, "added": 1}}
 *     },
 *     "metadata": {"git_available": true, "elapsed_seconds": 0.8, "version": "1.1.0"}
 *   }
 */

const { execSync, spawnSync } = require('child_process');

function checkGitAvailable() {
    try {
        execSync('git --version', { timeout: 2000, stdio: 'ignore' });
        return true;
    } catch (e) {
        return false;
    }
}

function getReferenceCommit(since) {
    try {
        let cmd;
        if (since.includes('ago') || since.includes('days') || since.includes('hours')) {
            cmd = `git log --since="${since}" --max-count=1 --format=%H`;
        } else {
            cmd = `git log --since="${since}" --max-count=1 --format=%H`;
        }
        
        const result = execSync(cmd, { encoding: 'utf8', timeout: 5000 });
        return result.trim();
    } catch (e) {
        return "HEAD~10"; // 默认对比最近 10 个提交
    }
}

function analyzeChanges(sinceCommit = "HEAD~10") {
    try {
        const cmd = `git diff --numstat ${sinceCommit}..HEAD`;
        const result = execSync(cmd, { encoding: 'utf8', timeout: 10000 });
        
        const changes = [];
        const filesByType = { modified: 0, added: 0, deleted: 0 };
        
        const lines = result.split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;
            
            const parts = line.split('\t');
            if (parts.length !== 3) continue;
            
            const [added, deleted, filepath] = parts;
            
            // 判断变更类型
            let changeType;
            let linesChanged;
            
            if (added === '0' && deleted !== '0') {
                changeType = 'deleted';
                linesChanged = deleted === '-' ? 0 : parseInt(deleted);
            } else if (deleted === '0' && added !== '0') {
                changeType = 'added';
                linesChanged = added === '-' ? 0 : parseInt(added);
            } else {
                changeType = 'modified';
                const addedNum = added === '-' ? 0 : parseInt(added);
                const deletedNum = deleted === '-' ? 0 : parseInt(deleted);
                linesChanged = addedNum + deletedNum;
            }
            
            filesByType[changeType]++;
            
            changes.push({
                path: filepath,
                change_type: changeType,
                lines_changed: linesChanged
            });
        }
        
        return { changes, filesByType };
    } catch (e) {
        if (e.message && e.message.includes('timed out')) {
            return { error: 'timeout' };
        }
        return { error: e.message };
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let since = '7 days ago';
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--since') {
            since = args[++i];
        }
    }
    
    // 检查 git 可用性
    if (!checkGitAvailable()) {
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        const result = {
            success: false,
            error: 'git_not_available',
            suggestion: '使用 timestamp_analyzer.js 作为替代',
            metadata: {
                git_available: false,
                elapsed_seconds: parseFloat(elapsedTime),
                timeout_threshold: 10,
                version: "1.1.0"
            }
        };
        console.log(JSON.stringify(result, null, 2));
        return;
    }
    
    // 获取参考提交
    const referenceCommit = getReferenceCommit(since);
    
    // 分析变更
    const analysisResult = analyzeChanges(referenceCommit);
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    
    if (analysisResult.error) {
        // 发生错误
        const result = {
            success: false,
            error: analysisResult.error,
            suggestion: '检查 git 仓库状态或使用 timestamp_analyzer.js',
            metadata: {
                git_available: true,
                elapsed_seconds: parseFloat(elapsedTime),
                timeout_threshold: 10,
                version: "1.1.0"
            }
        };
        console.log(JSON.stringify(result, null, 2));
    } else {
        // 成功
        const result = {
            data: {
                reference_commit: referenceCommit,
                changed_files: analysisResult.changes,
                summary: {
                    total_files_changed: analysisResult.changes.length,
                    files_by_type: analysisResult.filesByType
                }
            },
            metadata: {
                git_available: true,
                elapsed_seconds: parseFloat(elapsedTime),
                timeout_threshold: 10,
                version: "1.1.0"
            }
        };
        console.log(JSON.stringify(result, null, 2));
    }
}

main();
