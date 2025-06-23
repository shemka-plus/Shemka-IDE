# utils/editor/layout.py
import customtkinter as ctk
from tkinter import Frame, Menu
from .linenumbers import LineNumbers
from utils.editor.base_editor import SyntaxText

def setup_ui(self):
    top_frame = ctk.CTkFrame(self)
    top_frame.pack(fill="x", padx=5, pady=5)

    ctk.CTkButton(top_frame, text="Новый", command=self.new_file).pack(side="left", padx=5)
    ctk.CTkButton(top_frame, text="Открыть", command=self.open_file).pack(side="left", padx=5)
    ctk.CTkButton(top_frame, text="Сохранить", command=self.save_file).pack(side="left", padx=5)
    ctk.CTkButton(top_frame, text="Сохранить как", command=self.save_file_as).pack(side="left", padx=5)

    self.recent_menu = Menu(top_frame, tearoff=0)
    self.recent_button = ctk.CTkButton(top_frame, text="История", command=self.show_recent_menu)
    self.recent_button.pack(side="left", padx=5)

    editor_container = Frame(self)
    editor_container.pack(fill="both", expand=True, padx=5, pady=0)

    self.line_numbers = LineNumbers(editor_container, width=4)
    self.line_numbers.pack(side="left", fill="y")

    self.editor = SyntaxText(editor_container, wrap="none", font=("Consolas", 12))
    self.editor.pack(side="left", fill="both", expand=True)

    self.line_numbers.text_widget = self.editor
    self.line_numbers.bind_to_widget()
    self.line_numbers.update_line_numbers()

    self.console = SyntaxText(self, height=10, font=("Consolas", 10))
    self.console.configure(state="disabled")
    self.console.pack(fill="x", padx=5, pady=5)

    bottom_frame = ctk.CTkFrame(self)
    bottom_frame.pack(fill="x", padx=5, pady=5)

    ctk.CTkLabel(bottom_frame, text="МК:").pack(side="left", padx=5)
    ctk.CTkOptionMenu(bottom_frame, variable=self.mcu_var, values=list(self.boards.keys())).pack(side="left")

    ctk.CTkLabel(bottom_frame, text="COM:").pack(side="left", padx=5)
    self.port_menu = ctk.CTkOptionMenu(bottom_frame, variable=self.com_var, values=[])
    self.port_menu.pack(side="left")
    ctk.CTkButton(bottom_frame, text="↻", width=30, command=self.update_ports).pack(side="left", padx=5)

    ctk.CTkButton(bottom_frame, text="Прошить", command=self.upload_code).pack(side="right", padx=5)
    ctk.CTkButton(bottom_frame, text="Компилировать", command=self.compile_code).pack(side="right", padx=5)

    self.editor.bind("<<Modified>>", self.schedule_syntax_highlight)
    self.setup_syntax_tags()