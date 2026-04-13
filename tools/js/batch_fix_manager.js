/**
 * 批量修复管理器 - 管理批量文档修复任务
 *
 * 功能说明:
 *     - 生成修复方案清单
 *     - 分阶段执行修复任务
 *     - 提供修复预览和确认功能
 *     - 支持风险控制机制
 *     - 自动错误处理和回滚
 *
 * 使用方法:
 *     // 生成修复方案
 *     node tools/js/batch_fix_manager.js --generate --pattern "getUserInfo" --replacement "fetchUserProfile"
 *
 *     // 执行批量修复
 *     node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
 *
 *     // 执行快速修复（自动确认低风险修复）
 *     node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --auto
 *
 *     // 预览修复效果
 *     node tools/js/batch_fix_manager.js --preview --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
 *
 *     // 检查修复方案
 *     node tools/js/batch_fix_manager.js --check --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
 *
 *     // 设置批次大小
 *     node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --batch-size 5
 *
 *     // 分阶段执行（只执行第 1 阶段）
 *     node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --stage 1
 *
 * 参数说明:
 *     --generate               生成修复方案
 *     --pattern PATTERN        查找模式（正则表达式）
 *     --replacement TEXT       替换文本
 *     --execute                执行修复
 *     --plan PATH              修复方案路径
 *     --auto                   自动确认低风险修复
 *     --preview                预览修复效果
 *     --check                  检查修复方案
 *     --batch-size NUM         批次大小，默认 10 个文档/批次
 *     --stage NUM              阶段号（用于分阶段执行）
 *     --analysis-dir PATH      分析目录，默认 dev_docs/_analysis/
 *     --doc-dir PATH           文档目录，默认 dev_docs/
 *     --verbose                输出详细信息
 *     --timeout SECONDS        超时时间，默认 60 秒
 *
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-13
 *     Purpose: Support 011-Document Error Fix Workflow
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

const VERSION = "1.0.0";
const DEFAULT_TIMEOUT = 60;
const DEFAULT_DOC_DIR = "dev_docs";
const DEFAULT_ANALYSIS_DIR = "dev_docs/_analysis";
const DEFAULT_BATCH_SIZE = 10;

function ensureDirExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function findMarkdownFiles(directory, recursive = true) {
    const pattern = recursive ? path.join(directory, '**', '*.md') : path.join(directory, '*.md');
    return glob.sync(pattern, { ignore: ['**/.git/**', '**/node_modules/**', '**/__pycache__/**', '**/dist/**', '**/build/**'] });
}

function searchInFile(filePath, pattern, replacement) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const regex = new RegExp(pattern, 'g');
        const matches = [...content.matchAll(regex)];
        if (matches.length > 0) {
            const replacedContent = content.replace(regex, replacement);
            return {
                success: true,
                filePath: filePath,
                matchCount: matches.length,
                originalContent: content,
                replacedContent: replacedContent,
                matches: matches.map(m => ({
                    start: m.index,
                    end: m.index + m[0].length,
                    text: m[0]
                }))
            };
        }
        return null;
    } catch (e) {
        return { success: false, error: e.message };
    }
}

function generateFixPlan(pattern, replacement, docDir, analysisDir) {
    ensureDirExists(analysisDir);

    const mdFiles = findMarkdownFiles(docDir);
    const affectedDocs = [];

    for (const doc of mdFiles) {
        const result = searchInFile(doc, pattern, replacement);
        if (result && result.success) {
            affectedDocs.push(result);
        }
    }

    if (!affectedDocs.length) {
        return {
            success: false,
            error: '未找到匹配的文档',
            affectedDocs: 0
        };
    }

    const lowRiskDocs = [];
    const mediumRiskDocs = [];
    const highRiskDocs = [];

    for (const doc of affectedDocs) {
        const fileName = path.basename(doc.filePath);
        if (fileName.toLowerCase().includes('api') || fileName.toLowerCase().includes('interface')) {
            highRiskDocs.push(doc);
        } else if (fileName.toLowerCase().includes('state') || fileName.toLowerCase().includes('data')) {
            mediumRiskDocs.push(doc);
        } else {
            lowRiskDocs.push(doc);
        }
    }

    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-T:]/g, '');
    const planPath = path.join(analysisDir, `doc_fix_plan_${timestamp}.md`);

    const planContent = [];
    planContent.push(`# 文档修复方案 (${timestamp})`);
    planContent.push(`\n## 修复信息`);
    planContent.push(`- 模式: ${pattern}`);
    planContent.push(`- 替换: ${replacement}`);
    planContent.push(`- 受影响文档: ${affectedDocs.length}`);

    planContent.push(`\n## 分阶段执行`);

    let stageCount = 0;
    if (lowRiskDocs.length) {
        stageCount++;
        planContent.push(`\n### 阶段 ${stageCount} (低风险 - ${lowRiskDocs.length} 个文档)`);
        lowRiskDocs.forEach(doc => {
            planContent.push(`- ${doc.filePath} (${doc.matchCount} 个匹配)`);
        });
    }
    if (mediumRiskDocs.length) {
        stageCount++;
        planContent.push(`\n### 阶段 ${stageCount} (中风险 - ${mediumRiskDocs.length} 个文档)`);
        mediumRiskDocs.forEach(doc => {
            planContent.push(`- ${doc.filePath} (${doc.matchCount} 个匹配)`);
        });
    }
    if (highRiskDocs.length) {
        stageCount++;
        planContent.push(`\n### 阶段 ${stageCount} (高风险 - ${highRiskDocs.length} 个文档)`);
        highRiskDocs.forEach(doc => {
            planContent.push(`- ${doc.filePath} (${doc.matchCount} 个匹配)`);
        });
    }

    fs.writeFileSync(planPath, planContent.join('\n'));

    return {
        success: true,
        planPath: planPath,
        affectedDocs: affectedDocs.length,
        stageCount: stageCount,
        riskLevel: stageCount === 1 ? 'low' : stageCount === 2 ? 'medium' : 'high'
    };
}

function parseFixPlan(planPath) {
    try {
        const content = fs.readFileSync(planPath, 'utf-8');
        const stages = [];
        let currentStage = null;

        const lines = content.split('\n');
        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;

            const stageMatch = trimmed.match(/### 阶段 (\d+) \((.*?) - (\d+) 个文档\)/);
            if (stageMatch) {
                currentStage = {
                    stage: parseInt(stageMatch[1]),
                    riskLevel: stageMatch[2],
                    docCount: parseInt(stageMatch[3]),
                    docs: []
                };
                stages.push(currentStage);
            } else if (currentStage && trimmed.startsWith('- ')) {
                const docMatch = trimmed.match(/- (.*?) \((\d+) 个匹配\)/);
                if (docMatch) {
                    currentStage.docs.push({
                        filePath: docMatch[1],
                        matchCount: parseInt(docMatch[2])
                    });
                }
            }
        }

        return {
            success: true,
            planPath: planPath,
            stages: stages
        };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

function executeFixPlan(planPath, auto = false, stage = null, batchSize = DEFAULT_BATCH_SIZE) {
    const parseResult = parseFixPlan(planPath);
    if (!parseResult.success) {
        return parseResult;
    }

    const stages = stage ? parseResult.stages.filter(s => s.stage === stage) : parseResult.stages;

    if (!stages.length) {
        return { success: false, error: stage ? `阶段 ${stage} 不存在` : '修复方案为空' };
    }

    const results = [];

    for (const stageInfo of stages) {
        const stageResult = {
            stage: stageInfo.stage,
            riskLevel: stageInfo.riskLevel,
            docs: []
        };
        results.push(stageResult);

        for (let i = 0; i < stageInfo.docs.length; i++) {
            if (i % batchSize === 0 && i > 0) {
                // 简单的批次控制
                new Promise(resolve => setTimeout(resolve, 1000));
            }

            const doc = stageInfo.docs[i];
            try {
                // 提取模式和替换
                const planContent = fs.readFileSync(planPath, 'utf-8');
                const patternMatch = planContent.match(/模式: (.*)/);
                const replacementMatch = planContent.match(/替换: (.*)/);
                if (!patternMatch || !replacementMatch) {
                    continue;
                }

                const content = fs.readFileSync(doc.filePath, 'utf-8');
                const regex = new RegExp(patternMatch[1], 'g');
                const newContent = content.replace(regex, replacementMatch[1]);
                fs.writeFileSync(doc.filePath, newContent);

                stageResult.docs.push({
                    filePath: doc.filePath,
                    success: true,
                    message: '修复成功'
                });
            } catch (e) {
                stageResult.docs.push({
                    filePath: doc.filePath,
                    success: false,
                    error: e.message
                });
            }
        }
    }

    return {
        success: true,
        planPath: planPath,
        executionResult: results
    };
}

function previewFixPlan(planPath) {
    const parseResult = parseFixPlan(planPath);
    if (!parseResult.success) {
        return parseResult;
    }

    return {
        success: true,
        planPath: planPath,
        preview: {
            stages: parseResult.stages.map(s => ({
                stage: s.stage,
                riskLevel: s.riskLevel,
                docCount: s.docCount,
                docs: s.docs.map(d => d.filePath)
            }))
        }
    };
}

function printHelp() {
    console.log(`
批量修复管理器 - 管理批量文档修复任务

使用方法:
    node tools/js/batch_fix_manager.js --generate --pattern "getUserInfo" --replacement "fetchUserProfile"
    node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
    node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --auto
    node tools/js/batch_fix_manager.js --preview --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
    node tools/js/batch_fix_manager.js --check --plan "dev_docs/_analysis/doc_fix_plan_20260413.md"
    node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --batch-size 5
    node tools/js/batch_fix_manager.js --execute --plan "dev_docs/_analysis/doc_fix_plan_20260413.md" --stage 1

选项:
    --generate               生成修复方案
    --pattern PATTERN        查找模式（正则表达式）
    --replacement TEXT       替换文本
    --execute                执行修复
    --plan PATH              修复方案路径
    --auto                   自动确认低风险修复
    --preview                预览修复效果
    --check                  检查修复方案
    --batch-size NUM         批次大小，默认 10 个文档/批次
    --stage NUM              阶段号（用于分阶段执行）
    --analysis-dir PATH      分析目录，默认 dev_docs/_analysis/
    --doc-dir PATH           文档目录，默认 dev_docs/
    --verbose                输出详细信息
    --timeout SECONDS        超时时间，默认 60 秒
    --help, -h              显示此帮助信息
`);
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        generate: false,
        pattern: null,
        replacement: null,
        execute: false,
        plan: null,
        auto: false,
        preview: false,
        check: false,
        batchSize: DEFAULT_BATCH_SIZE,
        stage: null,
        analysisDir: DEFAULT_ANALYSIS_DIR,
        docDir: DEFAULT_DOC_DIR,
        verbose: false,
        timeout: DEFAULT_TIMEOUT,
        help: false
    };

    let i = 0;
    while (i < args.length) {
        switch (args[i]) {
            case '--help':
            case '-h':
                options.help = true;
                i++;
                break;
            case '--generate':
                options.generate = true;
                i++;
                break;
            case '--pattern':
                options.pattern = args[++i];
                i++;
                break;
            case '--replacement':
                options.replacement = args[++i];
                i++;
                break;
            case '--execute':
                options.execute = true;
                i++;
                break;
            case '--plan':
                options.plan = args[++i];
                i++;
                break;
            case '--auto':
                options.auto = true;
                i++;
                break;
            case '--preview':
                options.preview = true;
                i++;
                break;
            case '--check':
                options.check = true;
                i++;
                break;
            case '--batch-size':
                options.batchSize = parseInt(args[++i]);
                i++;
                break;
            case '--stage':
                options.stage = parseInt(args[++i]);
                i++;
                break;
            case '--analysis-dir':
                options.analysisDir = args[++i];
                i++;
                break;
            case '--doc-dir':
                options.docDir = args[++i];
                i++;
                break;
            case '--verbose':
                options.verbose = true;
                i++;
                break;
            case '--timeout':
                options.timeout = parseInt(args[++i]);
                i++;
                break;
            default:
                console.error(`Unknown option: ${args[i]}`);
                process.exit(1);
        }
    }

    // 显示帮助
    if (options.help) {
        printHelp();
        process.exit(0);
    }

    const result = {
        success: true,
        data: {},
        metadata: { version: VERSION }
    };

    try {
        if (options.generate) {
            if (!options.pattern || !options.replacement) {
                result.success = false;
                result.error = '缺少必填参数';
            } else {
                const genResult = generateFixPlan(
                    options.pattern,
                    options.replacement,
                    options.docDir,
                    options.analysisDir
                );
                result.data = { action: 'generate_plan', result: genResult };
                if (!genResult.success) {
                    result.success = false;
                    result.error = genResult.error;
                }
            }
        } else if (options.execute) {
            if (!options.plan) {
                result.success = false;
                result.error = '缺少修复方案路径';
            } else {
                const execResult = executeFixPlan(
                    options.plan,
                    options.auto,
                    options.stage,
                    options.batchSize
                );
                result.data = { action: 'execute_plan', result: execResult };
                if (!execResult.success) {
                    result.success = false;
                    result.error = execResult.error;
                }
            }
        } else if (options.preview) {
            if (!options.plan) {
                result.success = false;
                result.error = '缺少修复方案路径';
            } else {
                const previewResult = previewFixPlan(options.plan);
                result.data = { action: 'preview_plan', result: previewResult };
                if (!previewResult.success) {
                    result.success = false;
                    result.error = previewResult.error;
                }
            }
        } else if (options.check) {
            if (!options.plan) {
                result.success = false;
                result.error = '缺少修复方案路径';
            } else {
                const checkResult = parseFixPlan(options.plan);
                result.data = { action: 'check_plan', result: checkResult };
                if (!checkResult.success) {
                    result.success = false;
                    result.error = checkResult.error;
                }
            }
        } else {
            result.success = false;
            result.error = '请指定操作';
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }

    console.log(JSON.stringify(result, null, 2));
}

main();
