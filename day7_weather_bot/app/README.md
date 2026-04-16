# AI Weather Assistant 🌤️

一个基于 FastAPI 和 LLM 的智能天气助手，具备 RAG 检索增强和决策能力。

## 🚀 功能特性
- **实时天气查询**：连接 SQLite 数据库获取精准气象数据。
- **RAG 知识增强**：利用 ChromaDB 检索本地知识库（景点、交通、习俗）。
- **智能决策**：根据温度自动切换“舒适模式”、“预警模式”或“通用模式”。
- **鲁棒性设计**：支持处理未知城市（如“上海”）甚至虚构城市（如“哥谭”）的查询。

## 🛠️ 技术栈
- **Backend**: Python, FastAPI
- **AI**: Alibaba Cloud Qwen (via OpenAI SDK)
- **Database**: SQLite (结构化数据), ChromaDB (向量数据库)
- **Tools**: Pydantic, python-dotenv

## 📦 快速开始

1. 安装依赖：
   ```bash
   pip install fastapi uvicorn openai chromadb sentence-transformers python-dotenv
2. 配置环境变量：
   DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
3. 初始化数据库：
   运行 init_db.py 和 init_chroma.py 加载初始数据。
4. 启动服务：
   uvicorn app.main:app --reload

## 项目结构
**main.py**: API 入口与路由
**data_service.py**: 数据库操作
**llm_service.py**: AI 逻辑与 Prompt 工程
**chroma_db/**: 向量数据库存储目录