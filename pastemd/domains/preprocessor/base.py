"""Base preprocessor class."""

from abc import ABC, abstractmethod


class BasePreprocessor(ABC):
    """内容预处理器基类"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def process(self, content: any) -> any:
        """
        预处理内容

        Args:
            content: 原始内容

        Returns:
            处理后的内容
        """
        pass
