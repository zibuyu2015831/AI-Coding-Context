---
title: V2.3 到 V3.0 配置迁移指南
summary: 指导现有用户将 V2.3 的配置方式平滑迁移到 V3.0 的统一配置系统，涵盖自动迁移、手动迁移、差异对比和常见问题处理。
keywords: migration | config | v2.3 | v3.0 | upgrade | aicc
scope: 配置系统从 V2.3 升级到 V3.0 的迁移流程
related_files: config/CONFIG_TEMPLATE.md | config/README.md
dependencies: README.md | AI_ENTRY_POINT.md
verified_at: 2026-05-05
---

# V2.3 → V3.0 配置迁移指南

> **目标用户**: 从 V2.3 升级到 V3.0 的现有用户  
> **版本**: v1.0  
> **最后更新**: 2025-12-01

---

## 📋 概述

V3.0 引入了统一配置管理系统,本文档指导您将现有项目平滑迁移到新的配置体系。

## 🔄 自动迁移

### 触发条件

AI 启动时会自动检测:

```bash
if 检测到旧项目(无config/目录):
    进入自动迁移流程
```

### 迁移流程

**步骤 1: 检测旧配置**

```bash
# 检查是否存在旧的语言配置
检测 dev_docs/_analysis/generation_plan.md
提取 documentLanguage 配置
```

**步骤 2: 创建新配置目录**

```bash
# 创建 config/ 目录结构
mkdir -p config
cp CONFIG_TEMPLATE.md config/
创建 config/.gitignore
```

**步骤 3: 迁移配置值**

```
从 generation_plan.md 读取:
- documentLanguage (文档语言)

写入 config/user_config.md:
- 复制 CONFIG_TEMPLATE.md
- 更新 documentLanguage 值
- 其他配置使用默认值
```

**步骤 4: 提示用户**

```markdown
✅ 配置系统已启用！

📋 迁移结果:

- 文档语言: zh-CN (从旧配置迁移)
- 其他配置: 使用默认值

📁 新配置文件:

- config/user_config.md (您的个人配置)

💡 后续操作:

1. 查看 config/README.md 了解配置系统
2. 编辑 config/user_config.md 调整其他配置
3. 配置会在下次运行时自动生效
```

---

## 🔧 手动迁移

如果自动迁移失败或您希望手动操作:

### 步骤 1: 创建配置文件

```bash
# 复制模板
cp config/CONFIG_TEMPLATE.md config/user_config.md
```

### 步骤 2: 设置语言偏好

编辑 `config/user_config.md` frontmatter:

```yaml
---
documentLanguage: zh-CN # 改为您之前使用的语言
# 其他配置保持默认
---
```

### 步骤 3: 保存文件

保存后,下次运行框架时自动生效。

---

## 📊 配置对比

### V2.3 配置方式

**位置**: 散落在多处

- 语言配置: `generation_plan.md` 中记录
- 每次生成都需要询问用户

**缺点**:

- 无持久化
- 配置分散
- 重复配置

### V3.0 配置方式

**位置**: 集中在 `config/` 目录

- `config/user_config.md`: 您的个人配置
- `config/CONFIG_TEMPLATE.md`: 框架默认配置

**优点**:

- ✅ 持久化存储
- ✅ 集中管理
- ✅ 一次配置,永久生效
- ✅ 支持更多配置项

---

## 🆕 新增配置项

V3.0 新增了多个配置项,迁移后可以自定义:

| 配置项                   | 说明             | 默认值   |
| ------------------------ | ---------------- | -------- |
| `enableMutualReview`     | AI 互审机制      | false    |
| `dangerousCommandGuard`  | 危险指令拦截级别 | moderate |
| `enforceDesignThinking`  | 设计思维引导     | false    |
| `enableADR`              | 架构决策记录     | false    |
| `aiCapabilityTier`       | AI 能力分级      | auto     |
| `preferredRoles`         | 偏好的 AI 角色   | []       |
| `verboseMode`            | 详细输出模式     | false    |
| `defaultHealthCheckMode` | 默认健康检查模式 | standard |

详细说明请参阅 `config/CONFIG_TEMPLATE.md`

---

## ⚠️ 常见问题

### Q: 迁移会影响已有项目吗?

不会。配置只影响**新生成的文档**,已有项目的文档不会自动更新。

### Q: 旧的 generation_plan.md 会被删除吗?

不会。旧文件保持不变,仅读取配置值用于迁移。

### Q: 如果我不想迁移怎么办?

您可以选择:

1. 跳过迁移,每次重新配置(不推荐)
2. 手动删除 config/ 目录,恢复旧行为(不推荐)
3. 使用配置系统(推荐)

### Q: 迁移失败怎么办?

迁移失败时会降级到询问用户:

```markdown
⚠️ 自动迁移失败

原因: [错误信息]

请选择:
A. 手动配置语言偏好
B. 跳过配置系统
```

---

## 📚 相关文档

- [config/README.md](./README.md) - 配置系统使用指南
- [config/CONFIG_TEMPLATE.md](./CONFIG_TEMPLATE.md) - 所有配置项详细说明
- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 框架入口(包含迁移检测逻辑)

---

**维护者**: AI Coding Context Framework Team  
**版本**: v1.0  
**最后更新**: 2025-12-01
