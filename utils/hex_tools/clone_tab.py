from .base_tab import BaseTab

class CloneTab(BaseTab):
    def __init__(self, console_callback=None):
        super().__init__(console_callback)

    def clone_chip(self, mcu, port, baud, programmer, output_prefix):
        if not self.validate_connection(mcu, port, baud, programmer):
            return

        tasks = [
            ("flash", f"{output_prefix}_flash.hex"),
            ("eeprom", f"{output_prefix}_eeprom.hex"),
            ("lfuse", f"{output_prefix}_lfuse.txt"),
            ("hfuse", f"{output_prefix}_hfuse.txt"),
            ("efuse", f"{output_prefix}_efuse.txt"),
        ]

        for section, out in tasks:
            if section in ["flash", "eeprom"]:
                fmt = "i"
            else:
                fmt = "h"
            args = [
                "-p", mcu.lower(),
                "-c", programmer,
                "-P", port,
                "-b", baud,
                "-U", f"{section}:r:{out}:{fmt}"
            ]
            self.run_command(args, f"Чтение {section.upper()}")

    def restore_chip(self, mcu, port, baud, programmer, input_prefix):
        if not self.validate_connection(mcu, port, baud, programmer):
            return

        tasks = [
            ("flash", f"{input_prefix}_flash.hex"),
            ("eeprom", f"{input_prefix}_eeprom.hex"),
        ]

        for section, inp in tasks:
            args = [
                "-p", mcu.lower(),
                "-c", programmer,
                "-P", port,
                "-b", baud,
                "-U", f"{section}:w:{inp}:i"
            ]
            self.run_command(args, f"Запись {section.upper()}")
