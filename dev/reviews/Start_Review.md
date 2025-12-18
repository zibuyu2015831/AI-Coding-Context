# 启动框架审查

本文档是启动AI Coding Context框架审查的入口点，包含AI助手执行审查所需的全部上下文信息和使用指南。

## 📋 审查指令模板

当你被要求对AI Coding Context框架进行审查时，请遵循以下步骤：

### 1. 初始化审查
```bash
# 读取审查入口文档
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/Start_Review.md

# 读取标准指南
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/Framework_Review_Guidelines.md

# 读取问题记录标准
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/Issue_Recording_Standard.md

# 读取进度跟踪标准
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/Progress_Tracking_Standard.md
```

### 2. 确定审查参数
根据用户提供的审查要求，确定以下参数：
- **审查日期**：当前日期，格式为YYYY-MM-DD
- **框架版本**：如V3.0、V3.1等
- **审查范围**：
  - Comprehensive（全面审查）
  - P0（P0任务专项审查）
  - Component（组件专项审查）
  - Security（安全专项审查）
  - Performance（性能专项审查）
  - 自定义范围

### 3. 创建审查目录
```bash
# 创建审查目录（替换YYYY-MM-DD、Version和Scope为实际值）
mkdir -p d:/zibuyu_code/ai_coding_context/dev/reviews/YYYY-MM-DD_Version_Scope
```

### 4. 制定专项审查计划
```bash
# 读取框架审查指南（包含专项审查计划模板）
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/Framework_Review_Guidelines.md

# 基于指南中的模板创建新的专项审查计划
write_to_file d:/zibuyu_code/ai_coding_context/dev/reviews/YYYY-MM-DD_Version_Scope/Review_Plan_Specific.md

# 专项审查计划应包含：
# - 本次审查的基本信息（日期、版本、范围）
# - 基于审查范围确定的特定任务清单
# - 针对特定范围的审查重点和调整
# - 基于标准指南的时间表和交付物
```

### 5. 更新审查索引
```bash
# 更新README.md，添加新的审查条目
read_file d:/zibuyu_code/ai_coding_context/dev/reviews/README.md
# 按照模板在"当前审查状态"部分添加新审查信息
replace_in_file d:/zibuyu_code/ai_coding_context/dev/reviews/README.md
```

## 📊 审查执行流程

### 准备阶段
1. 创建问题跟踪表
2. 创建审查进度跟踪表
3. 创建审查日志
4. 准备审查环境

### 执行阶段
1. 按照`Framework_Review_Guidelines.md`执行各项审查活动
2. 按照`Issue_Recording_Standard.md`记录所有发现的问题
3. 按照`Progress_Tracking_Standard.md`实时更新审查进度
4. 每日更新审查日志

### 报告阶段
1. 生成全面审查报告
2. 进行问题分析和统计
3. 创建改进路线图和复查清单

### 归档阶段
1. 更新审查状态
2. 完成所有交付物
3. 更新README.md的审查历史

## 🚀 快速启动命令

如果你是AI助手，收到审查指令后，可以执行以下快速启动序列：

```python
# 1. 读取上下文
context_docs = [
    "d:/zibuyu_code/ai_coding_context/dev/reviews/Start_Review.md",
    "d:/zibuyu_code/ai_coding_context/dev/reviews/Framework_Review_Guidelines.md",
    "d:/zibuyu_code/ai_coding_context/dev/reviews/Issue_Recording_Standard.md",
    "d:/zibuyu_code/ai_coding_context/dev/reviews/Progress_Tracking_Standard.md"
]

# 2. 确定审查参数
review_date = "当前日期"
version = "用户提供"
scope = "用户提供"

# 3. 创建审查目录和文档
review_dir = f"d:/zibuyu_code/ai_coding_context/dev/reviews/{review_date}_{version}_{scope}"
create_directory(review_dir)

# 4. 开始审查
start_review_process(review_dir, version, scope)
```

## 📝 审查请求示例

当用户提出以下请求时，使用此文档作为入口：

1. "请对V3.1版本进行全面审查"
   - 解析：日期=当前日期，版本=V3.1，范围=Comprehensive
   - 参考：Framework_Review_Guidelines.md中的"全面审查"部分

2. "执行P0任务专项审查"
   - 解析：日期=当前日期，版本=最新版本，范围=P0
   - 参考：Framework_Review_Guidelines.md中的"P0任务专项审查清单"

3. "检查agents/目录的实现质量"
   - 解析：日期=当前日期，版本=最新版本，范围=Component
   - 参考：Framework_Review_Guidelines.md中的"组件审查清单"

4. "评估框架的安全性和性能"
   - 解析：日期=当前日期，版本=最新版本，范围=Security/Performance
   - 参考：Framework_Review_Guidelines.md中的"技术质量与安全性审查清单"

## ⚠️ 重要注意事项

1. **排除dev目录**：审查时应跳过dev/目录下的开发中文件（除审查文档目录）
2. **问题路径记录**：确保所有问题都包含详细的文件路径和相关文档路径
3. **标准遵循**：严格按照Framework_Review_Guidelines.md和Issue_Recording_Standard.md执行
4. **文档更新**：及时更新README.md的审查状态和历史

## 📞 联系与反馈

如果在审查过程中遇到问题或需要澄清，请参考：
- `Framework_Review_Guidelines.md` - 详细审查方法和计划模板
- `Issue_Recording_Standard.md` - 问题记录标准
- `Progress_Tracking_Standard.md` - 进度跟踪标准和模板
- `README.md` - 审查文档结构和交付物标准

---

**文档版本**：1.0  
**创建日期**：2025-12-18  
**创建人**：AI助手  
**状态**：就绪  
**用途**：AI助手启动框架审查的入口点