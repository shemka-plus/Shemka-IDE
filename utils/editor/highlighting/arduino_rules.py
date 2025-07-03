arduino_keywords = [
    "pinMode", "digitalWrite", "digitalRead", "analogWrite", "analogRead",
    "delay", "millis", "micros", "delayMicroseconds", "Serial", "setup", 
    "loop", "HIGH", "LOW", "INPUT", "OUTPUT", "INPUT_PULLUP"
]

arduino_types = ["boolean", "byte", "word", "String", "array", "void"]

cpp_keywords = [
    "if", "else", "while", "for", "switch", "case", "break", "continue",
    "return", "class", "public", "private", "protected", "static", "const",
    "volatile", "sizeof", "new", "delete", "true", "false", "nullptr"
]

rules = [
    (r'\b(int|float|double|char|short|long|unsigned|signed)\b', "type"),
    (rf'\b({"|".join(arduino_keywords)})\b', "arduino"),
    (rf'\b({"|".join(cpp_keywords)})\b', "keyword"),
    (rf'\b({"|".join(arduino_types)})\b', "type"),
    (r'#define\s+\w+', "define"),
    (r'#include\s+[<"].+?[>"]', "define"),
    (r'//.*?$|/\*.*?\*/', "comment"),
    (r'"(?:\\.|[^"\\])*"', "string"),
    (r'\b\d+\b', "number"),
    (r'\b([A-Z_][A-Z0-9_]+)\b', "constant"),
]

def get_styles():
    from customtkinter import get_appearance_mode
    if get_appearance_mode() == "Light":
        return {
            "keyword": "#0000BB",
            "define": "#8B008B",
            "comment": "#008000",
            "string": "#A31515",
            "arduino": "#1A1AA6",
            "type": "#008B8B",
            "number": "#1C00CF",
            "constant": "#AF0000",
        }
    else:
        return {
            "keyword": "#569CD6",
            "define": "#C586C0",
            "comment": "#6A9955",
            "string": "#CE9178",
            "arduino": "#DFDF72",
            "type": "#4EC9B0",
            "number": "#B5CEA8",
            "constant": "#D16969",
        }
