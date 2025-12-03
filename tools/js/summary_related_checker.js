/**
 * 文档关联检查工具 - 检测哪些文档的related_files包含已变更的代码
 * 
 * 功能说明:
 *     - 提取所有文档的related_files字段
 *     - 对比代码变更文件列表
 *     - 输出受影响的文档列表
 *     - 支持从stdin读取(配合git_diff_analyzer)
 *     - 提供更新建议
 * 
 * 使用方法:
 *     // 指定变更文件列表
 *     node tools/js/summary_related_checker.js --changed-files "src/api/user.ts,src/api/post.ts"
 *     
 *     // 从stdin读取(配合git_diff_analyzer)
 *     node tools/js/git_diff_analyzer.js --since "7 days ago" | node tools/js/summary_related_checker.js --from-stdin
 *     
 *     // 指定文档目录
 *     node tools/js/summary_related_checker.js --changed-files "src/api/user.ts" --doc-dir dev_docs/
 *     
 *     // 递归扫描
 *     node tools/js/summary_related_checker.js --changed-files "src/api/user.ts" --doc-dir dev_docs/ --recursive
 * 
 * 参数说明:
 *     --changed-files FILES    逗号分隔的变更文件列表
 *     --from-stdin             从stdin读取变更文件(JSON格式,来自git_diff_analyzer)
 *     --doc-dir PATH           文档目录,默认为dev_docs/
 *     --recursive              递归扫描文档目录
 *     --timeout SECONDS        超时时间,默认10秒
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
 * 从文档提取related_files
 */
function extractRelatedFiles(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);
        
        if (!summary || !summary.related_files) {
            return null;
        }
        
        const related = summary.related_files;
        if (Array.isArray(related)) {
            // 过滤掉'无'等占位符
            return related.filter(f => f && f !== '无');
        } else if (typeof related === 'string' && related !== '无') {
            return [related];
        }
        
        return null;
        
    } catch (e) {
        return null;
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
 * 标准化路径用于比较
 */
function normalizePath(pathStr) {
    return path.normalize(pathStr).replace(/\\/g, '/');
}

/**
 * 检查哪些文档受变更文件影响
 */
function checkAffectedDocs(changedFiles, docDir, recursive = false) {
    // 标准化变更文件路径
    const changedFilesNormalized = changedFiles.map(f => normalizePath(f));
    
    // 查找所有文档
    const mdFiles = findMarkdownFiles(docDir, recursive);
    
    const affectedDocs = [];
    
    for (const mdFile of mdFiles) {
        const relatedFiles = extractRelatedFiles(mdFile);
        
        if (!relatedFiles) {
            continue;
        }
        
        // 检查是否有匹配的文件
        const matchedFiles = [];
        for (const related of relatedFiles) {
            const relatedNormalized = normalizePath(related);
            for (const changed of changedFilesNormalized) {
                // 支持部分路径匹配
                if (relatedNormalized.includes(changed) || changed.includes(relatedNormalized)) {
                    matchedFiles.push(related);
                    break;
                }
            }
        }
        
        if (matchedFiles.length > 0) {
            affectedDocs.push({
                file: mdFile,
                matched_files: matchedFiles,
                all_related_files: relatedFiles,
                suggestion: "建议更新此文档,因为关联文件已变更"
            });
        }
    }
    
    return {
        affected_docs: affectedDocs,
        total_docs_scanned: mdFiles.length,
        total_affected: affectedDocs.length,
        changed_files: changedFiles
    };
}

/**
 * 解析git_diff_analyzer的JSON输出
 */
function parseGitDiffOutput(jsonStr) {
    try {
        const data = JSON.parse(jsonStr);
        
        if (!data.success) {
            return null;
        }
        
        // 提取文件列表
        let files = [];
        if (data.data && data.data.files) {
            files = data.data.files;
        } else if (data.data && data.data.changed_files) {
            files = data.data.changed_files;
        }
        
        return files;
        
    } catch (e) {
        return null;
    }
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        changedFiles: null,
        fromStdin: false,
        docDir: DEFAULT_DOC_DIR,
        recursive: false,
        timeout: DEFAULT_TIMEOUT
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--changed-files': options.changedFiles = args[++i]; break;
            case '--from-stdin': options.fromStdin = true; break;
            case '--doc-dir': options.docDir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    // 参数验证
    if (!options.changedFiles && !options.fromStdin) {
        console.error("Error: 必须指定 --changed-files 或 --from-stdin");
        process.exit(1);
    }
    
    if (options.changedFiles && options.fromStdin) {
        console.error("Error: --changed-files 和 --from-stdin 不能同时使用");
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
        // 获取变更文件列表
        let changedFiles = [];
        
        if (options.fromStdin) {
            // 从stdin读取
            let stdinContent = '';
            const stdin = process.stdin;
            stdin.setEncoding('utf-8');
            
            // 同步读取stdin (需要特殊处理)
            // Node.js streams are async by default, but for this tool we can use sync methods
            try {
                stdinContent = fs.readFileSync(0, 'utf-8'); // 0 is stdin file descriptor
            } catch (e) {
                result.success = false;
                result.error = "Failed to read from stdin";
            }
            
            if (stdinContent) {
                const parsedFiles = parseGitDiffOutput(stdinContent);
                
                if (parsedFiles === null) {
                    result.success = false;
                    result.error = "Failed to parse stdin input (expected JSON from git_diff_analyzer)";
                } else {
                    changedFiles = parsedFiles;
                }
            }
        } else {
            // 从参数读取
            changedFiles = options.changedFiles.split(',').map(f => f.trim());
        }
        
        if (changedFiles.length === 0 && result.success) {
            result.success = false;
            result.error = "No changed files provided";
        } else if (result.success) {
            // 检查文档目录是否存在
            if (!fs.existsSync(options.docDir) || !fs.statSync(options.docDir).isDirectory()) {
                result.success = false;
                result.error = `Document directory not found: ${options.docDir}`;
            } else {
                // 执行检查
                const checkResult = checkAffectedDocs(changedFiles, options.docDir, options.recursive);
                result.data = checkResult;
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
