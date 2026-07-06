"""前后端共享的常量定义。"""

# 支持的文档上传格式：扩展名 → MIME 类型
SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

# 人类可读的文件类型标签
FILE_TYPE_LABELS: dict[str, str] = {
    ".txt": "TXT 文本",
    ".pdf": "PDF 文档",
    ".docx": "Word 文档",
    ".pptx": "PPT 演示",
}

# API 版本前缀
API_V1_PREFIX = "/api/v1"
