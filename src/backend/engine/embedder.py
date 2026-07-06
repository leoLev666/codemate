"""文本嵌入模块。

使用 sentence-transformers 将文本块编码为向量。
模型以单例模式常驻内存，避免每次请求重复加载（~90MB 模型加载耗时数秒）。

关键：必须在 import sentence-transformers 之前设置 HF_ENDPOINT，
否则 huggingface_hub 会直连 huggingface.co（国内可能不可达）。
"""

import os

from src.backend.config import Settings

# 全局缓存的嵌入模型实例，None 表示尚未加载
_embedder = None  # type: HuggingFaceEmbeddings | None


def get_embedder(settings: Settings):
    """获取（或懒加载）HuggingFaceEmbeddings 单例。

    首次调用时下载/加载模型（约 90MB），后续调用直接返回缓存。
    HF_ENDPOINT 环境变量必须在 import 之前设置，才能走镜像。
    HF_HUB_OFFLINE=1 防止在已有缓存时做网络校验（国内网络问题会导致 httpx 报错）。
    """
    global _embedder
    if _embedder is None:
        # ★ 关键：必须在 import langchain_huggingface 之前设置
        if settings.HF_ENDPOINT:
            os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT

        # 离线模式：模型已在本地缓存，直接读取不校验网络
        # 配合 model_kwargs 传入 local_files_only=True，双重保障
        os.environ["HF_HUB_OFFLINE"] = "1"

        # 延迟 import，确保环境变量先生效
        from langchain_huggingface import HuggingFaceEmbeddings

        _embedder = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"local_files_only": True},
        )
    return _embedder
