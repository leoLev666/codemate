"""重排序模块（可选功能）。

使用 CrossEncoder 模型对检索到的候选块进行精细打分，
解决双塔嵌入模型"问题和文档分别编码、交互不充分"的问题。

开关由 settings.RERANKER_ENABLED 控制：
  - True: 加载 CrossEncoder，对候选块重排序。
  - False: 直接透传原结果，零额外开销。
"""

from sentence_transformers import CrossEncoder

from src.backend.config import Settings
from src.backend.engine.retriever import RetrievedChunk

# 全局缓存的 CrossEncoder 模型
_reranker_model: CrossEncoder | None = None


def _get_model(settings: Settings) -> CrossEncoder:
    """懒加载 CrossEncoder 模型（全局单例）。"""
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = CrossEncoder(settings.RERANKER_MODEL)
    return _reranker_model


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    settings: Settings,
) -> list[RetrievedChunk]:
    """用 CrossEncoder 对候选块重新打分并排序。

    原理：向量检索是"粗筛"（双塔模型，速度快但交互不充分），
    CrossEncoder 把 query 和 chunk 拼接后联合编码，
    是"精选"（交互充分但速度慢），只对少量候选块做。

    Args:
        query: 用户问题。
        chunks: 向量检索引擎返回的候选块列表。
        settings: 应用配置（控制开关和模型选择）。

    Returns:
        重排后的块列表（按新分数降序）。如果功能关闭则原样返回。
    """
    if not settings.RERANKER_ENABLED or not chunks:
        return chunks

    model = _get_model(settings)
    # 构造 (query, chunk) 对
    pairs = [(query, chunk.content) for chunk in chunks]
    scores = model.predict(pairs)  # type: ignore[attr-defined]

    for chunk, score in zip(chunks, scores):
        chunk.score = float(score)

    chunks.sort(key=lambda c: c.score, reverse=True)
    return chunks
