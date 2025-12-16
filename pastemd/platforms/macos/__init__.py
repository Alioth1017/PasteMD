"""macOS platform module - exports macOS-specific implementations."""

from .app_detector import MacOSAppDetector
from .clipboard import MacOSClipboardHandler
from .hotkey import MacOSHotkeyManager
from .notification import MacOSNotificationHandler
from .document_inserter import MacOSDocumentInserterFactory


def get_app_detector():
    return MacOSAppDetector()


def get_clipboard_handler():
    return MacOSClipboardHandler()


def get_hotkey_manager():
    return MacOSHotkeyManager()


def get_notification_handler():
    return MacOSNotificationHandler()


def get_document_inserter_factory():
    return MacOSDocumentInserterFactory()


__all__ = [
    "MacOSAppDetector",
    "MacOSClipboardHandler",
    "MacOSHotkeyManager",
    "MacOSNotificationHandler",
    "MacOSDocumentInserterFactory",
    "get_app_detector",
    "get_clipboard_handler",
    "get_hotkey_manager",
    "get_notification_handler",
    "get_document_inserter_factory",
]