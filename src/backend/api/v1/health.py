"""健康检查端点。"""

from fastapi import APIRouter

from src.backend.api.deps import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """存活检查 & 就绪检查。

    返回服务基本信息。生产环境中还应检查 DB 连接、ChromaDB 状态、
    DeepSeek API 可达性等。
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "model": settings.DEEPSEEK_MODEL,
    }
