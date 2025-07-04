import customtkinter as ctk
import serial.tools.list_ports

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, boards):
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("400x200")
        self.resizable(False, False)

        self.config = config
        self.boards = boards

        self._setup_ui()

    def _setup_ui(self):
        padding = {"padx": 10, "pady": 10}

        # COM-порт
        ctk.CTkLabel(self, text="COM-порт:").grid(row=0, column=0, sticky="w", **padding)
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_var = ctk.StringVar(value=self.config.get("port", ""))
        self.port_menu = ctk.CTkOptionMenu(self, variable=self.port_var, values=ports)
        self.port_menu.grid(row=0, column=1, **padding)

        # Плата
        ctk.CTkLabel(self, text="Плата:").grid(row=1, column=0, sticky="w", **padding)
        board_names = list(self.boards.keys())
        self.board_var = ctk.StringVar(value=self.config.get("board", ""))
        self.board_menu = ctk.CTkOptionMenu(self, variable=self.board_var, values=board_names)
        self.board_menu.grid(row=1, column=1, **padding)

        # Кнопки
        save_btn = ctk.CTkButton(self, text="Сохранить", command=self._save)
        save_btn.grid(row=2, column=0, columnspan=2, pady=(20, 10))

    def _save(self):
        self.config["port"] = self.port_var.get()
        self.config["board"] = self.board_var.get()
        self.destroy()
