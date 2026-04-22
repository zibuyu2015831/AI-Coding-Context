/**
 * Commit 质量评分工具 - 评估 commit 质量
 * 
 * 功能说明：
 * - 5维度评分（WHAT/WHY/HOW/粒度/可测试性）
 * - 生成改进建议
 * - 识别优质 commit
 * 
 * 使用方法：
 *   node tools/js/commit_quality_scorer.js [--message MESSAGE] [--hash HASH]
 * 
 * 参数说明：
 *   --message MESSAGE        Commit message文本
 *   --hash HASH             Commit哈希（自动获取message）
 *   --threshold SCORE       及格分数线（默认：60）
 * 
 * 输出格式：
 *   {
 *     "data": {
 *       "total_score": 总分(0-100),
 *       "breakdown": {
 *         "what_clarity": WHAT清晰度(0-30),
 *         "why_depth": WHY深度(0-30),
 *         "how_completeness": HOW完整性(0-20),
 *         "granularity": 粒度合理性(0-10),
 *         "testability": 可测试性(0-10)
 *       },
 *       "grade": "优秀/良好/及格/不及格",
 *       "suggestions": ["建议1", "建议2"],
 *       "is_quality": true/false
 *     }
 *   }
 * 
 * 版本信息：
 *   版本：1.1.0
 *   更新日期：2026-04-22
 */

const { execSync } = require('child_process');
const { parseCommitMessage } = require('./commit_parser');

/**
 * 评分WHAT清晰度 (满分30)
 */
function scoreWhatClarity(whatText) {
    if (!whatText || whatText === '(未提供)') {
        return [0, ["缺少WHAT字段,无法理解做了什么"]];
    }
    
    let score = 0;
    const suggestions = [];
    
    // 长度合理性 (10分)
    const length = whatText.length;
    if (length >= 10 && length <= 100) {
        score += 10;
    } else if (length < 10) {
        score += 3;
        suggestions.push("WHAT过于简短,建议补充更多细节");
    } else {
        score += 7;
        suggestions.push("WHAT过长,建议精简为一句话");
    }
    
    // 动词开头 (10分)
    const actionVerbs = ['新增', '修复', '优化', '重构', '删除', '更新', '实现', '添加', 
                        '移除', '调整', 'add', 'fix', 'update', 'remove', 'refactor', 
                        'implement', 'optimize', 'delete', 'adjust'];
    if (actionVerbs.some(verb => whatText.toLowerCase().startsWith(verb))) {
        score += 10;
    } else {
        score += 5;
        suggestions.push("建议以动词开头,如'新增'、'修复'、'优化'等");
    }
    
    // 具体性 (10分)
    if (/[A-Z][a-z]+|[\u4e00-\u9fa5]{2,}/.test(whatText)) {
        score += 10;
    } else {
        score += 5;
        suggestions.push("建议包含具体的模块名或功能名");
    }
    
    return [score, suggestions];
}

/**
 * 评分WHY深度 (满分30)
 */
function scoreWhyDepth(whyText) {
    if (!whyText || whyText === '(未提供)') {
        return [0, ["缺少WHY字段,无法理解为什么要做这个变更"]];
    }
    
    let score = 0;
    const suggestions = [];
    
    // 长度 (10分)
    const length = whyText.length;
    if (length >= 20) score += 10;
    else if (length >= 10) score += 7;
    else {
        score += 3;
        suggestions.push("WHY过于简短,建议详细说明动机");
    }
    
    // 业务价值 (10分)
    const businessKeywords = ['需求', '用户', '业务', '提升', '优化', '解决', '问题', 
                            'requirement', 'user', 'business', 'improve', 'solve'];
    if (businessKeywords.some(kw => whyText.includes(kw))) {
        score += 10;
    } else {
        score += 3;
        suggestions.push("建议说明业务价值或用户价值");
    }
    
    // 避免空洞理由 (10分)
    const emptyReasons = ['需求要求', '老板说', '产品要求', '必须做'];
    if (emptyReasons.some(r => whyText.includes(r))) {
        score += 2;
        suggestions.push("避免使用'需求要求'等空洞理由,说明真实动机");
    } else {
        score += 10;
    }
    
    return [score, suggestions];
}

/**
 * 评分HOW完整性 (满分20)
 */
function scoreHowCompleteness(howItems) {
    if (!howItems || howItems.length === 0 || howItems[0] === '(需分析diff)') {
        return [0, ["缺少HOW字段,无法理解实现方式"]];
    }
    
    let score = 0;
    const suggestions = [];
    
    // 条目数量 (10分)
    const count = howItems.length;
    if (count >= 2 && count <= 5) {
        score += 10;
    } else if (count === 1) {
        score += 6;
        suggestions.push("HOW只有一条,建议补充更多实现细节");
    } else {
        score += 7;
        suggestions.push("HOW条目过多,建议精简关键点");
    }
    
    // 具体性 (10分)
    const hasTechnicalDetail = howItems.some(item => /[A-Z][a-z]+|[\u4e00-\u9fa5]{3,}/.test(item));
    if (hasTechnicalDetail) {
        score += 10;
    } else {
        score += 5;
        suggestions.push("HOW缺少技术细节,建议说明具体实现方式");
    }
    
    return [score, suggestions];
}

/**
 * 评分粒度合理性 (满分10)
 */
function scoreGranularity(whatText, howItems) {
    let score = 10;
    const suggestions = [];
    
    if (howItems && howItems.length > 8) {
        score = 5;
        suggestions.push("commit粒度过大,建议拆分为多个commit");
    }
    
    if (whatText && (whatText.includes('修改空格') || whatText.includes('调整缩进') || /typo/i.test(whatText))) {
        score = 7;
        suggestions.push("commit粒度过小,建议合并到相关功能commit中");
    }
    
    return [score, suggestions];
}

/**
 * 评分可测试性 (满分10)
 */
function scoreTestability(howItems) {
    if (!howItems || howItems.length === 0 || howItems[0] === '(需分析diff)') {
        return [5, ["未说明如何验证,建议补充测试方法"]];
    }
    
    const testKeywords = ['测试', '验证', '检查', 'test', 'verify', 'check', '单元测试', '集成测试'];
    const hasTestMention = howItems.some(item => testKeywords.some(kw => item.toLowerCase().includes(kw)));
    
    if (hasTestMention) {
        return [10, []];
    } else {
        return [5, ["建议说明如何测试或验证这个变更"]];
    }
}

/**
 * 计算 commit 总分
 */
function calculateCommitScore(commitData) {
    const what = commitData.what || '';
    const why = commitData.why || '';
    const how = commitData.how || [];
    
    const [whatScore, whatSuggestions] = scoreWhatClarity(what);
    const [whyScore, whySuggestions] = scoreWhyDepth(why);
    const [howScore, howSuggestions] = scoreHowCompleteness(how);
    const [granularityScore, granularitySuggestions] = scoreGranularity(what, how);
    const [testabilityScore, testabilitySuggestions] = scoreTestability(how);
    
    const total = whatScore + whyScore + howScore + granularityScore + testabilityScore;
    
    let grade = '不及格';
    if (total >= 80) grade = '优秀';
    else if (total >= 60) grade = '良好';
    else if (total >= 40) grade = '及格';
    
    const allSuggestions = [
        ...whatSuggestions,
        ...whySuggestions,
        ...howSuggestions,
        ...granularitySuggestions,
        ...testabilitySuggestions
    ];
    
    return {
        total_score: total,
        breakdown: {
            what_clarity: whatScore,
            why_depth: whyScore,
            how_completeness: howScore,
            granularity: granularityScore,
            testability: testabilityScore
        },
        grade,
        suggestions: allSuggestions,
        is_quality: total >= 80
    };
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let message = null;
    let hash = null;
    let threshold = 60;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--message') message = args[i + 1];
        if (args[i] === '--hash') hash = args[i + 1];
        if (args[i] === '--threshold') threshold = parseInt(args[i + 1]);
    }
    
    if (hash) {
        try {
            message = execSync(`git show --no-patch --format=%s%n%b ${hash}`, { encoding: 'utf8' }).trim();
        } catch (e) {
            message = null;
        }
    }
    
    let resultData;
    if (!message) {
        resultData = { error: 'No commit message provided' };
    } else {
        const commitData = parseCommitMessage(message);
        resultData = calculateCommitScore(commitData);
        resultData.commit_data = commitData;
    }
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    const result = {
        data: resultData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            version: '1.1.0'
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
    main();
}
