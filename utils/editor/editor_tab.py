import customtkinter as ctk
from tkinter import StringVar, Menu, Frame, filedialog, font as tkfont
from pathlib import Path
#import re
import serial.tools.list_ports
from avr.compiler import AVRCompiler
from avr.uploader import AVRUploader
from utils.editor.linenumbers import LineNumbers
from utils.editor.highlighting.registry import get_rules_for_extension
from gui.config_manager import ConfigManager
from utils.editor.syntax_editor import SyntaxText
from utils.editor.settings_window import EditorSettingsWindow
#import tkinter as tk

class EditorTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config or ConfigManager()
        self.tools_root = tools_root

        self.font_family = "Consolas"
        self.font_size = 12
        
        self.current_file = None
        self.recent_files = self.config.recent_files
        self.mcu_var = StringVar(value=self.config.config.get("mcu", "ATmega328P"))
        self.com_var = StringVar(value=self.config.config.get("com_port", ""))
        
        self._highlight_job = None
        self._last_highlighted_text = ""

        self.compiler = AVRCompiler(avr_tools=self.avr_tools, tools_root=self.tools_root)
        self.uploader = AVRUploader(avr_tools)
        
        self._setup_ui()
        self.update_ports()
        self._apply_theme()
        
        if self.recent_files:
            last_file = self.recent_files[0]
            if Path(last_file).exists():
                self.load_file(last_file)

    def _setup_ui(self):
        # Верхняя панель с меню
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Меню "Файл"
        self.file_menu = Menu(top_frame, tearoff=0)
        self.file_menu.add_command(label="Новый", command=self.new_file)
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить", command=self.save_file)
        self.file_menu.add_command(label="Сохранить как", command=self.save_file_as)
        
        self.file_button = ctk.CTkButton(top_frame, text="Файл", command=self.show_file_menu)
        self.file_button.pack(side="left", padx=5)

        # Меню "История"
        self.recent_menu = Menu(top_frame, tearoff=0)
        self.recent_button = ctk.CTkButton(top_frame, text="История", command=self.show_recent_menu)
        self.recent_button.pack(side="left", padx=5)

        # Кнопка настроек с иконкой ⚙
        self.settings_button = ctk.CTkButton(
            top_frame, 
            text="⚙", 
            width=30,
            command=self.open_settings_window
        )
        self.settings_button.pack(side="left", padx=5)

        # Кнопки компиляции и прошивки
        ctk.CTkButton(top_frame, text="Компилировать", command=self.compile_code).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="Прошить", command=self.upload_code).pack(side="right", padx=5)

        # Область редактора
        editor_container = Frame(self)
        editor_container.pack(fill="both", expand=True, padx=5, pady=0)

        self.line_numbers = LineNumbers(editor_container, width=4)
        self.line_numbers.pack(side="left", fill="y")

        self.editor = SyntaxText(editor_container, wrap="none", font=(self.font_family, self.font_size), undo=True)
        self.editor.pack(side="left", fill="both", expand=True)

        self.line_numbers.text_widget = self.editor
        self.line_numbers.bind_to_widget()
        self.line_numbers.update_line_numbers()

        # Консоль вывода
        self.console = SyntaxText(self, height=10, font=(self.font_family, self.font_size))
        self.console.configure(state="disabled")
        self.console.pack(fill="x", padx=5, pady=5)

    def open_settings_window(self):
        """Открывает окно настроек"""
        if hasattr(self, '_settings_window') and self._settings_window.winfo_exists():
            self._settings_window.lift()
            return
            
        self._settings_window = EditorSettingsWindow(
            self,
            mcu_var=self.mcu_var,
            com_var=self.com_var,
            boards=self.boards,
            font_family=self.font_family,
            font_size=self.font_size
        )
        
        # Ждем закрытия окна и применяем настройки
        self.wait_window(self._settings_window)
        self._apply_font_settings()

    def _apply_font_settings(self):
        """Применяет настройки шрифта"""
        if hasattr(self, '_settings_window'):
            # Создаем новый шрифт
            new_font = (self._settings_window.font_family, self._settings_window.font_size)
            
            # Применяем ко всем элементам
            self.editor.configure(font=new_font)
            self.console.configure(font=new_font)
            self.line_numbers.configure(font=new_font)
            
            # Обновляем нумерацию строк
            self.line_numbers.update_line_numbers()
            
            # Сохраняем новые значения
            self.font_family = self._settings_window.font_family
            self.font_size = self._settings_window.font_size

    def show_file_menu(self):
        try:
            self.file_menu.tk_popup(self.file_button.winfo_rootx(), self.file_button.winfo_rooty() + 30)
        finally:
            self.file_menu.grab_release()

    def show_settings_menu(self):
        try:
            self.settings_menu.tk_popup(self.settings_button.winfo_rootx(), self.settings_button.winfo_rooty() + 30)
        finally:
            self.settings_menu.grab_release()

    def show_mcu_menu(self):
        mcu_menu = Menu(self, tearoff=0)
        for mcu in self.boards.keys():
            mcu_menu.add_command(label=mcu, command=lambda m=mcu: self.mcu_var.set(m))
        
        try:
            mcu_menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            mcu_menu.grab_release()

    def show_port_menu(self):
        self.update_ports()
        port_menu = Menu(self, tearoff=0)
        for port in self.port_menu.cget("values"):
            port_menu.add_command(label=port, command=lambda p=port: self.com_var.set(p))
        
        try:
            port_menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            port_menu.grab_release()

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
            
        except Exception as e:
            print(f"Ошибка применения темы: {e}")

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
            if not ports:
                self.log("Нет доступных COM-портов")
                return False
            return True
        except Exception as e:
            self.log(f"Ошибка обновления портов: {str(e)}")
            return False

    def compile_code(self):
        if not self.update_ports():
            self.log("Проверьте подключение COM-порта перед компиляцией")
            return
            
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