"""侧边栏组件 —— 文档上传、会话管理和操作按钮。"""

import streamlit as st

from src.frontend import api_client
from src.frontend.state import (
    clear_messages,
    set_current_doc,
    set_session_id,
)


def render() -> None:
    """渲染侧边栏 UI。"""
    st.header("📄 知识库")

    # ── 文档上传 ─────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "上传文档（PDF, DOCX, PPTX, TXT）",
        type=["txt", "pdf", "docx", "pptx"],
    )
    if uploaded_file is not None:
        with st.spinner("正在解析并索引文档..."):
            try:
                result = api_client.upload_document(
                    uploaded_file.read(), uploaded_file.name
                )
                if "error" in result:
                    st.error(result["error"])
                else:
                    set_current_doc(result)
                    st.success(
                        f"✅ {result['filename']} — {result['chunk_count']} 个块已索引"
                    )
                    api_client.list_documents.clear()  # 清除缓存
            except Exception as e:
                st.error(f"上传失败: {e}")

    # ── 已索引文档列表 ────────────────────────────────────
    st.divider()
    st.subheader("📋 已索引文档")
    try:
        docs = api_client.list_documents()
        if not docs:
            st.caption("暂无文档")
        for doc in docs:
            status_icon = {"ready": "✅", "indexing": "⏳", "error": "❌"}.get(
                doc.get("status", ""), "❓"
            )
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{status_icon} {doc.get('filename', '?')}")
            with col2:
                if st.button("🗑️", key=f"del_{doc['id']}", help="删除此文档"):
                    api_client.delete_document(doc["id"])
                    api_client.list_documents.clear()
                    st.rerun()
    except Exception:
        st.caption("无法连接后端服务")

    # ── 会话管理 ──────────────────────────────────────────
    st.divider()
    st.subheader("💬 历史会话")
    try:
        sessions = api_client.list_sessions()
        for s in sessions[:10]:  # 最多显示最近 10 个会话
            if st.button(
                s.get("title", "Chat")[:30],
                key=f"session_{s['id']}",
                use_container_width=True,
            ):
                set_session_id(s["id"])
                clear_messages()
                # 加载历史消息
                try:
                    history = api_client.get_history(s["id"])
                    for msg in history:
                        from src.frontend.state import add_message
                        add_message(msg["role"], msg["content"])
                except Exception:
                    pass
                st.rerun()
    except Exception:
        st.caption("无法加载会话列表")

    # ── 操作按钮 ──────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 新对话", use_container_width=True):
            try:
                session = api_client.create_session()
                set_session_id(session["id"])
                clear_messages()
                st.rerun()
            except Exception:
                st.error("创建会话失败")
    with col2:
        if st.button("🗑️ 清空", use_container_width=True):
            sid = st.session_state.get("codemate_session_id")
            if sid:
                try:
                    api_client.delete_session(sid)
                except Exception:
                    pass
            set_session_id(None)
            clear_messages()
            st.rerun()
