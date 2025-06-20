import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from core.version import APP_VERSION

POPULAR_EXTENSIONS = [".py", ".cpp", ".h", ".c", ".txt"]

class CollectorTab(ctk.CTkFrame):
    def __init__(self, parent, app_version="?", **kwargs):
        super().__init__(parent)
        self.version = APP_VERSION
        self.setup_ui()


    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Объединение")
        self.tabview.add("Разделение")
        self.tabview.add("Структура")

        self.setup_collect_tab()
        self.setup_split_tab()
        self.setup_structure_tab()

    def setup_collect_tab(self):
        frame = self.tabview.tab("Объединение")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame, text="Папка с исходными файлами:").grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")
        self.entry_src = ctk.CTkEntry(frame, placeholder_text="Путь к исходной папке")
        self.entry_src.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(frame, text="Выбрать...", command=lambda: self.select_directory(self.entry_src)).grid(row=2, column=0, padx=5, pady=5)

        ext_frame = ctk.CTkFrame(frame)
        ext_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(ext_frame, text="Расширения (через запятую):").pack(pady=(5, 0))
        self.entry_ext = ctk.CTkEntry(ext_frame, placeholder_text=".py,.h")
        self.entry_ext.pack(fill="x", padx=10, pady=5)
        self.entry_ext.insert(0, ",".join(POPULAR_EXTENSIONS[:2]))
        ctk.CTkOptionMenu(ext_frame, values=POPULAR_EXTENSIONS, command=self.add_extension).pack(pady=5)
        ctk.CTkButton(ext_frame, text="Объединить файлы", command=self.collect_files).pack(pady=10)

        ctk.CTkLabel(frame, text="Файл для сохранения результата:").grid(row=0, column=2, padx=5, pady=(5, 0), sticky="w")
        self.entry_output = ctk.CTkEntry(frame, placeholder_text="Путь к выходному файлу")
        self.entry_output.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(frame, text="Сохранить как...", command=lambda: self.select_output_file(self.entry_output)).grid(row=2, column=2, padx=5, pady=5)

        self.console = ctk.CTkTextbox(frame, height=100)
        self.console.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.console.configure(state="disabled")
        frame.grid_rowconfigure(3, weight=1)

    def setup_split_tab(self):
        frame = self.tabview.tab("Разделение")

        ctk.CTkLabel(frame, text="Файл для разбора:").pack(pady=(10, 0))
        self.entry_input = ctk.CTkEntry(frame, width=500, placeholder_text="Файл для разбора")
        self.entry_input.pack(pady=5)
        ctk.CTkButton(frame, text="Выбрать файл", command=lambda: self.select_input_file(self.entry_input)).pack()

        ctk.CTkLabel(frame, text="Папка для сохранения файлов:").pack(pady=(10, 0))
        self.entry_dest = ctk.CTkEntry(frame, width=500, placeholder_text="Куда разложить")
        self.entry_dest.pack(pady=5)
        ctk.CTkButton(frame, text="Выбрать папку", command=lambda: self.select_directory(self.entry_dest)).pack()

        ctk.CTkButton(frame, text="Разделить файл", command=self.split_file).pack(pady=10)

    def setup_structure_tab(self):
        frame = self.tabview.tab("Структура")

        ctk.CTkLabel(frame, text="Папка для сканирования:").pack(pady=(10, 0))
        self.entry_struct_src = ctk.CTkEntry(frame, width=500, placeholder_text="Папка для сканирования")
        self.entry_struct_src.pack(pady=5)
        ctk.CTkButton(frame, text="Выбрать...", command=lambda: self.select_directory(self.entry_struct_src)).pack()

        ctk.CTkLabel(frame, text="Файл для сохранения структуры:").pack(pady=(10, 0))
        self.entry_struct_output = ctk.CTkEntry(frame, width=500, placeholder_text="Файл для сохранения структуры")
        self.entry_struct_output.pack(pady=5)
        ctk.CTkButton(frame, text="Сохранить как...", command=lambda: self.select_output_file(self.entry_struct_output)).pack()

        ctk.CTkButton(frame, text="Сохранить структуру", command=self.save_structure).pack(pady=10)

    def select_directory(self, entry_widget):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, os.path.normpath(path))

    def select_input_file(self, entry_widget):
        path = filedialog.askopenfilename()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, os.path.normpath(path))

    def select_output_file(self, entry_widget):
        extensions = self.entry_ext.get().split(',')
        ext = extensions[0] if extensions else ".txt"
        path = filedialog.asksaveasfilename(defaultextension=ext.strip())
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, os.path.normpath(path))

    def add_extension(self, value):
        current = self.entry_ext.get().strip()
        values = [v.strip() for v in current.split(',') if v.strip()]
        if value not in values:
            values.append(value)
            self.entry_ext.delete(0, "end")
            self.entry_ext.insert(0, ",".join(values))

    def collect_files(self):
        src = self.entry_src.get()
        out_file = self.entry_output.get()
        exts = [e.strip() for e in self.entry_ext.get().split(',') if e.strip()]

        if not all([src, out_file, exts]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        total_files, total_lines, total_chars = 0, 0, 0
        try:
            with open(out_file, 'w', encoding='utf-8') as outfile:
                outfile.write(f"### COLLECTOR {self.version} ###\n### OS: {os.name} ###\n\n")
                for root, _, files in os.walk(src):
                    for fname in files:
                        if any(fname.endswith(ext) for ext in exts):
                            fpath = os.path.join(root, fname)
                            try:
                                with open(fpath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    lines = content.count('\n') + 1
                                    chars = len(content)
                                    rel = os.path.relpath(fpath, src).replace("\\", "/")
                                    outfile.write(f"### FILE BEGIN: {rel} ###\n{content}\n### FILE END ###\n\n")
                                    total_files += 1
                                    total_lines += lines
                                    total_chars += chars
                            except Exception as e:
                                self.log(f"[ERROR] {fpath} пропущен: {str(e)}")

            self.log(f"[INFO] Объединено файлов: {total_files}, строк: {total_lines}, символов: {total_chars}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка объединения: {e}")

    def split_file(self):
        input_file = self.entry_input.get()
        dest_dir = self.entry_dest.get()
        if not all([input_file, dest_dir]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = content.split('### FILE BEGIN: ')[1:]
            total = 0
            for block in blocks:
                if '### FILE END ###' not in block:
                    continue
                path_end = block.find(' ###\n')
                if path_end == -1:
                    continue
                unix_path = block[:path_end].strip()
                code = block[path_end + 5:].split('### FILE END ###')[0].strip()
                win_path = os.path.join(dest_dir, *unix_path.split('/'))
                os.makedirs(os.path.dirname(win_path), exist_ok=True)
                with open(win_path, 'w', encoding='utf-8') as out:
                    out.write(code)
                    total += 1
            self.log(f"[INFO] Восстановлено файлов: {total}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def save_structure(self):
        src_dir = self.entry_struct_src.get()
        out_file = self.entry_struct_output.get()
        if not all([src_dir, out_file]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        try:
            with open(out_file, encoding='utf-8') as f:
                f.write(f"### STRUCTURE SCAN v0.4 ###\n### Directory: {src_dir} ###\n\n")
                total = 0
                for root, dirs, files in os.walk(src_dir):
                    level = root.replace(src_dir, '').count(os.sep)
                    indent = '    ' * level
                    rel = os.path.relpath(root, src_dir)
                    f.write(f"{indent}├── {rel}/\n" if rel != '.' else f"{src_dir}\n")
                    subindent = '    ' * (level + 1)
                    for name in files:
                        f.write(f"{subindent}├── {name}\n")
                        total += 1
            self.log(f"[INFO] Структура сохранена. Элементов: {total}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")
