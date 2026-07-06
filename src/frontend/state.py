"""Streamlit 会话状态管理 —— 类型化的读写封装。

避免在整个应用中散落原始的 st.session_state["key"] 字符串，
提供命名 getter/setter 函数，方便 IDE 自动补全和重构。
"""

import streamlit as st

# ── 会话状态键名常量 ─────────────────────────────────────────

_KEY_SESSION_ID = "codemate_session_id"
_KEY_MESSAGES = "codemate_messages"
_KEY_DOCS_CONTENT = "codemate_docs_content"
_KEY_CURRENT_DOC = "codemate_current_doc"


def init_state() -> None:
    """初始化会话状态默认值（在 app 启动时调用一次）。"""
    defaults = {
        _KEY_SESSION_ID: None,
        _KEY_MESSAGES: [],
        _KEY_DOCS_CONTENT: "",
        _KEY_CURRENT_DOC: None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ── Getters / Setters ─────────────────────────────────────────

def get_session_id() -> str | None:
    """获取当前聊天会话 ID。"""
    return st.session_state[_KEY_SESSION_ID]


def set_session_id(sid: str | None) -> None:
    """设置当前聊天会话 ID。"""
    st.session_state[_KEY_SESSION_ID] = sid


def get_messages() -> list[dict]:
    """获取当前会话的所有消息。"""
    return st.session_state[_KEY_MESSAGES]


def add_message(role: str, content: str) -> None:
    """追加一条消息到当前会话。"""
    st.session_state[_KEY_MESSAGES].append({"role": role, "content": content})


def clear_messages() -> None:
    """清空当前会话的所有消息。"""
    st.session_state[_KEY_MESSAGES] = []


def get_current_doc() -> dict | None:
    """获取当前选中的文档信息。"""
    return st.session_state[_KEY_CURRENT_DOC]


def set_current_doc(doc: dict | None) -> None:
    """设置当前选中的文档。"""
    st.session_state[_KEY_CURRENT_DOC] = doc
