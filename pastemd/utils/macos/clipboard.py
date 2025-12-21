"""macOS clipboard operations using AppKit.NSPasteboard."""

import pyperclip
from AppKit import (
    NSPasteboard,
    NSPasteboardTypeHTML,
    NSPasteboardTypeString,
    NSFilenamesPboardType,
    NSURL,
)
from ...core.errors import ClipboardError
from ...core.state import app_state
from ..html_formatter import clean_html_content
from ..clipboard_file_utils import read_file_with_encoding, filter_markdown_files, read_markdown_files
from ..logging import log


def get_clipboard_text() -> str:
    """
    获取剪贴板文本内容
    
    Returns:
        剪贴板文本内容
        
    Raises:
        ClipboardError: 剪贴板操作失败时
    """
    try:
        text = pyperclip.paste()
        if text is None:
            return ""
        return text
    except Exception as e:
        raise ClipboardError(f"Failed to read clipboard: {e}")


def is_clipboard_empty() -> bool:
    """
    检查剪贴板是否为空
    
    Returns:
        True 如果剪贴板为空或只包含空白字符
    """
    try:
        text = get_clipboard_text()
        return not text or not text.strip()
    except ClipboardError:
        return True


def is_clipboard_html() -> bool:
    """
    检查剪切板内容是否为 HTML 富文本

    Returns:
        True 如果剪贴板中存在 HTML 富文本格式；否则 False
    """
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        # 检查是否存在 HTML 类型
        types = pasteboard.types()
        if types is None:
            return False
        
        # macOS 使用 NSPasteboardTypeHTML (public.html)
        return NSPasteboardTypeHTML in types
    except Exception:
        return False


def get_clipboard_html(config: dict | None = None) -> str:
    """
    获取剪贴板 HTML 富文本内容，并清理 SVG 等不可用内容

    Returns:
        清理后的 HTML 富文本内容

    Raises:
        ClipboardError: 剪贴板操作失败时
    """
    try:
        config = config or getattr(app_state, "config", {})

        pasteboard = NSPasteboard.generalPasteboard()

        # 尝试获取 HTML 数据
        html_data = pasteboard.stringForType_(NSPasteboardTypeHTML)

        if html_data is None:
            raise ClipboardError("No HTML format data in clipboard")

        # macOS 返回的已经是 HTML 内容字符串，不需要像 Windows 那样解析 CF_HTML 格式
        html_content = str(html_data)

        # 清理 SVG 等不可用内容
        cleaned = clean_html_content(html_content, config.get("html_formatting"))

        return cleaned

    except Exception as e:
        raise ClipboardError(f"Failed to read HTML from clipboard: {e}")


# ============================================================
# macOS 文件操作功能
# ============================================================

def copy_files_to_clipboard(file_paths: list) -> None:
    """
    将文件路径复制到剪贴板（NSFilenamesPboardType）

    Args:
        file_paths: 文件路径列表

    Raises:
        ClipboardError: 剪贴板操作失败时
    """
    try:
        import os
        # 确保文件路径是绝对路径
        absolute_paths = [os.path.abspath(path) for path in file_paths if os.path.exists(path)]
        
        if not absolute_paths:
            raise ClipboardError("No valid files to copy to clipboard")
        
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        
        # macOS 使用 NSFilenamesPboardType 存储文件路径
        success = pasteboard.setPropertyList_forType_(absolute_paths, NSFilenamesPboardType)
        
        if not success:
            raise ClipboardError("Failed to set file paths to clipboard")
        
        log(f"Successfully copied {len(absolute_paths)} files to clipboard")
        
    except Exception as e:
        raise ClipboardError(f"Failed to copy files to clipboard: {e}")


def is_clipboard_files() -> bool:
    """
    检测剪贴板是否包含文件

    Returns:
        True 如果剪贴板中存在文件；否则 False
    """
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        types = pasteboard.types()
        if types is None:
            return False
        
        # macOS 使用 NSFilenamesPboardType (或 public.file-url)
        result = NSFilenamesPboardType in types
        log(f"Clipboard files check: {result}")
        return result
    except Exception as e:
        log(f"Failed to check clipboard files: {e}")
        return False


def get_clipboard_files() -> list[str]:
    """
    获取剪贴板中的文件路径列表

    Returns:
        文件绝对路径列表
    """
    file_paths = []
    try:
        pasteboard = NSPasteboard.generalPasteboard()
        
        # 尝试从 NSFilenamesPboardType 获取文件路径
        files = pasteboard.propertyListForType_(NSFilenamesPboardType)
        
        if files:
            file_paths = list(files)
            log(f"Got {len(file_paths)} files from clipboard")
        
    except Exception as e:
        log(f"Failed to get clipboard files: {e}")
    
    return file_paths


def get_markdown_files_from_clipboard() -> list[str]:
    """
    从剪贴板获取 Markdown 文件路径列表

    只返回扩展名为 .md 或 .markdown 的文件

    Returns:
        Markdown 文件的绝对路径列表（按文件名排序）
    """
    all_files = get_clipboard_files()
    return filter_markdown_files(all_files)


def read_markdown_files_from_clipboard() -> tuple[bool, list[tuple[str, str]], list[tuple[str, str]]]:
    """
    从剪贴板读取 Markdown 文件内容

    封装了"获取剪贴板 MD 文件路径 + 逐个读取内容"的完整逻辑。
    读取失败的文件会被跳过，继续处理其它文件。

    Returns:
        (found, files_data, errors) 元组：
        - found: 是否发现并成功读取至少一个 MD 文件
        - files_data: [(filename, content), ...] 成功读取的文件名和内容列表
        - errors: [(filename, error_message), ...] 读取失败的文件和错误信息
    """
    md_files = get_markdown_files_from_clipboard()
    return read_markdown_files(md_files)

