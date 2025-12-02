/**
 * 环境诊断工具 - 检测 Python 和 Node.js 运行环境
 * 
 * 功能说明：
 * - 检测 Python 版本和可用性
 * - 检测 Node.js 版本和可用性
 * - 识别操作系统类型
 * - 验证版本是否满足最低要求
 * 
 * 使用方法：
 *   node tools/js/env_diagnosis.js
 * 
 * 参数说明：
 *   无参数
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "python": {
 *         "version": "版本号",
 *         "ok": 是否满足要求(bool)
 *       },
 *       "node": {
 *         "version": "版本号",
 *         "path": "可执行文件路径",
 *         "ok": 是否满足要求(bool)
 *       },
 *       "os": "操作系统信息"
 *     },
 *     "metadata": {
 *       "elapsed_seconds": 耗时(秒),
 *       "timeout_threshold": 10,
 *       "version": "1.1.0"
 *     }
 *   }
 * 
 * 使用示例：
 *   // 检测当前环境
 *   node tools/js/env_diagnosis.js
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2025-12-02
 */

const { execSync } = require('child_process');
const os = require('os');

function checkPythonVersion() {
    try {
        const stdout = execSync("python --version", { encoding: 'utf8' }).trim();
        return stdout;
    } catch (e) {
        try {
             const stdout = execSync("python3 --version", { encoding: 'utf8' }).trim();
             return stdout;
        } catch (e2) {
            return null;
        }
    }
}

function main() {
    const startTime = Date.now();
    
    const nodeVersion = process.version;
    const pythonVersion = checkPythonVersion();
    const osInfo = `${os.type()} ${os.release()}`;
    
    const status = {
        python: {
            version: pythonVersion,
            ok: false
        },
        node: {
            version: nodeVersion,
            path: process.execPath,
            ok: false
        },
        os: osInfo
    };
    
    // Check Node version (>=14)
    const nodeMajor = parseInt(nodeVersion.substring(1).split('.')[0]);
    status.node.ok = nodeMajor >= 14;
    
    // Check Python version (>=3.6)
    if (pythonVersion) {
        const parts = pythonVersion.split(' ')[1].split('.');
        const major = parseInt(parts[0]);
        const minor = parseInt(parts[1]);
        status.python.ok = (major > 3) || (major === 3 && minor >= 6);
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    const result = {
        data: status,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            timeout_threshold: 10,
            version: "1.1.0"
        }
    };
    console.log(JSON.stringify(result, null, 2));
}

main();
