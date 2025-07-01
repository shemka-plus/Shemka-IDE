import json
from pathlib import Path

class ConfigManager:
    """Класс для управления настройками приложения"""
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "shemka_config.json"
        self.default_config = {
            "theme": "dark",
            "color_theme": "blue",
            "editor_theme": "default",
            "recent_files": [],
            "com_port": "",
            "baudrate": "9600",
            "mcu": "ATmega328P"
        }
        self.available_themes = ["dark", "light", "system"]
        self.available_color_themes = ["blue", "green", "dark-blue", "red", "purple"]
        self.available_editor_themes = ["default", "monokai", "solarized", "dracula"]
        self.config = self._load_config()
    
    def _load_config(self):
        """Загружает конфигурацию из файла"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
        return self.default_config.copy()
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")

    @property
    def recent_files(self):
        """Возвращает список последних файлов"""
        return self.config.get("recent_files", [])
    
    def add_recent_file(self, file_path):
        """Добавляет файл в историю"""
        if file_path in self.config["recent_files"]:
            self.config["recent_files"].remove(file_path)
        self.config["recent_files"].insert(0, file_path)
        self.config["recent_files"] = self.config["recent_files"][:10]  # Ограничиваем 10 файлами
        self.save_config()
    
    def set_theme(self, theme):
        """Устанавливает тему интерфейса"""
        self.config["theme"] = theme
        self.save_config()
    
    def set_color_theme(self, color_theme):
        """Устанавливает цветовую схему"""
        self.config["color_theme"] = color_theme
        self.save_config()
    
    def set_com_settings(self, com_port, baudrate, mcu):
        """Сохраняет настройки подключения"""
        self.config["com_port"] = com_port
        self.config["baudrate"] = baudrate
        self.config["mcu"] = mcu
        self.save_config()