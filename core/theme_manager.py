# core/theme_manager.py
import customtkinter as ctk
import json
from pathlib import Path
from gui.config_manager import ConfigManager

class ThemeManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config = ConfigManager()
        self.load_editor_themes()
    
    def load_editor_themes(self):
        themes_dir = Path(__file__).parent.parent / "data" / "editor_themes"
        self.editor_themes = {
            "default": {
                "editor_bg": "#FFFFFF",
                "editor_fg": "#333333",
                "cursor": "#000000",
                "selection": "#B3D7FF",
                "gutter_bg": "#F5F5F5",
                "gutter_fg": "#999999",
                "console_bg": "#F0F0F0", 
                "console_fg": "#333333"
            },
            "dark": {
                "editor_bg": "#1E1E1E",
                "editor_fg": "#E0E0E0", 
                "cursor": "#FFFFFF",
                "selection": "#264F78",
                "gutter_bg": "#252526",
                "gutter_fg": "#858585",
                "console_bg": "#2D2D2D",
                "console_fg": "#CCCCCC"
            }
        }
        
        # Дополнительно загружаем темы из файлов, если они есть
        themes_dir.mkdir(exist_ok=True, parents=True)
        for theme_file in themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    self.editor_themes[theme_file.stem] = json.load(f)
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def apply_theme(self, widget):
        """Применяет текущую тему к интерфейсу"""
        try:
            # Применяем основную тему
            ctk.set_appearance_mode(self.config.config["theme"])
            ctk.set_default_color_theme(self.config.config["color_theme"])
            
            # Применяем тему редактора
            self.apply_editor_theme(widget)
            
            if hasattr(widget, 'update_theme'):
                widget.update_theme()
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def apply_editor_theme(self, widget, theme_name=None):
        """Применяет тему к редактору кода"""
        if not hasattr(widget, 'editor'):
            return
            
        try:
            if theme_name is None:
                theme_name = "dark" if self.config.config["theme"] == "dark" else "default"
            
            theme = self.editor_themes.get(theme_name, self.editor_themes["default"])
            
            # Настройка редактора
            widget.editor.configure(
                bg=theme["editor_bg"],
                fg=theme["editor_fg"],
                insertbackground=theme["cursor"],
                selectbackground=theme["selection"]
            )
            
            # Настройка номеров строк
            if hasattr(widget, 'line_numbers'):
                widget.line_numbers.configure(
                    bg=theme["gutter_bg"],
                    fg=theme["gutter_fg"]
                )
            
            # Настройка консоли
            if hasattr(widget, 'console'):
                widget.console.configure(
                    bg=theme["console_bg"],
                    fg=theme["console_fg"],
                    insertbackground=theme["cursor"],
                    selectbackground=theme["selection"]
                )
        except Exception as e:
            print(f"Error applying editor theme: {e}")