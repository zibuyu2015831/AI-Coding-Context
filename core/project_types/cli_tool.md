---
title: CLI 工具项目配置
summary: 定义命令行工具项目的推荐子文档清单、特殊关注点和核心代码模式。包括命令结构、参数验证、交互式提示、输出格式等关键规范。
keywords: cli-tool | command-line | commander | yargs | click | cobra | interactive
scope: CLI 工具项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# CLI 工具项目

> **适用场景**: 命令行工具 / 开发者工具 / 运维工具

---

## 🎯 适用框架

### Node.js/TypeScript
- **Commander.js**: 功能丰富，易用
- **Yargs**: 强大的参数解析
- **oclif**: Heroku 开源，插件化
- **Ink**: React 风格的 CLI UI
- **Enquirer**: 交互式提示

### Python
- **Click**: 装饰器风格，优雅
- **Typer**: 基于类型提示，现代
- **argparse**: 标准库
- **questionary**: 交互式提示

### Go
- **Cobra**: Kubernetes/Docker 使用
- **urfave/cli**: 简洁易用
- **survey**: 交互式提示

### Rust
- **clap**: 功能强大，性能优秀
- **structopt**: 基于结构体（已合并到 clap v3）
- **dialoguer**: 交互式提示

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `cli_usage.md` | 命令使用手册 |
| 🔴 高 | `installation.md` | 安装与配置 |
| 🟡 中 | `plugin_system.md` | 插件系统（如有） |
| 🟡 中 | `configuration.md` | 配置文件说明 |
| 🟢 低 | `contributing.md` | 贡献指南 |

---

## 🔍 特殊关注点

### 命令结构设计

- **单命令**: 简单工具（如 `cat`, `grep`）
- **子命令**: 复杂工具（如 `git`, `docker`）
- **插件式**: 可扩展工具（如 `kubectl`）

### 参数验证

- 必需参数 vs 可选参数
- 参数类型验证（字符串/数字/布尔/枚举）
- 互斥参数（--verbose vs --quiet）
- 参数默认值

### 交互式提示

- 单选/多选
- 文本输入/密码输入
- 确认提示
- 进度条/加载动画

### 输出格式

- 纯文本（人类可读）
- JSON（机器可读）
- 表格（美化输出）
- 彩色输出（chalk/colorama）

### 错误提示友好性

- 清晰的错误信息
- 建议性提示
- 退出码规范（0=成功，非0=失败）

### 自动补全支持

- Bash/Zsh 补全脚本
- Fish 补全脚本

---

## 💻 核心代码模式

### Commander.js（Node.js）

```typescript
#!/usr/bin/env node
import { Command } from 'commander'
import chalk from 'chalk'
import inquirer from 'inquirer'

const program = new Command()

program
  .name('mycli')
  .description('A sample CLI tool')
  .version('1.0.0')

// 简单命令
program
  .command('hello')
  .description('Say hello')
  .option('-n, --name <name>', 'Your name', 'World')
  .action((options) => {
    console.log(chalk.green(`Hello, ${options.name}!`))
  })

// 带参数的命令
program
  .command('init')
  .description('Initialize a new project')
  .option('-t, --template <type>', 'Project template', 'basic')
  .option('-f, --force', 'Force overwrite', false)
  .action(async (options) => {
    // 交互式提示
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'projectName',
        message: 'Project name:',
        default: 'my-project'
      },
      {
        type: 'list',
        name: 'framework',
        message: 'Choose a framework:',
        choices: ['React', 'Vue', 'Angular', 'Svelte']
      }
    ])
    
    console.log(chalk.blue('Creating project...'))
    // 实现逻辑
  })

// 带子命令
const config = program.command('config').description('Manage configuration')

config
  .command('get <key>')
  .description('Get a config value')
  .action((key) => {
    console.log(`Config ${key}: ${getConfig(key)}`)
  })

config
  .command('set <key> <value>')
  .description('Set a config value')
  .action((key, value) => {
    setConfig(key, value)
    console.log(chalk.green(`✓ Config ${key} set to ${value}`))
  })

program.parse()
```

### Click（Python）

```python
#!/usr/bin/env python3
import click
from rich.console import Console
from rich.progress import Progress

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """A sample CLI tool"""
    pass

@cli.command()
@click.option('--name', '-n', default='World', help='Your name')
def hello(name):
    """Say hello"""
    console.print(f'[green]Hello, {name}![/green]')

@cli.command()
@click.option('--template', '-t', type=click.Choice(['basic', 'advanced']), default='basic')
@click.option('--force', '-f', is_flag=True, help='Force overwrite')
def init(template, force):
    """Initialize a new project"""
    project_name = click.prompt('Project name', default='my-project')
    framework = click.prompt(
        'Choose a framework',
        type=click.Choice(['React', 'Vue', 'Angular', 'Svelte'])
    )
    
    console.print('[blue]Creating project...[/blue]')
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Installing...", total=100)
        # 实现逻辑
        progress.update(task, advance=100)
    
    console.print('[green]✓ Project created successfully![/green]')

@cli.group()
def config():
    """Manage configuration"""
    pass

@config.command()
@click.argument('key')
def get(key):
    """Get a config value"""
    value = get_config(key)
    console.print(f'Config {key}: {value}')

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a config value"""
    set_config(key, value)
    console.print(f'[green]✓ Config {key} set to {value}[/green]')

if __name__ == '__main__':
    cli()
```

### Cobra（Go）

```go
package main

import (
    "fmt"
    "github.com/spf13/cobra"
    "github.com/fatih/color"
)

var rootCmd = &cobra.Command{
    Use:   "mycli",
    Short: "A sample CLI tool",
    Long:  `A sample CLI tool built with Cobra`,
}

var helloCmd = &cobra.Command{
    Use:   "hello",
    Short: "Say hello",
    Run: func(cmd *cobra.Command, args []string) {
        name, _ := cmd.Flags().GetString("name")
        color.Green("Hello, %s!", name)
    },
}

var initCmd = &cobra.Command{
    Use:   "init",
    Short: "Initialize a new project",
    Run: func(cmd *cobra.Command, args []string) {
        template, _ := cmd.Flags().GetString("template")
        force, _ := cmd.Flags().GetBool("force")
        
        color.Blue("Creating project with template: %s", template)
        // 实现逻辑
    },
}

func init() {
    helloCmd.Flags().StringP("name", "n", "World", "Your name")
    initCmd.Flags().StringP("template", "t", "basic", "Project template")
    initCmd.Flags().BoolP("force", "f", false, "Force overwrite")
    
    rootCmd.AddCommand(helloCmd)
    rootCmd.AddCommand(initCmd)
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}
```

### 进度条和加载动画

```typescript
import ora from 'ora'
import cliProgress from 'cli-progress'

// 加载动画
const spinner = ora('Loading...').start()
await doSomething()
spinner.succeed('Done!')

// 进度条
const progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic)
progressBar.start(100, 0)

for (let i = 0; i <= 100; i++) {
  progressBar.update(i)
  await sleep(50)
}

progressBar.stop()
```

### 表格输出

```typescript
import Table from 'cli-table3'

const table = new Table({
  head: ['Name', 'Age', 'Email'],
  colWidths: [20, 10, 30]
})

table.push(
  ['Alice', '25', 'alice@example.com'],
  ['Bob', '30', 'bob@example.com']
)

console.log(table.toString())
```

---

## ⚠️ 常见问题

### 问题 1: 帮助信息不清晰

**解决方案**: 提供详细的描述和示例

```typescript
program
  .command('deploy')
  .description('Deploy the application')
  .option('-e, --env <environment>', 'Target environment (dev/staging/prod)')
  .addHelpText('after', `
Examples:
  $ mycli deploy --env staging
  $ mycli deploy -e prod
  `)
```

### 问题 2: 错误提示不友好

**解决方案**: 提供清晰的错误信息和建议

```typescript
try {
  await deployApp(env)
} catch (error) {
  console.error(chalk.red('✗ Deployment failed'))
  console.error(chalk.yellow(`Reason: ${error.message}`))
  console.log(chalk.blue('\nTry:'))
  console.log('  - Check your credentials')
  console.log('  - Verify the environment name')
  process.exit(1)
}
```

### 问题 3: 缺少自动补全

**解决方案**: 生成补全脚本

```typescript
// 使用 omelette
import * as omelette from 'omelette'

const completion = omelette('mycli <command>')

completion.on('command', ({ reply }) => {
  reply(['init', 'deploy', 'config'])
})

completion.init()
```

---

## 🎯 检查清单

生成 CLI 工具项目文档前，确认：

- [ ] 已识别主要语言（Node.js/Python/Go/Rust）
- [ ] 已确定命令行框架（Commander/Click/Cobra 等）
- [ ] 已确定是否需要交互式提示
- [ ] 已确定输出格式（文本/JSON/表格）
- [ ] 已确定是否需要进度条/加载动画
- [ ] 已确定配置文件格式（JSON/YAML/TOML）
- [ ] 已确定是否需要插件系统
- [ ] 已确定是否需要自动补全
- [ ] 已确定错误处理策略

---

**版本**: v3.0  
**路径**: `core/project_types/cli_tool.md`  
**最后更新**: 2026-01-21
