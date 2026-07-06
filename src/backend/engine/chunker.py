"""文本分块模块。

使用 LangChain 的 RecursiveCharacterTextSplitter 将长文档
切分为重叠的文本块，每块大小适合嵌入模型的上下文窗口。
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.backend.config import Settings


def chunk_text(
    text: str,
    settings: Settings,
    metadata: dict | None = None,
) -> list[Document]:
    """将长文本切分为带重叠的块，用于后续嵌入和检索。

    切分策略：
      - 优先在段落边界（\n\n）切分，其次换行（\n），最后句号/空格/字符。
      - 块之间有 overlap，防止关键信息刚好落在边界上被切断。

    Args:
        text: 原始文档文本。
        settings: 应用配置（含 chunk_size、chunk_overlap）。
        metadata: 附加到每个块上的元数据（如来源文件名、页码）。

    Returns:
        LangChain Document 对象列表，可直接送入嵌入模型。
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    docs = splitter.create_documents(
        texts=[text],
        metadatas=[metadata or {}],
    )
    return docs
