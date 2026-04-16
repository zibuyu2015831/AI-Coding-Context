#!/usr/bin/env node
/**
 * AICC 知识匹配与引用解析工具 (Node.js 版本)
 */

const fs = require('fs');
const path = require('path');

const CONFIG_FILE = '.aicc/knowledge_config.json';
const CACHE_DIR = '.aicc-cache';
const SHARED_KNOWLEDGE_DIR = path.join(CACHE_DIR, 'shared-knowledge');
const DEFAULT_LOCAL_PATH = 'dev_docs/knowledge';

class KnowledgeMatcher {
  constructor(configPath = CONFIG_FILE) {
    this.config = this._loadConfig(configPath);
    this.localPath = this.config.knowledge.local_path || DEFAULT_LOCAL_PATH;
    this.sharedPath = SHARED_KNOWLEDGE_DIR;
    this.sharedEnabled = this.config.knowledge.shared ? this.config.knowledge.shared.enabled : false;
    this.strategy = this.config.knowledge.match_strategy || 'local-first';
  }

  _loadConfig(configPath) {
    if (!fs.existsSync(configPath)) {
      return {
        knowledge: {
          local_path: DEFAULT_LOCAL_PATH,
          shared: { enabled: false },
          match_strategy: 'local-first'
        }
      };
    }
    try {
      return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
      return this._loadConfig('');
    }
  }

  findKnowledge(refKey) {
    const parts = refKey.split(':');
    if (parts.length !== 2) return null;
    const [kType, kName] = parts;

    let searchPaths = [];
    if (this.strategy === 'local-first') {
      searchPaths = [this.localPath];
      if (this.sharedEnabled) searchPaths.push(this.sharedPath);
    } else if (this.strategy === 'shared-first') {
      if (this.sharedEnabled) searchPaths.push(this.sharedPath);
      searchPaths.push(this.localPath);
    } else {
      searchPaths = [this.localPath];
      if (this.sharedEnabled) searchPaths.push(this.sharedPath);
    }

    for (const basePath of searchPaths) {
      if (!fs.existsSync(basePath)) continue;

      const result = this._searchRecursive(basePath, `${kName}.md`);
      if (result) return fs.readFileSync(result, 'utf8');
    }
    return null;
  }

  _searchRecursive(dir, targetFile) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      if (fs.statSync(fullPath).isDirectory()) {
        if (file === '.git') continue;
        const result = this._searchRecursive(fullPath, targetFile);
        if (result) return result;
      } else if (file === targetFile) {
        return fullPath;
      }
    }
    return null;
  }

  resolveDocument(content) {
    const pattern = /:::knowledge-ref\s+([^\s:]+:[^\s:]+)\s*:::/g;
    return content.replace(pattern, (match, refKey) => {
      let knowledgeContent = this.findKnowledge(refKey);
      if (knowledgeContent) {
        if (knowledgeContent.startsWith('---')) {
          const parts = knowledgeContent.split('---');
          if (parts.length >= 3) {
            knowledgeContent = parts.slice(2).join('---').trim();
          }
        }
        return `\n<!-- START KNOWLEDGE-REF: ${refKey} -->\n${knowledgeContent}\n<!-- END KNOWLEDGE-REF: ${refKey} -->\n`;
      } else {
        return `<!-- UNRESOLVED KNOWLEDGE-REF: ${refKey} -->`;
      }
    });
  }
}

function showHelp() {
  console.log(`
AICC 知识匹配解析器 (Node.js)

用法: node tools/js/knowledge_matcher.js --ref "pattern:mvc"
      node tools/js/knowledge_matcher.js --file doc.md [--inplace]
`);
}

const args = process.argv.slice(2);
const matcher = new KnowledgeMatcher();

if (args.includes('--help')) {
  showHelp();
} else if (args.includes('--ref')) {
  const ref = args[args.indexOf('--ref') + 1];
  const result = matcher.findKnowledge(ref);
  if (result) {
    console.log(result);
  } else {
    console.error(`未找到引用: ${ref}`);
    process.exit(1);
  }
} else if (args.includes('--file')) {
  const file = args[args.indexOf('--file') + 1];
  if (!fs.existsSync(file)) {
    console.error(`找不到文件: ${file}`);
    process.exit(1);
  }
  const content = fs.readFileSync(file, 'utf8');
  const resolved = matcher.resolveDocument(content);
  if (args.includes('--inplace')) {
    fs.writeFileSync(file, resolved, 'utf8');
    console.log(`已更新文件: ${file}`);
  } else {
    console.log(resolved);
  }
} else {
  showHelp();
}
