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
        # Оставляем только основные биндинги
        self.bind("<Key>", self._handle_shortcuts_by_keycode)

    def _handle_shortcuts_by_keycode(self, event):
        # Обрабатываем только специальные комбинации
        if event.state & 0x4:  # Ctrl
            if event.keycode == 67:  # C
                return self._handle_copy()
            elif event.keycode == 86:  # V
                return self._handle_paste()
            elif event.keycode == 88:  # X
                return self._handle_cut()
            elif event.keycode == 65:  # A
                return self._handle_select_all()
            elif event.keycode == 90:  # Z
                return self._handle_undo()
            elif event.keycode == 89:  # Y
                return self._handle_redo()
        return None
