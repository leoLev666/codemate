"""RAG 流水线测试。"""

from io import BytesIO

from src.backend.config import Settings
from src.backend.engine.rag_pipeline import RAGPipeline


def test_index_and_retrieve_txt(settings: Settings):
    """端到端测试：索引一个文本文件，然后检索相关块。

    写入链路：解析 → 分块 → 嵌入 → 存储
    查询链路：问题嵌入 → 向量检索 → 返回相关块
    """
    pipeline = RAGPipeline(settings)

    # 准备测试文档
    content = (
        "2025年全球智能家居市场规模达到1200亿美元。\n"
        "主要参与者包括小米、华为、谷歌、海尔。\n"
        "AI语音助手和Matter协议是关键技术。"
    )
    file = BytesIO(content.encode("utf-8"))

    # 写入：索引文档
    result = pipeline.index_document(file, "report.txt")
    assert result.chunk_count > 0, "应该至少切分出 1 个块"

    # 查询：检索相关内容
    chunks = pipeline.retrieve("智能家居市场规模 2025")
    assert len(chunks) > 0, "应该检索到至少 1 个相关块"

    # 检索到的内容应与查询相关
    combined = " ".join(c.content for c in chunks)
    assert "1200" in combined or "智能家居" in combined


def test_build_context(settings: Settings):
    """上下文组装应包含来源标注和相关度分数。"""
    pipeline = RAGPipeline(settings)
    from src.backend.engine.retriever import RetrievedChunk

    chunks = [
        RetrievedChunk(
            content="市场增长率为15%。",
            score=0.95,
            metadata={"source_file": "report.pdf", "chunk_index": 0},
        )
    ]
    ctx = pipeline.build_context(chunks)
    assert "report.pdf" in ctx, "上下文应包含来源文件名"
    assert "0.95" in ctx, "上下文应包含相关度分数"
    assert "市场增长率为15%" in ctx, "上下文应包含原文内容"
