"""文档解析器抽象基类。

定义所有解析器必须实现的接口，使用策略模式让不同文件格式
各自实现解析逻辑，通过 registry 自动分发。
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseParser(ABC):
    """文档文本提取的策略接口。"""

    @abstractmethod
    def parse(self, file: BinaryIO) -> str:
        """从二进制文件流中提取纯文本。

        Args:
            file: 以二进制模式打开的文件对象。

        Returns:
            提取出的文本内容字符串。
        """
        ...

    @staticmethod
    @abstractmethod
    def supports(extension: str) -> bool:
        """判断该解析器是否支持给定的文件扩展名。

        Args:
            extension: 小写的文件扩展名，包含点号（如 '.pdf'）。
        """
        ...
