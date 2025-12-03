/**
 * 文档摘要索引生成器 - 生成文档摘要索引页
 * 
 * ⚠️ 状态说明:
 *     此工具暂不启用,后续根据需要决定是否使用。
 *     原因: 索引页生成可能导致冗余信息,且不确定实际使用价值。
 *     如需启用,请移除此注释并在implementation_plan中更新状态。
 * 
 * 功能说明:
 *     - 遍历所有文档
 *     - 批量提取摘要
 *     - 生成Markdown格式索引页
 *     - 支持按分类组织索引
 * 
 * 使用方法:
 *     // 生成索引页
 *     node tools/js/summary_index_generator.js --doc-dir dev_docs/ --output dev_docs/_index.md
 *     
 *     // 递归扫描
 *     node tools/js/summary_index_generator.js --doc-dir dev_docs/ --output dev_docs/_index.md --recursive
 *     
 *     // 按分类组织
 *     node tools/js/summary_index_generator.js --doc-dir dev_docs/ --output dev_docs/_index.md --group-by-dir
 * 
 * 参数说明:
 *     --doc-dir PATH      文档目录,默认dev_docs/
 *     --output PATH       输出索引文件路径
 *     --recursive         递归扫描子目录
 *     --group-by-dir      按目录分组索引
 *     --timeout SECONDS   超时时间,默认10秒
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2025-12-03
 *     Purpose: Support 012-Mandatory Document Summary mechanism
 *     Status: DISABLED - 暂不启用
 */

const fs = require('fs');
const path = require('path');

const VERSION = "1.0.0";
const DEFAULT_TIMEOUT = 10;
const DEFAULT_DOC_DIR = "dev_docs";

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
 * 简单的YAML解析器
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
        
        if (!value || ['无', 'none', ''].includes(value.toLowerCase())) {
            result[key] = null;
        } else if (value.includes('|')) {
            result[key] = value.split('|').map(item => item.trim()).filter(item => item);
        } else {
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
        
        return {
            file: filePath,
            summary: summary
        };
        
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

/**
 * 生成索引页Markdown内容
 */
function generateIndexMarkdown(summaries, groupByDir = false) {
    const lines = [];
    
    lines.push("# 文档索引");
    lines.push("");
    lines.push("> 📋 本文档由工具自动生成,包含所有文档的摘要信息");
    lines.push("");
    lines.push(`> 🕐 生成时间: ${new Date().toISOString().replace('T', ' ').substring(0, 19)}`);
    lines.push("");
    lines.push("---");
    lines.push("");
    
    if (groupByDir) {
        // 按目录分组
        const grouped = {};
        for (const item of summaries) {
            if (item.summary) {
                let dirName = path.dirname(item.file);
                if (!dirName || dirName === '.') {
                    dirName = "根目录";
                }
                if (!grouped[dirName]) {
                    grouped[dirName] = [];
                }
                grouped[dirName].push(item);
            }
        }
        
        const sortedDirs = Object.keys(grouped).sort();
        for (const dirName of sortedDirs) {
            lines.push(`## ${dirName}`);
            lines.push("");
            
            for (const item of grouped[dirName]) {
                const summary = item.summary;
                const fileName = path.basename(item.file);
                
                lines.push(`### [${summary.title || fileName}](${item.file})`);
                lines.push("");
                lines.push(`**摘要**: ${summary.summary || '无'}`);
                lines.push("");
                
                if (summary.keywords) {
                    const keywords = Array.isArray(summary.keywords) ? summary.keywords : [summary.keywords];
                    lines.push(`**关键词**: ${keywords.join(', ')}`);
                    lines.push("");
                }
                
                if (summary.scope) {
                    lines.push(`**范围**: ${summary.scope}`);
                    lines.push("");
                }
                
                lines.push("---");
                lines.push("");
            }
        }
    } else {
        // 不分组,按文件名排序
        const sortedSummaries = summaries.filter(s => s.summary).sort((a, b) => a.file.localeCompare(b.file));
        
        for (const item of sortedSummaries) {
            const summary = item.summary;
            const fileName = path.basename(item.file);
            
            lines.push(`## [${summary.title || fileName}](${item.file})`);
            lines.push("");
            lines.push(`**文件**: \`${item.file}\``);
            lines.push("");
            lines.push(`**摘要**: ${summary.summary || '无'}`);
            lines.push("");
            
            if (summary.keywords) {
                const keywords = Array.isArray(summary.keywords) ? summary.keywords : [summary.keywords];
                lines.push(`**关键词**: ${keywords.join(', ')}`);
                lines.push("");
            }
            
            if (summary.scope) {
                lines.push(`**范围**: ${summary.scope}`);
                lines.push("");
            }
            
            lines.push("---");
            lines.push("");
        }
    }
    
    return lines.join('\n');
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        docDir: DEFAULT_DOC_DIR,
        output: null,
        recursive: false,
        groupByDir: false,
        timeout: DEFAULT_TIMEOUT
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--doc-dir': options.docDir = args[++i]; break;
            case '--output': options.output = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--group-by-dir': options.groupByDir = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    if (!options.output) {
        console.error("Error: --output is required");
        process.exit(1);
    }
    
    const result = {
        success: true,
        data: {},
        metadata: {
            elapsed_seconds: 0,
            timeout_threshold: options.timeout,
            version: VERSION,
            status: "DISABLED - 此工具暂不启用"
        }
    };
    
    try {
        // 检查文档目录
        if (!fs.existsSync(options.docDir) || !fs.statSync(options.docDir).isDirectory()) {
            result.success = false;
            result.error = `Document directory not found: ${options.docDir}`;
        } else {
            // 查找所有文档
            const mdFiles = findMarkdownFiles(options.docDir, options.recursive);
            
            // 提取摘要
            const summaries = [];
            for (const mdFile of mdFiles) {
                // 检查超时
                if ((Date.now() - startTime) / 1000 > options.timeout) {
                    result.warning = "Timeout reached, partial results returned";
                    break;
                }
                
                const extraction = extractSummaryFromFile(mdFile);
                summaries.push(extraction);
            }
            
            // 生成索引
            const indexContent = generateIndexMarkdown(summaries, options.groupByDir);
            
            // 写入文件
            fs.writeFileSync(options.output, indexContent, 'utf-8');
            
            result.data = {
                output_file: options.output,
                total_files: mdFiles.length,
                processed: summaries.length,
                has_summary: summaries.filter(s => s.summary).length
            };
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
