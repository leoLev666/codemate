"""Agent 执行循环 —— ReAct 模式，含原生 Function Calling。

执行流程：
  1. 将用户消息 + 上下文（RAG 检索结果）发送给 LLM（附带工具定义）。
  2. 如果 LLM 返回文本 → 这就是最终回答。
  3. 如果 LLM 返回 tool_calls → 逐个执行工具，将结果反馈给 LLM，
     回到步骤 1 继续循环。
  4. 重复上述步骤直到获得最终回答或达到 max_steps 上限。

与旧代码的关键区别：
  旧代码用 system prompt 告诉 LLM "请输出 JSON 格式"，
  然后自己 json.loads() 解析。这很脆弱 —— LLM 输出的 JSON
  经常不合规，导致静默 fallback。
  新代码用 DeepSeek 原生 function calling API
  （tools + tool_choice="auto"），API 返回结构化的
  tool_calls 数组，零解析、零 fragile prompt engineering。
"""

import json
from dataclasses import dataclass, field

from src.backend.config import Settings
from src.backend.engine.llm_client import LLMClient
from src.backend.engine.agent.tool_registry import ToolRegistry, ToolResult


@dataclass
class AgentStep:
    """Agent 执行过程中的每一步记录（用于调试和可观测性）。"""

    step_number: int
    tool_name: str | None = None
    tool_arguments: dict | None = None
    tool_result: ToolResult | None = None
    llm_content: str | None = None


@dataclass
class AgentResult:
    """Agent 运行的最终结果。"""

    final_answer: str
    steps: list[AgentStep] = field(default_factory=list)
    total_tokens: int = 0


class AgentExecutor:
    """运行 Agent 循环：LLM ↔ 工具执行，直到得到最终回答。

    用法:
        executor = AgentExecutor(settings, tool_registry)
        result = await executor.run("123 * 456 等于多少？")
        print(result.final_answer)  # "56088"
    """

    def __init__(self, settings: Settings, tool_registry: ToolRegistry):
        self._llm = LLMClient(settings)
        self._tools = tool_registry
        self._max_steps = settings.AGENT_MAX_STEPS

    async def run(
        self,
        user_message: str,
        context: str | None = None,
        chat_history: list[dict] | None = None,
    ) -> AgentResult:
        """执行 Agent 循环。

        Args:
            user_message: 用户输入的原始问题。
            context: 可选的 RAG 检索上下文（文档片段）。
            chat_history: 可选的历史对话消息列表，用于多轮对话。

        Returns:
            AgentResult，包含最终回答、执行步骤轨迹和 token 消耗。
        """
        # 构建初始消息列表（system prompt + 可选上下文 + 用户消息）
        messages: list[dict] = self._build_messages(
            user_message, context, chat_history
        )
        steps: list[AgentStep] = []
        total_tokens = 0

        for step_num in range(self._max_steps):
            # 发送请求（附带工具定义，让 LLM 自行决定是否调用）
            response = self._llm.chat(
                messages=messages,
                tools=self._tools.get_tool_schemas() or None,
            )
            total_tokens += response.usage.total_tokens if response.usage else 0
            choice = response.choices[0]
            msg = choice.message

            # 情况 1：LLM 决定调用工具
            if msg.tool_calls:
                # 将 assistant 消息（含 tool_calls）加入对话历史
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    arguments = json.loads(tc.function.arguments)
                    handler = self._tools.get_handler(tool_name)

                    if handler is None:
                        tool_result = ToolResult(
                            output="", error=f"未知工具: {tool_name}"
                        )
                    else:
                        try:
                            # 执行工具（如 Docker 沙箱中运行 Python 代码）
                            tool_result = await handler(**arguments)
                        except Exception as e:
                            tool_result = ToolResult(
                                output="", error=f"工具执行异常: {e}"
                            )

                    steps.append(
                        AgentStep(
                            step_number=step_num,
                            tool_name=tool_name,
                            tool_arguments=arguments,
                            tool_result=tool_result,
                        )
                    )

                    # 将工具结果反馈给 LLM
                    result_content = tool_result.output or tool_result.error or ""
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_content,
                    })

                # 继续下一轮循环 —— LLM 可能还需要调用更多工具
                continue

            # 情况 2：LLM 给出了最终文本答案
            steps.append(
                AgentStep(step_number=step_num, llm_content=msg.content)
            )
            return AgentResult(
                final_answer=msg.content or "(无响应)",
                steps=steps,
                total_tokens=total_tokens,
            )

        # 超过最大步数仍未得到最终答案
        return AgentResult(
            final_answer="Agent 达到最大步数限制，未获得最终答案。",
            steps=steps,
            total_tokens=total_tokens,
        )

    def _build_messages(
        self,
        user_message: str,
        context: str | None,
        chat_history: list[dict] | None,
    ) -> list[dict]:
        """组装发送给 LLM 的初始消息列表。

        结构：system prompt（含上下文 + 工具说明）→ 历史对话 → 用户消息。
        """
        system_parts = ["你是一个智能助手。"]

        # 如果有 RAG 检索到的文档上下文，注入 system prompt
        if context:
            system_parts.append(
                "请基于以下检索到的文档内容回答用户问题。"
                "如果上下文中没有相关信息，如实说明，用你自己的知识回答。\n\n"
                f"─── 检索到的上下文 ───\n{context}"
            )

        # 如果有可用的工具，告知 LLM
        if self._tools.tool_names:
            system_parts.append(
                "你可以使用工具来辅助回答。当用户的问题需要计算或代码执行时，"
                "请调用相应的工具。对于一般性问题，直接回答即可。"
            )

        messages: list[dict] = [
            {"role": "system", "content": "\n\n".join(system_parts)}
        ]

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": user_message})
        return messages
