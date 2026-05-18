const assert = require('assert');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const CHECKER = path.join(ROOT, 'tools', 'js', 'semantic_review_checker.js');
const SEMANTIC_ROOT = path.join(ROOT, 'tools', 'testdata', 'semantic_review');

function runJson(args) {
  const result = spawnSync('node', [CHECKER, ...args], { cwd: ROOT, encoding: 'utf8' });
  return { result, payload: JSON.parse(result.stdout) };
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
    assert.ok(issueTypes.has('evidence_level_completeness'));
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

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) {
    process.exit(1);
  }
}

if (require.main === module) {
  runTests();
}
