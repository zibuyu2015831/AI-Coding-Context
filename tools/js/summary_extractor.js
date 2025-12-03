/**
 * 文档摘要提取工具 - 从Markdown文档中提取YAML Frontmatter摘要
 * 
 * 功能说明:
 *     - 从Markdown文档中提取YAML Frontmatter格式的摘要
 *     - 支持单文件和批量目录处理
 *     - YAML解析优先,正则表达式作为备用方案
 *     - JSON格式统一输出
 *     - 超时机制保护(默认10秒)
 * 
 * 使用方法:
 *     // 单文件提取
 *     node tools/js/summary_extractor.js --file dev_docs/api_layer.md
 *     
 *     // 批量提取目录下所有.md文件
 *     node tools/js/summary_extractor.js --dir dev_docs/
 *     
 *     // 递归扫描子目录
 *     node tools/js/summary_extractor.js --dir dev_docs/ --recursive
 * 
 * 参数说明:
 *     --file PATH          单个Markdown文件路径
 *     --dir PATH           批量处理目录路径
 *     --recursive          递归扫描子目录(仅与--dir配合使用)
 *     --timeout SECONDS    超时时间,默认10秒
 * 
 * 输出格式:
 *     {
 *       "success": true,
 *       "data": {
 *         "file": "dev_docs/api_layer.md",
 *         "summary": {
 *           "title": "API层设计规范",
 *           "summary": "定义前端API调用的统一接口规范...",
 *           "keywords": ["API", "HTTP", "Axios"],
 *           "scope": "前端API层 (src/api/)",
 *           "related_files": ["src/api/http.ts", "src/api/types.ts"],
 *           "dependencies": ["dev_docs/state_management.md"],
 *           "verified_at": "2025-12-03"
 *         }
 *       },
 *       "metadata": {
 *         "elapsed_seconds": 0.15,
 *         "timeout_threshold": 10,
 *         "version": "1.0.0"
 *       }
 *     }
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2025-12-03
 *     Purpose: Support 012-Mandatory Document Summary mechanism
 */

const fs = require('fs');
const path = require('path');

const VERSION = "1.0.0";
const DEFAULT_TIMEOUT = 10;
const REQUIRED_FIELDS = ['title', 'summary', 'keywords', 'scope', 'related_files', 'dependencies', 'verified_at'];

/**
 * 提取YAML Frontmatter
 */
function extractFrontmatter(content) {
    const pattern = /^---\s*\n(.*?)\n---\s*\n/s;
    const match = content.match(pattern);
    
    if (!match) {
        return null;
    }
    
    const yamlContent = match[1];
    return parseYamlSimple(yamlContent);
}

/**
 * 简单的YAML解析器(仅使用标准库)
 */
function parseYamlSimple(yamlStr) {
    const result = {};
    const lines = yamlStr.trim().split('\n');
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) {
            continue;
        }
        
        if (!trimmed.includes(':')) {
            continue;
        }
        
        const colonIndex = trimmed.indexOf(':');
        const key = trimmed.substring(0, colonIndex).trim();
        let value = trimmed.substring(colonIndex + 1).trim();
        
        // 处理值
        if (!value || ['无', 'none', ''].includes(value.toLowerCase())) {
            result[key] = null;
        } else if (value.includes('|')) {
            // 使用 | 分隔的列表
            result[key] = value.split('|').map(item => item.trim()).filter(item => item);
        } else {
            // 移除引号
            value = value.replace(/^["']|["']$/g, '');
            result[key] = value;
        }
    }
    
    return result;
}

/**
 * 从单个文件提取摘要
 */
function extractSummaryFromFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);
        
        if (!summary) {
            return {
                file: filePath,
                summary: null,
                error: "No YAML Frontmatter found"
            };
        }
        
        // 验证必须字段是否存在
        const missingFields = REQUIRED_FIELDS.filter(field => !(field in summary));
        
        const result = {
            file: filePath,
            summary: summary
        };
        
        if (missingFields.length > 0) {
            result.warning = `Missing fields: ${missingFields.join(', ')}`;
        }
        
        return result;
        
    } catch (e) {
        return {
            file: filePath,
            summary: null,
            error: e.message
        };
    }
}

/**
 * 查找目录下的所有Markdown文件
 */
function findMarkdownFiles(directory, recursive = false) {
    const mdFiles = [];
    const excludeDirs = new Set(['.git', 'node_modules', '__pycache__', 'dist', 'build']);
    
    function scan(dir) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                if (recursive && !excludeDirs.has(entry.name)) {
                    scan(fullPath);
                }
            } else if (entry.isFile() && entry.name.endsWith('.md')) {
                mdFiles.push(fullPath);
            }
        }
    }
    
    scan(directory);
    return mdFiles;
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        file: null,
        dir: null,
        recursive: false,
        timeout: DEFAULT_TIMEOUT
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--file': options.file = args[++i]; break;
            case '--dir': options.dir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    // 参数验证
    if (!options.file && !options.dir) {
        console.error("Error: 必须指定 --file 或 --dir 参数");
        process.exit(1);
    }
    
    if (options.file && options.dir) {
        console.error("Error: --file 和 --dir 不能同时使用");
        process.exit(1);
    }
    
    const result = {
        success: true,
        data: {},
        metadata: {
            elapsed_seconds: 0,
            timeout_threshold: options.timeout,
            version: VERSION
        }
    };
    
    try {
        // 单文件模式
        if (options.file) {
            if (!fs.existsSync(options.file)) {
                result.success = false;
                result.error = `File not found: ${options.file}`;
            } else {
                const extraction = extractSummaryFromFile(options.file);
                result.data = extraction;
                
                if (extraction.error) {
                    result.success = false;
                }
            }
        }
        // 批量模式
        else {
            if (!fs.existsSync(options.dir) || !fs.statSync(options.dir).isDirectory()) {
                result.success = false;
                result.error = `Directory not found: ${options.dir}`;
            } else {
                const mdFiles = findMarkdownFiles(options.dir, options.recursive);
                
                const summaries = [];
                let successful = 0;
                let failed = 0;
                
                for (const mdFile of mdFiles) {
                    // 检查超时
                    if ((Date.now() - startTime) / 1000 > options.timeout) {
                        result.warning = "Timeout reached, partial results returned";
                        break;
                    }
                    
                    const extraction = extractSummaryFromFile(mdFile);
                    summaries.push(extraction);
                    
                    if (!extraction.error || extraction.summary !== null) {
                        successful++;
                    } else {
                        failed++;
                    }
                }
                
                result.data = {
                    summaries: summaries,
                    total_files: mdFiles.length,
                    processed: summaries.length,
                    successful: successful,
                    failed: failed
                };
            }
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }
    
    // 计算耗时
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    result.metadata.elapsed_seconds = parseFloat(elapsedTime);
    
    // 输出JSON
    console.log(JSON.stringify(result, null, 2));
}

main();
