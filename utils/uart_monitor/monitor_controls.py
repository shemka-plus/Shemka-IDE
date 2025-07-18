import threading
import serial
import serial.tools.list_ports
import datetime
from customtkinter import (
    CTkFrame, CTkButton, CTkOptionMenu, CTkEntry, CTkCheckBox, CTkImage
)
from tkinter import PhotoImage
from PIL import Image
#from .monitor_serial import SerialReader  # зарезервировано
from .theme import get_console_theme


class MonitorControls(CTkFrame):
    def __init__(self, master, display):
        super().__init__(master)
        self.display = display
        self.serial_port = None
        self.reader_thread = None
        self.running = False
        self.show_time = False

        # Обновить порты с иконкой
        #refresh_img = CTkImage(Image.open("docs/img/refresh.png"), size=(20, 20))
        self.refresh_btn = CTkButton(self, text="⮎", width=32, command=self.refresh_ports)
        self.refresh_btn.grid(row=0, column=0, padx=5)

        # Меню портов
        self.port_menu = CTkOptionMenu(self, values=self.get_ports())
        self.port_menu.grid(row=0, column=1, padx=5)

        # Скорость
        self.baud_menu = CTkOptionMenu(self, values=["9600", "19200", "38400", "57600", "115200"])
        self.baud_menu.set("9600")
        self.baud_menu.grid(row=0, column=2, padx=5)

        # Очистка
        self.clear_btn = CTkButton(self, text="Очистить", command=self.display.clear_text)
        self.clear_btn.grid(row=0, column=3, padx=5)

        # Время
        self.time_checkbox = CTkCheckBox(self, text="⏱", command=self.toggle_time)
        self.time_checkbox.grid(row=0, column=4, padx=5)

        # Ввод текста
        self.input_entry = CTkEntry(self.master, width=400)
        self.input_entry.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Кнопка отправки
        self.send_btn = CTkButton(self.master, text="Отправить", command=self.send_data)
        self.send_btn.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=0)
        self.grid_rowconfigure(0, weight=0)

        # После запуска открыть порт
        self.open_serial()

    def toggle_time(self):
        self.show_time = not self.show_time

    def refresh_ports(self):
        self.port_menu.configure(values=self.get_ports())
        ports = self.get_ports()
        if ports:
            self.port_menu.set(ports[0])

    def get_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] or ["Нет портов"]

    def open_serial(self):
        try:
            self.serial_port = serial.Serial(
                self.port_menu.get(),
                int(self.baud_menu.get()),
                timeout=0.1
            )
            self.running = True
            self.reader_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            self.display.append_text(f"[Ошибка открытия порта] {e}\n")

    def read_serial(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.readline()
                if data:
                    text = data.decode(errors="ignore")
                    if self.show_time:
                        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
                        text = timestamp + text
                    self.display.append_text(text)
            except Exception as e:
                self.display.append_text(f"[Ошибка чтения] {e}\n")
                break

    def send_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                text = self.input_entry.get()
                if text:
                    self.serial_port.write((text + "\n").encode())
                    self.input_entry.delete(0, "end")
            except Exception as e:
                self.display.append_text(f"[Ошибка отправки] {e}\n")

    def update_theme(self):
        pass
