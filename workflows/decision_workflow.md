---
title: 策略决策流程（步骤 2-3）
summary: 定义 AI 如何根据项目规模、复杂度与上下文状态选择生成、健康检查、增量更新等执行路径，并决定批次、深度与资源投入策略。
keywords: decision | workflow | routing | strategy | project-size | aicc
scope: AI 在项目分析后的路径与策略决策
related_files: 无
dependencies: workflows/detection_workflow.md | workflows/path_a_first_generation.md | workflows/path_b_health_check.md | workflows/path_c_incremental_update.md
verified_at: 2026-05-05
---

# 策略决策流程 (步骤 2-3)

> **上级文档**: [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md)  
> **版本**: v2.2  
> **最后更新**: 2025-11-27

---

## 步骤 2: 策略决策

### 规模策略决策表

根据项目规模自动决定策略:

| 检测到的规模 (排除依赖后) | 自动选择策略      | 执行方式                |
| ------------------------- | ----------------- | ----------------------- |
| <50 文件, <5K 行          | 🟢 小型项目策略   | 一次性完成(2-4 小时)    |
| 50-200 文件, 5K-20K 行    | 🟡 中型项目策略   | 分 2-3 批(8-12 小时)    |
| 200-500 文件, 20K-50K 行  | 🔴 大型项目策略   | 分 5-8 批(1-2 天)       |
| >500 文件, >50K 行        | 🟣 超大型项目策略 | 分 10+批,按模块(1-2 周) |

---

## 步骤 3: 确定子文档清单

### 3.1 基于项目类型选择

**必读**: [项目类型规范](../core/project_types.md)

**示例 - Vue 3 前端项目**:

必需子文档(P0):

- `architecture_overview.md`
- `api_layer.md`
- `state_management.md`

推荐子文档(P1):

- `routing_guide.md`
- `component_guide.md`
- `testing_guide.md`

可选子文档(P2):

- `styling_guide.md`
- `form_validation.md`

### 3.2 复杂度因子调整 (v2.1)

**检测复杂度特征,智能调整策略级别**:

#### Monorepo 检测 (+1 级)

特征:

- 存在`pnpm-workspace.yaml`或`lerna.json`
- `package.json`中有`workspaces`字段

```bash
test -f pnpm-workspace.yaml && echo "✅ Monorepo"
```

#### 微服务架构 (+1 级)

特征:

- Docker Compose 配置多个服务
- 多个独立服务目录

```bash
test -f docker-compose.yml && grep -c "services:" docker-compose.yml
```

#### 混合语言 (+0.5 级)

检测到 ≥3 种语言 → +0.5 级

#### 多租户架构 (+0.5 级)

代码中有`tenant` / `multi-tenant`关键词

---

## 🔗 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 主流程
- [检测流程](./detection_workflow.md) - 上一步
- [生成流程](./generation_workflow.md) - 下一步

---

**版本**: v2.2  
**路径**: `workflows/decision_workflow.md`
