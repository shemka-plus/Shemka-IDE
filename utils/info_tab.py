import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from pathlib import Path
import webbrowser
import re


class InfoTab(ctk.CTkFrame):
    def __init__(self, master, data_dir: Path = Path("data"), version: str = "", config=None, **kwargs):
        kwargs.pop("avr_tools", None)
        kwargs.pop("boards", None)
        kwargs.pop("config", None)

        super().__init__(master, **kwargs)
        self.data_dir = data_dir
        self.version = version
        self.config = config

        self.about_path = self.data_dir / "about.txt"
        self.history_path = self.data_dir / "history.txt"
        self.instr_path = self.data_dir / "instructions.txt"
        self.products_path = self.data_dir / "products.txt"

        self.logo_image = None

        self.setup_ui()
        self.show_about()

    def setup_ui(self):
        # 🔹 Кнопки выбора разделов
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=(10, 0))

        self.about_btn = ctk.CTkButton(button_frame, text="О программе", command=self.show_about)
        self.about_btn.pack(side="left", padx=5)

        self.instr_btn = ctk.CTkButton(button_frame, text="Инструкция", command=self.show_instructions)
        self.instr_btn.pack(side="left", padx=5)

        self.history_btn = ctk.CTkButton(button_frame, text="История", command=self.show_history)
        self.history_btn.pack(side="left", padx=5)

        self.products_btn = ctk.CTkButton(button_frame, text="Наша продукция", command=self.show_products)
        self.products_btn.pack(side="left", padx=5)

        # 🔹 Логотип (непрокручиваемый)
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=(10, 0))

        self.logo_label = ctk.CTkLabel(self.logo_frame, text="")
        self.logo_label.pack()
        self.update_logo()

        # 🔹 Прокручиваемая текстовая область
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # 🔹 Ссылки
        links_frame = ctk.CTkFrame(self)
        links_frame.pack(pady=10)

        ctk.CTkLabel(links_frame, text="Ссылки:", font=("", 14, "bold")).pack(anchor="w", padx=5)

        link_row = ctk.CTkFrame(links_frame)
        link_row.pack(pady=5)

        self.add_link(link_row, "🌐 GitFlic", "https://gitflic.ru/company/shemka-plus", side="left")
        self.add_link(link_row, "🌐 GitHub", "https://github.com/shemka-plus/Shemka-IDE", side="left")
        self.add_link(link_row, "📘 Документация", "https://b24-bcp47f.bitrix24site.ru/", side="left")
        self.add_link(link_row, "✉️ Поддержка", "mailto:support@shemka.com", side="left")

    def add_link(self, parent, text, url, side="top"):
        def open_link():
            webbrowser.open(url)

        link = ctk.CTkButton(
            parent,
            text=text,
            fg_color="transparent",
            text_color="#3a5fcd",
            hover_color="#7799ff",
            font=("", 12, "underline"),
            anchor="w",
            command=open_link
        )
        link.pack(side=side, padx=10, pady=2)

    def update_logo(self):
        theme = ctk.get_appearance_mode()  # "Light" или "Dark"
        logo_file = "logo.png" if theme == "Light" else "logo_w.png"
        logo_path = self.data_dir / logo_file

        try:
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(300, 64))
            self.logo_label.configure(image=self.logo_image, text="")
        except Exception as e:
            print(f"[InfoTab] Ошибка загрузки логотипа {logo_file}: {e}")
            self.logo_label.configure(text="Shemka+", image=None)

    def show_about(self):
        self.load_text(self.about_path, prepend=f"shemka-IDE v{self.version}\n\n", allow_images=False)

    def show_instructions(self):
        self.load_text(self.instr_path, allow_images=False)

    def show_history(self):
        self.load_text(self.history_path, allow_images=False)

    def show_products(self):
        self.load_text(self.products_path, allow_images=True)

    def load_text(self, filepath, prepend="", allow_images=False):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = f"[Файл не найден: {filepath.name}]"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Отображение текста и изображений
        for line in (prepend + content).splitlines():
            line = line.strip()
            if allow_images and line.startswith("!["):
                # Новый формат с размерами: ![alt](path <WxH>)
                match = re.match(r"!\[.*?\]\((.*?)(?:\s*<(\d+)x(\d+)>)?\)", line)
                if match:
                    image_path = self.data_dir.parent / match.group(1)
                    width = int(match.group(2)) if match.group(2) else 150  # default width
                    height = int(match.group(3)) if match.group(3) else 450  # default height
                    
                    try:
                        img = ctk.CTkImage(
                            Image.open(image_path), 
                            size=(width, height))
                        ctk.CTkLabel(
                            self.scroll_frame, 
                            image=img, 
                            text=""
                        ).pack(pady=10)
                    except Exception as e:
                        ctk.CTkLabel(
                            self.scroll_frame, 
                            text=f"[Ошибка загрузки изображения: {image_path}]"
                        ).pack()
                    continue

            ctk.CTkLabel(
                self.scroll_frame, 
                text=line, 
                anchor="w", 
                justify="left", 
                wraplength=1000
            ).pack(fill="x", padx=10, pady=1)
