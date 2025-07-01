# utils/editor/highlighting/cpp_rules.py
cpp_keywords = [
    'auto', 'break', 'case', 'const', 'continue', 'default', 'do', 'else',
    'enum', 'extern', 'for', 'goto', 'if', 'register', 'return', 'sizeof',
    'static', 'struct', 'switch', 'typedef', 'union', 'volatile', 'while'
]

cpp_types = [
    'bool', 'char', 'double', 'float', 'int', 'long', 'short', 'void',
    'unsigned', 'signed', 'size_t', 'uint8_t', 'uint16_t', 'uint32_t'
]

rules = [
    (rf'\b({"|".join(cpp_keywords)})\b', 'keyword'),
    (rf'\b({"|".join(cpp_types)})\b', 'type'),
    (r'//.*?$|/\*.*?\*/', 'comment'),
    (r'"(?:\\.|[^"\\])*"', 'string'),
    (r'#\s*\w+', 'define'),
    (r'\b\d+\b', 'number'),
]

styles = {}