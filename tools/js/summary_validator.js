/**
 * 文档摘要验证工具 - 验证YAML Frontmatter摘要的格式和完整性
 * 
 * 功能说明:
 *     - 验证YAML Frontmatter格式正确性
 *     - 检查必填字段是否完整
 *     - 验证related_files和dependencies文件是否存在
 *     - 检测摘要是否过期(>90天)
 *     - 提供详细的错误、警告和建议
 * 
 * 使用方法:
 *     // 验证单个文件
 *     node tools/js/summary_validator.js --file dev_docs/api_layer.md
 *     
 *     // 批量验证目录
 *     node tools/js/summary_validator.js --dir dev_docs/
 *     
 *     // 递归验证
 *     node tools/js/summary_validator.js --dir dev_docs/ --recursive
 *     
 *     // 严格模式(警告也视为失败)
 *     node tools/js/summary_validator.js --file dev_docs/api_layer.md --strict
 * 
 * 参数说明:
 *     --file PATH          单个Markdown文件路径
 *     --dir PATH           批量验证目录路径
 *     --recursive          递归扫描子目录
 *     --strict             严格模式,警告也视为失败
 *     --timeout SECONDS    超时时间,默认10秒
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2025-12-03
 *     Purpose: Support 012-Mandatory Document Summary mechanism
 */

const fs = require('fs');
const path = require('path');

const VERSION = "1.0.0";
const DEFAULT_TIMEOUT = 10;
const REQUIRED_FIELDS = ['title', 'summary', 'keywords', 'scope', 'related_files', 'dependencies', 'verified_at'];
const EXPIRY_DAYS = 90;

/**
 * 提取YAML Frontmatter
 */
function extractFrontmatter(content) {
    const pattern = /^---\s*\n(.*?)\n---\s*\n/s;
    const match = content.match(pattern);
    
    if (!match) {
        return null;
    }
    
    const yamlContent = match[1];
    return parseYamlSimple(yamlContent);
}

/**
 * 简单的YAML解析器
 */
function parseYamlSimple(yamlStr) {
    const result = {};
    const lines = yamlStr.trim().split('\n');
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) {
            continue;
        }
        
        if (!trimmed.includes(':')) {
            continue;
        }
        
        const colonIndex = trimmed.indexOf(':');
        const key = trimmed.substring(0, colonIndex).trim();
        let value = trimmed.substring(colonIndex + 1).trim();
        
        if (!value || ['无', 'none', ''].includes(value.toLowerCase())) {
            result[key] = null;
        } else if (value.includes('|')) {
            result[key] = value.split('|').map(item => item.trim()).filter(item => item);
        } else {
            value = value.replace(/^["']|["']$/g, '');
            result[key] = value;
        }
    }
    
    return result;
}

/**
 * 验证日期格式 YYYY-MM-DD
 */
function validateDateFormat(dateStr) {
    const pattern = /^\d{4}-\d{2}-\d{2}$/;
    if (!pattern.test(dateStr)) {
        return false;
    }
    
    try {
        const date = new Date(dateStr);
        return !isNaN(date.getTime());
    } catch {
        return false;
    }
}

/**
 * 检查文件是否存在
 */
function checkFileExists(filePath, baseDir) {
    if (path.isAbsolute(filePath)) {
        return fs.existsSync(filePath);
    } else {
        const fullPath = path.join(baseDir, filePath);
        return fs.existsSync(fullPath);
    }
}

/**
 * 查找项目根目录
 */
function findProjectRoot(filePath) {
    let dir = path.dirname(path.resolve(filePath));
    
    while (dir !== path.dirname(dir)) {  // 直到根目录
        if (fs.existsSync(path.join(dir, 'package.json')) ||
            fs.existsSync(path.join(dir, '.git'))) {
            return dir;
        }
        dir = path.dirname(dir);
    }
    
    return process.cwd();
}

/**
 * 验证单个文件的摘要
 */
function validateSummary(filePath, projectRoot = null) {
    if (!projectRoot) {
        projectRoot = findProjectRoot(filePath);
    }
    
    const result = {
        file: filePath,
        valid: true,
        errors: [],
        warnings: [],
        suggestions: []
    };
    
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const summary = extractFrontmatter(content);
        
        if (!summary) {
            result.valid = false;
            result.errors.push("未找到 YAML Frontmatter");
            return result;
        }
        
        // 检查必填字段
        const missingFields = REQUIRED_FIELDS.filter(field => !(field in summary));
        if (missingFields.length > 0) {
            result.valid = false;
            result.errors.push(`缺少必填字段: ${missingFields.join(', ')}`);
        }
        
        // 检查日期格式
        if (summary.verified_at) {
            if (!validateDateFormat(summary.verified_at)) {
                result.errors.push(`verified_at 日期格式错误,应为 YYYY-MM-DD: ${summary.verified_at}`);
                result.valid = false;
            } else {
                // 检查是否过期
                const verifiedDate = new Date(summary.verified_at);
                const now = new Date();
                const daysOld = Math.floor((now - verifiedDate) / (1000 * 60 * 60 * 24));
                
                if (daysOld > EXPIRY_DAYS) {
                    result.warnings.push(`摘要已过期 ${daysOld} 天 (阈值: ${EXPIRY_DAYS}天)`);
                    result.suggestions.push("建议更新 verified_at 字段");
                }
            }
        }
        
        // 检查related_files文件存在性
        if (summary.related_files && Array.isArray(summary.related_files)) {
            for (const relFile of summary.related_files) {
                if (relFile && relFile !== '无') {
                    if (!checkFileExists(relFile, projectRoot)) {
                        result.warnings.push(`关联文件不存在: ${relFile}`);
                    }
                }
            }
        }
        
        // 检查dependencies文件存在性
        if (summary.dependencies && Array.isArray(summary.dependencies)) {
            for (const depFile of summary.dependencies) {
                if (depFile && depFile !== '无') {
                    if (!checkFileExists(depFile, projectRoot)) {
                        result.warnings.push(`依赖文档不存在: ${depFile}`);
                    }
                }
            }
        }
        
        // 检查字段类型
        for (const field of ['keywords', 'related_files', 'dependencies']) {
            if (summary[field] !== null && summary[field] !== undefined) {
                if (!Array.isArray(summary[field]) && summary[field] !== '无') {
                    result.warnings.push(`${field} 应为列表格式(使用 | 分隔)`);
                }
            }
        }
        
        // 如果有错误,valid为False
        if (result.errors.length > 0) {
            result.valid = false;
        }
        
        return result;
        
    } catch (e) {
        result.valid = false;
        result.errors.push(`验证失败: ${e.message}`);
        return result;
    }
}

/**
 * 查找目录下的所有Markdown文件
 */
function findMarkdownFiles(directory, recursive = false) {
    const mdFiles = [];
    const excludeDirs = new Set(['.git', 'node_modules', '__pycache__', 'dist', 'build']);
    
    function scan(dir) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                if (recursive && !excludeDirs.has(entry.name)) {
                    scan(fullPath);
                }
            } else if (entry.isFile() && entry.name.endsWith('.md')) {
                mdFiles.push(fullPath);
            }
        }
    }
    
    scan(directory);
    return mdFiles;
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    const options = {
        file: null,
        dir: null,
        recursive: false,
        strict: false,
        timeout: DEFAULT_TIMEOUT
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--file': options.file = args[++i]; break;
            case '--dir': options.dir = args[++i]; break;
            case '--recursive': options.recursive = true; break;
            case '--strict': options.strict = true; break;
            case '--timeout': options.timeout = parseInt(args[++i]); break;
        }
    }
    
    // 参数验证
    if (!options.file && !options.dir) {
        console.error("Error: 必须指定 --file 或 --dir 参数");
        process.exit(1);
    }
    
    if (options.file && options.dir) {
        console.error("Error: --file 和 --dir 不能同时使用");
        process.exit(1);
    }
    
    const result = {
        success: true,
        data: {},
        metadata: {
            elapsed_seconds: 0,
            timeout_threshold: options.timeout,
            strict_mode: options.strict,
            version: VERSION
        }
    };
    
    try {
        // 单文件模式
        if (options.file) {
            if (!fs.existsSync(options.file)) {
                result.success = false;
                result.error = `File not found: ${options.file}`;
            } else {
                const validation = validateSummary(options.file);
                result.data = validation;
                
                // 严格模式下,警告也视为失败
                if (options.strict && validation.warnings.length > 0) {
                    result.success = false;
                } else if (!validation.valid) {
                    result.success = false;
                }
            }
        }
        // 批量模式
        else {
            if (!fs.existsSync(options.dir) || !fs.statSync(options.dir).isDirectory()) {
                result.success = false;
                result.error = `Directory not found: ${options.dir}`;
            } else {
                const mdFiles = findMarkdownFiles(options.dir, options.recursive);
                
                const validations = [];
                let totalValid = 0;
                let totalInvalid = 0;
                let totalWarnings = 0;
                
                for (const mdFile of mdFiles) {
                    // 检查超时
                    if ((Date.now() - startTime) / 1000 > options.timeout) {
                        result.warning = "Timeout reached, partial results returned";
                        break;
                    }
                    
                    const validation = validateSummary(mdFile);
                    validations.push(validation);
                    
                    if (validation.valid) {
                        totalValid++;
                    } else {
                        totalInvalid++;
                    }
                    
                    if (validation.warnings) {
                        totalWarnings += validation.warnings.length;
                    }
                }
                
                result.data = {
                    validations: validations,
                    total_files: mdFiles.length,
                    processed: validations.length,
                    valid: totalValid,
                    invalid: totalInvalid,
                    total_warnings: totalWarnings
                };
                
                // 严格模式下,有警告也视为失败
                if (options.strict && totalWarnings > 0) {
                    result.success = false;
                } else if (totalInvalid > 0) {
                    result.success = false;
                }
            }
        }
    } catch (e) {
        result.success = false;
        result.error = e.message;
    }
    
    // 计算耗时
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    result.metadata.elapsed_seconds = parseFloat(elapsedTime);
    
    // 输出JSON
    console.log(JSON.stringify(result, null, 2));
}

main();
