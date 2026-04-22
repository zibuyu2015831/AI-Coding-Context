/**
 * 时间戳分析工具 - 采集项目文件和文档的修改时间供 AI 分析文档健康度
 * 
 * 功能说明:
 *   递归采集指定目录下文件的时间戳信息，
 *   为 AI 分析文档健康度、判断文档是否过期提供数据支持。
 *   - 采集文件最后修改时间 (mtime)
 *   - 计算文件年龄和相对新鲜度
 *   - 识别最旧和最新的文件
 *   - 生成时间戳统计信息
 *   - 支持按文件类型过滤
 * 
 * 使用方法:
 *   # 分析当前目录
 *   node tools/js/timestamp_analyzer.js
 * 
 *   # 分析指定目录
 *   node tools/js/timestamp_analyzer.js --path docs/
 * 
 *   # 仅分析 Markdown 文件
 *   node tools/js/timestamp_analyzer.js --ext .md
 * 
 *   # 限制扫描深度
 *   node tools/js/timestamp_analyzer.js --max-depth 3
 * 
 *   # 输出 JSON 格式
 *   node tools/js/timestamp_analyzer.js --format json
 * 
 * 参数说明:
 *   --path PATH            要分析的目录路径 (默认: 当前目录)
 *   --ext EXTENSION        仅分析指定扩展名的文件 (例如: .md, .txt)
 *   --max-depth DEPTH      最大扫描深度 (默认: 无限制)
 *   --format FORMAT        输出格式: text, json (默认: text)
 *   --threshold-days DAYS  文档过期阈值天数 (默认: 90 天)
 *   --include-hidden       包含隐藏文件和目录
 *   --exclude PATTERN      排除匹配模式的文件 (可多次使用，逗号分隔)
 * 
 * 版本信息:
 *   版本: 1.1.0
 *   更新日期: 2026-04-22
 */

const fs = require('fs');
const path = require('path');

function matchGlob(str, pattern) {
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    return new RegExp(`^${regexStr}$`).test(str);
}

function collectFiles(basePath, ext, maxDepth, includeHidden, excludePatterns) {
    const files = [];
    
    function walk(currentPath, depth) {
        if (maxDepth !== undefined && depth > maxDepth) return;
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) { return; }
        
        for (const entry of entries) {
            if (!includeHidden && entry.startsWith('.')) continue;
            
            const fullPath = path.join(currentPath, entry);
            const relPath = path.relative(basePath, fullPath).replace(/\\/g, '/');
            
            if (excludePatterns.some(p => relPath.includes(p) || matchGlob(entry, p))) continue;
            
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                walk(fullPath, depth + 1);
            } else {
                if (!ext || entry.endsWith(ext)) {
                    files.push({
                        path: relPath,
                        fullPath: fullPath,
                        mtime: stat.mtime,
                        size: stat.size
                    });
                }
            }
        }
    }
    
    walk(basePath, 0);
    return files;
}

function analyzeTimestamps(files) {
    if (files.length === 0) {
        return {
            total_files: 0,
            total_size_bytes: 0,
            oldest_file: null,
            newest_file: null,
            average_age_days: 0,
            files_by_age: []
        };
    }
    
    const now = new Date();
    let totalSize = 0;
    const fileData = files.map(file => {
        const ageDays = Math.floor((now - file.mtime) / (1000 * 60 * 60 * 24));
        totalSize += file.size;
        return {
            path: file.path,
            mtime: file.mtime.toISOString(),
            age_days: ageDays,
            size_bytes: file.size
        };
    });
    
    fileData.sort((a, b) => b.age_days - a.age_days); // Oldest first
    
    const oldest = fileData[0];
    const newest = fileData[fileData.length - 1];
    const avgAge = fileData.reduce((acc, f) => acc + f.age_days, 0) / fileData.length;
    
    return {
        total_files: fileData.length,
        total_size_bytes: totalSize,
        oldest_file: oldest,
        newest_file: newest,
        average_age_days: avgAge,
        files_by_age: fileData
    };
}

function formatTextOutput(stats, expiredDocs, recentlyModified, thresholdDays, scanPath) {
    let output = "";
    const line = "=".repeat(60);
    const subLine = "-".repeat(60);
    
    output += line + "\n时间戳分析报告\n" + line + "\n\n";
    output += `扫描路径: ${scanPath}\n`;
    output += `扫描时间: ${new Date().toISOString()}\n\n`;
    
    output += subLine + "\n统计概览\n" + subLine + "\n";
    output += `总文件数: ${stats.total_files}\n`;
    output += `总大小: ${(stats.total_size_bytes / 1024).toFixed(2)} KB\n\n`;
    
    if (stats.oldest_file) {
        output += subLine + "\n时间戳统计\n" + subLine + "\n";
        output += `最旧文件: ${stats.oldest_file.path}\n`;
        output += `  修改时间: ${stats.oldest_file.mtime}\n`;
        output += `  年龄: ${stats.oldest_file.age_days} 天\n\n`;
        
        output += `最新文件: ${stats.newest_file.path}\n`;
        output += `  修改时间: ${stats.newest_file.mtime}\n`;
        output += `  年龄: ${stats.newest_file.age_days} 天\n\n`;
        
        output += `平均年龄: ${stats.average_age_days.toFixed(1)} 天\n\n`;
    }
    
    if (expiredDocs.length > 0) {
        output += subLine + `\n⚠️ 过期文档 (超过 ${thresholdDays} 天未更新)\n` + subLine + "\n";
        expiredDocs.slice(0, 10).forEach(doc => {
            output += `  ${doc.path} (${doc.age_days} 天)\n`;
        });
        if (expiredDocs.length > 10) {
            output += `  ... 还有 ${expiredDocs.length - 10} 个文件\n`;
        }
        output += "\n";
    }
    
    if (recentlyModified.length > 0) {
        output += subLine + "\n📄 最近修改的文件 (Top 10)\n" + subLine + "\n";
        recentlyModified.forEach(doc => {
            output += `  ${doc.mtime.substring(0, 10)} - ${doc.path}\n`;
        });
        output += "\n";
    }
    
    output += line + "\n报告生成完成\n" + line + "\n";
    return output;
}

function main() {
    const startTime = Date.now();
    const args = process.argv.slice(2);
    const options = {
        path: '.',
        ext: null,
        maxDepth: undefined,
        format: 'text',
        thresholdDays: 90,
        includeHidden: false,
        exclude: []
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--path': options.path = args[++i]; break;
            case '--ext': options.ext = args[++i]; break;
            case '--max-depth': options.maxDepth = parseInt(args[++i]); break;
            case '--format': options.format = args[++i]; break;
            case '--threshold-days': options.thresholdDays = parseInt(args[++i]); break;
            case '--include-hidden': options.includeHidden = true; break;
            case '--exclude': options.exclude = options.exclude.concat(args[++i].split(',')); break;
        }
    }
    
    const absPath = path.resolve(options.path);
    if (!fs.existsSync(absPath)) {
        console.error(`❌ 错误: 路径不存在: ${options.path}`);
        process.exit(1);
    }
    
    const files = collectFiles(absPath, options.ext, options.maxDepth, options.includeHidden, options.exclude);
    const stats = analyzeTimestamps(files);
    const expiredDocs = stats.files_by_age.filter(f => f.age_days > options.thresholdDays);
    const recentlyModified = [...stats.files_by_age].sort((a, b) => new Date(b.mtime) - new Date(a.mtime)).slice(0, 10);
    
    if (options.format === 'json') {
        const output = {
            scan_info: {
                path: absPath,
                total_files: files.length,
                scan_time: new Date().toISOString()
            },
            stats: stats,
            expired_docs: expiredDocs,
            recently_modified: recentlyModified,
            threshold_days: options.thresholdDays,
            metadata: {
                elapsed_seconds: parseFloat(((Date.now() - startTime) / 1000).toFixed(2)),
                timeout_threshold: 10,
                version: "1.1.0"
            }
        };
        console.log(JSON.stringify(output, null, 2));
    } else {
        console.log(formatTextOutput(stats, expiredDocs, recentlyModified, options.thresholdDays, absPath));
    }
    
    if (expiredDocs.length > 0) process.exit(2);
    else process.exit(0);
}

main();
