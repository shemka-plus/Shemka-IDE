import customtkinter as ctk
from tkinter import filedialog, StringVar, Menu
from utils.hex_tools.hex_tab import HexTab
from utils.hex_tools.eeprom_tab import EepromTab
from utils.hex_tools.fuses_tab import FusesTab
from utils.hex_tools.clone_tab import CloneTab
import os
from gui.config_manager import ConfigManager
import serial.tools.list_ports
from pathlib import Path
import threading
import tkinter as tk
from utils.ui.tooltip import CTkTooltip

class HexTabUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config_manager = ConfigManager()
        self.operation_in_progress = False

        # Настройки
        self.mcu = StringVar(value=self.config_manager.config.get("mcu", "ATmega328P"))
        self.port = StringVar(value=self.config_manager.config.get("com_port", "COM1"))
        self.baud = StringVar(value="19200")
        self.programmer = StringVar(value="stk500v1")
        self.hex_path = StringVar(value=self.config_manager.config.get("last_hex", ""))

        self.project_name = StringVar()
        self.saved_project = StringVar()

        # Логика
        self.hex = HexTab(console_callback=self.log)
        self.eeprom = EepromTab(console_callback=self.log)
        self.fuses = FusesTab(console_callback=self.log)
        self.clone = CloneTab(console_callback=self.log)

        self.create_widgets()
        self.setup_context_menu()

    def setup_context_menu(self):
        """Контекстное меню для HEX Viewer"""
        self.viewer_menu = Menu(self, tearoff=0)
        self.viewer_menu.add_command(label="Копировать", command=self.copy_hex_viewer)
        self.viewer_menu.add_command(label="Выделить всё", command=self.select_all_hex_viewer)
        self.viewer.bind("<Button-3>", self.show_viewer_menu)

    def show_viewer_menu(self, event):
        try:
            self.viewer_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.viewer_menu.grab_release()

    def run_with_progress(self, operation, title):
        """Запуск операции с индикатором прогресса"""
        if self.operation_in_progress:
            return
            
        self.operation_in_progress = True
        
        # Создаем окно прогресса
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title(title)
        self.progress_window.geometry("300x100")
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        
        # Центрируем окно
        self.center_window(self.progress_window)
        
        ctk.CTkLabel(self.progress_window, text=f"{title}...").pack(pady=10)
        self.progress_bar = ctk.CTkProgressBar(self.progress_window)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        self.progress_bar.set(0)
        self.progress_window.update()
        
        # Запускаем операцию в отдельном потоке
        def thread_operation():
            try:
                operation()
            finally:
                self.after(100, self.close_progress)
        
        threading.Thread(target=thread_operation, daemon=True).start()

    def center_window(self, window):
        """Центрирует окно относительно главного окна"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')

    def create_widgets(self):
        # Верхняя панель
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=(10, 0))

        # МК
        ctk.CTkLabel(top, text="МК:").grid(row=0, column=0, padx=5, sticky="e")
        ctk.CTkOptionMenu(top, variable=self.mcu, values=["ATmega328P", "ATmega168PA"]).grid(row=0, column=1, padx=5)

        # Порт
        ctk.CTkLabel(top, text="Порт:").grid(row=0, column=2, padx=5, sticky="e")
        self.port_menu = ctk.CTkOptionMenu(top, variable=self.port, values=self.get_ports())
        self.port_menu.grid(row=0, column=3, padx=5)
        ctk.CTkButton(top, text="🔄", width=30, command=self.update_ports).grid(row=0, column=4)

        # Скорость (фиксированная)
        ctk.CTkLabel(top, text="Скорость:").grid(row=0, column=5, padx=5, sticky="e")
        ctk.CTkLabel(top, textvariable=self.baud).grid(row=0, column=6, padx=5)

        # Панель вкладок
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="x", padx=10, pady=10)

        self.create_hex_tab(tabs.add("HEX"))
        self.create_eeprom_tab(tabs.add("EEPROM"))
        self.create_fuses_tab(tabs.add("Фьюзы"))
        self.create_clone_tab(tabs.add("Клон"))

        # Контейнер для HEX Viewer и консоли
        viewer_console_frame = ctk.CTkFrame(self)
        viewer_console_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # HEX Viewer с прокруткой

        self.viewer_frame = ctk.CTkFrame(viewer_console_frame)
        self.viewer_frame.pack(fill="both", expand=True, pady=(0, 5))

        # Используем CTkTextbox вместо tk.Text для сохранения темы
        self.viewer = ctk.CTkTextbox(
            self.viewer_frame, 
            wrap="none", 
            font=("Courier New", 11),
            state="disabled"
        )
        self.viewer.pack(side="left", fill="both", expand=True)

        # Оставим одну полосу прокрутки CTk
        self.viewer_scroll = ctk.CTkScrollbar(
            self.viewer_frame, 
            orientation="vertical", 
            command=self.viewer.yview
        )
        self.viewer_scroll.pack(side="right", fill="y")
        self.viewer.configure(yscrollcommand=self.viewer_scroll.set)

        # Консоль сделаем ниже viewer с фиксированной высотой
        self.console_frame = ctk.CTkFrame(viewer_console_frame)
        self.console_frame.pack(fill="x", pady=(5, 0))
        self.console = ctk.CTkTextbox(self.console_frame, height=120)
        self.console.pack(fill="x")
        self.console.configure(state="disabled")

    def show_eeprom_file(self, path):
        if not os.path.exists(path):
            self.log(True, f"[Ошибка] EEPROM-файл не найден: {path}")
            return

        try:
            with open(path, "r") as f:
                lines = f.readlines()

            self.viewer.configure(state="normal")
            self.viewer.delete("1.0", "end")

            address = 0
            for line in lines:
                if not line.startswith(":"):
                    continue
                byte_count = int(line[1:3], 16)
                data = line[9:9 + byte_count * 2]
                if not data:
                    continue
                formatted = " ".join(data[i:i + 2] for i in range(0, len(data), 2))
                self.viewer.insert("end", f"{address:04X}: {formatted}\n")
                address += byte_count

            self.viewer.configure(state="disabled")
            self.log(False, f"[EEPROM] Загружено {len(lines)} строк из {os.path.basename(path)}")
        except Exception as e:
            self.log(True, f"[Ошибка при отображении EEPROM] {e}")   

    def setup_context_menu(self):
        """Контекстное меню для HEX Viewer"""
        self.viewer_menu = Menu(self, tearoff=0)
        self.viewer_menu.add_command(label="Копировать", command=self.copy_hex_viewer)
        self.viewer_menu.add_command(label="Выделить всё", command=self.select_all_hex_viewer)
        self.viewer.bind("<Button-3>", self.show_viewer_menu)

    def show_viewer_menu(self, event):
        try:
            self.viewer_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.viewer_menu.grab_release()

    def copy_hex_viewer(self):
        try:
            text = self.viewer.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(text)
        except:
            pass

    def select_all_hex_viewer(self):
        self.viewer.configure(state="normal")
        self.viewer.tag_add("sel", "1.0", "end")
        self.viewer.configure(state="disabled")
        return "break"

    def create_hex_tab(self, tab):
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=5, fill="x")

        buttons = [
            ("📂", "Открыть HEX", self.open_hex),
            ("💾", "Сохранить HEX", self.save_hex),
            ("🧩", "Прошить", lambda: self.run_with_progress(self.flash_hex, "Прошивка HEX")),
            ("📥", "Считать", lambda: self.run_with_progress(self.read_hex, "Чтение HEX")),
            ("📏", "Верифицировать", lambda: self.run_with_progress(self.verify_hex, "Верификация HEX")),
            ("❌", "Очистить чип", lambda: self.run_with_progress(self.erase_chip, "Очистка чипа")),
        ]

        for icon, tooltip, cmd in buttons:
            btn = ctk.CTkButton(btn_frame, text=icon, width=36, height=36, command=cmd)
            btn.pack(side="left", padx=6)
            CTkTooltip(btn, text=tooltip)

    def close_progress(self):
        """Закрыть окно прогресса"""
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
            del self.progress_window
        self.operation_in_progress = False



    def create_eeprom_tab(self, tab):
        ctk.CTkButton(tab, text="Чтение EEPROM", command=self.read_eeprom).grid(row=3, column=0, pady=10)
        ctk.CTkButton(tab, text="Запись EEPROM", command=self.write_eeprom).grid(row=3, column=1, pady=10)

    def create_fuses_tab(self, tab):
        self.fuse_l = StringVar()
        self.fuse_h = StringVar()
        self.fuse_e = StringVar()
        
        # Горизонтальный фрейм для фьюзов
        fuses_frame = ctk.CTkFrame(tab)
        fuses_frame.pack(fill="x", pady=5, padx=5)
        
        # LFuse
        fuse_l_frame = ctk.CTkFrame(fuses_frame)
        fuse_l_frame.pack(side="left", padx=5)
        ctk.CTkLabel(fuse_l_frame, text="LFuse:").pack()
        ctk.CTkEntry(fuse_l_frame, textvariable=self.fuse_l, width=70).pack()
        
        # HFuse
        fuse_h_frame = ctk.CTkFrame(fuses_frame)
        fuse_h_frame.pack(side="left", padx=5)
        ctk.CTkLabel(fuse_h_frame, text="HFuse:").pack()
        ctk.CTkEntry(fuse_h_frame, textvariable=self.fuse_h, width=70).pack()
        
        # EFuse
        fuse_e_frame = ctk.CTkFrame(fuses_frame)
        fuse_e_frame.pack(side="left", padx=5)
        ctk.CTkLabel(fuse_e_frame, text="EFuse:").pack()
        ctk.CTkEntry(fuse_e_frame, textvariable=self.fuse_e, width=70).pack()
        
        # Горизонтальный фрейм для кнопок
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkButton(btn_frame, text="Чтение", command=self.read_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Запись", command=self.write_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Загрузить", command=self.load_fuses).pack(side="left", padx=5)

    def save_fuses(self):
        path = filedialog.asksaveasfilename(defaultextension=".fuses", filetypes=[("Файлы фьюзов", "*.fuses")])
        if path:
            with open(path, "w") as f:
                f.write(f"LFuse: {self.fuse_l.get()}\n")
                f.write(f"HFuse: {self.fuse_h.get()}\n")
                f.write(f"EFuse: {self.fuse_e.get()}\n")
            self.log(False, f"[Фьюзы] Сохранены в {path}")

    def load_fuses(self):
        path = filedialog.askopenfilename(filetypes=[("Файлы фьюзов", "*.fuses")])
        if path:
            try:
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("LFuse:"):
                            self.fuse_l.set(line.split(":")[1].strip())
                        elif line.startswith("HFuse:"):
                            self.fuse_h.set(line.split(":")[1].strip())
                        elif line.startswith("EFuse:"):
                            self.fuse_e.set(line.split(":")[1].strip())
                self.log(False, f"[Фьюзы] Загружены из {path}")
            except Exception as e:
                self.log(True, f"[Ошибка загрузки фьюзов] {e}")


    def create_clone_tab(self, tab):
        # Горизонтальный фрейм для полей ввода
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", pady=(10, 5), padx=5)
        
        # Поле имени проекта
        ctk.CTkLabel(input_frame, text="Имя проекта:").pack(side="left", padx=(0, 5))
        ctk.CTkEntry(input_frame, textvariable=self.project_name).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Поле выбора сохраненного проекта
        ctk.CTkLabel(input_frame, text="Сохранённые:").pack(side="left", padx=(0, 5))
        self.project_list = ctk.CTkOptionMenu(
            input_frame, 
            variable=self.saved_project, 
            values=self.get_saved_projects()
        )
        self.project_list.pack(side="left", fill="x", expand=True)

        # Горизонтальный фрейм для кнопок
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        ctk.CTkButton(btn_frame, text="Клонировать чип", command=self.clone_chip).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Восстановить чип", command=self.restore_chip).pack(side="left", padx=5)

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()] or ["COM1"]

    def update_ports(self):
        ports = self.get_ports()
        self.port_menu.configure(values=ports)
        if ports:
            self.port.set(ports[0])

    def get_saved_projects(self):
        folder = Path("clones")
        folder.mkdir(exist_ok=True)
        return [f.stem.replace("_flash", "") for f in folder.glob("*_flash.hex")]

    # Функции HEX
    def open_hex(self):
        path = filedialog.askopenfilename(filetypes=[("HEX-файлы", "*.hex")])
        if path:
            self.hex_path.set(path)
            self.config_manager.config["last_hex"] = path
            self.config_manager.save_config()
            self.show_hex_file(path)

    def show_hex_file(self, path):
        if not os.path.exists(path):
            self.log(True, f"[Ошибка] HEX-файл не найден: {path}")
            return

        try:
            with open(path, "r") as f:
                lines = f.readlines()

            self.viewer.configure(state="normal")
            self.viewer.delete("1.0", "end")

            address = 0
            for line in lines:
                if not line.startswith(":"):
                    continue
                byte_count = int(line[1:3], 16)
                data = line[9:9 + byte_count * 2]
                if not data:
                    continue
                formatted = " ".join(data[i:i + 2] for i in range(0, len(data), 2))
                self.viewer.insert("end", f"{address:04X}: {formatted}\n")
                address += byte_count

            self.viewer.configure(state="disabled")
            self.log(False, f"[HEX] Загружено {len(lines)} строк из {os.path.basename(path)}")
        except Exception as e:
            self.log(True, f"[Ошибка при отображении HEX] {e}")

    def save_hex(self):
        path = filedialog.asksaveasfilename(defaultextension=".hex")
        if path:
            with open(path, "w") as f:
                f.write(self.viewer.get("1.0", "end").strip())

    def flash_hex(self):
        self.log(False, "[Прошивка HEX]...")
        self.hex.flash_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), self.hex_path.get())

    def read_hex(self):
        """Чтение HEX с индикатором прогресса"""
        path = self.hex_path.get() or "read_flash.hex"
        self.hex.read_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), path)
        self.show_hex_file(path)

    def show_hex_file(self, path):
        """Показать содержимое HEX файла с прогрессом"""
        if not os.path.exists(path):
            self.log(True, f"[Ошибка] HEX-файл не найден: {path}")
            return

        try:
            with open(path, "r") as f:
                lines = f.readlines()

            self.viewer.configure(state="normal")
            self.viewer.delete("1.0", "end")

            total_lines = len(lines)
            for i, line in enumerate(lines):
                if not line.startswith(":"):
                    continue
                    
                byte_count = int(line[1:3], 16)
                data = line[9:9 + byte_count * 2]
                if not data:
                    continue
                    
                formatted = " ".join(data[i:i + 2] for i in range(0, len(data), 2))
                self.viewer.insert("end", f"{i:04X}: {formatted}\n")
                
                # Обновляем прогресс каждые 100 строк
                if i % 100 == 0 and hasattr(self, 'progress_window'):
                    self.progress_bar.set(i / total_lines)
                    self.progress_window.update()

            self.viewer.configure(state="disabled")
            self.log(False, f"[HEX] Загружено {len(lines)} строк из {os.path.basename(path)}")
        except Exception as e:
            self.log(True, f"[Ошибка при отображении HEX] {e}")

    def verify_hex(self):
        self.log(False, "[Верификация HEX]...")
        self.hex.verify_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), self.hex_path.get())

    def erase_chip(self):
        self.hex.run_command([
            "-p", self.mcu.get().lower(),
            "-c", self.programmer.get(),
            "-P", self.port.get(),
            "-b", self.baud.get(),
            "-e"
        ], "Очистка чипа")

    # EEPROM
    def read_eeprom(self):
        path = self.hex_path.get().replace(".hex", "_eeprom.hex") or "read_eeprom.hex"
        self.eeprom.read_eeprom(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), path)
        self.show_eeprom_file(path)

    def write_eeprom(self):
        self.eeprom.write_eeprom(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), self.hex_path.get())

    # Фьюзы
    def read_fuses(self):
        self.fuses.read_fuses(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get())

    def write_fuses(self):
        self.fuses.write_fuses(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(),
                               lfuse=self.fuse_l.get(), hfuse=self.fuse_h.get(), efuse=self.fuse_e.get())

    # Клон
    def clone_chip(self):
        name = self.project_name.get() or "clone"
        path = Path("clones") / name
        self.clone.clone_chip(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), str(path))

    def restore_chip(self):
        name = self.saved_project.get()
        if not name:
            return
        path = Path("clones") / name
        self.clone.restore_chip(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), str(path))

    def log(self, error, message):
        prefix = "❌ " if error else "🟢 "
        self.console.configure(state="normal")
        self.console.insert("end", prefix + message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def update_theme(self):
        """Обновление темы для всех элементов"""
        from core.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_key = "dark" if theme_manager.config.config.get("theme") == "dark" else "default"
        theme = theme_manager.editor_themes.get(theme_key)
        
        # Применяем тему к viewer
        self.viewer.configure(
            fg_color=theme["editor_bg"],
            text_color=theme["editor_fg"],
            scrollbar_button_color=theme["selection"],
            scrollbar_button_hover_color=theme["cursor"]
        )
        
        # Применяем тему к консоли
        self.console.configure(
            fg_color=theme["console_bg"],
            text_color=theme["console_fg"]
        )
