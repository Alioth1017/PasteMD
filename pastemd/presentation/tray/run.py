"""Tray icon runner."""

import pystray

from ...core.state import app_state
from ...utils.app_logging import log
from .icon import create_status_icon
from .menu import TrayMenuManager


class TrayRunner:
    """托盘运行器"""
    
    def __init__(self, menu_manager: TrayMenuManager):
        self.menu_manager = menu_manager
    
    def run(self, app_name: str = "PasteMD") -> None:
        """启动托盘图标"""
        log("TrayRunner: creating status icon")
        tray_icon = create_status_icon(ok=True)
        
        log("TrayRunner: building pystray icon")
        icon = pystray.Icon(
            app_name,
            tray_icon,
            app_name,
            self.menu_manager.build_menu()
        )
        
        # 保存图标实例到全局状态
        app_state.icon = icon
        
        log("TrayRunner: entering icon.run (blocking)")
        icon.run()
        log("TrayRunner: icon.run returned")
