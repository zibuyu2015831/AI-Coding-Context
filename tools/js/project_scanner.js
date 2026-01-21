/**
 * 项目结构扫描工具 - 生成项目目录树的 JSON 或文本表示
 * 
 * 功能说明：
 * - 扫描指定目录，生成完整的目录树结构
 * - 自动读取并尊重 .gitignore 规则
 * - 智能自适应输出策略，根据项目规模自动优化
 * - 重要文件优先显示（README.md, package.json等）
 * - 支持输出 JSON 格式（供 AI 解析）或树形文本格式（供人类阅读）
 * 
 * 使用方法：
 *   node tools/js/project_scanner.js [--path 路径] [选项]
 * 
 * 核心参数：
 *   --mode MODE              输出模式: tree, summary, auto (默认: auto)
 *   --complexity-override    手动指定复杂度: basic, medium, advanced
 *   --limit-files NUM        中级/高级模式每目录文件数限制 (默认: 10)
 *   --limit-dirs NUM         高级模式每目录子目录数限制 (默认: 10)
 *   --no-adaptive            禁用自适应，始终输出完整树
 *   --advanced-dir-threshold 高级模式智能判断阈值 (默认: 20)
 * 
 * 传统参数：
 *   --path PATH              要扫描的根目录路径（默认：当前目录）
 *   --ignore PATTERNS        逗号分隔的忽略模式
 *   --exclude-standard       一键排除标准模式（框架、依赖、IDE）
 *   --follow-symlinks        跟随符号链接
 *   --max-files NUM          每目录最大文件数（旧参数，建议用--limit-files）
 *   --depth NUM              最大扫描深度
 *   --format FORMAT          输出格式：json 或 tree（默认：json）
 * 
 * 版本信息：
 *   版本：1.3.0
 *   更新日期：2025-12-21
 */

const fs = require('fs');
const path = require('path');

// ==================== 重要文件优先级系统 ====================
// 参见 dev/tools_optimization/important_files_reference.md

const IMPORTANT_FILES = {
    // 优先级 1 (最高)
    'README.md': 1, 'README.rst': 1, 'LICENSE': 1, 'LICENSE.md': 1,
    'package.json': 1, 'setup.py': 1, 'pyproject.toml': 1,
    'pom.xml': 1, 'build.gradle': 1, 'go.mod': 1, 'Cargo.toml': 1,
    'Dockerfile': 1,
    
    // 优先级 2 (高)
    'tsconfig.json': 2, 'jsconfig.json': 2,
    'requirements.txt': 2, 'Pipfile': 2,
    '.gitignore': 2, 'CHANGELOG.md': 2,
    'docker-compose.yml': 2,
    
    // 优先级 3 (中)
    'webpack.config.js': 3, 'vite.config.ts': 3, 'vite.config.js': 3,
    'next.config.js': 3, 'nuxt.config.js': 3,
    '.eslintrc.js': 3, '.eslintrc.json': 3, '.prettierrc': 3,
    'jest.config.js': 3, 'vitest.config.ts': 3,
};

const IMPORTANT_PATTERNS = [
    /^index\.(js|ts|jsx|tsx|py|php)$/,
    /^main\.(js|ts|go|rs|c|cpp)$/,
    /^app\.(js|ts|jsx|tsx|py)$/,
    /^App\.(tsx|jsx)$/,
    /^__init__\.py$/,
    /^__main__\.py$/,
    /\.config\.(js|ts)$/,
    /^\.env/,
];

const IMPORTANT_DIRS = {
    'src': 1,
    'lib': 2,
    'app': 2,
    'components': 3,
    'pages': 3,
    'utils': 3,
    'api': 3,
    'config': 3,
    'tests': 10,
};

function getFilePriority(filename) {
    if (filename in IMPORTANT_FILES) {
        return [IMPORTANT_FILES[filename], filename];
    }
    
    for (const pattern of IMPORTANT_PATTERNS) {
        if (pattern.test(filename)) {
            return [2, filename];
        }
    }
    
    return [100, filename.toLowerCase()];
}

function sortFilesByImportance(files) {
    return files.sort((a, b) => {
        const [priorityA, nameA] = getFilePriority(a);
        const [priorityB, nameB] = getFilePriority(b);
        
        if (priorityA !== priorityB) {
            return priorityA - priorityB;
        }
        return nameA.localeCompare(nameB);
    });
}

function sortDirsByImportance(dirs) {
    return dirs.sort((a, b) => {
        const cleanA = a.replace(/\/$/, '');
        const cleanB = b.replace(/\/$/, '');
        
        const priorityA = IMPORTANT_DIRS[cleanA] || 100;
        const priorityB = IMPORTANT_DIRS[cleanB] || 100;
        
        if (priorityA !== priorityB) {
            return priorityA - priorityB;
        }
        return cleanA.toLowerCase().localeCompare(cleanB.toLowerCase());
    });
}

function loadGitignorePatterns(rootDir) {
    const patterns = [];
    const gitignorePath = path.join(rootDir, '.gitignore');
    
    if (fs.existsSync(gitignorePath)) {
        const content = fs.readFileSync(gitignorePath, 'utf-8');
        const lines = content.split(/\r?\n/);
        
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed && !trimmed.startsWith('#')) {
                patterns.push(trimmed);
            }
        }
    }
    
    return patterns;
}

function detectFrameworkDir(rootDir, scriptFile = null) {
    if (scriptFile) {
        try {
            const scriptPath = path.resolve(scriptFile);
            const scriptDir = path.dirname(scriptPath);
            const toolsDir = path.dirname(scriptDir);
            const frameworkDir = toolsDir;
            
            if (frameworkDir.startsWith(rootDir)) {
                return path.relative(rootDir, frameworkDir).replace(/\\/g, '/');
            }
        } catch (e) {
            // Fallback to detection
        }
    }
    
    const commonNames = [
        'ai_coding_context',
        '.ai_coding_context',
        'ai-coding-context',
        '.ai-coding-context'
    ];
    
    for (const name of commonNames) {
        const frameworkPath = path.join(rootDir, name);
        if (fs.existsSync(frameworkPath)) {
            return name;
        }
    }
    
    return null;
}

function getStandardExcludePatterns(rootDir, scriptFile = null) {
    const patterns = [
        ['node_modules/', 'dependency'],
        ['package-lock.json', 'lock file'],
        ['venv/', 'python env'],
        ['env/', 'env'],
        ['.env/', 'env'],
        ['__pycache__/', 'python cache'],
        ['dist/', 'build'],
        ['build/', 'build'],
        ['.next/', 'next.js'],
        ['out/', 'build output'],
        ['target/', 'build'],
        ['*.egg-info/', 'python'],
        ['.pytest_cache/', 'test cache'],
        ['.svn/', 'vcs'],
        ['.vscode/', 'ide'],
        ['.idea/', 'ide'],
        ['*.swp', 'temp'],
        ['*.swo', 'temp']
    ];
    
    const frameworkDir = detectFrameworkDir(rootDir, scriptFile);
    if (frameworkDir) {
        patterns.unshift([frameworkDir + '/', 'framework']);
        patterns.unshift(['.ai/', 'ai workspace']);
        patterns.unshift(['docs/ai_context/', 'ai docs']);
    }
    
    return patterns;
}

function matchGlob(str, pattern) {
    const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*')
        .replace(/\?/g, '.');
    const regex = new RegExp(`^${regexPattern}$`);
    return regex.test(str);
}

function isIgnored(filePath, patterns, rootDir) {
    const relativePath = path.relative(rootDir, filePath).replace(/\\/g, '/');
    const fileName = path.basename(filePath);
    
    for (let pattern of patterns) {
        if (Array.isArray(pattern)) {
            pattern = pattern[0];
        }
        
        if (pattern.endsWith('/')) {
            const dirPattern = pattern.slice(0, -1);
            if (relativePath === dirPattern || relativePath.startsWith(dirPattern + '/')) {
                return true;
            }
        } else if (matchGlob(relativePath, pattern) || matchGlob(fileName, pattern)) {
            return true;
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

function scanSummary(rootDir, ignorePatterns, followSymlinks, excludeStandard, scriptFile) {
    const stats = { files: 0, dirs: 0, maxDepth: 0 };
    const emptyDirs = [];
    
    let allPatterns = [...ignorePatterns, '.git'];
    if (excludeStandard) {
        const standardPatterns = getStandardExcludePatterns(rootDir, scriptFile);
        for (const p of standardPatterns) {
            if (Array.isArray(p)) {
                allPatterns.push(p[0]);
            } else {
                allPatterns.push(p);
            }
        }
    }
    
    const gitignorePatterns = loadGitignorePatterns(rootDir);
    allPatterns = allPatterns.concat(gitignorePatterns);
    
    const queue = [[rootDir, 0]];
    const processedDirs = new Set();
    
    while (queue.length > 0) {
        const [currentPath, depth] = queue.shift();
        
        if (!followSymlinks && fs.lstatSync(currentPath).isSymbolicLink()) {
            continue;
        }
        
        const realPath = fs.realpathSync(currentPath);
        if (processedDirs.has(realPath)) {
            continue;
        }
        processedDirs.add(realPath);
        
        stats.maxDepth = Math.max(stats.maxDepth, depth);
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (err) {
            continue;
        }
        
        let hasContent = false;
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry);
            if (isIgnored(fullPath, allPatterns, rootDir)) {
                continue;
            }
            hasContent = true;
            
            const stat = fs.lstatSync(fullPath);
            if (stat.isDirectory()) {
                stats.dirs++;
                queue.push([fullPath, depth + 1]);
            } else {
                stats.files++;
            }
        }
        
        if (!hasContent && currentPath !== rootDir) {
            const relPath = path.relative(rootDir, currentPath).replace(/\\/g, '/');
            emptyDirs.push(relPath + '/');
        }
    }
    
    return {
        total_files: stats.files,
        total_dirs: stats.dirs,
        max_depth: stats.maxDepth,
        empty_dirs: emptyDirs
    };
}

function assessComplexity(summary) {
    const totalFiles = summary.total_files;
    
    if (totalFiles <= 500) {
        return 'basic';
    } else if (totalFiles <= 2000) {
        return 'medium';
    } else {
        return 'advanced';
    }
}

function scanProject(rootDir, ignorePatterns, followSymlinks, maxFilesPerDir, maxDepth, excludeStandard = false, scriptFile = null, limitDirs = null, advancedDirThreshold = 20) {
    const structure = {};
    const stats = { files: 0, dirs: 0 };
    const excludedInfo = [];
    
    const queue = [[rootDir, 0, structure]];
    
    let allPatterns = [...ignorePatterns, '.git'];
    excludedInfo.push('.git/ (hardcoded)');
    
    if (excludeStandard) {
        const standardPatterns = getStandardExcludePatterns(rootDir, scriptFile);
        for (const p of standardPatterns) {
            if (Array.isArray(p)) {
                const [pattern, label] = p;
                allPatterns.push(pattern);
                excludedInfo.push(`${pattern} (${label})`);
            } else {
                allPatterns.push(p);
                excludedInfo.push(p);
            }
        }
    }
    
    for (const p of ignorePatterns) {
        excludedInfo.push(`${p} (manual)`);
    }
    
    const gitignorePatterns = loadGitignorePatterns(rootDir);
    allPatterns = allPatterns.concat(gitignorePatterns);
    if (gitignorePatterns.length > 0) {
        excludedInfo.push(`.gitignore (${gitignorePatterns.length} patterns)`);
    }
    
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
            entries = fs.readdirSync(currentPath);
        } catch (e) {
            console.error(`Warning: Error accessing ${currentPath}: ${e.message}`);
            continue;
        }
        
        const files = [];
        const dirs = [];
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry);
            
            if (isIgnored(fullPath, allPatterns, rootDir)) continue;
            
            let stat;
            try {
                stat = followSymlinks ? fs.statSync(fullPath) : fs.lstatSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                if (!followSymlinks && stat.isSymbolicLink()) {
                    files.push(entry);
                } else {
                    dirs.push(entry);
                }
            } else {
                files.push(entry);
            }
        }
        
        const sortedFiles = sortFilesByImportance(files);
        const sortedDirs = sortDirsByImportance(dirs);
        
        const dirLimit = limitDirs !== null ? limitDirs : Infinity;
        
        if (limitDirs !== null && sortedDirs.length <= advancedDirThreshold && sortedDirs.length > 0) {
            for (const entry of sortedDirs) {
                const fullPath = path.join(currentPath, entry);
                try {
                    const subdirFiles = fs.readdirSync(fullPath).filter(f => {
                        const fp = path.join(fullPath, f);
                        if (isIgnored(fp, allPatterns, rootDir)) return false;
                        try {
                            return fs.lstatSync(fp).isFile();
                        } catch {
                            return false;
                        }
                    });
                    parentDict[entry] = `(${subdirFiles.length} files)`;
                    stats.dirs++;
                } catch {
                    parentDict[entry] = "(无法访问)";
                    stats.dirs++;
                }
            }
        } else {
            for (let i = 0; i < sortedDirs.length; i++) {
                const entry = sortedDirs[i];
                const fullPath = path.join(currentPath, entry);
                
                if (i < dirLimit) {
                    const newDict = {};
                    parentDict[entry] = newDict;
                    stats.dirs++;
                    queue.push([fullPath, depth + 1, newDict]);
                } else if (i === dirLimit) {
                    const relPath = path.relative(rootDir, currentPath).replace(/\\/g, '/');
                    const omittedCount = sortedDirs.length - dirLimit;
                    const suggestion = relPath 
                        ? `使用 --path ./${relPath} --limit-dirs ${sortedDirs.length} 查看更多`
                        : `使用 --limit-dirs ${sortedDirs.length} 查看更多`;
                    parentDict[`... (省略 ${omittedCount} 个子目录, ${suggestion})`] = null;
                    break;
                }
            }
        }
        
        for (let i = 0; i < sortedFiles.length; i++) {
            const entry = sortedFiles[i];
            const fullPath = path.join(currentPath, entry);
            
            if (i < maxFilesPerDir) {
                try {
                    const stat = fs.lstatSync(fullPath);
                    if (stat.isDirectory() && stat.isSymbolicLink()) {
                        parentDict[entry] = "[Symlink Dir]";
                    } else {
                        parentDict[entry] = null;
                    }
                    stats.files++;
                } catch {
                    continue;
                }
            } else if (i === maxFilesPerDir) {
                const relPath = path.relative(rootDir, currentPath).replace(/\\/g,'/');
                const omittedCount = sortedFiles.length - maxFilesPerDir;
                const suggestion = relPath
                    ? `使用 --path ./${relPath} --no-adaptive 查看完整列表`
                    : `使用 --no-adaptive 查看完整列表`;
                parentDict[`... (省略 ${omittedCount} 个文件, ${suggestion})`] = null;
                break;
            }
        }
    }
    
    return { structure, stats, excludedInfo };
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        path: '.',
        mode: 'auto',
        complexityOverride: null,
        limitFiles: 10,
        limitDirs: 10,
        noAdaptive: false,
        advancedDirThreshold: 20,
        ignore: [],
        excludeStandard: false,
        followSymlinks: false,
        maxFiles: 1000,
        depth: undefined,
        format: 'json'
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--path': options.path = args[++i]; break;
            case '--mode': options.mode = args[++i]; break;
            case '--complexity-override': options.complexityOverride = args[++i]; break;
            case '--limit-files': options.limitFiles = parseInt(args[++i]); break;
            case '--limit-dirs': options.limitDirs = parseInt(args[++i]); break;
            case '--no-adaptive': options.noAdaptive = true; break;
            case '--advanced-dir-threshold': options.advancedDirThreshold = parseInt(args[++i]); break;
            case '--ignore': options.ignore = args[++i].split(','); break;
            case '--exclude-standard': options.excludeStandard = true; break;
            case '--follow-symlinks': options.followSymlinks = true; break;
            case '--max-files': options.maxFiles = parseInt(args[++i]); break;
            case '--depth': options.depth = parseInt(args[++i]); break;
            case '--format': options.format = args[++i]; break;
        }
    }
    
    const rootDir = path.resolve(options.path);
    
    let complexity, limitFiles, limitDirs, summary;
    
    if (options.noAdaptive) {
        if (options.complexityOverride || options.limitFiles !== 10 || options.limitDirs !== 10) {
            console.error('Warning: --no-adaptive is enabled, other limit parameters will be ignored');
        }
        complexity = 'basic';
        limitFiles = Infinity;
        limitDirs = Infinity;
    } else {
        summary = scanSummary(rootDir, options.ignore, options.followSymlinks,
                             options.excludeStandard, __filename);
        
        complexity = options.complexityOverride || assessComplexity(summary);
        
        if (complexity === 'basic') {
            limitFiles = Infinity;
            limitDirs = Infinity;
        } else if (complexity === 'medium') {
            limitFiles = options.limitFiles;
            limitDirs = Infinity;
        } else {
            limitFiles = options.limitFiles;
            limitDirs = options.limitDirs;
        }
    }
    
    if (options.mode === 'summary') {
        if (options.noAdaptive) {
            summary = scanSummary(rootDir, options.ignore, options.followSymlinks,
                                 options.excludeStandard, __filename);
        }
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        const result = {
            data: {
                summary: {
                    total_files: summary.total_files,
                    total_dirs: summary.total_dirs,
                    max_depth: summary.max_depth,
                    complexity_level: complexity,
                    empty_dirs_count: summary.empty_dirs.length,
                    empty_dirs: summary.empty_dirs
                }
            },
            metadata: {
                mode: 'summary',
                elapsed_seconds: parseFloat(elapsedTime),
                version: '1.3.0'
            }
        };
        console.log(JSON.stringify(result, null, 2));
    } else {
        const { structure, stats, excludedInfo } = scanProject(
            rootDir,
            options.ignore,
            options.followSymlinks,
            limitFiles === Infinity ? options.maxFiles : limitFiles,
            options.depth,
            options.excludeStandard,
            __filename,
            limitDirs === Infinity ? null : limitDirs,
            options.advancedDirThreshold
        );
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        
        const emptyDirs = (summary && summary.empty_dirs) || [];
        const emptyDirsCount = emptyDirs.length;
        
        if (options.format === 'json') {
            let outputStrategy;
            if (options.noAdaptive || complexity === 'basic') {
                outputStrategy = 'full_tree';
            } else if (complexity === 'medium') {
                outputStrategy = 'limited_files_with_smart_sort';
            } else {
                outputStrategy = 'limited_dirs_and_files_with_smart_judgment';
            }
            
            const result = {
                data: { structure, stats },
                metadata: {
                    mode: 'tree',
                    complexity_level: complexity,
                    output_strategy: outputStrategy,
                    limit_files: options.noAdaptive ? null : options.limitFiles,
                    limit_dirs: (options.noAdaptive || complexity !== 'advanced') ? null : options.limitDirs,
                    empty_dirs_count: emptyDirsCount,
                    empty_dirs: emptyDirs.slice(0, 10),
                    elapsed_seconds: parseFloat(elapsedTime),
                    timeout_threshold: 10,
                    version: '1.3.0',
                    excluded_patterns: excludedInfo,
                    excluded_count: excludedInfo.length
                }
            };
            console.log(JSON.stringify(result, null, 2));
        } else {
            const tree = generateTree(structure);
            console.log(tree.join('\n'));
            console.log(`\nStats: ${stats.files} files, ${stats.dirs} directories`);
            console.log(`Complexity: ${complexity}`);
            if (emptyDirsCount > 0) {
                console.log(`Empty directories: ${emptyDirsCount}`);
            }
            console.log(`Excluded: ${excludedInfo.length} patterns`);
            console.log(`Elapsed: ${elapsedTime}s`);
        }
    }
}

main();
