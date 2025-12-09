"""Settings configuration dialog."""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, Dict, Any

from ...utils.logging import log
from ...utils.win32 import get_dpi_scale
from ...utils.resources import resource_path
from ...i18n import t, iter_languages, get_language_label
from ...core.state import app_state
from ...config.loader import ConfigLoader


class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, on_save: Callable[[], None], on_close: Optional[Callable[[], None]] = None):
        """
        初始化设置对话框
        
        Args:
            on_save: 保存回调函数
            on_close: 关闭回调函数
        """
        self.on_save_callback = on_save
        self.on_close_callback = on_close
        self.config_loader = ConfigLoader()
        
        # 加载当前配置的副本，避免直接修改 app_state
        self.current_config = app_state.config.copy()
        
        if app_state.root:
            self.root = tk.Toplevel(app_state.root)
        else:
            self.root = tk.Tk()
            
        self.root.title(t("settings.dialog.title"))
        
        # 设置图标
        try:
            icon_path = resource_path("assets/icons/logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            log(f"Failed to set settings dialog icon: {e}")
        
        # 适配高分屏
        scale = get_dpi_scale()
        width = int(600 * scale)
        height = int(500 * scale)
        self.root.geometry(f"{width}x{height}")
        
        # 设置关闭窗口时的处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 窗口居中
        self._center_window()
        
        # 创建UI组件
        self._create_widgets()
        
    def _center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        """创建UI组件"""
        # 创建 Notebook (选项卡容器)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建选项卡
        self._create_general_tab()
        self._create_conversion_tab()
        self._create_advanced_tab()
        self._create_experimental_tab()
        
        # 底部按钮栏
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        cancel_btn = ttk.Button(
            button_frame,
            text=t("settings.buttons.cancel"),
            command=self._on_cancel,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = ttk.Button(
            button_frame,
            text=t("settings.buttons.save"),
            command=self._on_save,
            width=10
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

    def _create_general_tab(self):
        """创建常规设置选项卡"""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text=t("settings.tab.general"))
        
        # 语言设置
        ttk.Label(frame, text=t("settings.general.language")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.lang_var = tk.StringVar(value=self.current_config.get("language", "zh"))
        lang_combo = ttk.Combobox(frame, textvariable=self.lang_var, state="readonly")
        
        # 构建语言列表
        langs = []
        lang_codes = []
        for code, label in iter_languages():
            langs.append(label)
            lang_codes.append(code)
        
        lang_combo['values'] = langs
        
        # 设置当前选中的语言
        current_lang_code = self.current_config.get("language", "zh")
        try:
            current_index = lang_codes.index(current_lang_code)
            lang_combo.current(current_index)
        except ValueError:
            lang_combo.current(0)
            
        # 绑定选择事件，将显示名称映射回代码
        def on_lang_select(event):
            selected_idx = lang_combo.current()
            if selected_idx >= 0:
                self.lang_var.set(lang_codes[selected_idx])
                
        lang_combo.bind("<<ComboboxSelected>>", on_lang_select)
        lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 保存目录
        ttk.Label(frame, text=t("settings.general.save_dir")).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.save_dir_var = tk.StringVar(value=self.current_config.get("save_dir", ""))
        ttk.Entry(frame, textvariable=self.save_dir_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(frame, text=t("settings.general.browse"), command=self._browse_save_dir).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 复选框选项
        self.keep_file_var = tk.BooleanVar(value=self.current_config.get("keep_file", False))
        ttk.Checkbutton(frame, text=t("settings.general.keep_file"), variable=self.keep_file_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.notify_var = tk.BooleanVar(value=self.current_config.get("notify", True))
        ttk.Checkbutton(frame, text=t("settings.general.notify"), variable=self.notify_var).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.auto_open_var = tk.BooleanVar(value=self.current_config.get("auto_open_on_no_app", True))
        ttk.Checkbutton(frame, text=t("settings.general.auto_open"), variable=self.auto_open_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.move_cursor_var = tk.BooleanVar(value=self.current_config.get("move_cursor_to_end", True))
        ttk.Checkbutton(frame, text=t("settings.general.move_cursor"), variable=self.move_cursor_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)

    def _create_conversion_tab(self):
        """创建转换设置选项卡"""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text=t("settings.tab.conversion"))
        
        # Pandoc 路径
        ttk.Label(frame, text=t("settings.conversion.pandoc_path")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pandoc_path_var = tk.StringVar(value=self.current_config.get("pandoc_path", "pandoc"))
        ttk.Entry(frame, textvariable=self.pandoc_path_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(frame, text=t("settings.general.browse"), command=self._browse_pandoc).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Reference Docx
        ttk.Label(frame, text=t("settings.conversion.reference_docx")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ref_docx = self.current_config.get("reference_docx")
        self.ref_docx_var = tk.StringVar(value=ref_docx if ref_docx else "")
        ttk.Entry(frame, textvariable=self.ref_docx_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(frame, text=t("settings.general.browse"), command=self._browse_ref_docx).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # HTML 格式化
        ttk.Label(frame, text=t("settings.conversion.html_formatting"), font=("", 10, "bold")).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        html_fmt = self.current_config.get("html_formatting", {})
        self.strikethrough_var = tk.BooleanVar(value=html_fmt.get("strikethrough_to_del", True))
        ttk.Checkbutton(frame, text=t("settings.conversion.strikethrough"), variable=self.strikethrough_var).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # 其他转换选项
        self.md_indent_var = tk.BooleanVar(value=self.current_config.get("md_disable_first_para_indent", True))
        ttk.Checkbutton(frame, text=t("settings.conversion.md_indent"), variable=self.md_indent_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        self.html_indent_var = tk.BooleanVar(value=self.current_config.get("html_disable_first_para_indent", True))
        ttk.Checkbutton(frame, text=t("settings.conversion.html_indent"), variable=self.html_indent_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=2)

    def _create_advanced_tab(self):
        """创建高级设置选项卡"""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text=t("settings.tab.advanced"))
        
        # Excel 选项
        self.excel_enable_var = tk.BooleanVar(value=self.current_config.get("enable_excel", True))
        ttk.Checkbutton(frame, text=t("settings.advanced.excel_enable"), variable=self.excel_enable_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.excel_format_var = tk.BooleanVar(value=self.current_config.get("excel_keep_format", True))
        ttk.Checkbutton(frame, text=t("settings.advanced.excel_format"), variable=self.excel_format_var).grid(row=1, column=0, sticky=tk.W, pady=5)

    def _create_experimental_tab(self):
        """创建实验性功能选项卡"""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text=t("settings.tab.experimental"))
        
        self.keep_formula_var = tk.BooleanVar(value=self.current_config.get("Keep_original_formula", False))
        ttk.Checkbutton(frame, text=t("settings.conversion.keep_formula"), variable=self.keep_formula_var).grid(row=0, column=0, sticky=tk.W, pady=5)

    def _browse_save_dir(self):
        path = filedialog.askdirectory(initialdir=os.path.expandvars(self.save_dir_var.get()))
        if path:
            self.save_dir_var.set(path)

    def _browse_pandoc(self):
        path = filedialog.askopenfilename(
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.pandoc_path_var.get()) if self.pandoc_path_var.get() else None
        )
        if path:
            self.pandoc_path_var.set(path)

    def _browse_ref_docx(self):
        path = filedialog.askopenfilename(
            filetypes=[("Word Document", "*.docx"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.ref_docx_var.get()) if self.ref_docx_var.get() else None
        )
        if path:
            self.ref_docx_var.set(path)

    def _on_save(self):
        """保存配置"""
        try:
            # 更新配置字典
            new_config = self.current_config.copy()
            
            new_config["language"] = self.lang_var.get()
            new_config["save_dir"] = self.save_dir_var.get()
            new_config["keep_file"] = self.keep_file_var.get()
            new_config["notify"] = self.notify_var.get()
            new_config["auto_open_on_no_app"] = self.auto_open_var.get()
            new_config["move_cursor_to_end"] = self.move_cursor_var.get()
            
            new_config["pandoc_path"] = self.pandoc_path_var.get()
            ref_docx = self.ref_docx_var.get()
            new_config["reference_docx"] = ref_docx if ref_docx else None
            
            if "html_formatting" not in new_config:
                new_config["html_formatting"] = {}
            new_config["html_formatting"]["strikethrough_to_del"] = self.strikethrough_var.get()
            
            new_config["md_disable_first_para_indent"] = self.md_indent_var.get()
            new_config["html_disable_first_para_indent"] = self.html_indent_var.get()
            new_config["Keep_original_formula"] = self.keep_formula_var.get()
            
            new_config["enable_excel"] = self.excel_enable_var.get()
            new_config["excel_keep_format"] = self.excel_format_var.get()
            
            # 保存到文件
            self.config_loader.save(new_config)
            
            # 更新全局状态
            app_state.config = new_config
            
            # 如果语言改变了，可能需要重启或刷新界面（这里简单处理，回调中处理刷新）
            
            messagebox.showinfo("Success", t("settings.success.saved"))
            
            if self.on_save_callback:
                self.on_save_callback()
                
            self._safe_destroy()
            
        except Exception as e:
            log(f"Failed to save settings: {e}")
            messagebox.showerror("Error", t("settings.error.save_failed", error=str(e)))

    def _on_cancel(self):
        self._safe_destroy()

    def _on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self._safe_destroy()

    def _safe_destroy(self):
        try:
            self.root.destroy()
        except Exception as e:
            log(f"Error destroying settings window: {e}")

    def show(self):
        try:
            if isinstance(self.root, tk.Toplevel):
                self.root.wait_window()
            else:
                self.root.mainloop()
        except Exception as e:
            log(f"Error in settings mainloop: {e}")