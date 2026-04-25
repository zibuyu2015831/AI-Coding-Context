# 工作流共享资源 (Shared Resources)

本目录为各 workflow 文档复用的横切组件，可被任意工作流引用。

## 📚 资源索引

| 文件 | 用途 |
|------|------|
| [ai_checklist.md](./ai_checklist.md) | AI 通用自检清单，所有工作流的最后一步质检 |
| [failure_handling.md](./failure_handling.md) | 失败场景与回退策略集合 |
| [special_scenarios.md](./special_scenarios.md) | 跨工作流的特殊业务场景指南 |

---

## 🧭 与其他工作流的关系

- 所有 [workflows/](../) 下的具体工作流（generation / detection / decision / health_check 等）均可引用本目录共享内容
- 共享内容**不应**包含工作流特有的步骤逻辑，仅提取通用部分
- 修改本目录文件需同时验证引用方文档，避免破坏既有工作流

---

[← 返回主文档](../../AI_ENTRY_POINT.md)
