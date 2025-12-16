"""macOS application detector using AppKit and ScriptingBridge."""

from typing import Optional
from ..base import AppDetector

try:
    from AppKit import NSWorkspace
except ImportError:
    NSWorkspace = None

try:
    import subprocess
except ImportError:
    subprocess = None


class MacOSAppDetector(AppDetector):
    """macOS application detector using NSWorkspace."""

    def __init__(self):
        self._workspace = NSWorkspace.sharedWorkspace() if NSWorkspace else None

    def _get_frontmost_app_info(self) -> tuple[Optional[str], Optional[str]]:
        """
        获取最前端应用的信息
        
        Returns:
            (bundle_id, app_name) 或 (None, None)
        """
        if not self._workspace:
            return None, None
        
        try:
            frontmost_app = self._workspace.frontmostApplication()
            bundle_id = frontmost_app.bundleIdentifier()
            app_name = frontmost_app.localizedName()
            return bundle_id, app_name
        except Exception:
            return None, None

    def _get_active_window_title(self) -> Optional[str]:
        """
        使用 AppleScript 获取当前活动窗口标题
        
        Returns:
            窗口标题或 None
        """
        if not subprocess:
            return None
        
        try:
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set windowTitle to name of front window of frontApp
                return windowTitle
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def detect_active_app(self) -> str:
        """
        检测当前活跃的插入目标应用
        
        Returns:
            "word", "excel" 或空字符串
            注: macOS 上暂不区分 WPS，统一映射到 word/excel
        """
        bundle_id, app_name = self._get_frontmost_app_info()
        
        if not bundle_id:
            return ""
        
        # 记录检测到的应用信息
        try:
            from ...utils.app_logging import log
            log(f"macOS frontmost app: {app_name} ({bundle_id})")
        except Exception:
            pass
        
        # Microsoft Word
        if "microsoft.word" in bundle_id.lower():
            return "word"
        
        # Microsoft Excel
        if "microsoft.excel" in bundle_id.lower():
            return "excel"
        
        # WPS Office (如果有 macOS 版本)
        if "wps" in bundle_id.lower() or (app_name and "wps" in app_name.lower()):
            # 尝试通过窗口标题区分 WPS 类型
            window_title = self._get_active_window_title()
            if window_title:
                # 检查是否为表格应用
                excel_indicators = [".xls", ".xlsx", ".csv", "表格", "spreadsheet"]
                for indicator in excel_indicators:
                    if indicator in window_title.lower():
                        return "excel"
                
                # 检查是否为文字处理应用
                word_indicators = [".doc", ".docx", "文字", "writer"]
                for indicator in word_indicators:
                    if indicator in window_title.lower():
                        return "word"
            
            # 默认返回 word
            return "word"
        
        # Apple Pages (可选：作为 Word 的替代)
        if "apple.iwork.pages" in bundle_id.lower():
            return "word"
        
        # Apple Numbers (可选：作为 Excel 的替代)
        if "apple.iwork.numbers" in bundle_id.lower():
            return "excel"
        
        return ""

    def is_word_like_app_available(self) -> bool:
        """检查是否有 Word 类应用在运行"""
        if not self._workspace:
            return False
        
        try:
            running_apps = self._workspace.runningApplications()
            word_bundle_ids = [
                "com.microsoft.word",
                "com.kingsoft.wps",
                "com.apple.iwork.pages"
            ]
            
            for app in running_apps:
                bundle_id = app.bundleIdentifier()
                if bundle_id and any(wid in bundle_id.lower() for wid in word_bundle_ids):
                    return True
        except Exception:
            pass
        return False

    def is_excel_like_app_available(self) -> bool:
        """检查是否有 Excel 类应用在运行"""
        if not self._workspace:
            return False
        
        try:
            running_apps = self._workspace.runningApplications()
            excel_bundle_ids = [
                "com.microsoft.excel",
                "com.kingsoft.wps",
                "com.apple.iwork.numbers"
            ]
            
            for app in running_apps:
                bundle_id = app.bundleIdentifier()
                if bundle_id and any(eid in bundle_id.lower() for eid in excel_bundle_ids):
                    return True
        except Exception:
            pass
        return False


def get_app_detector():
    return MacOSAppDetector()


__all__ = ["MacOSAppDetector", "get_app_detector"]
