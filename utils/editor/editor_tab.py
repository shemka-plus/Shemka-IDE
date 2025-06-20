import customtkinter as ctk
from tkinter import filedialog, Menu, messagebox, PanedWindow, Text, Frame, Scrollbar
from utils.editor.base_editor import SyntaxText
from avr.compiler import AVRCompiler
from avr.uploader import AVRUploader
from pathlib import Path
import threading
import re
import os
import serial.tools.list_ports

class LineNumbers(Text):
    def __init__(self, master, text_widget=None, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(
            state="disabled",
            width=4,
            padx=5,  # Упростили отступ до одного значения
            pady=5,
            bg="#252526",
            fg="#858585",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 12),
            takefocus=0,
            highlightthickness=0
        )
        
        # Привязка событий скроллинга
        self.bind("<MouseWheel>", self._on_mousewheel)
        
        if self.text_widget is not None:
            self.bind_to_widget()

    def bind_to_widget(self):
        """Привязываем события к текстовому виджету"""
        self.text_widget.bind("<Configure>", self._on_configure)
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_configure(self, event=None):
        self.update_line_numbers()
        
    def _on_key_release(self, event=None):
        self.update_line_numbers()
        
    def _on_mousewheel(self, event):
        # Прокрутка обоих виджетов одновременно
        self.text_widget.yview_scroll(-1 * int(event.delta/120), "units")
        self.yview_moveto(self.text_widget.yview()[0])
        return "break"
        
    def update_line_numbers(self):
        self.config(state="normal")
        self.delete("1.0", "end")
        
        # Получаем количество строк
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        
        # Вставляем номера строк
        for i in range(1, lines + 1):
            self.insert("end", f"{i}\n")
            
        self.config(state="disabled")
        self.yview_moveto(self.text_widget.yview()[0])

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
        self.mcu_var = ctk.StringVar(value=config.config.get("mcu", "ATmega328P"))
        self.com_var = ctk.StringVar(value=config.config.get("com_port", ""))

        self._highlight_job = None
        self._last_highlighted_text = ""  # Для отслеживания изменений
        self.setup_ui()
        self.update_ports()

        # Автооткрытие последнего файла
        if self.recent_files:
            last_file = self.recent_files[0]
            if Path(last_file).exists():
                self.load_file(last_file)

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(top_frame, text="Новый", command=self.new_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Открыть", command=self.open_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Сохранить", command=self.save_file).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Сохранить как", command=self.save_file_as).pack(side="left", padx=5)  # Новая кнопка

        self.recent_menu = Menu(top_frame, tearoff=0)
        self.recent_button = ctk.CTkButton(top_frame, text="История", command=self.show_recent_menu)
        self.recent_button.pack(side="left", padx=5)

        # Создаем основной контейнер с использованием Frame вместо CTkFrame
        editor_container = Frame(self)
        editor_container.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Номера строк (слева)
        self.line_numbers = LineNumbers(editor_container, width=4)
        self.line_numbers.pack(side="left", fill="y")

        # Основной редактор (занимает оставшееся пространство)
        self.editor = SyntaxText(editor_container, wrap="none", font=("Consolas", 12))
        self.editor.pack(side="left", fill="both", expand=True)

        # Привязываем редактор к номерам строк
        self.line_numbers.text_widget = self.editor
        self.line_numbers.bind_to_widget()
        self.line_numbers.update_line_numbers()

        # Консоль
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

    def save_file_as(self):
        """Сохранение файла под новым именем"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cpp",
            filetypes=[("C Files", "*.cpp"), ("Arduino", "*.ino"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()  # Используем существующую логику сохранения
            self.config.add_recent_file(file_path)
            self.log(f"Файл сохранен как: {file_path}")        

    def setup_syntax_tags(self):
        # Стили для редактора
        self.editor.configure(bg="#2b2b2b", fg="#d4d4d4", insertbackground="white", selectbackground="#264F78")
        self.editor.tag_config("keyword", foreground="#569CD6")
        self.editor.tag_config("define", foreground="#C586C0")
        self.editor.tag_config("comment", foreground="#6A9955")
        self.editor.tag_config("string", foreground="#CE9178")

        # Стили для консоли
        self.console.configure(bg="#000000", fg="#d4d4d4", insertbackground="white", selectbackground="#264F78")

    def schedule_syntax_highlight(self, event=None):
        current_text = self.editor.get("1.0", "end-1c")
        if current_text == self._last_highlighted_text:
            return  # Пропускаем, если текст не изменился

        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after_idle(self.highlight_syntax)  # Используем after_idle для минимизации нагрузки

    def highlight_syntax(self):
        current_text = self.editor.get("1.0", "end-1c")
        if current_text == self._last_highlighted_text:
            return  # Пропускаем, если текст не изменился

        self._last_highlighted_text = current_text

        # Очистка предыдущих тегов
        for tag in ["keyword", "define", "comment", "string"]:
            self.editor.tag_remove(tag, "1.0", "end")

        # Пропускаем большие файлы для производительности
        #if len(current_text) > 10000:
         #   return

        # Оптимизированные регулярные выражения
        patterns = [
            (r'\b(int|char|float|void|return|if|else|while|for|break|continue|include|define|struct|sizeof)\b', "keyword"),
            (r'#define\s+\w+', "define"),
            (r'//.*?$|/\*.*?\*/', "comment"),
            (r'"(?:\\.|[^"\\])*"', "string"),
        ]

        for pattern, tag in patterns:
            for match in re.finditer(pattern, current_text, re.MULTILINE | re.DOTALL):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.editor.tag_add(tag, start, end)

        self.editor.edit_modified(False)

    # Остальные методы остаются без изменений...

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
                self.com_var.set(ports[0])
        except Exception as e:
            self.log(f"Ошибка портов: {e}")

    def new_file(self):
        self.editor.delete("1.0", "end")
        self.current_file = None
        self.log("Создан новый файл")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("C Files", "*.cpp"), ("Arduino", "*.ino"), ("All Files", "*.*")])
        if file_path:
            self.load_file(file_path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.highlight_syntax()
            self.current_file = path
            self.config.add_recent_file(path)
            self.log(f"Открыт файл: {path}")
        except Exception as e:
            self.log(f"Ошибка открытия: {e}")

    def save_file(self):
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(defaultextension=".c")
            if not file_path:
                return
            self.current_file = file_path
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.config.add_recent_file(self.current_file)
            self.log(f"Сохранено: {self.current_file}")
        except Exception as e:
            self.log(f"Ошибка сохранения: {e}")

    def compile_code(self):
        code = self.editor.get("1.0", "end-1c")
        mcu = self.boards.get(self.mcu_var.get())
        self.log("=== Компиляция ===")

        def run_compile():
            self.compiler.compile(code, mcu, callback=self.compile_callback)

        threading.Thread(target=run_compile, daemon=True).start()

    def compile_callback(self, success, output):
        self.log(output or "")
        if success:
            self.log("Компиляция завершена успешно")
        else:
            self.log("Ошибка компиляции")

    def upload_code(self):
        hex_path = Path("build/sketch.hex")
        if not hex_path.exists():
            self.log("HEX-файл не найден. Сначала скомпилируйте проект.")
            return
        mcu = self.boards.get(self.mcu_var.get())
        port = self.com_var.get()
        self.log("=== Прошивка ===")
        self.uploader.upload(str(hex_path), mcu, port=port, callback=self.upload_callback)

    def upload_callback(self, success, output):
        self.log(output or "")
        if success:
            self.log("Прошивка завершена успешно")
        else:
            self.log("Ошибка прошивки")

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")
