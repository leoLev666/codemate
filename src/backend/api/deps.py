"""依赖注入模块。

为 FastAPI 端点提供共享依赖：Settings 实例、DB 会话。
采用模块级单例缓存，避免每次请求重复创建。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import Settings
from src.backend.db import get_db as _get_db


# ── 缓存单例 ─────────────────────────────────────────────────

_settings: Settings | None = None


def get_settings() -> Settings:
    """返回缓存的 Settings 实例（首次调用时创建）。"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：异步 DB 会话，请求结束时自动提交/回滚。"""
    async for session in _get_db():
        yield session
