"""RAG Pipeline —— 检索增强生成的核心编排器。

这是整个项目最重要的文件。它串联了 RAG 的完整流程：

  写入链路（文档上传时）：  解析 → 分块 → 嵌入 → 存入 ChromaDB
  查询链路（用户提问时）：  向量检索 → [可选重排序] → 构建上下文 → 交给 LLM

注意：本文件不依赖 FastAPI、SQLAlchemy 或任何 Web 框架。
它可以在 CLI、测试、Web 端点等任何场景中工作。
"""

import uuid
from dataclasses import dataclass, field
from io import BytesIO
from typing import BinaryIO

from langchain_core.documents import Document as LCDocument

from src.backend.config import Settings
from src.backend.engine.chunker import chunk_text
from src.backend.engine.embedder import get_embedder
from src.backend.engine.parser.registry import parse_document
from src.backend.engine.reranker import rerank
from src.backend.engine.retriever import RetrievedChunk, Retriever


# ── 数据结构 ──────────────────────────────────────────────────

@dataclass
class IndexResult:
    """文档索引结果。"""

    doc_id: str
    chunk_count: int


@dataclass
class QueryResult:
    """单次 RAG 查询的完整结果。"""

    answer: str
    sources: list[RetrievedChunk] = field(default_factory=list)


# ── Pipeline 核心 ─────────────────────────────────────────────

class RAGPipeline:
    """完整的 RAG 流水线：文档入库 + 智能问答。

    使用示例:
        pipeline = RAGPipeline(settings)
        pipeline.index_document(file_bytes, "report.pdf")
        result = pipeline.query("市场规模是多少？")
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._retriever = Retriever(settings)

    # ── 写入链路（文档上传时调用） ──────────────────────────

    def index_document(self, file: BinaryIO, filename: str) -> IndexResult:
        """解析文档 → 分块 → 嵌入 → 存入向量数据库。

        这是 RAG 的"离线"阶段：用户上传文档时执行。

        Args:
            file: 二进制文件对象。
            filename: 原始文件名（用于识别格式）。

        Returns:
            IndexResult，包含生成的文档 ID 和切分的块数量。
        """
        # 1. 解析 —— 从 PDF/DOCX/PPTX/TXT 中提取纯文本
        text = parse_document(file, filename)

        # 2. 分块 —— 切分为带重叠的文本段
        doc_id = str(uuid.uuid4())
        metadata = {"doc_id": doc_id, "source_file": filename}
        chunks = chunk_text(text, self._settings, metadata=metadata)

        # 标记每个块在原文中的序号
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i

        # 3. 嵌入 + 4. 存储 —— ChromaDB 在 add_documents 内部完成
        self._retriever.add_documents(chunks)

        return IndexResult(doc_id=doc_id, chunk_count=len(chunks))

    # ── 查询链路（用户提问时调用） ──────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """检索与问题最相关的文档块（不调用 LLM）。

        单独暴露此方法，方便调试检索质量而不消耗 API 额度。

        Args:
            query: 用户问题。
            top_k: 返回块数（默认取配置值）。

        Returns:
            相关度降序排列的检索结果。
        """
        chunks = self._retriever.search(query, top_k=top_k)
        chunks = rerank(query, chunks, self._settings)
        return chunks

    def build_context(self, chunks: list[RetrievedChunk]) -> str:
        """将检索到的块组装为 LLM 可读的上下文字符串。

        每个块前标注来源文件和相似度分数，
        帮助 LLM 理解哪些信息更可靠。
        """
        if not chunks:
            return ""

        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source_file", "unknown")
            parts.append(
                f"─── 来源 {i}（{source}，相关度 {chunk.score:.2f}）───\n"
                f"{chunk.content}"
            )
        return "\n\n".join(parts)

    # ── 维护操作 ────────────────────────────────────────────

    def delete_document(self, doc_id: str) -> None:
        """从向量库中移除指定文档的所有块。"""
        self._retriever.delete_by_filter({"doc_id": doc_id})

    @property
    def chunk_count(self) -> int:
        """当前已索引的块总数。"""
        return self._retriever.collection_count()
