import subprocess
from pathlib import Path
import threading
import os

class AVRUploader:
    def __init__(self, avr_tools, tools_root=None):
        self.avr_tools = avr_tools
        self.tools_root = Path(tools_root) if tools_root else Path(__file__).parent.parent.parent / "bin"
        self.tools_root = self.tools_root.resolve()
        self.bin_dir = self.tools_root / "bin"
        self.avrdude_conf = self.tools_root / "etc" / "avrdude.conf"  # Стандартный путь

    def upload(self, hex_path, mcu, programmer="arduino", port="COM1", baud="115200", callback=None):
        """Загружает прошивку в микроконтроллер"""
        def runner():
            try:
                cmd = [
                    str(self.avr_tools['avrdude']),
                    "-C", str(self.avrdude_conf),
                    "-p", mcu,
                    "-c", programmer,
                    "-P", port,
                    "-b", baud,
                    "-U", f"flash:w:{hex_path}:i"
                ]

                # Обновляем PATH
                env = os.environ.copy()
                env["PATH"] = os.pathsep.join([
                    str(self.bin_dir),
                    env.get("PATH", "")
                ])

                print(f"[Загрузка] {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)

                if callback:
                    if result.returncode == 0:
                        callback(True, None)
                    else:
                        callback(False, result.stderr)

            except Exception as e:
                if callback:
                    callback(False, str(e))

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        return thread
