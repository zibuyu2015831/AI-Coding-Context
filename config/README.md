---
title: AI Coding Context 配置系统
summary: 说明 AICC 配置目录的组成、用户配置与默认模板的关系、首次配置方式以及安全与隐私边界，帮助使用者正确理解配置系统的运行机制。
keywords: config | configuration | user-config | template | guide | aicc
scope: 框架配置系统的目录说明与使用指南
related_files: config/CONFIG_TEMPLATE.md | config/.gitignore
dependencies: README.md | AI_ENTRY_POINT.md
verified_at: 2026-05-05
---

# AI Coding Context 配置系统

## 📖 概述

本目录包含 AI Coding Context 框架的配置文件,用于管理框架行为和用户偏好。

## 📁 文件说明

### CONFIG_TEMPLATE.md

**作用**: 框架默认配置模板

**特点**:

- 包含所有可用配置项及其默认值
- 包含详细的配置说明和最佳实践
- 提交到 Git 仓库,随框架分发

**使用方式**:

- **查看**: 了解所有可用配置项
- **复制**: 创建个人配置时参考
- **严禁修改**: 这是框架默认配置,严禁修改

### user_config.md

**作用**: 用户个人配置文件

**特点**:

- 不提交到 Git(已在 .gitignore 中排除)
- 覆盖 CONFIG_TEMPLATE.md 中的默认值
- 首次使用时自动创建

**使用方式**:

1. 复制 CONFIG_TEMPLATE.md 为 user_config.md
2. 修改 frontmatter 中的配置值
3. 保存后下次运行自动生效

## 🚀 快速开始

### 首次配置

如果 `user_config.md` 不存在,框架会在首次运行时:

1. 询问基本配置(如文档语言)
2. 自动创建 `user_config.md`
3. 写入您的选择

### 手动配置

```bash
# 1. 复制模板
cp CONFIG_TEMPLATE.md user_config.md

# 2. 编辑配置
# 修改 frontmatter 中的值

# 3. 保存文件
# 配置立即生效
```

## ⚙️ 配置项说明

详细配置项说明请参阅 `CONFIG_TEMPLATE.md` 文档正文。

### 核心配置

- `documentLanguage` - 文档语言(zh-CN/en-US/ja-JP)
- `configVersion` - 配置版本(自动管理)

### V3.0 功能开关

- `enableMutualReview` - AI 互审机制
- `dangerousCommandGuard` - 危险指令拦截级别
- `enforceDesignThinking` - 设计思维引导
- `enableADR` - 架构决策记录
- `aiCapabilityTier` - AI 能力分级

### 用户偏好

- `preferredRoles` - 偏好的 AI 角色
- `verboseMode` - 详细输出模式
- `defaultHealthCheckMode` - 默认健康检查模式

## 🔒 安全与隐私

### 什么会被提交到 Git?

✅ **会提交**:

- `CONFIG_TEMPLATE.md` - 框架默认配置
- `README.md` - 本说明文档
- `.gitignore` - 排除规则

❌ **不会提交**:

- `user_config.md` - 您的个人配置
- `.system/` - 运行时状态数据

### 团队协作建议

本框架专为**独立开发者**设计,无团队配置功能。如果您在团队环境中使用:

1. **个人偏好**: 保留在 `user_config.md`(不提交)
2. **团队约定**: 在团队文档中说明推荐配置
3. **项目规范**: 在项目 README 中注明必需的功能开关

## 🔧 配置优先级

```
user_config.md (个人配置,最高)
       ↓
CONFIG_TEMPLATE.md (框架默认)
       ↓
硬编码默认值 (兜底)
```

## 📝 配置文件格式

采用 **Markdown + YAML Frontmatter** 格式:

```markdown
---
documentLanguage: zh-CN
enableMutualReview: false
---

# 配置说明

正文部分包含详细的配置项说明...
```

**为什么选择这种格式?**

1. ✅ 人类和 AI 都易读
2. ✅ 配置即文档,鼓励阅读
3. ✅ 符合框架统一的 Markdown 风格

## 🆘 常见问题

### Q: 配置不生效怎么办?

**检查步骤**:

1. 确认 `user_config.md` 位于 `config/` 目录
2. 确认 YAML frontmatter 格式正确
3. 查看框架启动时是否有警告信息

**降级机制**: 如果配置文件损坏,框架会自动使用默认配置并警告。

### Q: 如何恢复默认配置?

```bash
# 方法 1: 删除个人配置
rm user_config.md

# 方法 2: 重新复制模板
cp CONFIG_TEMPLATE.md user_config.md
```

### Q: 配置会影响已有项目吗?

不会。配置只影响**新生成的文档**。已有项目的文档不会自动更新。

### Q: V3.1 升级后配置会失效吗?

不会。框架采用**增量式设计**:

- 旧配置项继续有效
- 新配置项使用默认值
- 升级时会提示您查看新增配置项

## 📚 相关文档

- [AI_ENTRY_POINT.md](../AI_ENTRY_POINT.md) - 框架入口
- [README.md](../README.md) - 框架介绍

---

**最后更新**: 2025-12-01  
**框架版本**: V3.0
