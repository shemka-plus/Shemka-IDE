# utils/hex_tools/hex_tab_ui.py

import customtkinter as ctk
from tkinter import filedialog, StringVar
from utils.hex_tools.hex_tab import HexTab
from utils.hex_tools.eeprom_tab import EepromTab
from utils.hex_tools.fuses_tab import FusesTab
from utils.hex_tools.clone_tab import CloneTab
import os
from gui.config_manager import ConfigManager
import serial.tools.list_ports
from pathlib import Path


# Простой Tooltip для customtkinter
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text="Подсказка", delay=500):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.delay = delay
        self._add_events()

    def _add_events(self):
        self.widget.bind("<Enter>", self._schedule)
        self.widget.bind("<Leave>", self._unschedule)

    def _schedule(self, event=None):
        self._unschedule()
        self.id = self.widget.after(self.delay, self._show_tooltip)

    def _unschedule(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        self._hide_tooltip()

    def _show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 30
        y += self.widget.winfo_rooty() + cy + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("tahoma", "9", "normal")
        )
        label.pack(ipadx=5, ipady=2)

    def _hide_tooltip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None



class HexTabUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config_manager = ConfigManager()

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
        tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_hex_tab(tabs.add("HEX"))
        self.create_eeprom_tab(tabs.add("EEPROM"))
        self.create_fuses_tab(tabs.add("Фьюзы"))
        self.create_clone_tab(tabs.add("Клон"))

        # HEX Viewer
        self.viewer = ctk.CTkTextbox(self, height=200)
        self.viewer.pack(fill="both", padx=10, pady=(0, 5))
        self.viewer.configure(state="disabled", font=("Courier New", 11))

        # Консоль
        self.console = ctk.CTkTextbox(self, height=120)
        self.console.pack(fill="x", padx=10, pady=(0, 10))
        self.console.configure(state="disabled")

    #def create_hex_tab(self, tab):
    #    ctk.CTkButton(tab, text="Открыть HEX", command=self.open_hex).pack(pady=2)
    #    ctk.CTkButton(tab, text="Сохранить HEX", command=self.save_hex).pack(pady=2)
    #    ctk.CTkButton(tab, text="Прошить", command=self.flash_hex).pack(pady=2)
    #    ctk.CTkButton(tab, text="Считать", command=self.read_hex).pack(pady=2)
    #    ctk.CTkButton(tab, text="Верифицировать", command=self.verify_hex).pack(pady=2)
    #    ctk.CTkButton(tab, text="Очистить чип", command=self.erase_chip).pack(pady=2)
    def create_hex_tab(self, tab):
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=5, fill="x")

        buttons = [
            ("📂", "Открыть HEX", self.open_hex),
            ("💾", "Сохранить HEX", self.save_hex),
            ("🧩", "Прошить", self.flash_hex),
            ("📥", "Считать", self.read_hex),
            ("📏", "Верифицировать", self.verify_hex),
            ("❌", "Очистить чип", self.erase_chip),
        ]

        for icon, tooltip, cmd in buttons:
            btn = ctk.CTkButton(btn_frame, text=icon, width=36, height=36, command=cmd)
            btn.pack(side="left", padx=6)
            ToolTip(btn, text=tooltip)


    def create_eeprom_tab(self, tab):
        ctk.CTkButton(tab, text="Чтение EEPROM", command=self.read_eeprom).pack(pady=10)
        ctk.CTkButton(tab, text="Запись EEPROM", command=self.write_eeprom).pack(pady=10)

    def create_fuses_tab(self, tab):
        self.fuse_l = StringVar()
        self.fuse_h = StringVar()
        self.fuse_e = StringVar()
        for i, (label, var) in enumerate([("LFuse", self.fuse_l), ("HFuse", self.fuse_h), ("EFuse", self.fuse_e)]):
            ctk.CTkLabel(tab, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="e")
            ctk.CTkEntry(tab, textvariable=var, width=100).grid(row=i, column=1, pady=2)
        ctk.CTkButton(tab, text="Чтение", command=self.read_fuses).grid(row=3, column=0, pady=10)
        ctk.CTkButton(tab, text="Запись", command=self.write_fuses).grid(row=3, column=1, pady=10)

    def create_clone_tab(self, tab):
        ctk.CTkLabel(tab, text="Имя проекта:").pack(pady=(10, 2))
        ctk.CTkEntry(tab, textvariable=self.project_name).pack(pady=2)

        ctk.CTkLabel(tab, text="Сохранённые проекты:").pack(pady=(10, 2))
        self.project_list = ctk.CTkOptionMenu(tab, variable=self.saved_project, values=self.get_saved_projects())
        self.project_list.pack(pady=2)

        ctk.CTkButton(tab, text="Клонировать чип", command=self.clone_chip).pack(pady=10)
        ctk.CTkButton(tab, text="Восстановить чип", command=self.restore_chip).pack(pady=2)

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

    #def read_hex(self):
    #    path = self.hex_path.get() or "read_flash.hex"
    #    self.hex.read_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), path)
#
    #def verify_hex(self):
    #    self.hex.verify_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), self.hex_path.get())
    def read_hex(self):
        path = self.hex_path.get() or "read_flash.hex"
        self.log(False, "[Чтение HEX]...")
        self.hex.read_hex(self.mcu.get(), self.port.get(), self.baud.get(), self.programmer.get(), path)
        self.show_hex_file(path)

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
