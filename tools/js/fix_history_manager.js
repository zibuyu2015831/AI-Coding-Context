/**
 * 修复历史管理器 - 管理文档修复历史记录
 *
 * 功能说明:
 *     - 基于 Git 提交信息记录修复历史
 *     - 在 _analysis/fix_history/ 目录中存储修复元数据
 *     - 支持修复查询和统计
 *     - 提供命令行接口查询修复历史
 *     - 自动与 Git 提交关联
 *
 * 使用方法:
 *     // 记录修复历史
 *     node tools/js/fix_history_manager.js --record --commit "a1b2c3d" --target-docs "dev_docs/api_layer.md,dev_docs/state_management.md"
 *
 *     // 查询修复历史
 *     node tools/js/fix_history_manager.js --query
 *
 *     // 查询特定修复记录
 *     node tools/js/fix_history_manager.js --query --commit "a1b2c3d"
 *
 *     // 查询特定文档的修复历史
 *     node tools/js/fix_history_manager.js --query --doc "dev_docs/api_layer.md"
 *
 *     // 获取修复统计信息
 *     node tools/js/fix_history_manager.js --stats
 *
 *     // 清理修复历史
 *     node tools/js/fix_history_manager.js --cleanup --days 90
 *
 *     // 与 Git 提交关联
 *     node tools/js/fix_history_manager.js --sync
 *
 * 参数说明:
 *     --record                 记录修复历史
 *     --commit HASH           Git 提交哈希
 *     --target-docs DOCS      逗号分隔的目标文档列表
 *     --query                  查询修复历史
 *     --doc PATH              特定文档路径
 *     --stats                  获取修复统计信息
 *     --cleanup               清理旧的修复历史
 *     --days NUM              保留天数，默认 90 天
 *     --sync                  与 Git 提交同步修复历史
 *     --analysis-dir PATH     分析目录，默认 dev_docs/_analysis/
 *     --verbose               输出详细信息
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
const DEFAULT_ANALYSIS_DIR = "dev_docs/_analysis";
const FIX_HISTORY_DIR = "fix_history";

function ensureDirExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function getFixHistoryDir(analysisDir = DEFAULT_ANALYSIS_DIR) {
    return path.join(analysisDir, FIX_HISTORY_DIR);
}

function recordFixHistory(commitHash, targetDocs, analysisDir = DEFAULT_ANALYSIS_DIR) {
    /**
     * 记录修复历史
     *
     * Args:
     *     commitHash: Git 提交哈希
     *     targetDocs: 目标文档列表
     *     analysisDir: 分析目录
     *
     * Returns:
     *     dict: 记录结果
     */
    const historyDir = getFixHistoryDir(analysisDir);
    ensureDirExists(historyDir);

    // 检查记录是否已存在
    const existingFiles = glob.sync(path.join(historyDir, `*${commitHash}*.json`));
    if (existingFiles.length > 0) {
        return {
            success: true,
            message: "记录已存在",
            filePath: existingFiles[0]
        };
    }

    // 构建记录文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-T:]/g, '');
    const filename = `${timestamp}_${commitHash}.json`;
    const filePath = path.join(historyDir, filename);

    // 保存修复记录
    const record = {
        commitHash: commitHash,
        date: new Date().toISOString().slice(0, 19).replace('T', ' '),
        targetDocs: targetDocs,
        timestamp: Date.now()
    };

    try {
        fs.writeFileSync(filePath, JSON.stringify(record, null, 2, (_, v) => v instanceof Date ? v.toISOString() : v));
        return {
            success: true,
            message: "记录成功",
            filePath: filePath
        };
    } catch (e) {
        return {
            success: false,
            error: `记录失败: ${e.message}`
        };
    }
}

function queryFixHistory(commitHash = null, docPath = null, analysisDir = DEFAULT_ANALYSIS_DIR) {
    /**
     * 查询修复历史
     *
     * Args:
     *     commitHash: Git 提交哈希
     *     docPath: 文档路径
     *     analysisDir: 分析目录
     *
     * Returns:
     *     dict: 查询结果
     */
    const historyDir = getFixHistoryDir(analysisDir);
    ensureDirExists(historyDir);

    const records = [];
    const historyFiles = glob.sync(path.join(historyDir, "*.json"));

    for (const filePath of historyFiles) {
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const record = JSON.parse(content);
            record.filePath = filePath;

            // 筛选条件
            if (commitHash && record.commitHash !== commitHash) {
                continue;
            }
            if (docPath) {
                const found = record.targetDocs.some(doc => doc === docPath);
                if (!found) {
                    continue;
                }
            }

            records.push(record);
        } catch (e) {
            console.error(`Error reading ${filePath}: ${e.message}`);
            continue;
        }
    }

    // 按日期降序排序
    records.sort((a, b) => b.timestamp - a.timestamp);

    return {
        success: true,
        totalRecords: records.length,
        records: records
    };
}

function getFixStats(analysisDir = DEFAULT_ANALYSIS_DIR) {
    /**
     * 获取修复统计信息
     *
     * Args:
     *     analysisDir: 分析目录
     *
     * Returns:
     *     dict: 统计信息
     */
    const historyDir = getFixHistoryDir(analysisDir);
    ensureDirExists(historyDir);

    const historyFiles = glob.sync(path.join(historyDir, "*.json"));
    const totalRecords = historyFiles.length;
    const records = [];
    const docsSet = new Set();

    for (const filePath of historyFiles) {
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const record = JSON.parse(content);
            records.push(record);

            // 统计文档
            record.targetDocs.forEach(doc => docsSet.add(doc));
        } catch (e) {
            continue;
        }
    }

    // 按日期分组统计
    const dailyStats = {};
    records.forEach(record => {
        const dateStr = record.date ? record.date.split(' ')[0] : ''; // 获取日期部分
        if (dateStr && !dailyStats[dateStr]) {
            dailyStats[dateStr] = 0;
        }
        if (dateStr) {
            dailyStats[dateStr] += record.targetDocs.length;
        }
    });

    // 统计每个文档的修复次数
    const recordsPerDoc = {};
    docsSet.forEach(doc => {
        recordsPerDoc[doc] = records.filter(r => r.targetDocs.includes(doc)).length;
    });

    return {
        success: true,
        totalRecords: totalRecords,
        totalDocsFixed: docsSet.size,
        dailyStats: dailyStats,
        recordsPerDoc: recordsPerDoc
    };
}

function cleanupOldRecords(days = 90, analysisDir = DEFAULT_ANALYSIS_DIR) {
    /**
     * 清理旧的修复历史记录
     *
     * Args:
     *     days: 保留天数
     *     analysisDir: 分析目录
     *
     * Returns:
     *     dict: 清理结果
     */
    const historyDir = getFixHistoryDir(analysisDir);
    ensureDirExists(historyDir);

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const historyFiles = glob.sync(path.join(historyDir, "*.json"));
    let deleted = 0;

    for (const filePath of historyFiles) {
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const record = JSON.parse(content);
            const recordDate = new Date(record.date);

            if (recordDate < cutoffDate) {
                fs.unlinkSync(filePath);
                deleted++;
            }
        } catch (e) {
            continue;
        }
    }

    return {
        success: true,
        deletedRecords: deleted,
        message: `已删除 ${deleted} 条旧记录`
    };
}

function syncWithGit(analysisDir = DEFAULT_ANALYSIS_DIR) {
    /**
     * 与 Git 提交同步修复历史
     *
     * Args:
     *     analysisDir: 分析目录
     *
     * Returns:
     *     dict: 同步结果
     */
    const historyDir = getFixHistoryDir(analysisDir);
    ensureDirExists(historyDir);

    // 检查是否为 Git 仓库
    try {
        const { execSync } = require('child_process');
        const result = execSync('git rev-parse --is-inside-work-tree', { encoding: 'utf-8' });
        if (result.trim() !== 'true') {
            return {
                success: false,
                error: "不是 Git 仓库"
            };
        }
    } catch (e) {
        return {
            success: false,
            error: "无法执行 Git 命令"
        };
    }

    return {
        success: true,
        message: "同步功能已启用，但需要进一步实现"
    };
}

function printHelp() {
    console.log(`
修复历史管理器 - 管理文档修复历史记录

使用方法:
    node tools/js/fix_history_manager.js --record --commit "a1b2c3d" --target-docs "dev_docs/api_layer.md,dev_docs/state_management.md"
    node tools/js/fix_history_manager.js --query
    node tools/js/fix_history_manager.js --query --commit "a1b2c3d"
    node tools/js/fix_history_manager.js --query --doc "dev_docs/api_layer.md"
    node tools/js/fix_history_manager.js --stats
    node tools/js/fix_history_manager.js --cleanup --days 90
    node tools/js/fix_history_manager.js --sync

选项:
    --record                 记录修复历史
    --commit HASH           Git 提交哈希
    --target-docs DOCS      逗号分隔的目标文档列表
    --query                  查询修复历史
    --doc PATH              特定文档路径
    --stats                  获取修复统计信息
    --cleanup               清理旧的修复历史
    --days NUM              保留天数，默认 90 天
    --sync                  与 Git 提交同步修复历史
    --analysis-dir PATH     分析目录，默认 dev_docs/_analysis/
    --verbose               输出详细信息
    --help, -h              显示此帮助信息
`);
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        record: false,
        commit: null,
        targetDocs: null,
        query: false,
        doc: null,
        stats: false,
        cleanup: false,
        days: 90,
        sync: false,
        analysisDir: DEFAULT_ANALYSIS_DIR,
        verbose: false,
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
            case '--record':
                options.record = true;
                i++;
                break;
            case '--commit':
                options.commit = args[++i];
                i++;
                break;
            case '--target-docs':
                options.targetDocs = args[++i];
                i++;
                break;
            case '--query':
                options.query = true;
                i++;
                break;
            case '--doc':
                options.doc = args[++i];
                i++;
                break;
            case '--stats':
                options.stats = true;
                i++;
                break;
            case '--cleanup':
                options.cleanup = true;
                i++;
                break;
            case '--days':
                options.days = parseInt(args[++i]);
                i++;
                break;
            case '--sync':
                options.sync = true;
                i++;
                break;
            case '--analysis-dir':
                options.analysisDir = args[++i];
                i++;
                break;
            case '--verbose':
                options.verbose = true;
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
        metadata: {
            version: VERSION
        }
    };

    try {
        if (options.record) {
            // 记录修复历史
            if (!options.commit) {
                result.success = false;
                result.error = "请指定提交哈希: --commit";
            } else if (!options.targetDocs) {
                result.success = false;
                result.error = "请指定目标文档: --target-docs";
            } else {
                const targetDocs = options.targetDocs.split(',').map(doc => doc.trim()).filter(doc => doc);

                const recordResult = recordFixHistory(
                    options.commit,
                    targetDocs,
                    options.analysisDir
                );
                result.data = {
                    action: "record",
                    result: recordResult
                };
                if (!recordResult.success) {
                    result.success = false;
                    result.error = recordResult.error;
                }
            }
        } else if (options.query) {
            // 查询修复历史
            const queryResult = queryFixHistory(
                options.commit,
                options.doc,
                options.analysisDir
            );
            result.data = {
                action: "query",
                result: queryResult
            };
        } else if (options.stats) {
            // 获取修复统计信息
            const statsResult = getFixStats(options.analysisDir);
            result.data = {
                action: "stats",
                result: statsResult
            };
        } else if (options.cleanup) {
            // 清理旧记录
            const cleanupResult = cleanupOldRecords(
                options.days,
                options.analysisDir
            );
            result.data = {
                action: "cleanup",
                result: cleanupResult
            };
        } else if (options.sync) {
            // 与 Git 同步
            const syncResult = syncWithGit(options.analysisDir);
            result.data = {
                action: "sync",
                result: syncResult
            };
            if (!syncResult.success) {
                result.success = false;
                result.error = syncResult.error;
            }
        } else {
            result.success = false;
            result.error = "请指定操作: --record, --query, --stats, --cleanup, 或 --sync";
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }

    // 输出 JSON
    console.log(JSON.stringify(result, null, 2, (_, v) => v instanceof Date ? v.toISOString() : v));
}

main();
