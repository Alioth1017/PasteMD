"""Application awakener - awakens applications by creating and opening files."""

import os
import subprocess
import sys
from typing import Literal, List

from ...utils.app_logging import log
from ...domains.spreadsheet.generator import SpreadsheetGenerator


AppType = Literal["word", "wps", "excel", "wps_excel"]


class AppLauncher:
    """应用唤醒器 - 通过创建文件并用默认应用打开来唤醒应用"""
    
    @staticmethod
    def awaken_and_open_document(docx_path: str) -> bool:
        """
        唤醒文档应用（Word/WPS）并打开指定的 DOCX 文件（前台显示）
        
        Args:
            docx_path: DOCX 文件的完整路径（文件应已存在且包含内容）
            
        Returns:
            True 如果成功打开
        """
        try:
            if not os.path.exists(docx_path):
                log(f"Document file not found: {docx_path}")
                return False
            
            # 使用平台特定的方式打开文件
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', docx_path])
                log(f"Successfully opened document in foreground: {docx_path}")
                return True
            elif sys.platform == 'win32':  # Windows
                try:
                    # 方法1: 使用 start 命令，会在前台打开
                    subprocess.Popen(
                        ['cmd', '/c', 'start', '', docx_path],
                        shell=False,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    log(f"Successfully opened document in foreground: {docx_path}")
                    return True
                except Exception as e:
                    log(f"Failed to open with subprocess, falling back to os.startfile: {e}")
                    # 回退到 os.startfile
                    os.startfile(docx_path)
                    log(f"Successfully opened document with default application: {docx_path}")
                    return True
            else:  # Linux
                subprocess.Popen(['xdg-open', docx_path])
                log(f"Successfully opened document: {docx_path}")
                return True
        except Exception as e:
            log(f"Failed to open document: {e}")
            return False
    
    @staticmethod
    def awaken_and_open_spreadsheet(xlsx_path: str) -> bool:
        """
        唤醒表格应用（Excel/WPS）并打开指定的 XLSX 文件（前台显示）
        
        Args:
            xlsx_path: XLSX 文件的完整路径（文件应已存在且包含内容）
            
        Returns:
            True 如果成功打开
        """
        try:
            if not os.path.exists(xlsx_path):
                log(f"Spreadsheet file not found: {xlsx_path}")
                return False
            
            # 使用平台特定的方式打开文件
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', xlsx_path])
                log(f"Successfully opened spreadsheet in foreground: {xlsx_path}")
                return True
            elif sys.platform == 'win32':  # Windows
                try:
                    subprocess.Popen(
                        ['cmd', '/c', 'start', '', xlsx_path],
                        shell=False,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    log(f"Successfully opened spreadsheet in foreground: {xlsx_path}")
                    return True
                except Exception as e:
                    log(f"Failed to open with subprocess, falling back to os.startfile: {e}")
                    os.startfile(xlsx_path)
                    log(f"Successfully opened spreadsheet with default application: {xlsx_path}")
                    return True
            else:  # Linux
                subprocess.Popen(['xdg-open', xlsx_path])
                log(f"Successfully opened spreadsheet: {xlsx_path}")
                return True
        except Exception as e:
            log(f"Failed to open spreadsheet: {e}")
            return False
    
    @staticmethod
    def generate_and_open_spreadsheet(table_data: List[List[str]], output_path: str,
                                      keep_format: bool = True) -> bool:
        """
        生成 XLSX 文件并用默认应用打开
        
        Args:
            table_data: 二维数组表格数据
            output_path: 输出 XLSX 文件路径
            keep_format: 是否保留格式
            
        Returns:
            True 如果成功生成并打开
        """
        try:
            # 生成 XLSX 文件
            SpreadsheetGenerator.generate_xlsx(table_data, output_path, keep_format)
            
            # 打开文件
            return AppLauncher.awaken_and_open_spreadsheet(output_path)
        except Exception as e:
            log(f"Failed to generate and open spreadsheet: {e}")
            return False


