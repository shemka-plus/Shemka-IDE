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
    ext = ext.lower()

    if ext in (".ino", ".pde"):
        from utils.editor.highlighting import arduino_rules
        return arduino_rules.rules, arduino_rules.styles

    elif ext in (".c", ".cpp", ".h", ".hpp"):
        from utils.editor.highlighting import c_cpp_rules
        return c_cpp_rules.rules, c_cpp_rules.styles

    # fallback — пустые правила и стили
    return [], {}

#def get_rules_for_extension(ext):
#    """Возвращает правила подсветки для расширения файла"""
#    ext = ext.lower()
#
#    print(f"[DEBUG] Загружаем правила для расширения: {ext}")
#    
#    # Для Arduino файлов
#    if ext in ('ino', 'pde'):
#        from utils.editor.highlighting import arduino_rules
#        return arduino_rules.rules, arduino_rules.styles
#        #from .arduino_rules import rules as arduino_rules
#        #return arduino_rules, {}
#    
#    # Для C/C++ файлов
#    elif ext in ('c', 'cpp', 'h', 'hpp'):
#        from utils.editor.highlighting import c_cpp_rules
#        return c_cpp_rules.rules, c_cpp_rules.styles
#        #from .cpp_rules import rules as cpp_rules
#        #return cpp_rules, {}
#    
#    # Для Python файлов
#    elif ext == 'py':
#        from .python_rules import rules as python_rules
#        return python_rules, {}
#    
#    # По умолчанию используем Arduino правила
#    from .arduino_rules import rules as default_rules
#    return default_rules, {}