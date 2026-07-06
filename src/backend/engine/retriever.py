"""向量检索引擎，基于 ChromaDB。

支持纯向量检索。混合检索（向量 + BM25）作为后续优化方向预留。
检索返回时已按相似度降序排列。
"""

from dataclasses import dataclass, field

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.backend.config import Settings
from src.backend.engine.embedder import get_embedder


@dataclass
class RetrievedChunk:
    """单个检索结果，包含文本内容、相关度分数和来源元数据。"""

    content: str
    score: float
    metadata: dict = field(default_factory=dict)


class Retriever:
    """ChromaDB 向量检索器。

    负责：
      1. 将文档块嵌入并存入 ChromaDB。
      2. 根据用户查询检索最相似的 top_k 个块。
      3. 支持按元数据过滤删除。
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        embedder = get_embedder(settings)
        self._store = Chroma(
            collection_name="documents",
            embedding_function=embedder,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )

    def add_documents(self, docs: list[Document]) -> list[str]:
        """嵌入并存储文档块，返回块 ID 列表。"""
        return self._store.add_documents(docs)

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filter_metadata: dict | None = None,
    ) -> list[RetrievedChunk]:
        """向量相似度检索。

        底层计算：将 query 嵌入为向量 → 在 ChromaDB 中做余弦相似度搜索。

        Args:
            query: 用户问题 / 搜索查询。
            top_k: 返回的块数量（默认取 settings 中的值）。
            filter_metadata: 可选的 ChromaDB 元数据过滤条件
                             （如 {'source_file': 'report.pdf'}）。

        Returns:
            按相关度降序排列的检索结果列表。
        """
        k = top_k or self._settings.RETRIEVAL_TOP_K
        results = self._store.similarity_search_with_relevance_scores(
            query,
            k=k,
            filter=filter_metadata,
        )
        chunks = []
        for doc, score in results:
            chunks.append(
                RetrievedChunk(
                    content=doc.page_content,
                    score=score,
                    metadata=doc.metadata,
                )
            )
        return chunks

    def delete_by_filter(self, filter_metadata: dict) -> None:
        """按元数据条件批量删除文档块。"""
        ids = self._store.get(where=filter_metadata).get("ids", [])
        if ids:
            self._store.delete(ids)

    def collection_count(self) -> int:
        """当前集合中已索引的块总数。"""
        return self._store._collection.count()
