"""
环境诊断工具 - 检测 Python 和 Node.js 运行环境

功能说明：
- 检测 Python 版本和可用性
- 检测 Node.js 版本和可用性
- 识别操作系统类型
- 验证版本是否满足最低要求

使用方法：
    python tools/py/env_diagnosis.py

参数说明：
    无参数

输出格式：
    {
      "data": {
        "python": {
          "version": "版本号",
          "path": "可执行文件路径",
          "ok": 是否满足要求(bool)
        },
        "node": {
          "version": "版本号",
          "ok": 是否满足要求(bool)
        },
        "os": "操作系统信息"
      },
      "metadata": {
        "elapsed_seconds": 耗时(秒),
        "timeout_threshold": 10,
        "version": "1.1.0"
      }
    }

使用示例：
    # 检测当前环境
    python tools/py/env_diagnosis.py

版本信息：
    版本：1.1.0
    更新日期：2025-12-02
"""

import sys
import json
import subprocess
import platform
import time

def check_node_version():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None

def main():
    start_time = time.time()
    
    python_version = sys.version.split()[0]
    node_version = check_node_version()
    
    os_info = f"{platform.system()} {platform.release()}"
    
    status = {
        "python": {
            "version": python_version,
            "path": sys.executable,
            "ok": sys.version_info >= (3, 6)
        },
        "node": {
            "version": node_version,
            "ok": False
        },
        "os": os_info
    }
    
    if node_version:
        try:
            major_version = int(node_version.lstrip('v').split('.')[0])
            status["node"]["ok"] = major_version >= 14
        except ValueError:
            pass
    
    elapsed_time = round(time.time() - start_time, 2)
    result = {
        "data": status,
        "metadata": {"elapsed_seconds": elapsed_time, "timeout_threshold": 10, "version": "1.1.0"}
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
