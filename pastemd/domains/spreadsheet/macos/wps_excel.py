"""macOS WPS Excel spreadsheet placer - not supported."""

from typing import List
from ..base import BaseSpreadsheetPlacer
from ....core.types import PlacementResult
from ....utils.logging import log
from ....i18n import t


class WPSExcelPlacer(BaseSpreadsheetPlacer):
    """macOS WPS Excel 内容落地器 - 暂不支持"""
    
    def place(self, table_data: List[List[str]], config: dict) -> PlacementResult:
        """
        macOS WPS Excel 暂不支持自动插入
        
        原因：
        - macOS WPS 没有提供 AppleScript 接口
        - 无法通过自动化方式插入内容
        """
        error_msg = t("placer.macos_wps_excel.not_supported")
        log(f"macOS WPS Excel 不支持: {error_msg}")
        return PlacementResult(
            success=False,
            method="unsupported",
            error=error_msg
        )
