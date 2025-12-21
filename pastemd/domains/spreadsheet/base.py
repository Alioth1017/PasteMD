"""Base classes for spreadsheet placement."""

from abc import ABC, abstractmethod
from typing import List
from ...core.types import PlacementResult


class BaseSpreadsheetPlacer(ABC):
    """表格内容落地器基类"""
    
    @abstractmethod
    def place(self, table_data: List[List[str]], config: dict) -> PlacementResult:
        """
        将表格数据落地到目标应用
        
        Args:
            table_data: 二维数组表格数据
            config: 配置字典（包含 keep_format 等选项）
            
        Returns:
            PlacementResult: 落地结果
            
        Note:
            ❌ 不做优雅降级,失败即返回错误
            ✅ 由 Workflow 决定如何处理失败(通知用户/记录日志)
        """
        pass
