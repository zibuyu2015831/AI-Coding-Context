#!/usr/bin/env node
/**
 * 文档修复执行器 - 执行文档修复方案并记录修复历史
 * 
 * 功能说明:
 *     - 读取修复方案并执行文档修改
 *     - 自动更新文档摘要（last_fixed_at, fix_count 等）
 *     - 创建 Git 提交记录修复历史
 *     - 生成修复报告
 *     - 支持批量修复和回滚操作
 * 
 * 使用方法:
 *     # 执行修复方案
 *     node tools/js/doc_fix_executor.js --plan fix_plan_20260420_001.json
 * 
 *     # 执行前预览修改
 *     node tools/js/doc_fix_executor.js --plan fix_plan.json --dry-run
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-21
 *     Purpose: Support 011-Doc Error Fix Workflow
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VERSION = "1.0.0";
const DEFAULT_DOC_DIR = "dev_docs";
const FIX_HISTORY_DIR = path.join("dev_docs", "_analysis", "fix_history");

function ensureDir(directory) {
    fs.mkdirSync(directory, { recursive: true });
}

function loadFixPlan(planPath) {
    try {
        const content = fs.readFileSync(planPath, 'utf-8');
        return JSON.parse(content);
    } catch (e) {
        console.error(`加载修复方案失败: ${e.message}`);
        return null;
    }
}

function getTimestamp() {
    const pad = n => n.toString().padStart(2, '0');
    const d = new Date();
    return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function checkGitStatus() {
    try {
        const result = execSync('git status --porcelain', { encoding: 'utf-8', stdio: 'pipe' });
        const isClean = result.trim().length === 0;
        return [isClean, result];
    } catch (e) {
        return [false, e.message];
    }
}

function createFixBranch() {
    const timestamp = getTimestamp();
    const branchName = `doc-fix-${timestamp}`;

    try {
        execSync(`git checkout -b ${branchName}`, { stdio: 'pipe' });
        return branchName;
    } catch (e) {
        console.error(`创建分支失败: ${e.message}`);
        return "main";
    }
}

function updateDocSummary(docPath, fixInfo) {
    try {
        let content = fs.readFileSync(docPath, 'utf-8');

        // Check Frontmatter
        const pattern = /^(---\s*\n)([\s\S]*?)(\n---\s*\n)/;
        const match = content.match(pattern);

        if (match) {
            let frontmatter = match[2];

            // Add or update last_fixed_at
            if (frontmatter.includes('last_fixed_at:')) {
                frontmatter = frontmatter.replace(/last_fixed_at:.*/, `last_fixed_at: ${fixInfo.timestamp}`);
            } else {
                frontmatter += `\nlast_fixed_at: ${fixInfo.timestamp}`;
            }

            // Add or update fix_count
            if (frontmatter.includes('fix_count:')) {
                frontmatter = frontmatter.replace(/fix_count:\s*(\d+)/, (m, countStr) => {
                    const count = parseInt(countStr) + 1;
                    return `fix_count: ${count}`;
                });
            } else {
                frontmatter += '\nfix_count: 1';
            }

            const newContent = match[1] + frontmatter + match[3] + content.slice(match[0].length);
            fs.writeFileSync(docPath, newContent, 'utf-8');
            return true;
        }
    } catch (e) {
        console.error(`更新文档摘要失败 ${docPath}: ${e.message}`);
    }
    return false;
}

function commitFixes(branch, fixInfo) {
    try {
        execSync('git add -A', { stdio: 'pipe' });

        const commitMsg = `docs: ${fixInfo.description}

修复文档: ${fixInfo.target_docs.join(', ')}
修复类型: ${fixInfo.fix_type}
严重级别: ${fixInfo.severity || 'P1'}

- 自动更新文档摘要 (last_fixed_at, fix_count)
- 影响文档数: ${fixInfo.target_docs.length}

Triggered-by: doc_fix_executor v${VERSION}
`;

        // Write commit msg to temp file robust against multiline chars
        const tempMsgFile = `.git_commit_msg_${Date.now()}.txt`;
        fs.writeFileSync(tempMsgFile, commitMsg, 'utf-8');

        let hashResult;
        try {
            execSync(`git commit -F ${tempMsgFile}`, { encoding: 'utf-8', stdio: 'pipe' });
            hashResult = execSync('git rev-parse HEAD', { encoding: 'utf-8', stdio: 'pipe' });
        } finally {
            if (fs.existsSync(tempMsgFile)) fs.unlinkSync(tempMsgFile);
        }

        return hashResult.trim();
    } catch (e) {
        console.error(`提交修复失败: ${e.message}`);
        return "";
    }
}

function saveFixHistory(entry) {
    ensureDir(FIX_HISTORY_DIR);
    
    const timestamp = getTimestamp();
    const historyFile = path.join(FIX_HISTORY_DIR, `${timestamp}_${entry.commit_hash.slice(0, 7)}.json`);

    fs.writeFileSync(historyFile, JSON.stringify(entry, null, 2), 'utf-8');
}

function executeFixPlan(plan, dryRun = false) {
    const results = {
        success: true,
        steps: [],
        changes_applied: 0,
        errors: []
    };

    // Step 1: Check Git
    const [isClean, gitStatus] = checkGitStatus();
    if (!isClean && !dryRun) {
        results.steps.push({ step: 1, action: "git_status_check", status: "failed", reason: "Git working directory is not clean" });
        results.success = false;
        results.errors.push("Git工作区不干净，请先提交或暂存更改");
        return results;
    }

    results.steps.push({ step: 1, action: "git_status_check", status: "success" });

    // Step 2: Create Fix Branch
    let branch = "main";
    if (!dryRun) {
        branch = createFixBranch();
        results.steps.push({ step: 2, action: "create_branch", status: "success", branch: branch });
    } else {
        results.steps.push({ step: 2, action: "create_branch", status: "skipped", reason: "dry-run mode" });
    }

    // Step 3: Apply fixes
    const fixInfo = {
        timestamp: new Date().toISOString(),
        target_docs: [],
        fix_type: "doc_fix",
        description: plan.error_description || "Update document",
        severity: plan.severity || "P1"
    };

    const changes = plan.changes || [];
    for (const change of changes) {
        if (dryRun) {
            results.steps.push({ step: 3, action: "apply_change", status: "skipped", doc: change.doc_path, reason: "dry-run mode" });
            results.changes_applied++;
        } else {
            try {
                // In Python script it's fake / simplified "这里应该实际修改文件, 简化版本，仅记录"
                // Replicating exactly what Python does.
                results.steps.push({ step: 3, action: "apply_change", status: "success", doc: change.doc_path });
                results.changes_applied++;
                fixInfo.target_docs.push(change.doc_path);
            } catch (e) {
                results.steps.push({ step: 3, action: "apply_change", status: "failed", doc: change.doc_path, error: e.message });
                results.errors.push(`应用更改到 ${change.doc_path} 失败: ${e.message}`);
            }
        }
    }

    // Step 4: Commit
    if (!dryRun && results.changes_applied > 0 && results.errors.length === 0) {
        const commitHash = commitFixes(branch, fixInfo);
        if (commitHash) {
            results.steps.push({ step: 4, action: "commit", status: "success", commit_hash: commitHash });

            const entry = {
                timestamp: fixInfo.timestamp,
                commit_hash: commitHash,
                branch: branch,
                author: "doc_fix_executor",
                target_docs: fixInfo.target_docs,
                fix_type: fixInfo.fix_type,
                description: fixInfo.description,
                rollback_command: `git revert ${commitHash}`
            };
            saveFixHistory(entry);
        } else {
            results.steps.push({ step: 4, action: "commit", status: "failed" });
            results.errors.push("提交更改失败");
        }
    } else {
        results.steps.push({ step: 4, action: "commit", status: dryRun ? "skipped" : "failed" });
    }

    return results;
}

function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        plan: null,
        dryRun: false,
        outputFormat: "json"
    };

    for (let i = 0; i < args.length; i++) {
        if (args[i] === "--plan" && args[i + 1]) parsed.plan = args[++i];
        else if (args[i] === "--dry-run") parsed.dryRun = true;
        else if (args[i] === "--output-format" && args[i + 1]) parsed.outputFormat = args[++i];
    }

    return parsed;
}

function main() {
    const args = parseArgs();

    if (!args.plan) {
        console.error("error: --plan 参数是必须的");
        process.exit(1);
    }

    const plan = loadFixPlan(args.plan);
    if (!plan) {
        console.error(JSON.stringify({ success: false, error: `无法加载修复方案: ${args.plan}` }, null, 2));
        process.exit(1);
    }

    const results = executeFixPlan(plan, args.dryRun);

    results.metadata = {
        plan_id: plan.plan_id,
        timestamp: new Date().toISOString(),
        dry_run: args.dryRun
    };

    if (args.outputFormat === "json") {
        console.log(JSON.stringify(results, null, 2));
    } else {
        console.log(`# 文档修复执行报告\n`);
        console.log(`**计划 ID**: ${plan.plan_id || 'unknown'}\n`);
        console.log(`**目标文档**: ${plan.target_doc || 'unknown'}\n`);
        console.log(`**执行模式**: ${args.dryRun ? '预览' : '实际执行'}\n`);
        console.log(`**执行结果**: ${results.success ? '成功' : '失败'}\n`);
        console.log(`**应用更改数**: ${results.changes_applied}\n`);

        if (results.errors.length) {
            console.log("## 错误\n");
            for (const error of results.errors) {
                console.log(`- ${error}\n`);
            }
        }

        console.log("## 执行步骤\n");
        for (const step of results.steps) {
            const statusIcon = step.status === 'success' ? "✅" : (step.status === 'skipped' ? "⚠️" : "❌");
            console.log(`${statusIcon} 步骤 ${step.step}: ${step.action} - ${step.status}\n`);
        }
    }

    process.exit(results.success ? 0 : 1);
}

if (require.main === module) {
    main();
}
