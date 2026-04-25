#!/usr/bin/env node
/**
 * 文档健康检查工具 — Hybrid Orchestrator (B4#017，与 tools/py/doc_health_checker.py 双脚本对称)
 *
 * 功能说明：
 *     薄编排层（thin orchestrator），不重新实现已存在的能力，而是 delegate 到现有工具
 *     并仅补差缺能力（代码示例语法 / 依赖版本对照）。
 *
 *     检查项：
 *       - 文件路径准确性（delegate 到 doc_dependency_tracer.py）
 *       - 代码示例语法有效性（新增最小检查）
 *       - 依赖版本对照（新增最小检查）
 *       - frontmatter 摘要合规（delegate 到 summary_validator.py）
 *
 * 使用方法：
 *     # 单文件子集检查（仅链接 + 代码示例 + frontmatter）
 *     node tools/js/doc_health_checker.js --file dev_docs/api_layer.md
 *
 *     # 按 mode 触发的组合检查
 *     node tools/js/doc_health_checker.js --mode quick      # 仅 file-paths
 *     node tools/js/doc_health_checker.js --mode standard   # quick + code-samples
 *     node tools/js/doc_health_checker.js --mode deep       # standard + dependencies + frontmatter
 *
 *     # 显式单项检查
 *     node tools/js/doc_health_checker.js --check-code-samples [--doc-dir DIR]
 *     node tools/js/doc_health_checker.js --check-file-paths  [--doc-dir DIR]
 *     node tools/js/doc_health_checker.js --check-dependencies [--doc-dir DIR]
 *
 *     # 综合检查
 *     node tools/js/doc_health_checker.js --full-check
 *
 * 参数说明：
 *     --file FILE              单文件子集检查
 *     --mode quick|standard|deep   预设组合模式
 *     --check-file-paths       文件路径准确性
 *     --check-code-samples     代码示例有效性
 *     --check-dependencies     依赖版本对照
 *     --full-check             全部检查
 *     --doc-dir DIR            文档目录（默认 dev_docs/）
 *     --output FILE            JSON 输出（默认 stdout）
 *     --timeout SECONDS        子工具超时（默认 30）
 *
 * 退出码：
 *     - 0: 健康（无 issue）
 *     - 1: 发现问题
 *     - 2: 工具或参数错误
 *
 * 设计决策（V3.0 红线）：
 *     - 零依赖：仅 fs / path / child_process
 *     - 双脚本对称：与 tools/py/doc_health_checker.py 完全镜像
 *     - Hybrid 模式：delegate > 重写
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const TOOLS_PY = path.join(ROOT, 'tools', 'py');

function parseArgs() {
  const argv = process.argv.slice(2);
  const out = { timeout: 30 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = argv[i + 1];
    switch (a) {
      case '--file': out.file = next; i++; break;
      case '--mode': out.mode = next; i++; break;
      case '--check-file-paths': out.checkFilePaths = true; break;
      case '--check-code-samples': out.checkCodeSamples = true; break;
      case '--check-dependencies': out.checkDependencies = true; break;
      case '--full-check': out.fullCheck = true; break;
      case '--doc-dir': out.docDir = next; i++; break;
      case '--output': out.output = next; i++; break;
      case '--timeout': out.timeout = parseInt(next, 10) || 30; i++; break;
      case '-h':
      case '--help': out.help = true; break;
    }
  }
  return out;
}

function runPyTool(args, timeoutSec) {
  const res = spawnSync('python3', [path.join(TOOLS_PY, args[0]), ...args.slice(1)], {
    cwd: ROOT,
    encoding: 'utf8',
    timeout: timeoutSec * 1000
  });
  if (res.error) return { code: 2, stdout: '', stderr: String(res.error.message) };
  return { code: res.status == null ? 124 : res.status, stdout: res.stdout || '', stderr: res.stderr || '' };
}

function checkFilePaths(targets, timeoutSec) {
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  const issues = [];
  for (const f of targets) {
    if (!fs.existsSync(f)) {
      issues.push({ file: f, type: 'doc_missing', message: '目标文档不存在' });
      continue;
    }
    const r = runPyTool(['doc_dependency_tracer.py', '--doc', f, '--strategy', 'all', '--output-format', 'json'], timeoutSec);
    if (r.code !== 0 && r.code !== 1) {
      issues.push({ file: f, type: 'tool_error', message: (r.stderr || '').slice(0, 200) });
      continue;
    }
    let data = {};
    try { if (r.stdout.trim()) data = JSON.parse(r.stdout); } catch (e) { /* ignore */ }
    const broken = data.broken_references || data.missing_files || [];
    for (const b of broken) issues.push({ file: f, type: 'broken_link', target: b });
  }
  return { checked: targets.length, issues };
}

function extractCodeBlocks(text) {
  const re = /```([a-zA-Z0-9_+\-]*)\n([\s\S]*?)```/g;
  const out = [];
  let m;
  while ((m = re.exec(text)) !== null) {
    out.push({ lang: (m[1] || 'text').toLowerCase(), code: m[2] });
  }
  return out;
}

function checkJsBlock(code) {
  // 最小语法检查：尝试 Function 构造（不执行）
  try {
    new Function(code);
    return null;
  } catch (e) {
    return `SyntaxError: ${e.message}`;
  }
}

function checkBashBlock(code) {
  const issues = [];
  const lines = code.split('\n').slice(0, 5);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('#') || line.startsWith('$')) continue;
    const first = line.split(/\s+/)[0];
    if (['rm', 'sudo', 'kill'].includes(first)) issues.push(`L${i + 1}: 危险命令 ${first}`);
  }
  return issues.length ? issues.join('; ') : null;
}

function checkCodeSamples(targets) {
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  const issues = [];
  let blocksTotal = 0;
  for (const f of targets) {
    if (!fs.existsSync(f)) continue;
    let text;
    try { text = fs.readFileSync(f, 'utf8'); } catch (e) {
      issues.push({ file: f, type: 'read_error', message: String(e.message).slice(0, 100) });
      continue;
    }
    const blocks = extractCodeBlocks(text);
    blocks.forEach((b, idx) => {
      blocksTotal++;
      let err = null;
      if (['javascript', 'js', 'node'].includes(b.lang)) err = checkJsBlock(b.code);
      else if (['bash', 'sh', 'shell'].includes(b.lang)) err = checkBashBlock(b.code);
      // python / 其他暂不在 JS 端检查（避免误报；交给 .py 版处理）
      if (err) issues.push({ file: f, type: 'code_sample', block: idx, lang: b.lang, message: err });
    });
  }
  return { checked: blocksTotal, issues };
}

const DEP_PATTERN = /\b([a-zA-Z][\w\-]*)\s*[~^>=]+\s*([0-9][\w\.\-]*)/g;

function checkDependencies(targets, projectRoot) {
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  projectRoot = projectRoot || ROOT;
  const declared = {};
  const pkgPath = path.join(projectRoot, 'package.json');
  if (fs.existsSync(pkgPath)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      Object.assign(declared, pkg.dependencies || {});
      Object.assign(declared, pkg.devDependencies || {});
    } catch (e) { /* ignore */ }
  }
  const reqPath = path.join(projectRoot, 'requirements.txt');
  if (fs.existsSync(reqPath)) {
    const lines = fs.readFileSync(reqPath, 'utf8').split('\n');
    for (const ln of lines) {
      const t = ln.trim();
      if (!t || t.startsWith('#')) continue;
      const m = t.match(/([A-Za-z][\w\-]*)\s*[~=<>]=?\s*([\w\.\-]+)/);
      if (m) declared[m[1]] = m[2];
    }
  }
  const issues = [];
  for (const f of targets) {
    if (!fs.existsSync(f)) continue;
    const text = fs.readFileSync(f, 'utf8');
    let m;
    DEP_PATTERN.lastIndex = 0;
    while ((m = DEP_PATTERN.exec(text)) !== null) {
      const name = m[1], ver = m[2];
      const actual = declared[name];
      const stripPrefix = (s) => s.replace(/^[~^>=<]+/, '');
      if (actual && stripPrefix(actual) !== stripPrefix(ver)) {
        issues.push({ file: f, type: 'dep_version_drift', package: name, doc_says: ver, manifest_says: actual });
      }
    }
  }
  return { checked: targets.length, issues };
}

function checkFrontmatter(targets, timeoutSec) {
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  const issues = [];
  for (const f of targets) {
    const r = runPyTool(['summary_validator.py', '--file', f, '--strict'], timeoutSec);
    if (!r.stdout.trim()) {
      issues.push({ file: f, type: 'tool_error', message: (r.stderr || '').slice(0, 200) });
      continue;
    }
    let data;
    try { data = JSON.parse(r.stdout); } catch (e) {
      issues.push({ file: f, type: 'tool_error', message: 'non-JSON output' });
      continue;
    }
    if (!(data.data && data.data.valid)) {
      const errors = (data.data && data.data.errors) || [];
      for (const e of errors) issues.push({ file: f, type: 'frontmatter', message: e });
    }
  }
  return { checked: targets.length, issues };
}

function walkMd(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  const stack = [dir];
  while (stack.length) {
    const cur = stack.pop();
    let entries;
    try { entries = fs.readdirSync(cur, { withFileTypes: true }); } catch (e) { continue; }
    for (const ent of entries) {
      const full = path.join(cur, ent.name);
      if (ent.isDirectory()) stack.push(full);
      else if (ent.isFile() && ent.name.endsWith('.md')) out.push(full);
    }
  }
  return out;
}

function collectTargets(args) {
  // Fallback 优先级（与 B3#021 同源 dogfood 治理）：
  //   1. CLI 显式 --file → 仅该文件
  //   2. CLI 显式 --doc-dir → 使用之
  //   3. dev_docs/ 存在（用户项目）
  //   4. dev/ 存在（框架自审 / dogfood）
  //   5. 当前目录
  if (args.file) return [args.file];
  const candidates = args.docDir ? [args.docDir] : [
    path.join(ROOT, 'dev_docs'),
    path.join(ROOT, 'dev'),
    '.'
  ];
  for (const d of candidates) {
    if (fs.existsSync(d) && fs.statSync(d).isDirectory()) return walkMd(d);
  }
  return [];
}

function showHelp() {
  console.log(`AICC 文档健康检查工具（hybrid orchestrator）

用法：
  node tools/js/doc_health_checker.js --file FILE
  node tools/js/doc_health_checker.js --mode quick|standard|deep
  node tools/js/doc_health_checker.js --check-file-paths | --check-code-samples | --check-dependencies
  node tools/js/doc_health_checker.js --full-check
  [--doc-dir DIR] [--output FILE] [--timeout SECONDS]
`);
}

function main() {
  const args = parseArgs();
  if (args.help) { showHelp(); process.exit(0); }

  const doPaths = !!(args.checkFilePaths || args.fullCheck || ['quick', 'standard', 'deep'].includes(args.mode) || args.file);
  const doSamples = !!(args.checkCodeSamples || args.fullCheck || ['standard', 'deep'].includes(args.mode) || args.file);
  const doDeps = !!(args.checkDependencies || args.fullCheck || args.mode === 'deep');
  const doFm = !!(args.fullCheck || args.mode === 'deep' || args.file);

  if (!(doPaths || doSamples || doDeps || doFm)) {
    console.error('错误：请提供 --file / --mode / --check-* / --full-check 之一');
    process.exit(2);
  }

  const targets = collectTargets(args);
  if (targets.length === 0) {
    console.log(JSON.stringify({ summary: { passed: false }, error: 'no targets found' }));
    process.exit(2);
  }

  const checks = {};
  if (doPaths) checks.file_paths = checkFilePaths(targets, args.timeout);
  if (doSamples) checks.code_samples = checkCodeSamples(targets);
  if (doDeps) checks.dependencies = checkDependencies(targets);
  if (doFm) checks.frontmatter = checkFrontmatter(targets, args.timeout);

  const totalIssues = Object.values(checks).reduce((s, v) => s + v.issues.length, 0);
  const result = {
    summary: {
      file: args.file,
      doc_dir: args.docDir || 'dev_docs',
      modes: { file: !!args.file, mode: args.mode, full_check: !!args.fullCheck },
      targets_count: targets.length,
      total_issues: totalIssues,
      passed: totalIssues === 0
    },
    checks
  };
  const output = JSON.stringify(result, null, 2);
  if (args.output) fs.writeFileSync(args.output, output, 'utf8');
  else console.log(output);
  process.exit(totalIssues === 0 ? 0 : 1);
}

main();
