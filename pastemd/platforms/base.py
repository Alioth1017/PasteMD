"""Base interface definitions for platform-specific implementations (Python 3)."""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class ClipboardHandler(ABC):
    """Abstract base for clipboard operations."""

    @abstractmethod
    def get_text(self) -> str:
        """Get plain text from clipboard."""

    @abstractmethod
    def get_html(self, config: Optional[dict] = None) -> Optional[str]:
        """Get HTML content from clipboard if available."""

    @abstractmethod
    def is_html_available(self) -> bool:
        """Check if HTML format is available in clipboard."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if clipboard is empty."""


class HotkeyManager(ABC):
    """Abstract base for global hotkey management."""

    @abstractmethod
    def bind(self, hotkey: str, callback: Callable[[], None]) -> None:
        """Bind a global hotkey."""

    @abstractmethod
    def unbind(self) -> None:
        """Unbind current hotkey."""

    @abstractmethod
    def is_hotkey_available(self, hotkey: str) -> bool:
        """Check if a hotkey is available."""


class NotificationHandler(ABC):
    """Abstract base for system notifications."""

    @abstractmethod
    def notify(self, title: str, message: str, timeout: int = 5, ok: bool = True) -> None:
        """Show a system notification."""


class AppDetector(ABC):
    """Abstract base for detecting active applications."""

    @abstractmethod
    def detect_active_app(self) -> str:
        """Detect the currently active application."""

    @abstractmethod
    def is_word_like_app_available(self) -> bool:
        """Check if any Word-like application is running."""

    @abstractmethod
    def is_excel_like_app_available(self) -> bool:
        """Check if any Excel-like application is running."""


class DocumentInserter(ABC):
    """Abstract base for document insertion."""

    @abstractmethod
    def insert(self, docx_path: str, move_cursor_to_end: bool = True) -> None:
        """Insert DOCX content at current cursor position."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the document application is available."""


class SpreadsheetInserter(ABC):
    """Abstract base for spreadsheet (table) insertion."""

    @abstractmethod
    def insert_table(self, xlsx_path: str) -> None:
        """Insert table/spreadsheet at current location."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the spreadsheet application is available."""


class DocumentInserterFactory(ABC):
    """Factory for creating appropriate document inserters."""

    @abstractmethod
    def get_word_inserter(self) -> DocumentInserter:
        """Get Word document inserter."""

    @abstractmethod
    def get_excel_inserter(self) -> SpreadsheetInserter:
        """Get Excel/spreadsheet inserter."""

    @abstractmethod
    def get_inserter_for_app(self, app_id: str) -> Optional[object]:
        """Get appropriate inserter for detected application."""


__all__ = [
    "ClipboardHandler",
    "HotkeyManager",
    "NotificationHandler",
    "AppDetector",
    "DocumentInserter",
    "SpreadsheetInserter",
    "DocumentInserterFactory",
]
