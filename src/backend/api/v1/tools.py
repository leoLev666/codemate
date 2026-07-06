"""工具执行 API 端点。

提供直接代码执行接口，绕过 Agent 循环，用于测试和调试沙箱。
"""

from fastapi import APIRouter

from src.backend.api.deps import get_settings
from src.backend.models.schemas import ToolExecuteRequest, ToolExecuteResponse
from src.backend.services.tool_service import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])

_tool_service: ToolService | None = None


def _get_tool_service() -> ToolService:
    global _tool_service
    if _tool_service is None:
        _tool_service = ToolService(get_settings())
    return _tool_service


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_code(req: ToolExecuteRequest):
    """在隔离的 Docker 沙箱中执行 Python 代码。"""
    service = _get_tool_service()
    return await service.execute_code(req.code)
