# Windows 降级命令速查表 (PowerShell)

当 Python 或 Node.js 不可用时，请使用这些 PowerShell 命令。

## 1. 项目结构扫描

```powershell
# 递归列出文件，排除 .git 和 node_modules
Get-ChildItem -Recurse -Exclude .git,node_modules | Select-Object FullName
```

## 2. 文件读取

```powershell
# 读取文件内容 (前 100 行)
Get-Content -Path "path/to/file" -TotalCount 100
```

## 3. 内容搜索

```powershell
# 递归搜索字符串
Get-ChildItem -Recurse -Filter "*.js" | Select-String -Pattern "search_term"
```

## 4. 环境检查

```powershell
$PSVersionTable.PSVersion
```
