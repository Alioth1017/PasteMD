"""macOS notification handler using AppKit."""

from ..base import NotificationHandler

try:
    from AppKit import NSUserNotification, NSUserNotificationCenter
    _APPKIT_OK = True
except ImportError:
    _APPKIT_OK = False


class MacOSNotificationHandler(NotificationHandler):
    """macOS notification handler with AppKit native Notification Center."""

    def notify(self, title: str, message: str, timeout: int = 5, ok: bool = True) -> None:
        """Show a notification on macOS."""
        if _APPKIT_OK:
            try:
                self._show_appkit_notification(title, message)
            except Exception as e:
                # Silent fail or log to console
                print(f"Notification failed: {e}")
        else:
            # AppKit not available
            print(f"Notification: {title} - {message}")

    def _show_appkit_notification(self, title: str, message: str) -> None:
        """Show notification using AppKit NSUserNotification."""
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)
        notification.setHasActionButton_(False)
        
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)


def get_notification_handler():
    return MacOSNotificationHandler()


__all__ = ["MacOSNotificationHandler", "get_notification_handler"]