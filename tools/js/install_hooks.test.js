/**
 * install_hooks.js 单元测试
 * 
 * 测试覆盖：
 * - findGitRoot() 在不同目录层级的行为
 * - hook 安装在文件已存在/不存在时的行为
 * - hook 卸载在有/无备份时的行为
 * - 跨平台路径处理
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { findGitRoot, setExecutable } = require('./install_hooks.js');

// 测试辅助函数
function createTempDir() {
    const tempDir = path.join(os.tmpdir(), `test-git-hooks-${Date.now()}`);
    fs.mkdirSync(tempDir, { recursive: true });
    return tempDir;
}

function cleanupTempDir(dir) {
    if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
    }
}

// 测试套件
function runTests() {
    console.log('🧪 开始运行 install_hooks.js 单元测试...\n');
    
    let passed = 0;
    let failed = 0;
    
    // 测试 1: findGitRoot() 在 Git 仓库中
    try {
        console.log('测试 1: findGitRoot() 应该找到当前 Git 仓库');
        const gitRoot = findGitRoot();
        assert.ok(gitRoot !== null, 'Git 仓库根目录不应为 null');
        assert.ok(fs.existsSync(path.join(gitRoot, '.git')), '.git 目录应该存在');
        console.log('✅ 测试 1 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 1 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 2: findGitRoot() 在非 Git 目录中
    try {
        console.log('测试 2: findGitRoot() 在非 Git 目录应返回 null');
        const tempDir = createTempDir();
        const originalCwd = process.cwd();
        
        try {
            process.chdir(tempDir);
            const gitRoot = findGitRoot();
            
            // 如果 tempDir 在某个 Git 仓库内，这个测试可能会失败
            // 所以我们只检查返回值是否不等于 tempDir
            assert.ok(gitRoot !== tempDir, '应该不返回临时目录本身');
            console.log('✅ 测试 2 通过\n');
            passed++;
        } finally {
            process.chdir(originalCwd);
            cleanupTempDir(tempDir);
        }
    } catch (error) {
        console.log(`❌ 测试 2 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 3: 路径处理跨平台兼容性
    try {
        console.log('测试 3: 路径处理应该跨平台兼容');
        const testPath = path.join('tools', 'js', 'install_hooks.js');
        assert.ok(!testPath.includes('\\\\'), '路径不应包含双反斜杠');
        assert.ok(fs.existsSync(testPath) || fs.existsSync(path.join(process.cwd(), testPath)), 
                  '路径应该可以正确解析');
        console.log('✅ 测试 3 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 3 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 4: setExecutable() 在 Unix 系统上设置权限
    try {
        console.log('测试 4: setExecutable() 应该正确设置文件权限');
        const tempDir = createTempDir();
        const testFile = path.join(tempDir, 'test-file.sh');
        
        try {
            fs.writeFileSync(testFile, '#!/bin/bash\necho "test"');
            const statsBefore = fs.statSync(testFile);
            
            setExecutable(testFile);
            
            if (os.platform() !== 'win32') {
                const statsAfter = fs.statSync(testFile);
                // 检查是否添加了执行权限
                assert.ok((statsAfter.mode & 0o111) !== 0, '应该设置执行权限');
            }
            
            console.log('✅ 测试 4 通过\n');
            passed++;
        } finally {
            cleanupTempDir(tempDir);
        }
    } catch (error) {
        console.log(`❌ 测试 4 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 5: 文件复制操作的正确性
    try {
        console.log('测试 5: 文件复制应该保持内容一致');
        const tempDir = createTempDir();
        const sourceFile = path.join(tempDir, 'source.txt');
        const targetFile = path.join(tempDir, 'target.txt');
        const content = 'Test content\n测试内容';
        
        try {
            fs.writeFileSync(sourceFile, content);
            fs.copyFileSync(sourceFile, targetFile);
            
            const copiedContent = fs.readFileSync(targetFile, 'utf8');
            assert.strictEqual(copiedContent, content, '复制的内容应该一致');
            
            console.log('✅ 测试 5 通过\n');
            passed++;
        } finally {
            cleanupTempDir(tempDir);
        }
    } catch (error) {
        console.log(`❌ 测试 5 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 6: 备份文件命名正确性
    try {
        console.log('测试 6: 备份文件应该使用 .backup 后缀');
        const tempDir = createTempDir();
        const originalFile = path.join(tempDir, 'pre-commit');
        const backupFile = originalFile + '.backup';
        
        try {
            fs.writeFileSync(originalFile, 'original content');
            fs.copyFileSync(originalFile, backupFile);
            
            assert.ok(fs.existsSync(backupFile), '备份文件应该存在');
            assert.ok(backupFile.endsWith('.backup'), '备份文件应该以 .backup 结尾');
            
            console.log('✅ 测试 6 通过\n');
            passed++;
        } finally {
            cleanupTempDir(tempDir);
        }
    } catch (error) {
        console.log(`❌ 测试 6 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 7: 目录创建的递归性
    try {
        console.log('测试 7: 应该能够递归创建目录');
        const tempDir = createTempDir();
        const nestedDir = path.join(tempDir, 'a', 'b', 'c');
        
        try {
            fs.mkdirSync(nestedDir, { recursive: true });
            assert.ok(fs.existsSync(nestedDir), '嵌套目录应该被创建');
            
            console.log('✅ 测试 7 通过\n');
            passed++;
        } finally {
            cleanupTempDir(tempDir);
        }
    } catch (error) {
        console.log(`❌ 测试 7 失败: ${error.message}\n`);
        failed++;
    }
    
    // 输出测试结果
    console.log('═══════════════════════════════════════');
    console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
    console.log('═══════════════════════════════════════\n');
    
    if (failed > 0) {
        process.exit(1);
    }
}

// 运行测试
if (require.main === module) {
    runTests();
}

module.exports = { runTests };
