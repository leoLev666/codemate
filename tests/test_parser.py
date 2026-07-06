"""文档解析器的单元测试。"""

from io import BytesIO

import pytest

from src.backend.engine.parser.docx_parser import DocxParser
from src.backend.engine.parser.pdf_parser import PdfParser
from src.backend.engine.parser.pptx_parser import PptxParser
from src.backend.engine.parser.registry import parse_document
from src.backend.engine.parser.txt_parser import TxtParser


class TestTxtParser:
    """TXT 解析器测试。"""

    def test_supports_txt(self):
        """supports() 应对 .txt 返回 True，其他返回 False。"""
        assert TxtParser.supports(".txt") is True
        assert TxtParser.supports(".pdf") is False

    def test_parse_utf8(self):
        """应正确解析 UTF-8 编码的文本（含中文）。"""
        content = "Hello, 世界!"
        parser = TxtParser()
        result = parser.parse(BytesIO(content.encode("utf-8")))
        assert result == content


class TestPdfParser:
    def test_supports_pdf(self):
        assert PdfParser.supports(".pdf") is True
        assert PdfParser.supports(".docx") is False


class TestDocxParser:
    def test_supports_docx(self):
        assert DocxParser.supports(".docx") is True
        assert DocxParser.supports(".pdf") is False


class TestPptxParser:
    def test_supports_pptx(self):
        assert PptxParser.supports(".pptx") is True
        assert PptxParser.supports(".pdf") is False


class TestRegistry:
    """解析器注册表测试。"""

    def test_parse_txt(self):
        """应通过文件名自动分发到 TxtParser。"""
        data = BytesIO("hello world".encode("utf-8"))
        result = parse_document(data, "test.txt")
        assert result == "hello world"

    def test_unsupported_extension(self):
        """不支持的文件类型应抛出 ValueError。"""
        data = BytesIO(b"dummy")
        with pytest.raises(ValueError, match="不支持"):
            parse_document(data, "test.xyz")
