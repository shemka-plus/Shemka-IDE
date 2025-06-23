# utils/editor/highlighting/arduino_rules.py
arduino_keywords = [
    "pinMode", "digitalWrite", "digitalRead", "analogWrite", "analogRead",
    "delay", "millis", "Serial", "setup", "loop", "HIGH", "LOW", "INPUT", "OUTPUT"
]

arduino_types = ["boolean", "byte", "word", "String"]

rules = [
    (rf'\b({"|".join(arduino_keywords)})\b', "arduino"),
    (rf'\b({"|".join(arduino_types)})\b', "type"),
    (r'\b(int|char|float|void|return|if|else|while|for|break|continue|include|define|struct|sizeof)\b', "keyword"),
    (r'#define\s+\w+', "define"),
    (r'//.*?$|/\*.*?\*/', "comment"),
    (r'"(?:\\.|[^"\\])*"', "string"),
]

styles = {
    "keyword": "#569CD6",
    "define": "#C586C0",
    "comment": "#6A9955",
    "string": "#CE9178",
    "arduino": "#DFDF72",
    "type": "#4EC9B0",
}
