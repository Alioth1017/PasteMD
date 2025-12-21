"""macOS Excel spreadsheet placer."""

import subprocess
import json
from typing import List
from ..base import BaseSpreadsheetPlacer
from ..formatting import CellFormat
from ....core.types import PlacementResult
from ....utils.logging import log
from ....i18n import t


class ExcelPlacer(BaseSpreadsheetPlacer):
    """macOS Excel 内容落地器（直接操作单元格）"""
    
    def place(self, table_data: List[List[str]], config: dict) -> PlacementResult:
        """
        通过 AppleScript 直接插入表格数据到 Excel
        
        策略（类似 Windows COM 方案）：
        1. 获取当前选中的单元格位置
        2. 批量设置单元格值
        3. 应用格式（粗体、斜体等）
        
        Note:
            使用 AppleScript 直接操作单元格，无需临时文件
        """
        try:
            keep_format = config.get("keep_format", True)
            
            # 预处理表格数据
            processed_data = self._process_table_data(table_data, keep_format)
            
            # 使用 AppleScript 插入
            success = self._applescript_insert_direct(processed_data, keep_format)
            
            if success:
                return PlacementResult(success=True, method="applescript")
            else:
                raise Exception(t("placer.macos_excel.applescript_failed"))
        
        except Exception as e:
            log(f"Excel AppleScript 插入失败: {e}")
            return PlacementResult(
                success=False,
                method="applescript",
                error=t("placer.macos_excel.insert_failed", error=str(e))
            )
    
    def _process_table_data(self, table_data: List[List[str]], keep_format: bool) -> dict:
        """
        预处理表格数据，提取纯文本和格式信息
        
        Args:
            table_data: 原始表格数据
            keep_format: 是否保留格式
            
        Returns:
            包含纯文本数据和格式信息的字典
        """
        rows_count = len(table_data)
        cols_count = max(len(row) for row in table_data) if table_data else 0
        
        # 纯文本数据（用于批量设置）
        clean_data = []
        # 格式信息 [{row, col, bold, italic, ...}, ...]
        format_info = []
        
        for i, row in enumerate(table_data):
            clean_row = []
            for j, cell_value in enumerate(row):
                if keep_format:
                    cell_format = CellFormat(cell_value)
                    clean_text = cell_format.parse()
                    clean_row.append(clean_text)
                    
                    # 收集格式信息
                    if len(cell_format.segments) > 0:
                        seg = cell_format.segments[0]  # 暂时只支持单段格式
                        if seg.bold or seg.italic or seg.strikethrough:
                            format_info.append({
                                "row": i,
                                "col": j,
                                "bold": seg.bold,
                                "italic": seg.italic,
                                "strikethrough": seg.strikethrough
                            })
                else:
                    cell_format = CellFormat(cell_value)
                    clean_row.append(cell_format.parse())
            
            # 补齐行长度
            while len(clean_row) < cols_count:
                clean_row.append('')
            clean_data.append(clean_row)
        
        return {
            "data": clean_data,
            "rows": rows_count,
            "cols": cols_count,
            "formats": format_info
        }
    
    def _applescript_insert_direct(self, processed_data: dict, keep_format: bool) -> bool:
        """
        使用 AppleScript 直接插入表格数据（无需临时文件）
        
        Args:
            processed_data: 预处理后的数据
            keep_format: 是否应用格式
            
        Returns:
            True 如果插入成功
            
        Raises:
            Exception: 插入失败时
        """
        clean_data = processed_data["data"]
        rows_count = processed_data["rows"]
        cols_count = processed_data["cols"]
        format_info = processed_data["formats"]
        
        # 将数据转换为 JSON 字符串（用于传递给 AppleScript）
        data_json = json.dumps(clean_data).replace('"', '\\"')
        
        # 构建 AppleScript
        script = f'''
        tell application "Microsoft Excel"
            -- 确保有活动工作簿
            if (count of workbooks) is 0 then
                make new workbook
            end if
            
            -- 获取活动工作表
            set targetSheet to active sheet
            
            -- 获取起始单元格位置
            set startCell to selection
            set startRow to first row index of startCell
            set startCol to first column index of startCell
            
            -- 设置数据
            set dataArray to {{}}
            {self._build_data_assignment(clean_data)}
            
            -- 批量设置单元格值
            repeat with i from 1 to {rows_count}
                repeat with j from 1 to {cols_count}
                    set cellRow to startRow + i - 1
                    set cellCol to startCol + j - 1
                    set targetCell to cell cellRow of row cellRow of targetSheet
                    set value of cell cellCol of row cellRow to item j of item i of dataArray
                end repeat
            end repeat
            
            -- 应用格式（第一行加粗）
            repeat with j from 1 to {cols_count}
                set cellCol to startCol + j - 1
                set headerCell to cell cellCol of row startRow
                set bold of font object of headerCell to true
            end repeat
            
            {self._build_format_script(format_info, keep_format) if keep_format else ""}
            
            -- 选中插入的区域
            set endRow to startRow + {rows_count} - 1
            set endCol to startCol + {cols_count} - 1
            set endCell to cell endCol of row endRow
            select range (get address startCell & ":" & get address endCell)
            
            return true
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            log(f"Excel AppleScript 执行成功，插入 {rows_count}x{cols_count} 表格")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            log(f"Excel AppleScript 执行失败: {error_msg}")
            raise Exception(t("placer.macos_excel.script_execution_failed", error=error_msg))
        except subprocess.TimeoutExpired:
            log("Excel AppleScript 执行超时")
            raise Exception(t("placer.macos_excel.script_timeout"))
    
    def _build_data_assignment(self, clean_data: List[List[str]]) -> str:
        """构建 AppleScript 的数据赋值语句"""
        lines = []
        for i, row in enumerate(clean_data, 1):
            row_items = []
            for cell in row:
                # 转义 AppleScript 字符串
                escaped = cell.replace('\\', '\\\\').replace('"', '\\"')
                row_items.append(f'"{escaped}"')
            lines.append(f"set item {i} of dataArray to {{{', '.join(row_items)}}}")
        return '\n            '.join(lines)
    
    def _build_format_script(self, format_info: List[dict], apply: bool) -> str:
        """构建格式应用的 AppleScript"""
        if not apply or not format_info:
            return ""
        
        lines = ["-- 应用单元格格式"]
        for fmt in format_info:
            row_offset = fmt["row"]
            col_offset = fmt["col"]
            lines.append(f'''
            set fmtCell to cell (startCol + {col_offset}) of row (startRow + {row_offset})
            ''')
            if fmt.get("bold"):
                lines.append("set bold of font object of fmtCell to true")
            if fmt.get("italic"):
                lines.append("set italic of font object of fmtCell to true")
            if fmt.get("strikethrough"):
                lines.append("set strikethrough of font object of fmtCell to true")
        
        return '\n            '.join(lines)
