"""集中配置管理 —— 基于 pydantic-settings。

所有配置项从环境变量或 .env 文件加载。
启动时自动校验，配错立刻报错，不会带着错误配置"带病运行"。

特色：
  - extra="forbid" → 未知环境变量会报错，防止拼写错误。
  - SecretStr → API Key 不会出现在日志或 traceback 中。
  - Field(ge=, le=) → 数值范围校验。
  - @validator → 自定义校验逻辑。
"""

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，所有字段从环境变量自动加载。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",  # 禁止未定义的环境变量 —— 防止拼写错误
    )

    # ── DeepSeek API ──────────────────────────────────────────
    DEEPSEEK_API_KEY: SecretStr = Field(
        description="DeepSeek API 密钥，从 https://platform.deepseek.com/api_keys 获取",
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API 地址（OpenAI 兼容接口）",
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat",
        description="聊天补全使用的模型名称",
    )

    # ── 数据库 ──────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/codemate.db",
        description="SQLAlchemy 异步数据库连接 URL",
    )

    # ── ChromaDB（向量存储） ───────────────────────────────
    CHROMA_PERSIST_DIR: str = Field(
        default="./data/chroma",
        description="ChromaDB 持久化存储目录",
    )

    # ── 嵌入模型 ───────────────────────────────────────────
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace sentence-transformers 模型名称",
    )
    HF_ENDPOINT: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace 镜像地址（国内加速下载）",
    )

    # ── 文本分块 ───────────────────────────────────────────
    CHUNK_SIZE: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="每个文本块的目标字符数",
    )
    CHUNK_OVERLAP: int = Field(
        default=50,
        ge=0,
        le=500,
        description="相邻文本块之间的重叠字符数",
    )

    # ── 检索参数 ───────────────────────────────────────────
    RETRIEVAL_TOP_K: int = Field(
        default=4,
        ge=1,
        le=20,
        description="每次查询检索的块数量",
    )
    HYBRID_SEARCH_ENABLED: bool = Field(
        default=False,
        description="是否启用 BM25 + 向量的混合检索（实验性功能）",
    )
    RERANKER_ENABLED: bool = Field(
        default=False,
        description="是否启用 CrossEncoder 对检索结果重排序",
    )
    RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="重排序用的 CrossEncoder 模型",
    )

    # ── Docker 沙箱 ────────────────────────────────────────
    DOCKER_SANDBOX_IMAGE: str = Field(
        default="codemate-sandbox",
        description="代码执行沙箱的 Docker 镜像名",
    )
    SANDBOX_TIMEOUT: int = Field(
        default=10,
        ge=1,
        le=60,
        description="沙箱代码执行的最大秒数",
    )
    SANDBOX_MEMORY_LIMIT: str = Field(
        default="128m",
        description="沙箱容器的内存限制",
    )

    # ── Agent ───────────────────────────────────────────────
    AGENT_MAX_STEPS: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Agent 单次调用的最大工具执行步数",
    )

    # ── 服务器 ─────────────────────────────────────────────
    HOST: str = Field(default="0.0.0.0", description="服务监听地址")
    PORT: int = Field(default=8000, ge=1, le=65535, description="服务监听端口")
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别（DEBUG / INFO / WARNING / ERROR）",
    )

    @validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """校验日志级别是否为有效值。"""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL 必须是 {allowed} 之一，实际值: '{v}'")
        return upper
