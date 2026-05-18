const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const CHECKER = path.join(ROOT, 'tools', 'js', 'semantic_review_checker.js');
const SEMANTIC_ROOT = path.join(ROOT, 'tools', 'testdata', 'semantic_review');

function runJson(args) {
  const result = spawnSync('node', [CHECKER, ...args], { cwd: ROOT, encoding: 'utf8' });
  return { result, payload: JSON.parse(result.stdout) };
}

function makePhase1Case(options = {}) {
  const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-phase1-js-'));
  fs.mkdirSync(path.join(caseRoot, 'dev_docs', '_analysis'), { recursive: true });
  fs.mkdirSync(path.join(caseRoot, 'tests', 'Feature'), { recursive: true });
  fs.writeFileSync(path.join(caseRoot, 'tests', 'Feature', 'ExampleTest.php'), '<?php\n', 'utf8');
  if (options.contributing) {
    fs.writeFileSync(path.join(caseRoot, 'CONTRIBUTING.md'), options.contributing, 'utf8');
  }
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'generation_plan.md'), `# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用，文档方案需覆盖主应用、开源维护与队列边界。

## 🧾 证据与验证记录

| 结论 | 证据等级 | 证据文件 | 验证方式 |
| --- | --- | --- | --- |
| 测试目录存在 | E1 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。
   - 为什么代码或仓库文档无法回答: 生产部署策略属于团队运维决策，仓库只包含示例配置。
   - blocks_phase1: false
   - 回写目标: deployment.md

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 \`证据等级\`
${options.planExtra || ''}
`, 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'project_analysis_report.md'), `# 项目分析报告

## 架构分析

已覆盖 tests/Feature/ExampleTest.php。

## 复查记录

| 事项 | 证据等级 | 当前状态 | blocks_phase1 | 回写目标 |
| --- | --- | --- | --- | --- |
| 部署环境边界 | E2 | 待用户确认 | false | deployment.md |

## 待确认问题

- 部署环境边界

${options.reportExtra || ''}
`, 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'generation_progress.md'), `# 文档生成进度记录

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-18 10:00
- **review_completed_at**: 2026-05-18 10:10
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **machine_checks**: doc_health_checker=PASS, semantic_review_checker=PASS
- **manual_review_summary**: 已复查
- **writeback_summary**: 已更新 generation_plan.md
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
`, 'utf8');
  return caseRoot;
}

function makeFirstReleaseCase(options = {}) {
  const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-first-release-js-'));
  fs.mkdirSync(path.join(caseRoot, 'dev_docs', '_analysis'), { recursive: true });
  fs.mkdirSync(path.join(caseRoot, 'dev_docs', 'rules', 'combined'), { recursive: true });
  fs.mkdirSync(path.join(caseRoot, 'resources', 'js', 'vuex'), { recursive: true });
  fs.mkdirSync(path.join(caseRoot, 'docker'), { recursive: true });
  fs.mkdirSync(path.join(caseRoot, 'routes'), { recursive: true });
  fs.writeFileSync(path.join(caseRoot, 'package.json'), JSON.stringify(options.packageJson || {
    dependencies: {
      vue: '^2.6.12',
      vuex: '^3.6.2',
    },
  }), 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'docker', 'PhpDockerfile'), options.dockerfile || 'FROM php:8.2-apache\nCOPY ./docker/vhost.conf /etc/apache2/sites-available/000-default.conf\n', 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'routes', 'web.php'), "<?php\nRoute::get('/books', 'BookController@index');\n", 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'routes', 'api.php'), "<?php\n", 'utf8');
  (options.vuexModules || ['Shared', 'InteractiveText', 'HoverVocabularyBox', 'VocabularyBox']).forEach((module) => {
    fs.writeFileSync(path.join(caseRoot, 'resources', 'js', 'vuex', `${module}.js`), 'export default {}\n', 'utf8');
  });
  if (options.contributing) {
    fs.writeFileSync(path.join(caseRoot, 'CONTRIBUTING.md'), options.contributing, 'utf8');
  }
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'generation_plan.md'), 'Phase 1 脱敏要求: 不复述密码、Token、完整密钥或个人联系信息。\n', 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'architecture_overview.md'), options.docsExtra || 'Web 层为 Nginx/PHP-FPM。\n', 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'deployment_guide.md'), 'DB_PASSWORD 默认值为 `linguacafe`，PUSHER_APP_KEY 为 `wjp2pou6ebgibtwccqsj`。\n', 'utf8');
  fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'rules', 'combined', 'AI_RULES.md'), options.aiRules || '前端框架: Vue 2 + Vuex 4\n状态管理模块: `user_storage`, `shared`, `theme`\n部署: Nginx/PHP-FPM\n', 'utf8');
  return caseRoot;
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

  test('help shows core flags', () => {
    const result = spawnSync('node', [CHECKER, '--help'], { cwd: ROOT, encoding: 'utf8' });
    assert.strictEqual(result.status, 0);
    assert.ok(result.stdout.includes('--check-fact-conflicts'));
    assert.ok(result.stdout.includes('--check-metrics'));
    assert.ok(result.stdout.includes('--check-test-topology'));
  });

  test('fact conflicts are reported', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'conflict_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--check-fact-conflicts',
    ]);
    assert.strictEqual(result.status, 1);
    assert.ok(payload.checks.fact_conflicts.some((issue) => issue.type === 'fact_conflict'));
  });

  test('generated file rule rephrasing is not fact conflict', () => {
    const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-rule-rephrasing-js-'));
    try {
      fs.mkdirSync(path.join(caseRoot, 'dev_docs'));
      fs.writeFileSync(path.join(caseRoot, 'CONTRIBUTING.md'), 'Generated output `*.g.dart` should not be edited by hand.\n', 'utf8');
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'AI_Coding_Context.md'), '不要手改 `*.g.dart`。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--check-fact-conflicts',
      ]);
      assert.strictEqual(result.status, 0, JSON.stringify(payload));
      assert.deepStrictEqual(payload.checks.fact_conflicts, []);
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('generated file opposite rule is fact conflict', () => {
    const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-rule-conflict-js-'));
    try {
      fs.mkdirSync(path.join(caseRoot, 'dev_docs'));
      fs.writeFileSync(path.join(caseRoot, 'CONTRIBUTING.md'), 'Generated output `*.g.dart` should not be edited by hand.\n', 'utf8');
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'AI_Coding_Context.md'), '建议直接编辑 `*.g.dart`。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--check-fact-conflicts',
      ]);
      assert.strictEqual(result.status, 1);
      assert.ok(payload.checks.fact_conflicts.some((issue) => issue.type === 'rule_conflict'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('sensitive keyword attention is not fact conflict authority', () => {
    const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-sensitive-attention-js-'));
    try {
      fs.mkdirSync(path.join(caseRoot, 'dev_docs'));
      fs.mkdirSync(path.join(caseRoot, 'docs'));
      fs.writeFileSync(
        path.join(caseRoot, 'docs', 'pr-policy-preflight.en.md'),
        '| Sensitive keyword | Added lines include keywords such as `UserStorage`, `GlobalEventBus` | These words are not necessarily wrong, but AI or reviewers should notice them. |\n',
        'utf8',
      );
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'AI_Coding_Context.md'), '新增数据偏好时优先使用 `UserStorage`。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--check-fact-conflicts',
      ]);
      assert.strictEqual(result.status, 0, JSON.stringify(payload));
      assert.deepStrictEqual(payload.checks.fact_conflicts, []);
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('mixed rule line applies negative polarity to actual negative anchor only', () => {
    const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-mixed-rule-js-'));
    try {
      fs.mkdirSync(path.join(caseRoot, 'dev_docs'));
      fs.writeFileSync(
        path.join(caseRoot, 'AGENTS.md'),
        'Do not scatter Drift `query.watch()` streams across services; centralize change observation through `TableChangeNotifier`.\n',
        'utf8',
      );
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'AI_Coding_Context.md'), '文件/数据库层变更：优先统一到 `TableChangeNotifier`。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--check-fact-conflicts',
      ]);
      assert.strictEqual(result.status, 0, JSON.stringify(payload));
      assert.deepStrictEqual(payload.checks.fact_conflicts, []);
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('metric drift is reported', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'metric_drift_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--check-metrics',
    ]);
    assert.strictEqual(result.status, 1);
    assert.ok(payload.checks.metrics.some((issue) => issue.type === 'metric_drift'));
  });

  test('uncovered test topology is reported', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'test_topology_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--check-test-topology',
    ]);
    assert.strictEqual(result.status, 1);
    assert.ok(payload.checks.test_topology.some((issue) => issue.type === 'uncovered_test_topology'));
  });

  test('Memex-style test topology requires all test roots', () => {
    const caseRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'semantic-memex-topology-js-'));
    try {
      fs.mkdirSync(path.join(caseRoot, 'dev_docs'));
      fs.mkdirSync(path.join(caseRoot, 'test', 'agent'), { recursive: true });
      fs.mkdirSync(path.join(caseRoot, 'tests', 'tools'), { recursive: true });
      fs.mkdirSync(path.join(caseRoot, 'ios', 'RunnerTests'), { recursive: true });
      fs.writeFileSync(path.join(caseRoot, 'test', 'agent', 'agent_test.dart'), 'void main() {}\n', 'utf8');
      fs.writeFileSync(path.join(caseRoot, 'tests', 'tools', 'test_tool.py'), 'def test_tool(): pass\n', 'utf8');
      fs.writeFileSync(path.join(caseRoot, 'ios', 'RunnerTests', 'RunnerTests.swift'), 'import XCTest\n', 'utf8');
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'testing_guide.md'), '仅记录 `test/`。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--check-test-topology',
      ]);
      assert.strictEqual(result.status, 1);
      const uncovered = new Set(payload.checks.test_topology.map((issue) => issue.path));
      assert.ok(uncovered.has('tests/'));
      assert.ok(uncovered.has('ios/RunnerTests/'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('Swift/Xcode tests are counted', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'dayflow_like_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--check-metrics',
      '--check-test-topology',
    ]);
    assert.strictEqual(result.status, 0);
    assert.deepStrictEqual(payload.checks.metrics, []);
    assert.deepStrictEqual(payload.checks.test_topology, []);
  });

  test('non-Swift *Tests directories fall back to all files', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'non_swift_tests_suffix_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--check-metrics',
      '--check-test-topology',
    ]);
    assert.strictEqual(result.status, 0);
    assert.deepStrictEqual(payload.checks.metrics, []);
    assert.deepStrictEqual(payload.checks.test_topology, []);
  });

  test('second review semantic issues are reported', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'dayflow_second_review_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--full-check',
    ]);
    assert.strictEqual(result.status, 1);
    const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
    assert.ok(issueTypes.has('summary_question_count_mismatch'));
    assert.ok(issueTypes.has('unevidenced_strong_conclusion'));
    assert.ok(issueTypes.has('invalid_evidence_path'));
  });

  test('LinguaCafe Phase 1 progress-only case is blocked', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'linguacafe_phase1_progress_only_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--full-check',
    ]);
    assert.strictEqual(result.status, 1);
    const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
    assert.ok(issueTypes.has('evidence_level_completeness') || issueTypes.has('evidence_table_level_column_missing'));
    assert.ok(issueTypes.has('project_analysis_issue_status_missing'));
    assert.ok(issueTypes.has('phase1_progress_only_review'));
    assert.ok(issueTypes.has('confirmable_fact_misclassified'));
    assert.ok(issueTypes.has('project_positioning_coverage_missing'));
  });

  test('LinguaCafe Phase 1 reviewed case passes', () => {
    const caseRoot = path.join(SEMANTIC_ROOT, 'linguacafe_phase1_reviewed_case');
    const { result, payload } = runJson([
      '--doc-dir', path.join(caseRoot, 'dev_docs'),
      '--repo-root', caseRoot,
      '--full-check',
    ]);
    assert.strictEqual(result.status, 0);
    assert.strictEqual(payload.summary.passed, true);
  });

  test('embedded AICC symlink is excluded from project scan', () => {
    const caseRoot = makePhase1Case();
    try {
      fs.symlinkSync(ROOT, path.join(caseRoot, 'AI-Coding-Context'), 'dir');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 0);
      assert.strictEqual(payload.summary.passed, true);
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('evidence table requires level column even when checklist mentions it', () => {
    const caseRoot = makePhase1Case();
    try {
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'generation_plan.md'), `# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用。

## 🧾 证据与验证记录

| 结论 | 证据文件 | 验证方式 |
| --- | --- | --- |
| 测试目录存在 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。
   - 为什么代码或仓库文档无法回答: 生产部署策略属于团队运维决策，仓库只包含示例配置。
   - blocks_phase1: false
   - 回写目标: deployment.md

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 \`证据等级\`
`, 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 1);
      const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
      assert.ok(issueTypes.has('evidence_table_level_column_missing'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('user confirmation items require rationale and writeback target', () => {
    const caseRoot = makePhase1Case();
    try {
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', '_analysis', 'generation_plan.md'), `# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用。

## 🧾 证据与验证记录

| 结论 | 证据等级 | 证据文件 | 验证方式 |
| --- | --- | --- | --- |
| 测试目录存在 | E1 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 \`证据等级\`
`, 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 1);
      const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
      assert.ok(issueTypes.has('user_confirmation_rationale_missing'));
      assert.ok(issueTypes.has('user_confirmation_blocks_phase1_missing'));
      assert.ok(issueTypes.has('user_confirmation_writeback_missing'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('test recommendation conflicting with CONTRIBUTING is reported', () => {
    const caseRoot = makePhase1Case({
      reportExtra: '后续优先补核心 Service 与队列 Job 的回归测试。',
      contributing: "Currently I don't use tests neither for Javascript, Python or PHP, please do not write any for PR-s.\n",
    });
    try {
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 1);
      const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
      assert.ok(issueTypes.has('test_recommendation_conflicts_with_contributing'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('first-release runtime, AI rules, and sensitive conflicts are reported', () => {
    const caseRoot = makeFirstReleaseCase({
      contributing: "Currently I don't use tests neither for Javascript, Python or PHP, please do not write any for PR-s.\n",
    });
    try {
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 1);
      const issueTypes = new Set(Object.values(payload.checks).flat().map((issue) => issue.type));
      assert.ok(issueTypes.has('runtime_stack_conflict'));
      assert.ok(issueTypes.has('ai_rules_dependency_version_conflict'));
      assert.ok(issueTypes.has('ai_rules_state_module_conflict'));
      assert.ok(issueTypes.has('ai_rules_runtime_stack_conflict'));
      assert.ok(issueTypes.has('sensitive_policy_declared_but_violated'));
      assert.ok(issueTypes.has('secret_like_value_in_docs'));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
    }
  });

  test('first-release correct docs pass without ecosystem false positives', () => {
    const caseRoot = makeFirstReleaseCase({
      docsExtra: 'Web 层为 Apache + Laravel + Supervisor。\n',
      aiRules: '前端框架: Vue 2 + Vuex 3\n状态管理模块: `shared`, `interactiveText`, `hoverVocabularyBox`, `vocabularyBox`\n部署: Apache\n',
    });
    try {
      fs.writeFileSync(path.join(caseRoot, 'dev_docs', 'deployment_guide.md'), '只列变量名：`DB_PASSWORD`、`PUSHER_APP_KEY`，生产环境必须改写。\n', 'utf8');
      const { result, payload } = runJson([
        '--doc-dir', path.join(caseRoot, 'dev_docs'),
        '--repo-root', caseRoot,
        '--full-check',
      ]);
      assert.strictEqual(result.status, 0, JSON.stringify(payload));
    } finally {
      fs.rmSync(caseRoot, { recursive: true, force: true });
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
