const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const CHECKER = path.join(ROOT, 'tools', 'js', 'doc_health_checker.js');

const MAIN_DOC_BASE = `---
title: 示例
summary: 示例摘要，长度足够用于通过 frontmatter 检查。
keywords: example | test | aicc
scope: test
related_files: core/framework_spec.md
dependencies: 无
verified_at: 2026-05-12
---

# AI 编码上下文

## 📊 项目概览
## 📂 关键目录速查
## 🎯 场景快速导航
## 🚀 文档索引
## 💻 核心代码模式
## 🛠️ 开发流程规范
## 📋 命名规范
## 🏢 业务模块映射
## ⚠️ AI 编码禁忌
## 🔧 常见任务速查
`;

const GENERATION_PLAN_BASE = `# 文档生成方案模板

## 🎯 任务复杂度评估 (Complexity Assessment)

## ⚠️ 风险点与注意事项

## 🤝 交互策略 (Interaction Strategy)

## 📚 第三阶段：子文档规划（待审核）

## 📊 质量保证措施

## 🧾 证据与验证记录

## 🔎 Phase 1 方案复查清单
`;

const GENERATION_PROGRESS_BASE = `# 文档生成进度记录

> **开始时间**: 2026-05-12 10:00
> **最后更新**: 2026-05-12 10:30
> **当前状态**: 生成中
> **流程阶段进度**: Step 4/8，当前处于方案生成
> **产物完成度**: 1/3，已完成部分 _analysis 产物
> **当前 gate**: Phase 1 自检
> **下一步动作**: 继续生成

## 🎯 总体步骤进度

## 📝 逐文档完成状态

## 📊 统计信息

- **总任务数**: 3
- **已完成数**: 1
`;

function makeTempDevDocs() {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'doc-health-js-'));
  const devDocs = path.join(base, 'dev_docs');
  fs.mkdirSync(path.join(devDocs, '_analysis'), { recursive: true });
  fs.writeFileSync(path.join(devDocs, 'AI_Coding_Context.md'), MAIN_DOC_BASE, 'utf8');
  fs.writeFileSync(path.join(devDocs, '_analysis', 'generation_plan.md'), GENERATION_PLAN_BASE, 'utf8');
  fs.writeFileSync(path.join(devDocs, '_analysis', 'generation_progress.md'), GENERATION_PROGRESS_BASE, 'utf8');
  return { base, devDocs };
}

function runJson(args) {
  const result = spawnSync('node', [CHECKER, ...args], { cwd: ROOT, encoding: 'utf8' });
  return { result, payload: JSON.parse(result.stdout) };
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

function runTests() {
  let passed = 0;
  let failed = 0;

  function test(name, fn) {
    try {
      fn();
      console.log(`✅ ${name}`);
      passed++;
    } catch (error) {
      console.log(`❌ ${name}: ${error.message}`);
      failed++;
    }
  }

  test('help shows new checker flags', () => {
    const result = spawnSync('node', [CHECKER, '--help'], { cwd: ROOT, encoding: 'utf8' });
    assert.strictEqual(result.status, 0);
    assert.ok(result.stdout.includes('--check-required-sections'));
    assert.ok(result.stdout.includes('--check-template-residue'));
    assert.ok(result.stdout.includes('--check-run-record-integrity'));
  });

  test('required sections pass for complete main doc', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-required-sections']);
      assert.strictEqual(result.status, 0);
      assert.strictEqual(payload.summary.passed, true);
      assert.deepStrictEqual(payload.checks.required_sections.issues, []);
    } finally {
      cleanup(base);
    }
  });

  test('template residue is reported', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      fs.writeFileSync(path.join(devDocs, 'AI_Coding_Context.md'), `${MAIN_DOC_BASE}\nTODO [PROJECT_NAME]\n`, 'utf8');
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-template-residue']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.template_residue.issues.some((issue) => issue.type === 'template_residue'));
    } finally {
      cleanup(base);
    }
  });

  test('run record integrity is reported', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      fs.writeFileSync(path.join(devDocs, '_analysis', 'generation_progress.md'), '# 文档生成进度记录\n', 'utf8');
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.run_record_integrity.issues.some((issue) => issue.type === 'run_record_integrity'));
    } finally {
      cleanup(base);
    }
  });

  test('Phase 1 PASS requires review record and user confirmation boundary', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const progress = GENERATION_PROGRESS_BASE
        .replace('> **当前状态**: 生成中', '> **当前状态**: 等待人工审核')
        .replace('> **下一步动作**: 继续生成', '> **下一步动作**: Phase 1 PASS，可进入正式文档生成');
      fs.writeFileSync(path.join(devDocs, '_analysis', 'generation_progress.md'), progress, 'utf8');
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      const issueTypes = new Set(payload.checks.run_record_integrity.issues.map((issue) => issue.type));
      assert.ok(issueTypes.has('phase1_pass_without_plan_review_record'));
      assert.ok(issueTypes.has('phase1_pass_before_user_confirmation'));
    } finally {
      cleanup(base);
    }
  });

  test('Phase 1 review record requires writeback summary', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const progress = `${GENERATION_PROGRESS_BASE
        .replace('> **当前状态**: 生成中', '> **当前状态**: 等待人工审核')
        .replace('> **下一步动作**: 继续生成', '> **下一步动作**: Phase 1 建议通过，等待用户确认')}

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-12 10:30
- **review_completed_at**: 2026-05-12 10:40
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **machine_checks**: doc_health_checker=PASS, semantic_review_checker=PASS
- **manual_review_summary**: 已复查
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
`;
      fs.writeFileSync(path.join(devDocs, '_analysis', 'generation_progress.md'), progress, 'utf8');
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.run_record_integrity.issues.some((issue) => issue.type === 'phase1_plan_review_writeback_missing'));
    } finally {
      cleanup(base);
    }
  });

  test('duplicate last updated values are reported', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      fs.writeFileSync(
        path.join(devDocs, '_analysis', 'generation_progress.md'),
        `${GENERATION_PROGRESS_BASE}\n**最后更新**: 2026-05-12 11:00\n`,
        'utf8',
      );
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.run_record_integrity.issues.some((issue) => issue.type === 'progress_metadata_mismatch'));
    } finally {
      cleanup(base);
    }
  });

  test('unlabeled multiple percentages are reported', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      fs.writeFileSync(
        path.join(devDocs, '_analysis', 'generation_progress.md'),
        `${GENERATION_PROGRESS_BASE}\n**进度**: 40%\n**进度**: 60%\n`,
        'utf8',
      );
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.run_record_integrity.issues.some((issue) => issue.type === 'ambiguous_progress_percentage'));
    } finally {
      cleanup(base);
    }
  });

  test('stale review conclusions are reported', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      fs.writeFileSync(
        path.join(devDocs, '_analysis', 'generation_plan.md'),
        `${GENERATION_PLAN_BASE}\n数据库技术: SQLite/Core Data / SwiftData (待确认)\n\n## 复查记录\n\n| 事实 | 新状态 |\n| --- | --- |\n| 数据库技术为 GRDB | ✅ 已确认 |\n`,
        'utf8',
      );
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.run_record_integrity.issues.some((issue) => issue.type === 'stale_review_conclusion'));
    } finally {
      cleanup(base);
    }
  });

  test('analysis docs do not require frontmatter', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const { result, payload } = runJson(['--doc-dir', devDocs, '--full-check']);
      assert.strictEqual(result.status, 0);
      assert.deepStrictEqual(payload.checks.frontmatter.issues, []);
    } finally {
      cleanup(base);
    }
  });

  test('completed count does not trigger health report requirement', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const { result, payload } = runJson(['--doc-dir', devDocs, '--check-run-record-integrity']);
      assert.strictEqual(result.status, 0);
      assert.deepStrictEqual(payload.checks.run_record_integrity.issues, []);
    } finally {
      cleanup(base);
    }
  });

  test('legacy quick mode still works', () => {
    const { base, devDocs } = makeTempDevDocs();
    try {
      const { result, payload } = runJson(['--doc-dir', devDocs, '--mode', 'quick']);
      assert.ok([0, 1].includes(result.status));
      assert.ok(payload.checks.file_paths);
    } finally {
      cleanup(base);
    }
  });

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) {
    process.exit(1);
  }
}

if (require.main === module) {
  runTests();
}
