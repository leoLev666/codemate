"""后端 API 的 HTTP 客户端封装。

提供类型化的方法封装所有后端端点。
使用 httpx 做 HTTP 请求，Streamlit 的 st.cache_data 做结果缓存。
"""

from typing import Any

import os

import httpx
import streamlit as st

# 后端地址 —— 可通过环境变量 BACKEND_URL 覆盖
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
API_PREFIX = "/api/v1"


def _url(path: str) -> str:
    """拼接完整的 API URL。"""
    return f"{BACKEND_URL}{API_PREFIX}{path}"


def _client() -> httpx.Client:
    """创建 HTTP 客户端（30 秒超时）。"""
    return httpx.Client(timeout=30.0)


# ── 健康检查 ────────────────────────────────────────────────

def health_check() -> dict:
    resp = _client().get(_url("/health"))
    resp.raise_for_status()
    return resp.json()


# ── 聊天 ────────────────────────────────────────────────────

def send_message(
    message: str,
    session_id: str | None = None,
    use_rag: bool = True,
    enable_tools: bool = True,
) -> dict[str, Any]:
    """发送聊天消息，返回 AI 回答。"""
    resp = _client().post(
        _url("/chat/send"),
        json={
            "session_id": session_id,
            "message": message,
            "use_rag": use_rag,
            "enable_tools": enable_tools,
        },
    )
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=5)
def list_sessions() -> list[dict]:
    """列出所有聊天会话（缓存 5 秒）。"""
    resp = _client().get(_url("/chat/sessions"))
    resp.raise_for_status()
    return resp.json()


def create_session(title: str = "New Chat") -> dict:
    """创建新的聊天会话。"""
    resp = _client().post(_url("/chat/sessions"), json={"title": title})
    resp.raise_for_status()
    return resp.json()


def get_history(session_id: str) -> list[dict]:
    """获取会话的消息历史。"""
    resp = _client().get(_url(f"/chat/history/{session_id}"))
    resp.raise_for_status()
    return resp.json()


def delete_session(session_id: str) -> None:
    """删除聊天会话。"""
    resp = _client().delete(_url(f"/chat/history/{session_id}"))
    resp.raise_for_status()


# ── 文档管理 ────────────────────────────────────────────────

def upload_document(file_bytes: bytes, filename: str) -> dict:
    """上传文档进行索引。"""
    resp = _client().post(
        _url("/documents/upload"),
        files={"file": (filename, file_bytes)},
    )
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=10)
def list_documents() -> list[dict]:
    """列出所有已索引文档（缓存 10 秒）。"""
    resp = _client().get(_url("/documents"))
    resp.raise_for_status()
    return resp.json()


def delete_document(doc_id: str) -> None:
    """删除文档及其索引。"""
    resp = _client().delete(_url(f"/documents/{doc_id}"))
    resp.raise_for_status()


# ── 工具 ────────────────────────────────────────────────────

def execute_code(code: str) -> dict:
    """直接在沙箱中执行代码（绕过 Agent）。"""
    resp = _client().post(_url("/tools/execute"), json={"code": code})
    resp.raise_for_status()
    return resp.json()
