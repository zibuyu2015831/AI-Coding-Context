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
    const nodeVersion = process.version;
    const pythonVersion = checkPythonVersion();
    const osInfo = `${os.type()} ${os.release()}`;
    
    const status = {
        python: {
            version: pythonVersion,
            ok: false // Will be updated if python is found and version is sufficient
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
    
    console.log(JSON.stringify(status, null, 2));
}

main();
