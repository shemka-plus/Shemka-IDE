# utils/editor/file_manager.py
from tkinter import filedialog
from pathlib import Path


def new_file(self):
    self.editor.delete("1.0", "end")
    self.current_file = None
    self.log("Создан новый файл")


def open_file(self):
    file_path = filedialog.askopenfilename(filetypes=[("C Files", "*.cpp"), ("Arduino", "*.ino"), ("All Files", "*.*")])
    if file_path:
        self.load_file(file_path)


def save_file_as(self):
    file_path = filedialog.asksaveasfilename(defaultextension=".cpp", filetypes=[("C Files", "*.cpp"), ("Arduino", "*.ino"), ("All Files", "*.*")])
    if file_path:
        self.current_file = file_path
        self.save_file()
        self.config.add_recent_file(file_path)
        self.log(f"Файл сохранен как: {file_path}")


def save_file(self):
    if not self.current_file:
        file_path = filedialog.asksaveasfilename(defaultextension=".c")
        if not file_path:
            return
        self.current_file = file_path
    try:
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(self.editor.get("1.0", "end-1c"))
        self.config.add_recent_file(self.current_file)
        self.log(f"Сохранено: {self.current_file}")
    except Exception as e:
        self.log(f"Ошибка сохранения: {e}")


def load_file(self, path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.highlight_syntax()
        self.current_file = path
        self.config.add_recent_file(path)
        self.log(f"Открыт файл: {path}")
    except Exception as e:
        self.log(f"Ошибка открытия: {e}")


def show_recent_menu(self):
    self.recent_menu.delete(0, 'end')
    for file in self.config.recent_files:
        self.recent_menu.add_command(label=file, command=lambda f=file: self.load_file(f))
    try:
        self.recent_menu.tk_popup(self.recent_button.winfo_rootx(), self.recent_button.winfo_rooty() + 30)
    finally:
        self.recent_menu.grab_release()