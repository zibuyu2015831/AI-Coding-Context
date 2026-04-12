#!/usr/bin/env node
/**
复杂度通知工具 - Node.js 版本
用于发送复杂度报告通知
作为 005 优化点的补充工具

功能说明:
- 发送 Slack 通知（严重警告级别）
- 发送 Email 通知（每日报告和严重警告）
- 支持 CI/CD 集成

使用方法:
    node tools/js/notifier.js [--data DATA] [--level LEVEL] [--channel CHANNEL]

参数说明:
    --data DATA              输入数据文件路径（JSON 格式）
    --level LEVEL            通知级别（info/warning/critical，默认：warning）
    --channel CHANNEL        Slack 通知频道（默认：#dev-complexity）
    --email EMAIL            Email 通知地址
    --webhook URL            Slack Webhook URL
    --subject SUBJECT        Email 主题
    --template TEMPLATE      通知模板路径

使用示例:
    # 发送 Slack 通知
    node tools/js/notifier.js --data data.json --level critical --channel #dev-alerts

    # 发送 Email 通知
    node tools/js/notifier.js --data data.json --email dev@example.com

版本信息:
    版本：1.0.0
    更新日期：2026-04-12
*/

const fs = require('fs');
const path = require('path');

// 帮助信息
function showHelp() {
    console.log(`
复杂度通知工具 - Node.js 版本
用于发送复杂度报告通知

使用方法:
    node tools/js/notifier.js [--data DATA] [--level LEVEL] [--channel CHANNEL]

参数说明:
    --data DATA              输入数据文件路径（JSON 格式）
    --level LEVEL            通知级别（info/warning/critical，默认：warning）
    --channel CHANNEL        Slack 通知频道（默认：#dev-complexity）
    --email EMAIL            Email 通知地址
    --webhook URL            Slack Webhook URL
    --subject SUBJECT        Email 主题
    --help, -h              显示此帮助信息

使用示例:
    # 发送 Slack 通知
    node tools/js/notifier.js --data data.json --level critical --channel #dev-alerts

    # 发送 Email 通知
    node tools/js/notifier.js --data data.json --email dev@example.com

版本信息:
    版本：1.0.0
    更新日期：2026-04-12
`);
}

// 加载复杂度数据
function loadData(dataPath) {
    try {
        const content = fs.readFileSync(dataPath, 'utf8');
        return JSON.parse(content);
    } catch (error) {
        console.error('Error loading data:', error.message);
        return null;
    }
}

// 生成通知文本
function generateNotificationText(data, level) {
    const complexityData = data.data || {};
    const riskAssessment = complexityData.risk_assessment || {};
    const codeSize = complexityData.code_size || {};
    const codeQuality = complexityData.code_quality || {};

    const overallScore = riskAssessment.overall_score || 0;
    const risks = riskAssessment.risks || [];

    // 风险等级图标
    const levelEmoji = {
        info: '📊',
        warning: '⚠️',
        critical: '🚨'
    }[level] || '📊';

    let text = `${levelEmoji} 项目复杂度报告\n\n`;
    text += `📅 生成时间: ${new Date().toLocaleString('zh-CN')}\n`;
    text += `🎯 整体风险评分: ${overallScore.toFixed(0)}/100\n\n`;

    // 关键指标
    text += '📈 关键指标:\n';
    text += `  - 新增代码: ${codeSize.new_lines || 0} 行\n`;
    text += `  - 代码质量: ${codeQuality.quality_score || 0}/100\n`;
    text += `  - 增长比例: ${(codeSize.growth_percentage || 0).toFixed(1)}%\n\n`;

    // 风险项
    if (risks.length > 0) {
        text += '⚠️ 风险项:\n';
        risks.forEach(risk => {
            const riskLevelEmoji = {
                high: '🔴',
                medium: '🟡',
                low: '🟢'
            }[risk.level] || '🟢';
            text += `  ${riskLevelEmoji} ${risk.message}\n`;
        });
        text += '\n';
    }

    // 行动建议
    if (level === 'critical') {
        text += '🛠️ 请立即查看详细报告并处理问题！\n';
    }

    return text;
}

// 发送 Slack 通知
function sendSlackNotification(text, webhookUrl, channel) {
    try {
        // 这里使用简单的实现，实际生产环境可能需要使用第三方库
        // 由于我们要保持零依赖，这里只打印通知内容
        console.log(`📤 Slack 通知 (频道: ${channel}):`);
        console.log('-'.repeat(50));
        console.log(text);
        console.log('-'.repeat(50));

        // 提示用户如何配置实际的 Slack Webhook
        console.log('\n💡 提示: 要启用实际的 Slack 通知，请:');
        console.log('   1. 创建 Slack Webhook');
        console.log('   2. 使用 --webhook 参数传入 URL');
        console.log('   3. 安装 axios 或其他 HTTP 库进行实际发送');

        return true;
    } catch (error) {
        console.error('Error sending Slack notification:', error.message);
        return false;
    }
}

// 发送 Email 通知
function sendEmailNotification(text, emailAddress, subject) {
    try {
        // 由于要保持零依赖，这里只打印通知内容
        console.log(`📤 Email 通知 (地址: ${emailAddress}):`);
        console.log(`📧 主题: ${subject}`);
        console.log('-'.repeat(50));
        console.log(text);
        console.log('-'.repeat(50));

        // 提示用户如何配置实际的邮件发送
        console.log('\n💡 提示: 要启用实际的 Email 通知，请:');
        console.log('   1. 配置 SMTP 服务器');
        console.log('   2. 使用 nodemailer 或其他库进行实际发送');

        return true;
    } catch (error) {
        console.error('Error sending Email notification:', error.message);
        return false;
    }
}

// 主函数
function main() {
    const args = process.argv.slice(2);

    // 检查是否请求帮助
    if (args.includes('--help') || args.includes('-h')) {
        showHelp();
        return 0;
    }

    // 解析参数
    const parsedArgs = {};
    for (let i = 0; i < args.length; i += 2) {
        if (args[i].startsWith('--')) {
            const key = args[i].substring(2);
            parsedArgs[key] = args[i + 1];
        }
    }

    // 必需参数检查
    if (!parsedArgs.data) {
        console.error('Error: --data parameter is required');
        showHelp();
        return 1;
    }

    // 加载数据
    const data = loadData(parsedArgs.data);
    if (!data) {
        return 1;
    }

    const level = parsedArgs.level || 'warning';
    const channel = parsedArgs.channel || '#dev-complexity';

    // 生成通知文本
    const text = generateNotificationText(data, level);

    // 发送通知
    let success = true;

    if (parsedArgs.webhook) {
        success = success && sendSlackNotification(text, parsedArgs.webhook, channel);
    }

    if (parsedArgs.email) {
        const defaultSubject = `[${level.toUpperCase()}] 项目复杂度报告 - ${new Date().toISOString().split('T')[0]}`;
        success = success && sendEmailNotification(text, parsedArgs.email, parsedArgs.subject || defaultSubject);
    }

    // 如果没有指定具体的通知方式，只打印
    if (!parsedArgs.webhook && !parsedArgs.email) {
        console.log('📋 通知预览:');
        console.log('='.repeat(50));
        console.log(text);
        console.log('='.repeat(50));
        console.log('\n💡 提示: 使用 --webhook 或 --email 参数发送实际通知');
    }

    return success ? 0 : 1;
}

// 启动程序
process.exit(main());
