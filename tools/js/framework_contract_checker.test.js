const assert = require('assert');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const CHECKER = path.join(ROOT, 'tools', 'js', 'framework_contract_checker.js');
const VALID_TEMPLATE = path.join(ROOT, 'tools', 'testdata', 'framework_contracts', 'valid_template.md');
const MISSING_TEMPLATE = path.join(ROOT, 'tools', 'testdata', 'framework_contracts', 'missing_sections_template.md');
const DRIFT_SPEC = path.join(ROOT, 'tools', 'testdata', 'framework_contracts', 'spec_workflow_drift_case', 'spec.md');
const DRIFT_WORKFLOW = path.join(ROOT, 'tools', 'testdata', 'framework_contracts', 'spec_workflow_drift_case', 'workflow.md');

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
    assert.ok(result.stdout.includes('--self-check'));
    assert.ok(result.stdout.includes('--check-template'));
    assert.ok(result.stdout.includes('--check-workflow'));
  });

  test('valid template passes', () => {
    const { result, payload } = runJson(['--check-template', VALID_TEMPLATE]);
    assert.strictEqual(result.status, 0);
    assert.strictEqual(payload.summary.passed, true);
    assert.deepStrictEqual(payload.checks.template.issues, []);
  });

  test('missing sections are reported', () => {
    const { result, payload } = runJson(['--check-template', MISSING_TEMPLATE]);
    assert.strictEqual(result.status, 1);
    assert.ok(payload.checks.template.issues.some((issue) => issue.type === 'missing_required_section'));
  });

  test('workflow drift is reported', () => {
    const { result, payload } = runJson(['--check-workflow', DRIFT_WORKFLOW, '--spec', DRIFT_SPEC]);
    assert.strictEqual(result.status, 1);
    assert.ok(payload.checks.workflow.issues.some((issue) => issue.type === 'workflow_path_drift'));
  });

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) {
    process.exit(1);
  }
}

if (require.main === module) {
  runTests();
}
