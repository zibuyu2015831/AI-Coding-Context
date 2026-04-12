#!/usr/bin/env node

/**
报告生成工具 - Node.js 版本
用于将复杂度数据转换为 Markdown 和 HTML 报告
作为 005 优化点的核心实施工具

功能说明：
- 读取 complexity_scanner.js 输出的 JSON 数据
- 生成 Markdown 格式报告
- 基于模板生成 HTML 仪表盘
- 支持自定义模板
- 集成 Mermaid 图表

使用方法：
    node tools/js/report_generator.js [--data DATA] [--output OUTPUT] [--format FORMAT] [--template TEMPLATE]

参数说明：
    --data DATA              输入数据文件路径（JSON 格式）
    --output OUTPUT          输出文件路径
    --format FORMAT          输出格式（markdown/html，默认：markdown）
    --template TEMPLATE      HTML 模板文件路径（仅 HTML 格式需要）
    --date DATE              报告日期（默认：当前日期）

输出格式（Markdown）：
    # 项目复杂度报告
    ## 摘要
    ## 代码规模
    ## 依赖关系
    ## 代码质量
    ## 架构健康度
    ## 风险分析
    ## 行动建议

输出格式（HTML）：
    基于 dev_docs/complexity/dashboard/template.html 渲染的完整 HTML 页面

使用示例：
    # 生成 Markdown 报告
    node tools/js/report_generator.js --data data.json --output report.md --format markdown

    # 生成 HTML 仪表盘
    node tools/js/report_generator.js --data data.json --output dashboard.html --format html --template template.html

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
*/

const fs = require('fs');
const path = require('path');

// 风险等级颜色映射
function riskColor(level) {
    if (level === 'high') {
        return '🔴';
    } else if (level === 'medium') {
        return '🟡';
    } else {
        return '🟢';
    }
}

// 生成 Markdown 报告
function generateMarkdownReport(data, reportDate = null) {
    if (!reportDate) {
        reportDate = new Date().toISOString().split('T')[0];
    }

    const complexityData = data.data || {};
    const codeSize = complexityData.code_size || {};
    const dependencies = complexityData.dependencies || {};
    const codeQuality = complexityData.code_quality || {};
    const architecture = complexityData.architecture || {};
    const riskAssessment = complexityData.risk_assessment || {};

    let report = `# 📊 项目复杂度报告

**生成日期**: ${reportDate}
**工具版本**: ${data.metadata?.version || '1.0.0'}
**扫描耗时**: ${data.metadata?.elapsed_seconds || 0}s

---

## 🎯 摘要

| 指标 | 当前值 | 状态 |
|------|---------|------|
| 整体风险评分 | ${(riskAssessment.overall_score || 0).toFixed(0)}/100 | ${riskColor(riskAssessment.overall_score > 70 ? 'low' : (riskAssessment.overall_score > 50 ? 'medium' : 'high'))} |
| 代码质量评分 | ${codeQuality.quality_score || 0}/100 | ${riskColor(codeQuality.quality_score > 70 ? 'low' : (codeQuality.quality_score > 50 ? 'medium' : 'high'))} |
| 新增代码 | ${codeSize.new_lines || 0} 行 | ${riskColor(codeSize.new_lines < 200 ? 'low' : (codeSize.new_lines < 500 ? 'medium' : 'high'))} |

---

## 📈 代码规模

| 指标 | 数值 |
|------|------|
| 新增代码行数 | ${codeSize.new_lines || 0} |
| 总代码量 | ${codeSize.total_lines || 0} |
| 变更文件数 | ${codeSize.files || 0} |
| 增长百分比 | ${(codeSize.growth_percentage || 0).toFixed(1)}% |

\`\`\`mermaid
graph TD
    A[代码规模] --> B[新增: ${codeSize.new_lines || 0}行]
    A --> C[总数: ${codeSize.total_lines || 0}行]
    A --> D[文件: ${codeSize.files || 0}个]
    A --> E[增长: ${(codeSize.growth_percentage || 0).toFixed(1)}%]
\`\`\`

---

## 🔗 依赖关系

| 指标 | 数值 |
|------|------|
| 新增依赖 | ${dependencies.new || 0} |
| 重复依赖 | ${dependencies.duplicate || 0} |
| 依赖深度 | ${dependencies.depth || 0} |

---

## 📋 代码质量

| 指标 | 数值 | 建议 |
|------|------|------|
| TODO 标记 | ${codeQuality.todo_count || 0} | < 10 |
| FIXME 标记 | ${codeQuality.fixme_count || 0} | 0 |
| 重复代码 | ${codeQuality.duplicate_code || 0} | 0 |
| 质量评分 | ${codeQuality.quality_score || 0}/100 | > 70 |

---

## 🏗️ 架构健康度

| 指标 | 数值 | 建议 |
|------|------|------|
| 核心文件变更 | ${architecture.core_files_changed || 0} | 少 |
| 代码耦合度 | ${architecture.coupling_score || 0} | < 20 |
| 领域边界清晰度 | ${(architecture.domain_boundary_score || 0)}/10 | > 7 |

---

## ⚠️ 风险分析

### 整体评分
**${(riskAssessment.overall_score || 0).toFixed(0)}/100**

### 风险项
`;

    // 添加风险项
    const risks = riskAssessment.risks || [];
    if (risks.length > 0) {
        risks.forEach((risk, i) => {
            report += `\n${riskColor(risk.level || 'low')} **风险 ${i + 1}**\n`;
            report += `- **指标**: ${risk.indicator || ''}\n`;
            report += `- **级别**: ${risk.level || ''}\n`;
            report += `- **说明**: ${risk.message || ''}\n`;
        });
    } else {
        report += '\n🟢 无显著风险项\n';
    }

    // 添加行动建议
    report += `
---

## 🛠️ 行动建议

`;

    let hasSuggestions = false;

    if (codeQuality.todo_count > 10) {
        report += `1. 🔴 **清理 TODO 标记**：当前有 ${codeQuality.todo_count} 个，建议减少到 10 个以下\n`;
        hasSuggestions = true;
    }

    if (codeQuality.fixme_count > 0) {
        report += `2. 🔴 **立即处理 FIXME**：当前有 ${codeQuality.fixme_count} 个需要立即修复\n`;
        hasSuggestions = true;
    }

    if (codeSize.growth_percentage > 5) {
        report += `3. 🟡 **控制代码增长**：当前增长 ${(codeSize.growth_percentage || 0).toFixed(1)}%，建议控制在 5% 以下\n`;
        hasSuggestions = true;
    }

    if (dependencies.depth > 3) {
        report += `4. 🟡 **优化依赖关系**：当前依赖深度 ${dependencies.depth}，建议减少到 3 层以下\n`;
        hasSuggestions = true;
    }

    if (!hasSuggestions) {
        report += '🟢 当前状态良好，建议保持！\n';
    }

    // 添加 Mermaid 图表
    report += `
---

## 📊 趋势图表

\`\`\`mermaid
pie title 风险分布
    "高风险" : ${risks.filter(r => r.level === 'high').length}
    "中风险" : ${risks.filter(r => r.level === 'medium').length}
    "低风险" : ${risks.filter(r => r.level === 'low' || (!['high', 'medium'].includes(r.level))).length}
\`\`\`

\`\`\`mermaid
stateDiagram-v2
    [*] --> 立即修复
    [*] --> 优先优化
    [*] --> 建议改进
    [*] --> 正常维护

    立即修复 --> TODO标记: ${codeQuality.todo_count || 0}
    立即修复 --> FIXME标记: ${codeQuality.fixme_count || 0}
    优先优化 --> 依赖深度: ${dependencies.depth || 0}
    建议改进 --> 代码增长: ${(codeSize.growth_percentage || 0).toFixed(1)}%
    正常维护 --> [*]
\`\`\`
`;

    return report;
}

// 生成 HTML 报告
function generateHtmlReport(data, templatePath, reportDate = null) {
    try {
        const templateContent = fs.readFileSync(templatePath, 'utf8');
        const complexityData = data.data || {};
        const reportDateStr = reportDate || new Date().toISOString().split('T')[0];

        // 简单的模板替换
        let html = templateContent.replace('{{data}}', JSON.stringify(data, null, 2));
        html = html.replace('{{report_date}}', reportDateStr);

        return html;
    } catch (error) {
        console.error('Error generating HTML report:', error);
        return null;
    }
}

// 主函数
function main() {
    const args = process.argv.slice(2);
    const parsedArgs = {};
    for (let i = 0; i < args.length; i += 2) {
        if (args[i].startsWith('--')) {
            const key = args[i].substring(2);
            parsedArgs[key] = args[i + 1];
        }
    }

    // 必填参数检查
    if (!parsedArgs.data) {
        console.error('Error: --data parameter is required');
        return;
    }

    try {
        // 加载数据
        const content = fs.readFileSync(parsedArgs.data, 'utf8');
        const data = JSON.parse(content);

        // 确定格式
        const format = parsedArgs.format || 'markdown';

        // 生成报告
        let report;
        if (format === 'markdown') {
            report = generateMarkdownReport(data, parsedArgs.date);
            outputExt = '.md';
        } else if (format === 'html') {
            if (!parsedArgs.template) {
                console.error('Error: --template is required for HTML format');
                return;
            }
            report = generateHtmlReport(data, parsedArgs.template, parsedArgs.date);
            outputExt = '.html';
        } else {
            console.error('Error: Unsupported format:', format);
            return;
        }

        if (!report) {
            console.error('Error: Report generation failed');
            return;
        }

        // 输出报告
        if (parsedArgs.output) {
            const outputDir = path.dirname(parsedArgs.output);
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }
            fs.writeFileSync(parsedArgs.output, report);
            console.log(`报告已保存到: ${parsedArgs.output}`);
        } else {
            console.log(report);
        }
    } catch (error) {
        console.error('Error:', error.message);
        return;
    }
}

// 帮助信息
function showHelp() {
    console.log(`
报告生成工具 - Node.js 版本
用于将复杂度数据转换为 Markdown 和 HTML 报告

使用方法：
    node tools/js/report_generator.js [--data DATA] [--output OUTPUT] [--format FORMAT] [--template TEMPLATE]

参数说明：
    --data DATA              输入数据文件路径（JSON 格式）
    --output OUTPUT          输出文件路径
    --format FORMAT          输出格式（markdown/html，默认：markdown）
    --template TEMPLATE      HTML 模板文件路径（仅 HTML 格式需要）
    --date DATE              报告日期（默认：当前日期）
    --help, -h              显示此帮助信息

使用示例：
    # 生成 Markdown 报告
    node tools/js/report_generator.js --data data.json --output report.md --format markdown

    # 生成 HTML 仪表盘
    node tools/js/report_generator.js --data data.json --output dashboard.html --format html --template template.html

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
`);
}

// 检查是否请求帮助
if (process.argv.includes('--help') || process.argv.includes('-h')) {
    showHelp();
} else {
    main();
}
