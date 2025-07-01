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
from core.theme_manager import ThemeManager  # Прямой импорт из модуля


class MainWindow(ctk.CTk):
    def __init__(self, avr_tools, boards, tools_root=None):
        super().__init__()
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = ConfigManager()
        self.tools_root = tools_root
        
        # Инициализация theme_manager
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self)

        # Установка иконки
        icon_path = Path(__file__).parent.parent / "data" / "Schemka-ico.ico"
        if icon_path.exists():
            self.iconbitmap(default=str(icon_path))

        from core.version import APP_VERSION
        self.title(f"shemka-IDE v{APP_VERSION}")

        # Применяем тему
        ctk.set_appearance_mode(self.config.config["theme"])
        ctk.set_default_color_theme(self.config.config["color_theme"])

        self.geometry("1200x800")
        self.setup_ui()
        
        # Применяем тему ко всему окну
        self.theme_manager.apply_theme(self)

    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=5, pady=5)

        tabs = {
            "Редактор": EditorTab,
            "UART монитор": UARTMonitorTab,
            "HEX инструменты": HexToolsTab,
            "Собиратель": CollectorTab,
            "Инфо": InfoTab,
            "Настройки": SettingsTab
        }

        for name, tab_class in tabs.items():
            tab = self.tabview.add(name)
            tab_instance = tab_class(
                tab,
                avr_tools=self.avr_tools,
                boards=self.boards,
                config=self.config,
                tools_root=self.tools_root
            )
            # Применяем тему к каждой вкладке
            self.theme_manager.apply_theme(tab_instance)
            tab_instance.pack(fill="both", expand=True)