"""DeepSeek LLM 客户端封装，支持原生 Function Calling。

DeepSeek API 兼容 OpenAI 接口格式，直接使用 OpenAI SDK 调用。
原生支持 tools/tool_choice 参数，无需手工 JSON 解析。
"""

from openai import OpenAI

from src.backend.config import Settings


class LLMClient:
    """DeepSeek（OpenAI 兼容）聊天 API 的薄封装。

    与旧代码的关键区别：
      旧代码用 JSON 字符串解析做工具调用，LLM 输出不合规 JSON 时静默失败。
      新代码用原生 function calling（tools + tool_choice="auto"），
      API 返回结构化的 tool_calls 数组，不需要自己解析。
    """

    def __init__(self, settings: Settings):
        self._client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY.get_secret_value(),
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self._model = settings.DEEPSEEK_MODEL

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
    ):
        """发送聊天补全请求。

        Args:
            messages: 消息列表，每项包含 'role' 和 'content'。
            tools: 可选的 OpenAI 兼容函数定义列表。
            temperature: 采样温度，0 表示确定性的输出。

        Returns:
            OpenAI Completion 对象（含 choices[0].message.tool_calls）。
        """
        kwargs: dict = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"  # 模型自己决定是否调用工具

        return self._client.chat.completions.create(**kwargs)
