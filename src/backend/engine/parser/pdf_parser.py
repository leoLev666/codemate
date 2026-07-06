"""PDF 文本提取器，基于 pypdf 库。"""

from typing import BinaryIO

import pypdf

from src.backend.engine.parser.base import BaseParser


class PdfParser(BaseParser):
    """使用 pypdf 逐页提取 PDF 中的文本内容。"""

    def parse(self, file: BinaryIO) -> str:
        reader = pypdf.PdfReader(file)
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts)

    @staticmethod
    def supports(extension: str) -> bool:
        return extension == ".pdf"
