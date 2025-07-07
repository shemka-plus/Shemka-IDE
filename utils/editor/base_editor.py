import tkinter as tk

class BaseEditor(tk.Text):
    def _setup_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Копировать", command=lambda: self.event_generate("<<Copy>>"))
        self.menu.add_command(label="Вставить", command=lambda: self.event_generate("<<Paste>>"))
        self.menu.add_command(label="Вырезать", command=lambda: self.event_generate("<<Cut>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Отменить", command=lambda: self.event_generate("<<Undo>>"))
        self.menu.add_command(label="Повторить", command=lambda: self.event_generate("<<Redo>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Выделить всё", command=lambda: self.event_generate("<<SelectAll>>"))

        self.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _bind_shortcuts(self):
        self.bind("<Control-c>", lambda e: self.event_generate("<<Copy>>"))
        self.bind("<Control-v>", lambda e: self.event_generate("<<Paste>>"))
        self.bind("<Control-x>", lambda e: self.event_generate("<<Cut>>"))
        self.bind("<Control-a>", lambda e: self.event_generate("<<SelectAll>>"))
        self.bind("<Control-z>", lambda e: self.event_generate("<<Undo>>"))
        self.bind("<Control-y>", lambda e: self.event_generate("<<Redo>>"))
        self.bind("<Key>", self._handle_shortcuts_by_keycode)

    def _handle_shortcuts_by_keycode(self, event):
        keycode = event.keycode
        if event.state & 0x4:  # Ctrl
            if keycode == 67:  # C
                self.event_generate("<<Copy>>")
                return "break"
            elif keycode == 86:  # V
                self.event_generate("<<Paste>>")
                return "break"
            elif keycode == 88:  # X
                self.event_generate("<<Cut>>")
                return "break"
            elif keycode == 65:  # A
                self.event_generate("<<SelectAll>>")
                return "break"
            elif keycode == 90:  # Z
                self.event_generate("<<Undo>>")
                return "break"
            elif keycode == 89:  # Y
                self.event_generate("<<Redo>>")
                return "break"
        # Не Ctrl — не мешаем вводу
        return None

