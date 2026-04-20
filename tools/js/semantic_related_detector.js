/**
 * 语义关联检测器 - 基于 keywords 字段检测语义关联文档
 *
 * 功能说明:
 *     - 基于文档的 keywords 字段进行语义关联检测
 *     - 支持关键词重叠度计算
 *     - 提供分级语义关联检测
 *     - 输出详细的语义关联信息
 *     - 与现有的文档处理工具集成
 *
 * 使用方法:
 *     // 检测单个文档的语义关联
 *     node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md"
 *
 *     // 检测语义关联（指定文档目录）
 *     node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/
 *
 *     // 递归扫描文档目录
 *     node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/ --recursive
 *
 *     // 调整最小重叠度（默认 1）
 *     node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --min-overlap 2
 *
 *     // 输出详细信息
 *     node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --verbose
 *
 *     // 批量检测多个文档
 *     node tools/js/semantic_related_detector.js --batch --doc-list "dev_docs/api_layer.md,dev_docs/state_management.md"
 *
 * 参数说明:
 *     --doc PATH               目标文档路径
 *     --doc-dir PATH           文档目录，默认 dev_docs/
 *     --recursive              递归扫描文档目录
 *     --min-overlap NUM        关键词最小重叠度，默认 1
 *     --batch                  批量检测模式
 *     --doc-list DOCS          逗号分隔的文档列表（批量模式）
 *     --verbose                输出详细信息
 *     --timeout SECONDS        超时时间，默认 10 秒
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

function extractFrontmatter(content) {
    /**
     * 提取YAML Frontmatter
     */
    const pattern = /^---\s*\n(.*?)\n---\s*\n/s;
    const match = content.match(pattern);

    if (!match) {
        return null;
    }

    const yamlContent = match[1];
    return parseYamlSimple(yamlContent);
}

function parseYamlSimple(yamlStr) {
    /**
     * 简单的YAML解析器
     */
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

function findMarkdownFiles(directory, recursive = false) {
    /**
     * 查找目录下的所有Markdown文件 (原生实现，零依赖)
     */
    const results = [];
    const ignoreDirs = ['.git', 'node_modules', '__pycache__', 'dist', 'build'];

    function walk(dir) {
        try {
            if (!fs.existsSync(dir)) return;
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const fullPath = path.join(dir, file);
                
                // 检查是否在忽略列表中
                if (ignoreDirs.some(ignore => file === ignore || fullPath.includes(path.sep + ignore + path.sep))) {
                    continue;
                }

                const stat = fs.statSync(fullPath);
                if (stat.isDirectory() && recursive) {
                    walk(fullPath);
                } else if (stat.isFile() && file.endsWith('.md')) {
                    results.push(fullPath);
                }
            }
        } catch (e) {
            // 忽略读取错误
        }
    }

    walk(directory);
    return results;
}

function extractKeywords(docPath) {
    /**
     * 从文档中提取 keywords 字段
     */
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

function calculateSimilarity(targetKeywords, docKeywords) {
    /**
     * 计算语义相似度分数
     */
    const targetSet = new Set(targetKeywords);
    const docSet = new Set(docKeywords);
    const overlap = new Set([...targetSet].filter(x => docSet.has(x)));

    // 使用 Jaccard 相似度
    if (targetKeywords.length === 0 || docKeywords.length === 0) {
        return 0.0;
    }

    const union = new Set([...targetSet, ...docSet]);
    const jaccardSimilarity = overlap.size / union.size;
    return jaccardSimilarity;
}

function detectSemanticRelated(targetDoc, docDir, recursive = false, minOverlap = 1) {
    /**
     * 检测语义关联文档
     *
     * Args:
     *     targetDoc: 目标文档
     *     docDir: 文档目录
     *     recursive: 是否递归扫描
     *     minOverlap: 关键词最小重叠度
     *
     * Returns:
     *     dict: 语义关联检测结果
     */
    const targetKeywords = extractKeywords(targetDoc);

    if (!targetKeywords.length) {
        return {
            success: true,
            targetDoc: targetDoc,
            semanticRelated: [],
            totalDocsScanned: 0,
            totalRelated: 0,
            warning: "目标文档没有关键词字段"
        };
    }

    const mdFiles = findMarkdownFiles(docDir, recursive);

    const semanticRelated = [];
    let totalDocsScanned = 0;

    for (const doc of mdFiles) {
        if (doc === targetDoc) {
            continue;
        }

        totalDocsScanned++;

        const docKeywords = extractKeywords(doc);
        if (!docKeywords.length) {
            continue;
        }

        // 计算关键词重叠
        const targetSet = new Set(targetKeywords);
        const docSet = new Set(docKeywords);
        const overlap = new Set([...targetSet].filter(x => docSet.has(x)));

        if (overlap.size >= minOverlap) {
            const similarity = calculateSimilarity(targetKeywords, docKeywords);

            semanticRelated.push({
                file: doc,
                overlapKeywords: Array.from(overlap),
                overlapCount: overlap.size,
                targetKeywords: targetKeywords,
                docKeywords: docKeywords,
                similarityScore: parseFloat(similarity.toFixed(2))
            });
        }
    }

    // 按相似度降序排序
    semanticRelated.sort((a, b) => b.similarityScore - a.similarityScore);

    return {
        success: true,
        targetDoc: targetDoc,
        semanticRelated: semanticRelated,
        totalDocsScanned: totalDocsScanned,
        totalRelated: semanticRelated.length
    };
}

function batchDetect(docList, docDir, recursive = false, minOverlap = 1) {
    /**
     * 批量检测语义关联
     *
     * Args:
     *     docList: 文档列表
     *     docDir: 文档目录
     *     recursive: 是否递归扫描
     *     minOverlap: 关键词最小重叠度
     *
     * Returns:
     *     dict: 批量检测结果
     */
    const results = [];

    for (const doc of docList) {
        const docPath = doc.startsWith(docDir) ? doc : path.join(docDir, doc);

        if (!fs.existsSync(docPath)) {
            results.push({
                doc: doc,
                success: false,
                error: "文件不存在"
            });
            continue;
        }

        const result = detectSemanticRelated(docPath, docDir, recursive, minOverlap);
        results.push({
            doc: doc,
            ...result
        });
    }

    return {
        success: true,
        results: results,
        totalDocs: docList.length,
        successfulDetections: results.filter(r => r.success).length,
        failedDetections: results.filter(r => !r.success).length
    };
}

function printHelp() {
    console.log(`
语义关联检测器 - 基于 keywords 字段检测语义关联文档

使用方法:
    node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md"
    node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/
    node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --doc-dir dev_docs/ --recursive
    node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --min-overlap 2
    node tools/js/semantic_related_detector.js --doc "dev_docs/api_layer.md" --verbose
    node tools/js/semantic_related_detector.js --batch --doc-list "dev_docs/api_layer.md,dev_docs/state_management.md"

选项:
    --doc PATH               目标文档路径
    --doc-dir PATH           文档目录，默认 dev_docs/
    --recursive              递归扫描文档目录
    --min-overlap NUM        关键词最小重叠度，默认 1
    --batch                  批量检测模式
    --doc-list DOCS          逗号分隔的文档列表（批量模式）
    --verbose                输出详细信息
    --timeout SECONDS        超时时间，默认 10 秒
    --help, -h              显示此帮助信息
`);
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        doc: null,
        docDir: DEFAULT_DOC_DIR,
        recursive: false,
        minOverlap: 1,
        batch: false,
        docList: null,
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
            case '--doc':
                options.doc = args[++i];
                i++;
                break;
            case '--doc-dir':
                options.docDir = args[++i];
                i++;
                break;
            case '--recursive':
                options.recursive = true;
                i++;
                break;
            case '--min-overlap':
                options.minOverlap = parseInt(args[++i]);
                i++;
                break;
            case '--batch':
                options.batch = true;
                i++;
                break;
            case '--doc-list':
                options.docList = args[++i];
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

    // 参数验证
    if (options.batch && !options.docList) {
        console.error("Error: 批量检测模式需要 --doc-list 参数");
        process.exit(1);
    }

    if (!options.batch && !options.doc) {
        console.error("Error: 单个文档检测需要 --doc 参数");
        process.exit(1);
    }

    const result = {
        success: true,
        data: {},
        metadata: {
            version: VERSION
        }
    };

    try {
        if (options.batch) {
            // 批量检测
            const docList = options.docList.split(',').map(d => d.trim()).filter(d => d);

            if (!docList.length) {
                result.success = false;
                result.error = "文档列表不能为空";
            } else {
                const batchResult = batchDetect(docList, options.docDir, options.recursive, options.minOverlap);
                result.data = {
                    action: "batch_detection",
                    result: batchResult
                };
            }
        } else {
            // 单个文档检测
            if (!fs.existsSync(options.doc)) {
                result.success = false;
                result.error = `文档不存在: ${options.doc}`;
            } else if (!fs.statSync(options.doc).isFile()) {
                result.success = false;
                result.error = `不是有效的文件: ${options.doc}`;
            } else {
                const detectionResult = detectSemanticRelated(
                    options.doc,
                    options.docDir,
                    options.recursive,
                    options.minOverlap
                );
                result.data = {
                    action: "single_detection",
                    result: detectionResult
                };
            }
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }

    // 输出JSON
    console.log(JSON.stringify(result, null, 2));
}

main();
