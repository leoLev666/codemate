"""异步 SQLAlchemy 引擎和会话管理。

使用 aiosqlite 驱动，支持 FastAPI 的异步依赖注入。
数据库文件保存在 data/ 目录下，启动时自动创建。
"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.backend.config import Settings

# 模块级缓存，避免重复创建引擎
_engine = None
_session_factory = None


def _get_settings() -> Settings:
    return Settings()


def get_engine():
    """返回（并懒创建）异步 SQLAlchemy 引擎。"""
    global _engine
    if _engine is None:
        settings = _get_settings()
        db_url = settings.DATABASE_URL
        # SQLite 需要确保目录存在
        if db_url.startswith("sqlite"):
            db_path = db_url.replace("sqlite+aiosqlite:///", "")
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        _engine = create_async_engine(db_url, echo=False)
    return _engine


def get_session_factory():
    """返回（并懒创建）异步会话工厂。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：提供异步 DB 会话，自动提交/回滚。

    用法:
        @app.get("/something")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
