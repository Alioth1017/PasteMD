# -*- coding: utf-8 -*-
"""Extensions tab for settings dialog."""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from ...i18n import t
from ...config.defaults import RESERVED_APPS
from ...utils.logging import log


class ExtensionsTab:
    """扩展设置选项卡
    
    管理可扩展工作流的设置，如 HTML+MD 粘贴。
    """
    
    def __init__(self, notebook: ttk.Notebook, config: dict):
        """
        Args:
            notebook: 父级 Notebook 容器
            config: 当前配置
        """
        self.notebook = notebook
        self.config = config
        self.frame = ttk.Frame(notebook, padding=10)
        
        # 存储应用数据 {iid: {"name": ..., "path": ...}}
        self.app_data: dict[str, dict] = {}
        
        # 图标缓存（保持引用避免垃圾回收）
        self._icons: list = []
        
        self._create_widgets()
        notebook.add(self.frame, text=t("settings.tab.extensions"))
    
    def _create_widgets(self):
        """创建 UI 组件"""
        self.frame.columnconfigure(1, weight=1)
        
        # HTML+MD 工作流配置
        ext_config = self.config.get("extensible_workflows", {})
        html_md_config = ext_config.get("html_md", {})
        
        # 标题
        ttk.Label(
            self.frame, 
            text=t("settings.extensions.html_md_title"),
            font=("", 11, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 启用开关
        self.html_md_enabled_var = tk.BooleanVar(
            value=html_md_config.get("enabled", True)
        )
        ttk.Checkbutton(
            self.frame, 
            text=t("settings.extensions.html_md_enable"),
            variable=self.html_md_enabled_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 应用列表标签
        ttk.Label(
            self.frame, 
            text=t("settings.extensions.app_list")
        ).grid(row=2, column=0, sticky=tk.NW, pady=5)
        
        # 应用列表 + 增删按钮
        self._create_app_listbox(html_md_config.get("apps", []))
        
        # 公式格式开关
        self.keep_latex_var = tk.BooleanVar(
            value=html_md_config.get("keep_formula_latex", True)
        )
        ttk.Checkbutton(
            self.frame, 
            text=t("settings.extensions.keep_latex"),
            variable=self.keep_latex_var
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # 说明文字
        ttk.Label(
            self.frame,
            text=t("settings.extensions.description"),
            foreground="gray",
            wraplength=400
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def _create_app_listbox(self, initial_apps: list):
        """创建带增删按钮的应用列表（Treeview 支持图标）"""
        list_frame = ttk.Frame(self.frame)
        list_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)
        list_frame.columnconfigure(0, weight=1)
        
        # Treeview
        columns = ("name",)
        self.app_treeview = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="tree headings",
            height=5
        )
        self.app_treeview.heading("#0", text="")
        self.app_treeview.heading("name", text=t("settings.extensions.app_name"))
        self.app_treeview.column("#0", width=30, stretch=False)
        self.app_treeview.column("name", width=200)
        
        # 加载已保存的应用
        for app in initial_apps:
            if isinstance(app, dict):
                name = app.get("name", "")
                path = app.get("path", "")
            else:
                name = str(app)
                path = ""
            
            icon = self._extract_icon(path) if path else None
            iid = self.app_treeview.insert("", tk.END, values=(name,), image=icon or "")
            self.app_data[iid] = {"name": name, "path": path}
        
        self.app_treeview.grid(row=0, column=0, sticky=tk.EW)
        
        # 按钮栏
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=0, column=1, sticky=tk.N, padx=(5, 0))
        
        ttk.Button(
            btn_frame, 
            text="+", 
            command=self._add_app, 
            width=3
        ).pack(pady=2)
        
        ttk.Button(
            btn_frame, 
            text="-", 
            command=self._remove_app, 
            width=3
        ).pack(pady=2)
    
    def _add_app(self):
        """添加应用（平台特定）"""
        if sys.platform == "darwin":
            self._add_app_macos()
        elif sys.platform == "win32":
            self._add_app_windows()
        else:
            messagebox.showinfo(
                t("settings.title.info"),
                t("settings.extensions.unsupported_platform")
            )
    
    def _add_app_macos(self):
        """macOS: 使用原生对话框选择 .app"""
        try:
            from AppKit import NSOpenPanel, NSApplication, NSURL
            
            # 创建原生打开面板
            panel = NSOpenPanel.openPanel()
            panel.setTitle_(t("settings.extensions.select_app"))
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setDirectoryURL_(NSURL.fileURLWithPath_("/Applications"))
            panel.setAllowedFileTypes_(["app"])
            
            # 显示面板
            result = panel.runModal()
            
            if result == 1:  # NSModalResponseOK
                url = panel.URL()
                if url:
                    path = url.path()
                    app_name = os.path.basename(path).replace(".app", "")
                    icon = self._extract_icon(path)
                    self._add_app_to_list(app_name, path, icon)
        except ImportError:
            # 如果 AppKit 不可用，回退到手动输入
            self._add_app_macos_fallback()
        except Exception as e:
            log(f"Failed to open macOS app selector: {e}")
            self._add_app_macos_fallback()
    
    def _add_app_macos_fallback(self):
        """macOS: 回退方案 - 手动输入应用名称"""
        from tkinter import simpledialog
        
        app_name = simpledialog.askstring(
            t("settings.extensions.select_app"),
            t("settings.extensions.enter_app_name"),
            parent=self.frame
        )
        if app_name:
            # 尝试找到应用路径
            app_path = f"/Applications/{app_name}.app"
            if not os.path.exists(app_path):
                app_path = ""
            icon = self._extract_icon(app_path) if app_path else None
            self._add_app_to_list(app_name, app_path, icon)
    
    def _add_app_windows(self):
        """Windows: 弹窗显示所有运行中的应用（带图标）供选择"""
        try:
            from ...utils.win32.window import get_running_apps
        except ImportError:
            messagebox.showerror(
                t("settings.title.error"),
                t("settings.extensions.win32_import_error")
            )
            return
        
        running_apps = get_running_apps()
        
        # 过滤保留应用
        apps_with_icons = []
        for app in running_apps:
            if app["name"].lower() not in RESERVED_APPS:
                app["icon"] = self._extract_icon(app.get("exe_path", ""))
                apps_with_icons.append(app)
        
        if not apps_with_icons:
            messagebox.showinfo(
                t("settings.title.info"), 
                t("settings.extensions.no_running_apps")
            )
            return
        
        selected = self._show_windows_app_selector(apps_with_icons)
        if selected:
            self._add_app_to_list(
                selected["name"], 
                selected.get("exe_path", ""), 
                selected.get("icon")
            )
    
    def _show_windows_app_selector(self, apps: list) -> Optional[dict]:
        """显示带图标的应用选择对话框"""
        dialog = tk.Toplevel(self.frame)
        dialog.title(t("settings.extensions.select_app"))
        dialog.transient(self.frame)
        dialog.grab_set()
        dialog.geometry("300x400")
        
        # Treeview
        tree = ttk.Treeview(dialog, columns=("name",), show="tree", height=15)
        tree.heading("#0", text="")
        tree.column("#0", width=30, stretch=False)
        tree.column("name", width=250)
        
        for app in apps:
            tree.insert("", tk.END, values=(app["name"],), image=app.get("icon") or "")
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        selected = [None]
        
        def on_select():
            sel = tree.selection()
            if sel:
                idx = tree.index(sel[0])
                selected[0] = apps[idx]
            dialog.destroy()
        
        ttk.Button(
            dialog, 
            text=t("settings.buttons.select"), 
            command=on_select
        ).pack(pady=10)
        
        dialog.wait_window()
        return selected[0]
    
    def _add_app_to_list(self, app_name: str, app_path: str, icon=None):
        """将应用添加到列表"""
        if app_name.lower() in RESERVED_APPS:
            messagebox.showerror(
                t("settings.title.error"), 
                t("settings.extensions.reserved_app_error", app=app_name)
            )
            return
        
        # 检查是否已存在
        existing = [self.app_data[iid]["name"] for iid in self.app_treeview.get_children()]
        if app_name in existing:
            messagebox.showinfo(
                t("settings.title.info"),
                t("settings.extensions.app_exists", app=app_name)
            )
            return
        
        iid = self.app_treeview.insert("", tk.END, values=(app_name,), image=icon or "")
        self.app_data[iid] = {"name": app_name, "path": app_path}
    
    def _extract_icon(self, path: str):
        """提取应用图标（平台特定）"""
        if not path:
            return None
        
        if sys.platform == "darwin":
            return self._extract_macos_icon(path)
        elif sys.platform == "win32":
            return self._extract_windows_icon(path)
        return None
    
    def _extract_macos_icon(self, app_path: str):
        """macOS: 从 .app 提取图标"""
        try:
            from AppKit import NSWorkspace, NSBitmapImageRep, NSPNGFileType, NSImage
            from PIL import Image, ImageTk
            import io
            
            ws = NSWorkspace.sharedWorkspace()
            ns_icon = ws.iconForFile_(app_path)
            
            if ns_icon:
                # 目标尺寸
                size = 16
                
                # 创建目标尺寸的新图像
                new_image = NSImage.alloc().initWithSize_((size, size))
                new_image.lockFocus()
                
                # 在新尺寸中绘制原图标
                ns_icon.drawInRect_fromRect_operation_fraction_(
                    ((0, 0), (size, size)),
                    ((0, 0), ns_icon.size()),
                    2,  # NSCompositeSourceOver
                    1.0
                )
                
                # 获取位图表示
                bitmap_rep = NSBitmapImageRep.alloc().initWithFocusedViewRect_(
                    ((0, 0), (size, size))
                )
                new_image.unlockFocus()
                
                if bitmap_rep:
                    # 转换为 PNG 数据
                    png_data = bitmap_rep.representationUsingType_properties_(
                        NSPNGFileType, None
                    )
                    if png_data:
                        # 使用 PIL 加载并确保尺寸
                        img = Image.open(io.BytesIO(bytes(png_data)))
                        img = img.resize((size, size), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self._icons.append(photo)  # 保持引用
                        return photo
        except Exception as e:
            log(f"Failed to extract macOS icon: {e}")
        return None
    
    def _extract_windows_icon(self, exe_path: str):
        """Windows: 从 .exe 提取图标"""
        try:
            import win32gui
            import win32con
            import win32ui
            from PIL import Image
            
            # 提取图标
            ico_x = win32gui.ExtractIcon(0, exe_path, 0)
            if ico_x:
                # 创建设备上下文
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, 16, 16)
                
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(hbmp)
                hdc_mem.DrawIcon((0, 0), ico_x)
                
                # 转换为 PIL Image
                bmpinfo = hbmp.GetInfo()
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGBA',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRA', 0, 1
                )
                
                # 清理
                win32gui.DestroyIcon(ico_x)
                hdc_mem.DeleteDC()
                hdc.DeleteDC()
                
                # 转换为 PhotoImage
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img)
                self._icons.append(photo)  # 保持引用
                return photo
        except Exception as e:
            log(f"Failed to extract Windows icon: {e}")
        return None
    
    def _remove_app(self):
        """移除选中的应用"""
        selection = self.app_treeview.selection()
        if selection:
            iid = selection[0]
            if iid in self.app_data:
                del self.app_data[iid]
            self.app_treeview.delete(iid)
    
    def get_config(self) -> dict:
        """获取当前配置"""
        # 返回 apps 列表，每个元素包含 name 和 path
        apps = [self.app_data[iid] for iid in self.app_treeview.get_children()]
        return {
            "html_md": {
                "enabled": self.html_md_enabled_var.get(),
                "apps": apps,
                "keep_formula_latex": self.keep_latex_var.get(),
            }
        }
