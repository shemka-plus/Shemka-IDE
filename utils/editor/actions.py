# utils/editor/actions.py
from pathlib import Path

def compile_code(self):
    source = self.editor.get("1.0", "end-1c")
    mcu = self.mcu_var.get()

    def cb(success, message, errors):
        self.compile_callback(success, message, errors)

    self.compiler.compile(source, mcu, output_dir="build", callback=cb)

def compile_callback(self, success, message, errors=[]):
    self.log(message)
    if hasattr(self, "editor"):
        self.editor.tag_delete("error")
    if success:
        return
    if errors:
        self.highlight_errors(errors)

def upload_code(self):
    hex_path = Path("build/sketch.hex")
    if not hex_path.exists():
        self.log("HEX-файл не найден. Сначала выполните компиляцию.")
        return

    port = self.com_var.get()
    mcu = self.mcu_var.get()

    def cb(success, message):
        self.upload_callback(success, message)

    self.uploader.upload(str(hex_path), port=port, mcu=mcu, callback=cb)

def upload_callback(self, success, message):
    self.log(message)
