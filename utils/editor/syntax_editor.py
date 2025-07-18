from utils.editor.base_editor import BaseEditor
from utils.editor.highlighter_core import setup_syntax_tags, highlight_syntax, schedule_syntax_highlight

class SyntaxText(BaseEditor):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self._highlight_job = None
        self._last_highlighted_text = ""
        self.current_file = None

        self.configure(undo=True, maxundo=-1, autoseparators=True)
        self._setup_context_menu()
        self._bind_shortcuts()
        self.after(100, self.setup_syntax_tags)

        self.bind("<<Modified>>", self._on_editor_modified)

    def _on_editor_modified(self, event=None):
        if self.edit_modified():
            schedule_syntax_highlight(self)
            self.edit_modified(False)

    def setup_syntax_tags(self):
        setup_syntax_tags(self)

    def highlight_syntax(self):
        highlight_syntax(self)

    def update_theme(self):
        from core.theme_manager import ThemeManager
        ThemeManager().apply_editor_theme(self.master)
        self.setup_syntax_tags()
        self.highlight_syntax()

    
    def _bind_shortcuts(self):
        # Убираем дублирующие биндинги
        self.bind("<Control-c>", self._handle_copy)
        self.bind("<Control-v>", self._handle_paste)
        self.bind("<Control-x>", self._handle_cut)
        self.bind("<Control-a>", self._handle_select_all)
        self.bind("<Control-z>", self._handle_undo)
        self.bind("<Control-y>", self._handle_redo)

    def _handle_copy(self, event=None):
        self.event_generate("<<Copy>>")
        return "break"  # Предотвращаем дальнейшую обработку

    def _handle_paste(self, event=None):
        self.event_generate("<<Paste>>")
        return "break"

    def _handle_cut(self, event=None):
        self.event_generate("<<Cut>>")
        return "break"

    def _handle_select_all(self, event=None):
        self.event_generate("<<SelectAll>>")
        return "break"

    def _handle_undo(self, event=None):
        self.event_generate("<<Undo>>")
        return "break"

    def _handle_redo(self, event=None):
        self.event_generate("<<Redo>>")
        return "break"