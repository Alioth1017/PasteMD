"""macOS clipboard operations using AppKit.NSPasteboard."""

import pyperclip
from AppKit import NSPasteboard, NSPasteboardTypeHTML, NSPasteboardTypeString
from ...core.errors import ClipboardError
from ...core.state import app_state
from ..html_formatter import clean_html_content


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
# macOS 文件操作功能 (TODO: 待实现)
# ============================================================

def copy_files_to_clipboard(file_paths: list) -> None:
    """
    将文件路径复制到剪贴板

    TODO: macOS 实现待完成

    Args:
        file_paths: 文件路径列表

    Raises:
        ClipboardError: 功能尚未实现
    """
    raise ClipboardError("copy_files_to_clipboard not implemented on macOS yet")


def is_clipboard_files() -> bool:
    """
    检测剪贴板是否包含文件

    TODO: macOS 实现待完成

    Returns:
        False (macOS 实现待完成)
    """
    return False


def get_clipboard_files() -> list[str]:
    """
    获取剪贴板中的文件路径列表

    TODO: macOS 实现待完成

    Returns:
        空列表 (macOS 实现待完成)
    """
    return []


def get_markdown_files_from_clipboard() -> list[str]:
    """
    从剪贴板获取 Markdown 文件路径列表

    TODO: macOS 实现待完成

    Returns:
        空列表 (macOS 实现待完成)
    """
    return []


def read_file_with_encoding(file_path: str) -> str:
    """
    读取文件内容，自动检测编码

    TODO: macOS 实现待完成

    Args:
        file_path: 文件路径

    Returns:
        文件内容字符串

    Raises:
        ClipboardError: 功能尚未实现
    """
    raise ClipboardError("read_file_with_encoding not implemented on macOS yet")


def read_markdown_files_from_clipboard() -> tuple[bool, list[tuple[str, str]], list[tuple[str, str]]]:
    """
    从剪贴板读取 Markdown 文件内容

    TODO: macOS 实现待完成

    Returns:
        (False, [], []) - macOS 实现待完成
    """
    return False, [], []
