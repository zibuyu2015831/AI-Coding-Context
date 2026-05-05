---
title: Python 专家角色使用示例
summary: 展示 Python 专家角色在数据处理、FastAPI 异步接口和 Pythonic 重构场景中的典型输出方式。
keywords: example | python-expert | pandas | fastapi | refactor | aicc
scope: Python 专家角色示例
related_files: 无
dependencies: agents/language_specific/python/python_expert.md | agents/examples/README.md
verified_at: 2026-05-05
---

# Python 专家 (Python Expert) 角色使用示例

**角色**: Python 专家
**文档**: [python_expert.md](../language_specific/python/python_expert.md)

---

## 📋 目录

- [示例 1: 使用 Pandas 进行数据清洗](#示例1)
- [示例 2: FastAPI 异步接口与 Pydantic 校验](#示例2)
- [示例 3: Pythonic 的代码重构](#示例3)

---

## <a id="示例1"></a>示例 1: 使用 Pandas 进行数据清洗

### 场景说明

读取 CSV 文件，处理缺失值，进行数据聚合计算，并导出结果。需展示高效的数据处理技巧。

### 用户输入

```text
有一个 sales.csv (date, category, amount)。
请帮我：
1. 读取文件
2. 填充 amount 列的缺失值为 0
3. 增加一列 month
4. 按 month 和 category 分组统计总 amount
5. 保存为 summary.csv
```

### 角色响应

```python
import pandas as pd

def process_sales_data(input_file: str, output_file: str):
    # 1. 读取文件 (指定类型优化内存)
    df = pd.read_csv(input_file, parse_dates=['date'])

    # 2. 填充缺失值 (In-place operation preferred for memory)
    df['amount'] = df['amount'].fillna(0)

    # 3. 增加月份列 (Vectorized string operation)
    df['month'] = df['date'].dt.to_period('M')

    # 4. 分组统计
    summary = df.groupby(['month', 'category'])['amount'].sum().reset_index()

    # 格式化一下输出 (可选)
    summary['amount'] = summary['amount'].round(2)

    # 5. 保存
    summary.to_csv(output_file, index=False)
    print(f"Summary saved to {output_file}")

if __name__ == "__main__":
    process_sales_data('sales.csv', 'summary.csv')
```

### 关键点说明

- ✅ **Pandas**: 使用 Pandas 方法而非 Python 原生循环，速度快几十倍。
- ✅ **Vectorization**: 利用向量化操作（如 `dt.to_period`）处理整列数据。
- ✅ **Type Hinting**: 函数参数添加类型注解。

---

## <a id="示例2"></a>示例 2: FastAPI 异步接口与 Pydantic 校验

### 场景说明

构建一个高性能的异步 API，接收复杂的 JSON 数据，自动校验类型，并进行简单的异步处理。

### 用户输入

```text
写一个 FastAPI 接口 POST /items/：
接收 Item 对象: { name: str, price: float (>0), tags: list[str] }
模拟一个耗时 1秒的异步操作，然后返回结果。
```

### 角色响应

```python
import asyncio
from typing import List, Optional
from fastapi import FastAPI, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

# 1. Pydantic 模型定义 Schema
class Item(BaseModel):
    name: str = Field(..., min_length=1, description="商品名称")
    price: float = Field(..., gt=0, description="价格必须大于0")
    tags: List[str] = []

    # 自定义校验逻辑
    @field_validator('tags')
    def tags_must_be_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Tags must be unique')
        return v

# 2. 异步路由处理
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    # 模拟 IO 操作 (不阻塞 Event Loop)
    await asyncio.sleep(1)

    return {
        "item_name": item.name,
        "price_with_tax": item.price * 1.1,
        "tags_count": len(item.tags)
    }

# 启动命令: uvicorn main:app --reload
```

### 关键点说明

- ✅ **FastAPI + Async**: `async def` 配合 `await`，充分利用 Python 异步特性。
- ✅ **Pydantic**: 声明式定义数据结构和校验规则 (`gt=0`, `field_validator`)。
- ✅ **Field**: 提供元数据（description, min_length），自动生成 OpenAPI 文档。

---

## <a id="示例3"></a>示例 3: Pythonic 的代码重构

### 场景说明

将一段“C 风格”或“Java 风格”的 Python 代码重构为地道的 Python 代码 (Pythonic)。

### 用户输入

```text
优化这段代码：
result = []
for i in range(len(numbers)):
    if numbers[i] % 2 == 0:
        result.append(numbers[i] * 2)

idx = 0
for name in names:
    print(str(idx) + ": " + name)
    idx += 1
```

### 角色响应

```python
# 1. 使用列表推导式 (List Comprehension)
# 替代 过滤+映射 的循环
result = [n * 2 for n in numbers if n % 2 == 0]

# 2. 使用 enumerate
# 替代手动维护索引变量
for idx, name in enumerate(names):
    # 使用 f-string 替代字符串拼接
    print(f"{idx}: {name}")
```

### 关键点说明

- ✅ **List Comprehension**: 简洁、可读性高且通常更快。
- ✅ **enumerate**: Python 处理带索引循环的标准方式。
- ✅ **f-string**: Python 3.6+ 推荐的字符串格式化方式。

---

## 📝 使用建议

1.  **数据科学**: 如果涉及 Excel/CSV/Database 数据处理，优先参考 **示例 1**。
2.  **Web 开发**: FastAPI (示例 2) 是现代 Python Web 开发的首选，比 Flask 更快且自带类型校验。
3.  **日常脚本**: 始终追求 **示例 3** 中的 Pythonic 写法，提升代码质量。
