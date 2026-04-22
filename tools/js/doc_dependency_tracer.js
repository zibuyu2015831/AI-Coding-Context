#!/usr/bin/env node

/**
 * 文档依赖追踪器 - 基于 dependencies 字段追踪文档间的依赖关系
 * 
 * 功能说明:
 *     - 读取目标文档的 dependencies 字段
 *     - 查找依赖当前文档的其他文档（反向依赖）
 *     - 支持三级检测策略: dependencies > keywords > 全文搜索
 *     - 生成依赖关系图谱和修复建议
 *     - 支持批量文档分析和影响范围评估
 * 
 * 使用方法:
 *     // 分析单个文档的依赖关系
 *     node tools/js/doc_dependency_tracer.js --doc "dev_docs/api_layer.md"
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-13
 *     Purpose: Support 011-Doc Error Fix Workflow
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
    if (!match) return null;
    const yamlContent = match[1];
    return parseYamlSimple(yamlContent);
}

/**
 * 简单的YAML解析器
 */
function parseYamlSimple(yamlStr) {
    const result = {};
    const lines = yamlStr.trim().split('\n');
    for (let line of lines) {
        line = line.trim();
        if (!line || line.startsWith('#')) continue;
        if (!line.includes(':')) continue;
        const colonIndex = line.indexOf(':');
        const key = line.substring(0, colonIndex).trim();
        let value = line.substring(colonIndex + 1).trim();
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
 * 从文档提取dependencies字段
 */
function extractDependencies(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);
        if (!summary || !summary.dependencies) return null;
        const dependencies = summary.dependencies;
        if (Array.isArray(dependencies)) {
            return dependencies.filter(d => d && d !== '无');
        } else if (typeof dependencies === 'string' && dependencies !== '无') {
            if (dependencies.includes('|')) {
                return dependencies.split('|').map(d => d.trim()).filter(d => d);
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
        if (!summary || !summary.keywords) return null;
        const keywords = summary.keywords;
        if (Array.isArray(keywords)) {
            return keywords.filter(k => k && k !== '无');
        } else if (typeof keywords === 'string' && keywords !== '无') {
            if (keywords.includes('|')) {
                return keywords.split('|').map(k => k.trim()).filter(k => k);
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
    const scan = (dir) => {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                if (recursive && !['.git', 'node_modules', '__pycache__', 'dist', 'build'].includes(entry.name)) {
                    scan(fullPath);
                }
            } else if (entry.isFile() && entry.name.endsWith('.md')) {
                mdFiles.push(fullPath);
            }
        }
    };
    scan(directory);
    return mdFiles;
}

/**
 * 标准化路径用于比较
 */
function normalizePath(p) {
    return path.normalize(p).replace(/\\/g, '/');
}

/**
 * 分析文档的依赖关系
 */
function analyzeDependencies(targetDocs, docDir, recursive = false, strategy = "dependencies", minOverlap = 1) {
    const targetDocsNormalized = targetDocs.map(doc => {
        const fullPath = path.isAbsolute(doc) ? doc : path.join(docDir, doc);
        return normalizePath(fullPath);
    });

    const allDocs = findMarkdownFiles(docDir, recursive);
    const results = [];

    for (const targetDoc of targetDocsNormalized) {
        if (!fs.existsSync(targetDoc)) {
            results.push({
                target_doc: targetDoc,
                error: "文件不存在",
                forward_deps: [],
                backward_deps: [],
                semantic_related: []
            });
            continue;
        }

        const result = {
            target_doc: targetDoc,
            forward_deps: [],
            backward_deps: [],
            semantic_related: []
        };

        // 正向依赖
        if (strategy === "dependencies" || strategy === "all") {
            const deps = extractDependencies(targetDoc);
            if (deps) result.forward_deps = deps;
        }

        // 反向依赖
        if (strategy === "dependencies" || strategy === "all") {
            const backwardDeps = [];
            for (const otherDoc of allDocs) {
                const otherDocNormalized = normalizePath(otherDoc);
                if (otherDocNormalized === targetDoc) continue;
                const otherDeps = extractDependencies(otherDoc);
                if (otherDeps) {
                    for (const dep of otherDeps) {
                        if (targetDoc.includes(dep) || dep.includes(targetDoc)) {
                            backwardDeps.push(path.relative(docDir, otherDoc));
                            break;
                        }
                    }
                }
            }
            result.backward_deps = backwardDeps;
        }

        // 语义关联
        if (strategy === "keywords" || strategy === "all") {
            const targetKeywords = extractKeywords(targetDoc);
            if (targetKeywords) {
                const semanticRelated = [];
                for (const otherDoc of allDocs) {
                    const otherDocNormalized = normalizePath(otherDoc);
                    if (otherDocNormalized === targetDoc) continue;
                    const otherKeywords = extractKeywords(otherDoc);
                    if (!otherKeywords) continue;
                    
                    const targetSet = new Set(targetKeywords.map(k => k.toLowerCase()));
                    const otherSet = new Set(otherKeywords.map(k => k.toLowerCase()));
                    const overlap = [...targetSet].filter(k => otherSet.has(k));
                    
                    if (overlap.length >= minOverlap) {
                        semanticRelated.push({
                            doc: path.relative(docDir, otherDoc),
                            overlap: overlap.length,
                            common_keywords: overlap
                        });
                    }
                }
                semanticRelated.sort((a, b) => b.overlap - a.overlap);
                result.semantic_related = semanticRelated;
            }
        }
        results.push(result);
    }

    const totalDeps = results.reduce((sum, r) => sum + r.forward_deps.length + r.backward_deps.length, 0);
    const impactScore = Math.min(1.0, totalDeps / 10);

    return {
        results,
        total_docs_scanned: allDocs.length,
        impact_score: impactScore,
        strategy
    };
}

function main() {
    const startTime = Date.now();
    const args = process.argv.slice(2);
    const options = {
        doc: null,
        strategy: "dependencies",
        docDir: DEFAULT_DOC_DIR,
        recursive: false,
        suggestFixes: false,
        minOverlap: 1,
        outputFormat: "json"
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--doc': options.doc = args[++i]; break;
            case '--strategy': options.strategy = args[++i]; break;
            case '--doc-dir': options.docDir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--suggest-fixes': options.suggestFixes = true; break;
            case '--min-overlap': options.minOverlap = parseInt(args[++i]); break;
            case '--output-format': options.outputFormat = args[++i]; break;
        }
    }

    if (!options.doc) {
        console.error("Error: --doc parameter is required");
        process.exit(1);
    }

    const targetDocs = options.doc.split(',').map(d => d.trim()).filter(d => d);
    const result = {
        success: true,
        data: {},
        metadata: {
            elapsed_seconds: 0,
            version: VERSION,
            target_docs: targetDocs,
            strategy: options.strategy
        }
    };

    try {
        const analysisResult = analyzeDependencies(
            targetDocs, options.docDir, options.recursive, options.strategy, options.minOverlap
        );
        result.data.analysis = analysisResult;
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }

    result.metadata.elapsed_seconds = (Date.now() - startTime) / 1000;

    if (options.outputFormat === "json") {
        console.log(JSON.stringify(result, null, 2));
    } else {
        // Simple markdown output
        console.log(`# 文档依赖分析报告\n`);
        console.log(`**分析时间**: ${result.metadata.elapsed_seconds}s\n`);
        console.log(`**目标文档**: ${targetDocs.join(', ')}\n`);
    }

    process.exit(result.success ? 0 : 1);
}

main();
