# gui/shared_panel.py
import customtkinter as ctk
import serial.tools.list_ports
from PIL import Image
from .config_manager import ConfigManager

class SharedPanel(ctk.CTkFrame):
    """Общая панель инструментов для всех вкладок"""
    def __init__(self, parent, config, boards):
        super().__init__(parent)
        self.config = config
        self.boards = boards
        
        # Настройка сетки
        self.grid_columnconfigure(4, weight=1)
        
        # Логотип (справа)
        self.logo_image = ctk.CTkImage(
            light_image=Image.open("logo.png"),
            dark_image=Image.open("logo.png"),
            size=(196, 42)
        )
        self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.logo_label.grid(row=0, column=4, rowspan=2, padx=5)
        
        # COM-порт
        ctk.CTkLabel(self, text="COM:").grid(row=0, column=0, padx=2)
        self.port_var = ctk.StringVar(value=self.config.config["com_port"])
        self.port_menu = ctk.CTkOptionMenu(
            self, 
            variable=self.port_var,
            width=100
        )
        self.port_menu.grid(row=0, column=1, padx=2)
        
        # Кнопка обновления портов
        ctk.CTkButton(
            self,
            text="↻",
            width=30,
            command=self.update_ports
        ).grid(row=0, column=2, padx=2)
        
        # Скорость соединения
        ctk.CTkLabel(self, text="Скорость:").grid(row=0, column=3, padx=2)
        self.baudrate_var = ctk.StringVar(value=self.config.config["baudrate"])
        ctk.CTkOptionMenu(
            self,
            variable=self.baudrate_var,
            values=["9600", "19200", "57600", "115200"],
            width=100
        ).grid(row=0, column=4, padx=2)
        
        # Выбор микроконтроллера
        ctk.CTkLabel(self, text="МК:").grid(row=1, column=0, padx=2)
        self.board_var = ctk.StringVar(value=self.config.config["mcu"])
        ctk.CTkOptionMenu(
            self,
            variable=self.board_var,
            values=list(self.boards.keys()),
            width=100
        ).grid(row=1, column=1, padx=2)
        
        # Кнопка сохранения настроек
        ctk.CTkButton(
            self,
            text="Сохранить настройки",
            command=self.save_settings,
            width=150
        ).grid(row=1, column=2, columnspan=3, padx=2)
        
        self.update_ports()

    def update_ports(self):
        """Обновляет список доступных COM-портов"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_menu.configure(values=ports)
            if ports:
                if self.config.config["com_port"] in ports:
                    self.port_var.set(self.config.config["com_port"])
                else:
                    self.port_var.set(ports[0])
        except Exception as e:
            print(f"Ошибка обновления портов: {e}")

    def save_settings(self):
        """Сохраняет текущие настройки подключения"""
        self.config.set_com_settings(
            self.port_var.get(),
            self.baudrate_var.get(),
            self.board_var.get()
        )
        ctk.CTkLabel(self, text="Сохранено!", text_color="green").grid(row=1, column=5, padx=5)
        self.after(2000, lambda: self.grid_slaves(row=1, column=5)[0].destroy())