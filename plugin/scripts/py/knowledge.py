#!/usr/bin/env python3
"""AICC knowledge base CLI: local entries + optional shared git repo.

Layout (compatible with the clone-form tools):
  dev_docs/knowledge/                local entries (committed with the project)
  .aicc/knowledge_config.json        config (shared repo url, enabled flag)
  .aicc-cache/shared-knowledge/      clone of the shared repo (gitignored)

Commands:
  status                       show local/shared state
  enable-shared <git-url>      clone the shared repo and enable it
  disable-shared               stop searching the shared repo
  update                       git pull the shared repo
  search <terms...>            grep local (and enabled shared) entries
"""

import argparse
import json
import os
import re
import subprocess
import sys

LOCAL_DIR = "dev_docs/knowledge"
CONFIG_PATH = ".aicc/knowledge_config.json"
CACHE_DIR = ".aicc-cache/shared-knowledge"


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")


def ensure_gitignored(path):
    line = path.rstrip("/") + "/"
    try:
        existing = open(".gitignore", "r", encoding="utf-8").read() if os.path.exists(".gitignore") else ""
        if line not in existing:
            with open(".gitignore", "a", encoding="utf-8") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write(line + "\n")
    except OSError:
        pass


def git(args, cwd=None):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def cmd_status(_):
    config = load_config()
    print("local: %s (%d entries)" % (
        "present" if os.path.isdir(LOCAL_DIR) else "absent",
        sum(1 for _, _, names in os.walk(LOCAL_DIR) for n in names
            if n.endswith(".md") and n != "README.md") if os.path.isdir(LOCAL_DIR) else 0))
    shared = config.get("shared", {})
    if shared.get("enabled"):
        print("shared: enabled — %s (cache: %s)" % (shared.get("url", "?"),
              "present" if os.path.isdir(CACHE_DIR) else "missing — run update"))
    else:
        print("shared: disabled")
    return 0


def cmd_enable_shared(args):
    result = git(["clone", "--depth", "1", args.url, CACHE_DIR]) \
        if not os.path.isdir(CACHE_DIR) else git(["pull"], cwd=CACHE_DIR)
    if result.returncode != 0:
        print("git failed: %s" % result.stderr.strip())
        return 1
    config = load_config()
    config["shared"] = {"enabled": True, "url": args.url}
    save_config(config)
    ensure_gitignored(".aicc-cache")
    print("shared knowledge enabled: %s" % args.url)
    return 0


def cmd_disable_shared(_):
    config = load_config()
    config.setdefault("shared", {})["enabled"] = False
    save_config(config)
    print("shared knowledge disabled (cache kept)")
    return 0


def cmd_update(_):
    if not os.path.isdir(CACHE_DIR):
        print("no shared cache; run enable-shared <git-url> first")
        return 1
    result = git(["pull"], cwd=CACHE_DIR)
    print(result.stdout.strip() or result.stderr.strip())
    return result.returncode


def search_dir(root, pattern, label):
    hits = []
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(base, name)
            try:
                text = open(path, "r", encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if pattern.search(text) or pattern.search(name):
                title = ""
                match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                hits.append((label, path, title))
    return hits


def cmd_search(args):
    pattern = re.compile("|".join(re.escape(t) for t in args.terms), re.IGNORECASE)
    hits = []
    if os.path.isdir(LOCAL_DIR):
        hits += search_dir(LOCAL_DIR, pattern, "local")
    config = load_config()
    if config.get("shared", {}).get("enabled") and os.path.isdir(CACHE_DIR):
        hits += search_dir(CACHE_DIR, pattern, "shared")
    if not hits:
        print("no knowledge entries match: %s" % " ".join(args.terms))
        return 1
    for label, path, title in hits:
        print("[%s] %s%s" % (label, path, " — " + title if title else ""))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="AICC knowledge base CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    enable = sub.add_parser("enable-shared")
    enable.add_argument("url", help="git URL of the shared knowledge repo")
    sub.add_parser("disable-shared")
    sub.add_parser("update")
    search = sub.add_parser("search")
    search.add_argument("terms", nargs="+")
    args = parser.parse_args(argv)
    return {
        "status": cmd_status, "enable-shared": cmd_enable_shared,
        "disable-shared": cmd_disable_shared, "update": cmd_update,
        "search": cmd_search,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
