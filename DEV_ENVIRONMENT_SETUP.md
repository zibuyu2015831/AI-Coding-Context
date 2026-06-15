# 开发环境搭建与多设备协作指南

> 本文说明如何在一台**新设备**上完整复刻本仓库的开发环境，使其与现有设备一致地进行 `dev` 分支开发，并正确挂载 `internal` 分支的框架维护资料。
>
> 适用对象：框架维护者 / 贡献者。最终用户只需 `git clone` 后阅读 [`AI_ENTRY_POINT.md`](AI_ENTRY_POINT.md)，无需本文。

---

## 1. 三分支模型概述

本仓库采用**三分支模型**，三者职责互不重叠（详见 [`CONTRIBUTING.md`](CONTRIBUTING.md) 的"分支模型与框架文档贡献规范"）：

| 分支 | 面向 | 内容 | 远程状态 |
|------|------|------|----------|
| `master` | **最终用户** | 干净的可用框架（clone+入口文档用法 + `plugin/` 插件用法），不含任何开发过程内容 | ✅ 已推送 `origin/master` |
| `dev` | 集成 / 测试 | 与 `master` **结构相同**的产品树；功能在此开发与测试，通过后合并入 `master` | ✅ 已推送 `origin/dev` |
| `internal` | 框架维护者 | 开发过程元数据：质量保证体系、计划、ADR、评审报告等。**孤儿分支，与 dev/master 无共同历史，永不参与其合并** | ✅ 已推送 `origin/internal` |
| `archive/master-v3-early` | 历史备份 | 插件化改造前的 master 快照 | ✅ 已推送 |

**关键设计原则：** `dev` 与 `master` 的文件结构必须始终保持一致。所有开发过程文件（`dev/` 目录、`FRAMEWORK_REVIEW*.md` 等）只能存在于 `internal` 分支，绝不能加回 `dev`/`master`，否则 `merge dev → master` 会产生 modify/delete 冲突，并可能把开发内容泄漏给用户。

`internal` 是**孤儿分支**：它没有和 dev/master 共享任何提交历史，因此本地通过 **git worktree** 把它挂载到 `_internal/` 子目录使用，而 `_internal/` 已在 `.gitignore` 中忽略，不会污染 dev/master 的工作树。

---

## 2. 远程现状（截至本文撰写）

所有分支均已推送到远程，新设备可以完整获取：

```
remote: git@github.com:zibuyu2015831/AI-Coding-Context.git

origin/master                  ← 用户面向的干净框架
origin/dev                     ← 开发分支（在此进行日常开发）
origin/internal                ← 框架维护资料（孤儿分支，本地以 worktree 挂载）
origin/archive/master-v3-early ← 历史备份
```

因此：**在任何已配置好 GitHub 访问权限的设备上，都可以一比一复刻当前开发环境。**

---

## 3. 新设备完整复刻步骤

### 3.1 前置条件

- 已安装 Git（建议 2.20+，确保 `git worktree` 可用）。
- 已为该设备配置好对 GitHub 仓库的访问（SSH key 或 HTTPS 凭据）。本仓库使用 SSH 地址，需先在 GitHub 账户添加该设备的 SSH 公钥。

### 3.2 克隆并切换到 dev

```bash
# 1. 克隆仓库（默认检出 master）
git clone git@github.com:zibuyu2015831/AI-Coding-Context.git
cd AI-Coding-Context

# 2. 切换到 dev 分支进行开发
git checkout dev
```

> `git clone` 默认只检出远程默认分支（master）。`git checkout dev` 会自动创建本地 `dev` 并跟踪 `origin/dev`。

### 3.3 挂载 internal 分支的 worktree（可选但推荐）

`internal` 分支的资料**不会**随 `git clone` 自动出现在工作目录里——你需要显式把它挂载为一个 worktree：

```bash
# 在仓库根目录执行，把 internal 分支挂载到 ./_internal 子目录
git worktree add _internal internal
```

完成后目录结构如下（`_internal/` 已被 `.gitignore` 忽略，不影响 dev 工作树）：

```
AI-Coding-Context/      ← dev 分支工作树
├── AI_ENTRY_POINT.md
├── CONTRIBUTING.md
├── plugin/
├── ...
└── _internal/          ← internal 分支工作树（gitignored）
    └── dev/
        ├── quality/    ← 质量保证体系
        ├── plan/
        └── architecture/
```

### 3.4 一键复刻命令汇总

```bash
git clone git@github.com:zibuyu2015831/AI-Coding-Context.git
cd AI-Coding-Context
git checkout dev
git worktree add _internal internal
```

执行完这四步，新设备的环境就与现有设备完全一致。

---

## 4. 日常开发工作流

### 4.1 在 dev 上开发并推送

```bash
# 确保在 dev 分支
git checkout dev

# 拉取最新（多设备协作时务必先 pull）
git pull origin dev

# ... 修改文件 ...

git add -A
git commit -m "feat: 你的改动说明"
git push origin dev
```

### 4.2 dev → master 发布

功能在 `dev` 测试通过后，合并入 `master`（按设计为 fast-forward，无冲突）：

```bash
git checkout master
git pull origin master
git merge dev          # 设计上为干净的 fast-forward
git push origin master
git checkout dev       # 切回 dev 继续开发
```

### 4.3 在 internal 上更新维护资料

`internal` 的改动在 `_internal/` worktree 里独立提交：

```bash
cd _internal
git add -A
git commit -m "docs(internal): 更新质量体系/计划/评审"
git push origin internal
cd ..
```

> 注意：`_internal/` 是 internal 分支的工作树，在其中执行 git 命令操作的是 `internal` 分支，与外层 dev 工作树互不干扰。

---

## 5. 多设备协作注意事项

1. **`_internal/` 不随 clone 复制。** 每台新设备都要单独执行一次 `git worktree add _internal internal`。它是本地挂载点，不是被跟踪的目录。

2. **开发前先 `git pull`。** 多设备并行开发时，在 `dev` 和 `internal` 上动手前都应先拉取远程最新，避免分叉。

3. **严守分支隔离。** 永远不要把 `dev/`、`FRAMEWORK_REVIEW*.md`、`PLUGIN_BUILD_KICKOFF.md`、`framework_improvement_*.md` 等开发过程文件提交到 `dev`/`master`。它们只属于 `internal`。

4. **同一仓库内一个分支只能被一个 worktree 检出。** 如果某分支已在别处检出，`git worktree add` 会报错；这是 Git 的保护机制，不是故障。

5. **删除 worktree 用专用命令**，不要直接 `rm -rf`：
   ```bash
   git worktree remove _internal
   ```

---

## 6. 常见问题排查

**Q: `git checkout dev` 提示 `pathspec 'dev' did not match`？**
远程引用未拉全。执行 `git fetch origin` 后重试。

**Q: clone 后看不到 `_internal/` 目录？**
正常现象——它需要手动 `git worktree add _internal internal` 挂载（见 3.3）。

**Q: `git worktree add` 报 `'internal' is already checked out`？**
该分支已被另一个 worktree 占用。用 `git worktree list` 查看当前所有挂载点。

**Q: 想确认本地分支是否与远程同步？**
```bash
git branch -vv                       # 查看各本地分支跟踪与领先/落后情况
git rev-list --left-right --count origin/dev...dev   # 输出 "0  0" 表示完全同步
```

**Q: 推送被拒绝（rejected, non-fast-forward）？**
远程有他人新提交。先 `git pull origin <branch>`（必要时 rebase）再 push。

---

## 相关文档

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — 分支模型与框架文档贡献规范（权威说明）
- [`AI_ENTRY_POINT.md`](AI_ENTRY_POINT.md) — 框架使用入口（最终用户）
- [`README.md`](README.md) — 项目总览
