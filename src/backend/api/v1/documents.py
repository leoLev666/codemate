"""文档管理 API 端点。

提供文档上传（自动解析 + 索引）、列表、详情和删除功能。
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_settings
from src.backend.engine.rag_pipeline import RAGPipeline
from src.backend.models.db import Document
from src.backend.models.schemas import DocumentOut, DocumentUploadResponse
from src.backend.services.document_service import DocumentService
from src.shared.constants import SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/documents", tags=["documents"])

# 模块级缓存
_rag_pipeline: RAGPipeline | None = None
_doc_service: DocumentService | None = None


def _get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(get_settings())
    return _rag_pipeline


def _get_doc_service() -> DocumentService:
    global _doc_service
    if _doc_service is None:
        _doc_service = DocumentService(get_settings())
    return _doc_service


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """上传文档：自动解析、分块、嵌入并存入 ChromaDB。

    支持格式：PDF、DOCX、PPTX、TXT。
    """
    if not file.filename:
        return {"error": "未提供文件名"}

    # 检查文件类型
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "error": f"不支持的文件类型: {ext}。支持的类型: {list(SUPPORTED_EXTENSIONS)}"
        }

    service = _get_doc_service()
    pipeline = _get_rag_pipeline()
    return await service.upload(db, file.file, file.filename, pipeline)


@router.get("", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    """列出所有已上传的文档，最近上传的排前面。"""
    result = await db.execute(
        select(Document).order_by(Document.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [
        DocumentOut(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            file_size_bytes=d.file_size_bytes,
            chunk_count=d.chunk_count,
            status=d.status,
            uploaded_at=d.uploaded_at,
        )
        for d in docs
    ]


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个文档的元数据。"""
    doc = await db.get(Document, doc_id)
    if not doc:
        return {"error": "文档不存在"}
    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        chunk_count=doc.chunk_count,
        status=doc.status,
        uploaded_at=doc.uploaded_at,
    )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """删除文档及其在向量库中的所有块。"""
    doc = await db.get(Document, doc_id)
    if doc:
        pipeline = _get_rag_pipeline()
        pipeline.delete_document(doc_id)
        await db.delete(doc)
    return {"status": "deleted", "doc_id": doc_id}
