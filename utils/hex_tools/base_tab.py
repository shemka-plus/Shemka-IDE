# utils/hex_tools/base_tab.py

import os
import subprocess
from pathlib import Path
from tkinter import messagebox

class BaseTab:
    def __init__(self, console_callback=None):
        self.console_callback = console_callback

        self.root = Path(__file__).parent.parent.parent
        self.avrdude_dir = self.root / "module" / "avrdude" / "etc"
        self.avrdude = self.avrdude_dir / "avrdude.exe"
        self.avrdude_conf = self.avrdude_dir / "avrdude.conf"

    def log(self, message, error=False):
        if self.console_callback:
            self.console_callback(error, message)
        else:
            print(f"{'[ERR]' if error else '[LOG]'} {message}")

    def run_command(self, args, title=""):
        if not self.avrdude.exists():
            self.log(f"[Ошибка] avrdude не найден: {self.avrdude}", error=True)
            return

        cmd = [
            str(self.avrdude),
            "-C", str(self.avrdude_conf),
        ] + args

        self.log(f"{title}: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
            if process.returncode != 0:
                self.log(f"[Ошибка] Код возврата: {process.returncode}", error=True)
        except Exception as e:
            self.log(f"[Ошибка выполнения]: {e}", error=True)

    def validate_connection(self, mcu, port, baud, programmer):
        if not mcu or not port:
            messagebox.showerror("Ошибка", "Не выбран порт или МК")
            return False
        return True
