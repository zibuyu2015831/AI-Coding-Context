#!/usr/bin/env node
/**
 * Commit 模板 CLI 工具 - 交互式生成结构化 commit
 * 
 * 功能说明：
 * - 交互式引导生成结构化 commit message
 * - 支持快速模式（命令行参数直接生成）
 * - 实时质量评分和改进建议
 * - 符合 Commit-as-Prompt 规范
 * - 跨平台兼容（Windows, macOS, Linux）
 * 
 * 使用方法：
 *   node tools/js/commit_template_cli.js                    # 交互式模式
 *   node tools/js/commit_template_cli.js --quick [OPTIONS] # 快速模式
 *   node tools/js/commit_template_cli.js --help            # 显示帮助
 * 
 * 参数说明：
 *   --help, -h        显示使用说明
 *   --quick           快速模式（跳过交互）
 *   --type TYPE       Commit 类型（feature/fix/architecture/other）
 *   --what WHAT       做什么（WHAT 描述）
 *   --why WHY         为什么做（WHY 原因）
 *   --how HOW         怎么做（逗号分隔的步骤列表）
 * 
 * 使用示例：
 *   # 示例 1: 交互式模式
 *   node tools/js/commit_template_cli.js
 * 
 *   # 示例 2: 快速模式
 *   node tools/js/commit_template_cli.js --quick --type feature --what "添加用户登录功能" --why "满足用户需求" --how "实现登录API,添加前端表单"
 * 
 *   # 示例 3: 查看帮助
 *   node tools/js/commit_template_cli.js --help
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-19
 */

const readline = require('readline');
const { execSync } = require('child_process');
const path = require('path');

/**
 * 创建 readline 接口
 * @returns {readline.Interface}
 */
function createInterface() {
    return readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
}

/**
 * 询问用户输入
 * @param {string} prompt - 提示文本
 * @returns {Promise<string>} 用户输入
 */
function askQuestion(prompt) {
    const rl = createInterface();
    return new Promise((resolve) => {
        rl.question(prompt, (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

/**
 * 询问多行输入
 * @param {string} prompt - 提示文本
 * @returns {Promise<Array<string>>} 用户输入的行数组
 */
function askMultiline(prompt) {
    console.log(prompt);
    const rl = createInterface();
    const lines = [];
    
    return new Promise((resolve) => {
        rl.on('line', (line) => {
            const trimmed = line.trim();
            if (trimmed === '') {
                rl.close();
                resolve(lines);
            } else {
                lines.push(trimmed);
            }
        });
    });
}

/**
 * 交互式模式
 * @returns {Promise<Object>} { commitType, what, why, howItems }
 */
async function interactiveMode() {
    console.log('📝 Commit-as-Prompt 向导\n');
    
    // 选择类型
    console.log('[1/4] 变更类型:');
    console.log('  1. 新功能 (feature)');
    console.log('  2. Bug修复 (fix)');
    console.log('  3. 架构调整 (architecture)');
    console.log('  4. 其他\n');
    
    const typeChoice = await askQuestion('选择: ');
    const typeMap = {
        '1': 'feature',
        '2': 'fix',
        '3': 'architecture',
        '4': 'other'
    };
    const commitType = typeMap[typeChoice] || 'feature';
    
    // WHAT
    console.log('\n[2/4] WHAT - 做什么? (一句话描述)');
    const what = await askQuestion('> ');
    
    // WHY
    console.log('\n[3/4] WHY - 为什么做? (业务动机、需求编号)');
    const why = await askQuestion('> ');
    
    // HOW
    const howItems = await askMultiline('\n[4/4] HOW - 怎么做? (实现策略、风险点，每行一条，空行结束)\n> ');
    
    return { commitType, what, why, howItems };
}

/**
 * 生成 commit message
 * @param {string} commitType - Commit 类型
 * @param {string} what - WHAT 内容
 * @param {string} why - WHY 内容
 * @param {Array<string>} howItems - HOW 列表
 * @returns {string} 生成的 commit message
 */
function generateCommitMessage(commitType, what, why, howItems) {
    let message = `prompt(${commitType}): ${what}\n\n`;
    message += `WHAT: ${what}\n`;
    message += `WHY: ${why}\n`;
    message += 'HOW:\n';
    for (const item of howItems) {
        message += `- ${item}\n`;
    }
    return message;
}

/**
 * 计算质量评分（调用外部工具）
 * @param {string} message - Commit message
 * @returns {Object|null} 评分结果，失败返回 null
 */
function calculateQualityScore(message) {
    try {
        // 转义双引号
        const escapedMessage = message.replace(/"/g, '\\"').replace(/\n/g, '\\n');
        const scriptPath = path.join(__dirname, 'commit_quality_scorer.js');
        
        const result = execSync(
            `node "${scriptPath}" --message "${escapedMessage}"`,
            { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }
        );
        
        const parsed = JSON.parse(result);
        return parsed.data;
    } catch (error) {
        // 失败时返回 null，不影响主流程
        return null;
    }
}

/**
 * 显示使用说明
 */
function showUsage() {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║  Commit 模板 CLI 工具                                    ║
╚══════════════════════════════════════════════════════════╝

功能:
  • 交互式生成结构化 commit message
  • 支持快速模式（命令行参数）
  • 实时质量评分和改进建议
  • 符合 Commit-as-Prompt 规范

使用方式:
  node tools/js/commit_template_cli.js                    # 交互式
  node tools/js/commit_template_cli.js --quick [OPTIONS] # 快速模式

参数说明:
  --help, -h        显示此帮助信息
  --quick           快速模式（跳过交互）
  --type TYPE       Commit 类型（feature/fix/architecture/other）
  --what WHAT       做什么（WHAT 描述）
  --why WHY         为什么做（WHY 原因）
  --how HOW         怎么做（逗号分隔）

示例:
  # 交互式模式
  node tools/js/commit_template_cli.js

  # 快速模式
  node tools/js/commit_template_cli.js --quick \\
    --type feature \\
    --what "添加用户登录功能" \\
    --why "满足用户需求" \\
    --how "实现登录API,添加前端表单"
`);
}

/**
 * 解析命令行参数
 * @param {Array<string>} args - 命令行参数
 * @returns {Object} 解析后的参数对象
 */
function parseArgs(args) {
    const result = {
        help: false,
        quick: false,
        type: 'feature',
        what: null,
        why: null,
        how: null
    };
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        
        if (arg === '--help' || arg === '-h') {
            result.help = true;
        } else if (arg === '--quick') {
            result.quick = true;
        } else if (arg === '--type' && i + 1 < args.length) {
            result.type = args[++i];
        } else if (arg === '--what' && i + 1 < args.length) {
            result.what = args[++i];
        } else if (arg === '--why' && i + 1 < args.length) {
            result.why = args[++i];
        } else if (arg === '--how' && i + 1 < args.length) {
            result.how = args[++i];
        }
    }
    
    return result;
}

/**
 * 主函数
 */
async function main() {
    const args = parseArgs(process.argv.slice(2));
    
    if (args.help) {
        showUsage();
        process.exit(0);
    }
    
    let commitType, what, why, howItems;
    
    if (args.quick) {
        // 快速模式
        commitType = args.type;
        what = args.what || '未指定';
        why = args.why || '未指定';
        howItems = args.how ? args.how.split(',').map(s => s.trim()) : [];
    } else {
        // 交互模式
        const result = await interactiveMode();
        commitType = result.commitType;
        what = result.what;
        why = result.why;
        howItems = result.howItems;
    }
    
    // 生成 commit message
    const message = generateCommitMessage(commitType, what, why, howItems);
    
    console.log('\n✅ 生成的commit:');
    console.log('-'.repeat(40));
    console.log(message);
    console.log('-'.repeat(40));
    
    // 质量评分
    const scoreResult = calculateQualityScore(message);
    if (scoreResult) {
        console.log(`\n💯 质量评分: ${scoreResult.total_score}/100 ${scoreResult.grade}`);
        console.log(`  - WHAT清晰度: ${scoreResult.breakdown.what_clarity}/30`);
        console.log(`  - WHY深度: ${scoreResult.breakdown.why_depth}/30`);
        console.log(`  - HOW完整性: ${scoreResult.breakdown.how_completeness}/20`);
        
        if (scoreResult.suggestions && scoreResult.suggestions.length > 0) {
            console.log('\n建议:');
            for (const suggestion of scoreResult.suggestions.slice(0, 3)) {
                console.log(`  - ${suggestion}`);
            }
        }
    }
    
    // 询问是否执行
    if (!args.quick) {
        const confirm = await askQuestion('\n执行? (Y/n): ');
        if (confirm.toLowerCase() === 'y' || confirm === '') {
            console.log('\n提示: 请手动执行: git commit -m "<message>"');
        } else {
            console.log('\n已取消');
        }
    }
}

// 执行主函数
if (require.main === module) {
    main().catch((error) => {
        console.error('❌ 发生错误:', error.message);
        process.exit(1);
    });
}

// 导出函数供测试使用
module.exports = {
    interactiveMode,
    generateCommitMessage,
    calculateQualityScore,
    askQuestion,
    askMultiline,
    parseArgs
};
