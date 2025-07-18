from .base_tab import BaseTab

class EepromTab(BaseTab):
    def __init__(self, console_callback=None):
        super().__init__(console_callback)

    def read_eeprom(self, mcu, port, baud, programmer, output_path):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
            "-U", f"eeprom:r:{output_path}:i"
        ]
        self.run_command(args, "Чтение EEPROM")
        if self.console_callback:
            self.console_callback(False, f"[EEPROM] Содержимое сохранено в {output_path}")

    def write_eeprom(self, mcu, port, baud, programmer, hex_path):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
            "-U", f"eeprom:w:{hex_path}:i"
        ]
        self.run_command(args, "Запись EEPROM")
