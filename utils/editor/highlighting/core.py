# utils/editor/highlighting/core.py
import re
from . import registry


def apply_highlighting(self):
    lang = registry.detect_language(self.current_file)
    if not lang:
        return

    rules, styles = registry.get_rules_and_styles(lang)

    self.editor.tag_delete("keyword", "define", "comment", "string", "arduino", "type")

    for tag, color in styles.items():
        self.editor.tag_config(tag, foreground=color)

    text = self.editor.get("1.0", "end-1c")

    for pattern, tag in rules:
        for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add(tag, start, end)

    self.editor.edit_modified(False)