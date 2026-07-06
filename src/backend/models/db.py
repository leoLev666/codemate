"""SQLAlchemy ORM 模型 —— 对话会话、消息和文档索引记录。

使用 SQLAlchemy 2.0 声明式风格，配合 aiosqlite 异步驱动。
未来如需切换到 PostgreSQL，只需修改 DATABASE_URL 和 driver 即可，
repository 层的抽象使得业务代码不受影响。
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    """生成 UUID 字符串作为主键。"""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass


class ChatSession(Base):
    """聊天会话 —— 对应一次完整的对话。"""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(200), default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 一对多关联：一个会话有多条消息，删除会话时级联删除消息
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    """聊天消息 —— 会话中的每一条对话记录。"""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # "user" / "assistant" / "tool"
    content: Mapped[str] = mapped_column(Text)
    # 工具调用和来源信息以 JSON 字符串存储，方便后续解析
    tool_calls_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped[ChatSession] = relationship(back_populates="messages")


class Document(Base):
    """已索引文档的元数据记录。"""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size_bytes: Mapped[int] = mapped_column(BigInteger)
    chunk_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="indexing")  # indexing / ready / error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
