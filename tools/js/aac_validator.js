#!/usr/bin/env node
/**
 * AaC Validator: 架构即代码静态验证工具 (Architecture as Code) — Node.js 版本
 *
 * 功能说明:
 *     从 Markdown ADR 文档中提取 YAML 约束，对代码进行静态扫描验证。
 *     - 解析 ADR 中的 machine-readable constraints 代码块
 *     - 支持 regex_check 正则匹配检查
 *     - 支持 dependency_check 依赖检查
 *     - 输出架构违规报告
 *
 * 使用方法:
 *     # 扫描整个目录
 *     node tools/js/aac_validator.js --scan-dir ./src
 *
 *     # 扫描特定文件
 *     node tools/js/aac_validator.js --scan-file src/utils/helpers.ts
 *
 *     # 指定自定义 ADR 目录
 *     node tools/js/aac_validator.js --adr-dir docs/architecture/decisions --scan-dir ./src
 *
 * 参数说明:
 *     --scan-file PATH    扫描特定文件路径
 *     --scan-dir PATH     扫描目录 (默认: 当前目录)
 *     --adr-dir PATH      ADR 文档目录 (默认: dev_docs/architecture/decisions)
 *
 * 输出格式:
 *     文本输出，包含以下信息:
 *     - 加载的约束数量
 *     - 扫描的文件数量
 *     - 违规详情列表 (ADR来源、违规类型、违规信息、文件路径)
 *     - 或合规确认信息
 *
 *     退出码:
 *     - 0: 无违规或未发现约束
 *     - 1: 发现架构违规
 *
 * 设计决策（V3.0 红线）:
 *     遵守"零依赖"约束 — 不引入 js-yaml，自实现简化 YAML 解析（针对 ADR
 *     constraints 代码块格式特化）。与 tools/py/aac_validator.py 双脚本对称。
 */

const fs = require('fs');
const path = require('path');

function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        scanFile: '',
        scanDir: '.',
        adrDir: 'dev_docs/architecture/decisions'
    };
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--scan-file' && i + 1 < args.length) {
            parsed.scanFile = args[++i];
        } else if (args[i] === '--scan-dir' && i + 1 < args.length) {
            parsed.scanDir = args[++i];
        } else if (args[i] === '--adr-dir' && i + 1 < args.length) {
            parsed.adrDir = args[++i];
        }
    }
    return parsed;
}

// Very naive YAML parsing since we cannot use npm installs (Zero-dependency rule)
function naiveParseYamlConstraints(yamlText) {
    const lines = yamlText.split('\n');
    const constraints = [];
    let currentConstraint = null;

    for (let line of lines) {
        line = line.trimEnd();
        if (!line.trim() || line.trim().startsWith('#')) continue;

        if (line.match(/^\s*-\s*type:\s*['"]?(.*?)['"]?$/)) {
            if (currentConstraint) {
                constraints.push(currentConstraint);
            }
            currentConstraint = { type: line.match(/^\s*-\s*type:\s*['"]?(.*?)['"]?$/)[1] };
        } else if (currentConstraint) {
            const propMatch = line.match(/^\s*([a-zA-Z_]+):\s*(.*)$/);
            if (propMatch) {
                const key = propMatch[1];
                const val = propMatch[2].trim();
                
                // Simple array detection [a, b]
                if (val.startsWith('[') && val.endsWith(']')) {
                    const arrText = val.slice(1, -1);
                    currentConstraint[key] = arrText.split(',').map(s => s.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
                } else {
                    // Handle quoted strings and escaped backslashes
                    const parsedVal = val.replace(/^['"]|['"]$/g, '').replace(/\\\\/g, '\\');
                    currentConstraint[key] = parsedVal;
                }
            }
        }
    }
    if (currentConstraint) {
        constraints.push(currentConstraint);
    }
    return constraints;
}

function extractConstraintsFromAdr(filepath) {
    try {
        const content = fs.readFileSync(filepath, 'utf-8');
        const match = content.match(/```yaml\s*\nconstraints:\n([\s\S]*?)\n```/i);
        if (!match) return [];
        return naiveParseYamlConstraints(match[1]);
    } catch (e) {
        console.error(`Error parsing constraints in ${filepath}: ${e.message}`);
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
        // Ignored
    }
    return results;
}

function loadAllActiveConstraints(adrDir) {
    const allConstraints = [];
    const files = getMarkdownFiles(adrDir);
    
    files.forEach(file => {
        const cList = extractConstraintsFromAdr(file);
        cList.forEach(c => {
            c.source_adr = path.basename(file);
            allConstraints.push(c);
        });
    });
    
    return allConstraints;
}

function matchPathGlob(pathStr, globPattern) {
    let pattern = globPattern.replace(/\./g, '\\.').replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*');
    const regex = new RegExp(`^${pattern}`);
    return regex.test(pathStr.replace(/\\/g, '/'));
}

function getAllFiles(dir) {
    let results = [];
    try {
        const list = fs.readdirSync(dir);
        list.forEach(file => {
            const filePath = path.join(dir, file);
            if (filePath.includes('.git') || filePath.includes('node_modules')) return;
            
            const stat = fs.statSync(filePath);
            if (stat && stat.isDirectory()) {
                results = results.concat(getAllFiles(filePath));
            } else {
                results.push(filePath);
            }
        });
    } catch (e) {
        // Ignored
    }
    return results;
}

function validateFile(filepath, constraints) {
    const violations = [];
    let content = '';
    
    try {
        content = fs.readFileSync(filepath, 'utf-8');
    } catch (e) {
        return violations;
    }

    const pathNormalized = filepath.replace(/\\/g, '/');

    constraints.forEach(c => {
        const cType = c.type;
        
        if (cType === 'regex_check') {
            const forbiddenIn = c.forbidden_in || [];
            const patternStr = c.pattern || '';
            
            let inScope = false;
            for (let i = 0; i < forbiddenIn.length; i++) {
                if (matchPathGlob(pathNormalized, forbiddenIn[i])) {
                    inScope = true;
                    break;
                }
            }
            
            if (inScope && patternStr) {
                const regex = new RegExp(patternStr, 'i');
                if (regex.test(pathNormalized)) {
                    violations.push({
                        adr: c.source_adr,
                        type: cType,
                        message: c.message || `FileName matched forbidden pattern: ${patternStr}`
                    });
                } else if (regex.test(content)) {
                    violations.push({
                        adr: c.source_adr,
                        type: cType,
                        message: c.message || `Content matched forbidden pattern: ${patternStr}`
                    });
                }
            }
        } else if (cType === 'dependency_check' && pathNormalized.endsWith('package.json')) {
            const required = c.required || [];
            const forbidden = c.forbidden || [];
            
            required.forEach(req => {
                if (!content.includes(`"${req}"`)) {
                    violations.push({
                        adr: c.source_adr,
                        type: cType,
                        message: `Required dependency missing: ${req}`
                    });
                }
            });
            
            forbidden.forEach(fp => {
                if (content.includes(`"${fp}"`)) {
                    violations.push({
                        adr: c.source_adr,
                        type: cType,
                        message: `Forbidden dependency found: ${fp}`
                    });
                }
            });
        }
    });

    return violations;
}

function main() {
    const args = parseArgs();
    
    console.log("=== AaC (Architecture as Code) Validator (Node.js) ===");
    const constraints = loadAllActiveConstraints(args.adrDir);
    
    if (constraints.length === 0) {
        console.log("No machine-readable constraints found in Active ADRs.");
        process.exit(0);
    }
    
    console.log(`Loaded ${constraints.length} constraint(s) from ADRs. Scanning...`);
    
    const allViolations = [];
    let filesToScan = [];
    
    if (args.scanFile) {
        filesToScan.push(args.scanFile);
    } else {
        filesToScan = getAllFiles(args.scanDir);
    }
    
    let scannedCount = 0;
    filesToScan.forEach(p => {
        scannedCount++;
        const v = validateFile(p, constraints);
        v.forEach(viol => {
            viol.file = p;
            allViolations.push(viol);
        });
    });
    
    if (allViolations.length > 0) {
        console.log(`\n❌ Found ${allViolations.length} architecture violation(s) across ${scannedCount} files:`);
        allViolations.forEach(v => {
            console.log(`  - [${v.adr}] in ${v.file}: ${v.message}`);
        });
        process.exit(1);
    } else {
        console.log(`\n✅ All ${scannedCount} scanned file(s) comply with Active ADRs.`);
        process.exit(0);
    }
}

main();
