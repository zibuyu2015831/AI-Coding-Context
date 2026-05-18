const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const SCANNER = path.join(ROOT, 'tools', 'js', 'project_scanner.js');
const DAYFLOW_LIKE = path.join(ROOT, 'tools', 'testdata', 'semantic_review', 'dayflow_like_case');

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

  test('Swift/Xcode manifests are reported', () => {
    const result = spawnSync('node', [SCANNER, '--path', DAYFLOW_LIKE, '--format', 'json'], { cwd: ROOT, encoding: 'utf8' });
    assert.strictEqual(result.status, 0);
    const payload = JSON.parse(result.stdout);
    const data = payload.data;
    assert.ok(data.dependency_manifest_candidates.includes('Dayflow/Dayflow.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'));
    assert.ok(data.xcode_project_files.includes('Dayflow/Dayflow.xcodeproj/project.pbxproj'));
    assert.ok(data.platform_config_files.includes('Dayflow/Dayflow/Info.plist'));
    assert.ok(data.platform_config_files.includes('Dayflow/Dayflow/Dayflow.entitlements'));
  });

  test('standard exclude skips embedded AICC symlink', () => {
    const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'project-scanner-aicc-js-'));
    try {
      fs.writeFileSync(path.join(tmpdir, 'app.txt'), 'app\n', 'utf8');
      fs.symlinkSync(ROOT, path.join(tmpdir, 'AI-Coding-Context'), 'dir');
      const result = spawnSync('node', [SCANNER, '--path', tmpdir, '--format', 'json', '--exclude-standard', '--follow-symlinks'], { cwd: ROOT, encoding: 'utf8' });
      assert.strictEqual(result.status, 0);
      assert.ok(result.stdout.includes('app.txt'));
      assert.ok(!result.stdout.includes('AI_ENTRY_POINT.md'));
    } finally {
      fs.rmSync(tmpdir, { recursive: true, force: true });
    }
  });

  console.log(`测试完成: ${passed} 通过, ${failed} 失败`);
  if (failed > 0) process.exit(1);
}

if (require.main === module) {
  runTests();
}
