const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function runRipgrep(query, rootPath, includes, excludes, isRegex, timeout) {
    const args = ["--json", "--line-number", "--heading", "--color=never"];
    
    if (!isRegex) {
        args.push("--fixed-strings");
    }
    
    if (includes) {
        includes.forEach(inc => args.push("--glob", inc));
    }
    
    if (excludes) {
        excludes.forEach(exc => args.push("--glob", `!${exc}`));
    }
    
    args.push(query);
    args.push(rootPath);
    
    try {
        const result = spawnSync("rg", args, { 
            timeout: timeout * 1000, 
            encoding: 'utf-8',
            maxBuffer: 1024 * 1024 * 10 // 10MB buffer
        });
        
        if (result.error) {
            if (result.error.code === 'ENOENT') return null; // rg not found
            if (result.error.code === 'ETIMEDOUT') return { error: "Search timed out (rg)" };
            return { error: result.error.message };
        }
        
        const matches = [];
        if (result.status === 0) {
            const lines = result.stdout.split('\n');
            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    if (data.type === "match") {
                        matches.push({
                            file: data.data.path.text,
                            line: data.data.line_number,
                            content: data.data.lines.text.trim()
                        });
                    }
                } catch (e) { continue; }
            }
        }
        return matches;
    } catch (e) {
        return { error: e.message };
    }
}

// Simple glob matcher
function matchGlob(str, pattern) {
    let regexStr = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    regexStr = regexStr.replace(/\*/g, '.*').replace(/\?/g, '.');
    return new RegExp(`^${regexStr}$`).test(str);
}

function fallbackSearch(query, rootPath, includes, excludes, isRegex, timeout) {
    const matches = [];
    const startTime = Date.now();
    const timeoutMs = timeout * 1000;
    
    let regex;
    try {
        regex = isRegex ? new RegExp(query) : null;
    } catch (e) {
        return { error: `Invalid regex: ${e.message}` };
    }
    
    function walk(currentPath) {
        if (Date.now() - startTime > timeoutMs) throw new Error("Search timed out (fallback)");
        
        let entries;
        try {
            entries = fs.readdirSync(currentPath);
        } catch (e) { return; }
        
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry);
            const relPath = path.relative(rootPath, fullPath);
            const name = entry;
            
            // Handle excludes
            if (excludes && excludes.some(exc => matchGlob(name, exc) || matchGlob(relPath, exc))) continue;
            
            let stat;
            try {
                stat = fs.statSync(fullPath);
            } catch (e) { continue; }
            
            if (stat.isDirectory()) {
                walk(fullPath);
            } else {
                // Handle includes
                if (includes && !includes.some(inc => matchGlob(name, inc) || matchGlob(relPath, inc))) continue;
                
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const lines = content.split(/\r\n|\r|\n/);
                    
                    lines.forEach((line, index) => {
                        let found = false;
                        if (isRegex) {
                            if (regex.test(line)) found = true;
                        } else {
                            if (line.includes(query)) found = true;
                        }
                        
                        if (found) {
                            matches.push({
                                file: fullPath,
                                line: index + 1,
                                content: line.trim()
                            });
                        }
                    });
                } catch (e) { continue; }
            }
        }
    }
    
    try {
        walk(rootPath);
        return matches;
    } catch (e) {
        if (e.message === "Search timed out (fallback)") return { error: e.message };
        return { error: e.message };
    }
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        query: '',
        path: '.',
        include: [],
        exclude: [],
        regex: false,
        timeout: 5
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--query': options.query = args[++i]; break;
            case '--path': options.path = args[++i]; break;
            case '--include': options.include = args[++i].split(','); break;
            case '--exclude': options.exclude = args[++i].split(','); break;
            case '--regex': options.regex = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    if (!options.query) {
        console.error("Error: --query is required");
        process.exit(1);
    }
    
    let matches = runRipgrep(
        options.query, 
        options.path, 
        options.include, 
        options.exclude, 
        options.regex, 
        options.timeout
    );
    
    if (matches === null) {
        matches = fallbackSearch(
            options.query, 
            options.path, 
            options.include, 
            options.exclude, 
            options.regex, 
            options.timeout
        );
    }
    
    if (matches.error) {
        console.log(JSON.stringify(matches));
    } else {
        console.log(JSON.stringify({ matches: matches }, null, 2));
    }
}

main();
