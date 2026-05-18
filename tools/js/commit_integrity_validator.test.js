const assert = require('assert');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const VALIDATOR = path.join(ROOT, 'tools', 'js', 'commit_integrity_validator.js');

function runJson(message) {
  const result = spawnSync('node', [VALIDATOR, '--message', message, '--format', 'json'], {
    cwd: ROOT,
    encoding: 'utf8',
  });
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

  test('HOW parser does not treat extensions as hidden files', () => {
    const message = `prompt(feature): test commit
WHAT: test
WHY: test
HOW:
- 修改了 src/models/user.py
- 新增了 src/api/auth.ts 文件
- 调整了 config/settings.yaml
- 修改了 README.md
`;
    const { result, payload } = runJson(message);
    assert.strictEqual(result.status, 0);
    assert.ok(payload.data.over_reported.includes('src/models/user.py'));
    assert.ok(payload.data.over_reported.includes('src/api/auth.ts'));
    assert.ok(payload.data.over_reported.includes('config/settings.yaml'));
    assert.ok(payload.data.over_reported.includes('README.md'));
    assert.ok(!payload.data.over_reported.includes('py'));
    assert.ok(!payload.data.over_reported.includes('ts'));
    assert.ok(!payload.data.over_reported.includes('yaml'));
    assert.ok(!payload.data.over_reported.includes('md'));
  });

  test('HOW parser keeps hidden files', () => {
    const { result, payload } = runJson('HOW: 更新 .gitignore 和 ./src/utils/helper.js');
    assert.strictEqual(result.status, 0);
    assert.ok(payload.data.over_reported.includes('.gitignore'));
    assert.ok(payload.data.over_reported.includes('src/utils/helper.js'));
    assert.ok(!payload.data.over_reported.includes('js'));
  });

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) process.exit(1);
}

if (require.main === module) {
  runTests();
}
