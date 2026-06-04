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
const CONTRACTS_DIR = path.join(ROOT, 'core', 'contracts');

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
      case '--check-required-sections': out.checkRequiredSections = true; break;
      case '--check-template-residue': out.checkTemplateResidue = true; break;
      case '--check-run-record-integrity': out.checkRunRecordIntegrity = true; break;
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
  const transformed = code
    .replace(/^\s*import\s+[^;\n]+;?\s*$/gm, '')
    .replace(/^\s*export\s+default\s+/gm, 'const __default__ = ')
    .replace(/^\s*export\s+(const|let|var|function|class)\s+/gm, '$1 ')
    .replace(/\bimport\.meta\b/g, '({})');
  try {
    new Function(transformed);
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
  let checked = 0;
  for (const f of targets) {
    if (f.split(path.sep).includes('_analysis')) {
      let hasFrontmatter = false;
      try { hasFrontmatter = fs.readFileSync(f, 'utf8').trimStart().startsWith('---'); } catch (e) { hasFrontmatter = false; }
      if (!hasFrontmatter) continue;
    }
    checked++;
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
  return { checked, issues };
}

function loadMainDocRequiredTitles() {
  const contractPath = path.join(CONTRACTS_DIR, 'main_doc_contract.yaml');
  if (!fs.existsSync(contractPath)) return [];
  return fs.readFileSync(contractPath, 'utf8')
    .split('\n')
    .map((line) => {
      const match = line.match(/^\s*title:\s*"?(.*?)"?\s*$/);
      return match ? match[1] : null;
    })
    .filter(Boolean);
}

function loadRunRecordContract() {
  const contractPath = path.join(CONTRACTS_DIR, 'run_record_contract.yaml');
  const docs = { generation_plan: [], generation_progress: [] };
  if (!fs.existsSync(contractPath)) return docs;
  const lines = fs.readFileSync(contractPath, 'utf8').split('\n');
  let currentDoc = null;
  let currentKey = null;
  for (const line of lines) {
    const anyDocMatch = line.match(/^\s{2}([A-Za-z0-9_]+):\s*$/);
    if (anyDocMatch && !Object.prototype.hasOwnProperty.call(docs, anyDocMatch[1])) {
      currentDoc = null;
      currentKey = null;
      continue;
    }
    const docMatch = line.match(/^\s{2}(generation_plan|generation_progress):\s*$/);
    if (docMatch) {
      currentDoc = docMatch[1];
      currentKey = null;
      continue;
    }
    const keyMatch = line.match(/^\s{4}(required_headings|required_fields):\s*$/);
    if (keyMatch && currentDoc) {
      currentKey = keyMatch[1];
      continue;
    }
    const itemMatch = line.match(/^\s{6}-\s*"(.*?)"\s*$/);
    if (itemMatch && currentDoc && currentKey) {
      docs[currentDoc].push(itemMatch[1]);
    }
  }
  return docs;
}

function extractH2Titles(text) {
  const titles = [];
  const re = /^##\s+(.+?)\s*$/gm;
  let match;
  while ((match = re.exec(text)) !== null) {
    titles.push(match[1].trim());
  }
  return titles;
}

function checkRequiredSections(targets) {
  const requiredTitles = loadMainDocRequiredTitles();
  if (!targets || targets.length === 0 || requiredTitles.length === 0) {
    return { checked: 0, issues: [] };
  }
  const issues = [];
  let checked = 0;
  for (const file of targets) {
    if (path.basename(file) !== 'AI_Coding_Context.md' || !fs.existsSync(file)) continue;
    checked++;
    const headings = new Set(extractH2Titles(fs.readFileSync(file, 'utf8')));
    for (const title of requiredTitles) {
      if (!headings.has(title)) {
        issues.push({ file, type: 'missing_required_section', section: title, message: `缺少必需章节: ${title}` });
      }
    }
  }
  return { checked, issues };
}

const RESIDUE_PATTERNS = [
  { re: /\[填写\]/g, label: '[填写]' },
  { re: /\[PROJECT_NAME\]/g, label: '[PROJECT_NAME]' },
  { re: /\bTODO\b/g, label: 'TODO' },
  { re: /待补充/g, label: '待补充' },
  { re: /^\|\s*\.\.\.\s*\|/gm, label: 'ellipsis_table_row' }
];

function isTemplateResidueScanLine(line) {
  const stripped = line.trim();
  if (!stripped.includes('rg ') && !stripped.includes('ripgrep')) return false;
  return ['<marker:T-O-D-O>', '<marker:T-B-D>', '<marker:fill>', '待补充', 'TODO', 'TBD']
    .some((marker) => stripped.includes(marker));
}

function templateResidueExemptLines(lines) {
  const exempt = new Set();
  let inFence = false;
  let fenceStart = '';
  lines.forEach((line, idx) => {
    const stripped = line.trim();
    if (stripped.startsWith('```')) {
      if (!inFence) {
        inFence = true;
        fenceStart = stripped.toLowerCase();
      } else {
        inFence = false;
        fenceStart = '';
      }
      return;
    }
    if (!isTemplateResidueScanLine(line)) return;
    if (inFence && ['bash', 'sh', 'shell', 'zsh', 'console'].some((lang) => fenceStart.includes(lang))) {
      exempt.add(idx + 1);
    } else if (stripped.startsWith('|') && stripped.endsWith('|')) {
      exempt.add(idx + 1);
    } else if (stripped.includes('`')) {
      exempt.add(idx + 1);
    }
  });
  return exempt;
}

function checkTemplateResidue(targets) {
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  const issues = [];
  let checked = 0;
  for (const file of targets) {
    if (!fs.existsSync(file)) continue;
    checked++;
    const text = fs.readFileSync(file, 'utf8');
    const lines = text.split('\n');
    const exemptLines = templateResidueExemptLines(lines);
    for (const { re, label } of RESIDUE_PATTERNS) {
      re.lastIndex = 0;
      let match;
      while ((match = re.exec(text)) !== null) {
        const line = text.slice(0, match.index).split('\n').length;
        if (exemptLines.has(line)) continue;
        issues.push({ file, type: 'template_residue', marker: label, line, message: `检测到模板残留: ${label}` });
      }
    }
    lines.forEach((line, index) => {
      const stripped = line.trim();
      if (stripped === '...' || stripped === '- ...') {
        issues.push({ file, type: 'template_residue', marker: '...', line: index + 1, message: '检测到省略型占位符' });
      }
    });
  }
  return { checked, issues };
}

const PHASE1_REVIEW_FIELDS = [
  'review_trigger',
  'review_started_at',
  'review_completed_at',
  'reviewed_files',
  'machine_checks',
  'manual_review_summary',
  'writeback_summary',
  'blocker_count',
  'warning_count',
  'waived_issue_count',
  'phase1_recommendation',
  'user_confirmation_status',
  'formal_generation_authorization',
  'authorization_source_summary',
];

const PHASE1_REQUIRED_TOOL_IMPLEMENTATIONS = new Set([
  'summary_validator|python',
  'doc_health_checker|python',
  'doc_health_checker|js',
  'semantic_review_checker|python',
  'semantic_review_checker|js',
]);

const HEALTH_CHECK_REQUIRED_TOOLS = new Set([
  'summary_validator|python',
  'doc_health_checker|python',
  'doc_health_checker|js',
  'semantic_review_checker|python',
  'semantic_review_checker|js',
]);

const ACCEPTED_ISSUE_REQUIRED_FIELDS = [
  'issue_id',
  'tool',
  'implementation',
  'file',
  'issue_type',
  'original_status',
  'accepted_reason',
  'residual_risk',
  'follow_up',
];

const NON_WAIVABLE_ACCEPTED_ISSUE_TYPES = [
  'sensitive',
  'secret',
  'ai_rules',
  'runtime_stack',
  'required_doc',
  'doc_missing',
  'health_report',
];

function isPhase1PassOrRecommendation(text) {
  if (!text.includes('Phase 1') && !text.toLowerCase().includes('phase1')) return false;
  return /\bPASS\b|verdict\s*=\s*PASS|建议通过|可进入正式文档生成/i.test(text);
}

function hasUserConfirmation(text) {
  return /当前状态\*\*:\s*已获用户确认|user_confirmation_status\*\*:\s*(confirmed|已确认)/i.test(text);
}

function hasFormalGenerationAuthorization(text) {
  return [
    /user_confirmation_status\*\*:\s*(confirmed|已确认)/i,
    /当前状态\*\*:\s*已获用户确认/i,
    /formal_generation_authorization\*\*:\s*(confirmed|explicit|已授权|已确认)/i,
    /user_authorized_formal_generation\*\*:\s*(true|yes|是)/i,
    /授权来源\s*[:：].*(用户|user)/i,
    /明确授权跳过审核/i,
    /用户确认.*正式文档生成/i,
  ].some((pattern) => pattern.test(text));
}

function isAnalysisPath(file) {
  return file.split(path.sep).includes('_analysis');
}

function isFormalDocPath(file) {
  const name = path.basename(file);
  if (name === 'health_check_report.md' || isAnalysisPath(file)) return false;
  return true;
}

function formalDocPaths(targets) {
  const paths = targets.filter((target) => fs.existsSync(target) && target.endsWith('.md') && isFormalDocPath(target));
  if (paths.length <= 1 && paths.every((target) => path.basename(target) === 'AI_Coding_Context.md')) return [];
  return paths;
}

function nearestDevDocsDir(file) {
  let current = fs.existsSync(file) && fs.statSync(file).isDirectory() ? file : path.dirname(file);
  while (current && current !== path.dirname(current)) {
    if (path.basename(current) === 'dev_docs') return current;
    current = path.dirname(current);
  }
  return null;
}

function findAnalysisFileNearTargets(targets, filename) {
  for (const target of targets) {
    if (!fs.existsSync(target)) continue;
    const devDocsDir = nearestDevDocsDir(target);
    if (!devDocsDir) continue;
    const candidate = path.join(devDocsDir, '_analysis', filename);
    if (fs.existsSync(candidate)) return candidate;
  }
  return null;
}

function extractSectionAfterHeading(text, heading) {
  const lines = text.split('\n');
  let start = -1;
  const headingRe = new RegExp(`^##+\\s+${heading}\\s*$`, 'i');
  for (let i = 0; i < lines.length; i++) {
    if (headingRe.test(lines[i])) {
      start = i + 1;
      break;
    }
  }
  if (start < 0) return '';
  let end = lines.length;
  for (let i = start; i < lines.length; i++) {
    if (/^##+\s+/.test(lines[i])) {
      end = i;
      break;
    }
  }
  return lines.slice(start, end).join('\n');
}

function parseFirstMarkdownTable(section) {
  const rows = [];
  section.split('\n').forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) rows.push(trimmed);
  });
  if (rows.length < 2) return { headers: [], body: [] };
  const cells = (row) => row.replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim());
  return {
    headers: cells(rows[0]),
    body: rows.slice(2).filter((row) => !/^\|\s*-+/.test(row)).map(cells),
  };
}

function tableRowsAsDicts(headers, rows) {
  return rows.map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] || ''])));
}

function extractFinalVerdict(text) {
  const match = text.match(/(?:最终\s*)?verdict\*\*?\s*[:：]\s*\*{0,2}([A-Z_]+)/i) || text.match(/(?:最终\s*)?verdict\s*=\s*([A-Z_]+)/i);
  return match ? match[1].toUpperCase() : '';
}

function checkHealthReportSelfResidue(file, text) {
  const issues = [];
  RESIDUE_PATTERNS.forEach(({ re, label }) => {
    re.lastIndex = 0;
    let match;
    while ((match = re.exec(text)) !== null) {
      const line = text.slice(0, match.index).split('\n').length;
      issues.push({ file, type: 'health_report_self_template_residue', severity: 'blocker', marker: label, line, message: `健康报告自身包含模板残留: ${label}` });
    }
  });
  return issues;
}

function checkAcceptedIssuesTable(file, text, hasAcceptedMachineCheck) {
  const issues = [];
  const section = extractSectionAfterHeading(text, 'accepted_issues');
  if (!section) {
    if (hasAcceptedMachineCheck || text.toLowerCase().includes('accepted')) {
      issues.push({ file, type: 'health_report_accepted_issue_missing_detail', severity: 'blocker', message: '存在 accepted issue，但缺少 accepted_issues 结构化章节' });
    }
    return issues;
  }
  if (section.includes('无 accepted issue') && !hasAcceptedMachineCheck) return issues;
  const { headers, body } = parseFirstMarkdownTable(section);
  if (headers.length === 0) {
    if (hasAcceptedMachineCheck) {
      issues.push({ file, type: 'health_report_accepted_issue_missing_detail', severity: 'blocker', message: 'accepted_issues 必须使用可解析表格逐项记录' });
    }
    return issues;
  }
  const missing = ACCEPTED_ISSUE_REQUIRED_FIELDS.filter((field) => !headers.includes(field));
  if (missing.length > 0) {
    issues.push({ file, type: 'health_report_accepted_issue_missing_detail', severity: 'blocker', missing, message: 'accepted_issues 表缺少必填列' });
    return issues;
  }
  tableRowsAsDicts(headers, body).forEach((row) => {
    const emptyFields = ACCEPTED_ISSUE_REQUIRED_FIELDS.filter((field) => !row[field]);
    if (emptyFields.length > 0) {
      issues.push({ file, type: 'health_report_accepted_issue_missing_detail', severity: 'blocker', issue_id: row.issue_id, missing: emptyFields, message: 'accepted issue 缺少原因、残余风险或 follow-up 等必填信息' });
    }
    const issueType = (row.issue_type || '').toLowerCase();
    if (NON_WAIVABLE_ACCEPTED_ISSUE_TYPES.some((marker) => issueType.includes(marker))) {
      issues.push({ file, type: 'health_report_accepted_issue_not_allowed', severity: 'blocker', issue_id: row.issue_id, issue_type: row.issue_type, message: '该类型问题不得通过 accepted issue 豁免' });
    }
  });
  return issues;
}

function checkHealthReport(file, text, targetCount) {
  const issues = [];
  const verdict = extractFinalVerdict(text);
  const { headers, body } = parseFirstMarkdownTable(extractSectionAfterHeading(text, 'machine_checks'));
  if (headers.length === 0) {
    issues.push({ file, type: 'health_report_machine_checks_missing', severity: 'blocker', message: 'health_check_report.md 缺少结构化 machine_checks 表' });
    return { issues, verdict };
  }
  const required = ['round', 'tool', 'implementation', 'command', 'exit_code', 'issue_count', 'status', 'disposition'];
  const missing = required.filter((field) => !headers.includes(field));
  if (missing.length > 0) {
    issues.push({ file, type: 'health_report_machine_checks_missing', severity: 'blocker', missing, message: 'health_check_report.md 的 machine_checks 表缺少必需列' });
    return { issues, verdict };
  }
  const rows = tableRowsAsDicts(headers, body);
  const seen = new Set(rows.map((row) => `${row.tool}|${row.implementation}`));
  HEALTH_CHECK_REQUIRED_TOOLS.forEach((key) => {
    if (!seen.has(key)) {
      const [tool, implementation] = key.split('|');
      issues.push({ file, type: 'health_report_machine_checks_missing', severity: 'blocker', tool, implementation, message: `health_check_report.md 缺少 ${implementation} ${tool} 运行记录` });
    }
  });
  let hasFailed = false;
  let hasAccepted = false;
  let hasUnacceptedFailure = false;
  rows.forEach((row) => {
    if (!/^\d+$/.test(row.exit_code || '') || !/^\d+$/.test(row.issue_count || '')) {
      issues.push({ file, type: 'health_report_machine_checks_missing', severity: 'blocker', message: 'machine_checks exit_code 与 issue_count 必须为数字' });
      return;
    }
    const failed = Number(row.exit_code) !== 0 || Number(row.issue_count) !== 0 || ['FAIL', 'ERROR'].includes((row.status || '').toUpperCase());
    const disposition = (row.disposition || '').toLowerCase();
    if (failed) {
      hasFailed = true;
      if (disposition === 'accepted') hasAccepted = true;
      else if (!['fixed', 'verified'].includes(disposition)) hasUnacceptedFailure = true;
    }
  });
  if (verdict === 'PASS' && (hasFailed || hasAccepted)) {
    issues.push({ file, type: 'health_report_verdict_conflicts_with_checks', severity: 'blocker', message: 'health_check_report.md 写 PASS，但 machine_checks 存在失败或 accepted issue' });
  }
  if (['PASS', 'PASS_WITH_ACCEPTED_ISSUES', '建议通过'].includes(verdict) && hasUnacceptedFailure) {
    issues.push({ file, type: 'health_report_verdict_conflicts_with_checks', severity: 'blocker', message: 'health_check_report.md 存在未修复/未豁免的失败检查' });
  }
  if (hasAccepted && verdict === 'PASS') {
    issues.push({ file, type: 'health_report_verdict_conflicts_with_checks', severity: 'blocker', message: '存在 accepted issue 时最终结论不得写裸 PASS' });
  }
  issues.push(...checkAcceptedIssuesTable(file, text, hasAccepted));
  issues.push(...checkHealthReportSelfResidue(file, text));
  const countRe = /全部\s*(\d+)\s*个(?:产物|文档)|已完成\s*(\d+)\s*\/\s*(\d+)\s*个产物|总文件数\s*(\d+)/g;
  let match;
  while ((match = countRe.exec(text)) !== null) {
    const expected = Number(match[1] || match[3] || match[4]);
    if (expected !== targetCount) {
      issues.push({ file, type: 'artifact_count_mismatch', severity: 'blocker', expected, actual: targetCount, message: '健康报告或进度记录中的产物数量与实际 Markdown 文件数量不一致' });
    }
  }
  return { issues, verdict };
}

function checkMachineChecksTable(file, text, phase1Pass) {
  const issues = [];
  const { headers, body } = parseFirstMarkdownTable(extractSectionAfterHeading(text, 'machine_checks'));
  if (headers.length === 0) {
    issues.push({
      file,
      type: 'machine_check_table_missing',
      severity: 'blocker',
      message: 'Phase 1 建议通过时必须用可解析表格记录 machine_checks',
    });
    return issues;
  }
  const required = ['phase', 'tool', 'implementation', 'command', 'exit_code', 'issue_count', 'status', 'required', 'disposition'];
  const missing = required.filter((field) => !headers.includes(field));
  if (missing.length > 0) {
    issues.push({ file, type: 'machine_check_table_column_missing', severity: 'blocker', missing, message: 'machine_checks 表缺少必需列' });
    return issues;
  }
  const rows = tableRowsAsDicts(headers, body);
  const seen = new Set(rows.map((row) => `${row.tool}|${row.implementation}`));
  PHASE1_REQUIRED_TOOL_IMPLEMENTATIONS.forEach((key) => {
    if (!seen.has(key)) {
      const [tool, implementation] = key.split('|');
      issues.push({ file, type: 'machine_check_required_tool_missing', severity: 'blocker', tool, implementation, message: `machine_checks 缺少工具运行记录: ${implementation} ${tool}` });
    }
  });
  let hasRequiredFailure = false;
  rows.forEach((row) => {
    if (!/^\d+$/.test(row.exit_code || '')) {
      issues.push({ file, type: 'machine_check_exit_code_missing', severity: 'blocker', message: 'machine_checks exit_code 必须为数字' });
    }
    if (!/^\d+$/.test(row.issue_count || '')) {
      issues.push({ file, type: 'machine_check_issue_count_mismatch', severity: 'blocker', message: 'machine_checks issue_count 必须为数字' });
    }
    const status = (row.status || '').toUpperCase();
    if ((row.required || '').toLowerCase() === 'yes' && status !== 'PASS') hasRequiredFailure = true;
    if (['FAIL', 'ERROR', 'UNAVAILABLE', 'NOT_RUN'].includes(status) && !row.disposition) {
      issues.push({ file, type: 'machine_check_unresolved_failure', severity: 'blocker', message: '失败的 machine_checks 行必须说明 disposition' });
    }
  });
  const verdict = extractPhase1Verdict(text);
  if (phase1Pass && hasRequiredFailure && verdict !== 'BLOCKED_NEEDS_FIX') {
    issues.push({ file, type: 'phase1_verdict_conflicts_with_machine_checks', severity: 'blocker', message: '存在 required machine check 失败时，phase1_review_verdict 必须为 BLOCKED_NEEDS_FIX' });
  }
  return issues;
}

function extractPhase1Verdict(text) {
  const { headers, body } = parseFirstMarkdownTable(extractSectionAfterHeading(text, 'phase1_review_verdict'));
  for (const row of tableRowsAsDicts(headers, body)) {
    if (row.field === 'verdict') return (row.value || '').trim().toUpperCase();
  }
  const match = text.match(/phase1_review_verdict[^\n]*(BLOCKED_NEEDS_FIX|READY_FOR_USER_REVIEW|USER_APPROVED_FORMAL_GENERATION)/i);
  return match ? match[1].toUpperCase() : '';
}

function checkCheckerStatusConflicts(file, text) {
  const issues = [];
  if (!text.includes('checker_status_matrix') || !text.includes('machine_checks')) return issues;
  const statusByTool = {};
  text.split('\n').forEach((line) => {
    if (!line.trim().startsWith('|')) return;
    ['summary_validator', 'doc_health_checker', 'semantic_review_checker', 'health_check_report'].forEach((tool) => {
      if (!line.includes(tool)) return;
      const match = line.match(/\b(PASS|FAIL|NOT_RUN|UNAVAILABLE|WAIVED_WITH_REASON)\b/);
      if (!match) return;
      if (!statusByTool[tool]) statusByTool[tool] = new Set();
      statusByTool[tool].add(match[1]);
    });
  });
  Object.entries(statusByTool).forEach(([tool, statuses]) => {
    if (statuses.has('NOT_RUN') && (statuses.has('PASS') || statuses.has('FAIL'))) {
      issues.push({ file, type: 'checker_status_matrix_conflict', severity: 'blocker', tool, statuses: Array.from(statuses).sort(), message: '同一工具在 checker_status_matrix 和 machine_checks 中出现 NOT_RUN 与已运行状态冲突' });
    }
  });
  return issues;
}

function checkPhase1ReviewRecord(file, text) {
  const issues = [];
  const phase1Pass = isPhase1PassOrRecommendation(text);
  const hasRecord = text.includes('Phase 1 方案复查记录');
  if (phase1Pass && !hasRecord) {
    issues.push({
      file,
      type: 'phase1_pass_without_plan_review_record',
      severity: 'blocker',
      message: '进度记录声明 Phase 1 PASS/建议通过，但缺少 Phase 1 方案复查记录',
    });
  }
  if (hasRecord) {
    PHASE1_REVIEW_FIELDS.forEach((field) => {
      if (!text.includes(field)) {
        issues.push({
          file,
          type: field === 'writeback_summary' ? 'phase1_plan_review_writeback_missing' : 'phase1_plan_review_record_missing',
          severity: phase1Pass ? 'blocker' : 'warning',
          missing: field,
          message: `Phase 1 方案复查记录缺少字段: ${field}`,
        });
      }
    });
    if (!text.includes('phase1_review_verdict')) {
      issues.push({
        file,
        type: 'phase1_review_verdict_missing',
        severity: phase1Pass ? 'blocker' : 'warning',
        message: 'Phase 1 方案复查记录缺少 phase1_review_verdict',
      });
    } else {
      const verdict = extractPhase1Verdict(text);
      if (!['BLOCKED_NEEDS_FIX', 'READY_FOR_USER_REVIEW', 'USER_APPROVED_FORMAL_GENERATION'].includes(verdict)) {
        issues.push({ file, type: 'phase1_review_verdict_invalid', severity: 'blocker', verdict, message: 'phase1_review_verdict 取值不合法' });
      }
      if (verdict === 'USER_APPROVED_FORMAL_GENERATION' && !hasUserConfirmation(text)) {
        issues.push({ file, type: 'phase1_approved_without_user_confirmation', severity: 'blocker', message: '没有用户确认时不得记录 USER_APPROVED_FORMAL_GENERATION' });
      }
    }
    issues.push(...checkMachineChecksTable(file, text, phase1Pass));
    issues.push(...checkCheckerStatusConflicts(file, text));
  }
  if (phase1Pass && text.includes('可进入正式文档生成') && !hasUserConfirmation(text)) {
    issues.push({
      file,
      type: 'phase1_pass_before_user_confirmation',
      severity: 'blocker',
      message: '用户确认前不得将 Phase 1 建议通过表述为可进入正式文档生成',
    });
  }
  return issues;
}

function checkRunRecordIntegrity(targets) {
  const contracts = loadRunRecordContract();
  if (!targets || targets.length === 0) return { checked: 0, issues: [] };
  const issues = [];
  let checked = 0;
  const existingMarkdownTargets = targets.filter((target) => fs.existsSync(target) && target.endsWith('.md'));
  const targetCount = existingMarkdownTargets.length;
  const healthReportPath = existingMarkdownTargets.find((target) => path.basename(target) === 'health_check_report.md') || findAnalysisFileNearTargets(targets, 'health_check_report.md');
  const progressPath = existingMarkdownTargets.find((target) => path.basename(target) === 'generation_progress.md');
  const progressText = progressPath ? fs.readFileSync(progressPath, 'utf8') : '';
  const formalDocs = formalDocPaths(targets);
  const mainDocPath = existingMarkdownTargets.find((target) => path.basename(target) === 'AI_Coding_Context.md');
  if (healthReportPath && mainDocPath && formalDocs.length === 0) formalDocs.push(mainDocPath);
  if (formalDocs.length > 0 && !healthReportPath) {
    issues.push({
      file: progressPath || formalDocs[0],
      type: 'formal_docs_without_health_report',
      severity: 'blocker',
      formal_docs: formalDocs,
      message: '正式文档已生成，但缺少 dev_docs/_analysis/health_check_report.md',
    });
  }
  if (formalDocs.length > 0 && progressText && !hasFormalGenerationAuthorization(progressText)) {
    issues.push({
      file: progressPath,
      type: 'formal_docs_generated_without_phase1_confirmation',
      severity: 'blocker',
      formal_docs: formalDocs,
      message: '正式文档已生成，但 generation_progress.md 缺少用户确认或明确授权记录',
    });
  }
  let healthReportIssues = [];
  let healthReportVerdict = '';
  if (healthReportPath) {
    checked++;
    const healthText = fs.readFileSync(healthReportPath, 'utf8');
    const healthResult = checkHealthReport(healthReportPath, healthText, targetCount);
    healthReportIssues = healthResult.issues;
    healthReportVerdict = healthResult.verdict;
    issues.push(...healthReportIssues);
  }
  for (const file of targets) {
    const name = path.basename(file);
    if (!['generation_plan.md', 'generation_progress.md'].includes(name) || !fs.existsSync(file)) continue;
    checked++;
    const text = fs.readFileSync(file, 'utf8');
    const requiredItems = name === 'generation_plan.md' ? contracts.generation_plan : contracts.generation_progress;
    requiredItems.forEach((item) => {
      if (!text.includes(item)) {
        issues.push({ file, type: 'run_record_integrity', missing: item, message: `运行记录缺少必需项: ${item}` });
      }
    });
    const statusMatch = text.match(/\*\*当前状态\*\*:\s*([^\n]+)/);
    const currentStatus = statusMatch ? statusMatch[1].trim() : '';
    if (name === 'generation_progress.md' && currentStatus === '已完成' && !text.includes('health_check_report')) {
      issues.push({
        file,
        type: 'run_record_integrity',
        missing: 'health_check_report',
        message: '进度记录声明已完成，但未见 health_check_report 留痕'
      });
    }
    if (name === 'generation_progress.md') {
      const hasSummaryValidatorPass = /summary_validator[^\n|]*(?:PASS|通过)/i.test(text);
      const claimsValidationPassed = /验证(?:已)?通过|检查(?:已)?通过|验收(?:已)?通过/.test(text);
      const hasRequiredQualityTools = text.includes('doc_health_checker') && text.includes('semantic_review_checker');
      if (hasSummaryValidatorPass && claimsValidationPassed && !hasRequiredQualityTools) {
        issues.push({
          file,
          type: 'summary_only_validation_misrepresented',
          severity: 'blocker',
          message: '进度记录只记录 summary_validator 通过，却表述为整体验证通过',
        });
      }
      const firstReleaseDone = ['首版建议通过', '首版验收 verdict = PASS', '首版验收完成', 'Step 9/9 已完成'].some((marker) => text.includes(marker));
      if (firstReleaseDone && !healthReportPath) {
        issues.push({ file, type: 'progress_completion_without_valid_health_report', severity: 'blocker', message: '进度记录声明首版完成或建议通过，但缺少 health_check_report.md' });
      }
      if (firstReleaseDone && healthReportPath && (healthReportIssues.length > 0 || ['FAIL', ''].includes(healthReportVerdict))) {
        issues.push({ file, type: 'progress_completion_without_valid_health_report', severity: 'blocker', message: '进度记录声明首版完成或建议通过，但健康报告未通过结构化验收' });
      }
      const countRe = /全部\s*(\d+)\s*个(?:产物|文档)|已完成\s*(\d+)\s*\/\s*(\d+)\s*个产物|总文件数\s*(\d+)/g;
      let countMatch;
      while ((countMatch = countRe.exec(text)) !== null) {
        const expected = Number(countMatch[1] || countMatch[3] || countMatch[4]);
        if (expected !== targetCount) {
          issues.push({ file, type: 'artifact_count_mismatch', severity: 'blocker', expected, actual: targetCount, message: '进度记录中的产物数量与实际 Markdown 文件数量不一致' });
        }
      }
      issues.push(...checkPhase1ReviewRecord(file, text));
      const lastUpdates = Array.from(text.matchAll(/\*\*最后更新\*\*:\s*([^\n]+)/g)).map((match) => match[1].trim());
      const uniqueLastUpdates = Array.from(new Set(lastUpdates)).sort();
      if (uniqueLastUpdates.length > 1) {
        issues.push({
          file,
          type: 'progress_metadata_mismatch',
          field: '最后更新',
          values: uniqueLastUpdates,
          message: '进度记录中存在多个不一致的最后更新时间',
        });
      }
      const progressLabels = Array.from(text.matchAll(/\*\*([^*\n]*进度[^*\n]*)\*\*:\s*[^\n]*\d+%/g)).map((match) => match[1].trim());
      const ambiguous = progressLabels.filter((label) => label === '进度');
      if (ambiguous.length > 1) {
        issues.push({
          file,
          type: 'ambiguous_progress_percentage',
          message: '同一进度文件中存在多个未标明含义的百分比进度',
        });
      }
    }
    if (name === 'generation_plan.md') {
      if (text.includes('Package.resolved') && ['Package.resolved 待确认', '检查 Package.resolved', '未发现 Package.resolved'].some((marker) => text.includes(marker))) {
        issues.push({
          file,
          type: 'stale_review_conclusion',
          fact: 'Package.resolved',
          message: '文档已引用 Package.resolved，但正文仍残留依赖待确认旧结论',
        });
      }
    }
  }
  return { checked, issues };
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
  node tools/js/doc_health_checker.js --check-required-sections | --check-template-residue | --check-run-record-integrity
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
  const doRequired = !!(args.checkRequiredSections || args.fullCheck || args.mode === 'deep');
  const doResidue = !!(args.checkTemplateResidue || args.fullCheck || args.mode === 'deep');
  const doRunRecords = !!(args.checkRunRecordIntegrity || args.fullCheck || args.mode === 'deep');

  if (!(doPaths || doSamples || doDeps || doFm || doRequired || doResidue || doRunRecords)) {
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
  if (doRequired) checks.required_sections = checkRequiredSections(targets);
  if (doResidue) checks.template_residue = checkTemplateResidue(targets);
  if (doRunRecords) checks.run_record_integrity = checkRunRecordIntegrity(targets);

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
