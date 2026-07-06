"""解析器注册表 —— 根据文件扩展名自动分发到正确的解析器。

扩展新格式只需两步：
  1. 写一个继承 BaseParser 的新类。
  2. 在下面的 _PARSERS 列表中注册。
其他任何文件都不需要改动。
"""

import os
from typing import BinaryIO

from src.backend.engine.parser.base import BaseParser
from src.backend.engine.parser.docx_parser import DocxParser
from src.backend.engine.parser.pdf_parser import PdfParser
from src.backend.engine.parser.pptx_parser import PptxParser
from src.backend.engine.parser.txt_parser import TxtParser

# 所有已注册的解析器实例，顺序不重要，按扩展名精确匹配。
_PARSERS: list[BaseParser] = [
    PdfParser(),
    DocxParser(),
    PptxParser(),
    TxtParser(),
]


def _get_extension(filename: str) -> str:
    """从文件名提取小写扩展名（含点号）。"""
    return os.path.splitext(filename)[1].lower()


def parse_document(file: BinaryIO, filename: str) -> str:
    """根据文件名自动选择解析器并提取文本。

    Args:
        file: 二进制文件对象（需支持 .read()）。
        filename: 原始文件名，用于识别文件格式。

    Returns:
        提取到的纯文本内容。

    Raises:
        ValueError: 文件类型不受支持时抛出。
    """
    ext = _get_extension(filename)
    for parser in _PARSERS:
        if parser.supports(ext):
            return parser.parse(file)
    raise ValueError(f"不支持的文件类型: {ext}")
