"""工具服务 —— 直接代码执行（绕过 Agent 循环）。"""

from src.backend.config import Settings
from src.backend.engine.agent.sandbox.docker_sandbox import DockerSandbox
from src.backend.models.schemas import ToolExecuteResponse


class ToolService:
    """处理直接工具调用（不经过 Agent 决策）。"""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def execute_code(self, code: str) -> ToolExecuteResponse:
        """在 Docker 沙箱中直接执行代码。

        这是绕过 Agent 的快捷路径，适合测试沙箱功能。
        Agent 正常路径走 AgentExecutor → ToolRegistry → DockerSandbox。
        """
        sandbox = DockerSandbox(self._settings)
        result = await sandbox.execute(code)
        return ToolExecuteResponse(
            stdout=result.output,
            stderr=result.error or "",
            exit_code=0 if not result.error else 1,
            timed_out="timed out" in (result.error or "").lower() or "超时" in (result.error or ""),
        )
