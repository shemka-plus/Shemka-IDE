import customtkinter as ctk
from core.version import APP_VERSION
from pathlib import Path
from tkinter import messagebox
from PIL import Image
import webbrowser

class InfoTab(ctk.CTkFrame):
    def __init__(self, parent, tools_root=None, **kwargs):
        super().__init__(parent)

        self.version = APP_VERSION
        self.tools_root = Path(tools_root) if tools_root else Path(".")
        self.data_dir = self.tools_root.parent / "data"

        self.about_path = self.data_dir / "about.txt"
        self.instructions_path = self.data_dir / "instructions.txt"
        self.history_path = self.data_dir / "history.txt"

        from customtkinter import get_appearance_mode
        print(get_appearance_mode())
        theme = get_appearance_mode()
        filename = "logo.png" if theme == "Light" else "logo_w.png"
        self.logo_path = self.data_dir / filename

        self.setup_ui()
        self.show_about()

    def setup_ui(self):
        # Кнопки переключения
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.about_btn = ctk.CTkButton(button_frame, text="О программе", command=self.show_about)
        self.about_btn.pack(side="left", padx=5)

        self.instr_btn = ctk.CTkButton(button_frame, text="Инструкция", command=self.show_instructions)
        self.instr_btn.pack(side="left", padx=5)

        self.instr_btn = ctk.CTkButton(button_frame, text="История", command=self.show_history)
        self.instr_btn.pack(side="left", padx=5)

        # Область контента
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Логотип
        try:
            self.logo_image = ctk.CTkImage(Image.open(self.logo_path), size=(300, 64))
            ctk.CTkLabel(self.scroll_frame, image=self.logo_image, text="").pack(pady=10)
        except Exception as e:
            print(f"[InfoTab] Логотип не загружен: {e}")

        # Основной текст
        self.textbox = ctk.CTkTextbox(self.scroll_frame, wrap="word", height=400)
        self.textbox.pack(fill="both", expand=True, pady=5)
        self.textbox.configure(state="disabled")

        # Ссылки
        link_frame = ctk.CTkFrame(self.scroll_frame)
        link_frame.pack(pady=10)

        ctk.CTkLabel(link_frame, text="Ссылки:", font=("", 14, "bold")).pack(anchor="w", padx=5)

        self.add_link(link_frame, "🌐 GitFlic", "https://gitflic.ru/company/shemka-plus")
        self.add_link(link_frame, "🌐 GitHub", "https://github.com/shemka-plus/Shemka-IDE")
        self.add_link(link_frame, "📘 Документация", "https://b24-bcp47f.bitrix24site.ru/")
        self.add_link(link_frame, "✉️ Поддержка", "mailto:support@shemka.com")

    def add_link(self, parent, text, url):
        def open_link():
            webbrowser.open(url)

        link = ctk.CTkButton(
            parent,
            text=text,
            fg_color="transparent",
            text_color="#3a5fcd",  # 🔵 новый цвет ссылки
            hover_color="#7799ff",  # 🔵 цвет при наведении
            font=("", 12, "underline"),
            anchor="w",
            command=open_link
        )

        link.pack(anchor="w", padx=10, pady=2)

    def show_about(self):
        self.load_text(self.about_path, prepend=f"shemka-IDE v{self.version}\n\n")

    def show_instructions(self):
        self.load_text(self.instructions_path)

    def show_history(self):
        self.load_text(self.history_path)

    def load_text(self, filepath, prepend=""):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = f"[Файл не найден: {filepath.name}]"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", prepend + content)
        self.textbox.configure(state="disabled")
