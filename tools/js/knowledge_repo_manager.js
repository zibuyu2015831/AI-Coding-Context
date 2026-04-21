#!/usr/bin/env node
/**
 * 知识库仓库管理器 - 管理跨项目知识库的创建、同步和版本控制
 * 
 * 功能说明:
 *     - 初始化知识库仓库结构
 *     - 管理知识库版本控制
 *     - 同步远程知识库
 *     - 生成知识库索引
 * 
 * 使用方法:
 *     # 初始化知识库
 *     node tools/js/knowledge_repo_manager.js --init --path .knowledge
 * 
 *     # 同步远程知识库
 *     node tools/js/knowledge_repo_manager.js --sync --remote-url https://github.com/org/shared-knowledge.git
 * 
 * 版本信息:
 *     Version: 1.0.0
 *     Created: 2026-04-21
 *     Purpose: Support 010-Cross Project Knowledge Reuse
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VERSION = "1.0.0";
const DEFAULT_KNOWLEDGE_DIR = ".knowledge";

function initKnowledgeRepo(repoPath, remoteUrl = "") {
    try {
        fs.mkdirSync(repoPath, { recursive: true });

        const categories = [
            "fundamentals",
            "languages",
            "frameworks",
            "platforms",
            "databases",
            "case-studies"
        ];

        for (const cat of categories) {
            fs.mkdirSync(path.join(repoPath, cat), { recursive: true });
        }

        const aiccDir = path.join(repoPath, ".aicc");
        fs.mkdirSync(aiccDir, { recursive: true });

        const metadata = {
            version: "1.0.0",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            remote_url: remoteUrl,
            branch: "main",
            total_entries: 0,
            categories: categories
        };

        fs.writeFileSync(
            path.join(aiccDir, "metadata.json"),
            JSON.stringify(metadata, null, 2),
            "utf-8"
        );

        const readmeContent = `# 共享知识库

**版本**: ${metadata.version}
**创建时间**: ${metadata.created_at}

## 目录结构

\`\`\`
${repoPath}/
├── fundamentals/      # 基础知识（语言无关、通用原则）
├── languages/         # 编程语言特定知识
├── frameworks/        # 框架特定知识
├── platforms/         # 平台特定知识
├── databases/         # 数据库特定知识
└── case-studies/      # 完整案例研究
\`\`\`

## 知识类型

- **规范性知识**: 架构模式、编码规范、流程规范
- **问题解决型知识**: 常见错误、调试方法、性能优化
- **决策型知识**: 技术选型、架构决策、权衡分析
- **经验型知识**: 最佳实践、反模式、经验教训

## 使用说明

1. 知识条目使用 YAML Frontmatter 格式
2. 确保添加正确的分类和标签
3. 定期同步远程仓库获取更新
`;

        fs.writeFileSync(path.join(repoPath, "README.md"), readmeContent, "utf-8");

        try {
            execSync("git init", { cwd: repoPath, stdio: 'pipe' });
            execSync("git add .", { cwd: repoPath, stdio: 'pipe' });
            execSync('git commit -m "Initial commit"', { cwd: repoPath, stdio: 'pipe' });
        } catch (e) {
            console.error(`Git 初始化警告: ${e.message}`);
        }

        return {
            success: true,
            path: repoPath,
            categories: categories,
            metadata: metadata
        };
    } catch (e) {
        return {
            success: false,
            error: e.message
        };
    }
}

function syncKnowledgeRepo(localPath, remoteUrl = "", branch = "main") {
    try {
        if (!fs.existsSync(path.join(localPath, ".git"))) {
            return {
                success: false,
                error: "本地知识库不是 Git 仓库"
            };
        }

        if (remoteUrl) {
            try {
                execSync(`git remote add origin ${remoteUrl}`, { cwd: localPath, stdio: 'pipe' });
            } catch (e) {
                execSync(`git remote set-url origin ${remoteUrl}`, { cwd: localPath, stdio: 'pipe' });
            }
        }

        try {
            execSync("git fetch origin", { cwd: localPath, stdio: 'pipe' });
            execSync(`git merge origin/${branch}`, { cwd: localPath, stdio: 'pipe' });
        } catch (e) {
            let errorMsg = e.stderr ? e.stderr.toString() : e.message;
            return {
                success: false,
                error: `同步失败: ${errorMsg}`
            };
        }

        const metadataPath = path.join(localPath, ".aicc", "metadata.json");
        if (fs.existsSync(metadataPath)) {
            const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
            metadata.updated_at = new Date().toISOString();
            fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2), "utf-8");
        }

        return {
            success: true,
            message: "同步成功",
            branch: branch
        };
    } catch (e) {
        return {
            success: false,
            error: e.message
        };
    }
}

function generateIndex(repoPath) {
    try {
        const index = {
            generated_at: new Date().toISOString(),
            entries: []
        };

        function walk(dir) {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                if (file === ".git" || file === ".aicc") continue;
                const fullPath = path.join(dir, file);
                const stat = fs.statSync(fullPath);

                if (stat.isDirectory()) {
                    walk(fullPath);
                } else if (file.endsWith(".md") && file !== "README.md") {
                    const relPath = path.relative(repoPath, fullPath);
                    try {
                        const content = fs.readFileSync(fullPath, "utf-8");
                        const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
                        if (match) {
                            const yamlContent = match[1];
                            const entry = { file: relPath };
                            const lines = yamlContent.split("\n");
                            for (const line of lines) {
                                if (line.includes(":")) {
                                    let [key, ...valParts] = line.split(":");
                                    key = key.trim();
                                    let value = valParts.join(":").trim().replace(/^["']|["']$/g, '');
                                    
                                    if (["title", "category", "tags", "description", "created_at"].includes(key)) {
                                        entry[key] = value;
                                    }
                                }
                            }
                            index.entries.push(entry);
                        }
                    } catch (e) {
                        console.error(`解析 ${fullPath} 失败: ${e.message}`);
                    }
                }
            }
        }

        walk(repoPath);

        const indexPath = path.join(repoPath, ".aicc", "index.json");
        fs.mkdirSync(path.dirname(indexPath), { recursive: true });
        fs.writeFileSync(indexPath, JSON.stringify(index, null, 2), "utf-8");

        return {
            success: true,
            total_entries: index.entries.length,
            index_path: indexPath
        };
    } catch (e) {
        return {
            success: false,
            error: e.message
        };
    }
}

function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        init: false,
        sync: false,
        generateIndex: false,
        path: DEFAULT_KNOWLEDGE_DIR,
        remoteUrl: "",
        branch: "main"
    };

    for (let i = 0; i < args.length; i++) {
        if (args[i] === "--init") parsed.init = true;
        else if (args[i] === "--sync") parsed.sync = true;
        else if (args[i] === "--generate-index") parsed.generateIndex = true;
        else if (args[i] === "--path" && args[i + 1]) parsed.path = args[++i];
        else if (args[i] === "--remote-url" && args[i + 1]) parsed.remoteUrl = args[++i];
        else if (args[i] === "--branch" && args[i + 1]) parsed.branch = args[++i];
    }

    return parsed;
}

function main() {
    const args = parseArgs();
    let result = { success: false, action: null };

    if (args.init) {
        result = initKnowledgeRepo(args.path, args.remoteUrl);
        result.action = "init";
    } else if (args.sync) {
        result = syncKnowledgeRepo(args.path, args.remoteUrl, args.branch);
        result.action = "sync";
    } else if (args.generateIndex) {
        result = generateIndex(args.path);
        result.action = "generate_index";
    } else {
        result.error = "请指定操作: --init, --sync, 或 --generate-index";
    }

    console.log(JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
    main();
}
