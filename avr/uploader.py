import subprocess
import threading
import os
from pathlib import Path
import serial
import time
from gui.config_manager import ConfigManager

class AVRUploader:
    def __init__(self, tools_root=None):
        avrdude_dir = Path(__file__).parent.parent / "module" / "avrdude" / "etc"
        self.avr_tools = {
            "avrdude": avrdude_dir / "avrdude.exe"
        }
        self.avrdude_conf = avrdude_dir / "avrdude.conf"
        self.avrdude_env_dir = avrdude_dir

    def upload(self, *, hex_path, mcu=None, port=None, baud=None, programmer=None, uploader_type=None, callback=None):
        config = ConfigManager()

        uploader_type = uploader_type or config.get_uploader_type()
        bootloader = config.get_bootloader()
        mcu = mcu or config.config.get("mcu", "ATmega328P")
        port = port or config.config.get("com_port", "")
        hex_path = Path(hex_path)

        boards = {
            "ATmega328P": "atmega328p",
            "ATmega328PB": "atmega328pb",
            "ATmega168PA": "m168p"
        }

        partno = boards.get(mcu, "atmega328p")
        programmer = "stk500v1" if uploader_type == "isp" else "arduino"

        # Определим скорость
        if not baud:
            if uploader_type == "uart":
                if bootloader == "old":
                    baud = "57600"
                elif bootloader == "new":
                    baud = "115200"
                else:  # auto
                    baud = "57600" if "168" in partno else "115200"
            else:
                baud = config.config.get("baudrate", "19200")

        def pulse_dtr(port_name):
            try:
                with serial.Serial(port=port_name, baudrate=1200) as ser:
                    ser.dtr = False
                    time.sleep(0.05)
                    ser.dtr = True
                    time.sleep(0.05)
            except Exception as e:
                if callback:
                    callback(False, f"[DTR] Не удалось сбросить порт: {e}")

        def run_avrdude():
            try:
                cmd = [
                    str(self.avr_tools['avrdude']),
                    "-C", str(self.avrdude_conf),
                    "-p", partno,
                    "-c", programmer,
                    "-P", port,
                    "-b", str(baud),
                    "-D",
                    "-U", f"flash:w:{hex_path}:i"
                ]

                if not self.avr_tools["avrdude"].exists():
                    if callback:
                        callback(False, f"[Ошибка] avrdude не найден: {self.avr_tools['avrdude']}")
                    return

                # Сброс через DTR перед прошивкой
                if uploader_type == "uart":
                    pulse_dtr(port)
                    time.sleep(1.5)  # дать загрузчику активироваться

                if callback:
                    callback(True, f"[Загрузка] {' '.join(cmd)}")

                env = os.environ.copy()
                env["PATH"] = os.pathsep.join([
                    str(self.avrdude_env_dir),
                    env.get("PATH", "")
                ])

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )

                for line in process.stdout:
                    if callback:
                        callback(True, line.strip())

                process.wait()
                if process.returncode == 0:
                    if callback:
                        callback(True, "[OK] Загрузка завершена успешно.")
                else:
                    if callback:
                        callback(False, "[Ошибка] avrdude завершился с кодом " + str(process.returncode))

            except Exception as e:
                if callback:
                    callback(False, f"[Ошибка выполнения avrdude] {e}")

        # Запуск в отдельном потоке
        threading.Thread(target=run_avrdude, daemon=True).start()
