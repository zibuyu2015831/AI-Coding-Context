# `dev/` —— AICC 框架自身的开发工作区

本目录承载 AICC 框架自身的开发与维护资产，**不属于框架对外发布的内容**。

## ⚠️ 不入 main / release

- `.gitattributes` 已配置 `dev/ export-ignore`：`git archive`、GitHub release tarball 会自动剔除本目录。
- **merge dev → main 时也应保持 `dev/` 不进入 main**：在合并前确认 main 不携带 `dev/`，必要时通过 `git rm -r --cached dev/ && git commit` 清除。
- 用户克隆 main 分支时不会看到本目录。

## 目录角色（与 [`FRAMEWORK_CONTEXT.md`](./FRAMEWORK_CONTEXT.md) §3.1.1 保持一致）

| 子目录 / 文件 | 用途 |
|---|---|
| `FRAMEWORK_CONTEXT.md` | 框架全局上下文（开发 AI 加载入口） |
| `architecture/` | 架构产物：ADR 模板、演进图谱、已接受决策 |
| `complexity/` | 复杂度仪表盘运行时（config + dashboard + data） |
| `quality/` | 文档质量保证体系：标准、审查 SOP、contexts、归档 |
| `V3.0/` | V3.0 规划、设计提案、进度跟踪（活跃） |
| `reference/` | 开发参考资料：理论分析、外部案例研究 |
| `case_skillatlas_review/` | SkillAtlas 项目审查案例（V3.0 019 ADR 真实来源） |
| `plan/` | 框架迭代的长期计划与蓝图（如 Skill Migration） |

## 开发 AI 的入口

开始开发 AICC 框架本身的会话前，AI 应当首先加载：

1. `dev/FRAMEWORK_CONTEXT.md` —— 全局心智模型
2. （按任务）相关 V3.0 提案 / ADR / quality 标准

详情见 `dev/quality/Start_Review.md`（启动审查）与 `dev/quality/Framework_Review_Guidelines.md`（审查方法论）。
