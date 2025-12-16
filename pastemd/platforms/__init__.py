"""Platform abstraction layer - handles OS-specific implementations."""

import importlib
import platform as _platform_module
import sys

# Platform detection
PLATFORM_TYPE = sys.platform  # "win32", "darwin", "linux"
OS_NAME = _platform_module.system()  # "Windows", "Darwin", "Linux"

IS_WINDOWS = OS_NAME == "Windows" or PLATFORM_TYPE == "win32"
IS_MACOS = OS_NAME == "Darwin" or PLATFORM_TYPE == "darwin"
IS_LINUX = OS_NAME == "Linux" or PLATFORM_TYPE == "linux"


def get_platform():
    """Get the current platform type: "windows", "macos", or "linux"."""
    if IS_WINDOWS:
        return "windows"
    elif IS_MACOS:
        return "macos"
    elif IS_LINUX:
        return "linux"
    else:
        return "unknown"


# Lazy import platform-specific implementations
_platform_modules_cache = {}


def _import_platform_module(module_name):
    """Dynamically import platform-specific module by name."""
    platform_name = get_platform()
    cache_key = f"{platform_name}:{module_name}"

    if cache_key in _platform_modules_cache:
        return _platform_modules_cache[cache_key]

    module_path = f"pastemd.platforms.{platform_name}.{module_name}"
    try:
        module = importlib.import_module(module_path)
        _platform_modules_cache[cache_key] = module
        return module
    except ImportError as e:
        raise ImportError(f"Failed to import platform-specific module: {module_name} for {platform_name}") from e


def get_app_detector():
    """Get platform-specific application detector."""
    module = _import_platform_module("app_detector")
    return module.get_app_detector()


def get_clipboard_handler():
    """Get platform-specific clipboard handler."""
    module = _import_platform_module("clipboard")
    return module.get_clipboard_handler()


def get_hotkey_manager():
    """Get platform-specific hotkey manager."""
    module = _import_platform_module("hotkey")
    return module.get_hotkey_manager()


def get_notification_handler():
    """Get platform-specific notification handler."""
    module = _import_platform_module("notification")
    return module.get_notification_handler()


def get_document_inserter_factory():
    """Get platform-specific document inserter factory."""
    module = _import_platform_module("document_inserter")
    return module.get_document_inserter_factory()


__all__ = [
    "PLATFORM_TYPE",
    "OS_NAME",
    "IS_WINDOWS",
    "IS_MACOS",
    "IS_LINUX",
    "get_platform",
    "get_app_detector",
    "get_clipboard_handler",
    "get_hotkey_manager",
    "get_notification_handler",
    "get_document_inserter_factory",
]
