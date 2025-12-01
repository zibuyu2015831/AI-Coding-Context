const fs = require('fs');
const path = require('path');

// Simple glob matcher
function matchGlob(str, pattern) {
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    return new RegExp(`^${regexStr}$`).test(str);
}

function findFiles(rootPath, pattern, limit) {
    const matches = [];
    
    function walk(currentPath) {
        if (limit && matches.length >= limit) return;
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) { return; }
        
        for (const entry of entries) {
            if (limit && matches.length >= limit) return;
            
            const fullPath = path.join(currentPath, entry);
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                walk(fullPath);
            } else {
                if (matchGlob(entry, pattern)) {
                    matches.push(fullPath);
                }
            }
        }
    }
    
    walk(rootPath);
    return matches;
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        pattern: '',
        path: '.',
        limit: undefined
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--pattern': options.pattern = args[++i]; break;
            case '--path': options.path = args[++i]; break;
            case '--limit': options.limit = parseInt(args[++i]); break;
        }
    }
    
    if (!options.pattern) {
        console.error("Error: --pattern is required");
        process.exit(1);
    }
    
    const files = findFiles(options.path, options.pattern, options.limit);
    console.log(JSON.stringify({ files: files }, null, 2));
}

main();
