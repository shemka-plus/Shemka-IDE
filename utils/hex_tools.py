import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext, Menu
import subprocess
import os
import serial.tools.list_ports
import intelhex
import threading
from datetime import datetime
from pathlib import Path

class HexToolsTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config
        self.current_file = None
        self.current_eeprom_file = None
        self.backup_dir = Path("Backup")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Стандартные фьюзы для Arduino
        self.default_fuses = {
            "ATmega328P": {"low": "0xFF", "high": "0xDE", "ext": "0xFD", "lock": "0xFF"},
            "ATmega328PB": {"low": "0xFF", "high": "0xDE", "ext": "0xFD", "lock": "0xFF"},
            "ATmega168PA": {"low": "0xFF", "high": "0xDE", "ext": "0xFD", "lock": "0xFF"}
        }
        
        # Переменные
        self.board_var = ctk.StringVar(value="ATmega328P")
        self.port_var = ctk.StringVar()
        self.programmer_var = ctk.StringVar(value="PG-1 (stk500v1)")
        self.baudrate_var = ctk.StringVar(value="19200")
        
        # Фьюзы
        self.low_fuse_var = ctk.StringVar(value="0x00")
        self.high_fuse_var = ctk.StringVar(value="0x00")
        self.ext_fuse_var = ctk.StringVar(value="0x00")
        self.lock_bits_var = ctk.StringVar(value="0x00")
        
        # Статус
        self.status_var = ctk.StringVar(value="Готов")
        self.progress_var = ctk.DoubleVar(value=0.0)
        
        self.setup_ui()
        self.update_ports()
        self.setup_context_menus()

    def setup_ui(self):
        # Основная сетка
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Верхняя панель инструментов
        self.setup_toolbar()
        
        # Вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Добавляем вкладки
        self.hex_tab = self.tabview.add("HEX")
        self.eeprom_tab = self.tabview.add("EEPROM")
        self.fuses_tab = self.tabview.add("Фьюзы")
        self.clone_tab = self.tabview.add("Клонирование")
        
        # Настройка вкладок
        self.setup_hex_tab()
        self.setup_eeprom_tab()
        self.setup_fuses_tab()
        self.setup_clone_tab()
        
        # Консоль вывода
        self.console = scrolledtext.ScrolledText(
            self,
            height=10,
            font=("Consolas", 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            selectbackground='#3b3b3b',
            state='disabled'
        )
        self.console.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Уведомление о режиме программатора
        self.programmer_notice = ctk.CTkLabel(
        self, 
        text="Для работы переключите программатор в режим ISP",
        text_color="#FFA500",
        font=("", 12, "bold")
        )
        self.programmer_notice.grid(row=4, column=0, sticky="ew", padx=5, pady=(0,5))
        
        # Статусбар
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,5))
        
        self.progress = ctk.CTkProgressBar(status_frame, variable=self.progress_var)
        self.progress.pack(side="left", fill="x", expand=True, padx=5)
        
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var, width=200)
        self.status_label.pack(side="right", padx=5)
        
        # Настройка тегов для цветного текста
        self.console.tag_config("error", foreground="#FF4444")
        self.console.tag_config("success", foreground="#44FF44")
        self.console.tag_config("warning", foreground="#FFA500")

    def setup_toolbar(self):
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Выбор COM-порта
        ctk.CTkLabel(toolbar, text="Порт:").pack(side="left", padx=5)
        self.port_menu = ctk.CTkOptionMenu(toolbar, variable=self.port_var, width=120)
        self.port_menu.pack(side="left", padx=5)
        
        # Программатор (фиксированный PG-1)
        ctk.CTkLabel(toolbar, text="Программатор:").pack(side="left", padx=5)
        ctk.CTkLabel(toolbar, text="PG-1 (stk500v1)", width=120).pack(side="left", padx=5)
        
        # Выбор скорости
        ctk.CTkLabel(toolbar, text="Скорость:").pack(side="left", padx=5)
        ctk.CTkOptionMenu(
            toolbar,
            variable=self.baudrate_var,
            values=["19200", "57600", "115200"],
            width=100
        ).pack(side="left", padx=5)
        
        # Выбор микроконтроллера
        ctk.CTkLabel(toolbar, text="МК:").pack(side="left", padx=5)
        ctk.CTkOptionMenu(
            toolbar,
            variable=self.board_var,
            values=list(self.boards.keys()) if self.boards else ["ATmega328P"],
            width=120
        ).pack(side="left", padx=5)

    def setup_hex_tab(self):
        frame = ctk.CTkFrame(self.hex_tab)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Открыть HEX", command=self.open_hex).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Сохранить HEX", command=self.save_hex).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Прошить", command=self.flash_hex).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Считать", command=self.read_hex).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Верифицировать", command=self.verify_hex).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Очистить чип", command=self.erase_flash).pack(side="left", padx=5)
        
        # Поле для HEX-данных
        self.hex_content = scrolledtext.ScrolledText(
            frame,
            wrap="none",
            font=("Consolas", 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            selectbackground='#3b3b3b'
        )
        self.hex_content.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_eeprom_tab(self):
        frame = ctk.CTkFrame(self.eeprom_tab)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Открыть EEPROM", command=self.open_eeprom).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Сохранить EEPROM", command=self.save_eeprom).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Записать", command=self.write_eeprom).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Считать", command=self.read_eeprom).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Верифицировать", command=self.verify_eeprom).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Очистить EEPROM", command=self.erase_eeprom).pack(side="left", padx=5)
        
        # Поле для EEPROM-данных
        self.eeprom_content = scrolledtext.ScrolledText(
            frame,
            wrap="none",
            font=("Consolas", 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            selectbackground='#3b3b3b'
        )
        self.eeprom_content.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_fuses_tab(self):
        frame = ctk.CTkFrame(self.fuses_tab)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Ввод фьюзов
        fuse_frame = ctk.CTkFrame(frame)
        fuse_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(fuse_frame, text="Low Fuse:").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkEntry(fuse_frame, textvariable=self.low_fuse_var, width=70).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fuse_frame, text="High Fuse:").grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkEntry(fuse_frame, textvariable=self.high_fuse_var, width=70).grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fuse_frame, text="Ext Fuse:").grid(row=2, column=0, padx=5, pady=5)
        ctk.CTkEntry(fuse_frame, textvariable=self.ext_fuse_var, width=70).grid(row=2, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fuse_frame, text="Lock Bits:").grid(row=3, column=0, padx=5, pady=5)
        ctk.CTkEntry(fuse_frame, textvariable=self.lock_bits_var, width=70).grid(row=3, column=1, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Считать фьюзы", command=self.read_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Записать фьюзы", command=self.write_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Стандартные (Arduino)", command=self.set_default_fuses).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Заводские", command=self.set_factory_fuses).pack(side="left", padx=5)

    def setup_clone_tab(self):
        frame = ctk.CTkFrame(self.clone_tab)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Поля ввода
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(input_frame, text="Имя проекта:").pack(side="left", padx=5)
        self.project_name = ctk.CTkEntry(input_frame)
        self.project_name.pack(side="left", padx=5, fill="x", expand=True)
        
        # Список существующих проектов
        self.project_list = ctk.CTkOptionMenu(
            frame,
            values=self.get_existing_projects(),
            command=self.select_project
        )
        self.project_list.pack(fill="x", padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Клонировать чип", 
            command=self.clone_chip
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Восстановить чип", 
            command=self.restore_chip
        ).pack(side="left", padx=5)

    def setup_context_menus(self):
        # Меню для консоли
        self.console_menu = Menu(self, tearoff=0)
        self.console_menu.add_command(label="Копировать", command=self.copy_console)
        self.console_menu.add_command(label="Очистить", command=self.clear_console)
        self.console.bind("<Button-3>", lambda e: self.console_menu.tk_popup(e.x_root, e.y_root))
        
        # Меню для HEX-контента
        self.hex_menu = Menu(self, tearoff=0)
        self.hex_menu.add_command(label="Копировать", command=self.copy_hex)
        self.hex_content.bind("<Button-3>", lambda e: self.hex_menu.tk_popup(e.x_root, e.y_root))
        
        # Меню для EEPROM-контента
        self.eeprom_menu = Menu(self, tearoff=0)
        self.eeprom_menu.add_command(label="Копировать", command=self.copy_eeprom)
        self.eeprom_content.bind("<Button-3>", lambda e: self.eeprom_menu.tk_popup(e.x_root, e.y_root))
        
        # Горячие клавиши
        self.hex_content.bind("<Control-c>", lambda e: self.copy_hex())
        self.eeprom_content.bind("<Control-c>", lambda e: self.copy_eeprom())
        self.console.bind("<Control-c>", lambda e: self.copy_console())

    def update_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu.configure(values=ports)
        if ports:
            self.port_var.set(ports[0])

    def get_existing_projects(self):
        return [d.name for d in self.backup_dir.glob("*") if d.is_dir()]

    def select_project(self, choice):
        self.project_name.delete(0, "end")
        self.project_name.insert(0, choice)

    # HEX-функции
    def open_hex(self):
        file_path = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
        if file_path:
            self.current_file = file_path
            threading.Thread(target=self.display_hex_content, args=(file_path,)).start()
            self.log_message(f"Открыт HEX-файл: {file_path}", "success")

    def save_hex(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Нет открытого файла для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".hex",
            filetypes=[("HEX files", "*.hex")],
            initialfile=os.path.basename(self.current_file)
        )
        
        if file_path:
            try:
                ih = intelhex.IntelHex(self.current_file)
                ih.write_hex_file(file_path)
                self.log_message(f"HEX-файл сохранен: {file_path}", "success")
            except Exception as e:
                self.log_message(f"Ошибка сохранения: {str(e)}", "error")

    def flash_hex(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала откройте HEX-файл")
            return
            
        if not self.validate_connection():
            return
            
        def flash_thread():
            self.set_status("Прошивка HEX...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",  # Фиксированный программатор PG-1
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"flash:w:{self.current_file}:i"
            ]
            self.run_command(cmd, "Прошивка HEX")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=flash_thread, daemon=True).start()

    def read_hex(self):
        if not self.validate_connection():
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".hex",
            filetypes=[("HEX files", "*.hex")]
        )
        
        if not save_path:
            return
            
        def read_thread():
            self.set_status("Чтение HEX...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"flash:r:{save_path}:i"
            ]
            if self.run_command(cmd, "Чтение HEX"):
                self.current_file = save_path
                self.display_hex_content(save_path)
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=read_thread, daemon=True).start()

    def verify_hex(self):
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала откройте HEX-файл")
            return
            
        if not self.validate_connection():
            return
            
        def verify_thread():
            self.set_status("Верификация HEX...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"flash:v:{self.current_file}:i"
            ]
            self.run_command(cmd, "Верификация HEX")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=verify_thread, daemon=True).start()

    def erase_flash(self):
        if not self.validate_connection():
            return
            
        if not messagebox.askyesno("Подтверждение", "Очистить Flash память микроконтроллера?"):
            return
            
        def erase_thread():
            self.set_status("Очистка Flash...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-e"
            ]
            self.run_command(cmd, "Очистка Flash")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=erase_thread, daemon=True).start()

    def display_hex_content(self, file_path):
        try:
            ih = intelhex.IntelHex(file_path)
            content = ""
            bytes_per_line = 16
            
            for segment in ih.segments():
                for addr in range(segment[0], segment[1]):
                    if addr % bytes_per_line == 0:
                        content += f"\n{addr:04X}: "
                    content += f"{ih[addr]:02X} "
            
            self.hex_content.config(state='normal')
            self.hex_content.delete("1.0", "end")
            self.hex_content.insert("1.0", content.strip())
            self.hex_content.config(state='disabled')
        except Exception as e:
            self.log_message(f"Ошибка чтения HEX: {str(e)}", "error")

    # EEPROM-функции
    def open_eeprom(self):
        file_path = filedialog.askopenfilename(filetypes=[("EEPROM files", "*.eep")])
        if file_path:
            self.current_eeprom_file = file_path
            threading.Thread(target=self.display_eeprom_content, args=(file_path,)).start()
            self.log_message(f"Открыт EEPROM-файл: {file_path}", "success")

    def save_eeprom(self):
        if not self.current_eeprom_file:
            messagebox.showwarning("Предупреждение", "Нет открытого файла для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".eep",
            filetypes=[("EEPROM files", "*.eep")],
            initialfile=os.path.basename(self.current_eeprom_file)
        )
        
        if file_path:
            try:
                ih = intelhex.IntelHex(self.current_eeprom_file)
                ih.write_hex_file(file_path)
                self.log_message(f"EEPROM-файл сохранен: {file_path}", "success")
            except Exception as e:
                self.log_message(f"Ошибка сохранения: {str(e)}", "error")

    def write_eeprom(self):
        if not self.current_eeprom_file:
            messagebox.showwarning("Предупреждение", "Сначала откройте EEPROM-файл")
            return
            
        if not self.validate_connection():
            return
            
        def write_thread():
            self.set_status("Запись EEPROM...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"eeprom:w:{self.current_eeprom_file}:i"
            ]
            self.run_command(cmd, "Запись EEPROM")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=write_thread, daemon=True).start()

    def read_eeprom(self):
        if not self.validate_connection():
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".eep",
            filetypes=[("EEPROM files", "*.eep")]
        )
        
        if not save_path:
            return
            
        def read_thread():
            self.set_status("Чтение EEPROM...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"eeprom:r:{save_path}:i"
            ]
            if self.run_command(cmd, "Чтение EEPROM"):
                self.current_eeprom_file = save_path
                self.display_eeprom_content(save_path)
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=read_thread, daemon=True).start()

    def verify_eeprom(self):
        if not self.current_eeprom_file:
            messagebox.showwarning("Предупреждение", "Сначала откройте EEPROM-файл")
            return
            
        if not self.validate_connection():
            return
            
        def verify_thread():
            self.set_status("Верификация EEPROM...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"eeprom:v:{self.current_eeprom_file}:i"
            ]
            self.run_command(cmd, "Верификация EEPROM")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=verify_thread, daemon=True).start()

    def erase_eeprom(self):
        if not self.validate_connection():
            return
            
        if not messagebox.askyesno("Подтверждение", "Очистить EEPROM микроконтроллера?"):
            return
            
        def erase_thread():
            self.set_status("Очистка EEPROM...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", "eeprom:w:0xFF:i"
            ]
            self.run_command(cmd, "Очистка EEPROM")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=erase_thread, daemon=True).start()

    def display_eeprom_content(self, file_path):
        try:
            ih = intelhex.IntelHex(file_path)
            content = ""
            bytes_per_line = 16
            
            for segment in ih.segments():
                for addr in range(segment[0], segment[1]):
                    if addr % bytes_per_line == 0:
                        content += f"\n{addr:04X}: "
                    content += f"{ih[addr]:02X} "
            
            self.eeprom_content.config(state='normal')
            self.eeprom_content.delete("1.0", "end")
            self.eeprom_content.insert("1.0", content.strip())
            self.eeprom_content.config(state='disabled')
        except Exception as e:
            self.log_message(f"Ошибка чтения EEPROM: {str(e)}", "error")

    # Функции для работы с фьюзами
    def read_fuses(self):
        if not self.validate_connection():
            return
            
        def read_thread():
            self.set_status("Чтение фьюзов...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", "lfuse:r:-:h",
                "-U", "hfuse:r:-:h",
                "-U", "efuse:r:-:h",
                "-U", "lock:r:-:h"
            ]
            
            result = self.run_command(cmd, "Чтение фьюзов", capture_output=True)
            if result:
                # Парсим вывод avrdude
                fuses = {}
                for line in (result.stdout + result.stderr).split('\n'):
                    if "lfuse" in line:
                        fuses['lfuse'] = line.split()[-1]
                    elif "hfuse" in line:
                        fuses['hfuse'] = line.split()[-1]
                    elif "efuse" in line:
                        fuses['efuse'] = line.split()[-1]
                    elif "lock" in line:
                        fuses['lock'] = line.split()[-1]
                
                if fuses:
                    self.low_fuse_var.set(fuses.get('lfuse', '0x00'))
                    self.high_fuse_var.set(fuses.get('hfuse', '0x00'))
                    self.ext_fuse_var.set(fuses.get('efuse', '0x00'))
                    self.lock_bits_var.set(fuses.get('lock', '0x00'))
                    self.log_message("Фьюзы успешно прочитаны", "success")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=read_thread, daemon=True).start()

    def write_fuses(self):
        if not self.validate_connection():
            return
            
        if not messagebox.askyesno("Подтверждение", "Записать новые значения фьюзов?"):
            return
            
        def write_thread():
            self.set_status("Запись фьюзов...", 0.3)
            cmd = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get()
            ]
            
            # Добавляем фьюзы в команду
            if self.low_fuse_var.get():
                cmd.extend(["-U", f"lfuse:w:{self.low_fuse_var.get()}:m"])
            if self.high_fuse_var.get():
                cmd.extend(["-U", f"hfuse:w:{self.high_fuse_var.get()}:m"])
            if self.ext_fuse_var.get():
                cmd.extend(["-U", f"efuse:w:{self.ext_fuse_var.get()}:m"])
            if self.lock_bits_var.get():
                cmd.extend(["-U", f"lock:w:{self.lock_bits_var.get()}:m"])
            
            self.run_command(cmd, "Запись фьюзов")
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=write_thread, daemon=True).start()

    def set_default_fuses(self):
        mcu = self.board_var.get()
        if mcu in self.default_fuses:
            self.low_fuse_var.set(self.default_fuses[mcu]["low"])
            self.high_fuse_var.set(self.default_fuses[mcu]["high"])
            self.ext_fuse_var.set(self.default_fuses[mcu]["ext"])
            self.lock_bits_var.set(self.default_fuses[mcu]["lock"])
            self.log_message("Установлены стандартные фьюзы для Arduino", "success")
        else:
            self.log_message("Не найдены стандартные фьюзы для этого МК", "warning")

    def set_factory_fuses(self):
        # Заводские настройки (консервативные)
        self.low_fuse_var.set("0x62")
        self.high_fuse_var.set("0xD9")
        self.ext_fuse_var.set("0xFF")
        self.lock_bits_var.set("0xFF")
        self.log_message("Установлены заводские фьюзы", "success")

    # Функции клонирования
    def clone_chip(self):
        project_name = self.project_name.get()
        if not project_name:
            messagebox.showwarning("Предупреждение", "Введите имя проекта")
            return
            
        if not self.validate_connection():
            return
            
        project_dir = self.backup_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        flash_file = project_dir / f"{project_name}_flash_{timestamp}.hex"
        eeprom_file = project_dir / f"{project_name}_eeprom_{timestamp}.eep"
        fuses_file = project_dir / f"{project_name}_fuses_{timestamp}.txt"
        
        def clone_thread():
            self.set_status("Клонирование чипа...", 0.5)
            
            # Считываем флеш
            cmd_flash = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"flash:r:{flash_file}:i"
            ]
            
            # Считываем EEPROM
            cmd_eeprom = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"eeprom:r:{eeprom_file}:i"
            ]
            
            # Считываем фьюзы
            cmd_fuses = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", "lfuse:r:-:h",
                "-U", "hfuse:r:-:h",
                "-U", "efuse:r:-:h",
                "-U", "lock:r:-:h"
            ]
            
            # Выполняем все операции
            success = True
            if not self.run_command(cmd_flash, "Считывание Flash"):
                success = False
            if not self.run_command(cmd_eeprom, "Считывание EEPROM"):
                success = False
                
            result = self.run_command(cmd_fuses, "Считывание фьюзов", capture_output=True)
            if result:
                with open(fuses_file, 'w') as f:
                    f.write(result.stdout + result.stderr)
            else:
                success = False
                
            if success:
                self.log_message(f"Чип успешно клонирован в папку: {project_dir}", "success")
                messagebox.showinfo("Успех", "Клонирование завершено успешно!\nЗамените чип и нажмите 'Подтвердить'")
            else:
                self.log_message("Ошибка при клонировании чипа", "error")
            
            self.set_status("Готов", 0.0)
            self.project_list.configure(values=self.get_existing_projects())
                
        threading.Thread(target=clone_thread, daemon=True).start()

    def restore_chip(self):
        project_name = self.project_name.get()
        if not project_name:
            messagebox.showwarning("Предупреждение", "Введите имя проекта")
            return
            
        if not self.validate_connection():
            return
            
        project_dir = self.backup_dir / project_name
        if not project_dir.exists():
            messagebox.showerror("Ошибка", f"Папка проекта {project_name} не найдена")
            return
            
        # Ищем последние файлы в папке проекта
        flash_files = list(project_dir.glob("*_flash_*.hex"))
        eeprom_files = list(project_dir.glob("*_eeprom_*.eep"))
        fuses_files = list(project_dir.glob("*_fuses_*.txt"))
        
        if not flash_files or not eeprom_files or not fuses_files:
            messagebox.showerror("Ошибка", "Не найдены файлы для восстановления")
            return
            
        # Берем самые свежие файлы
        latest_flash = max(flash_files, key=os.path.getmtime)
        latest_eeprom = max(eeprom_files, key=os.path.getmtime)
        latest_fuses = max(fuses_files, key=os.path.getmtime)
        
        def restore_thread():
            self.set_status("Восстановление чипа...", 0.5)
            
            # Восстанавливаем флеш
            cmd_flash = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"flash:w:{latest_flash}:i"
            ]
            
            # Восстанавливаем EEPROM
            cmd_eeprom = [
                str(self.avr_tools['avrdude']),
                "-p", self.boards[self.board_var.get()],
                "-c", "stk500v1",
                "-P", self.port_var.get(),
                "-b", self.baudrate_var.get(),
                "-U", f"eeprom:w:{latest_eeprom}:i"
            ]
            
            # Читаем фьюзы из файла
            try:
                with open(latest_fuses, 'r') as f:
                    fuses_content = f.read()
                
                fuses = {}
                for line in fuses_content.split('\n'):
                    if "lfuse" in line:
                        fuses['lfuse'] = line.split()[-1]
                    elif "hfuse" in line:
                        fuses['hfuse'] = line.split()[-1]
                    elif "efuse" in line:
                        fuses['efuse'] = line.split()[-1]
                    elif "lock" in line:
                        fuses['lock'] = line.split()[-1]
                
                # Восстанавливаем фьюзы
                if fuses:
                    cmd_fuses = [
                        str(self.avr_tools['avrdude']),
                        "-p", self.boards[self.board_var.get()],
                        "-c", "stk500v1",
                        "-P", self.port_var.get(),
                        "-b", self.baudrate_var.get()
                    ]
                    
                    if 'lfuse' in fuses:
                        cmd_fuses.extend(["-U", f"lfuse:w:{fuses['lfuse']}:m"])
                    if 'hfuse' in fuses:
                        cmd_fuses.extend(["-U", f"hfuse:w:{fuses['hfuse']}:m"])
                    if 'efuse' in fuses:
                        cmd_fuses.extend(["-U", f"efuse:w:{fuses['efuse']}:m"])
                    if 'lock' in fuses:
                        cmd_fuses.extend(["-U", f"lock:w:{fuses['lock']}:m"])
            except Exception as e:
                self.log_message(f"Ошибка чтения фьюзов: {str(e)}", "error")
                cmd_fuses = None
            
            # Выполняем все операции
            success = True
            if not self.run_command(cmd_flash, "Восстановление Flash"):
                success = False
            if not self.run_command(cmd_eeprom, "Восстановление EEPROM"):
                success = False
            if cmd_fuses and not self.run_command(cmd_fuses, "Восстановление фьюзов"):
                success = False
                
            if success:
                self.log_message("Чип успешно восстановлен", "success")
            else:
                self.log_message("Ошибка при восстановлении чипа", "error")
            
            self.set_status("Готов", 0.0)
                
        threading.Thread(target=restore_thread, daemon=True).start()

    # Контекстные меню
    def copy_console(self):
        self.clipboard_clear()
        text = self.console.get("1.0", "end-1c")
        self.clipboard_append(text)

    def clear_console(self):
        self.console.config(state='normal')
        self.console.delete("1.0", "end")
        self.console.config(state='disabled')

    def copy_hex(self):
        self.clipboard_clear()
        text = self.hex_content.get("sel.first", "sel.last")
        self.clipboard_append(text)

    def copy_eeprom(self):
        self.clipboard_clear()
        text = self.eeprom_content.get("sel.first", "sel.last")
        self.clipboard_append(text)

    # Вспомогательные функции
    def validate_connection(self):
        if not self.port_var.get():
            messagebox.showerror("Ошибка", "Выберите COM-порт")
            return False
        if not self.board_var.get():
            messagebox.showerror("Ошибка", "Выберите микроконтроллер")
            return False
        return True

    def set_status(self, text, progress):
        self.status_var.set(text)
        self.progress_var.set(progress)
        self.update_idletasks()

    def run_command(self, cmd, title, capture_output=False):
        self.log_message(f">>> {title}: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if capture_output:
                return result
                
            if result.returncode == 0:
                self.log_message(f"✅ {title} успешно завершена!", "success")
                return True
            else:
                self.log_message(result.stderr, "error")
                self.log_message(f"❌ Ошибка {title.lower()}!", "error")
                return False
        except subprocess.TimeoutExpired:
            self.log_message(f"❌ Таймаут выполнения команды {title.lower()}!", "error")
            return False
        except Exception as e:
            self.log_message(f"❌ Ошибка выполнения: {str(e)}", "error")
            return False

    def log_message(self, message, msg_type=None):
        self.console.config(state='normal')
        self.console.insert("end", message + "\n")
        if msg_type:
            self.console.tag_add(msg_type, "end-2c linestart", "end-1c")
        self.console.see("end")
        self.console.config(state='disabled')