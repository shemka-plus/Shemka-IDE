import customtkinter as ctk
import serial.tools.list_ports
from tkinter import font as tkfont
from pathlib import Path


class EditorSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, mcu_var, com_var, boards,
                 font_family, font_size, uploader_type="uart", bootloader="auto"):
        super().__init__(parent)
        self.title("Настройки редактора")
        self.geometry("420x480")
        self.resizable(False, False)

        # Иконка
        icon_path = Path(__file__).parent.parent.parent / "data" / "Schemka-ico.ico"
        if icon_path.exists():
            self.iconbitmap(icon_path)

        self.transient(parent)
        self.grab_set()

        self.mcu_var = mcu_var
        self.com_var = com_var
        self.boards = boards
        self.font_family = font_family  # ctk.StringVar
        self.font_size = font_size      # ctk.IntVar
        self.uploader_var = ctk.StringVar(value=uploader_type)
        self.bootloader_var = ctk.StringVar(value=bootloader)

        # Вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Микроконтроллер")
        self.tabview.add("Порт")
        self.tabview.add("Шрифт")

        self._setup_mcu_tab()
        self._setup_port_tab()
        self._setup_font_tab()

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="Применить", command=self._apply_settings).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy).pack(side="right", padx=5)

        self._center_window()
        self._toggle_bootloader_options()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def _setup_mcu_tab(self):
        tab = self.tabview.tab("Микроконтроллер")
        ctk.CTkLabel(tab, text="Выберите микроконтроллер:").pack(pady=(10, 5))

        for mcu in self.boards.keys():
            ctk.CTkRadioButton(
                tab,
                text=mcu,
                variable=self.mcu_var,
                value=mcu
            ).pack(anchor="w", padx=20, pady=2)

    def _setup_port_tab(self):
        tab = self.tabview.tab("Порт")
        ctk.CTkLabel(tab, text="Выберите COM-порт:").pack(pady=(10, 5))

        try:
            self.ports = [port.device for port in serial.tools.list_ports.comports()]
            if not self.ports:
                ctk.CTkLabel(tab, text="Нет доступных COM-портов").pack()
            else:
                for port in self.ports:
                    ctk.CTkRadioButton(
                        tab,
                        text=port,
                        variable=self.com_var,
                        value=port
                    ).pack(anchor="w", padx=20, pady=2)
        except Exception as e:
            ctk.CTkLabel(tab, text=f"Ошибка получения портов: {str(e)}").pack()

        ctk.CTkLabel(tab, text="Метод прошивки:").pack(pady=(10, 5))
        uploader_frame = ctk.CTkFrame(tab)
        uploader_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkRadioButton(uploader_frame, text="UART", variable=self.uploader_var, value="uart",
                           command=self._toggle_bootloader_options).pack(anchor="w")
        ctk.CTkRadioButton(uploader_frame, text="ISP", variable=self.uploader_var, value="isp",
                           command=self._toggle_bootloader_options).pack(anchor="w")

        self.bootloader_frame = ctk.CTkFrame(tab)
        self.bootloader_frame.pack(fill="x", padx=20, pady=(5, 0))

        ctk.CTkLabel(self.bootloader_frame, text="Загрузчик (UART):").pack(anchor="w", pady=(5, 0))
        ctk.CTkRadioButton(self.bootloader_frame, text="Новый", variable=self.bootloader_var, value="new").pack(anchor="w")
        ctk.CTkRadioButton(self.bootloader_frame, text="Старый", variable=self.bootloader_var, value="old").pack(anchor="w")
        ctk.CTkRadioButton(self.bootloader_frame, text="Авто", variable=self.bootloader_var, value="auto").pack(anchor="w")

    def _setup_font_tab(self):
        tab = self.tabview.tab("Шрифт")
        ctk.CTkLabel(tab, text="Шрифт:").pack(pady=(10, 5))

        font_families = sorted(tkfont.families())
        ctk.CTkOptionMenu(
            tab,
            values=font_families,
            variable=self.font_family
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(tab, text="Размер:").pack(pady=(10, 5))
        ctk.CTkOptionMenu(
            tab,
            values=["8", "10", "12", "14", "16", "18", "20", "22", "24"],
            variable=self.font_size
        ).pack(fill="x", padx=20, pady=5)

    def _toggle_bootloader_options(self):
        if self.uploader_var.get() == "uart":
            self.bootloader_frame.pack(fill="x", padx=20, pady=(5, 0))
        else:
            self.bootloader_frame.pack_forget()

    def _apply_settings(self):
        if self.mcu_var.get() == "ATmega328P (Old Bootloader)":
            self.mcu_var.set("ATmega328P")
            self.bootloader_var.set("old")

        config = self.master.config
        config.config["com_port"] = self.com_var.get()
        config.config["mcu"] = self.mcu_var.get()
        config.config["uploader_type"] = self.uploader_var.get()
        config.config["bootloader"] = self.bootloader_var.get()
        config.config["font_family"] = self.font_family.get()
        config.config["font_size"] = self.font_size.get()
        config.save_config()

        self.destroy()
