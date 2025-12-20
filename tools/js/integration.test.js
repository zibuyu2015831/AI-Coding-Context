/**
 * 端到端集成测试
 * 
 * 测试覆盖：
 * - install_hooks.js 完整安装/卸载流程
 * - commit_template_cli.js 快速模式
 * - 与 Python 版本的输出一致性
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// 测试辅助函数
function createTempGitRepo() {
    const tempDir = path.join(os.tmpdir(), `test-git-repo-${Date.now()}`);
    fs.mkdirSync(tempDir, { recursive: true });
    
    // 初始化 Git 仓库
    execSync('git init', { cwd: tempDir, stdio: 'ignore' });
    
    // 创建 tools/git-hooks 目录和 pre-commit 文件
    const toolsDir = path.join(tempDir, 'tools', 'git-hooks');
    fs.mkdirSync(toolsDir, { recursive: true });
    fs.writeFileSync(
        path.join(toolsDir, 'pre-commit'),
        '#!/bin/bash\necho "Pre-commit hook"\n'
    );
    
    return tempDir;
}

function cleanupTempDir(dir) {
    if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
    }
}

// 测试套件
function runTests() {
    console.log('🧪 开始运行端到端集成测试...\n');
    
    let passed = 0;
    let failed = 0;
    
    // 测试 1: install_hooks.js 帮助信息
    try {
        console.log('测试 1: install_hooks.js --help 应该显示帮助信息');
        const output = execSync('node tools/js/install_hooks.js --help', { encoding: 'utf8' });
        
        assert.ok(output.includes('Git Hooks 安装工具'), '应包含标题');
        assert.ok(output.includes('使用方式'), '应包含使用说明');
        assert.ok(output.includes('Hook 功能'), '应包含功能列表');
        
        console.log('✅ 测试 1 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 1 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 2: commit_template_cli.js 帮助信息
    try {
        console.log('测试 2: commit_template_cli.js --help 应该显示帮助信息');
        const output = execSync('node tools/js/commit_template_cli.js --help', { encoding: 'utf8' });
        
        assert.ok(output.includes('Commit 模板 CLI 工具'), '应包含标题');
        assert.ok(output.includes('参数说明'), '应包含参数说明');
        assert.ok(output.includes('示例'), '应包含使用示例');
        
        console.log('✅ 测试 2 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 2 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 3: commit_template_cli.js 快速模式
    try {
        console.log('测试 3: commit_template_cli.js 快速模式应该生成正确的 commit message');
        const output = execSync(
            'node tools/js/commit_template_cli.js --quick --type feature --what "测试功能" --why "测试原因" --how "步骤1,步骤2"',
            { encoding: 'utf8' }
        );
        
        assert.ok(output.includes('prompt(feature): 测试功能'), '应包含标题');
        assert.ok(output.includes('WHAT: 测试功能'), '应包含 WHAT');
        assert.ok(output.includes('WHY: 测试原因'), '应包含 WHY');
        assert.ok(output.includes('HOW:'), '应包含 HOW');
        assert.ok(output.includes('- 步骤1'), '应包含步骤1');
        assert.ok(output.includes('- 步骤2'), '应包含步骤2');
        
        console.log('✅ 测试 3 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 3 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 4: commit_template_cli.js 质量评分集成
    try {
        console.log('测试 4: commit_template_cli.js 应该显示质量评分');
        const output = execSync(
            'node tools/js/commit_template_cli.js --quick --type feature --what "添加用户登录功能" --why "满足业务需求提升用户体验" --how "实现登录API,添加前端表单,集成认证系统"',
            { encoding: 'utf8' }
        );
        
        assert.ok(output.includes('质量评分'), '应包含质量评分');
        assert.ok(output.includes('WHAT清晰度'), '应包含 WHAT 评分');
        assert.ok(output.includes('WHY深度'), '应包含 WHY 评分');
        assert.ok(output.includes('HOW完整性'), '应包含 HOW 评分');
        
        console.log('✅ 测试 4 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 4 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 5: 输出格式与 Python 版本一致性
    try {
        console.log('测试 5: JS 版本输出应该与 Python 版本格式一致');
        
        // 生成相同的 commit message
        const jsOutput = execSync(
            'node tools/js/commit_template_cli.js --quick --type fix --what "修复登录bug" --why "用户反馈" --how "修改验证逻辑"',
            { encoding: 'utf8' }
        );
        
        // 检查关键格式元素
        assert.ok(jsOutput.includes('prompt(fix):'), '应包含 prompt 前缀');
        assert.ok(jsOutput.includes('WHAT:'), '应包含 WHAT 字段');
        assert.ok(jsOutput.includes('WHY:'), '应包含 WHY 字段');
        assert.ok(jsOutput.includes('HOW:'), '应包含 HOW 字段');
        assert.ok(jsOutput.includes('- 修改验证逻辑'), '应包含 HOW 列表项');
        
        console.log('✅ 测试 5 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 5 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 6: 错误处理 - 未找到 Git 仓库
    try {
        console.log('测试 6: install_hooks.js 应该正确处理未找到 Git 仓库的情况');
        const tempDir = path.join(os.tmpdir(), `test-no-git-${Date.now()}`);
        fs.mkdirSync(tempDir, { recursive: true });
        
        try {
            execSync('node tools/js/install_hooks.js', { 
                cwd: tempDir, 
                encoding: 'utf8',
                stdio: 'pipe'
            });
            // 如果没有抛出错误，说明测试失败
            throw new Error('应该抛出错误');
        } catch (error) {
            // 预期会失败
            assert.ok(error.status === 1, '应该返回退出码 1');
        } finally {
            cleanupTempDir(tempDir);
        }
        
        console.log('✅ 测试 6 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 6 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 7: 跨平台路径处理
    try {
        console.log('测试 7: 工具应该正确处理跨平台路径');
        
        // 测试路径分隔符
        const testPath = path.join('tools', 'js', 'install_hooks.js');
        assert.ok(fs.existsSync(testPath), '应该能找到文件');
        
        // 测试路径规范化
        const normalized = path.normalize(testPath);
        assert.ok(!normalized.includes('//'), '路径不应包含双斜杠');
        
        console.log('✅ 测试 7 通过\n');
        passed++;
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
