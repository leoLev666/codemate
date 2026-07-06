"""工具注册表 —— Agent 可调用工具的注册与查询中心。

每个工具用 ToolDefinition 描述：名称、功能说明、参数 JSON Schema、
处理函数。ToolRegistry 负责管理所有已注册工具，并提供
OpenAI 兼容的 function definitions 供 LLM 使用。
"""

from dataclasses import dataclass, field
from collections.abc import Awaitable
from typing import Any, Callable


@dataclass
class ToolResult:
    """工具执行结果。"""

    output: str
    error: str | None = None


@dataclass
class ToolDefinition:
    """描述 Agent 可以调用的一个工具。

    Attributes:
        name: 唯一工具名（如 'execute_python'）。
        description: 给 LLM 看的功能说明，影响模型何时调用该工具。
        parameters: 函数参数的 JSON Schema（OpenAI 格式）。
        handler: 异步/同步可调用对象，接收关键字参数，返回 ToolResult。
        require_sandbox: 是否需要在隔离环境中执行（安全敏感操作）。
    """

    name: str
    description: str
    parameters: dict
    handler: Callable[..., Awaitable[ToolResult]] | Callable[..., ToolResult]
    require_sandbox: bool = False


class ToolRegistry:
    """工具注册表。

    用法:
        registry = ToolRegistry()
        registry.register(ToolDefinition(...))
        schemas = registry.get_tool_schemas()   # 传给 LLM
        handler = registry.get_handler("xxx")    # 收到 tool_calls 后执行
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """注册一个工具。"""
        self._tools[tool.name] = tool

    def get_tool_schemas(self) -> list[dict]:
        """生成 OpenAI 兼容的 function definitions 列表。

        这个列表直接传给 LLM 的 tools 参数，
        LLM 据此决定是否调用以及调用哪个工具。
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def get_handler(self, name: str):
        """按名称查找工具的处理函数，未找到返回 None。"""
        td = self._tools.get(name)
        return td.handler if td else None

    @property
    def tool_names(self) -> list[str]:
        """所有已注册工具的名称列表。"""
        return list(self._tools.keys())
