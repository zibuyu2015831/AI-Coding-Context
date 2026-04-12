#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
// Note: Normally we would use a real yaml parser 'js-yaml' through require,
// but for zero-dependency standard, we'll do a simple naive text regex parser
// specifically tuned for the constraints format in ADRs.

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
