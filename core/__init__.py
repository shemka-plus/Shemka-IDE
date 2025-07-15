# core/__init__.py

# Импортируем ThemeManager из модуля theme_manager
from .theme_manager import ThemeManager

# Можно также импортировать другие важные классы/функции из core модуля
from .compiler_manager import CompilerManager
from .launcher import run_ide
from .version import APP_VERSION

# Опционально: список __all__ для явного указания экспортируемых имен
__all__ = ['ThemeManager', 'CompilerManager', 'run_ide', 'APP_VERSION']
