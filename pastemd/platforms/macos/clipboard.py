"""macOS clipboard handler using NSPasteboard and pyperclip."""

from typing import Optional
from ..base import ClipboardHandler

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    from AppKit import NSPasteboard, NSPasteboardTypeString, NSPasteboardTypeHTML
except ImportError:
    NSPasteboard = None
    NSPasteboardTypeString = None
    NSPasteboardTypeHTML = None


class MacOSClipboardHandler(ClipboardHandler):
    """macOS clipboard implementation using NSPasteboard and pyperclip."""

    def get_text(self) -> str:
        """Get plain text from clipboard."""
        try:
            if pyperclip:
                text = pyperclip.paste()
                return text if text else ""
            elif NSPasteboard:
                pasteboard = NSPasteboard.generalPasteboard()
                text = pasteboard.stringForType_(NSPasteboardTypeString)
                return str(text) if text else ""
            else:
                return ""
        except Exception:
            return ""

    def get_html(self, config: Optional[dict] = None) -> Optional[str]:
        """Get HTML content from clipboard if available."""
        if not NSPasteboard:
            return None
        
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            types = pasteboard.types()
            
            if types and NSPasteboardTypeHTML in types:
                html_data = pasteboard.stringForType_(NSPasteboardTypeHTML)
                return str(html_data) if html_data else None
            
            return None
        except Exception:
            return None

    def is_html_available(self) -> bool:
        """Check if HTML format is available in clipboard."""
        if not NSPasteboard:
            return False
        
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            types = pasteboard.types()
            return types and NSPasteboardTypeHTML in types
        except Exception:
            return False

    def is_empty(self) -> bool:
        """Check if clipboard is empty."""
        try:
            text = self.get_text()
            return not text or not text.strip()
        except Exception:
            return True


def get_clipboard_handler():
    return MacOSClipboardHandler()


__all__ = ["MacOSClipboardHandler", "get_clipboard_handler"]
