"""文档服务 —— 编排文件上传、解析和索引流程。"""

from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import Settings
from src.backend.engine.rag_pipeline import RAGPipeline
from src.backend.models.db import Document as DocumentORM
from src.backend.models.schemas import DocumentUploadResponse


class DocumentService:
    """处理文档上传 → 解析 → 索引 → 持久化的完整工作流。"""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def upload(
        self,
        db: AsyncSession,
        file: BinaryIO,
        filename: str,
        pipeline: RAGPipeline,
    ) -> DocumentUploadResponse:
        """上传并索引一份文档。

        流程：
          1. 读取文件内容，记录文件大小
          2. 调用 RAG Pipeline 进行 解析→分块→嵌入→存储
          3. 将文档元数据写入 DB

        Args:
            db: 异步数据库会话。
            file: 二进制文件对象。
            filename: 原始文件名。
            pipeline: RAG 流水线实例。

        Returns:
            包含文档元数据的上传结果。
        """
        content = file.read()
        size = len(content)
        file.seek(0)  # 重置指针，否则 pipeline 读到空文件

        # 索引到向量库（解析 + 分块 + 嵌入 + 存储）
        try:
            index_result = pipeline.index_document(file, filename)
        except Exception:
            # 记录失败状态到 DB
            doc = DocumentORM(
                filename=filename,
                file_type=filename.rsplit(".", 1)[-1],
                file_size_bytes=size,
                chunk_count=0,
                status="error",
                error_message=f"解析或索引失败: {filename}",
            )
            db.add(doc)
            await db.flush()
            raise

        # 将元数据写入 DB
        doc = DocumentORM(
            id=index_result.doc_id,
            filename=filename,
            file_type=filename.rsplit(".", 1)[-1],
            file_size_bytes=size,
            chunk_count=index_result.chunk_count,
            status="ready",
        )
        db.add(doc)
        await db.flush()

        return DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size_bytes=doc.file_size_bytes,
            chunk_count=doc.chunk_count,
            status=doc.status,
        )
