"""Spreadsheet domain - cross-platform spreadsheet placement."""

import sys

# 导出基类
from .base import BaseSpreadsheetPlacer
from .generator import SpreadsheetGenerator

# 导出类型
from ...core.types import PlacementResult

# 平台特定实现(统一类名)
if sys.platform == "darwin":
    from .macos.excel import ExcelPlacer
    from .macos.wps_excel import WPSExcelPlacer
elif sys.platform == "win32":
    from .win32.excel import ExcelPlacer
    from .win32.wps_excel import WPSExcelPlacer
else:
    # 不支持的平台
    class ExcelPlacer(BaseSpreadsheetPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")
    
    class WPSExcelPlacer(BaseSpreadsheetPlacer):
        def place(self, *args, **kwargs):
            raise NotImplementedError(f"不支持的平台: {sys.platform}")

__all__ = [
    "BaseSpreadsheetPlacer",
    "PlacementResult",
    "ExcelPlacer",
    "WPSExcelPlacer",
    "SpreadsheetGenerator",
]
