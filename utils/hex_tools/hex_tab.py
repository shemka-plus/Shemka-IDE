from .base_tab import BaseTab

class HexTab(BaseTab):
    def __init__(self, console_callback=None):
        super().__init__(console_callback)

    def flash_hex(self, mcu, port, baud, programmer, hex_path):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
            "-D",
            "-U", f"flash:w:{hex_path}:i"
        ]
        self.run_command(args, "Прошивка HEX")

    def read_hex(self, mcu, port, baud, programmer, output_path):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
            "-U", f"flash:r:{output_path}:i"
        ]
        self.run_command(args, "Чтение HEX")

    def verify_hex(self, mcu, port, baud, programmer, hex_path):
        if not self.validate_connection(mcu, port, baud, programmer):
            return
        args = [
            "-p", mcu.lower(),
            "-c", programmer,
            "-P", port,
            "-b", baud,
            "-U", f"flash:v:{hex_path}:i"
        ]
        self.run_command(args, "Верификация HEX")
