"""
文档摘要验证工具 - 验证YAML Frontmatter摘要的格式和完整性

功能说明:
    - 验证YAML Frontmatter格式正确性
    - 检查必填字段是否完整
    - 验证related_files和dependencies文件是否存在
    - 检测摘要是否过期(>90天)
    - 提供详细的错误、警告和建议

使用方法:
    # 验证单个文件
    python tools/py/summary_validator.py --file dev_docs/api_layer.md
    
    # 批量验证目录
    python tools/py/summary_validator.py --dir dev_docs/
    
    # 递归验证
    python tools/py/summary_validator.py --dir dev_docs/ --recursive
    
    # 严格模式(警告也视为失败)
    python tools/py/summary_validator.py --file dev_docs/api_layer.md --strict

参数说明:
    --file PATH          单个Markdown文件路径
    --dir PATH           批量验证目录路径
    --recursive          递归扫描子目录
    --strict             严格模式,警告也视为失败
    --timeout SECONDS    超时时间,默认10秒

输出格式:
    {
      "success": true,
      "data": {
        "file": "dev_docs/api_layer.md",
        "valid": true,
        "errors": [],
        "warnings": ["摘要已过期 120 天"],
        "suggestions": ["建议更新 verified_at 字段"]
      },
      "metadata": {
        "elapsed_seconds": 0.15,
        "timeout_threshold": 10,
        "version": "1.0.0"
      }
    }

验证规则:
    1. 必填字段: title, summary, keywords, scope, related_files, dependencies, verified_at
    2. 字段格式: keywords/related_files/dependencies 为列表(|分隔)
    3. 文件存在性: related_files和dependencies中的文件应该存在
    4. 过期检测: verified_at距今>90天标记为警告

版本信息:
    Version: 1.0.0
    Created: 2025-12-03
    Purpose: Support 012-Mandatory Document Summary mechanism
"""

import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

VERSION = "1.0.0"
DEFAULT_TIMEOUT = 10
REQUIRED_FIELDS = ['title', 'summary', 'keywords', 'scope', 'related_files', 'dependencies', 'verified_at']
EXPIRY_DAYS = 90

def extract_frontmatter(content):
    """提取YAML Frontmatter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    yaml_content = match.group(1)
    return parse_yaml_simple(yaml_content)

def parse_yaml_simple(yaml_str):
    """简单的YAML解析器"""
    result = {}
    lines = yaml_str.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        if not value or value.lower() in ['无', 'none', '']:
            result[key] = None
        elif '|' in value:
            result[key] = [item.strip() for item in value.split('|') if item.strip()]
        else:
            value = value.strip('"\'')
            result[key] = value
    
    return result

def validate_date_format(date_str):
    """验证日期格式 YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False

def check_file_exists(file_path, base_dir):
    """检查文件是否存在"""
    # 处理相对路径和绝对路径
    if os.path.isabs(file_path):
        return os.path.exists(file_path)
    else:
        # 相对于项目根目录
        full_path = os.path.join(base_dir, file_path)
        return os.path.exists(full_path)

def validate_summary(file_path, project_root=None):
    """
    验证单个文件的摘要
    
    Returns:
        dict: 验证结果
    """
    if project_root is None:
        # 尝试找到项目根目录
        project_root = os.getcwd()
        # 如果文件路径包含多个目录层级,向上查找项目根
        file_dir = os.path.dirname(os.path.abspath(file_path))
        while file_dir != os.path.dirname(file_dir):  # 直到根目录
            if os.path.exists(os.path.join(file_dir, 'package.json')) or \
               os.path.exists(os.path.join(file_dir, '.git')):
                project_root = file_dir
                break
            file_dir = os.path.dirname(file_dir)
    
    result = {
        "file": file_path,
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = extract_frontmatter(content)
        
        if not summary:
            result["valid"] = False
            result["errors"].append("未找到 YAML Frontmatter")
            return result
        
        # 检查必填字段
        missing_fields = [field for field in REQUIRED_FIELDS if field not in summary]
        if missing_fields:
            result["valid"] = False
            result["errors"].append(f"缺少必填字段: {', '.join(missing_fields)}")
        
        # 检查日期格式
        if 'verified_at' in summary and summary['verified_at']:
            if not validate_date_format(summary['verified_at']):
                result["errors"].append(f"verified_at 日期格式错误,应为 YYYY-MM-DD: {summary['verified_at']}")
                result["valid"] = False
            else:
                # 检查是否过期
                verified_date = datetime.strptime(summary['verified_at'], '%Y-%m-%d')
                days_old = (datetime.now() - verified_date).days
                if days_old > EXPIRY_DAYS:
                    result["warnings"].append(f"摘要已过期 {days_old} 天 (阈值: {EXPIRY_DAYS}天)")
                    result["suggestions"].append("建议更新 verified_at 字段")
        
        # 检查related_files文件存在性
        if 'related_files' in summary and summary['related_files']:
            if isinstance(summary['related_files'], list):
                for rel_file in summary['related_files']:
                    if rel_file and rel_file != '无':
                        if not check_file_exists(rel_file, project_root):
                            result["warnings"].append(f"关联文件不存在: {rel_file}")
        
        # 检查dependencies文件存在性
        if 'dependencies' in summary and summary['dependencies']:
            if isinstance(summary['dependencies'], list):
                for dep_file in summary['dependencies']:
                    if dep_file and dep_file != '无':
                        if not check_file_exists(dep_file, project_root):
                            result["warnings"].append(f"依赖文档不存在: {dep_file}")
        
        # 检查字段类型
        for field in ['keywords', 'related_files', 'dependencies']:
            if field in summary and summary[field] is not None:
                if not isinstance(summary[field], list) and summary[field] != '无':
                    result["warnings"].append(f"{field} 应为列表格式(使用 | 分隔)")
        
        # 如果有错误,valid为False
        if result["errors"]:
            result["valid"] = False
        
        return result
        
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"验证失败: {str(e)}")
        return result

def find_markdown_files(directory, recursive=False):
    """查找目录下的所有Markdown文件"""
    md_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'dist', 'build'}]
            
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith('.md'):
                md_files.append(file_path)
    
    return md_files

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(
        description="验证Markdown文档的YAML Frontmatter摘要",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--file", help="单个Markdown文件路径")
    parser.add_argument("--dir", help="批量验证目录路径")
    parser.add_argument("--recursive", action="store_true", help="递归扫描子目录")
    parser.add_argument("--strict", action="store_true", help="严格模式,警告也视为失败")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"超时时间(秒),默认{DEFAULT_TIMEOUT}秒")
    
    args = parser.parse_args()
    
    # 参数验证
    if not args.file and not args.dir:
        parser.error("必须指定 --file 或 --dir 参数")
    
    if args.file and args.dir:
        parser.error("--file 和 --dir 不能同时使用")
    
    result = {
        "success": True,
        "data": {},
        "metadata": {
            "elapsed_seconds": 0,
            "timeout_threshold": args.timeout,
            "strict_mode": args.strict,
            "version": VERSION
        }
    }
    
    try:
        # 单文件模式
        if args.file:
            if not os.path.isfile(args.file):
                result["success"] = False
                result["error"] = f"File not found: {args.file}"
            else:
                validation = validate_summary(args.file)
                result["data"] = validation
                
                # 严格模式下,警告也视为失败
                if args.strict and validation.get("warnings"):
                    result["success"] = False
                elif not validation.get("valid"):
                    result["success"] = False
        
        # 批量模式
        else:
            if not os.path.isdir(args.dir):
                result["success"] = False
                result["error"] = f"Directory not found: {args.dir}"
            else:
                md_files = find_markdown_files(args.dir, args.recursive)
                
                validations = []
                total_valid = 0
                total_invalid = 0
                total_warnings = 0
                
                for md_file in md_files:
                    # 检查超时
                    if time.time() - start_time > args.timeout:
                        result["warning"] = "Timeout reached, partial results returned"
                        break
                    
                    validation = validate_summary(md_file)
                    validations.append(validation)
                    
                    if validation.get("valid"):
                        total_valid += 1
                    else:
                        total_invalid += 1
                    
                    if validation.get("warnings"):
                        total_warnings += len(validation["warnings"])
                
                result["data"] = {
                    "validations": validations,
                    "total_files": len(md_files),
                    "processed": len(validations),
                    "valid": total_valid,
                    "invalid": total_invalid,
                    "total_warnings": total_warnings
                }
                
                # 严格模式下,有警告也视为失败
                if args.strict and total_warnings > 0:
                    result["success"] = False
                elif total_invalid > 0:
                    result["success"] = False
    
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    # 计算耗时
    elapsed_time = round(time.time() - start_time, 2)
    result["metadata"]["elapsed_seconds"] = elapsed_time
    
    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
