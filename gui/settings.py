import customtkinter as ctk
from .config_manager import ConfigManager
from tkinter import messagebox

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
        
        # Theme selection
        ctk.CTkLabel(frame, text="Тема:").grid(row=1, column=0, sticky="w")
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
    
    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)
        self.config.set_theme(choice)
    
    def change_color(self, choice):
        try:
            ctk.set_default_color_theme(choice)
            self.config.set_color_theme(choice)
            # Принудительно обновляем тему
            ctk.set_appearance_mode(ctk.get_appearance_mode())
        except Exception as e:
            print(f"Ошибка смены темы: {e}")
    
    def apply_settings(self):
        messagebox.showinfo("Сохранено", "Настройки применены и сохранены")