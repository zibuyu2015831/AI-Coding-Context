---
title: AI/LLM 应用项目配置
summary: 定义 AI/LLM 应用项目的推荐子文档清单、特殊关注点和核心代码模式。包括 Prompt 管理、RAG 架构、向量数据库、模型配置、评估指标、成本优化等关键规范。
keywords: ai-llm | rag | prompt-engineering | vector-database | langchain | openai | embeddings | llm
scope: AI/LLM 应用项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# AI/LLM 应用

> **适用场景**: RAG 应用 / Prompt 工程 / AI Agent / 聊天机器人 / 文档问答

---

## 🎯 核心技术栈

### LLM 提供商
- **OpenAI**: GPT-4 / GPT-3.5
- **Anthropic**: Claude 3
- **Google**: Gemini Pro
- **开源模型**: Llama 2/3 / Mistral / Qwen

### 框架与工具
- **LangChain**: Python/JavaScript LLM 框架
- **LlamaIndex**: 数据索引和查询
- **Semantic Kernel**: 微软 LLM 框架
- **Haystack**: NLP 框架

### 向量数据库
- **Pinecone**: 托管向量数据库
- **Weaviate**: 开源向量搜索
- **Qdrant**: Rust 向量数据库
- **Milvus**: 大规模向量搜索
- **Chroma**: 轻量级嵌入数据库
- **pgvector**: PostgreSQL 扩展

### Embedding 模型
- **OpenAI**: text-embedding-ada-002
- **Sentence Transformers**: 开源模型
- **Cohere**: Embed API
- **BGE**: 中文优化模型

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `prompt_management.md` | Prompt 管理 |
| 🔴 高 | `rag_architecture.md` | RAG 架构 |
| 🔴 高 | `vector_database.md` | 向量数据库 |
| 🟡 中 | `model_configuration.md` | 模型配置 |
| 🟡 中 | `evaluation_metrics.md` | 评估指标 |
| 🟡 中 | `cost_optimization.md` | 成本优化 |

---

## 🔍 特殊关注点

### Prompt 管理

- Prompt 模板化
- 版本控制
- A/B 测试
- Few-shot 示例管理

### RAG 架构

- 文档加载和分块
- Embedding 生成
- 向量检索
- 上下文注入
- 答案生成

### 向量数据库

- 索引策略
- 相似度搜索
- 元数据过滤
- 混合搜索（向量+关键词）

### 模型配置

- Temperature / Top-p
- Max tokens
- 停止序列
- 流式输出

### 评估指标

- 准确性（Accuracy）
- 相关性（Relevance）
- 幻觉检测（Hallucination）
- 延迟（Latency）

### 成本优化

- 模型选择（GPT-4 vs GPT-3.5）
- Prompt 长度优化
- 缓存策略
- 批处理

---

## 💻 核心代码模式

### LangChain RAG 基础

```python
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 1. 加载文档
loader = DirectoryLoader('docs/', glob="**/*.md", loader_cls=TextLoader)
documents = loader.load()

# 2. 分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
chunks = text_splitter.split_documents(documents)

# 3. 生成 Embeddings 并存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 4. 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# 5. 创建 Prompt 模板
template = """使用以下上下文来回答问题。如果你不知道答案，就说不知道，不要试图编造答案。

上下文: {context}

问题: {question}

答案:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# 6. 创建 QA 链
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt}
)

# 7. 查询
response = qa_chain.run("什么是 RAG？")
print(response)
```

### Prompt 模板管理

```python
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# 系统提示
system_template = """你是一个专业的技术文档助手。
你的任务是根据提供的文档回答用户的技术问题。

规则:
1. 只基于提供的上下文回答
2. 如果不确定，明确说明
3. 使用专业但易懂的语言
4. 提供代码示例时使用 Markdown 格式

上下文:
{context}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_template)

# 用户提示
human_template = "{question}"
human_prompt = HumanMessagePromptTemplate.from_template(human_template)

# 组合
chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    human_prompt
])

# 使用
messages = chat_prompt.format_messages(
    context=context,
    question="如何使用 LangChain？"
)
```

### 向量数据库操作（Pinecone）

```python
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

# 初始化 Pinecone
pinecone.init(
    api_key="your-api-key",
    environment="us-west1-gcp"
)

# 创建索引
index_name = "my-rag-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embedding 维度
        metric="cosine"
    )

# 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=index_name
)

# 相似度搜索
results = vectorstore.similarity_search(
    "什么是 RAG？",
    k=4
)

# 带分数的搜索
results_with_scores = vectorstore.similarity_search_with_score(
    "什么是 RAG？",
    k=4
)

for doc, score in results_with_scores:
    print(f"Score: {score}")
    print(f"Content: {doc.page_content[:100]}...")
```

### 流式输出

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI

# 创建支持流式输出的 LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# 流式生成
response = llm.predict("写一个关于 AI 的故事")

# 自定义回调
from langchain.callbacks.base import BaseCallbackHandler

class CustomStreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(f"Token: {token}", end="", flush=True)

llm = ChatOpenAI(
    streaming=True,
    callbacks=[CustomStreamHandler()]
)
```

### Agent 实现

```python
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI

# 定义工具
search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="用于搜索互联网信息"
    ),
    Tool(
        name="Calculator",
        func=lambda x: eval(x),
        description="用于数学计算"
    )
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 运行
response = agent.run("2024年世界杯在哪里举办？")
```

### 评估和测试

```python
from langchain.evaluation import load_evaluator
from langchain.evaluation.criteria import LabeledCriteriaEvalChain

# 准确性评估
evaluator = load_evaluator("labeled_criteria", criteria="correctness")

result = evaluator.evaluate_strings(
    prediction="巴黎是法国的首都",
    reference="法国的首都是巴黎",
    input="法国的首都是哪里？"
)
print(result)

# 相关性评估
relevance_evaluator = load_evaluator("criteria", criteria="relevance")

result = relevance_evaluator.evaluate_strings(
    prediction="RAG 是检索增强生成的缩写",
    input="什么是 RAG？"
)
print(result)

# 幻觉检测
from langchain.evaluation import QAEvalChain

qa_eval_chain = QAEvalChain.from_llm(llm)

examples = [
    {
        "query": "什么是 RAG？",
        "answer": "RAG 是检索增强生成",
        "result": "RAG 代表 Retrieval-Augmented Generation"
    }
]

graded_outputs = qa_eval_chain.evaluate(
    examples,
    predictions=[ex["result"] for ex in examples]
)
```

### 成本优化

```python
import tiktoken

# Token 计数
def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Prompt 优化
def optimize_prompt(prompt: str, max_tokens: int = 2000) -> str:
    tokens = count_tokens(prompt)
    if tokens > max_tokens:
        # 截断或总结
        return prompt[:max_tokens * 4]  # 粗略估计
    return prompt

# 缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_call(prompt: str) -> str:
    return llm.predict(prompt)

# 批处理
def batch_process(prompts: list[str]) -> list[str]:
    # 使用批处理 API 降低成本
    return llm.batch(prompts)
```

---

## ⚠️ 常见问题

### 问题 1: 幻觉（Hallucination）

**解决方案**: 使用 RAG 提供上下文，明确指示

```python
template = """严格基于以下上下文回答问题。
如果上下文中没有相关信息，明确说"我不知道"或"上下文中没有相关信息"。
不要编造或推测答案。

上下文: {context}
问题: {question}
答案:"""
```

### 问题 2: 检索质量差

**解决方案**: 优化分块策略和 Embedding 模型

```python
# 使用更好的分块策略
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 减小块大小
    chunk_overlap=50,  # 增加重叠
    separators=["\n\n", "\n", "。", "！", "？", " ", ""]
)

# 使用混合搜索
results = vectorstore.similarity_search(
    query,
    k=10,
    filter={"source": "official_docs"}  # 元数据过滤
)
```

### 问题 3: 成本过高

**解决方案**: 使用更便宜的模型或缓存

```python
# 使用 GPT-3.5 而不是 GPT-4
llm = ChatOpenAI(model="gpt-3.5-turbo")

# 实现缓存
from langchain.cache import InMemoryCache
import langchain
langchain.llm_cache = InMemoryCache()
```

---

## 🎯 检查清单

生成 AI/LLM 应用项目文档前，确认：

- [ ] 已确定 LLM 提供商（OpenAI/Anthropic/开源）
- [ ] 已确定应用类型（RAG/Agent/聊天机器人）
- [ ] 已确定向量数据库（Pinecone/Weaviate/Chroma）
- [ ] 已确定 Embedding 模型
- [ ] 已确定 Prompt 管理策略
- [ ] 已确定评估指标和测试方法
- [ ] 已考虑成本优化策略
- [ ] 已确定数据隐私和安全措施
- [ ] 已确定错误处理和重试机制
- [ ] 已确定监控和日志方案

---

**版本**: v3.0  
**路径**: `core/project_types/ai_llm_app.md`  
**最后更新**: 2026-01-21
