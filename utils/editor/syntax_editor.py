# utils/editor/syntax_editor.py

import tkinter as tk
from tkinter import Text
from utils.editor.highlighter_core import setup_syntax_tags, highlight_syntax, schedule_syntax_highlight

class SyntaxText(Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<<Modified>>", self._on_editor_modified)
        self._highlight_job = None
        self._last_highlighted_text = ""
        self.current_file = None
        self._setup_context_menu()

        self.configure(undo=True, maxundo=-1, autoseparators=True)
        self.after(100, self.setup_syntax_tags)  # отложено на запуск

    def _on_editor_modified(self, event=None):
        if self.edit_modified():
            schedule_syntax_highlight(self)
            self.edit_modified(False)

    def setup_syntax_tags(self):
        setup_syntax_tags(self)

    def highlight_syntax(self):
        highlight_syntax(self)

    def update_theme(self):
        """Обновляет тему редактора и подсветку"""
        from core.theme_manager import ThemeManager
        ThemeManager().apply_editor_theme(self.master)
        self.setup_syntax_tags()
        self.highlight_syntax()

    def _setup_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Копировать", command=lambda: self.event_generate("<<Copy>>"))
        self.menu.add_command(label="Вставить", command=lambda: self.event_generate("<<Paste>>"))
        self.menu.add_command(label="Вырезать", command=lambda: self.event_generate("<<Cut>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Выделить всё", command=lambda: self.event_generate("<<SelectAll>>"))

        self.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

