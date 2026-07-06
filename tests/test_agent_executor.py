"""Agent 执行器和工具注册表测试。"""

from src.backend.config import Settings
from src.backend.engine.agent.tool_registry import ToolRegistry, ToolDefinition, ToolResult


def test_tool_registry_register_and_lookup():
    """工具注册后应能通过名称查找到。"""
    registry = ToolRegistry()

    async def dummy_handler(x: int) -> ToolResult:
        return ToolResult(output=str(x * 2))

    registry.register(
        ToolDefinition(
            name="double",
            description="将数字翻倍",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            },
            handler=dummy_handler,
        )
    )

    assert "double" in registry.tool_names
    assert registry.get_handler("double") is not None
    assert registry.get_handler("nonexistent") is None, "未注册的工具应返回 None"


def test_tool_registry_schemas():
    """生成的 JSON Schema 应符合 OpenAI function calling 格式。"""
    registry = ToolRegistry()

    async def noop(**kwargs) -> ToolResult:
        return ToolResult(output="ok")

    registry.register(
        ToolDefinition(
            name="test_tool",
            description="一个测试工具",
            parameters={"type": "object", "properties": {}},
            handler=noop,
        )
    )

    schemas = registry.get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function", "最外层 type 应为 'function'"
    assert schemas[0]["function"]["name"] == "test_tool", "function name 应与注册名一致"
