import customtkinter as ctk
from tkinter import StringVar, Menu, Frame, filedialog, font as tkfont
from pathlib import Path
import serial.tools.list_ports
from avr.compiler import AVRCompiler
from avr.uploader import AVRUploader
from utils.editor.linenumbers import LineNumbers
from utils.editor.highlighting.registry import get_rules_for_extension
from gui.config_manager import ConfigManager
from utils.editor.syntax_editor import SyntaxText
from utils.editor.settings_window import EditorSettingsWindow
from utils.ui.tooltip import CTkTooltip
from tkinter import messagebox
from core.compiler_manager import CompilerManager

class EditorTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None, undo=True, autoseparators=True, maxundo=-1):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config or ConfigManager()
        self.tools_root = tools_root

        self.font_family = "Consolas"
        self.font_size = 12

        self.font_family = ctk.StringVar(value=self.config.config.get("font_family", "Consolas"))
        self.font_size = ctk.IntVar(value=self.config.config.get("font_size", 12))
 
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
        # Верхняя панель с кнопками
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", pady=5)

        # Меню "Файл"
        self.file_menu = Menu(top_frame, tearoff=0)
        self.file_menu.add_command(label="Новый", command=self.new_file)
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить", command=self.save_file)
        self.file_menu.add_command(label="Сохранить как", command=self.save_file_as)

        self.file_button = ctk.CTkButton(top_frame, text="📂 Файл ⮟", width=30, command=self.show_file_menu)
        self.file_button.pack(side="left", padx=5)
        CTkTooltip(self.file_button, "Файл")

        # Меню "История"
        self.recent_menu = Menu(top_frame, tearoff=0)
        self.recent_button = ctk.CTkButton(top_frame, text="🕘 История ⮟", width=30, command=self.show_recent_menu)
        self.recent_button.pack(side="left", padx=5)
        CTkTooltip(self.recent_button, "История файлов")

        # Undo / Redo
        self.Undo_button = ctk.CTkButton(top_frame, text="⮌", width=30, command=lambda: self.editor.event_generate("<<Undo>>"))
        self.Undo_button.pack(side="left", padx=5)
        CTkTooltip(self.Undo_button, "Отменить (Ctrl+Z)")

        self.Redo_button = ctk.CTkButton(top_frame, text="⮎", width=30, command=lambda: self.editor.event_generate("<<Redo>>"))
        self.Redo_button.pack(side="left", padx=5)
        CTkTooltip(self.Redo_button, "Повторить (Ctrl+Y)")

        # Кнопка настроек
        self.settings_button = ctk.CTkButton(top_frame, text="⚙", width=30, command=self.open_settings_window)
        self.settings_button.pack(side="left", padx=5)
        CTkTooltip(self.settings_button, "Настройки")

        # Кнопки компиляции и загрузки
        compile_btn = ctk.CTkButton(top_frame, text="🧩 Компилировать", command=self.compile_code)
        compile_btn.pack(side="right", padx=5)
        CTkTooltip(compile_btn, "Скомпилировать текущий файл")

        upload_label = "Прошить через UART" if self.config.get_uploader_type() == "uart" else "Прошить через ISP"
        upload_btn = ctk.CTkButton(top_frame, text=upload_label, command=self.upload_code)
        upload_btn.pack(side="right", padx=5)
        CTkTooltip(upload_btn, "Загрузить прошивку в микроконтроллер")

        from customtkinter import CTkScrollbar
        import tkinter as tk

        # Контейнер редактора
        editor_container = Frame(self)
        editor_container.pack(fill="both", expand=True, padx=5, pady=0)

        # Левый блок — нумерация строк
        self.line_numbers = LineNumbers(editor_container, width=4)
        self.line_numbers.pack(side="left", fill="y")

        # Контейнер для текста и прокруток
        text_frame = ctk.CTkFrame(editor_container)
        text_frame.pack(side="left", fill="both", expand=True)

        # Создаем текстовый редактор
        self.editor = SyntaxText(text_frame, wrap="none",
                    font=(self.font_family.get(), self.font_size.get()),
                    undo=True, autoseparators=True, maxundo=-1)

        self.editor.grid(row=0, column=0, sticky="nsew")

        # Горизонтальная прокрутка
        x_scrollbar = CTkScrollbar(text_frame, orientation="horizontal", command=self.editor.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Вертикальная прокрутка
        y_scrollbar = CTkScrollbar(text_frame, orientation="vertical", command=self.editor.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        # Привязка прокрутки
        self.editor.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Настройка сетки
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Подключение номеров строк
        self.line_numbers.text_widget = self.editor
        self.line_numbers.bind_to_widget()
        self.line_numbers.update_line_numbers()


        # Контейнер консоли
        console_frame = ctk.CTkFrame(self)
        console_frame.pack(fill="both", padx=5, pady=5)

        # Консоль
        self.console = SyntaxText(console_frame, height=10,
                        font=(self.font_family.get(), self.font_size.get()),
                        wrap="none")

        self.console.grid(row=0, column=0, sticky="nsew")

        # Вертикальная прокрутка
        console_yscroll = CTkScrollbar(console_frame, orientation="vertical", command=self.console.yview)
        console_yscroll.grid(row=0, column=1, sticky="ns")

        self.console.configure(yscrollcommand=console_yscroll.set)

        # Настройка сетки
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        # Блокируем редактирование
        self.console.configure(state="disabled")

    def open_settings_window(self):
        if hasattr(self, '_settings_window') and self._settings_window.winfo_exists():
            self._settings_window.lift()
            return

        self._settings_window = EditorSettingsWindow(
            self,
            mcu_var=self.mcu_var,
            com_var=self.com_var,
            boards=self.boards,
            font_family=self.font_family,
            font_size=self.font_size,
            uploader_type=self.config.get_uploader_type(),
            bootloader=self.config.config.get("bootloader", "auto")
        )

        self.wait_window(self._settings_window)
        self._apply_font_settings()
        
    def _apply_font_settings(self):
        """Применяет настройки шрифта"""
        if hasattr(self, '_settings_window'):
            # Создаем новый шрифт
            new_font = (self.font_family.get(), self.font_size.get())
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
            
            # Добавляем подсветку после загрузки файла
            self.editor.after(100, lambda: self.editor.highlight_syntax())
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
        compiler_manager = CompilerManager()
        if not compiler_manager.is_installed():
            archives = compiler_manager.available_archives()
            if archives:
                if messagebox.askyesno("Установка компилятора", f"Компилятор не найден. Установить из {archives[0].name}?"):
                    compiler_manager.install_from_archive(archives[0])
                    messagebox.showinfo("Установлено", "Компилятор успешно установлен.")
                else:
                    self.log("Компиляция отменена. Компилятор не установлен.")
                    return
            else:
                messagebox.showwarning("Нет компилятора", "Папка 'compilers/' пуста. Установите компилятор вручную.")
                self.log("Компиляция невозможна — нет компилятора.")
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

        self.uploader.upload(
            hex_path=str(hex_path),
            mcu=mcu,
            port=port,
            callback=callback
        )

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
        from core.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_key = "dark" if theme_manager.config.config.get("theme") == "dark" else "default"
        theme = theme_manager.editor_themes.get(theme_key)

        # Применяем тему ко всем элементам
        if hasattr(self, "editor"):
            self.editor.configure(
                bg=theme["editor_bg"],
                fg=theme["editor_fg"],
                insertbackground=theme["cursor"],
                selectbackground=theme["selection"]
            )
        
        if hasattr(self, "console"):
            self.console.configure(
                bg=theme["console_bg"],
                fg=theme["console_fg"],
                insertbackground=theme["cursor"],
                selectbackground=theme["selection"]
            )
        
        if hasattr(self, "line_numbers"):
            self.line_numbers.configure(
                bg=theme["gutter_bg"],
                fg=theme["gutter_fg"]
            )