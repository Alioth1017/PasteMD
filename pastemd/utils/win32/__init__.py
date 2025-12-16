"""Windows platform utilities (lazy imports to avoid import errors on non-Windows platforms)."""

import sys

def __getattr__(name):
    """Lazy import for Windows-specific modules."""
    if sys.platform != 'win32':
        # 非 Windows 平台返回空实现
        if name == 'cleanup_background_wps_processes':
            return lambda: None
        elif name == 'HotkeyChecker':
            class _DummyHotkeyChecker:
                def __init__(self, *args, **kwargs):
                    pass
                def is_available(self, *args, **kwargs):
                    return False
                @staticmethod
                def validate_hotkey_string(hotkey_str):
                    """Dummy validation - always returns None (no error)."""
                    return None
            return _DummyHotkeyChecker
        elif name == 'set_dpi_awareness':
            return lambda: None
        elif name == 'get_dpi_scale':
            return lambda: 1.0
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    # Windows 平台惰性导入
    if name == 'cleanup_background_wps_processes':
        from .window import cleanup_background_wps_processes
        return cleanup_background_wps_processes
    elif name == 'HotkeyChecker':
        from .hotkey_checker import HotkeyChecker
        return HotkeyChecker
    elif name == 'set_dpi_awareness':
        from .dpi import set_dpi_awareness
        return set_dpi_awareness
    elif name == 'get_dpi_scale':
        from .dpi import get_dpi_scale
        return get_dpi_scale
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['cleanup_background_wps_processes', 'HotkeyChecker', 'set_dpi_awareness', 'get_dpi_scale']
