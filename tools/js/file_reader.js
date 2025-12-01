const fs = require('fs');

function isBinaryFile(filePath, chunkSize = 1024) {
    try {
        const fd = fs.openSync(filePath, 'r');
        const buffer = Buffer.alloc(chunkSize);
        const bytesRead = fs.readSync(fd, buffer, 0, chunkSize, 0);
        fs.closeSync(fd);
        
        for (let i = 0; i < bytesRead; i++) {
            if (buffer[i] === 0) return true;
        }
        return false;
    } catch (e) {
        return false;
    }
}

function countLines(filePath, encoding) {
    try {
        const content = fs.readFileSync(filePath, { encoding: encoding });
        return content.split(/\r\n|\r|\n/).length;
    } catch (e) {
        return 0;
    }
}

function readFile(filePath, offset, limit) {
    if (!fs.existsSync(filePath)) {
        return { error: `File not found: ${filePath}` };
    }
    
    if (isBinaryFile(filePath)) {
        return {
            content: null,
            lines_read: 0,
            total_lines: 0,
            truncated: false,
            is_binary: true
        };
    }
    
    const encodings = ['utf8', 'latin1'];
    let content = "";
    let linesRead = 0;
    let totalLines = 0;
    let encodingUsed = null;
    
    for (const enc of encodings) {
        try {
            const fileContent = fs.readFileSync(filePath, { encoding: enc });
            const lines = fileContent.split(/\r\n|\r|\n/);
            totalLines = lines.length;
            
            const selectedLines = lines.slice(offset, offset + limit);
            content = selectedLines.join('\n');
            linesRead = selectedLines.length;
            encodingUsed = enc;
            break;
        } catch (e) {
            continue;
        }
    }
    
    if (!encodingUsed) {
        return {
            content: null,
            lines_read: 0,
            total_lines: 0,
            truncated: false,
            is_binary: true,
            note: "Failed to decode text with common encodings"
        };
    }
    
    const truncated = (offset + linesRead) < totalLines;
    
    return {
        content: content,
        lines_read: linesRead,
        total_lines: totalLines,
        truncated: truncated,
        is_binary: false,
        encoding: encodingUsed
    };
}

function main() {
    const args = process.argv.slice(2);
    const options = {
        path: '',
        offset: 0,
        limit: 1000
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--path': options.path = args[++i]; break;
            case '--offset': options.offset = parseInt(args[++i]); break;
            case '--limit': options.limit = parseInt(args[++i]); break;
        }
    }
    
    if (!options.path) {
        console.error("Error: --path is required");
        process.exit(1);
    }
    
    const result = readFile(options.path, options.offset, options.limit);
    console.log(JSON.stringify(result, null, 2));
}

main();
