# utils/editor/actions.py
import threading
from core.compiler_manager import CompilerManager
from tkinter import messagebox


def compile_code(self):
    mgr = CompilerManager()
    if not mgr.is_installed():
        if messagebox.askyesno("Нет компилятора", "Компилятор не установлен. Установить сейчас?"):
            archives = mgr.available_archives()
            if not archives:
                messagebox.showerror("Ошибка", "Нет архивов в папке compilers/")
                return
            mgr.install_from_archive(archives[0])
            messagebox.showinfo("Установлено", f"Установлен компилятор из {archives[0].name}")
        else:
            return

    code = self.editor.get("1.0", "end-1c")
    mcu = self.boards.get(self.mcu_var.get())
    self.log("=== Компиляция ===")

    def run_compile():
        self.compiler.compile(code, mcu, callback=self.compile_callback)

    threading.Thread(target=run_compile, daemon=True).start()


def compile_callback(self, success, output):
    self.log(output or "")
    if success:
        self.log("Компиляция завершена успешно")
    else:
        self.log("Ошибка компиляции")


def upload_code(self):
    from pathlib import Path
    hex_path = Path("build/sketch.hex")
    if not hex_path.exists():
        self.log("HEX-файл не найден. Сначала скомпилируйте проект.")
        return
    mcu = self.boards.get(self.mcu_var.get())
    port = self.com_var.get()
    self.log("=== Прошивка ===")
    self.uploader.upload(str(hex_path), mcu, port=port, callback=self.upload_callback)


def upload_callback(self, success, output):
    self.log(output or "")
    if success:
        self.log("Прошивка завершена успешно")
    else:
        self.log("Ошибка прошивки")