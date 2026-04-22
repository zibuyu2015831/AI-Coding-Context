/**
 * 内容搜索工具 - 在项目文件中搜索文本（类似 grep）
 * 
 * 功能说明：
 * - 优先使用 ripgrep (rg) 进行高速搜索
 * - 当 ripgrep 不可用时，自动降级到纯 JavaScript 实现
 * - 支持正则表达式和固定字符串搜索
 * - 支持文件包含/排除模式
 * - 自动处理超时和编码问题
 * 
 * 使用方法：
 *   node tools/js/content_searcher.js --query "搜索内容" [选项]
 * 
 * 参数说明：
 *   --query QUERY            要搜索的文本（必需）
 *   --path PATH              搜索根目录（默认：当前目录）
 *   --include PATTERNS       逗号分隔的包含模式（如："*.js,*.ts"）
 *   --exclude PATTERNS       逗号分隔的排除模式（如："node_modules,dist"）
 *   --regex                  将查询视为正则表达式（默认：否）
 *   --timeout SECONDS        搜索超时时间（默认：5秒）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "matches": [
 *         {"file": "文件路径", "line": 行号, "content": "匹配内容"},
 *         ...
 *       ]
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   // 搜索所有 TODO 注释
 *   node tools/js/content_searcher.js --query "TODO" --path ./src
 * 
 *   // 仅在 JavaScript 文件中搜索
 *   node tools/js/content_searcher.js --query "import" --include "*.js"
 * 
 *   // 使用正则表达式搜索
 *   node tools/js/content_searcher.js --query "function\s+\w+" --regex
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2025-12-02
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function runRipgrep(query, rootPath, includes, excludes, isRegex, timeout) {
    const args = ["--json", "--line-number", "--heading", "--color=never"];
    
    if (!isRegex) {
        args.push("--fixed-strings");
    }
    
    if (includes) {
        includes.forEach(inc => args.push("--glob", inc));
    }
    
    if (excludes) {
        excludes.forEach(exc => args.push("--glob", `!${exc}`));
    }
    
    args.push(query);
    args.push(rootPath);
    
    try {
        const result = spawnSync("rg", args, { 
            timeout: timeout * 1000, 
            encoding: 'utf-8',
            maxBuffer: 1024 * 1024 * 10 // 10MB buffer
        });
        
        if (result.error) {
            if (result.error.code === 'ENOENT') return null; // rg not found
            if (result.error.code === 'ETIMEDOUT') return { error: "Search timed out (rg)" };
            return { error: result.error.message };
        }
        
        const matches = [];
        if (result.status === 0) {
            const lines = result.stdout.split('\n');
            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    if (data.type === "match") {
                        matches.push({
                            file: data.data.path.text,
                            line: data.data.line_number,
                            content: data.data.lines.text.trim()
                        });
                    }
                } catch (e) { continue; }
            }
        }
        return matches;
    } catch (e) {
        return { error: e.message };
    }
}

// Simple glob matcher
function matchGlob(str, pattern) {
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    return new RegExp(`^${regexStr}$`).test(str);
}

function fallbackSearch(query, rootPath, includes, excludes, isRegex, timeout) {
    const matches = [];
    const startTime = Date.now();
    const timeoutMs = timeout * 1000;
    
    let regex;
    try {
        regex = isRegex ? new RegExp(query) : null;
    } catch (e) {
        return { error: `Invalid regex: ${e.message}` };
    }
    
    function walk(currentPath) {
        if (Date.now() - startTime > timeoutMs) throw new Error("Search timed out (fallback)");
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) { return; }
        
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry);
            const relPath = path.relative(rootPath, fullPath);
            const name = entry;
            
            // Handle excludes
            if (excludes && excludes.length > 0 && excludes.some(exc => matchGlob(name, exc) || (relPath && matchGlob(relPath, exc)))) continue;
            
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                walk(fullPath);
            } else {
                // Handle includes
                if (includes && includes.length > 0 && !includes.some(inc => matchGlob(name, inc) || (relPath && matchGlob(relPath, inc)))) continue;
                
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const lines = content.split(/\r\n|\r|\n/);
                    
                    lines.forEach((line, index) => {
                        let found = false;
                        if (isRegex) {
                            if (regex.test(line)) found = true;
                        } else {
                            if (line.includes(query)) found = true;
                        }
                        
                        if (found) {
                            matches.push({
                                file: fullPath,
                                line: index + 1,
                                content: line.trim()
                            });
                        }
                    });
                } catch (e) { continue; }
            }
        }
    }
    
    try {
        walk(rootPath);
        return matches;
    } catch (e) {
        if (e.message === "Search timed out (fallback)") return { error: e.message };
        return { error: e.message };
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        query: '',
        path: '.',
        include: [],
        exclude: [],
        regex: false,
        timeout: 5
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--query': options.query = args[++i]; break;
            case '--path': options.path = args[++i]; break;
            case '--include': options.include = args[++i].split(','); break;
            case '--exclude': options.exclude = args[++i].split(','); break;
            case '--regex': options.regex = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    if (!options.query) {
        console.error("Error: --query is required");
        process.exit(1);
    }
    
    let matches = runRipgrep(
        options.query, 
        options.path, 
        options.include, 
        options.exclude, 
        options.regex, 
        options.timeout
    );
    
    if (matches === null) {
        matches = fallbackSearch(
            options.query, 
            options.path, 
            options.include, 
            options.exclude, 
            options.regex, 
            options.timeout
        );
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    
    if (matches.error) {
        matches.metadata = {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        };
        console.log(JSON.stringify(matches, null, 2));
    } else {
        const result = {
            data: { matches: matches },
            metadata: {
                elapsed_seconds: parseFloat(elapsedTime),
                timeout_threshold: 10,
                version: "1.1.0"
            }
        };
        console.log(JSON.stringify(result, null, 2));
    }
}

main();
