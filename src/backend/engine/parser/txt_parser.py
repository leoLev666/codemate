"""纯文本文件读取器。"""

from typing import BinaryIO

from src.backend.engine.parser.base import BaseParser


class TxtParser(BaseParser):
    """读取纯文本文件，使用 UTF-8 编码，容错处理乱码。"""

    def parse(self, file: BinaryIO) -> str:
        raw = file.read()
        return raw.decode("utf-8", errors="ignore")

    @staticmethod
    def supports(extension: str) -> bool:
        return extension == ".txt"
