# 016 - 配置管理系统实施方案

**优化点**: 016-unified-config-system  
**优先级**: P0 (基础设施)  
**预估工作量**: 4 天  
**文档版本**: v1.0  
**最后更新**: 2025-12-01

---

## 📋 实施概述

本文档详细说明配置管理系统（含智能系统追踪器）的实施步骤。该系统是 V3.0 多个优化点的基础设施，优先级为 P0。

**核心目标**:

1. 建立统一的配置管理系统
2. 支持用户偏好持久化
3. 提供 V3.0 功能开关
4. 实现 System Tracker 智能推荐

---

## 🎯 实施阶段

### 阶段 1: 设计和规范（1 天）

#### 任务清单

**1.1 确认配置 Schema**

- [ ] 定义所有用户可见配置项（9 个）
  - documentLanguage
  - configVersion
  - enableMutualReview
  - dangerousCommandGuard
  - enforceDesignThinking
  - enableADR
  - aiCapabilityTier
  - preferredRoles
  - verboseMode
  - defaultHealthCheckMode
- [ ] 定义内部配置项
  - 框架内部阈值
  - 系统路径配置
  - 调试选项
  - System Tracker 阈值
- [ ] 设置默认值

**1.2 编写 config/README.md**

- [ ] 创建 `config/README.md`
- [ ] 内容包含：
  - 配置系统概述
  - 文件说明（CONFIG_TEMPLATE.md, user_config.md）
  - 快速开始指南
  - 配置项说明
  - 安全与隐私
  - 配置优先级说明
  - 常见问题

**1.3 编写 config/CONFIG_TEMPLATE.md**

- [ ] 创建 `config/CONFIG_TEMPLATE.md`
- [ ] 编写 YAML frontmatter（包含所有配置项及默认值）
- [ ] 为每个配置项编写详细说明章节
  - 字段说明
  - 可选值
  - 使用场景
  - 示例
- [ ] 添加最佳实践章节
  - 快速开发模式
  - 标准开发模式
  - 严格模式

**1.4 编写 .gitignore 规则**

- [ ] 创建 `config/.gitignore`
- [ ] 添加规则：

  ```gitignore
  # 用户个人配置，不提交到版本控制
  user_config.md

  # 备份文件
  *.backup
  *.bak

  # 运行时状态
  .system/
  ```

#### 产出物

- ✅ `config/README.md` - 配置系统说明文档
- ✅ `config/CONFIG_TEMPLATE.md` - 配置模板文件
- ✅ `config/.gitignore` - 排除规则

---

### 阶段 2: 工作流集成（1 天）

#### 任务清单

**2.1 修改 AI_ENTRY_POINT.md**

- [ ] 在现有流程最前面添加"步骤 -1: 读取配置"
- [ ] 描述配置读取流程：
  ```
  1. 检测 config/user_config.md
  2. 读取 config/CONFIG_TEMPLATE.md
  3. 合并配置（优先级: user > default）
  4. 验证配置
  5. 使用 finalConfig 进行后续流程
  ```
- [ ] 添加配置验证逻辑说明

**2.2 修改 core/language_rules.md**

- [ ] 添加配置读取优先级
- [ ] 流程调整：
  ```
  1. 检查 config/user_config.md 中的 documentLanguage
  2. 如果存在，直接使用
  3. 如果不存在，询问用户并创建配置文件
  ```

**2.3 修改 workflows/detection_workflow.md**

- [ ] 集成工具偏好配置
- [ ] 使用 `preferredRoles` 配置
- [ ] 使用 `aiCapabilityTier` 配置

**2.4 修改 workflows/document_health_check.md**

- [ ] 使用 `defaultHealthCheckMode` 配置
- [ ] 支持配置覆盖命令行参数

**2.5 更新 README.md**

- [ ] 在文件结构中添加 `config/` 目录
- [ ] 添加配置系统简介
- [ ] 添加快速配置指南链接

**2.6 更新 CONTRIBUTING.md**

- [ ] 添加 `config/` 目录说明
- [ ] 编写"如何添加新配置项"指南
  - 在 CONFIG_TEMPLATE.md 添加字段
  - 在 README.md 添加说明
  - 更新 configVersion
  - 更新相关工作流

#### 产出物

- ✅ 更新后的 `AI_ENTRY_POINT.md`
- ✅ 更新后的 `core/language_rules.md`
- ✅ 更新后的 `workflows/detection_workflow.md`
- ✅ 更新后的 `workflows/document_health_check.md`
- ✅ 更新后的 `README.md`
- ✅ 更新后的 `CONTRIBUTING.md`

---

### 阶段 3: 向后兼容（0.5 天）

#### 任务清单

**3.1 编写升级指南**

- [ ] 创建 `config/MIGRATION_GUIDE.md`
- [ ] 内容包含：
  - V2.3 到 V3.0 配置迁移步骤
  - 自动迁移机制说明
  - 手动配置调整指南
  - 常见迁移问题

**3.2 实现配置迁移逻辑**

- [ ] 在 `AI_ENTRY_POINT.md` 中添加迁移检测
- [ ] 检测逻辑：
  ```
  1. 检测到旧项目（无 config/ 目录）
  2. 读取 dev_docs/_analysis/generation_plan.md 中的语言配置
  3. 创建 config/ 目录
  4. 创建 user_config.md（从 CONFIG_TEMPLATE.md 复制）
  5. 写入迁移的配置值
  6. 提示用户配置系统已启用
  ```

**3.3 测试 V2.3 项目升级场景**

- [ ] 准备测试用例
  - 无配置的项目
  - 有语言配置的项目
  - 多语言项目
- [ ] 验证迁移逻辑
- [ ] 验证向后兼容性

#### 产出物

- ✅ `config/MIGRATION_GUIDE.md` - 升级指南
- ✅ 迁移逻辑（集成在 `AI_ENTRY_POINT.md`）
- ✅ 测试报告

---

### 阶段 4: V3.0 功能集成（0.5 天）

#### 任务清单

**4.1 为各优化点添加配置项**

- [ ] 013-AI 互审机制: `enableMutualReview`
- [ ] 002-危险指令拦截: `dangerousCommandGuard`
- [ ] 003-设计思维引导: `enforceDesignThinking`
- [ ] 004-ADR 系统: `enableADR`
- [ ] 008-AI 能力分级: `aiCapabilityTier`
- [ ] 001-AI 角色库: `preferredRoles`

**4.2 更新 CONFIG_TEMPLATE.md**

- [ ] 确保所有 V3.0 配置项都有详细说明
- [ ] 添加功能开关的说明链接到对应优化点

**4.3 在各优化点文档中注明配置项**

- [ ] 在每个优化点文档中添加"配置项"章节
- [ ] 说明如何通过配置启用/禁用该功能
- [ ] 提供配置示例

#### 产出物

- ✅ 完整的 V3.0 配置 schema
- ✅ 更新后的各优化点文档

---

### 阶段 5: System Tracker 集成（1 天）

#### 任务清单

**5.1 创建目录结构**

- [ ] 创建 `config/.system/` 目录
- [ ] 确保该目录在 .gitignore 中排除

**5.2 实现命令归一化逻辑**

- [ ] 定义归一化规则：
  - 路径替换为 `<PATH>`
  - 文件名替换为 `<FILE>`
  - 忽略调试标志（-v, --verbose 等）
  - 保留核心参数（-name, -type 等）
- [ ] 实现归一化函数
- [ ] 测试归一化准确性

**5.3 实现计数与推荐逻辑**

- [ ] 创建 `usage_stats.json` 数据结构
- [ ] 实现记录逻辑：
  - 命令执行前归一化
  - 更新计数器
  - 记录时间戳
- [ ] 实现分析逻辑：
  - 会话开始时读取数据
  - 检查阈值（默认 10 次，30 天）
  - 生成推荐
- [ ] 实现触发逻辑：
  - 满足条件时提示用户
  - 用户反馈后更新状态

**5.4 定义初始推荐规则**

- [ ] 高频 `find` 命令 → 推荐 `project_scanner`
- [ ] 高频 `grep` 命令 → 推荐 `content_searcher`
- [ ] 高频文件读取 → 推荐 `file_reader`
- [ ] 添加规则配置化机制

#### 产出物

- ✅ `config/.system/` 目录
- ✅ 命令归一化逻辑
- ✅ System Tracker 运行时系统
- ✅ 初始推荐规则集

---

## ✅ 验收标准

### 功能验收

- [ ] **配置读取**：能从 user_config.md 正确读取并应用配置
- [ ] **配置验证**：YAML 格式错误时能降级到默认配置并警告
- [ ] **配置合并**：user_config 能正确覆盖 CONFIG_TEMPLATE 中的值
- [ ] **首次使用**：无配置时能引导用户创建
- [ ] **迁移兼容**：V2.3 项目能平滑迁移
- [ ] **功能开关**：V3.0 功能能通过配置启用/禁用
- [ ] **System Tracker**：能识别高频操作并推荐工具

### 文档验收

- [ ] `config/README.md` 完整清晰
- [ ] `config/CONFIG_TEMPLATE.md` 包含所有配置项及详细说明
- [ ] `config/MIGRATION_GUIDE.md` 提供清晰的升级指南
- [ ] 所有相关工作流文档已更新

### 测试验收

- [ ] 新项目首次配置流程测试通过
- [ ] V2.3 项目迁移测试通过
- [ ] 配置验证和降级测试通过
- [ ] System Tracker 推荐测试通过

---

## ⚠️ 注意事项

1. **路径确认**：实施时确认 `config/README.md` 中的文档链接路径是否正确
2. **Git 提交**：记得将 `CONFIG_TEMPLATE.md` 和 `README.md` 提交，但排除 `user_config.md`
3. **测试覆盖**：务必测试各种边界情况（配置损坏、缺失字段等）
4. **文档同步**：每个阶段完成后及时更新 `progress.md`

---

## 📊 风险与应对

| 风险                | 影响 | 应对措施                   |
| ------------------- | ---- | -------------------------- |
| YAML 解析失败       | 高   | 实现降级机制，使用默认配置 |
| 迁移逻辑错误        | 中   | 充分测试 V2.3 项目迁移场景 |
| System Tracker 性能 | 低   | 使用异步记录，不阻塞主流程 |
| 用户配置损坏        | 中   | 多层验证+自动修复机制      |

---

**维护者**: AI Coding Context Framework Team  
**相关文档**: [016-unified-config-system.md](./016-unified-config-system.md)
