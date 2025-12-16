"""macOS hotkey manager using pynput."""

from typing import Callable, Optional
from ..base import HotkeyManager
# Import here to avoid circular dependency
from ...utils.app_logging import log

try:
    from pynput import keyboard
    _PYNPUT_OK = True
except ImportError:
    _PYNPUT_OK = False


class MacOSHotkeyManager(HotkeyManager):
    """macOS hotkey manager implementation using pynput."""

    def __init__(self):
        self.global_listener: Optional[keyboard.GlobalHotKeys] = None
        self.current_hotkey: Optional[str] = None

    def bind(self, hotkey: str, callback: Callable[[], None]) -> None:
        """Bind a global hotkey (requires Accessibility permissions on macOS)."""
        log(f"[MacOS] Attempting to bind hotkey: {hotkey}")
        self.unbind()
        
        if not _PYNPUT_OK:
            log("[MacOS] ERROR: pynput not available")
            raise RuntimeError("pynput is required for hotkey binding on macOS")
        
        try:
            mapping = {hotkey: callback}
            log(f"[MacOS] Creating GlobalHotKeys with mapping")
            self.global_listener = keyboard.GlobalHotKeys(mapping)
            self.global_listener.daemon = True
            self.global_listener.start()
            self.current_hotkey = hotkey
            log(f"[MacOS] Successfully bound hotkey: {hotkey}")
            log("[MacOS] Note: Accessibility permissions required - check System Settings > Privacy & Security > Accessibility")
        except Exception as e:
            log(f"[MacOS] ERROR binding hotkey: {e}")
            raise RuntimeError(f"Failed to bind hotkey {hotkey}: {e}")

    def unbind(self) -> None:
        """Unbind current hotkey."""
        if self.global_listener:
            try:
                self.global_listener.stop()
            except Exception:
                pass
            finally:
                self.global_listener = None
                self.current_hotkey = None

    def is_hotkey_available(self, hotkey: str) -> bool:
        """Check if a hotkey is available (simplified check on macOS)."""
        if not _PYNPUT_OK:
            return False
        
        try:
            test_callback = lambda: None
            mapping = {hotkey: test_callback}
            listener = keyboard.GlobalHotKeys(mapping)
            listener.stop()
            return True
        except Exception:
            return False


def get_hotkey_manager():
    return MacOSHotkeyManager()


__all__ = ["MacOSHotkeyManager", "get_hotkey_manager"]