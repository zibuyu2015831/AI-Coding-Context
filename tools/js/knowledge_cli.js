#!/usr/bin/env node
/**
 * AICC 知识库管理 CLI 工具 (Node.js 版本)
 *
 * 功能说明：
 * - status: 查看知识库状态
 * - config: 配置共享知识库
 * - enable-shared: 启用共享知识库
 * - disable-shared: 禁用共享知识库
 * - update-shared: 从远程更新共享知识库
 * - strategy: 设置匹配策略
 * - init: 初始化本地知识库为共享知识库
 * - publish: 发布本地共享知识库到云端
 *
 * 版本信息：
 *     版本：1.0.0
 *     更新日期：2026-04-16
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// --- 配置常量 ---
const CONFIG_DIR = '.aicc';
const CONFIG_FILE = path.join(CONFIG_DIR, 'knowledge_config.json');
const CACHE_DIR = '.aicc-cache';
const SHARED_KNOWLEDGE_DIR = path.join(CACHE_DIR, 'shared-knowledge');
const DEFAULT_LOCAL_PATH = 'dev_docs/knowledge';

// --- 辅助函数 ---
function printSuccess(msg) { console.log(`✅ ${msg}`); }
function printError(msg) { console.error(`❌ ${msg}`); }
function printWarning(msg) { console.warn(`⚠️ ${msg}`); }
function printInfo(msg) { console.log(`ℹ️ ${msg}`); }

function runCommand(cmd, cwd = null) {
  try {
    return execSync(cmd, { cwd, encoding: 'utf8', stdio: 'pipe' });
  } catch (error) {
    return { error: true, stderr: error.stderr || error.message };
  }
}

// --- 核心类 ---

class ConfigManager {
  static loadConfig() {
    if (!fs.existsSync(CONFIG_FILE)) {
      return {
        knowledge: {
          local_path: DEFAULT_LOCAL_PATH,
          shared: {
            enabled: false,
            repo_url: '',
            branch: 'main',
            cache_path: SHARED_KNOWLEDGE_DIR,
            last_updated: ''
          },
          match_strategy: 'local-first',
          match_threshold: 0.6
        }
      };
    }
    try {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    } catch (e) {
      printWarning(`无法读取配置文件: ${e.message}，使用默认配置。`);
      return ConfigManager.loadConfig();
    }
  }

  static saveConfig(config) {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf8');
  }

  static updateGitignore() {
    const gitignorePath = '.gitignore';
    const entry = `${CACHE_DIR}/`;
    if (fs.existsSync(gitignorePath)) {
      let content = fs.readFileSync(gitignorePath, 'utf8');
      if (!content.includes(entry)) {
        fs.appendFileSync(gitignorePath, `\n# AICC 知识库缓存\n${entry}\n`);
        printInfo(`已将 ${entry} 添加到 .gitignore`);
      }
    } else {
      fs.writeFileSync(gitignorePath, `# AICC 知识库缓存\n${entry}\n`);
      printInfo(`已创建 .gitignore 并添加 ${entry}`);
    }
  }
}

class KnowledgeCLI {
  constructor() {
    this.config = ConfigManager.loadConfig();
  }

  status() {
    console.log('\n📚 知识库配置状态');
    const localPath = this.config.knowledge.local_path || DEFAULT_LOCAL_PATH;
    const localExists = fs.existsSync(localPath);
    console.log(`  本地知识库: ${localExists ? '✅' : '❌'} ${localPath}`);

    const shared = this.config.knowledge.shared;
    if (shared.repo_url) {
      console.log(`  共享知识库: ${shared.enabled ? '✅ 已启用' : '⚠️ 已禁用'}`);
      console.log(`    仓库地址: ${shared.repo_url}`);
      console.log(`    分支: ${shared.branch}`);
      console.log(`    最近更新: ${shared.last_updated || '从不'}`);
    } else {
      console.log('  共享知识库: ❌ 未配置');
    }

    console.log(`  匹配策略: ${this.config.knowledge.match_strategy || 'local-first'}\n`);
  }

  configShared(repoUrl, branch = 'main', depth = null, force = false) {
    this.config.knowledge.shared.repo_url = repoUrl;
    this.config.knowledge.shared.branch = branch;
    this.config.knowledge.shared.enabled = true;

    if (fs.existsSync(SHARED_KNOWLEDGE_DIR) && fs.existsSync(path.join(SHARED_KNOWLEDGE_DIR, '.git'))) {
      if (force) {
        printInfo('正在强制更新共享知识库...');
        runCommand('git fetch --all', SHARED_KNOWLEDGE_DIR);
        runCommand(`git reset --hard origin/${branch}`, SHARED_KNOWLEDGE_DIR);
      } else {
        printInfo('正在同步共享知识库...');
        runCommand(`git pull origin ${branch}`, SHARED_KNOWLEDGE_DIR);
      }
    } else {
      printInfo(`正在克隆共享知识库到 ${SHARED_KNOWLEDGE_DIR}...`);
      if (!fs.existsSync(path.dirname(SHARED_KNOWLEDGE_DIR))) {
        fs.mkdirSync(path.dirname(SHARED_KNOWLEDGE_DIR), { recursive: true });
      }
      let cmd = `git clone ${repoUrl} ${SHARED_KNOWLEDGE_DIR} --branch ${branch}`;
      if (depth) cmd += ` --depth ${depth}`;
      const res = runCommand(cmd);
      if (res.error) {
        printError(`克隆失败: ${res.stderr}`);
        return;
      }
    }

    this.config.knowledge.shared.last_updated = new Date().toISOString();
    ConfigManager.saveConfig(this.config);
    ConfigManager.updateGitignore();
    printSuccess('共享知识库配置成功！');
  }

  enableShared() {
    if (!this.config.knowledge.shared.repo_url) {
      printError('未配置共享知识库，请先运行 config 命令。');
      return;
    }
    this.config.knowledge.shared.enabled = true;
    ConfigManager.saveConfig(this.config);
    printSuccess('共享知识库已启用');
  }

  disableShared() {
    this.config.knowledge.shared.enabled = false;
    ConfigManager.saveConfig(this.config);
    printWarning('共享知识库已禁用');
  }

  updateShared(force = false) {
    const shared = this.config.knowledge.shared;
    if (!shared.repo_url) {
      printError('未配置共享知识库。');
      return;
    }

    printInfo('正在同步共享知识库...');
    let res;
    if (force) {
      runCommand('git fetch --all', SHARED_KNOWLEDGE_DIR);
      res = runCommand(`git reset --hard origin/${shared.branch}`, SHARED_KNOWLEDGE_DIR);
    } else {
      res = runCommand(`git pull origin ${shared.branch}`, SHARED_KNOWLEDGE_DIR);
    }

    if (res.error) {
      printError(`更新失败: ${res.stderr}`);
    } else {
      this.config.knowledge.shared.last_updated = new Date().toISOString();
      ConfigManager.saveConfig(this.config);
      printSuccess('共享知识库已更新');
    }
  }

  setStrategy(mode) {
    const validModes = ['local-first', 'shared-first', 'hybrid'];
    if (!validModes.includes(mode)) {
      printError(`无效的策略模式。可选值: ${validModes.join(', ')}`);
      return;
    }
    this.config.knowledge.match_strategy = mode;
    ConfigManager.saveConfig(this.config);
    printSuccess(`知识匹配策略已切换为: ${mode}`);
  }

  initShared(force = false) {
    const localPath = this.config.knowledge.local_path || DEFAULT_LOCAL_PATH;
    if (!fs.existsSync(localPath)) {
      fs.mkdirSync(localPath, { recursive: true });
      printInfo(`已创建目录: ${localPath}`);
    }

    const subdirs = ['fundamentals', 'languages', 'frameworks', 'platforms', 'databases', 'case-studies'];
    subdirs.forEach(sd => {
      const p = path.join(localPath, sd);
      if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
    });

    const metaDir = path.join(localPath, '.aicc');
    if (!fs.existsSync(metaDir)) fs.mkdirSync(metaDir, { recursive: true });

    const metaFile = path.join(metaDir, 'metadata.json');
    if (!fs.existsSync(metaFile) || force) {
      const metadata = {
        name: path.basename(process.cwd()),
        version: '1.0.0',
        description: 'Shared Knowledge Repository',
        author: '',
        created_at: new Date().toISOString()
      };
      fs.writeFileSync(metaFile, JSON.stringify(metadata, null, 2), 'utf8');
    }

    if (!fs.existsSync(path.join(localPath, '.git'))) {
      runCommand('git init', localPath);
      printInfo('已在本地知识库目录初始化 Git 仓库');
    }

    printSuccess(`本地知识库已初始化为共享知识库标准结构: ${localPath}`);
  }

  publish(remoteUrl, branch = 'main', force = false) {
    const localPath = this.config.knowledge.local_path || DEFAULT_LOCAL_PATH;
    if (!fs.existsSync(path.join(localPath, '.git'))) {
      printError('本地知识库未初始化为 Git 仓库，请先运行 init 命令。');
      return;
    }

    const status = runCommand('git status --porcelain', localPath);
    if (typeof status === 'string' && status.trim()) {
      printWarning('检测到未提交的变更，正在自动提交...');
      runCommand('git add .', localPath);
      runCommand('git commit -m "chore: sync knowledge repository"', localPath);
    }

    try {
      runCommand(`git remote add origin ${remoteUrl}`, localPath);
    } catch (e) {
      runCommand(`git remote set-url origin ${remoteUrl}`, localPath);
    }

    printInfo(`正在发布到 ${remoteUrl} [${branch}]...`);
    let pushCmd = `git push -u origin ${branch}`;
    if (force) pushCmd += ' -f';
    const res = runCommand(pushCmd, localPath);

    if (res.error) {
      printError(`发布失败: ${res.stderr}`);
    } else {
      printSuccess('知识库发布成功！');
    }
  }
}

function showHelp() {
  console.log(`
📚 AICC 知识库管理工具

用法: node tools/js/knowledge_cli.js <command> [options]

命令:
  status              查看知识库配置状态
  config              配置共享知识库
    --shared <url>    Git 仓库地址
    --branch <name>   分支 (默认: main)
    --depth <n>       克隆深度
    --force           强制重新配置
  enable-shared       启用共享知识库
  disable-shared      禁用共享知识库
  update-shared       更新共享知识库
    --force           强制更新
  strategy            配置知识匹配策略
    --mode <mode>     local-first | shared-first | hybrid
  init                初始化本地知识库
    --as-shared       必须提供
    --force           强制重新初始化
  publish             发布本地知识库
    --remote <url>    远程仓库地址
    --branch <name>   分支
    --force           强制推送
  help                显示此帮助
`);
}

const args = process.argv.slice(2);
const command = args[0];
const cli = new KnowledgeCLI();

function getArg(flag) {
  const index = args.indexOf(flag);
  return index > -1 && args[index + 1] ? args[index + 1] : null;
}

function hasFlag(flag) {
  return args.includes(flag);
}

switch (command) {
  case 'status':
    cli.status();
    break;
  case 'config':
    const shared = getArg('--shared');
    if (!shared) { printError('--shared <url> 是必需的'); process.exit(1); }
    cli.configShared(shared, getArg('--branch') || 'main', getArg('--depth'), hasFlag('--force'));
    break;
  case 'enable-shared':
    cli.enable_shared();
    break;
  case 'disable-shared':
    cli.disable_shared();
    break;
  case 'update-shared':
    cli.updateShared(hasFlag('--force'));
    break;
  case 'strategy':
    const mode = getArg('--mode');
    if (!mode) { printError('--mode <mode> 是必需的'); process.exit(1); }
    cli.setStrategy(mode);
    break;
  case 'init':
    if (!hasFlag('--as-shared')) { printError('--as-shared 是必需的'); process.exit(1); }
    cli.initShared(hasFlag('--force'));
    break;
  case 'publish':
    const remote = getArg('--remote');
    if (!remote) { printError('--remote <url> 是必需的'); process.exit(1); }
    cli.publish(remote, getArg('--branch') || 'main', hasFlag('--force'));
    break;
  default:
    showHelp();
    break;
}
