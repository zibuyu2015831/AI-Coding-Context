---
title: 数据科学项目配置
summary: 定义数据科学项目（Jupyter/机器学习/深度学习）的推荐子文档清单、特殊关注点和核心代码模式。包括数据处理流程、模型文档、实验记录等关键规范。
keywords: data-science | machine-learning | deep-learning | jupyter | pandas | pytorch | tensorflow
scope: 数据科学项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 数据科学项目

> **适用场景**: Jupyter Notebook / 数据分析 / 机器学习 / 深度学习

---

## 🎯 适用框架

### 数据处理
- **Pandas**: 表格数据处理
- **NumPy**: 数值计算
- **Polars**: 高性能数据框架
- **Dask**: 大规模并行计算

### 机器学习
- **Scikit-learn**: 传统机器学习
- **XGBoost**: 梯度提升
- **LightGBM**: 轻量级梯度提升
- **CatBoost**: 类别特征友好

### 深度学习
- **PyTorch**: 灵活的深度学习框架
- **TensorFlow**: 生产级深度学习
- **JAX**: 高性能数值计算
- **Keras**: 高层 API

### 可视化
- **Matplotlib**: 基础绘图
- **Seaborn**: 统计可视化
- **Plotly**: 交互式图表
- **Altair**: 声明式可视化

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `data_pipeline.md` | 数据处理流程 |
| 🔴 高 | `model_documentation.md` | 模型文档 |
| 🟡 中 | `experiments.md` | 实验记录 |
| 🟡 中 | `environment_setup.md` | 环境配置 |
| 🟢 低 | `visualization.md` | 可视化说明 |

---

## 🔍 特殊关注点

### 数据来源与格式

- **CSV**: 常见表格数据
- **Parquet**: 列式存储，高效
- **HDF5**: 大规模数值数据
- **JSON/JSONL**: 半结构化数据
- **SQL**: 数据库查询

### 特征工程说明

- 特征选择方法
- 特征转换（标准化/归一化）
- 特征编码（One-Hot/Label/Target）
- 特征交叉
- 缺失值处理

### 模型参数调优

- **网格搜索**: GridSearchCV
- **随机搜索**: RandomizedSearchCV
- **贝叶斯优化**: Optuna / Hyperopt
- **自动化 ML**: AutoML / TPOT

### 实验结果记录

- **MLflow**: 实验跟踪和模型注册
- **Weights & Biases**: 可视化和协作
- **TensorBoard**: TensorFlow 可视化
- **Neptune.ai**: 元数据管理

### Notebook 组织结构

- 一个 Notebook 一个任务
- 清晰的章节划分
- Markdown 说明充分
- 代码单元格简洁

### 依赖管理

- **conda**: 科学计算环境
- **poetry**: Python 依赖管理
- **pip-tools**: pip 依赖锁定
- **requirements.txt**: 简单依赖列表

### GPU 环境配置

- **CUDA**: NVIDIA GPU 计算
- **cuDNN**: 深度学习加速
- **ROCm**: AMD GPU 支持

### 模型版本管理

- **DVC**: 数据版本控制
- **Git LFS**: 大文件存储
- **MLflow Model Registry**: 模型注册

### 数据版本控制

- **DVC**: 数据和模型版本控制
- **LakeFS**: 数据湖版本控制
- **Pachyderm**: 数据管道版本控制

---

## 💻 核心代码模式

### 数据加载和预处理

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 加载数据
df = pd.read_csv('data/dataset.csv')

# 数据探索
print(df.info())
print(df.describe())
print(df.isnull().sum())

# 特征工程
df['new_feature'] = df['feature1'] * df['feature2']
df = pd.get_dummies(df, columns=['category_col'])

# 分割数据
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 特征缩放
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 机器学习模型训练

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 训练模型
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
model.fit(X_train_scaled, y_train)

# 预测
y_pred = model.predict(X_test_scaled)

# 评估
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.4f}')
print(classification_report(y_test, y_pred))

# 保存模型
joblib.dump(model, 'models/random_forest.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
```

### 超参数调优

```python
from sklearn.model_selection import GridSearchCV
import optuna

# 方法1: GridSearchCV
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X_train_scaled, y_train)
print(f'Best params: {grid_search.best_params_}')

# 方法2: Optuna
def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 200),
        'max_depth': trial.suggest_int('max_depth', 5, 15),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10)
    }
    
    model = RandomForestClassifier(**params, random_state=42)
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    return accuracy_score(y_test, y_pred)

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)
print(f'Best params: {study.best_params}')
```

### PyTorch 深度学习

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# 定义模型
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

# 准备数据
X_train_tensor = torch.FloatTensor(X_train_scaled)
y_train_tensor = torch.LongTensor(y_train.values)
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 初始化模型
model = NeuralNetwork(input_size=X_train.shape[1], hidden_size=64, num_classes=2)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练
num_epochs = 100
for epoch in range(num_epochs):
    for inputs, labels in train_loader:
        # 前向传播
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 保存模型
torch.save(model.state_dict(), 'models/neural_network.pth')
```

### MLflow 实验跟踪

```python
import mlflow
import mlflow.sklearn

# 设置实验
mlflow.set_experiment("my_experiment")

# 记录实验
with mlflow.start_run():
    # 记录参数
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # 训练模型
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train_scaled, y_train)
    
    # 预测和评估
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    # 记录指标
    mlflow.log_metric("accuracy", accuracy)
    
    # 记录模型
    mlflow.sklearn.log_model(model, "model")
    
    # 记录artifacts
    mlflow.log_artifact("data/dataset.csv")
```

### 数据可视化

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 设置样式
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# 特征分布
plt.figure()
df['feature1'].hist(bins=50)
plt.title('Feature 1 Distribution')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.savefig('plots/feature1_dist.png')

# 相关性矩阵
plt.figure()
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Feature Correlation Matrix')
plt.savefig('plots/correlation_matrix.png')

# 特征重要性
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

plt.figure()
sns.barplot(data=feature_importance.head(10), x='importance', y='feature')
plt.title('Top 10 Feature Importance')
plt.savefig('plots/feature_importance.png')
```

---

## ⚠️ 常见问题

### 问题 1: 数据泄漏

**解决方案**: 在分割数据后再进行特征缩放

```python
# ❌ 错误：数据泄漏
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)

# ✅ 正确：先分割再缩放
X_train, X_test, y_train, y_test = train_test_split(X, y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 问题 2: 过拟合

**解决方案**: 使用正则化、交叉验证、早停

```python
from sklearn.model_selection import cross_val_score

# 交叉验证
scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
print(f'CV scores: {scores}')
print(f'Mean CV score: {scores.mean():.4f}')

# 早停（PyTorch）
best_loss = float('inf')
patience = 10
patience_counter = 0

for epoch in range(num_epochs):
    # 训练...
    val_loss = validate(model, val_loader)
    
    if val_loss < best_loss:
        best_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), 'best_model.pth')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print('Early stopping')
            break
```

### 问题 3: 内存不足

**解决方案**: 使用批处理或 Dask

```python
# 使用 Dask 处理大数据
import dask.dataframe as dd

ddf = dd.read_csv('large_dataset.csv')
result = ddf.groupby('category').mean().compute()

# 批处理
chunk_size = 10000
for chunk in pd.read_csv('large_dataset.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

---

## 🎯 检查清单

生成数据科学项目文档前，确认：

- [ ] 已识别数据来源和格式
- [ ] 已确定数据处理框架（Pandas/Polars）
- [ ] 已确定机器学习框架（Scikit-learn/XGBoost）
- [ ] 已确定深度学习框架（PyTorch/TensorFlow）
- [ ] 已确定实验跟踪工具（MLflow/W&B）
- [ ] 已确定可视化工具（Matplotlib/Plotly）
- [ ] 已确定环境管理方式（conda/poetry）
- [ ] 已检查是否需要 GPU 支持
- [ ] 已确定模型版本管理策略
- [ ] 已确定数据版本控制方案（DVC 等）

---

**版本**: v3.0  
**路径**: `core/project_types/data_science.md`  
**最后更新**: 2026-01-21
