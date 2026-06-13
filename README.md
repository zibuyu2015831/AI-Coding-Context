# internal — 框架开发元数据分支

> ⚠️ 这是一个**孤儿分支**(orphan branch),与 `master` / `dev` **没有共同历史**,因此**永远不会参与 `dev ↔ master` 的合并**。这是刻意的隔离设计。

## 这个分支装什么

只装"开发框架本身"才需要、但**绝不能发给最终用户**的过程性内容:

- `dev/quality/` — 框架文档质量保证体系(审查流程、标准、checklist、历次 audit 记录)
- `dev/plan/` — 各阶段开发计划
- `dev/architecture/` — 架构决策记录(ADR)、演进记录
- `dev/complexity/` — 复杂度仪表盘等
- `FRAMEWORK_REVIEW*.md` / `PLUGIN_BUILD_KICKOFF.md` / `framework_improvement_*.md` — 评审与改进报告

## 三分支模型

| 分支 | 面向 | 内容 |
|------|------|------|
| `master` | **最终用户** | 干净的可用框架(clone+入口文档用法 + `plugin/` 插件用法),零开发内容 |
| `dev` | 集成 / 测试 | 与 `master` **结构相同**的产品树;功能在此开发与测试,通过后合并入 `master` |
| `internal`(本分支) | 框架维护者 | 上述开发过程元数据;游离于合并图之外 |

## 开发时如何使用

在主仓库里用 worktree 把本分支挂到本地(`_internal/` 已被 `dev`/`master` 的 `.gitignore` 忽略):

```bash
git worktree add _internal internal
# 质量体系总览见 _internal/dev/quality/README.md
```

## 维护准则

- **不要**把 `dev/`、`FRAMEWORK_REVIEW*.md` 等本分支内容加回 `dev` 或 `master`——否则会破坏隔离,并在下次 `merge dev → master` 时产生 modify/delete 冲突。
- 本分支独立提交即可,无需与 `dev`/`master` 同步。
