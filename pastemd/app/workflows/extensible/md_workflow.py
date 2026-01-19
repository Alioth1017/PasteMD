# -*- coding: utf-8 -*-
"""Markdown paste workflow for note-taking apps."""

from .extensible_base import ExtensibleWorkflow
from ....core.errors import ClipboardError
from ....utils.clipboard import (
    get_clipboard_html,
    get_clipboard_text,
    is_clipboard_empty,
)
from ....utils.html_analyzer import is_plain_html_fragment
from ....i18n import t
from ....service.paste import PlainTextPastePlacer


class MdWorkflow(ExtensibleWorkflow):
    """Markdown 粘贴工作流

    适用于原生 Markdown 编辑器：
    - 读取剪贴板 HTML/Markdown
    - 如果是 HTML 则转换为 Markdown
    - 使用 PlainTextPastePlacer 粘贴
    """

    def __init__(self):
        super().__init__()
        self.placer = PlainTextPastePlacer()

    @property
    def workflow_key(self) -> str:
        return "md"
    
    def execute(self) -> None:
        """执行 Markdown 粘贴工作流"""
        try:
            # 1. 读取剪贴板内容
            content_type, content = self._read_clipboard()
            self._log(f"MD workflow: content_type={content_type}")
            
            # 2. 转换为 Markdown（如果是 HTML）
            if content_type == "html":
                content = self.html_preprocessor.process(content, self.config)
                md_text = self.doc_generator.convert_html_to_markdown_text(
                    content, self.config
                )
            else:
                md_text = content
            
            # 3. 预处理 Markdown
            md_text = self.markdown_preprocessor.process(md_text, self.config)

            # 4. 使用粘贴落地器
            result = self.placer.place(
                content=md_text,
                config=self.config,
            )

            if result.success:
                self._notify_success(t("workflow.md.paste_success"))
            else:
                self._notify_error(result.error or t("workflow.generic.failure"))

        except ClipboardError as e:
            self._log(f"Clipboard error: {e}")
            self._notify_error(t("workflow.clipboard.read_failed"))
        except Exception as e:
            self._log(f"MD workflow failed: {e}")
            import traceback
            traceback.print_exc()
            self._notify_error(t("workflow.generic.failure"))
    
    def _read_clipboard(self) -> tuple[str, str]:
        """读取剪贴板内容，返回 (类型, 内容)"""
        # 优先尝试 HTML
        try:
            html = get_clipboard_html(self.config)
            if not is_plain_html_fragment(html):
                return ("html", html)
        except ClipboardError:
            pass
        
        # 尝试纯文本
        if not is_clipboard_empty():
            return ("markdown", get_clipboard_text())
        
        raise ClipboardError("剪贴板为空或无有效内容")
