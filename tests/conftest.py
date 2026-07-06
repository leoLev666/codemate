"""pytest 共享 fixtures。"""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.backend.config import Settings
from src.backend.models.db import Base


@pytest.fixture
def settings() -> Settings:
    """从 .env 加载配置（或使用默认值）。"""
    return Settings()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """内存 SQLite 数据库，每次测试自动创建和销毁。"""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()
