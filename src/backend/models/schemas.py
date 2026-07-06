"""Pydantic v2 请求/响应模型。

定义 API 的输入输出格式，自动校验和序列化。
与 SQLAlchemy ORM 模型分离 —— ORM 管数据库，Schema 管 API 契约。
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── 通用模型 ──────────────────────────────────────────────────


class StatusResponse(BaseModel):
    """通用操作状态响应。"""
    status: str
    message: str | None = None


class ErrorResponse(BaseModel):
    """统一错误响应格式。"""
    error: str
    detail: str | None = None


# ── 聊天相关 ──────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """发送消息的请求体。"""
    session_id: str | None = Field(default=None, description="已有会话 ID；为空则自动创建")
    message: str = Field(min_length=1, max_length=10000, description="用户消息文本")
    use_rag: bool = Field(default=True, description="是否检索已索引的文档")
    enable_tools: bool = Field(default=True, description="是否允许 Agent 调用工具")


class SourceChunk(BaseModel):
    """回答中引用的一个检索来源块。"""
    content: str
    source_file: str
    chunk_index: int
    score: float


class ToolCallOut(BaseModel):
    """Agent 工具调用的记录。"""
    name: str
    arguments: dict
    result: str | None = None


class ChatResponse(BaseModel):
    """对话响应。"""
    answer: str
    session_id: str
    sources: list[SourceChunk] | None = None
    tool_steps: list[ToolCallOut] | None = None


class ChatMessageOut(BaseModel):
    """展示用的消息记录。"""
    id: str
    role: Literal["user", "assistant", "tool"]
    content: str
    tool_calls_json: str | None = None
    sources_json: str | None = None
    created_at: datetime


class SessionOut(BaseModel):
    """会话摘要。"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class CreateSessionRequest(BaseModel):
    """创建会话的请求体。"""
    title: str = Field(default="New Chat", min_length=1, max_length=200)


# ── 文档相关 ──────────────────────────────────────────────────


class DocumentOut(BaseModel):
    """文档元数据。"""
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: Literal["indexing", "ready", "error"]
    uploaded_at: datetime


class DocumentUploadResponse(BaseModel):
    """文档上传成功后的响应。"""
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: str


# ── 工具相关 ──────────────────────────────────────────────────


class ToolExecuteRequest(BaseModel):
    """直接执行代码的请求体（绕过 Agent 循环）。"""
    code: str = Field(min_length=1, max_length=5000, description="要在沙箱中执行的 Python 代码")


class ToolExecuteResponse(BaseModel):
    """代码执行结果。"""
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
