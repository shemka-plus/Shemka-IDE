# utils/editor/editor_tab.py
import customtkinter as ctk
from tkinter import StringVar, Menu, Frame, filedialog
from pathlib import Path
import re
import serial.tools.list_ports
from avr.compiler import AVRCompiler
from avr.uploader import AVRUploader
#from utils.editor.base_editor import SyntaxText
from utils.editor.linenumbers import LineNumbers
from utils.editor.highlighting.registry import get_rules_for_extension
from gui.config_manager import ConfigManager
from utils.editor.syntax_editor import SyntaxText
import tkinter as tk

class EditorTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config or ConfigManager()
        self.tools_root = tools_root

        self.compiler = AVRCompiler(avr_tools=self.avr_tools, tools_root=self.tools_root)
        self.uploader = AVRUploader(avr_tools)
        
        self.current_file = None
        self.recent_files = self.config.recent_files
        self.mcu_var = StringVar(value=self.config.config.get("mcu", "ATmega328P"))
        self.com_var = StringVar(value=self.config.config.get("com_port", ""))
        
        self._highlight_job = None
        self._last_highlighted_text = ""

        self._setup_ui()
        self.update_ports()
        
        # Применяем тему сразу при создании
        self._apply_theme()
        
        if self.recent_files:
            last_file = self.recent_files[0]
            if Path(last_file).exists():
                self.load_file(last_file)

    def _setup_ui(self):
        # Верхняя панель с кнопками
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(top_frame, text="Новый", command=self.new_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Открыть", command=self.open_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Сохранить", command=self.save_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Сохранить как", command=self.save_file_as).pack(side="left", padx=5)

        self.recent_menu = Menu(top_frame, tearoff=0)
        self.recent_button = ctk.CTkButton(top_frame, text="История", command=self.show_recent_menu)
        self.recent_button.pack(side="left", padx=5)

        # Область редактора
        editor_container = Frame(self)
        editor_container.pack(fill="both", expand=True, padx=5, pady=0)

        self.line_numbers = LineNumbers(editor_container, width=4)
        self.line_numbers.pack(side="left", fill="y")

        #self.editor = SyntaxText(
        #    editor_container, 
        #    wrap="none", 
        #    font=("Consolas", 12),
        #    undo=True
        #)
        #self.editor = SyntaxText(parent_frame, wrap="none", font=("Consolas", 12))
        self.editor = SyntaxText(editor_container, wrap="none", font=("Consolas", 12), undo=True)
        self.editor.pack(side="left", fill="both", expand=True)

        self.line_numbers.text_widget = self.editor
        self.line_numbers.bind_to_widget()
        self.line_numbers.update_line_numbers()

        # Консоль вывода
        self.console = SyntaxText(self, height=10, font=("Consolas", 10))
        self.console.configure(state="disabled")
        self.console.pack(fill="x", padx=5, pady=5)

        # Нижняя панель управления
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(bottom_frame, text="Микроконтроллер:").pack(side="left", padx=5)
        ctk.CTkOptionMenu(bottom_frame, variable=self.mcu_var, values=list(self.boards.keys())).pack(side="left")

        ctk.CTkLabel(bottom_frame, text="Порт:").pack(side="left", padx=5)
        self.port_menu = ctk.CTkOptionMenu(bottom_frame, variable=self.com_var, values=[])
        self.port_menu.pack(side="left")
        ctk.CTkButton(bottom_frame, text="Обновить", width=30, command=self.update_ports).pack(side="left", padx=5)

        ctk.CTkButton(bottom_frame, text="Прошить", command=self.upload_code).pack(side="right", padx=5)
        ctk.CTkButton(bottom_frame, text="Компилировать", command=self.compile_code).pack(side="right", padx=5)

        # Привязка событий
        #self.editor.bind("<<Modified>>", self._on_editor_modified)
        #self.setup_syntax_tags()

    #def _on_editor_modified(self, event=None):
        #self.schedule_syntax_highlight()

    def _apply_theme(self):
        """Применяет текущую тему и цветовую схему"""
        try:
            # Применяем тему интерфейса
            ctk.set_appearance_mode(self.config.config["theme"])
            ctk.set_default_color_theme(self.config.config["color_theme"])
            
            # Применяем тему редактора
            from core.theme_manager import ThemeManager
            editor_theme = "dark" if self.config.config["theme"] == "dark" else "default"
            ThemeManager().apply_editor_theme(self, editor_theme)
            
            # Обновляем подсветку синтаксиса
            #self.setup_syntax_tags()
            #self.highlight_syntax()
        except Exception as e:
            print(f"Ошибка применения темы: {e}")

    #def setup_syntax_tags(self):
    #    ext = self._get_current_extension()
    #    try:
    #        rules, _ = get_rules_for_extension(ext)
    #        for tag in {t for _, t in rules}:
    #            self.editor.tag_configure(tag)
    #    except Exception as e:
    #        print(f"Ошибка настройки тегов синтаксиса: {e}")

    #def schedule_syntax_highlight(self, event=None):
    #    current_text = self.editor.get("1.0", "end-1c")
    #    if current_text == self._last_highlighted_text:
    #        return
#
    #    if self._highlight_job:
    #        self.after_cancel(self._highlight_job)
    #    self._highlight_job = self.after(100, self.highlight_syntax)

    #def highlight_syntax(self):
    #    try:
    #        current_text = self.editor.get("1.0", "end-1c")
    #        if current_text == self._last_highlighted_text:
    #            return
#
    #        self._last_highlighted_text = current_text
    #        ext = self._get_current_extension()
    #        
    #        try:
    #            rules, _ = get_rules_for_extension(ext)
    #            if not rules:
    #                raise ValueError("Правила подсветки не найдены")
    #        except Exception:
    #            from utils.editor.highlighting.arduino_rules import rules as default_rules
    #            rules = default_rules
#
    #        # Очистка существующих тегов
    #        for tag in self.editor.tag_names():
    #            if tag not in ("sel", "cursor"):
    #                self.editor.tag_remove(tag, "1.0", "end")
#
    #        # Применение подсветки
    #        for pattern, tag in rules:
    #            try:
    #                for match in re.finditer(pattern, current_text, flags=re.MULTILINE | re.DOTALL):
    #                    start = f"1.0+{match.start()}c"
    #                    end = f"1.0+{match.end()}c"
    #                    self.editor.tag_add(tag, start, end)
    #            except re.error:
    #                continue
#
    #        self.editor.edit_modified(False)
    #    except Exception as e:
    #        print(f"Ошибка подсветки синтаксиса: {e}")

    def _get_current_extension(self):
        if hasattr(self, "current_file") and self.current_file:
            return Path(self.current_file).suffix[1:].lower()
        return "cpp"

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def new_file(self):
        self.editor.delete("1.0", "end")
        self.current_file = None
        self.log("Создан новый файл")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Файлы C++", "*.cpp"), ("Файлы Arduino", "*.ino"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.load_file(file_path)

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.config.add_recent_file(self.current_file)
            self.log(f"Файл сохранён: {self.current_file}")
        except Exception as e:
            self.log(f"Ошибка сохранения: {e}")

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cpp",
            filetypes=[("Файлы C++", "*.cpp"), ("Файлы Arduino", "*.ino"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.current_file = path
            self.config.add_recent_file(path)
            self.log(f"Открыт файл: {path}")
            #self.highlight_syntax()
        except Exception as e:
            self.log(f"Ошибка открытия файла: {e}")

    def show_recent_menu(self):
        self.recent_menu.delete(0, 'end')
        for file in self.config.recent_files:
            self.recent_menu.add_command(label=file, command=lambda f=file: self.load_file(f))
        try:
            self.recent_menu.tk_popup(self.recent_button.winfo_rootx(), self.recent_button.winfo_rooty() + 30)
        finally:
            self.recent_menu.grab_release()

    def update_ports(self):
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_menu.configure(values=ports)
            if ports:
                if self.com_var.get() in ports:
                    self.com_var.set(self.com_var.get())
                else:
                    self.com_var.set(ports[0])
        except Exception as e:
            self.log(f"Ошибка обновления портов: {e}")

    def compile_code(self):
        source = self.editor.get("1.0", "end-1c")
        mcu = self.mcu_var.get()

        def callback(success, message, errors=[]):
            self.compile_callback(success, message, errors)

        self.compiler.compile(source, mcu, output_dir="build", callback=callback)

    def compile_callback(self, success, message, errors=[]):
        self.log(message)
        if not success and errors:
            self.highlight_errors(errors)

    def upload_code(self):
        hex_path = Path("build/sketch.hex")
        if not hex_path.exists():
            self.log("HEX-файл не найден. Сначала выполните компиляцию.")
            return

        port = self.com_var.get()
        mcu = self.boards[self.mcu_var.get()]

        def callback(success, message):
            self.upload_callback(success, message)

        self.uploader.upload(str(hex_path), mcu=mcu, port=port, callback=callback)

    def upload_callback(self, success, message):
        self.log(message)

    def highlight_errors(self, errors):
        self.editor.tag_configure("error", background="#FFDDDD")
        for file, line, col, msg in errors:
            if file.endswith("sketch.cpp"):
                pos = f"{line}.{col}"
                self.editor.tag_add("error", f"{pos} linestart", f"{pos} lineend+1c")
                self.editor.see(pos)

    def update_theme(self):
        """Обновляет тему редактора"""
        from core.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.apply_editor_theme(self)
        #self.setup_syntax_tags()
        #self.highlight_syntax()