/**
 * Commit 质量评分工具 - 评估 commit 质量
 * 
 * 功能说明：
 * - 5维度评分（WHAT/WHY/HOW/粒度/可测试性）
 * - 生成改进建议
 * 
 * 使用方法：
 *   node tools/js/commit_quality_scorer.js [--message MESSAGE]
 * 
 * 参数说明：
 *   --message MESSAGE        Commit message文本
 * 
 * 版本信息：
 *   版本：1.0.0
 *   更新日期：2025-12-11
 */

const { execSync } = require('child_process');

function scoreWhatClarity(whatText) {
    if (!whatText || whatText === '(未提供)') {
        return [0, ["缺少WHAT字段,无法理解做了什么"]];
    }
    
    let score = 0;
    const suggestions = [];
    
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
    
    const actionVerbs = ['新增', '修复', '优化', '重构', '删除', '更新', '实现', 'add', 'fix', 'update'];
    if (actionVerbs.some(verb => whatText.startsWith(verb))) {
        score += 10;
    } else {
        score += 5;
        suggestions.push("建议以动词开头");
    }
    
    if (/[A-Z][a-z]+|[\u4e00-\u9fa5]{2,}/.test(whatText)) {
        score += 10;
    } else {
        score += 5;
    }
    
    return [score, suggestions];
}

function scoreWhyDepth(whyText) {
    if (!whyText || whyText === '(未提供)') {
        return [0, ["缺少WHY字段"]];
    }
    
    let score = 0;
    const suggestions = [];
    
    if (whyText.length >= 20) score += 10;
    else if (whyText.length >= 10) score += 7;
    else score += 3;
    
    const businessKeywords = ['需求', '用户', '业务', '提升', '优化', 'user', 'business'];
    if (businessKeywords.some(kw => whyText.includes(kw))) {
        score += 10;
    } else {
        score += 3;
        suggestions.push("建议说明业务价值");
    }
    
    const emptyReasons = ['需求要求', '老板说'];
    if (emptyReasons.some(r => whyText.includes(r))) {
        score += 2;
        suggestions.push("避免空洞理由");
    } else {
        score += 10;
    }
    
    return [score, suggestions];
}

function calculateCommitScore(commitData) {
    const what = commitData.what || '';
    const why = commitData.why || '';
    const how = commitData.how || [];
    
    const [whatScore, whatSuggestions] = scoreWhatClarity(what);
    const [whyScore, whySuggestions] = scoreWhyDepth(why);
    
    let howScore = 0;
    const howSuggestions = [];
    if (!how || how[0] === '(需分析diff)') {
        howSuggestions.push("缺少HOW字段");
    } else if (how.length >= 2 && how.length <= 5) {
        howScore = 20;
    } else {
        howScore = 10;
    }
    
    const total = whatScore + whyScore + howScore + 10 + 5; // granularity + testability defaults
    
    let grade = '不及格';
    if (total >= 80) grade = '优秀';
    else if (total >= 60) grade = '良好';
    else if (total >= 40) grade = '及格';
    
    return {
        total_score: total,
        breakdown: {
            what_clarity: whatScore,
            why_depth: whyScore,
            how_completeness: howScore,
            granularity: 10,
            testability: 5
        },
        grade,
        suggestions: [...whatSuggestions, ...whySuggestions, ...howSuggestions],
        is_quality: total >= 80
    };
}

function main() {
    const startTime = Date.now();
    
    const args = process.argv.slice(2);
    let message = null;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--message') message = args[i + 1];
    }
    
    if (!message) {
        console.log(JSON.stringify({ data: { error: 'No message provided' } }, null, 2));
        return;
    }
    
    // Simple parsing
    const commitData = {
        what: message,
        why: '(未提供)',
        how: ['(需分析diff)']
    };
    
    const resultData = calculateCommitScore(commitData);
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(4);
    const result = {
        data: resultData,
        metadata: {
            elapsed_seconds: parseFloat(elapsedTime),
            version: '1.0.0'
        }
    };
    
    console.log(JSON.stringify(result, null, 2));
}

main();
