# core/launcher.py

from gui.main_window import MainWindow
from gui.config_manager import ConfigManager
from pathlib import Path
import customtkinter as ctk


def run_ide():
    # Загрузка конфигурации
    config = ConfigManager()

    # Применение темы
    ctk.set_appearance_mode(config.config["theme"])
    ctk.set_default_color_theme(config.config["color_theme"])

    # Путь к корню компилятора
    TOOLS_ROOT = (Path(__file__).parent.parent / "bin").resolve()
    BIN_DIR = TOOLS_ROOT / "bin"

    # Подготовка путей к компилятору
    avr_tools = {
        'gcc': str(BIN_DIR / "avr-gcc.exe"),
        'objcopy': str(BIN_DIR / "avr-objcopy.exe"),
        'avrdude': "INTERNAL"  # больше не используется напрямую
    }

    boards = {
        "ATmega328P": "atmega328p",
        "ATmega328PB": "atmega328pb",
        "ATmega168PA": "m168p"
    }

    # Запуск главного окна
    app = MainWindow(avr_tools=avr_tools, boards=boards)
    app.mainloop()
