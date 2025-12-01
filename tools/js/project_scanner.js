const fs = require('fs');
const path = require('path');

function loadGitignorePatterns(rootDir) {
    const patterns = [];
    const gitignorePath = path.join(rootDir, '.gitignore');
    if (fs.existsSync(gitignorePath)) {
        try {
            const content = fs.readFileSync(gitignorePath, 'utf8');
            content.split('\n').forEach(line => {
                line = line.trim();
                if (line && !line.startsWith('#')) {
                    patterns.push(line);
                }
            });
        } catch (e) {
            console.error(`Warning: Could not read .gitignore: ${e.message}`);
        }
    }
    return patterns;
}

// Simple glob matcher (simplified for zero dependency)
function matchGlob(str, pattern) {
    // Escape regex characters except * and ?
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    // Handle directory specific pattern
    if (pattern.endsWith('/')) {
        return new RegExp(`^${regexStr}`).test(str + '/');
    }
    return new RegExp(`^${regexStr}$`).test(str);
}

function isIgnored(filePath, patterns, rootDir) {
    const relPath = path.relative(rootDir, filePath);
    if (relPath === '') return false;
    
    // Normalize to /
    const normalizedRelPath = relPath.split(path.sep).join('/');
    const name = path.basename(filePath);
    
    for (const pattern of patterns) {
        if (pattern.endsWith('/')) {
             if (matchGlob(normalizedRelPath + '/', pattern) || matchGlob(name + '/', pattern)) return true;
        } else {
             if (matchGlob(normalizedRelPath, pattern) || matchGlob(name, pattern)) return true;
        }
    }
    return false;
}

function generateTree(structure, prefix = "") {
    let lines = [];
    const keys = Object.keys(structure).sort();
    keys.forEach((key, i) => {
        const isLast = (i === keys.length - 1);
        const connector = isLast ? "└── " : "├── ";
        lines.push(`${prefix}${connector}${key}`);
        
        if (structure[key] && typeof structure[key] === 'object') {
            const extension = isLast ? "    " : "│   ";
            lines = lines.concat(generateTree(structure[key], prefix + extension));
        }
    });
    return lines;
}

function scanProject(rootDir, ignorePatterns, followSymlinks, maxFilesPerDir, maxDepth) {
    const structure = {};
    const stats = { files: 0, dirs: 0 };
    
    // Queue: [currentPath, depth, parentDict]
    const queue = [[rootDir, 0, structure]];
    
    const allPatterns = [...ignorePatterns, '.git'];
    const gitignorePatterns = loadGitignorePatterns(rootDir);
    allPatterns.push(...gitignorePatterns);
    
    const processedDirs = new Set();

    while (queue.length > 0) {
        const [currentPath, depth, parentDict] = queue.shift();
        
        if (maxDepth !== undefined && depth > maxDepth) continue;
        
        if (!followSymlinks) {
            try {
                const lstat = fs.lstatSync(currentPath);
                if (lstat.isSymbolicLink()) continue;
            } catch (e) { continue; }
        }
        
        const realPath = fs.realpathSync(currentPath);
        if (processedDirs.has(realPath)) continue;
        processedDirs.add(realPath);
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath).sort();
        } catch (e) {
            console.error(`Warning: Error accessing ${currentPath}: ${e.message}`);
            continue;
        }
        
        let fileCount = 0;
        
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry);
            
            if (isIgnored(fullPath, allPatterns, rootDir)) continue;
            
            let stat;
            try {
                stat = followSymlinks ? fs.statSync(fullPath) : fs.lstatSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                if (!followSymlinks && stat.isSymbolicLink()) {
                    parentDict[entry] = "[Symlink Dir]";
                    stats.files++;
                } else {
                    const newDict = {};
                    parentDict[entry] = newDict;
                    stats.dirs++;
                    queue.push([fullPath, depth + 1, newDict]);
                }
            } else {
                if (fileCount < maxFilesPerDir) {
                    parentDict[entry] = null;
                    stats.files++;
                    fileCount++;
                } else if (fileCount === maxFilesPerDir) {
                    parentDict["..."] = `(truncated, >${maxFilesPerDir} files)`;
                    fileCount++;
                }
            }
        }
    }
    
    return { structure, stats };
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        path: '.',
        ignore: [],
        followSymlinks: false,
        maxFiles: 1000,
        depth: undefined,
        format: 'json'
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--path': options.path = args[++i]; break;
            case '--ignore': options.ignore = args[++i].split(','); break;
            case '--follow-symlinks': options.followSymlinks = true; break;
            case '--max-files': options.maxFiles = parseInt(args[++i]); break;
            case '--depth': options.depth = parseInt(args[++i]); break;
            case '--format': options.format = args[++i]; break;
        }
    }
    
    const rootDir = path.resolve(options.path);
    const result = scanProject(
        rootDir, 
        options.ignore, 
        options.followSymlinks, 
        options.maxFiles, 
        options.depth
    );
    
    if (options.format === 'json') {
        console.log(JSON.stringify(result, null, 2));
    } else {
        const treeLines = generateTree(result.structure);
        console.log(treeLines.join('\n'));
        console.log(`\nStats: ${result.stats.files} files, ${result.stats.dirs} directories`);
    }
}

main();
