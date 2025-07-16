# gui/main_window.py

import customtkinter as ctk
from utils.editor.editor_tab import EditorTab
from utils.uart_monitor import UARTMonitorTab
from utils.collector_tab import CollectorTab
from .settings import SettingsTab
from .config_manager import ConfigManager
from utils.info_tab import InfoTab
from pathlib import Path
from core.theme_manager import ThemeManager
from utils.hex_tools.hex_tab_ui import HexTabUI

from utils.hex_tools.hex_tab import HexTab


class MainWindow(ctk.CTk):
    def __init__(self, avr_tools, boards):
        super().__init__()
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = ConfigManager()

        # Инициализация темы
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self)

        # Иконка и заголовок
        icon_path = Path(__file__).parent.parent / "data" / "Schemka-ico.ico"
        if icon_path.exists():
            self.iconbitmap(default=str(icon_path))

        from core.version import APP_VERSION
        self.title(f"shemka-IDE v{APP_VERSION}")
        self.geometry("1200x800")

        # UI
        self.setup_ui()
        self.theme_manager.apply_theme(self)

    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=5, pady=5)

        tabs = {
            "Редактор": EditorTab,
            "UART монитор": UARTMonitorTab,
            "HEX инструменты": HexTabUI,  # обновлённая ссылка
            "Собиратель": CollectorTab,
            "Инфо": InfoTab,
            "Настройки": SettingsTab
        }

        for name, tab_class in tabs.items():
            tab = self.tabview.add(name)

            if tab_class.__name__ == "HexTabUI":
                tab_instance = tab_class(tab)
            else:
                tab_instance = tab_class(
                    tab,
                    avr_tools=self.avr_tools,
                    boards=self.boards,
                    config=self.config,
                )


            #if tab_class is HexTab:
            #    tab_instance = tab_class(console_callback=self.log_to_console)
            #else:
            #    tab_instance = tab_class(
            #        tab,
            #        avr_tools=self.avr_tools,
            #        boards=self.boards,
            #        config=self.config,
            #    )

            self.theme_manager.apply_theme(tab_instance)
            tab_instance.pack(fill="both", expand=True)

    def log_to_console(self, error, message):
        prefix = "❌ " if error else "🟢 "
        if hasattr(self, "console"):
            self.console.configure(state="normal")
            self.console.insert("end", prefix + message + "\n")
            self.console.see("end")
            self.console.configure(state="disabled")
        else:
            print(prefix + message)
