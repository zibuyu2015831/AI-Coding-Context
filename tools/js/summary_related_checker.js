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
 *     Version: 1.1.0
 *     Created: 2025-12-03
 *     Updated: 2026-04-13
 *     Purpose: Support 012-Mandatory Document Summary mechanism
 *     Added: --dependencies and --keywords strategy support
 */

const fs = require('fs');
const path = require('path');

const VERSION = "1.1.0";
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
 * 从文档提取dependencies字段
 */
function extractDependencies(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);

        if (!summary || !summary.dependencies) {
            return null;
        }

        const dependencies = summary.dependencies;
        if (Array.isArray(dependencies)) {
            return dependencies.filter(f => f && f !== '无');
        } else if (typeof dependencies === 'string' && dependencies !== '无') {
            if (dependencies.includes('|')) {
                return dependencies.split('|').map(f => f.trim()).filter(f => f);
            }
            return [dependencies];
        }

        return null;

    } catch (e) {
        return null;
    }
}

/**
 * 从文档提取keywords字段
 */
function extractKeywords(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);

        if (!summary || !summary.keywords) {
            return null;
        }

        const keywords = summary.keywords;
        if (Array.isArray(keywords)) {
            return keywords.filter(f => f && f !== '无');
        } else if (typeof keywords === 'string' && keywords !== '无') {
            if (keywords.includes('|')) {
                return keywords.split('|').map(f => f.trim()).filter(f => f);
            }
            return [keywords];
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
function checkAffectedDocs(changedFiles, docDir, recursive = false, strategy = "related_files", minOverlap = 1) {
    // 标准化变更文件路径
    const changedFilesNormalized = changedFiles.map(f => normalizePath(f));

    // 查找所有文档
    const mdFiles = findMarkdownFiles(docDir, recursive);

    const affectedDocs = [];

    if (strategy === "related_files" || strategy === "all") {
        // 使用 related_files 字段检测（默认策略）
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
                // 检查是否已存在该文档的记录
                const existing = affectedDocs.find(d => d.file === mdFile);
                if (existing) {
                    existing.matched_files = [...new Set([...existing.matched_files, ...matchedFiles])];
                    existing.all_related_files = relatedFiles;
                } else {
                    affectedDocs.push({
                        file: mdFile,
                        matched_files: matchedFiles,
                        all_related_files: relatedFiles,
                        suggestion: "建议更新此文档,因为关联文件已变更"
                    });
                }
            }
        }
    }

    if (strategy === "dependencies" || strategy === "all") {
        // 使用 dependencies 字段检测
        for (const mdFile of mdFiles) {
            const dependencies = extractDependencies(mdFile);

            if (!dependencies) {
                continue;
            }

            for (const dep of dependencies) {
                for (const changed of changedFilesNormalized) {
                    if (dep.includes(changed) || changed.includes(dep)) {
                        // 检查是否已存在该文档的记录
                        const existing = affectedDocs.find(d => d.file === mdFile);
                        if (existing) {
                            if (!existing.dependencies) {
                                existing.dependencies = [];
                            }
                            if (!existing.dependencies.includes(dep)) {
                                existing.dependencies.push(dep);
                            }
                        } else {
                            affectedDocs.push({
                                file: mdFile,
                                matched_files: dependencies,
                                dependencies: dependencies,
                                suggestion: "建议更新此文档,因为依赖文件已变更"
                            });
                        }
                        break;
                    }
                }
            }
        }
    }

    if (strategy === "keywords" || strategy === "all") {
        // 使用 keywords 字段检测语义关联
        for (const mdFile of mdFiles) {
            const keywords = extractKeywords(mdFile);

            if (!keywords) {
                continue;
            }

            // 从变更文件名中提取词汇进行匹配
            const changeTerms = new Set();
            for (const file of changedFilesNormalized) {
                // 从路径中提取有意义的词汇
                const filename = path.basename(file);
                const name = path.parse(filename).name;
                const terms = name.split('_');
                terms.forEach(t => changeTerms.add(t));

                // 从路径中提取目录名
                const dirname = path.dirname(file);
                const dirTerms = dirname.split(path.sep);
                dirTerms.forEach(t => t && changeTerms.add(t));
            }

            // 计算关键词匹配
            const matchedKeywords = [];
            for (const keyword of keywords) {
                for (const term of changeTerms) {
                    if (term && term.length > 2 && keyword.toLowerCase().includes(term.toLowerCase())) {
                        matchedKeywords.push(keyword);
                    }
                }
            }

            if (matchedKeywords.length >= minOverlap) {
                // 检查是否已存在该文档的记录
                const existing = affectedDocs.find(d => d.file === mdFile);
                if (existing) {
                    if (!existing.keywords) {
                        existing.keywords = [];
                    }
                    for (const kw of matchedKeywords) {
                        if (!existing.keywords.includes(kw)) {
                            existing.keywords.push(kw);
                        }
                    }
                } else {
                    affectedDocs.push({
                        file: mdFile,
                        matched_keywords: matchedKeywords,
                        keywords: keywords,
                        suggestion: `建议更新此文档,因为语义关键词匹配 (${matchedKeywords.length}个匹配)`
                    });
                }
            }
        }
    }

    // 去重 - 确保同一文档不会多次添加
    const uniqueDocs = [];
    const seen = new Set();
    for (const doc of affectedDocs) {
        if (!seen.has(doc.file)) {
            seen.add(doc.file);
            uniqueDocs.push(doc);
        }
    }

    return {
        affected_docs: uniqueDocs,
        total_docs_scanned: mdFiles.length,
        total_affected: uniqueDocs.length,
        changed_files: changedFiles,
        strategy: strategy
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
        strategy: "related_files",
        minOverlap: 1,
        timeout: DEFAULT_TIMEOUT
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--changed-files': options.changedFiles = args[++i]; break;
            case '--from-stdin': options.fromStdin = true; break;
            case '--doc-dir': options.docDir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--strategy': options.strategy = args[++i]; break;
            case '--min-overlap': options.minOverlap = parseInt(args[++i]); break;
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
                const checkResult = checkAffectedDocs(
                    changedFiles,
                    options.docDir,
                    options.recursive,
                    options.strategy,
                    options.minOverlap
                );
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
