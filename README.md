# 🤖 Codemate — 智能 RAG 助手

基于 DeepSeek 大模型的 RAG（检索增强生成）智能助手，支持多格式文档问答、Python 代码执行和 Tool Agent。

## ✨ 功能

- **📄 多格式文档 RAG** — 上传 PDF / Word / PPTX / TXT，基于文档内容智能问答
- **🐍 Python 代码执行** — 自动识别并执行 Python 代码完成计算任务
- **🤖 Tool Agent** — 命令行交互式 Agent，支持工具调用
- **💬 Streamlit Web UI** — 美观的聊天界面
- **🔧 CLI 工具** — 命令行版本的 RAG 问答和向量检索

## 📁 项目结构

```
codemate_project/
├── app.py              # Streamlit Web 应用（主要入口）
├── tool_agent.py       # 命令行 Tool Agent
├── sample_rag.py       # 命令行 RAG 问答工具
├── rag_demo.py         # LangChain RAG 流水线演示
├── hello_deepseek.py   # DeepSeek API 基础调用示例
├── sample.txt          # 示例文档（智能家居报告）
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone <your-repo-url>
cd codemate_project

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 DeepSeek API Key
# 获取地址：https://platform.deepseek.com/api_keys
```

### 3. 运行

```bash
# 启动 Web 界面（推荐）
streamlit run app.py

# 或使用命令行工具
python sample_rag.py sample.txt "2025年智能家居市场规模是多少？"
python hello_deepseek.py
python tool_agent.py
```

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 大模型 | DeepSeek Chat API |
| Web UI | Streamlit |
| RAG 框架 | LangChain |
| 向量数据库 | ChromaDB |
| 嵌入模型 | sentence-transformers/all-MiniLM-L6-v2 |
| 文档解析 | PyPDF / python-docx / python-pptx |

## ⚠️ 安全提示

- **切勿** 将 `.env` 文件或 API Key 提交到 Git
- 本项目使用 `.gitignore` 排除了 `.env`
- 请参考 `.env.example` 创建自己的 `.env` 文件
- 如果你曾在 git 历史中提交过 API Key，请立即到 DeepSeek 平台重置密钥

## 📝 License

MIT
