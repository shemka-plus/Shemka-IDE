# utils/hex_tools/fuses_tab.py

from .base_tab import BaseTab

class FusesTab(BaseTab):
    def __init__(self, console_callback=None):
        super().__init__(console_callback)

    def read_fuses(self, mcu, port, baud, programmer):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        for fuse in ["lfuse", "hfuse", "efuse"]:
            args = [
                "-p", mcu.lower(),
                "-c", programmer,
                "-P", port,
                "-b", baud,
                "-U", f"{fuse}:r:-:h"
            ]
            self.run_command(args, f"Чтение {fuse.upper()}")

    def write_fuses(self, mcu, port, baud, programmer, lfuse=None, hfuse=None, efuse=None):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        fuse_args = []
        if lfuse:
            fuse_args.append(f"-U lfuse:w:{lfuse}:m")
        if hfuse:
            fuse_args.append(f"-U hfuse:w:{hfuse}:m")
        if efuse:
            fuse_args.append(f"-U efuse:w:{efuse}:m")

        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
        ] + fuse_args

        self.run_command(args, "Запись фьюзов")
