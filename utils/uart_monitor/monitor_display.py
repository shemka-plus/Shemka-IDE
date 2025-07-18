import tkinter as tk
from customtkinter import CTkFrame, CTkScrollbar
from .theme import get_console_theme


class MonitorDisplay(CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.output_text = tk.Text(self, wrap="none", font=("Consolas", 10), state="disabled")
        self.scrollbar = CTkScrollbar(self, orientation="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)

        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def append_text(self, text):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def clear_text(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def update_theme(self):
        theme = get_console_theme()
        self.output_text.configure(
            bg=theme["bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
            selectbackground=theme["selection"]
        )
