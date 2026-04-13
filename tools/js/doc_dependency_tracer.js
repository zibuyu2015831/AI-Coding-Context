/**
 * 文档依赖追踪器 - 基于 dependencies 和 keywords 字段检测关联文档
 *
 * 功能说明:
 *     - 基于文档的 dependencies 字段检测直接关联文档
 *     - 基于文档的 keywords 字段检测语义关联文档
 *     - 支持双向关联检测（正向依赖和反向依赖）
 *     - 提供分级关联检测策略（dependencies > keywords > 全文搜索）
 *     - 输出 JSON 格式的关联文档信息
 *
 * 使用方法:
 *     // 检测单个文档的关联文档
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md"
 *
 *     // 指定文档目录
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/
 *
 *     // 递归扫描
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/ --recursive
 *
 *     // 使用 dependencies 字段检测
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --strategy dependencies
 *
 *     // 使用 keywords 字段检测
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --strategy keywords
 *
 *     // 使用全文搜索兜底
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --strategy fulltext
 *
 *     // 输出详细信息
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --verbose
 *
 * 参数说明:
 *     --doc PATH                要检测的目标文档路径
 *     --doc-dir PATH            文档目录，默认为 dev_docs/
 *     --recursive               递归扫描文档目录
 *     --strategy STRATEGY       检测策略: dependencies (默认), keywords, fulltext
 *     --min-overlap NUM         关键词最小重叠度，默认 1
 *     --verbose                 输出详细信息
 *     --timeout SECONDS         超时时间，默认 10 秒
 *
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-13
 *     Purpose: Support 011-Document Error Fix Workflow
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
 * 从文档中提取 dependencies 字段
 */
function extractDependencies(docPath) {
    try {
        const content = fs.readFileSync(docPath, 'utf-8');
        const summary = extractFrontmatter(content);

        if (!summary || !summary.dependencies) {
            return [];
        }

        const dependencies = summary.dependencies;
        if (Array.isArray(dependencies)) {
            return dependencies.filter(d => d && d !== '无');
        } else if (typeof dependencies === 'string' && dependencies !== '无') {
            if (dependencies.includes('|')) {
                return dependencies.split('|').map(d => d.trim()).filter(d => d);
            }
            return [dependencies];
        }

        return [];

    } catch (e) {
        return [];
    }
}

/**
 * 从文档中提取 keywords 字段
 */
function extractKeywords(docPath) {
    try {
        const content = fs.readFileSync(docPath, 'utf-8');
        const summary = extractFrontmatter(content);

        if (!summary || !summary.keywords) {
            return [];
        }

        const keywords = summary.keywords;
        if (Array.isArray(keywords)) {
            return keywords.filter(k => k && k !== '无');
        } else if (typeof keywords === 'string' && keywords !== '无') {
            if (keywords.includes('|')) {
                return keywords.split('|').map(k => k.trim()).filter(k => k);
            }
            return [keywords];
        }

        return [];

    } catch (e) {
        return [];
    }
}

/**
 * 基于 dependencies 字段检测关联文档
 */
function detectRelatedByDependencies(targetDoc, allDocs) {
    const directRelated = [];
    const reverseRelated = [];

    // 提取目标文档的 dependencies 字段
    const targetDeps = extractDependencies(targetDoc);

    // 检测直接关联文档（目标文档依赖的文档）
    for (const doc of allDocs) {
        if (doc === targetDoc) {
            continue;
        }

        const docName = path.basename(doc);
        for (const dep of targetDeps) {
            if (dep.includes(doc) || docName.includes(dep)) {
                directRelated.push({
                    file: doc,
                    type: "direct",
                    reason: "dependencies 字段中引用"
                });
                break;
            }
        }
    }

    // 检测反向关联文档（依赖目标文档的文档）
    for (const doc of allDocs) {
        if (doc === targetDoc) {
            continue;
        }

        const docDeps = extractDependencies(doc);
        const targetName = path.basename(targetDoc);

        for (const dep of docDeps) {
            if (dep.includes(targetDoc) || dep.includes(targetName)) {
                reverseRelated.push({
                    file: doc,
                    type: "reverse",
                    reason: "被该文档的 dependencies 字段引用"
                });
                break;
            }
        }
    }

    return { direct: directRelated, reverse: reverseRelated };
}

/**
 * 基于 keywords 字段检测语义关联文档
 */
function detectRelatedByKeywords(targetDoc, allDocs, minOverlap = 1) {
    const semanticRelated = [];

    // 提取目标文档的 keywords 字段
    const targetKeywords = new Set(extractKeywords(targetDoc));

    for (const doc of allDocs) {
        if (doc === targetDoc) {
            continue;
        }

        // 提取其他文档的 keywords 字段
        const docKeywords = new Set(extractKeywords(doc));

        // 计算关键词重叠度
        const overlap = [...targetKeywords].filter(k => docKeywords.has(k));

        if (overlap.length >= minOverlap) {
            semanticRelated.push({
                file: doc,
                type: "semantic",
                reason: `关键词重叠度: ${overlap.length} (${overlap.join(', ')})`,
                overlapKeywords: overlap
            });
        }
    }

    // 按重叠度降序排序
    semanticRelated.sort((a, b) => b.overlapKeywords.length - a.overlapKeywords.length);

    return semanticRelated;
}

/**
 * 使用全文搜索检测关联文档（兜底方案）
 */
function detectRelatedByFulltext(targetDoc, allDocs) {
    const fulltextRelated = [];

    try {
        const targetContent = fs.readFileSync(targetDoc, 'utf-8').toLowerCase();
        const targetWords = new Set(targetContent.match(/\b\w{3,}\b/g) || []);

        for (const doc of allDocs) {
            if (doc === targetDoc) {
                continue;
            }

            try {
                const docContent = fs.readFileSync(doc, 'utf-8').toLowerCase();
                const docWords = new Set(docContent.match(/\b\w{3,}\b/g) || []);

                // 计算词汇重叠度
                const overlap = [...targetWords].filter(word => docWords.has(word));

                if (overlap.length > 3) {
                    fulltextRelated.push({
                        file: doc,
                        type: "fulltext",
                        reason: `词汇重叠度: ${overlap.length}`
                    });
                }

            } catch (e) {
                continue;
            }
        }

    } catch (e) {
        // 忽略错误
    }

    return fulltextRelated;
}

/**
 * 追踪文档的关联文档
 */
function traceDependencies(targetDoc, docDir, recursive = false, strategy = "dependencies", minOverlap = 1) {
    // 查找所有文档
    const allDocs = findMarkdownFiles(docDir, recursive);

    if (!allDocs.includes(targetDoc)) {
        allDocs.push(targetDoc);
    }

    const relatedDocs = {
        direct: [],
        reverse: [],
        semantic: [],
        fulltext: []
    };

    if (strategy === "dependencies" || strategy === "all") {
        const { direct, reverse } = detectRelatedByDependencies(targetDoc, allDocs);
        relatedDocs.direct = direct;
        relatedDocs.reverse = reverse;
    }

    if (strategy === "keywords" || strategy === "all") {
        const semantic = detectRelatedByKeywords(targetDoc, allDocs, minOverlap);
        relatedDocs.semantic = semantic;
    }

    if (strategy === "fulltext" || strategy === "all") {
        const fulltext = detectRelatedByFulltext(targetDoc, allDocs);
        relatedDocs.fulltext = fulltext;
    }

    // 去重
    const seen = new Set();
    for (const key in relatedDocs) {
        const unique = [];
        for (const doc of relatedDocs[key]) {
            if (!seen.has(doc.file)) {
                seen.add(doc.file);
                unique.push(doc);
            }
        }
        relatedDocs[key] = unique;
    }

    const totalRelated = Object.values(relatedDocs).reduce((sum, docs) => sum + docs.length, 0);

    return {
        targetDoc: targetDoc,
        strategy: strategy,
        relatedDocs: relatedDocs,
        totalRelated: totalRelated,
        totalDocsScanned: allDocs.length
    };
}

function printHelp() {
    console.log(`
文档依赖追踪器 - 基于 dependencies 和 keywords 字段检测关联文档

使用方法:
    node tools/js/doc_dependency_tracer.js --doc <文档路径> [选项]

选项:
    --doc PATH               要检测的目标文档路径（必需）
    --doc-dir PATH           文档目录，默认: dev_docs
    --recursive              递归扫描文档目录
    --strategy STRATEGY      检测策略: dependencies (默认), keywords, fulltext, all
    --min-overlap NUM        关键词最小重叠度，默认 1
    --verbose                输出详细信息
    --timeout SECONDS        超时时间（秒），默认10秒
    --help, -h               显示此帮助信息

示例:
    node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md"
    node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --strategy all
    node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md" --min-overlap 2 --verbose
`);
}

function main() {
    const startTime = Date.now();

    const args = process.argv.slice(2);
    const options = {
        doc: null,
        docDir: DEFAULT_DOC_DIR,
        recursive: false,
        strategy: "dependencies",
        minOverlap: 1,
        verbose: false,
        timeout: DEFAULT_TIMEOUT,
        help: false
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--help':
            case '-h':
                options.help = true;
                i++;
                break;
            case '--doc': options.doc = args[++i]; break;
            case '--doc-dir': options.docDir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--strategy': options.strategy = args[++i]; break;
            case '--min-overlap': options.minOverlap = parseInt(args[++i]); break;
            case '--verbose': options.verbose = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }

    // 参数验证
    if (options.help) {
        printHelp();
        process.exit(0);
    }

    if (!options.doc) {
        console.error("Error: 必须指定 --doc 参数");
        process.exit(1);
    }

    if (!fs.existsSync(options.doc) || !fs.statSync(options.doc).isFile()) {
        console.error(`Error: Target document not found: ${options.doc}`);
        process.exit(1);
    }

    if (!options.doc.endsWith('.md')) {
        console.error("Error: Target document must be a Markdown file (.md)");
        process.exit(1);
    }

    if (!fs.existsSync(options.docDir) || !fs.statSync(options.docDir).isDirectory()) {
        console.error(`Error: Document directory not found: ${options.docDir}`);
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
        const tracingResult = traceDependencies(
            options.doc,
            options.docDir,
            options.recursive,
            options.strategy,
            options.minOverlap
        );
        result.data = tracingResult;

        if (options.verbose) {
            console.error(`Scanned ${tracingResult.totalDocsScanned} documents, found ${tracingResult.totalRelated} related docs`);
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
