#!/usr/bin/env node

/**
 * Why-Tool: 架构探针检索工具 (Architecture Context Retriever)
 *
 * 功能说明:
 *   通过代码中的隐性注解或语义搜索，检索对应的技术决策理由(ADR)。
 *   - L1 注解优先检索: 扫描代码中的 @architecture 或 @reason 注解
 *   - 语义搜索兜底: 对 ADR 标题、摘要与正文进行关键词匹配
 *
 * 使用方法:
 *   # 通过查询搜索相关 ADR
 *   node tools/js/why_tool.js --query "why use pinia"
 *
 *   # 扫描源代码文件中的注解
 *   node tools/js/why_tool.js --file src/store/index.ts
 *
 *   # 组合使用: 先扫描注解，再语义搜索
 *   node tools/js/why_tool.js --file src/app.ts --query "state management"
 *
 * 参数说明:
 *   --query TEXT       搜索关键词或问题 (例如: "why use pinia")
 *   --file PATH        源代码文件路径，扫描 @architecture/@reason 注解
 *   --adr-dir PATH     ADR 文档目录 (默认: dev_docs/architecture/decisions)
 *
 * 输出格式:
 *   文本输出，包含以下信息:
 *   - 扫描到的 L1 注解列表 (文件路径、行号、ADR编号、描述)
 *   - 精确匹配的 ADR 详情
 *   - 语义搜索的 Top 3 推荐结果
 *
 * 使用示例:
 *   # 示例 1: 搜索为何选择 Pinia
 *   node tools/js/why_tool.js --query "pinia state management"
 *
 *   # 示例 2: 扫描文件中的架构注解
 *   node tools/js/why_tool.js --file src/components/UserList.vue
 *
 *   # 示例 3: 指定自定义 ADR 目录
 *   node tools/js/why_tool.js --adr-dir docs/decisions --query "database"
 *
 * 版本信息:
 *   版本: 1.0.0
 *   更新日期: 2026-04-12
 */

const fs = require('fs');
const path = require('path');

// 默认 ADR 目录
const DEFAULT_ADR_DIR = 'dev_docs/architecture/decisions';

/**
 * 解析命令行参数
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    query: null,
    file: null,
    adrDir: DEFAULT_ADR_DIR
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--query':
        options.query = args[++i];
        break;
      case '--file':
        options.file = args[++i];
        break;
      case '--adr-dir':
        options.adrDir = args[++i];
        break;
    }
  }

  return options;
}

/**
 * 提取 Frontmatter 和内容
 */
function extractFrontmatterAndContent(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');

  // 尝试解析 Frontmatter
  const fmMatch = content.match(/^---\n(.*?)\n---\n(.*)/s);
  if (fmMatch) {
    const fmText = fmMatch[1];
    const body = fmMatch[2];

    const metadata = {};
    for (const line of fmText.split('\n')) {
      if (line.includes(':')) {
        const [k, ...v] = line.split(':');
        metadata[k.trim()] = v.join(':').trim().replace(/^["']|["']$/g, '');
      }
    }
    return { metadata, body };
  }

  return { metadata: {}, body: content };
}

/**
 * 扫描文件中的注解
 */
function scanFileForAnnotations(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    const annotations = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // 匹配 @architecture 注解
      const archMatch = line.match(/@architecture\s+(ADR-\d+):?\s*(.*)/i);
      if (archMatch) {
        annotations.push({
          line: i + 1,
          adr: archMatch[1].toUpperCase(),
          desc: archMatch[2].trim()
        });
      }

      // 匹配 @reason 注解
      const reasonMatch = line.match(/@reason\s+(.*)/i);
      if (reasonMatch) {
        annotations.push({
          line: i + 1,
          adr: "IMPLICIT",
          desc: reasonMatch[1].trim()
        });
      }
    }

    return annotations;
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error.message);
    return [];
  }
}

/**
 * 搜索 ADR
 */
function searchADRs(query, adrDir) {
  const baseDir = path.resolve(adrDir);

  if (!fs.existsSync(baseDir)) {
    return [];
  }

  const results = [];
  const queryTerms = query
    .split(/\s+/)
    .filter(q => q)
    .map(q => q.toLowerCase());

  function scanDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        if (!entry.name.startsWith('.') && !entry.name.includes('archived')) {
          scanDir(fullPath);
        }
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        try {
          const { metadata, body } = extractFrontmatterAndContent(fullPath);

          let score = 0;
          const title = metadata.title || entry.name;
          const summary = metadata.summary || '';
          const searchTarget = `${title} ${summary} ${body}`.toLowerCase();

          for (const term of queryTerms) {
            if (searchTarget.includes(term)) {
              score += 1;
              if (summary.toLowerCase().includes(term) ||
                  title.toLowerCase().includes(term)) {
                score += 2;
              }
            }
          }

          if (score > 0) {
            results.push({
              file: fullPath,
              title: title,
              summary: summary,
              score: score
            });
          }
        } catch (error) {
          // 忽略无法读取的文件
        }
      }
    }
  }

  scanDir(baseDir);

  // 按分数排序
  results.sort((a, b) => b.score - a.score);

  return results;
}

/**
 * 主函数
 */
function main() {
  const options = parseArgs();

  // 检查必需参数
  if (!options.query && !options.file) {
    console.log("请提供 --query 或 --file 参数");
    console.log("\n使用示例:");
    console.log('  node why_tool.js --query "why use pinia"');
    console.log('  node why_tool.js --file src/store/index.ts');
    process.exit(1);
  }

  console.log("=== Why-Tool: Architecture Context Retriever ===\n");

  // 第一阶段：检查 L1 注解
  const foundADRs = new Set();

  if (options.file && fs.existsSync(options.file)) {
    console.log(`Scanning ${options.file} for L1 annotations...`);
    const annotations = scanFileForAnnotations(options.file);

    if (annotations.length > 0) {
      for (const ann of annotations) {
        console.log(`[Line ${ann.line}] Found Annotation: ${ann.adr} - ${ann.desc}`);
        if (ann.adr.startsWith("ADR-")) {
          foundADRs.add(ann.adr);
        }
      }
    } else {
      console.log("No @architecture annotations found in file.\n");
    }
  }

  // 第二阶段：提取精确匹配的 ADR
  if (foundADRs.size > 0) {
    console.log("\n=> Exact ADR Matches:\n");
    for (const adrId of foundADRs) {
      const adrDir = path.resolve(options.adrDir);
      if (fs.existsSync(adrDir)) {
        const files = fs.readdirSync(adrDir);
        for (const file of files) {
          if (file.toLowerCase().includes(adrId.toLowerCase())) {
            const filePath = path.join(adrDir, file);
            try {
              const { metadata, body } = extractFrontmatterAndContent(filePath);
              console.log(`🎯 ${file}`);
              console.log(`   Title: ${metadata.title || 'N/A'}`);
              console.log(`   Summary: ${metadata.summary || 'N/A'}`);
              console.log();
            } catch (error) {
              // 忽略解析错误
            }
          }
        }
      }
    }
  }

  // 第三阶段：语义搜索兜底
  if (options.query) {
    console.log(`\n=> Semantic search for: "${options.query}"\n`);
    const results = searchADRs(options.query, options.adrDir);

    if (results.length === 0) {
      console.log("No matching active ADRs found.\n");
    } else {
      console.log(`Found ${results.length} matching ADRs:\n`);
      for (let i = 0; i < Math.min(3, results.length); i++) {
        const res = results[i];
        console.log(`${i + 1}. [Score: ${res.score}] ${res.title}`);
        console.log(`   File: ${res.file}`);
        console.log(`   Summary: ${res.summary || 'N/A'}`);
        console.log();
      }
    }
  }

  console.log("=== Analysis Complete ===");
}

// 运行主函数
main();
