# core/__init__.py

# Импортируем ThemeManager из модуля theme_manager
from .theme_manager import ThemeManager

# Можно также импортировать другие важные классы/функции из core модуля
from .compiler_manager import CompilerManager
from .launcher import run_ide
from .version import APP_VERSION

# Опционально: список __all__ для явного указания экспортируемых имен
__all__ = ['ThemeManager', 'CompilerManager', 'run_ide', 'APP_VERSION']


#import customtkinter as ctk
#from gui.config_manager import ConfigManager  # Изменено с относительного импорта
#import json
#import os
#from pathlib import Path
#
#class ThemeManager:
#    _instance = None
#    
#    def __new__(cls):
#        if cls._instance is None:
#            cls._instance = super().__new__(cls)
#            cls._instance._initialized = False
#        return cls._instance
#    
#    def __init__(self):
#        if self._initialized:
#            return
#        self._initialized = True
#        self.config = ConfigManager()
#        self.load_editor_themes()
#    
#    def load_editor_themes(self):
#        themes_dir = Path(__file__).parent.parent / "data" / "editor_themes"
#        self.editor_themes = {}
#        
#        for theme_file in themes_dir.glob("*.json"):
#            try:
#                with open(theme_file, 'r', encoding='utf-8') as f:
#                    self.editor_themes[theme_file.stem] = json.load(f)
#            except Exception as e:
#                print(f"Error loading theme {theme_file}: {e}")
#    
#    def apply_theme(self, widget):
#        ctk.set_appearance_mode(self.config.config["theme"])
#        ctk.set_default_color_theme(self.config.config["color_theme"])
#        
#        if hasattr(widget, 'update_theme'):
#            widget.update_theme()