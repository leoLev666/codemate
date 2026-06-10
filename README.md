# 🤖 Codemate — 智能 RAG + Tool Agent 助手

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-4B6BFB)](https://platform.deepseek.com/)
[![LangChain](https://img.shields.io/badge/RAG-LangChain-1C3C3C?logo=langchain)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

基于 **DeepSeek 大模型** 的智能助手，集成了 **RAG（检索增强生成）**、**多格式文档解析** 和 **Python 代码自动执行** 能力。提供 Streamlit Web 界面和命令行两种交互方式。

## ✨ 核心功能

| 功能 | 说明 | 使用方式 |
|------|------|----------|
| 📄 **多格式文档 RAG** | 上传 PDF / Word / PPTX / TXT，基于文档内容智能问答 | Web UI & CLI |
| 🐍 **代码自动执行** | AI 自动生成 Python 代码完成计算和数据处理 | Web UI & CLI Agent |
| 🤖 **Tool Agent** | 命令行交互式 Agent，可自主决策调用工具 | `tool_agent.py` |
| 💬 **多轮对话** | Streamlit 聊天界面，支持上下文记忆 | `app.py` |
| 🔧 **CLI 快速问答** | 命令行直接传入文档和问题，秒出结果 | `sample_rag.py` |

## 📁 项目结构

```
codemate_project/
├── app.py              # 🖥️  Streamlit Web 应用（主入口）
├── tool_agent.py       # 🤖  命令行 Tool Agent
├── sample_rag.py       # 📄  命令行 RAG 问答工具
├── rag_demo.py         # 🔗  LangChain RAG 流水线演示
├── hello_deepseek.py   # 👋  DeepSeek API 入门示例
├── sample.txt          # 📝  示例文档（智能家居行业报告）
├── requirements.txt    # 📦  项目依赖
├── .env.example        # 🔑  环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/leoLev666/codemate.git
cd codemate
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> 首次运行时，`sentence-transformers` 会自动下载嵌入模型（约 90MB），请耐心等待。

### 4. 配置 API Key

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env，替换为你的 API Key
# 获取地址：https://platform.deepseek.com/api_keys
```

`.env` 文件内容：
```ini
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 5. 启动应用

```bash
# 🌐 Web 界面（推荐日常使用）
streamlit run app.py
# 浏览器访问 http://localhost:8501

# 📝 命令行文档问答
python sample_rag.py sample.txt "2025年智能家居市场规模是多少？"

# 🤖 交互式 Agent
python tool_agent.py

# 🔗 LangChain RAG 流水线
python rag_demo.py
```

## 🔄 工作流程

```
┌─────────────────────────────────────────────────────┐
│  用户上传文档（PDF / DOCX / PPTX / TXT）              │
│         ↓                                           │
│  多格式文本提取（PyPDF / docx / pptx）                │
│         ↓                                           │
│  RAG 模式：文本切片 → 向量嵌入 → 存入 ChromaDB        │
│         ↓                                           │
│  用户提问 → DeepSeek 判断问题类型                     │
│    ├── 文档相关 → 检索相关片段 → 基于文档回答          │
│    ├── 需要计算 → 生成代码 → 沙箱执行 → 返回结果       │
│    └── 通用知识 → 直接回答                            │
└─────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 大模型 | [DeepSeek Chat API](https://platform.deepseek.com/) | 通过 OpenAI 兼容接口调用 |
| Web UI | [Streamlit](https://streamlit.io/) | 纯 Python，无需前端知识 |
| RAG 框架 | [LangChain](https://www.langchain.com/) | 文档加载、文本切片、检索链 |
| 向量数据库 | [ChromaDB](https://www.trychroma.com/) | 轻量级本地向量存储 |
| 嵌入模型 | [sentence-transformers](https://www.sbert.net/) | `all-MiniLM-L6-v2`（384 维） |
| 文档解析 | PyPDF / python-docx / python-pptx | 多格式文本提取 |

## 📖 使用示例

### Web UI 文档问答

```bash
streamlit run app.py
```

1. 打开浏览器访问 `http://localhost:8501`
2. 左侧边栏上传文档（PDF/Word/PPT/TXT）
3. 在对话框中输入问题
4. AI 基于文档内容作答

### 命令行快速问答

```bash
# 指定文档和问题
python sample_rag.py report.pdf "总结一下这份报告的要点"

# 只指定文档，交互式提问
python sample_rag.py sample.txt
```

### 交互式 Agent

```bash
python tool_agent.py
# 你: 计算 123 * 456
# Agent: [执行] print(123 * 456)
# Agent: 56088
# 你: exit  (退出)
```

## ⚠️ 安全须知

- 🔐 `.env` 文件已被 `.gitignore` 排除，**切勿将 API Key 提交到 Git**
- 🧹 如曾误提交密钥，请立即到 [DeepSeek 平台](https://platform.deepseek.com/api_keys) 重置
- 🛡️ 代码执行功能已禁用 `eval`、`exec`、`__import__`、`open` 等危险关键字
- ⏱️ 每次代码执行设有 5 秒超时限制

## 📝 License

MIT
