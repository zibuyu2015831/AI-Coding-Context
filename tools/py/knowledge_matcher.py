#!/usr/bin/env python3
"""
AICC 知识匹配与引用解析工具

功能说明：
- 解析文档中的 :::knowledge-ref::: 语法
- 从本地或共享知识库中匹配相关知识内容
- 实现多种匹配策略 (local-first, shared-first, hybrid)

使用方法：
    python tools/py/knowledge_matcher.py --ref "pattern:mvc-architecture"

参数说明：
    --ref TEXT          解析特定的引用键 (格式: type:name, 例如: pattern:mvc)
    --file PATH         解析并处理整个 Markdown 文件
    --inplace           原地修改文件 (与 --file 一起使用)
    --strategy STRATEGY 匹配策略: local-first, shared-first, hybrid (默认: 配置中的策略)

输出格式：
    文本输出，当使用 --ref 时输出匹配的知识内容，
    当使用 --file 时输出解析后的完整文档内容

使用示例：
    # 示例 1: 查找特定知识条目
    python tools/py/knowledge_matcher.py --ref "pattern:mvc-architecture"

    # 示例 2: 解析文档中的知识引用
    python tools/py/knowledge_matcher.py --file docs/guide.md

    # 示例 3: 原地修改文件
    python tools/py/knowledge_matcher.py --file docs/guide.md --inplace

    # 示例 4: 使用指定策略
    python tools/py/knowledge_matcher.py --ref "framework:react" --strategy shared-first

知识引用语法：
    在 Markdown 文档中使用以下语法引用知识：

    :::knowledge-ref pattern:mvc-architecture :::

    其中 pattern 是知识类型，mvc-architecture 是知识条目名称

版本信息：
    版本：1.0.0
    更新日期：2026-04-16
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional, List

# --- 配置常量 (同步 knowledge_cli.py) ---
CONFIG_FILE = ".aicc/knowledge_config.json"
CACHE_DIR = ".aicc-cache"
SHARED_KNOWLEDGE_DIR = os.path.join(CACHE_DIR, "shared-knowledge")
DEFAULT_LOCAL_PATH = "dev_docs/knowledge"

class KnowledgeMatcher:
    def __init__(self, config_path: str = CONFIG_FILE):
        self.config = self._load_config(config_path)
        self.local_path = self.config["knowledge"].get("local_path", DEFAULT_LOCAL_PATH)
        self.shared_path = SHARED_KNOWLEDGE_DIR
        self.shared_enabled = self.config["knowledge"]["shared"].get("enabled", False)
        self.strategy = self.config["knowledge"].get("match_strategy", "local-first")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if not os.path.exists(config_path):
            return {
                "knowledge": {
                    "local_path": DEFAULT_LOCAL_PATH,
                    "shared": {"enabled": False},
                    "match_strategy": "local-first"
                }
            }
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._load_config("")

    def find_knowledge(self, ref_key: str, context: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        根据引用键查找知识内容。
        ref_key 格式: "type:name" (例如 "pattern:mvc-architecture")
        """
        parts = ref_key.split(':')
        if len(parts) != 2:
            return None

        k_type, k_name = parts

        # 转换类型到可能的目录
        # 简单实现：在所有子目录下搜索 k_name.md

        search_paths = []
        if self.strategy == "local-first":
            search_paths = [self.local_path]
            if self.shared_enabled:
                search_paths.append(self.shared_path)
        elif self.strategy == "shared-first":
            if self.shared_enabled:
                search_paths.append(self.shared_path)
            search_paths.append(self.local_path)
        else: # hybrid (currently defaults to local-first in this simple implementation)
            search_paths = [self.local_path]
            if self.shared_enabled:
                search_paths.append(self.shared_path)

        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue

            # 递归搜索 base_path 下的 k_name.md
            for root, dirs, files in os.walk(base_path):
                # 排除 .git
                if ".git" in dirs:
                    dirs.remove(".git")

                target_file = f"{k_name}.md"
                if target_file in files:
                    file_path = os.path.join(root, target_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except:
                        continue
        return None

    def resolve_document(self, content: str) -> str:
        """
        解析并替换文档内容中的所有知识引用。
        语法: :::knowledge-ref [key] :::
        """
        pattern = r':::knowledge-ref\s+([^\s:]+:[^\s:]+)\s*:::'

        def replacer(match):
            ref_key = match.group(1)
            knowledge_content = self.find_knowledge(ref_key)
            if knowledge_content:
                # 提取内容（可选：去掉 frontmatter）
                if knowledge_content.startswith('---'):
                    parts = re.split(r'---', knowledge_content, maxsplit=2)
                    if len(parts) >= 3:
                        knowledge_content = parts[2].strip()

                return f"\n<!-- START KNOWLEDGE-REF: {ref_key} -->\n{knowledge_content}\n<!-- END KNOWLEDGE-REF: {ref_key} -->\n"
            else:
                return f"<!-- UNRESOLVED KNOWLEDGE-REF: {ref_key} -->"

        return re.sub(pattern, replacer, content)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AICC 知识匹配解析器")
    parser.add_argument("--ref", help="解析特定的引用键 (e.g., pattern:mvc)")
    parser.add_argument("--file", help="解析并处理整个 Markdown 文件")
    parser.add_argument("--inplace", action="store_true", help="原地修改文件")

    args = parser.parse_args()
    matcher = KnowledgeMatcher()

    if args.ref:
        result = matcher.find_knowledge(args.ref)
        if result:
            print(result)
        else:
            print(f"未找到引用: {args.ref}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        if not os.path.exists(args.file):
            print(f"找不到文件: {args.file}", file=sys.stderr)
            sys.exit(1)

        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()

        resolved = matcher.resolve_document(content)

        if args.inplace:
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(resolved)
            print(f"已更新文件: {args.file}")
        else:
            print(resolved)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
