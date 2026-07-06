"""聊天组件 —— 消息展示和用户输入处理。"""

import streamlit as st

from src.frontend import api_client
from src.frontend.state import (
    add_message,
    get_messages,
    get_session_id,
    set_session_id,
)


def render() -> None:
    """渲染聊天历史和消息输入框。"""
    # ── 显示历史消息 ─────────────────────────────────────
    for msg in get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── 聊天输入框 ────────────────────────────────────────
    prompt = st.chat_input("问点什么...")
    if not prompt:
        return

    # 显示用户消息
    add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取 AI 回答
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = api_client.send_message(
                    message=prompt,
                    session_id=get_session_id(),
                )

                answer = response.get("answer", "无响应")

                # 显示 RAG 检索来源（如果有）
                sources = response.get("sources")
                if sources:
                    with st.expander(f"📚 参考来源（{len(sources)} 个片段）"):
                        for i, src in enumerate(sources, 1):
                            st.caption(
                                f"**{src.get('source_file', '?')}** "
                                f"（chunk {src.get('chunk_index', '?')}，"
                                f"score: {src.get('score', 0):.2f}）"
                            )
                            st.text(src.get("content", ""))

                # 显示 Agent 工具调用步骤（如果有）
                tool_steps = response.get("tool_steps")
                if tool_steps:
                    with st.expander(f"🔧 工具调用（{len(tool_steps)} 步）"):
                        for ts in tool_steps:
                            st.code(
                                ts.get("arguments", {}).get("code", ""),
                                language="python",
                            )
                            st.caption(f"执行结果: {ts.get('result', '')}")

                st.markdown(answer)
                add_message("assistant", answer)

                # 保存会话 ID 以支持多轮对话
                if response.get("session_id") and not get_session_id():
                    set_session_id(response["session_id"])

            except Exception as e:
                st.error(f"请求失败: {e}")
