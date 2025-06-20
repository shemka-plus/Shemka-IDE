from tkinter import scrolledtext
from .context_menu import bind_context_menu

class SyntaxText(scrolledtext.ScrolledText):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("undo", True)
        super().__init__(master, **kwargs)
        self._setup_context_menu()
        self._bind_shortcuts()

    def _setup_context_menu(self):
        bind_context_menu(self, {
            "Копировать": lambda: self.event_generate("<<Copy>>"),
            "Вставить": lambda: self.event_generate("<<Paste>>"),
            "Вырезать": lambda: self.event_generate("<<Cut>>"),
            "---": None,
            "Отменить": lambda: self.event_generate("<<Undo>>"),
            "Повторить": lambda: self.event_generate("<<Redo>>"),
            "---": None,
            "Выделить всё": lambda: self.event_generate("<<SelectAll>>"),
        })

    def _bind_shortcuts(self):
        bindings = {
            "<Control-c>": lambda e: self.event_generate("<<Copy>>"),
            "<Control-v>": lambda e: self.event_generate("<<Paste>>"),
            "<Control-x>": lambda e: self.event_generate("<<Cut>>"),
            "<Control-a>": lambda e: self.event_generate("<<SelectAll>>"),
            "<Control-z>": lambda e: self.event_generate("<<Undo>>"),
            "<Control-y>": lambda e: self.event_generate("<<Redo>>"),
        }
        for key, action in bindings.items():
            self.bind(key, action)
