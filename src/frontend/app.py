"""Codemate Streamlit 前端入口 —— 纯 UI，零业务逻辑。

所有数据操作通过 api_client 代理到后端 API。
前端只负责展示，后端负责所有计算和存储。
"""

import streamlit as st

from src.frontend.components import chat, sidebar
from src.frontend.state import init_state

# ── 页面配置 ─────────────────────────────────────────────────

st.set_page_config(
    page_title="Codemate — RAG + Agent 助手",
    page_icon="🤖",
    layout="wide",
)

# ── 初始化会话状态 ──────────────────────────────────────────

init_state()

# ── 页面布局 ─────────────────────────────────────────────────

st.title("🤖 Codemate — 智能 RAG + Agent 助手")
st.markdown(
    "上传文档后提问，基于向量检索（ChromaDB）精准定位相关内容；"
    "涉及计算时，Agent 自动在 Docker 沙箱中执行代码。"
)

# 侧边栏（文档上传 + 会话管理）
with st.sidebar:
    sidebar.render()

# 主聊天区
chat.render()
