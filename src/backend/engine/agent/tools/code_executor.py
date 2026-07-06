"""execute_python 工具 —— 在 Docker 沙箱中执行 Python 代码。

这是 Agent 可调用的核心工具。当用户需要数学计算或数据处理时，
LLM 通过 function calling 调用此工具，代码在隔离容器中运行。
"""

import json

from src.backend.config import Settings
from src.backend.engine.agent.sandbox.docker_sandbox import DockerSandbox
from src.backend.engine.agent.tool_registry import ToolDefinition, ToolResult

# 函数参数的 JSON Schema（OpenAI function calling 格式）
# LLM 根据此 Schema 生成符合格式的 arguments
EXECUTE_PYTHON_SCHEMA = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "要执行的 Python 代码。使用 print() 输出结果。",
        }
    },
    "required": ["code"],
}


def create_code_executor_tool(settings: Settings) -> ToolDefinition:
    """工厂函数：创建 execute_python 工具定义。

    返回的 ToolDefinition 可直接注册到 ToolRegistry 中。

    Args:
        settings: 应用配置（沙箱镜像名、超时等）。

    Returns:
        配置好的 ToolDefinition，含 Docker 沙箱处理函数。
    """
    sandbox = DockerSandbox(settings)

    async def handler(code: str) -> ToolResult:
        """在隔离沙箱中执行 Python 代码。"""
        return await sandbox.execute(code)

    return ToolDefinition(
        name="execute_python",
        description=(
            "执行 Python 代码进行数学计算或数据处理。"
            "用 print() 函数输出结果。"
            "代码运行在隔离沙箱中，无网络和文件系统访问权限。"
        ),
        parameters=EXECUTE_PYTHON_SCHEMA,
        handler=handler,
        require_sandbox=True,
    )
