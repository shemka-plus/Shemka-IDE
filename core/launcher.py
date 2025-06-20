from gui.main_window import MainWindow
from gui.config_manager import ConfigManager
from pathlib import Path
import customtkinter as ctk
#import os

def run_ide():
    # Загрузка конфигурации
    config = ConfigManager()

    # Применение темы
    ctk.set_appearance_mode(config.config["theme"])
    ctk.set_default_color_theme(config.config["color_theme"])

    # Путь к корневой папке инструментов (где лежат bin/, lib/, include/, device-specs/)
    TOOLS_ROOT = (Path(__file__).parent.parent / "bin").resolve()
    BIN_DIR = TOOLS_ROOT / "bin"  # Где avr-gcc.exe и т.п.

    # Проверка обязательных файлов
    required_files = {
        'gcc': BIN_DIR / "avr-gcc.exe",
        'objcopy': BIN_DIR / "avr-objcopy.exe",
        'avrdude': BIN_DIR / "avrdude.exe",
        'specs': TOOLS_ROOT / "device-specs" / "specs-atmega328p",
        'includes': TOOLS_ROOT / "include"
    }

    print("🔍 Проверка путей:")
    for name, path in required_files.items():
        print(f"{name}: {path} | Существует: {path.exists()}")

    missing = [name for name, path in required_files.items() if not path.exists()]
    if missing:
        error_msg = f"❌ Отсутствуют файлы: {', '.join(missing)}\n" \
                    f"Скопируйте их из Arduino IDE в папку:\n{TOOLS_ROOT}"
        print(error_msg)
        return

    avr_tools = {
        'gcc': str(required_files['gcc']),
        'objcopy': str(required_files['objcopy']),
        'avrdude': str(required_files['avrdude'])
    }

    # Поддерживаемые платы
    boards = {
        "ATmega328P": "atmega328p",
        "ATmega328PB": "atmega328pb",
        "ATmega168PA": "atmega168pa"
    }

    # Запуск главного окна
    app = MainWindow(avr_tools=avr_tools, boards=boards, tools_root=TOOLS_ROOT)
    app.mainloop()
