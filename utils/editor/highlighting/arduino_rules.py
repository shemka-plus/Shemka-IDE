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

# Цвета теперь определяются в темах, поэтому здесь их можно удалить
styles = {
    "keyword": "#569CD6",
    "define": "#C586C0",
    "comment": "#6A9955",
    "string": "#CE9178",
    "arduino": "#DFDF72",
    "type": "#4EC9B0",
    "number": "#B5CEA8",
    "constant": "#D16969",
}


## utils/editor/highlighting/arduino_rules.py
#arduino_keywords = [
#    "pinMode", "digitalWrite", "digitalRead", "analogWrite", "analogRead",
#    "delay", "millis", "Serial", "setup", "loop", "HIGH", "LOW", "INPUT", "OUTPUT"
#]
#
#arduino_types = ["boolean", "byte", "word", "String"]
#
#rules = [
#    (rf'\b({"|".join(arduino_keywords)})\b', "arduino"),
#    (rf'\b({"|".join(arduino_types)})\b', "type"),
#    (r'\b(int|char|float|void|return|if|else|while|for|break|continue|include|define|struct|sizeof)\b', "keyword"),
#    (r'#define\s+\w+', "define"),
#    (r'//.*?$|/\*.*?\*/', "comment"),
#    (r'"(?:\\.|[^"\\])*"', "string"),
#]
#
#styles = {
#    "keyword": "#569CD6",
#    "define": "#C586C0",
#    "comment": "#6A9955",
#    "string": "#CE9178",
#    "arduino": "#DFDF72",
#    "type": "#4EC9B0",
#}
