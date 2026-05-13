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

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) {
    process.exit(1);
  }
}

if (require.main === module) {
  runTests();
}
