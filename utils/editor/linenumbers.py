# utils/editor/linenumbers.py
from tkinter import Text

class LineNumbers(Text):
    def __init__(self, master, text_widget=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(
            state="disabled",
            width=4,
            padx=5,
            pady=5,
            bg="#252526",
            fg="#858585",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 12),
            takefocus=0,
            highlightthickness=0
        )
        self.bind("<MouseWheel>", self._on_mousewheel)
        if self.text_widget is not None:
            self.bind_to_widget()

    def bind_to_widget(self):
        self.text_widget.bind("<Configure>", self._on_configure)
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, event=None):
        self.update_line_numbers()

    def _on_key_release(self, event=None):
        self.update_line_numbers()

    def _on_mousewheel(self, event):
        self.text_widget.yview_scroll(-1 * int(event.delta/120), "units")
        self.yview_moveto(self.text_widget.yview()[0])
        return "break"

    def update_line_numbers(self):
        self.config(state="normal")
        self.delete("1.0", "end")
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        for i in range(1, lines + 1):
            self.insert("end", f"{i}\n")
        self.config(state="disabled")
        self.yview_moveto(self.text_widget.yview()[0])
