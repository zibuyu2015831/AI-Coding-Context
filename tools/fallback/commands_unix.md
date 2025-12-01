# Unix 降级命令速查表 (Bash)

当 Python 或 Node.js 不可用时，请使用这些 Bash 命令。

## 1. 项目结构扫描

```bash
# 递归列出文件，排除 .git 和 node_modules
find . -type d \( -name .git -o -name node_modules \) -prune -o -type f -print
```

## 2. 文件读取

```bash
# 读取文件内容 (前 100 行)
head -n 100 "path/to/file"
```

## 3. 内容搜索

```bash
# 递归搜索字符串
grep -r "search_term" . --exclude-dir={.git,node_modules}
```

## 4. 环境检查

```bash
uname -a
```
