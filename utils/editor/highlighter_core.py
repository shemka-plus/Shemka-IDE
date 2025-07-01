import re
from pathlib import Path
from utils.editor.highlighting.registry import get_rules_for_extension

def get_file_extension(widget):
    if hasattr(widget, "current_file") and widget.current_file:
        return Path(widget.current_file).suffix.lower()
    return ".ino"  # значение по умолчанию

def setup_syntax_tags(widget):
    ext = get_file_extension(widget)
    try:
        rules, styles = get_rules_for_extension(ext)
    except:
        from utils.editor.highlighting.arduino_rules import rules, styles

    widget.tag_delete(*widget.tag_names())

    for tag, color in styles.items():
        widget.tag_config(tag, foreground=color)

def schedule_syntax_highlight(widget, event=None):
    current_text = widget.get("1.0", "end-1c")
    if hasattr(widget, "_last_highlighted_text") and current_text == widget._last_highlighted_text:
        return

    if hasattr(widget, "_highlight_job") and widget._highlight_job:
        widget.after_cancel(widget._highlight_job)
    widget._highlight_job = widget.after_idle(lambda: highlight_syntax(widget))

def highlight_syntax(widget):
    text = widget.get("1.0", "end-1c")
    print(f"[DEBUG] highlight_syntax(): {len(text)} символов")

    ext = get_file_extension(widget)
    print(f"[DEBUG] Расширение файла: {ext}")

    try:
        rules, styles = get_rules_for_extension(ext)
    except:
        from utils.editor.highlighting.arduino_rules import rules, get_styles
        styles = get_styles()

    for tag, color in styles.items():
        #print(f"[DEBUG] tag_config: {tag} → {color}")
        widget.tag_config(tag, foreground=color)

    for tag in set(t for _, t in rules):
        widget.tag_remove(tag, "1.0", "end")

    for pattern, tag in rules:
        for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            #print(f"[DEBUG] match: {match.group()} → tag: {tag} at {start}-{end}")
            widget.tag_add(tag, start, end)

    widget.edit_modified(False)

