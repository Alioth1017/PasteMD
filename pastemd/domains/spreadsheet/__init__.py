"""Spreadsheet insertion domain."""

import sys

# Windows 专用导入
if sys.platform == 'win32':
    from .excel import MSExcelInserter
    from .wps_excel import WPSExcelInserter
    __all__ = ["MSExcelInserter", "WPSExcelInserter"]
else:
    # macOS/Linux: 提供空实现
    class MSExcelInserter:
        def insert(self, *args, **kwargs):
            raise NotImplementedError("Excel insertion not yet implemented on this platform")
    
    class WPSExcelInserter:
        def insert(self, *args, **kwargs):
            raise NotImplementedError("WPS Excel insertion not yet implemented on this platform")
    
    __all__ = ["MSExcelInserter", "WPSExcelInserter"]
