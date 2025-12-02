/**
 * 文件读取工具 - 安全地读取文件内容（支持大文件分页）
 * 
 * 功能说明：
 * - 自动检测二进制文件并跳过
 * - 自动尝试多种编码（utf8, latin1）
 * - 支持按行分页读取大文件
 * - 统计总行数并标识是否截断
 * 
 * 使用方法：
 *   node tools/js/file_reader.js --path "文件路径" [选项]
 * 
 * 参数说明：
 *   --path PATH              要读取的文件路径（必需）
 *   --offset NUM             起始行号（0-indexed，默认：0）
 *   --limit NUM              最多读取行数（默认：1000）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "content": "文件内容（字符串）",
 *       "lines_read": 读取的行数,
 *       "total_lines": 文件总行数,
 *       "truncated": 是否被截断(bool),
 *       "is_binary": 是否为二进制文件(bool),
 *       "encoding": "使用的编码"
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   // 读取文件前 50 行
 *   node tools/js/file_reader.js --path ./README.md --limit 50
 * 
 *   // 读取第 100-200 行
 *   node tools/js/file_reader.js --path ./log.txt --offset 100 --limit 100
 * 
 *   // 读取整个文件
 *   node tools/js/file_reader.js --path ./config.json
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2025-12-02
 */

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
    const startTime = Date.now();
    
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
    
    const fileData = readFile(options.path, options.offset, options.limit);
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    const result = {
        data: fileData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        }
    };
    console.log(JSON.stringify(result, null, 2));
}

main();
