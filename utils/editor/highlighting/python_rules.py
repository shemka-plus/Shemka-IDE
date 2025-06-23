rules = [
    (r'\b(def|class|import|from|return|if|elif|else|while|for|in|try|except|with|as|pass|break|continue|lambda|yield|True|False|None)\b', "keyword"),
    (r'#.*', "comment"),
    (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', "string"),
]

styles = {
    "keyword": "#569CD6",
    "comment": "#6A9955",
    "string": "#CE9178",
}
