"""聊天 API 端点。

提供会话管理（创建/列表/删除）和消息发送。
发送消息时会自动串联 RAG 检索 + Agent 执行。
"""

import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_settings
from src.backend.engine.agent.executor import AgentExecutor
from src.backend.engine.agent.tool_registry import ToolRegistry
from src.backend.engine.agent.tools.code_executor import create_code_executor_tool
from src.backend.engine.rag_pipeline import RAGPipeline
from src.backend.models.db import ChatMessage, ChatSession
from src.backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    CreateSessionRequest,
    SessionOut,
)
from src.backend.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# ── 模块级缓存的引擎实例（启动时懒加载，避免每次请求重建） ──

_rag_pipeline: RAGPipeline | None = None
_agent_executor: AgentExecutor | None = None
_chat_service: ChatService | None = None


def _get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(get_settings())
    return _rag_pipeline


def _get_agent_executor() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is None:
        settings = get_settings()
        registry = ToolRegistry()
        registry.register(create_code_executor_tool(settings))
        _agent_executor = AgentExecutor(settings, registry)
    return _agent_executor


def _get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(get_settings())
    return _chat_service


# ── 路由 ──────────────────────────────────────────────────────


@router.post("/send", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """发送消息并获取 AI 回答（含 RAG 检索来源和 Agent 工具调用步骤）。"""
    service = _get_chat_service()
    return await service.send_message(
        db=db,
        user_message=req.message,
        session_id=req.session_id,
        rag_pipeline=_get_rag_pipeline() if req.use_rag else None,
        agent_executor=_get_agent_executor() if req.enable_tools else None,
        use_rag=req.use_rag,
        enable_tools=req.enable_tools,
    )


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """列出所有聊天会话，最近更新的排前面。"""
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        SessionOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.post("/sessions", response_model=SessionOut)
async def create_session(
    req: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """创建新的聊天会话。"""
    session = ChatSession(title=req.title)
    db.add(session)
    await db.flush()
    return SessionOut(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取某个会话的完整消息历史。"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "tool_calls_json": m.tool_calls_json,
            "sources_json": m.sources_json,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.delete("/history/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除聊天会话及其所有消息。"""
    session = await db.get(ChatSession, session_id)
    if session:
        await db.delete(session)
    return {"status": "deleted", "session_id": session_id}
