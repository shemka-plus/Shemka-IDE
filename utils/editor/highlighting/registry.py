from .arduino_rules import rules as arduino_rules, styles as arduino_styles
from .python_rules import rules as python_rules, styles as python_styles

EXTENSION_RULES = {
    "ino": (arduino_rules, arduino_styles),
    "cpp": (arduino_rules, arduino_styles),
    "c":   (arduino_rules, arduino_styles),
    "h":   (arduino_rules, arduino_styles),
    "py":  (python_rules, python_styles),
}

def get_rules_for_extension(ext):
    """Вернёт (rules, styles) по расширению файла"""
    ext = ext.lower()
    return EXTENSION_RULES.get(ext, (arduino_rules, arduino_styles))  # по умолчанию Arduino
