/**
 * Git 仓库检查工具 - 获取 Git 仓库状态信息
 * 
 * 功能说明：
 * - 检测当前目录是否为 Git 仓库
 * - 获取当前分支名称
 * - 列出所有未提交的变更文件
 * - 检测仓库是否干净（无变更）
 * 
 * 使用方法：
 *   node tools/js/git_inspector.js [--mode MODE]
 * 
 * 参数说明：
 *   --mode MODE              检查模式（默认：status）
 *                           可选值：status（仓库状态）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "branch": "分支名",
 *       "changes": [
 *         {"status": "状态码", "file": "文件路径"},
 *         ...
 *       ],
 *       "clean": 是否干净(bool)
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   // 检查仓库状态
 *   node tools/js/git_inspector.js --mode status
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2025-12-02
 */

const { execSync } = require('child_process');

function getGitStatus() {
    try {
        // Check if git exists
        execSync("git --version", { stdio: 'ignore' });
        
        // Get status
        const statusOutput = execSync("git status --porcelain", { encoding: 'utf8' });
        
        const changes = [];
        statusOutput.split('\n').forEach(line => {
            if (line.length > 3) {
                const status = line.substring(0, 2);
                const file = line.substring(3);
                changes.push({ status, file });
            }
        });
        
        // Get branch
        const branch = execSync("git branch --show-current", { encoding: 'utf8' }).trim();
        
        return {
            branch: branch,
            changes: changes,
            clean: changes.length === 0
        };
    } catch (e) {
        if (e.message.includes("not a git repository")) {
             return { error: "Not a git repository" };
        }
        return { error: e.message };
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let currentMode = "status";
    for (let i = 0; i < args.length; i++) {
        if (args[i] === "--mode") {
            currentMode = args[i+1];
        }
    }
    
    const gitData = currentMode === "status" ? getGitStatus() : { error: `Unknown mode: ${currentMode}` };
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    const result = {
        data: gitData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        }
    };
    console.log(JSON.stringify(result, null, 2));
}

main();
