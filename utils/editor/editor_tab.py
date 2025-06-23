# utils/editor/editor_tab.py
import customtkinter as ctk
from pathlib import Path
from tkinter import StringVar

from .layout import setup_ui
from .actions import compile_code, compile_callback, upload_code, upload_callback
from .file_manager import new_file, open_file, save_file, save_file_as, load_file, show_recent_menu
from .highlighter_core import highlight_syntax, schedule_syntax_highlight, setup_syntax_tags
from .console import log
from .ports import update_ports

from avr.compiler import AVRCompiler
from avr.uploader import AVRUploader

class EditorTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config
        self.tools_root = tools_root

        self.compiler = AVRCompiler(avr_tools=self.avr_tools, tools_root=self.tools_root)
        self.uploader = AVRUploader(avr_tools)

        self.current_file = None
        self.recent_files = config.recent_files
        self.mcu_var = StringVar(value=config.config.get("mcu", "ATmega328P"))
        self.com_var = StringVar(value=config.config.get("com_port", ""))

        self._highlight_job = None
        self._last_highlighted_text = ""

        setup_ui(self)
        update_ports(self)

        if self.recent_files:
            last_file = self.recent_files[0]
            if Path(last_file).exists():
                load_file(self, last_file)

    def _get_current_extension(self):
        if hasattr(self, "current_file") and self.current_file:
            return self.current_file.lower().split(".")[-1]
        return "cpp"  # по умолчанию, если файл не сохранён


    # Связываем методы с текущим классом через делегирование
    compile_code = compile_code
    compile_callback = compile_callback
    upload_code = upload_code
    upload_callback = upload_callback

    new_file = new_file
    open_file = open_file
    save_file = save_file
    save_file_as = save_file_as
    load_file = load_file
    show_recent_menu = show_recent_menu

    highlight_syntax = highlight_syntax
    schedule_syntax_highlight = schedule_syntax_highlight
    setup_syntax_tags = setup_syntax_tags

    log = log
    update_ports = update_ports
