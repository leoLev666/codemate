"""聊天服务 —— 串联 RAG 检索 + Agent 执行 + 消息持久化。

这是业务编排层：不包含具体的 RAG/Agent 实现，
只负责把各个引擎按正确顺序串起来。
"""

import json

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import Settings
from src.backend.engine.agent.executor import AgentExecutor
from src.backend.engine.rag_pipeline import RAGPipeline
from src.backend.models.db import ChatMessage, ChatSession
from src.backend.models.schemas import ChatResponse, SourceChunk, ToolCallOut
from src.backend.engine.retriever import RetrievedChunk


class ChatService:
    """聊天业务编排：RAG → Agent → 持久化。

    Usage:
        service = ChatService(settings)
        response = await service.send_message(db, "你好", session_id, pipeline, executor)
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    async def send_message(
        self,
        db: AsyncSession,
        user_message: str,
        session_id: str | None,
        rag_pipeline: RAGPipeline | None,
        agent_executor: AgentExecutor | None,
        use_rag: bool = True,
        enable_tools: bool = True,
    ) -> ChatResponse:
        """处理单轮对话的完整流程。

        流程：
          1. 获取或创建聊天会话
          2. 保存用户消息到 DB
          3. RAG 检索相关的文档片段（如果启用）
          4. Agent 执行（如果启用工具）或简单 LLM 调用
          5. 保存 AI 回复到 DB
          6. 返回响应（含来源引用和工具调用记录）
        """
        # 1. 会话管理 —— 复用已有或创建新会话
        if session_id:
            session = await db.get(ChatSession, session_id)
            if session is None:
                session = ChatSession(id=session_id)
                db.add(session)
        else:
            session = ChatSession()
            db.add(session)
            await db.flush()

        # 2. 保存用户消息
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_message,
        )
        db.add(user_msg)

        # 首次对话：用第一条消息的前 50 个字符作为会话标题
        if session.title == "New Chat":
            session.title = user_message[:50] + ("..." if len(user_message) > 50 else "")

        await db.flush()

        # 3. RAG 检索 —— 从 ChromaDB 中召回最相关的文档块
        context: str | None = None
        sources: list[SourceChunk] = []
        if use_rag and rag_pipeline is not None:
            chunks = rag_pipeline.retrieve(user_message)
            if chunks:
                context = rag_pipeline.build_context(chunks)
                sources = [
                    SourceChunk(
                        content=c.content[:200],
                        source_file=c.metadata.get("source_file", "unknown"),
                        chunk_index=c.metadata.get("chunk_index", 0),
                        score=c.score,
                    )
                    for c in chunks
                ]

        # 4. Agent 执行（或简单 LLM 生成）
        tool_steps: list[ToolCallOut] = []
        if enable_tools and agent_executor is not None:
            # Agent 路径 —— LLM 可以自主决定调用工具
            result = await agent_executor.run(user_message, context=context)
            answer = result.final_answer
            for step in result.steps:
                if step.tool_name:
                    tool_steps.append(
                        ToolCallOut(
                            name=step.tool_name,
                            arguments=step.tool_arguments or {},
                            result=(
                                step.tool_result.output
                                if step.tool_result
                                else None
                            ),
                        )
                    )
        else:
            # 简单路径 —— 不启用工具，直接调用 LLM（含 RAG 上下文）
            from src.backend.engine.llm_client import LLMClient

            llm = LLMClient(self._settings)
            messages: list[dict] = [
                {"role": "system", "content": "你是一个乐于助人的助手。"},
            ]
            if context:
                messages[0]["content"] += f"\n\n检索到的上下文：\n{context}"
            messages.append({"role": "user", "content": user_message})
            response = llm.chat(messages)
            answer = response.choices[0].message.content or ""

        # 5. 保存 AI 回复到数据库
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            tool_calls_json=json.dumps(
                [tc.model_dump() for tc in tool_steps]
            ) if tool_steps else None,
            sources_json=json.dumps(
                [s.model_dump() for s in sources]
            ) if sources else None,
        )
        db.add(assistant_msg)

        return ChatResponse(
            answer=answer,
            session_id=session.id,
            sources=sources if sources else None,
            tool_steps=tool_steps if tool_steps else None,
        )
