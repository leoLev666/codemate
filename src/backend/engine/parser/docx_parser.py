"""DOCX 文本提取器，基于 python-docx 库。"""

from typing import BinaryIO

from docx import Document as DocxDocument

from src.backend.engine.parser.base import BaseParser


class DocxParser(BaseParser):
    """使用 python-docx 提取 Word 文档中的段落文本。"""

    def parse(self, file: BinaryIO) -> str:
        doc = DocxDocument(file)
        return "\n".join(p.text for p in doc.paragraphs)

    @staticmethod
    def supports(extension: str) -> bool:
        return extension == ".docx"
