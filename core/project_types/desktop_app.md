---
title: 桌面应用项目配置
summary: 定义桌面应用项目（Electron/Tauri/Qt）的推荐子文档清单、特殊关注点和核心代码模式。包括主进程/渲染进程架构、IPC通信、系统集成等关键规范。
keywords: desktop-app | electron | tauri | qt | ipc | native-integration | auto-update
scope: 桌面应用项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 桌面应用项目

> **适用框架**: Electron / Tauri / Qt / macOS SwiftUI/AppKit

---

## 🎯 适用框架

- **Electron**: JavaScript/TypeScript，Chromium + Node.js
- **Tauri**: Rust + Web 技术，轻量级
- **Qt**: C++/Python，跨平台原生 UI
- **macOS 原生**: SwiftUI / AppKit / Swift Package Manager

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `architecture.md` | 主进程/渲染进程 |
| 🔴 高 | `ipc_communication.md` | 进程间通信 |
| 🟡 中 | `native_integration.md` | 系统集成 |
| 🟡 中 | `auto_update.md` | 自动更新机制 |
| 🟡 中 | `packaging.md` | 打包与分发 |

---

## 🔍 特殊关注点

### 主进程 vs 渲染进程

- **主进程**: Node.js 环境，系统 API 访问
- **渲染进程**: Chromium 环境，Web 技术

### IPC 通信

- **Electron**: ipcMain / ipcRenderer
- **Tauri**: invoke / emit

### 系统集成

- 文件系统访问
- 系统托盘
- 全局快捷键
- 通知

### 自动更新

- **Electron**: electron-updater
- **Tauri**: tauri-plugin-updater

### 打包分发

- **Windows**: NSIS / Squirrel
- **macOS**: DMG / PKG
- **Linux**: AppImage / deb / rpm

### macOS / Xcode 必查文件

首次生成方案时，Swift/macOS 项目不得只扫描仓库根目录。必须检查：

- `*.xcodeproj/project.pbxproj`
- `*.xcworkspace/xcshareddata/swiftpm/Package.resolved`
- `Info.plist`
- `*.entitlements`
- `README.md`
- `scripts/`

`project_scanner` 输出中的 `dependency_manifest_candidates`、`xcode_project_files`、`platform_config_files` 应作为 Phase 1 技术栈和依赖判断的优先事实源。

---

## 💻 核心代码模式

### Electron 项目结构

```typescript
// main.ts - 主进程
import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000')
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC 处理
ipcMain.handle('read-file', async (event, filePath) => {
  const fs = require('fs').promises
  return await fs.readFile(filePath, 'utf-8')
})

// preload.ts - 预加载脚本
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (filePath: string) => ipcRenderer.invoke('read-file', filePath),
  onUpdateAvailable: (callback: () => void) => {
    ipcRenderer.on('update-available', callback)
  }
})

// renderer.ts - 渲染进程
declare global {
  interface Window {
    electronAPI: {
      readFile: (filePath: string) => Promise<string>
      onUpdateAvailable: (callback: () => void) => void
    }
  }
}

async function loadFile() {
  const content = await window.electronAPI.readFile('/path/to/file')
  console.log(content)
}
```

### Tauri 项目结构

```rust
// src-tauri/src/main.rs
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::Manager;

#[tauri::command]
async fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![read_file, greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
// src/App.tsx - 前端
import { invoke } from '@tauri-apps/api/tauri'

async function greet() {
  const message = await invoke<string>('greet', { name: 'World' })
  console.log(message)
}

async function readFile() {
  try {
    const content = await invoke<string>('read_file', {
      path: '/path/to/file'
    })
    console.log(content)
  } catch (error) {
    console.error(error)
  }
}
```

### 系统托盘

```typescript
// Electron
import { Tray, Menu } from 'electron'

let tray: Tray | null = null

function createTray() {
  tray = new Tray(path.join(__dirname, 'icon.png'))
  
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show App', click: () => mainWindow?.show() },
    { label: 'Quit', click: () => app.quit() }
  ])
  
  tray.setToolTip('My App')
  tray.setContextMenu(contextMenu)
}
```

### 自动更新

```typescript
// Electron with electron-updater
import { autoUpdater } from 'electron-updater'

autoUpdater.on('update-available', () => {
  mainWindow?.webContents.send('update-available')
})

autoUpdater.on('update-downloaded', () => {
  mainWindow?.webContents.send('update-downloaded')
})

// 检查更新
autoUpdater.checkForUpdatesAndNotify()

// 安装更新
ipcMain.on('install-update', () => {
  autoUpdater.quitAndInstall()
})
```

### 文件对话框

```typescript
// Electron
import { dialog } from 'electron'

ipcMain.handle('open-file-dialog', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  })
  
  if (!result.canceled) {
    return result.filePaths[0]
  }
  return null
})

// Tauri
import { open } from '@tauri-apps/api/dialog'

async function selectFile() {
  const selected = await open({
    multiple: false,
    filters: [{
      name: 'Text',
      extensions: ['txt']
    }]
  })
  
  if (selected) {
    console.log(selected)
  }
}
```

---

## ⚠️ 常见问题

### 问题 1: 安全问题（nodeIntegration）

**解决方案**: 使用 contextBridge 和 preload 脚本

```typescript
// ❌ 危险
webPreferences: {
  nodeIntegration: true,
  contextIsolation: false
}

// ✅ 安全
webPreferences: {
  preload: path.join(__dirname, 'preload.js'),
  contextIsolation: true,
  nodeIntegration: false
}
```

### 问题 2: 打包体积过大

**解决方案**: 使用 Tauri 或优化 Electron 打包

```javascript
// electron-builder.json
{
  "asar": true,
  "compression": "maximum",
  "files": [
    "dist/**/*",
    "!node_modules/**/*"
  ]
}
```

### 问题 3: 跨平台路径问题

**解决方案**: 使用 path 模块

```typescript
import path from 'path'

// ❌ 错误
const filePath = 'C:\\Users\\file.txt'

// ✅ 正确
const filePath = path.join(app.getPath('userData'), 'file.txt')
```

---

## 🎯 检查清单

生成桌面应用项目文档前，确认：

- [ ] 已识别主要框架（Electron/Tauri/Qt）
- [ ] 已确定目标平台（Windows/macOS/Linux）
- [ ] 已确定 IPC 通信方案
- [ ] 已确定是否需要系统托盘
- [ ] 已确定是否需要自动更新
- [ ] 已确定打包和分发策略
- [ ] 已确定安全策略（contextIsolation 等）
- [ ] 已确定文件系统访问需求

---

**版本**: v3.0  
**路径**: `core/project_types/desktop_app.md`  
**最后更新**: 2026-01-21
