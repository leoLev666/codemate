# 🤖 Codemate — 智能 RAG + Agent 助手

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-4B6BFB)](https://platform.deepseek.com/)
[![ChromaDB](https://img.shields.io/badge/Vector-DB-FFD700?logo=database)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Sandbox-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

基于 **DeepSeek 大模型** 的智能助手，采用 **标准前后端分离架构**。核心亮点：真正的 RAG 向量检索引擎、原生 Function Calling Agent、Docker 容器沙箱代码执行。

## 🏗️ 系统架构

```
浏览器                     Streamlit 前端              FastAPI 后端
┌──────────┐    HTTP      ┌──────────────┐    HTTP    ┌──────────────────────────┐
│  用户界面  │ ◄──────────► │ 纯 UI（无业务 │ ◄────────► │ /api/v1/chat             │
│           │             │ 逻辑）        │           │ /api/v1/documents        │
└──────────┘             └──────────────┘           │ /api/v1/tools            │
                                                     │                          │
                                                     │  ┌─────────────────────┐ │
                                                     │  │ RAG 引擎             │ │
                                                     │  │ 解析→分块→嵌入→检索   │ │
                                                     │  │ ChromaDB 向量数据库   │ │
                                                     │  └─────────────────────┘ │
                                                     │  ┌─────────────────────┐ │
                                                     │  │ Agent 引擎           │ │
                                                     │  │ Function Calling     │ │
                                                     │  │ Docker 沙箱执行       │ │
                                                     │  └─────────────────────┘ │
                                                     │  ┌─────────────────────┐ │
                                                     │  │ SQLite (aiosqlite)   │ │
                                                     │  │ 会话 & 文档元数据     │ │
                                                     │  └─────────────────────┘ │
                                                     └──────────────────────────┘
```

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📄 **RAG 文档检索** | 真正的向量检索（非全文塞入 prompt），支持 PDF / DOCX / PPTX / TXT |
| 🔍 **混合检索** | 向量语义检索 + 可选 BM25 关键词检索 + CrossEncoder 重排序 |
| 🤖 **Agent 工具调用** | 原生 Function Calling（非 JSON 字符串解析），模型自主决策调用工具 |
| 🐳 **Docker 沙箱** | 代码执行在隔离容器中运行：network_mode=none, read_only, cap_drop=ALL |
| 💬 **多轮对话** | 会话管理、历史记录持久化、来源标注 |

## 🔬 RAG 流水线详解

这是面试中最有可能被深挖的部分，RAG 分为两条链路：

### 写入链路（文档上传时，离线执行）

```
PDF/DOCX/PPTX/TXT
    │
    ▼
① 文本解析（Parser）── 策略模式，每个格式独立的解析器
    │
    ▼
② 分块（RecursiveCharacterTextSplitter）
   chunk_size=500, chunk_overlap=50
    │
    ▼
③ 向量嵌入（all-MiniLM-L6-v2 → 384 维）
    │
    ▼
④ 存入 ChromaDB（持久化到磁盘）
```

### 查询链路（用户提问时，在线执行）

```
用户问题
    │
    ▼
① 问题向量化（同一 embedding 模型）
    │
    ▼
② 向量检索（余弦相似度，top_k=4）
    │
    ▼
③ [可选] 重排序（CrossEncoder 精细打分）
    │
    ▼
④ 构建 Prompt → LLM 生成答案（附来源引用）
```

**设计权衡：**
- chunk_size=500：平衡语义完整性和检索精度
- chunk_overlap=50：防止关键信息落在块边界
- top_k=4：太多引入噪音，太少遗漏上下文
- MiniLM-L6-v2：本地运行，零延迟零费用，384 维在速度与质量间平衡

## 📁 项目结构

```
codemate_project/
├── src/
│   ├── backend/                       # FastAPI 后端
│   │   ├── main.py                    #   应用入口（工厂模式）
│   │   ├── config.py                  #   pydantic-settings 集中配置
│   │   ├── db.py                      #   异步 SQLAlchemy + aiosqlite
│   │   ├── api/v1/                    #   API 路由（薄层，不写业务逻辑）
│   │   │   ├── chat.py                #     对话接口
│   │   │   ├── documents.py           #     文档上传/列表/删除
│   │   │   ├── tools.py               #     工具调用接口
│   │   │   └── health.py              #     健康检查
│   │   ├── services/                  #   业务编排层
│   │   │   ├── chat_service.py        #     对话编排（RAG + Agent 串联）
│   │   │   ├── document_service.py    #     上传→解析→索引 工作流
│   │   │   └── tool_service.py        #     沙箱执行服务
│   │   ├── models/                    #   数据模型
│   │   │   ├── db.py                  #     SQLAlchemy ORM 表
│   │   │   └── schemas.py             #     Pydantic 请求/响应 模型
│   │   │
│   │   └── engine/                    #   ★ 核心引擎 — 面试重点 ★
│   │       ├── parser/                #     文档解析（策略模式）
│   │       │   ├── base.py            #       抽象基类
│   │       │   ├── pdf_parser.py      #       PDF 解析器
│   │       │   ├── docx_parser.py     #       DOCX 解析器
│   │       │   ├── pptx_parser.py     #       PPTX 解析器
│   │       │   ├── txt_parser.py      #       TXT 解析器
│   │       │   └── registry.py        #       按扩展名自动分发
│   │       ├── chunker.py             #     文本分块
│   │       ├── embedder.py            #     向量嵌入（单例懒加载）
│   │       ├── retriever.py           #     ChromaDB 向量检索
│   │       ├── reranker.py            #     CrossEncoder 重排序
│   │       ├── rag_pipeline.py        #     RAG 流水线编排
│   │       ├── llm_client.py          #     DeepSeek API 封装
│   │       └── agent/                 #     Agent 引擎
│   │           ├── executor.py        #       Agent 循环（ReAct 模式）
│   │           ├── tool_registry.py   #       工具注册表
│   │           ├── tools/             #       工具实现
│   │           │   └── code_executor.py
│   │           └── sandbox/           #       执行沙箱
│   │               └── docker_sandbox.py
│   │
│   ├── frontend/                      # Streamlit 前端（纯 UI）
│   │   ├── app.py                     #   应用入口
│   │   ├── api_client.py              #   后端 API 调用封装
│   │   ├── state.py                   #   会话状态管理
│   │   └── components/                #   UI 组件
│   │       ├── chat.py                #     聊天界面
│   │       └── sidebar.py             #     侧边栏（文档上传 & 会话管理）
│   │
│   └── shared/
│       └── constants.py               # 前后端共享常量
│
├── docker/                            # Docker 容器配置
│   ├── sandbox.Dockerfile             #   代码执行沙箱镜像
│   ├── backend.Dockerfile             #   后端服务镜像
│   ├── frontend.Dockerfile            #   前端服务镜像
│   └── docker-compose.yml             #   一键编排
│
├── scripts/                           # 历史实验脚本（集中存放）
│   ├── hello_deepseek.py
│   └── rag_demo.py
│
├── tests/                             # 测试（重点覆盖 engine）
│   ├── test_parser.py
│   ├── test_rag_pipeline.py
│   └── test_agent_executor.py
│
├── data/                              # 运行时数据（gitignore）
│   ├── chroma/                        #   ChromaDB 持久化文件
│   └── codemate.db                    #   SQLite 数据库
│
├── start_backend.bat / .sh            # 后端启动脚本
├── start_frontend.bat / .sh           # 前端启动脚本
├── pyproject.toml                     # 项目配置 & 依赖
├── sample.txt                         # 示例文档
├── .env.example                       # 环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/leoLev666/codemate.git
cd codemate

# 创建虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# 安装依赖
pip install -e .
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 DeepSeek API Key
# 获取地址：https://platform.deepseek.com/api_keys
```

`.env` 关键配置项：

```ini
DEEPSEEK_API_KEY=sk-your-api-key-here   # 必填
HF_ENDPOINT=https://hf-mirror.com       # 国内用户建议使用镜像
```

### 3. 构建 Docker 沙箱（可选，代码执行功能需要）

```bash
docker build -t codemate-sandbox -f docker/sandbox.Dockerfile .
```

### 4. 启动服务

```bash
# 终端 1：启动后端（端口 8001）
# Windows
start_backend.bat
# Linux/macOS
./start_backend.sh

# 终端 2：启动前端（端口 8501）
# Windows
start_frontend.bat
# Linux/macOS
./start_frontend.sh
```

浏览器打开 `http://localhost:8501`，上传文档并开始对话。

API 文档自动生成：`http://localhost:8001/docs`

### 5. 使用 Docker Compose 一键启动

```bash
docker compose -f docker/docker-compose.yml up -d
```

## 🛠️ 技术栈

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| LLM | DeepSeek Chat API | OpenAI 兼容接口，性价比高 |
| 后端框架 | FastAPI | 自动 API 文档、类型安全、异步支持 |
| 前端 | Streamlit | 纯 Python，快速迭代 |
| RAG 框架 | LangChain | 文档处理、向量检索、Prompt 编排 |
| 向量数据库 | ChromaDB | 轻量本地部署，零运维 |
| 嵌入模型 | all-MiniLM-L6-v2 | 本地运行，384 维，速度与质量平衡 |
| 数据库 | SQLite + aiosqlite | 单文件零配置，异步支持 |
| 沙箱 | Docker | 真正隔离，非字符串黑名单 |
| 配置管理 | pydantic-settings | 启动校验，SecretStr 防泄露 |
| 文档解析 | pypdf / python-docx / python-pptx | 多格式覆盖 |

## 🎯 面试亮点

这个项目展示了以下工程能力，面试时可以展开讲：

1. **"我的 RAG 是真正的向量检索，不是把全文塞进 prompt"**
   - 解析→分块→嵌入→检索→可选重排序 五级流水线
   - chunk_size/overlap 的含义和调参经验
   - 为什么选 MiniLM，不是 OpenAI Embedding

2. **"Agent 工具调用是原生 Function Calling，不是 JSON 字符串解析"**
   - `tools` + `tool_choice="auto"` 结构化响应
   - 不会有 JSON 格式错误的坑

3. **"代码执行是 Docker 容器隔离，不是 subprocess 黑名单"**
   - network_mode=none, read_only, cap_drop=ALL
   - 内存限制、超时控制、执行完自动销毁

4. **"文档解析用了策略模式，加新格式只需加一个类"**
   - 抽象基类 + registry 自动分发
   - 开闭原则：对扩展开放，对修改关闭

5. **"前后端分离，API 是契约"**
   - FastAPI + Streamlit，前端随时可换
   - 所有业务逻辑在后端，前端只做渲染

6. **"配置管理用 pydantic-settings，启动时校验"**
   - 配错立即报错，不会带病运行
   - SecretStr 防止 API Key 泄露到日志

## 📖 使用示例

### Web UI

1. 上传文档（侧边栏拖拽或选择文件）
2. 新建会话，输入问题
3. 查看 AI 回答及来源引用

### API 直接调用

```bash
# 上传文档
curl -X POST http://localhost:8001/api/v1/documents/upload \
  -F "file=@sample.txt"

# 创建会话并对话
curl -X POST http://localhost:8001/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message":"智能家居市场规模是多少？","session_id":"<从 sessions 获取>","use_rag":true,"enable_tools":false}'
```

## ⚠️ 安全须知

- 🔐 `.env` 已被 `.gitignore` 排除，**切勿将 API Key 提交到 Git**
- 🧹 如曾误提交密钥，请立即到 [DeepSeek 平台](https://platform.deepseek.com/api_keys) 重置
- 🐳 代码执行默认需要 Docker 沙箱镜像，不启用沙箱则不会执行代码

## 📝 License

MIT
