#!/usr/bin/env node
/**
 * 框架契约检查器
 *
 * 最小能力：
 * - 检查主文档模板是否满足 main_doc_contract.yaml 必需章节
 * - 检查 workflow 是否引入了未被 spec 收录的标准产物路径
 * - 提供框架自检模式
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const CONTRACTS_DIR = path.join(ROOT, 'core', 'contracts');
const DEFAULT_TEMPLATE = path.join(ROOT, 'templates', 'AI_Coding_Context_TEMPLATE.md');
const DEFAULT_SPEC = path.join(ROOT, 'core', 'framework_spec.md');
const DEFAULT_WORKFLOWS = [
  path.join(ROOT, 'workflows', 'generation_workflow.md'),
  path.join(ROOT, 'workflows', 'path_a_first_generation.md'),
];
const OBSOLETE_STANDARD_PATHS = new Set([
  'dev_docs/plans/features/',
  'dev_docs/plans/bugfixes/',
]);

function parseArgs() {
  const argv = process.argv.slice(2);
  const out = {
    contract: path.join(CONTRACTS_DIR, 'main_doc_contract.yaml'),
    spec: DEFAULT_SPEC,
    format: 'json',
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];
    switch (arg) {
      case '--self-check': out.selfCheck = true; break;
      case '--check-template': out.checkTemplate = next; i++; break;
      case '--check-workflow': out.checkWorkflow = next; i++; break;
      case '--contract': out.contract = next; i++; break;
      case '--spec': out.spec = next; i++; break;
      case '--format': out.format = next; i++; break;
      case '-h':
      case '--help': out.help = true; break;
    }
  }
  return out;
}

function loadRequiredTitles(contractPath) {
  return fs.readFileSync(contractPath, 'utf8')
    .split('\n')
    .map((line) => {
      const match = line.match(/^\s*title:\s*"?(.*?)"?\s*$/);
      return match ? match[1] : null;
    })
    .filter(Boolean);
}

function extractH2Titles(text) {
  const titles = [];
  const regex = /^##\s+(.+?)\s*$/gm;
  let match;
  while ((match = regex.exec(text)) !== null) {
    titles.push(match[1].trim());
  }
  return titles;
}

function checkTemplate(templatePath, contractPath) {
  const requiredTitles = loadRequiredTitles(contractPath);
  const actualTitles = extractH2Titles(fs.readFileSync(templatePath, 'utf8'));
  const issues = [];
  for (const title of requiredTitles) {
    if (!actualTitles.includes(title)) {
      issues.push({
        file: templatePath,
        type: 'missing_required_section',
        section: title,
        message: `缺少必需章节: ${title}`,
      });
    }
  }
  return { checked: 1, issues };
}

function extractStandardPaths(specPath) {
  const text = fs.readFileSync(specPath, 'utf8');
  const paths = new Set();
  text.split('\n').forEach((line) => {
    if (line.includes('❌')) return;
    Array.from(line.matchAll(/`(dev_docs\/[^`]+)`/g), (match) => match[1])
      .forEach((targetPath) => paths.add(targetPath));
  });
  return paths;
}

function normalizeStandardPath(targetPath) {
  if (targetPath === 'dev_docs/plans/README.md') return 'dev_docs/plans/';
  if (targetPath.startsWith('dev_docs/plans/active/')) return 'dev_docs/plans/active/';
  if (targetPath.startsWith('dev_docs/plans/done/')) return 'dev_docs/plans/done/';
  if (targetPath.startsWith('dev_docs/plans/archive/')) return 'dev_docs/plans/archive/';
  if (targetPath.startsWith('dev_docs/memos/')) return 'dev_docs/memos/';
  if (targetPath.startsWith('dev_docs/knowledge/')) return 'dev_docs/knowledge/';
  if (targetPath.startsWith('dev_docs/rules/combined/')) return 'dev_docs/rules/combined/AI_RULES.md';
  return targetPath;
}

function extractUserDocPaths(text) {
  return Array.from(text.matchAll(/dev_docs\/[\w./-]+/g), (match) => normalizeStandardPath(match[0]));
}

function checkSpecPaths(specPath) {
  const standardPaths = Array.from(extractStandardPaths(specPath)).sort();
  const issues = [];
  for (const obsoletePath of Array.from(OBSOLETE_STANDARD_PATHS).sort()) {
    if (standardPaths.includes(obsoletePath)) {
      issues.push({
        file: specPath,
        type: 'obsolete_standard_path',
        path: obsoletePath,
        message: `spec 仍包含过期标准路径: ${obsoletePath}`,
      });
    }
  }
  return { checked: 1, standard_paths: standardPaths, issues };
}

function contextIsOptional(lines, index) {
  let start = 0;
  for (let cursor = index; cursor >= 0; cursor--) {
    if (/^#{2,6}\s+/.test(lines[cursor])) {
      start = cursor;
      break;
    }
  }
  const end = Math.min(lines.length, index + 4);
  const context = lines.slice(start, end).join('\n');
  const markers = ['[OPTIONAL]', '不属于', '只有在用户明确需要', '可选', '不是必需'];
  return markers.some((marker) => context.includes(marker));
}

function checkWorkflow(workflowPath, specPath) {
  const specPaths = extractStandardPaths(specPath);
  const lines = fs.readFileSync(workflowPath, 'utf8').split('\n');
  const issues = [];
  const seenStandardPaths = new Set();
  lines.forEach((line, index) => {
    for (const driftPath of extractUserDocPaths(line)) {
      if (specPaths.has(driftPath)) {
        seenStandardPaths.add(driftPath);
      }
      if (OBSOLETE_STANDARD_PATHS.has(driftPath)) {
        issues.push({
          file: workflowPath,
          line: index + 1,
          type: 'obsolete_standard_path',
          path: driftPath,
          message: `workflow 使用了过期标准路径: ${driftPath}`,
        });
        continue;
      }
      if (
        !driftPath.startsWith('dev_docs/plans/')
        && !driftPath.startsWith('dev_docs/memos/')
        && !driftPath.startsWith('dev_docs/review/')
      ) {
        continue;
      }
      if (!specPaths.has(driftPath) && !contextIsOptional(lines, index)) {
        issues.push({
          file: workflowPath,
          line: index + 1,
          type: 'workflow_path_drift',
          path: driftPath,
          message: `workflow 使用了未被 spec 收录的标准路径: ${driftPath}`,
        });
      }
    }
  });
  return { checked: 1, seen_standard_paths: Array.from(seenStandardPaths).sort(), issues };
}

function renderText(payload) {
  const status = payload.summary.passed ? 'PASS' : 'FAIL';
  const lines = [`${status}: framework_contract_checker`];
  Object.entries(payload.checks).forEach(([name, result]) => {
    lines.push(`- ${name}: ${result.issues.length} issue(s)`);
    result.issues.forEach((issue) => {
      const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;
      lines.push(`  - ${issue.type} ${location} ${issue.message || ''}`.trimEnd());
    });
  });
  return `${lines.join('\n')}\n`;
}

function main() {
  const args = parseArgs();
  if (args.help) {
    process.stdout.write(
      'Usage: framework_contract_checker [--self-check] [--check-template FILE] [--check-workflow FILE] [--contract YAML] [--spec FILE] [--format json|text]\n'
    );
    return 0;
  }

  const checks = {};

  if (args.checkTemplate) {
    checks.template = checkTemplate(args.checkTemplate, args.contract);
  }

  if (args.checkWorkflow) {
    checks.workflow = checkWorkflow(args.checkWorkflow, args.spec);
  }

  if (args.selfCheck) {
    checks.template = checkTemplate(DEFAULT_TEMPLATE, args.contract);
    checks.spec_paths = checkSpecPaths(args.spec);
    const issues = [];
    const seenStandardPaths = new Set();
    DEFAULT_WORKFLOWS.forEach((workflowPath) => {
      const workflowResult = checkWorkflow(workflowPath, args.spec);
      issues.push(...workflowResult.issues);
      workflowResult.seen_standard_paths.forEach((seenPath) => seenStandardPaths.add(seenPath));
    });
    checks.workflow = {
      checked: DEFAULT_WORKFLOWS.length,
      seen_standard_paths: Array.from(seenStandardPaths).sort(),
      issues,
    };
  }

  if (Object.keys(checks).length === 0) {
    process.stdout.write(
      'Usage: framework_contract_checker [--self-check] [--check-template FILE] [--check-workflow FILE] [--contract YAML] [--spec FILE] [--format json|text]\n'
    );
    return 2;
  }

  const totalIssues = Object.values(checks).reduce((sum, result) => sum + result.issues.length, 0);
  const payload = {
    summary: {
      passed: totalIssues === 0,
      issues: totalIssues,
    },
    checks,
  };

  if (args.format === 'text') {
    process.stdout.write(renderText(payload));
  } else {
    process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  }

  return totalIssues === 0 ? 0 : 1;
}

process.exit(main());
