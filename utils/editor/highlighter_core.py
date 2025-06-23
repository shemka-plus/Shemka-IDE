import re
from utils.editor.highlighting.registry import get_rules_for_extension

def setup_syntax_tags(self):
    # Очистка предыдущих тегов (если нужно)
    self.editor.tag_delete(*self.editor.tag_names())

    # Получаем стиль подсветки по расширению
    ext = self._get_current_extension()
    _, styles = get_rules_for_extension(ext)

    # Применяем цвета тегов
    for tag, color in styles.items():
        self.editor.tag_config(tag, foreground=color)

    # Общий стиль фона и курсора
    self.editor.configure(bg="#2b2b2b", fg="#d4d4d4", insertbackground="white", selectbackground="#264F78")
    self.console.configure(bg="#000000", fg="#d4d4d4", insertbackground="white", selectbackground="#264F78")

def schedule_syntax_highlight(self, event=None):
    current_text = self.editor.get("1.0", "end-1c")
    if current_text == self._last_highlighted_text:
        return

    if self._highlight_job:
        self.after_cancel(self._highlight_job)
    self._highlight_job = self.after_idle(self.highlight_syntax)

def highlight_syntax(self):
    current_text = self.editor.get("1.0", "end-1c")
    if current_text == self._last_highlighted_text:
        return

    self._last_highlighted_text = current_text
    ext = self._get_current_extension()

    rules, _ = get_rules_for_extension(ext)

    for tag in set(t for _, t in rules):
        self.editor.tag_remove(tag, "1.0", "end")

    for pattern, tag in rules:
        for match in re.finditer(pattern, current_text, re.MULTILINE | re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add(tag, start, end)

    self.editor.edit_modified(False)

def _get_current_extension(self):
    if hasattr(self, "current_file") and self.current_file:
        return self.current_file.lower().split(".")[-1]
    return "cpp"  # По умолчанию Arduino/C++
