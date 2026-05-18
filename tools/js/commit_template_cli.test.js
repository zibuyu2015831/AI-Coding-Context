/**
 * commit_template_cli.js 单元测试
 * 
 * 测试覆盖：
 * - generateCommitMessage() 格式正确性
 * - 不同 commit 类型的映射
 * - 空输入的默认值处理
 * - 快速模式参数解析
 */

const assert = require('assert');
const { generateCommitMessage, parseArgs, calculateQualityScore } = require('./commit_template_cli.js');

// 测试套件
function runTests() {
    console.log('🧪 开始运行 commit_template_cli.js 单元测试...\n');
    
    let passed = 0;
    let failed = 0;
    
    // 测试 1: generateCommitMessage() 基本格式
    try {
        console.log('测试 1: generateCommitMessage() 应该生成正确的格式');
        const message = generateCommitMessage(
            'feature',
            '添加用户登录',
            '满足业务需求',
            ['实现登录API', '添加前端表单']
        );
        
        assert.ok(message.includes('prompt(feature): 添加用户登录'), '应包含标题行');
        assert.ok(message.includes('WHAT: 添加用户登录'), '应包含 WHAT 字段');
        assert.ok(message.includes('WHY: 满足业务需求'), '应包含 WHY 字段');
        assert.ok(message.includes('HOW:'), '应包含 HOW 标题');
        assert.ok(message.includes('- 实现登录API'), '应包含 HOW 第一项');
        assert.ok(message.includes('- 添加前端表单'), '应包含 HOW 第二项');
        
        console.log('✅ 测试 1 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 1 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 2: 不同 commit 类型
    try {
        console.log('测试 2: 应该支持不同的 commit 类型');
        const types = ['feature', 'fix', 'architecture', 'other'];
        
        for (const type of types) {
            const message = generateCommitMessage(type, 'test', 'test', []);
            assert.ok(message.includes(`prompt(${type}):`), `应包含类型 ${type}`);
        }
        
        console.log('✅ 测试 2 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 2 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 3: 空 HOW 列表
    try {
        console.log('测试 3: 应该正确处理空 HOW 列表');
        const message = generateCommitMessage('feature', 'test', 'test', []);
        
        assert.ok(message.includes('HOW:\n'), '应包含 HOW 标题');
        assert.ok(!message.includes('- '), '不应包含列表项');
        
        console.log('✅ 测试 3 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 3 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 4: parseArgs() 基本参数解析
    try {
        console.log('测试 4: parseArgs() 应该正确解析命令行参数');
        const args = parseArgs(['--quick', '--type', 'fix', '--what', 'test what', '--why', 'test why', '--how', 'step1,step2']);
        
        assert.strictEqual(args.quick, true, 'quick 应为 true');
        assert.strictEqual(args.type, 'fix', 'type 应为 fix');
        assert.strictEqual(args.what, 'test what', 'what 应正确');
        assert.strictEqual(args.why, 'test why', 'why 应正确');
        assert.strictEqual(args.how, 'step1,step2', 'how 应正确');
        
        console.log('✅ 测试 4 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 4 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 5: parseArgs() 帮助参数
    try {
        console.log('测试 5: parseArgs() 应该识别帮助参数');
        const args1 = parseArgs(['--help']);
        const args2 = parseArgs(['-h']);
        
        assert.strictEqual(args1.help, true, '--help 应设置 help 为 true');
        assert.strictEqual(args2.help, true, '-h 应设置 help 为 true');
        
        console.log('✅ 测试 5 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 5 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 6: parseArgs() 默认值
    try {
        console.log('测试 6: parseArgs() 应该使用正确的默认值');
        const args = parseArgs([]);
        
        assert.strictEqual(args.help, false, 'help 默认为 false');
        assert.strictEqual(args.quick, false, 'quick 默认为 false');
        assert.strictEqual(args.type, 'feature', 'type 默认为 feature');
        assert.strictEqual(args.what, null, 'what 默认为 null');
        assert.strictEqual(args.why, null, 'why 默认为 null');
        assert.strictEqual(args.how, null, 'how 默认为 null');
        
        console.log('✅ 测试 6 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 6 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 7: 消息格式的换行符
    try {
        console.log('测试 7: 生成的消息应该包含正确的换行符');
        const message = generateCommitMessage('feature', 'test', 'test', ['step1']);
        const lines = message.split('\n');
        
        assert.ok(lines.length >= 5, '应该有至少 5 行');
        assert.ok(lines[0].startsWith('prompt('), '第一行应该是标题');
        assert.strictEqual(lines[1], '', '第二行应该是空行');
        assert.ok(lines[2].startsWith('WHAT:'), '第三行应该是 WHAT');
        
        console.log('✅ 测试 7 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 7 失败: ${error.message}\n`);
        failed++;
    }
    
    // 测试 8: 特殊字符处理
    try {
        console.log('测试 8: 应该正确处理特殊字符');
        const message = generateCommitMessage(
            'feature',
            '添加"引号"测试',
            '包含\'单引号\'',
            ['步骤1: 测试', '步骤2: 验证']
        );
        
        assert.ok(message.includes('添加"引号"测试'), '应保留双引号');
        assert.ok(message.includes('包含\'单引号\''), '应保留单引号');
        assert.ok(message.includes('步骤1: 测试'), '应保留冒号');
        
        console.log('✅ 测试 8 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 8 失败: ${error.message}\n`);
        failed++;
    }

    // 测试 9: 质量评分解析
    try {
        console.log('测试 9: calculateQualityScore() 应该正确解析多行 commit message');
        const message = generateCommitMessage(
            'feature',
            '添加用户登录功能',
            '满足业务需求提升用户体验',
            ['实现登录API', '添加前端表单', '集成认证系统']
        );
        const score = calculateQualityScore(message);
        assert.ok(score, '评分结果不应为空');
        assert.ok(score.breakdown.why_depth > 0, 'WHY 评分应大于 0');
        assert.ok(score.breakdown.how_completeness > 0, 'HOW 评分应大于 0');

        console.log('✅ 测试 9 通过\n');
        passed++;
    } catch (error) {
        console.log(`❌ 测试 9 失败: ${error.message}\n`);
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
