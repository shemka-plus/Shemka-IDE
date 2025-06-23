from gui.main_window import MainWindow
from gui.config_manager import ConfigManager
from pathlib import Path
import customtkinter as ctk
from core.compiler_manager import CompilerManager
import tkinter.messagebox as msgbox

def run_ide():
    # Загрузка конфигурации
    config = ConfigManager()

    # Применение темы
    ctk.set_appearance_mode(config.config["theme"])
    ctk.set_default_color_theme(config.config["color_theme"])

    # Путь к корню инструментов
    TOOLS_ROOT = (Path(__file__).parent.parent / "bin").resolve()
    BIN_DIR = TOOLS_ROOT / "bin"

    # Проверка и установка компилятора при первом запуске
    compiler_manager = CompilerManager()
    if not compiler_manager.is_installed():
        archives = compiler_manager.available_archives()
        if archives:
            if msgbox.askyesno("Установка компилятора", f"Компилятор не найден. Установить из {archives[0].name}?"):
                compiler_manager.install_from_archive(archives[0])
                msgbox.showinfo("Установлено", "Компилятор успешно установлен.")
        else:
            msgbox.showwarning("Нет компилятора", "Папка 'compilers/' пуста. Установите компилятор вручную.")

    # Подготовка путей к утилитам (если компилятор уже установлен)
    avr_tools = {
        'gcc': str(BIN_DIR / "avr-gcc.exe"),
        'objcopy': str(BIN_DIR / "avr-objcopy.exe"),
        'avrdude': str(BIN_DIR / "avrdude.exe")
    }

    boards = {
        "ATmega328P": "atmega328p",
        "ATmega328PB": "atmega328pb",
        "ATmega168PA": "atmega168pa"
    }

    app = MainWindow(avr_tools=avr_tools, boards=boards, tools_root=TOOLS_ROOT)
    app.mainloop()
