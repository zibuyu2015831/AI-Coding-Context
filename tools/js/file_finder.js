/**
 * 文件查找工具 - 根据文件名模式查找文件（类似 find）
 * 
 * 功能说明：
 * - 递归遍历目录查找匹配的文件
 * - 支持通配符模式（如 *.js, config.*.json）
 * - 可限制返回结果数量
 * - 纯 JavaScript 实现，无外部依赖
 * 
 * 使用方法：
 *   node tools/js/file_finder.js --pattern "模式" [选项]
 * 
 * 参数说明：
 *   --pattern PATTERN        文件名匹配模式（必需），支持 * 和 ? 通配符
 *   --path PATH              搜索根目录（默认：当前目录）
 *   --limit NUM              最大返回结果数（默认：无限制）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "files": ["文件路径1", "文件路径2", ...]
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   // 查找所有 Markdown 文件
 *   node tools/js/file_finder.js --pattern "*.md" --path ./docs
 * 
 *   // 查找配置文件（限制 10 个结果）
 *   node tools/js/file_finder.js --pattern "config.*" --limit 10
 * 
 *   // 查找 JavaScript 测试文件
 *   node tools/js/file_finder.js --pattern "test_*.js"
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2025-12-02
 */

const fs = require('fs');
const path = require('path');

// Simple glob matcher
function matchGlob(str, pattern) {
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    return new RegExp(`^${regexStr}$`).test(str);
}

function findFiles(rootPath, pattern, limit) {
    const matches = [];
    
    function walk(currentPath) {
        if (limit && matches.length >= limit) return;
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) { return; }
        
        for (const entry of entries) {
            if (limit && matches.length >= limit) return;
            
            const fullPath = path.join(currentPath, entry);
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                walk(fullPath);
            } else {
                if (matchGlob(entry, pattern)) {
                    matches.push(fullPath);
                }
            }
        }
    }
    
    walk(rootPath);
    return matches;
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        pattern: '',
        path: '.',
        limit: undefined
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--pattern': options.pattern = args[++i]; break;
            case '--path': options.path = args[++i]; break;
            case '--limit': options.limit = parseInt(args[++i]); break;
        }
    }
    
    if (!options.pattern) {
        console.error("Error: --pattern is required");
        process.exit(1);
    }
    
    const files = findFiles(options.path, options.pattern, options.limit);
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    const result = {
        data: { files: files },
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        }
    };
    console.log(JSON.stringify(result, null, 2));
}

main();
