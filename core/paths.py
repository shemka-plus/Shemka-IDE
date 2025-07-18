# core/paths.py
from pathlib import Path
import sys
import os

def get_base_path():
    """Возвращает базовый путь в зависимости от режима (exe или разработка)"""
    if getattr(sys, 'frozen', False):  # Если собрано в exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Для разработки

BASE_PATH = Path(get_base_path())