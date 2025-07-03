import customtkinter as ctk
from .config_manager import ConfigManager
from tkinter import messagebox
from core.compiler_manager import CompilerManager

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Interface settings
        ctk.CTkLabel(frame, text="Настройки интерфейса", font=("", 16)).grid(row=0, column=0, pady=10, sticky="w", columnspan=2)

        ctk.CTkLabel(frame, text="Тема интерфейса:").grid(row=1, column=0, sticky="w")
        self.theme_var = ctk.StringVar(value=self.config.config["theme"])
        theme_menu = ctk.CTkOptionMenu(
            frame,
            values=["dark", "light", "system"],
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_menu.grid(row=1, column=1, pady=5, sticky="w")

        # Color theme selection
        ctk.CTkLabel(frame, text="Цветовая схема:").grid(row=2, column=0, sticky="w")
        self.color_var = ctk.StringVar(value=self.config.config["color_theme"])
        color_menu = ctk.CTkOptionMenu(
            frame,
            values=["blue", "green", "dark-blue"],
            variable=self.color_var,
            command=self.change_color
        )
        color_menu.grid(row=2, column=1, pady=5, sticky="w")

        # Save button
        save_btn = ctk.CTkButton(
            frame,
            text="Применить настройки",
            command=self.apply_settings
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Compiler management
        ctk.CTkLabel(frame, text="Управление компиляторами", font=("", 16)).grid(row=4, column=0, pady=(30, 10), sticky="w", columnspan=2)

        ctk.CTkButton(frame, text="Установить компилятор", command=self.install_compiler).grid(row=5, column=0, pady=5)
        ctk.CTkButton(frame, text="Удалить компилятор", command=self.uninstall_compiler).grid(row=5, column=1, pady=5)

        # Список архивов компиляторов
        mgr = CompilerManager()
        archives = [a.name for a in mgr.available_archives()]
        ctk.CTkLabel(frame, text="Доступные архивы:").grid(row=6, column=0, sticky="w")
        ctk.CTkOptionMenu(frame, values=archives or ["Нет архивов"]).grid(row=6, column=1, pady=5)

    def change_theme(self, choice):
        """Объединенная функция смены темы"""
        self.config.set_theme(choice)
        self.config.set_color_theme("blue")  # Фиксированная цветовая схема
        
        # Мгновенное применение темы
        ctk.set_appearance_mode(choice)
        from core.theme_manager import ThemeManager
        ThemeManager().apply_theme(self.master)

    def change_color(self, choice):
        try:
            ctk.set_default_color_theme(choice)
            self.config.set_color_theme(choice)
            # Обновим тему принудительно
            self.after(100, lambda: ctk.set_appearance_mode(ctk.get_appearance_mode()))
        except Exception as e:
            print(f"Ошибка смены темы: {e}")

    def apply_settings(self):
        messagebox.showinfo("Сохранено", "Настройки применены и сохранены")

    def install_compiler(self):
        mgr = CompilerManager()
        archives = mgr.available_archives()
        if not archives:
            messagebox.showwarning("Нет архивов", "В папке 'compilers' нет zip-файлов.")
            return

        archive_names = [a.name for a in archives]
        selected = archive_names[0]
        if messagebox.askyesno("Установка", f"Установить компилятор из {selected}?"):
            mgr.install_from_archive(mgr.zips_dir / selected)
            messagebox.showinfo("Готово", f"Компилятор из {selected} установлен.")

    def uninstall_compiler(self):
        mgr = CompilerManager()
        if messagebox.askyesno("Удаление", "Удалить текущий компилятор?"):
            mgr.uninstall()
            messagebox.showinfo("Удалено", "Компилятор удален. Перезапустите программу.")

    def change_editor_theme(self, choice):
        self.config.config["editor_theme"] = choice
        self.config.save_config()
        from core.theme_manager import ThemeManager
        ThemeManager().apply_theme(self.master)