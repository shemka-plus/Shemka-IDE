# gui/main_window.py
import customtkinter as ctk
from utils.editor.editor_tab import EditorTab
from utils.hex_tools import HexToolsTab
from utils.uart_monitor import UARTMonitorTab
from utils.collector_tab import CollectorTab
from .settings import SettingsTab
from .config_manager import ConfigManager
from utils.info_tab import InfoTab
from pathlib import Path


class MainWindow(ctk.CTk):
    def __init__(self, avr_tools, boards, tools_root=None):
        super().__init__()
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = ConfigManager()
        self.tools_root = tools_root  # ✅ Новый аргумент

        icon_path = Path(__file__).parent.parent / "data" / "Schemka-ico.ico"
        if icon_path.exists():
            self.iconbitmap(default=str(icon_path))

            from core.version import APP_VERSION
            self.title(f"shemka-IDE v{APP_VERSION}")


        # Применяем тему
        ctk.set_appearance_mode(self.config.config["theme"])
        ctk.set_default_color_theme(self.config.config["color_theme"])

        #self.title("shemka-IDE")
        self.geometry("1200x800")
        self.setup_ui()

    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=5, pady=5)

        tabs = {
            "Редактор": EditorTab,
            "UART монитор": UARTMonitorTab,
            "HEX инструменты": HexToolsTab,
            "Собиратель": CollectorTab,
            "Инфо": InfoTab, #lambda parent: InfoTab(parent, app_version=self.app_version),
            "Настройки": SettingsTab
        }

        for name, tab_class in tabs.items():
            tab = self.tabview.add(name)
            tab_instance = tab_class(
                tab,
                avr_tools=self.avr_tools,
                boards=self.boards,
                config=self.config,
                tools_root=self.tools_root  # ✅ Передаём в редактор
            )
            tab_instance.pack(fill="both", expand=True)
