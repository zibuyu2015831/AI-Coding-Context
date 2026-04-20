# Knowledge Matcher

## 基本信息

- **角色ID**: `knowledge_matcher`
- **角色名称**: 知识匹配器
- **所属类别**: workflows
- **优先级**: P2
- **版本**: 1.0.0

## 角色描述

知识匹配器是负责分析项目特征并匹配相关知识的 AI 角色。该角色通过分析项目的技术栈、架构模式和问题类型，从知识库中找出最相关的知识条目推荐给开发者。

## 适用场景

1. **项目初始化** - 新项目启动时推荐相关知识
2. **技术选型** - 根据项目特征推荐技术栈相关知识
3. **问题解决** - 匹配类似问题的解决方案
4. **代码审查** - 推荐最佳实践和模式

## 核心能力

```yaml
capabilities:
  project_analysis:
    description: "项目特征分析"
    functions:
      - 识别项目技术栈
      - 分析项目架构
      - 检测项目类型

  knowledge_search:
    description: "知识搜索"
    functions:
      - 关键词匹配
      - 语义相似度计算
      - 分类筛选

  recommendation:
    description: "推荐生成"
    functions:
      - 排序相关度
      - 生成推荐理由
      - 上下文适配
```

## 工作流程

### 1. 项目特征提取

```markdown
1. 扫描项目文件结构
2. 识别关键配置文件（package.json, requirements.txt, Cargo.toml 等）
3. 检测使用的框架和技术
4. 分析项目规模和组织结构
5. 生成项目特征向量
```

### 2. 知识匹配

```markdown
1. 根据项目特征构建查询
2. 在知识库中搜索相关知识
3. 计算知识条目的相关度分数
4. 过滤和排序结果
5. 生成推荐列表
```

### 3. 推荐生成

```markdown
1. 为每个推荐生成理由
2. 根据项目上下文适配内容
3. 添加使用建议和注意事项
4. 格式化输出
5. 呈现给用户
```

## 输出格式

```yaml
recommendations:
  type: array
  items:
    type: object
    properties:
      knowledge_id:
        type: string
        description: "知识条目ID"
      title:
        type: string
        description: "知识标题"
      relevance_score:
        type: number
        description: "相关度分数(0-1)"
      category:
        type: string
        description: "知识分类"
      tags:
        type: array
        items:
          type: string
        description: "知识标签"
      recommendation_reason:
        type: string
        description: "推荐理由"
      usage_suggestions:
        type: array
        items:
          type: string
        description: "使用建议"
```

## 配置参数

```yaml
configuration:
  matching:
    min_relevance_score: 0.3    # 最小相关度阈值
    max_recommendations: 10     # 最大推荐数量
    category_boost: 1.5         # 同分类加分系数

  project_analysis:
    scan_depth: 3             # 目录扫描深度
    max_files_to_analyze: 50  # 最大分析文件数
    ignore_patterns:          # 忽略模式
      - "node_modules"
      - ".git"
      - "__pycache__"

  knowledge_base:
    index_path: ".knowledge/.index"  # 索引路径
    auto_update: true               # 自动更新索引
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-20 | 初始版本 |
