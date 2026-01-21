---
title: 脚本项目配置
summary: 定义脚本项目（Python脚本/Shell脚本/数据处理/自动化任务）的推荐子文档清单、特殊关注点和核心代码模式。包括脚本使用说明、配置管理、错误处理等关键规范。
keywords: script | python | shell | automation | data-processing | cron | scheduling
scope: 脚本项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 脚本项目

> **适用场景**: Python 脚本 / Shell 脚本 / 数据处理 / 自动化任务

---

## 🎯 适用语言

- **Python**: 数据处理、自动化、系统管理
- **Bash/Shell**: 系统管理、部署脚本
- **PowerShell**: Windows 自动化
- **JavaScript/Node.js**: 构建脚本、自动化工具
- **Ruby**: 系统管理、自动化

---

## 📋 推荐子文档清单

| 优先级 | 文档名称            | 用途         |
| ------ | ------------------- | ------------ |
| 🔴 高  | `script_usage.md`   | 脚本使用说明 |
| 🔴 高  | `configuration.md`  | 配置文件说明 |
| 🟡 中  | `data_flow.md`      | 数据流程图   |
| 🟡 中  | `error_handling.md` | 异常处理机制 |
| 🟢 低  | `scheduling.md`     | 定时任务配置 |

---

## 🔍 特殊关注点

### 环境依赖

- **Python**: 虚拟环境（venv/conda）
- **系统依赖**: apt/yum/brew 包
- **环境变量**: 配置和凭证

### 配置管理

- **环境变量**: `.env` 文件
- **配置文件**: YAML/JSON/TOML
- **命令行参数**: argparse/click

### 日志输出

- **位置**: 文件/标准输出
- **格式**: 结构化日志（JSON）
- **轮转**: logrotate/TimedRotatingFileHandler

### 错误恢复机制

- 重试逻辑
- 断点续传
- 错误通知（邮件/Slack）

### 定时任务设置

- **Linux**: cron/systemd timer
- **Windows**: Task Scheduler
- **Python**: schedule/APScheduler

---

## 💻 核心代码模式

### Python 脚本结构

```python
#!/usr/bin/env python3
"""
数据处理脚本

用途: 从 API 获取数据并保存到数据库
使用: python script.py --config config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/script.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def process_data(config: dict):
    """处理数据的主要逻辑"""
    try:
        logger.info("开始处理数据")
        
        # 实现逻辑
        api_url = config['api']['url']
        db_conn = config['database']['connection_string']
        
        # 获取数据
        data = fetch_data(api_url)
        
        # 保存数据
        save_to_database(data, db_conn)
        
        logger.info("数据处理完成")
        return True
        
    except Exception as e:
        logger.error(f"处理数据时出错: {e}", exc_info=True)
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据处理脚本')
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='配置文件路径'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行，不实际执行'
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 处理数据
    if args.dry_run:
        logger.info("模拟运行模式")
        return 0
    
    success = process_data(config)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
```

### Shell 脚本结构

```bash
#!/bin/bash
set -euo pipefail  # 错误时退出，未定义变量报错，管道错误传播

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/backup.log"
CONFIG_FILE="${SCRIPT_DIR}/config.sh"

# 加载配置
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    echo "配置文件不存在: $CONFIG_FILE" >&2
    exit 1
fi

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

# 错误处理
trap 'log_error "脚本在第 $LINENO 行失败"' ERR

# 主要逻辑
backup_database() {
    local db_name="$1"
    local backup_dir="$2"
    
    log "开始备份数据库: $db_name"
    
    # 创建备份目录
    mkdir -p "$backup_dir"
    
    # 执行备份
    local backup_file="${backup_dir}/${db_name}_$(date +%Y%m%d_%H%M%S).sql"
    
    if pg_dump "$db_name" > "$backup_file"; then
        log "备份成功: $backup_file"
        
        # 压缩备份
        gzip "$backup_file"
        log "压缩完成: ${backup_file}.gz"
        
        return 0
    else
        log_error "备份失败: $db_name"
        return 1
    fi
}

# 主函数
main() {
    log "脚本开始执行"
    
    # 检查必需的命令
    for cmd in pg_dump gzip; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "未找到命令: $cmd"
            exit 1
        fi
    done
    
    # 执行备份
    if backup_database "$DB_NAME" "$BACKUP_DIR"; then
        log "所有任务完成"
        exit 0
    else
        log_error "任务失败"
        exit 1
    fi
}

main "$@"
```

### 配置文件示例

```yaml
# config.yaml
api:
  url: https://api.example.com/data
  timeout: 30
  retry: 3

database:
  connection_string: postgresql://user:pass@localhost/db
  pool_size: 5

logging:
  level: INFO
  file: logs/script.log
  max_bytes: 10485760  # 10MB
  backup_count: 5

schedule:
  enabled: true
  cron: "0 2 * * *"  # 每天凌晨2点
```

### 定时任务配置

```bash
# crontab -e
# 每天凌晨2点运行
0 2 * * * /path/to/venv/bin/python /path/to/script.py --config /path/to/config.yaml >> /path/to/logs/cron.log 2>&1

# 每小时运行
0 * * * * /path/to/script.sh

# 每5分钟运行
*/5 * * * * /path/to/script.py
```

### Python 定时任务

```python
import schedule
import time

def job():
    """定时执行的任务"""
    logger.info("执行定时任务")
    process_data()

# 每天10:30执行
schedule.every().day.at("10:30").do(job)

# 每小时执行
schedule.every().hour.do(job)

# 每5分钟执行
schedule.every(5).minutes.do(job)

# 运行调度器
while True:
    schedule.run_pending()
    time.sleep(1)
```

### 错误处理和重试

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1, backoff=2):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"重试{max_attempts}次后仍然失败: {e}")
                        raise
                    
                    logger.warning(f"第{attempts}次尝试失败，{current_delay}秒后重试: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2, backoff=2)
def fetch_data(url):
    """获取数据（带重试）"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## 📝 主文档特殊章节

### 环境准备

```markdown
## 🚀 快速开始

### 环境准备

#### Python项目
\`\`\`bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
\`\`\`

#### Shell脚本
\`\`\`bash
chmod +x script.sh
\`\`\`
```

### 运行示例

```markdown
### 运行示例

#### 基本运行
\`\`\`bash
python main.py --config config.yaml
\`\`\`

#### 定时运行
\`\`\`bash
# 添加到 crontab
0 2 * * * /path/to/script.py
\`\`\`
```

### 关键文件说明

```markdown
## 📁 关键文件说明

- `config.yaml` - 配置文件
- `requirements.txt` - Python 依赖
- `logs/` - 日志目录
- `data/` - 数据目录
```

---

## ⚠️ 常见问题

### 问题 1: 路径问题

**解决方案**: 使用绝对路径或相对于脚本的路径

```python
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent

# 构建配置文件路径
config_path = SCRIPT_DIR / 'config.yaml'
```

### 问题 2: 凭证硬编码

**解决方案**: 使用环境变量或配置文件

```python
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量获取
api_key = os.getenv('API_KEY')
db_password = os.getenv('DB_PASSWORD')
```

### 问题 3: 没有日志

**解决方案**: 添加完善的日志记录

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('script.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🎯 检查清单

生成脚本项目文档前，确认：

- [ ] 已识别主要语言（Python/Shell/PowerShell）
- [ ] 已确定环境依赖（虚拟环境/系统包）
- [ ] 已确定配置管理方式（环境变量/配置文件）
- [ ] 已确定日志策略（位置/格式/轮转）
- [ ] 已确定错误处理机制（重试/通知）
- [ ] 已确定是否需要定时任务
- [ ] 已确定数据流程
- [ ] 已准备使用说明和示例

---

**版本**: v3.0  
**路径**: `core/project_types/script.md`  
**最后更新**: 2026-01-21
