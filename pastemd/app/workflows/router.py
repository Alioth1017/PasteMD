"""Workflow router - main entry point."""

from ...core.state import app_state
from ...utils.detector import detect_active_app
from ...utils.logging import log
from ...service.notification.manager import NotificationManager
from ...i18n import t

from .word import WordWorkflow, WPSWorkflow
from .excel import ExcelWorkflow, WPSExcelWorkflow
from .fallback import FallbackWorkflow
from .extensible import HtmlMdWorkflow


class WorkflowRouter:
    """工作流路由器（单例）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        
        # 核心工作流（不可配置）
        self.core_workflows = {
            "word": WordWorkflow(),
            "wps": WPSWorkflow(),
            "excel": ExcelWorkflow(),
            "wps_excel": WPSExcelWorkflow(),
            "": FallbackWorkflow(),  # 空字符串表示无应用/兜底
        }
        
        # 可扩展工作流注册表
        self.extensible_registry = {
            "html_md": HtmlMdWorkflow(),
        }
        
        self.notification_manager = NotificationManager()
        self._initialized = True
        log("WorkflowRouter initialized")
    
    def _build_dynamic_routes(self) -> dict:
        """根据配置动态构建路由表"""
        routes = dict(self.core_workflows)
        
        ext_config = app_state.config.get("extensible_workflows", {})
        for key, workflow in self.extensible_registry.items():
            cfg = ext_config.get(key, {})
            if cfg.get("enabled", False):
                # apps 是 [{"name": ..., "path": ...}, ...] 格式
                for app in cfg.get("apps", []):
                    app_name = app.get("name") if isinstance(app, dict) else app
                    if app_name and app_name not in routes:
                        routes[app_name] = workflow
                        log(f"Registered extensible route: {app_name} -> {key}")
        
        return routes
    
    def route(self) -> None:
        """主入口：检测应用 → 路由到工作流"""
        try:
            # 检测目标应用
            target_app = detect_active_app()
            log(f"Detected target app: {target_app}")
            
            # 动态构建路由表并路由
            routes = self._build_dynamic_routes()
            workflow = routes.get(target_app, routes[""])
            workflow.execute()
        
        except Exception as e:
            log(f"Router failed: {e}")
            import traceback
            traceback.print_exc()
            self.notification_manager.notify("PasteMD", t("workflow.generic.failure"), ok=False)


# 全局单例
router = WorkflowRouter()


def execute_paste_workflow():
    """热键入口函数"""
    router.route()

