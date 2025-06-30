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
            "Удалить выделенное": lambda: self.delete("sel.first", "sel.last"),
            "---": None,
            "Отменить": lambda: self.event_generate("<<Undo>>"),
            "Повторить": lambda: self.event_generate("<<Redo>>"),
            "---": None,
            "Выделить всё": lambda: self.event_generate("<<SelectAll>>"),
        })

    def _bind_shortcuts(self):
        # Основные привязки для английской раскладки
        self.bind("<Control-c>", lambda e: self.event_generate("<<Copy>>"))
        self.bind("<Control-v>", lambda e: self.event_generate("<<Paste>>"))
        self.bind("<Control-x>", lambda e: self.event_generate("<<Cut>>"))
        self.bind("<Control-a>", lambda e: self.event_generate("<<SelectAll>>"))
        self.bind("<Control-z>", lambda e: self.event_generate("<<Undo>>"))
        self.bind("<Control-y>", lambda e: self.event_generate("<<Redo>>"))
        
        # Универсальные привязки по кодам клавиш (работают в любой раскладке)
        self.bind("<Control-Key>", self._handle_shortcuts_by_keycode)

    def _handle_shortcuts_by_keycode(self, event):
        # Коды клавиш для русской раскладки (QWERTY)
        keycode = event.keycode
        if event.state & 0x4:  # Проверяем, что нажат Ctrl
            if keycode == 67:  # C (англ) или С (рус)
                self.event_generate("<<Copy>>")
            elif keycode == 86:  # V (англ) или М (рус)
                self.event_generate("<<Paste>>")
            elif keycode == 88:  # X (англ) или Ч (рус)
                self.event_generate("<<Cut>>")
            elif keycode == 65:  # A (англ) или Ф (рус)
                self.event_generate("<<SelectAll>>")
            elif keycode == 90:  # Z (англ) или Я (рус)
                self.event_generate("<<Undo>>")
            elif keycode == 89:  # Y (англ) или Н (рус)
                self.event_generate("<<Redo>>")
        #print(f"Keycode: {event.keycode}, Keysym: {event.keysym}, Char: {event.char}")
        return "break"
