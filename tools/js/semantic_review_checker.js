#!/usr/bin/env node
/**
 * 半自动语义复查检查器
 */

const fs = require('fs');
const path = require('path');

const POSITIVE_KEYWORDS = ['推荐', '必须', '优先', '建议', 'should', 'recommended', 'prefer', '需要'];
const NEGATIVE_KEYWORDS = ['不建议', '不要', '禁止', 'deprecated', '废弃', 'avoid', 'do not', '不需要', '无需'];
const SOURCE_SUFFIXES = new Set(['.md', '.py', '.js', '.ts', '.tsx']);

function parseArgs() {
  const argv = process.argv.slice(2);
  const out = { repoRoot: '.', format: 'json' };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];
    switch (arg) {
      case '--doc-dir': out.docDir = next; i++; break;
      case '--repo-root': out.repoRoot = next; i++; break;
      case '--format': out.format = next; i++; break;
      case '--check-fact-conflicts': out.checkFactConflicts = true; break;
      case '--check-metrics': out.checkMetrics = true; break;
      case '--check-test-topology': out.checkTestTopology = true; break;
      case '--full-check': out.fullCheck = true; break;
      case '-h':
      case '--help': out.help = true; break;
    }
  }
  return out;
}

function walkFiles(root, predicate) {
  const results = [];
  function visit(current) {
    const stat = fs.statSync(current);
    if (stat.isFile()) {
      if (!predicate || predicate(current)) results.push(current);
      return;
    }
    fs.readdirSync(current).forEach((entry) => visit(path.join(current, entry)));
  }
  if (fs.existsSync(root)) visit(root);
  return results.sort();
}

function iterMarkdownFiles(root) {
  return walkFiles(root, (file) => file.endsWith('.md'));
}

function iterAuthorityFiles(repoRoot, docDir) {
  const files = [];
  const readme = path.join(repoRoot, 'README.md');
  if (fs.existsSync(readme)) files.push(readme);
  const docsDir = path.join(repoRoot, 'docs');
  if (fs.existsSync(docsDir)) {
    files.push(...walkFiles(docsDir, (file) => SOURCE_SUFFIXES.has(path.extname(file))));
  }
  walkFiles(repoRoot, (file) => SOURCE_SUFFIXES.has(path.extname(file))).forEach((file) => {
    if (file.startsWith(docDir + path.sep)) return;
    if (!files.includes(file)) files.push(file);
  });
  return files.sort();
}

function scanTestTopology(repoRoot) {
  const topology = [];
  function visit(current) {
    const stat = fs.statSync(current);
    if (!stat.isDirectory()) return;
    const name = path.basename(current);
    if (name === 'tests' || name === 'test') {
      const fileCount = walkFiles(current, () => true).length;
      topology.push({
        path: `${path.relative(repoRoot, current).replace(/\\/g, '/')}/`,
        file_count: fileCount,
      });
    }
    fs.readdirSync(current).forEach((entry) => {
      const child = path.join(current, entry);
      if (fs.statSync(child).isDirectory()) visit(child);
    });
  }
  visit(repoRoot);
  return topology.sort((a, b) => a.path.localeCompare(b.path));
}

function countFilesUnder(repoRoot, relativePath) {
  const target = path.join(repoRoot, relativePath);
  if (!fs.existsSync(target)) return null;
  if (fs.statSync(target).isFile()) return 1;
  return walkFiles(target, () => true).length;
}

function checkMetrics(docDir, repoRoot) {
  const issues = [];
  const topology = scanTestTopology(repoRoot);
  const totalTestFiles = topology.reduce((sum, item) => sum + item.file_count, 0);
  const totalTestDirs = topology.length;
  const pathPattern = /`?([\w./-]+)`?\s*下共有\s*(\d+)\s*个文件/g;
  const testFilePattern = /(\d+)\s*个测试文件/g;
  const testDirPattern = /(\d+)\s*个测试目录/g;
  iterMarkdownFiles(docDir).forEach((docPath) => {
    const lines = fs.readFileSync(docPath, 'utf8').split('\n');
    lines.forEach((line, index) => {
      let match;
      pathPattern.lastIndex = 0;
      while ((match = pathPattern.exec(line)) !== null) {
        const relativePath = match[1];
        const expected = parseInt(match[2], 10);
        const actual = countFilesUnder(repoRoot, relativePath);
        if (actual !== null && actual !== expected) {
          issues.push({ type: 'metric_drift', file: docPath, line: index + 1, metric: `${relativePath} file_count`, expected, actual });
        }
      }
      testFilePattern.lastIndex = 0;
      while ((match = testFilePattern.exec(line)) !== null) {
        const expected = parseInt(match[1], 10);
        if (expected !== totalTestFiles) {
          issues.push({ type: 'metric_drift', file: docPath, line: index + 1, metric: 'test_file_count', expected, actual: totalTestFiles });
        }
      }
      testDirPattern.lastIndex = 0;
      while ((match = testDirPattern.exec(line)) !== null) {
        const expected = parseInt(match[1], 10);
        if (expected !== totalTestDirs) {
          issues.push({ type: 'metric_drift', file: docPath, line: index + 1, metric: 'test_directory_count', expected, actual: totalTestDirs });
        }
      }
    });
  });
  return issues;
}

function checkTestTopology(docDir, repoRoot) {
  const issues = [];
  const topology = scanTestTopology(repoRoot);
  const documentText = iterMarkdownFiles(docDir).map((file) => fs.readFileSync(file, 'utf8')).join('\n');
  topology.forEach((item) => {
    const basename = `${item.path.replace(/\/$/, '').split('/').pop()}/`;
    let covered = documentText.includes(item.path);
    if (!covered && item.path.split('/').filter(Boolean).length === 1) {
      covered = documentText.includes(basename);
    }
    if (!covered) {
      issues.push({
        type: 'uncovered_test_topology',
        path: item.path,
        file_count: item.file_count,
        message: `测试目录未被文档覆盖: ${item.path}`,
      });
    }
  });
  return issues;
}

function classifyPolarity(line) {
  const negative = NEGATIVE_KEYWORDS.some((keyword) => line.includes(keyword));
  const positive = POSITIVE_KEYWORDS.some((keyword) => line.includes(keyword));
  if (negative && !positive) return 'negative';
  if (positive && !negative) return 'positive';
  if (negative && positive) return 'negative';
  return null;
}

function extractAnchors(line) {
  return Array.from(line.matchAll(/`([^`]+)`/g), (match) => match[1].trim()).filter(Boolean);
}

function collectAssertions(files) {
  const assertions = [];
  files.forEach((file) => {
    fs.readFileSync(file, 'utf8').split('\n').forEach((line, index) => {
      const polarity = classifyPolarity(line);
      if (!polarity) return;
      const anchors = extractAnchors(line);
      if (anchors.length === 0) return;
      assertions.push({
        file,
        line: index + 1,
        polarity,
        anchors,
        text: line.trim(),
      });
    });
  });
  return assertions;
}

function checkFactConflicts(docDir, repoRoot) {
  const issues = [];
  const docAssertions = collectAssertions(iterMarkdownFiles(docDir));
  const authorityAssertions = collectAssertions(iterAuthorityFiles(repoRoot, docDir));
  docAssertions.forEach((docAssertion) => {
    authorityAssertions.forEach((authorityAssertion) => {
      if (docAssertion.polarity === authorityAssertion.polarity) return;
      const shared = docAssertion.anchors.filter((anchor) => authorityAssertion.anchors.includes(anchor));
      if (shared.length === 0) return;
      issues.push({
        type: 'fact_conflict',
        anchor: shared[0],
        doc_file: docAssertion.file,
        doc_line: docAssertion.line,
        authority_file: authorityAssertion.file,
        authority_line: authorityAssertion.line,
        doc_text: docAssertion.text,
        authority_text: authorityAssertion.text,
      });
    });
  });
  return issues;
}

function renderText(payload) {
  const status = payload.summary.passed ? 'PASS' : 'FAIL';
  return `${status}: semantic_review_checker\n- fact_conflicts: ${payload.checks.fact_conflicts.length} issue(s)\n- metrics: ${payload.checks.metrics.length} issue(s)\n- test_topology: ${payload.checks.test_topology.length} issue(s)\n`;
}

function main() {
  const args = parseArgs();
  if (args.help) {
    process.stdout.write('Usage: semantic_review_checker --doc-dir DIR [--repo-root DIR] [--check-fact-conflicts] [--check-metrics] [--check-test-topology] [--full-check] [--format json|text]\n');
    return 0;
  }
  if (!args.docDir) {
    process.stdout.write('Usage: semantic_review_checker --doc-dir DIR [--repo-root DIR] [--check-fact-conflicts] [--check-metrics] [--check-test-topology] [--full-check] [--format json|text]\n');
    return 2;
  }

  const docDir = path.resolve(args.docDir);
  const repoRoot = path.resolve(args.repoRoot);
  const checks = { fact_conflicts: [], metrics: [], test_topology: [] };
  if (args.fullCheck || args.checkFactConflicts) {
    checks.fact_conflicts = checkFactConflicts(docDir, repoRoot);
  }
  if (args.fullCheck || args.checkMetrics) {
    checks.metrics = checkMetrics(docDir, repoRoot);
  }
  if (args.fullCheck || args.checkTestTopology) {
    checks.test_topology = checkTestTopology(docDir, repoRoot);
  }
  if (!(args.fullCheck || args.checkFactConflicts || args.checkMetrics || args.checkTestTopology)) {
    process.stdout.write('Usage: semantic_review_checker --doc-dir DIR [--repo-root DIR] [--check-fact-conflicts] [--check-metrics] [--check-test-topology] [--full-check] [--format json|text]\n');
    return 2;
  }

  const totalIssues = checks.fact_conflicts.length + checks.metrics.length + checks.test_topology.length;
  const payload = {
    summary: { passed: totalIssues === 0, issues: totalIssues },
    checks,
    metadata: { doc_dir: docDir, repo_root: repoRoot },
  };
  if (args.format === 'text') {
    process.stdout.write(renderText(payload));
  } else {
    process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  }
  return totalIssues === 0 ? 0 : 1;
}

process.exit(main());
