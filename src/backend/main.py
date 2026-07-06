"""FastAPI 应用入口。

使用工厂模式（create_app）构建应用，
方便测试时使用不同配置，也兼容 uvicorn 的 --factory 参数。

启动命令:
    uvicorn src.backend.main:create_app --factory --reload
"""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.api.deps import get_settings
from src.backend.api.v1.router import router as v1_router
from src.backend.db import get_engine
from src.backend.models.db import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时：自动创建数据库表（如果不存在）。
    关闭时：释放数据库连接池。
    """
    # 启动
    settings = get_settings()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭
    await engine.dispose()


def create_app() -> FastAPI:
    """构建并返回配置好的 FastAPI 应用。"""
    settings = get_settings()

    app = FastAPI(
        title="Codemate API",
        version="2.0.0",
        description="RAG + Agent 智能助手，基于 DeepSeek、ChromaDB 和 Docker 沙箱",
        lifespan=lifespan,
    )

    # CORS —— 本地开发全开放，生产环境需收紧
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router)

    # ── 全局异常处理：打印完整 traceback 到控制台，方便调试 ──
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"\n{'='*60}")
        print(f"[500 ERROR] {request.method} {request.url.path}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    return app
