#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        query: '',
        file: '',
        adrDir: 'dev_docs/architecture/decisions'
    };
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--query' && i + 1 < args.length) {
            parsed.query = args[++i];
        } else if (args[i] === '--file' && i + 1 < args.length) {
            parsed.file = args[++i];
        } else if (args[i] === '--adr-dir' && i + 1 < args.length) {
            parsed.adrDir = args[++i];
        }
    }
    return parsed;
}

function extractFrontmatterAndContent(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
        
        let meta = {};
        let body = content;
        
        if (match) {
            const fmText = match[1];
            body = match[2];
            
            fmText.split('\n').forEach(line => {
                const parts = line.split(':');
                if (parts.length >= 2) {
                    const key = parts.shift().trim();
                    const value = parts.join(':').trim().replace(/^['"]|['"]$/g, '');
                    meta[key] = value;
                }
            });
        }
        return { meta, body };
    } catch (e) {
        return { meta: {}, body: '' };
    }
}

function scanFileForAnnotations(filepath) {
    try {
        const content = fs.readFileSync(filepath, 'utf-8');
        const lines = content.split('\n');
        const annotations = [];
        
        lines.forEach((line, i) => {
            const match = line.match(/@architecture\s+(ADR-\d+):?\s*(.*)/i);
            if (match) {
                annotations.push({
                    line: i + 1,
                    adr: match[1].toUpperCase(),
                    desc: match[2].trim()
                });
            }
            
            const reasonMatch = line.match(/@reason\s+(.*)/i);
            if (reasonMatch) {
                annotations.push({
                    line: i + 1,
                    adr: "IMPLICIT",
                    desc: reasonMatch[1].trim()
                });
            }
        });
        return annotations;
    } catch (e) {
        console.error(`Error reading file ${filepath}: ${e.message}`);
        return [];
    }
}

function getMarkdownFiles(dir) {
    let results = [];
    try {
        const list = fs.readdirSync(dir);
        list.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            if (stat && stat.isDirectory()) {
                if (file !== 'archived') {
                    results = results.concat(getMarkdownFiles(filePath));
                }
            } else if (file.endsWith('.md')) {
                results.push(filePath);
            }
        });
    } catch (e) {
        // Directory might not exist
    }
    return results;
}

function searchAdrs(query, adrDir) {
    const files = getMarkdownFiles(adrDir);
    const queryTerms = query.toLowerCase().split(/\s+/).filter(q => q);
    const results = [];
    
    files.forEach(file => {
        const { meta, body } = extractFrontmatterAndContent(file);
        let score = 0;
        const title = meta.title || path.basename(file);
        const summary = meta.summary || '';
        
        const searchTarget = `${title} ${summary} ${body}`.toLowerCase();
        
        queryTerms.forEach(term => {
            if (searchTarget.includes(term)) {
                score += 1;
                if (summary.toLowerCase().includes(term) || title.toLowerCase().includes(term)) {
                    score += 2;
                }
            }
        });
        
        if (score > 0) {
            results.push({
                file,
                title,
                summary,
                score
            });
        }
    });
    
    return results.sort((a, b) => b.score - a.score);
}

function main() {
    const args = parseArgs();
    
    if (!args.query && !args.file) {
        console.log("Please provide either --query or --file argument.");
        process.exit(1);
    }
    
    console.log("=== Why-Tool: Architecture Context Retriever (Node.js) ===");
    
    const foundAdrs = new Set();
    if (args.file && fs.existsSync(args.file)) {
        console.log(`Scanning ${args.file} for L1 annotations...`);
        const annots = scanFileForAnnotations(args.file);
        if (annots.length > 0) {
            annots.forEach(ann => {
                console.log(`[Line ${ann.line}] Found Annotation: ${ann.adr} - ${ann.desc}`);
                if (ann.adr.startsWith("ADR-")) {
                    foundAdrs.add(ann.adr);
                }
            });
        } else {
            console.log("No @architecture annotations found in file.");
        }
    }
    
    foundAdrs.forEach(adrId => {
        const files = getMarkdownFiles(args.adrDir);
        files.forEach(file => {
            if (path.basename(file).toLowerCase().includes(adrId.toLowerCase())) {
                const { meta } = extractFrontmatterAndContent(file);
                console.log(`\n=> 🎯 Exact Match: ${path.basename(file)}`);
                console.log(`   Title: ${meta.title || 'N/A'}`);
                console.log(`   Summary: ${meta.summary || 'N/A'}`);
            }
        });
    });
    
    if (args.query) {
        console.log(`\nRunning semantic keyword search for: '${args.query}'...`);
        const results = searchAdrs(args.query, args.adrDir);
        if (results.length === 0) {
            console.log("No matching active ADRs found.");
        } else {
            console.log("\n=> 🔎 Top Matching Active ADRs:");
            results.slice(0, 3).forEach(res => {
                console.log(` - [${res.score} pts] ${res.file}`);
                console.log(`   Title: ${res.title}`);
                console.log(`   Summary: ${res.summary}`);
            });
        }
    }
}

main();
