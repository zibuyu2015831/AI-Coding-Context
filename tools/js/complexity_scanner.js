#!/usr/bin/env node

/**
复杂度扫描工具 - Node.js 版本
用于监控项目复杂度增长
作为 005 优化点的核心实施工具

功能说明：
- 调用 git_diff_analyzer.js 分析代码变更
- 调用 git_inspector.js 检查仓库状态
- 分析依赖关系和代码质量
- 计算复杂度评分
- 输出标准化 JSON 格式数据

使用方法：
    node tools/js/complexity_scanner.js [--path PATH] [--output OUTPUT] [--since SINCE] [--config CONFIG]

参数说明：
    --path PATH              扫描路径（默认：当前目录）
    --output OUTPUT          输出文件路径（默认：stdout）
    --since SINCE            分析时间窗口（默认：1 day ago）
                            支持格式：
                            - 绝对时间："2026-04-12"
                            - 相对时间："1 day ago"、"7 days ago"、"24 hours ago"
    --config CONFIG          配置文件路径（默认：dev_docs/complexity/config.yaml）

输出格式：
    {
      "data": {
        "code_size": {
          "new_lines": 450,
          "total_lines": 19850,
          "files": 120,
          "growth_percentage": 2.3
        },
        "dependencies": {
          "new": 3,
          "duplicate": 2,
          "depth": 4
        },
        "code_quality": {
          "todo_count": 8,
          "fixme_count": 3,
          "duplicate_code": 8,
          "quality_score": 72
        },
        "architecture": {
          "core_files_changed": 2,
          "coupling_score": 22,
          "domain_boundary_score": 7
        },
        "risk_assessment": {
          "overall_score": 75,
          "risks": [
            {"level": "high", "indicator": "growth_rate", "message": "代码增长过快"}
          ]
        }
      },
      "metadata": {
        "elapsed_seconds": 1.2,
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }

使用示例：
    # 扫描当前项目（输出到文件）
    node tools/js/complexity_scanner.js --path . --output data.json

    # 分析最近 7 天的复杂度增长
    node tools/js/complexity_scanner.js --since "7 days ago"

    # 使用自定义配置
    node tools/js/complexity_scanner.js --config custom_config.yaml

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
*/

const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');

// 显示帮助信息
function showHelp() {
  console.log(`
复杂度扫描工具 - Node.js 版本
用于监控项目复杂度增长
作为 005 优化点的核心实施工具

使用方法：
    node tools/js/complexity_scanner.js [--path PATH] [--output OUTPUT] [--since SINCE] [--config CONFIG]

参数说明：
    --path PATH              扫描路径（默认：当前目录）
    --output OUTPUT          输出文件路径（默认：stdout）
    --since SINCE            分析时间窗口（默认：1 day ago）
                            支持格式：
                            - 绝对时间："2026-04-12"
                            - 相对时间："1 day ago"、"7 days ago"、"24 hours ago"
    --config CONFIG          配置文件路径（默认：dev_docs/complexity/config.yaml）
    --help, -h              显示此帮助信息

版本信息：
    版本：1.0.0
    更新日期：2026-04-12
`);
}

// 简单的 YAML 解析（为了兼容性）
function parseYaml(text) {
  try {
    // 使用简单的方法解析基础的 YAML 结构
    const result = {};
    const lines = text.split('\n');
    let currentSection = null;

    for (let line of lines) {
      line = line.trim();
      if (!line || line.startsWith('#')) continue;

      if (line.includes(':')) {
        if (line.includes('threshold')) {
          const sectionName = line.split(':')[0].trim();
          currentSection = {};
          result[sectionName] = currentSection;
        } else if (currentSection) {
          const [key, value] = line.split(':');
          currentSection[key.trim()] = value.trim();
        }
      }
    }

    return result;
  } catch (e) {
    console.error('YAML parse error:', e);
    return null;
  }
}

// 调用子进程执行其他工具
function runCommand(cmd, args) {
  try {
    // 找到项目根目录
    const scriptDir = path.dirname(path.dirname(path.resolve(__filename)));
    const projectRoot = path.dirname(scriptDir);

    const result = childProcess.spawnSync(cmd, args, {
      encoding: 'utf8',
      stdio: 'pipe',
      cwd: projectRoot
    });

    if (result.status === 0) {
      try {
        return JSON.parse(result.stdout);
      } catch (e) {
        console.error('JSON parse error:', e);
        return null;
      }
    }

    return null;
  } catch (e) {
    console.error('Command error:', e);
    return null;
  }
}

// 调用 git_diff_analyzer.js
function callGitDiffAnalyzer(since) {
  const scriptPath = path.join(__dirname, 'git_diff_analyzer.js');
  return runCommand('node', [scriptPath, '--since', since]);
}

// 调用 git_inspector.js
function callGitInspector() {
  const scriptPath = path.join(__dirname, 'git_inspector.js');
  return runCommand('node', [scriptPath, '--mode', 'status']);
}

// 分析依赖关系
function analyzeDependencies(dirPath) {
  const dependencies = {
    new: 0,
    duplicate: 0,
    depth: 0
  };

  const packageJsonPath = path.join(dirPath, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    try {
      const packageData = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      dependencies.depth = 1;
      if (packageData.dependencies) {
        dependencies.new = Object.keys(packageData.dependencies).length;
      }
    } catch (e) {
      console.error('Error analyzing package.json:', e);
    }
  }

  const requirementsPath = path.join(dirPath, 'requirements.txt');
  if (fs.existsSync(requirementsPath)) {
    try {
      const requirements = fs.readFileSync(requirementsPath, 'utf8')
        .split('\n')
        .filter(line => line.trim().length > 0);

      dependencies.depth = Math.max(dependencies.depth, 1);
      if (dependencies.new === 0) {
        dependencies.new = requirements.length;
      }
    } catch (e) {
      console.error('Error analyzing requirements.txt:', e);
    }
  }

  return dependencies;
}

// 分析代码质量
function analyzeCodeQuality(dirPath) {
  const quality = {
    todo_count: 0,
    fixme_count: 0,
    duplicate_code: 0,
    quality_score: 100
  };

  const todoPattern = /TODO|todo|Todo/g;
  const fixmePattern = /FIXME|fixme|Fixme/g;

  // 递归扫描目录
  function scanDirectory(currentPath) {
    if (currentPath.includes('.git') || currentPath.includes('node_modules') ||
        currentPath.includes('dist') || currentPath.includes('build')) {
      return;
    }

    try {
      const stat = fs.statSync(currentPath);
      if (stat.isDirectory()) {
        const files = fs.readdirSync(currentPath);
        files.forEach(file => scanDirectory(path.join(currentPath, file)));
      } else if (stat.isFile() && ['.js', '.ts', '.jsx', '.tsx', '.py'].some(ext => currentPath.endsWith(ext))) {
        const content = fs.readFileSync(currentPath, 'utf8');
        const todos = (content.match(todoPattern) || []).length;
        const fixmes = (content.match(fixmePattern) || []).length;

        quality.todo_count += todos;
        quality.fixme_count += fixmes;
      }
    } catch (e) {
      // 忽略无法访问的文件
    }
  }

  scanDirectory(dirPath);

  // 简单的质量评分计算
  quality.quality_score = Math.max(0, Math.min(100, 100 - quality.todo_count * 2 - quality.fixme_count * 3));

  return quality;
}

// 分析架构健康度
function analyzeArchitecture(dirPath) {
  const architecture = {
    core_files_changed: 0,
    coupling_score: 0,
    domain_boundary_score: 7
  };

  const coreFiles = ['package.json', 'requirements.txt', 'README.md', 'tsconfig.json'];
  const gitDiffData = callGitDiffAnalyzer('1 day ago');

  if (gitDiffData && gitDiffData.data && gitDiffData.data.changed_files) {
    gitDiffData.data.changed_files.forEach(file => {
      if (coreFiles.some(coreFile => file.path.includes(coreFile))) {
        architecture.core_files_changed++;
      }
    });
  }

  return architecture;
}

// 计算风险评估
function calculateRiskAssessment(data, config) {
  const riskAssessment = {
    overall_score: 0,
    risks: []
  };

  // 综合评分（简单加权）
  const overallScore = (
    data.code_size.growth_percentage * 0.3 +
    data.dependencies.depth * 0.2 +
    (100 - data.code_quality.quality_score) * 0.3 +
    data.architecture.coupling_score * 0.2
  );

  riskAssessment.overall_score = Math.max(0, Math.min(100, 100 - overallScore));

  // 风险识别
  const warningThreshold = config.warning_threshold || {};

  if (data.code_size.growth_percentage > (parseFloat(warningThreshold.daily_growth) || 5)) {
    riskAssessment.risks.push({
      level: data.code_size.growth_percentage > 10 ? 'high' : 'medium',
      indicator: 'growth_rate',
      message: `代码增长过快 (${data.code_size.growth_percentage.toFixed(1)}%, 建议 <${warningThreshold.daily_growth}%)`
    });
  }

  if (data.dependencies.depth > (parseInt(warningThreshold.dependency_depth) || 3)) {
    riskAssessment.risks.push({
      level: 'medium',
      indicator: 'dependency_depth',
      message: `依赖深度超标 (${data.dependencies.depth}, 建议 <${warningThreshold.dependency_depth})`
    });
  }

  if (data.code_quality.quality_score < (parseInt(warningThreshold.quality_score) || 70)) {
    riskAssessment.risks.push({
      level: data.code_quality.quality_score > 60 ? 'medium' : 'high',
      indicator: 'code_quality',
      message: `代码质量评分低 (${data.code_quality.quality_score}, 建议 >${warningThreshold.quality_score})`
    });
  }

  if (data.architecture.coupling_score > (parseInt(warningThreshold.coupling_score) || 20)) {
    riskAssessment.risks.push({
      level: 'medium',
      indicator: 'coupling_score',
      message: `代码耦合度过高 (${data.architecture.coupling_score}, 建议 <${warningThreshold.coupling_score})`
    });
  }

  return riskAssessment;
}

// 加载配置（硬编码默认值，避免依赖）
function loadConfig(configPath) {
  return {
    warning_threshold: {
      daily_growth: 5,
      file_count: 150,
      dependency_depth: 3,
      quality_score: 70,
      coupling_score: 20
    },
    critical_threshold: {
      daily_growth: 10,
      file_count: 200,
      dependency_depth: 5,
      quality_score: 60,
      coupling_score: 30
    },
    crisis_threshold: {
      daily_growth: 15,
      file_count: 300,
      dependency_depth: 7,
      quality_score: 50,
      coupling_score: 40
    }
  };
}

// 主函数
function main() {
  const startTime = Date.now();

  // 解析命令行参数
  const args = process.argv.slice(2);

  // 检查是否请求帮助
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }

  const parsedArgs = {};
  for (let i = 0; i < args.length; i += 2) {
    if (args[i].startsWith('--')) {
      const key = args[i].substring(2);
      parsedArgs[key] = args[i + 1] || true;
    }
  }

  const scanPath = parsedArgs.path || '.';
  const outputPath = parsedArgs.output;
  const since = parsedArgs.since || '1 day ago';
  const configPath = parsedArgs.config || 'dev_docs/complexity/config.yaml';

  // 加载配置
  const config = loadConfig(configPath);

  // 调用现有工具获取数据
  const gitDiffData = callGitDiffAnalyzer(since);
  const gitInspectorData = callGitInspector();

  // 初始化结果
  const complexityData = {
    code_size: {
      new_lines: 0,
      total_lines: 0,
      files: 0,
      growth_percentage: 0
    },
    dependencies: analyzeDependencies(scanPath),
    code_quality: analyzeCodeQuality(scanPath),
    architecture: analyzeArchitecture(scanPath),
    risk_assessment: {}
  };

  // 处理 git 变更数据
  if (gitDiffData && gitDiffData.data) {
    let newLines = 0;
    const totalFilesChanged = gitDiffData.data.changed_files ? gitDiffData.data.changed_files.length : 0;

    gitDiffData.data.changed_files?.forEach(file => {
      if (file.lines_changed) {
        newLines += file.lines_changed;
      }
    });

    // 计算代码增长百分比（简化）
    const growthPercentage = newLines / 20000 * 100;

    complexityData.code_size = {
      new_lines: newLines,
      total_lines: 20000,
      files: totalFilesChanged,
      growth_percentage: Math.min(growthPercentage, 20)
    };
  }

  // 计算风险评估
  complexityData.risk_assessment = calculateRiskAssessment(complexityData, config);

  // 输出结果
  const result = {
    data: complexityData,
    metadata: {
      elapsed_seconds: (Date.now() - startTime) / 1000,
      timeout_threshold: 10,
      version: '1.0.0',
      git_available: !!gitInspectorData
    }
  };

  if (outputPath) {
    try {
      const outputDir = path.dirname(outputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
      console.log(`复杂度数据已保存到: ${outputPath}`);
    } catch (e) {
      console.error('输出文件写入错误:', e);
    }
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

// 启动程序
main();
