/**
 * 时间戳分析工具 - 采集项目文件和文档的修改时间供 AI 分析文档健康度
 * 
 * 用法:
 *   node tools/js/timestamp_analyzer.js [--project-root ./] [--max-files 5000]
 * 
 * 输出:
 *   {
 *     "data": {
 *       "project_files": [{"path": "src/api/user.ts", "modified_at": "2025-12-01T15:30:00"}],
 *       "doc_files": [{"path": "dev_docs/api_layer.md", "modified_at": "2025-11-10T16:00:00"}],
 *       "stats": {"total_project_files": 245, "total_doc_files": 8}
 *     },
 *     "metadata": {"elapsed_seconds": 2.1, "timeout_threshold": 10, "version": "1.1.0"}
 *   }
 */

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
            // Ignore
        }
    }
    return patterns;
}

function shouldIgnore(relPath, patterns) {
    // 始终忽略这些目录
    const ignoredDirs = new Set(['.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'venv']);
    
    const parts = relPath.split(path.sep);
    if (parts.some(part => ignoredDirs.has(part))) {
        return true;
    }
    
    // 简化的 gitignore 匹配
    for (const pattern of patterns) {
        if (relPath.includes(pattern) || relPath.startsWith(pattern.replace('/', ''))) {
            return true;
        }
    }
    
    return false;
}

function getFileTimestamp(filePath) {
    try {
        const stats = fs.statSync(filePath);
        return stats.mtime.toISOString();
    } catch (e) {
        return null;
    }
}

function scanDirectory(rootDir, patterns, maxFiles) {
    const projectFiles = [];
    const docFiles = [];
    let scannedCount = 0;
    
    function walk(currentPath) {
        if (scannedCount >= maxFiles) return;
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) {
            return;
        }
        
        for (const entry of entries) {
            if (scannedCount >= maxFiles) break;
            
            const fullPath = path.join(currentPath, entry);
            const relPath = path.relative(rootDir, fullPath);
            
            if (shouldIgnore(relPath, patterns)) continue;
            
            let stats;
            try {
                stats = fs.statSync(fullPath);
            } catch (e) {
                continue;
            }
            
            if (stats.isDirectory()) {
                walk(fullPath);
            } else {
                const modifiedAt = getFileTimestamp(fullPath);
                if (!modifiedAt) continue;
                
                const fileInfo = {
                    path: relPath.split(path.sep).join('/'),
                    modified_at: modifiedAt
                };
                
                // 判断是文档还是项目文件
                if (relPath.startsWith('dev_docs' + path.sep) || entry.endsWith('.md')) {
                    docFiles.push(fileInfo);
                } else {
                    projectFiles.push(fileInfo);
                }
                
                scannedCount++;
            }
        }
    }
    
    walk(rootDir);
    return { projectFiles, docFiles };
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        projectRoot: './',
        maxFiles: 5000
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--project-root': options.projectRoot = args[++i]; break;
            case '--max-files': options.maxFiles = parseInt(args[++i]); break;
        }
    }
    
    const rootDir = path.resolve(options.projectRoot);
    const patterns = loadGitignorePatterns(rootDir);
    
    const { projectFiles, docFiles } = scanDirectory(rootDir, patterns, options.maxFiles);
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    
    const result = {
        data: {
            project_files: projectFiles,
            doc_files: docFiles,
            stats: {
                total_project_files: projectFiles.length,
                total_doc_files: docFiles.length,
                scan_time: new Date().toISOString()
            }
        },
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

main();
