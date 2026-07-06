"""API v1 路由聚合 —— 将各模块的端点合并到统一前缀下。"""

from fastapi import APIRouter

from src.backend.api.v1 import chat, documents, health, tools

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(chat.router)
router.include_router(documents.router)
router.include_router(tools.router)
