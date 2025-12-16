"""Default configuration values."""

import os
import sys
from typing import Dict, Any
from .paths import resource_path


def find_pandoc() -> str:
    """
    查找 pandoc 路径，兼容：
    - PyInstaller 单文件（exe 同级 pandoc）
    - PyInstaller 非单文件
    - Nuitka 单文件 / 非单文件
    - Inno 安装
    - 源码运行（系统 pandoc）
    """
    # Windows 特定路径
    if sys.platform == 'win32':
        # exe 同级 pandoc
        exe_dir = os.path.dirname(sys.executable)
        candidate = os.path.join(exe_dir, "pandoc", "pandoc.exe")
        if os.path.exists(candidate):
            return candidate

        # 打包资源路径（Nuitka / PyInstaller onedir / 新方案）
        candidate = resource_path("pandoc/pandoc.exe")
        if os.path.exists(candidate):
            return candidate
    
    # 兜底：系统 pandoc
    return "pandoc"


def get_default_save_dir() -> str:
    """获取平台特定的默认保存目录"""
    if sys.platform == 'win32':
        # Windows: 使用 %USERPROFILE%\Documents\pastemd
        return os.path.expandvars(r"%USERPROFILE%\Documents\pastemd")
    elif sys.platform == 'darwin':
        # macOS: 使用 ~/Documents/pastemd
        return os.path.expanduser("~/Documents/pastemd")
    else:
        # Linux: 使用 ~/Documents/pastemd
        return os.path.expanduser("~/Documents/pastemd")


DEFAULT_CONFIG: Dict[str, Any] = {
    # Windows: Ctrl+Shift+V, macOS: Cmd+Shift+V
    "hotkey": "<cmd>+<shift>+v" if sys.platform == "darwin" else "<ctrl>+<shift>+v",
    "pandoc_path": find_pandoc(),
    "reference_docx": None,
    "save_dir": get_default_save_dir(),
    "keep_file": False,
    "notify": True,
    "enable_excel": True,
    "excel_keep_format": True,
    "auto_open_on_no_app": True,
    "md_disable_first_para_indent": True,
    "html_disable_first_para_indent": True,
    "html_formatting": {
        "strikethrough_to_del": True,
    },
    "move_cursor_to_end": True,
    "Keep_original_formula": False,
    "language": "zh",
    "enable_latex_replacements": True,
}
