from core.theme_manager import ThemeManager

def get_console_theme():
    theme_key = "dark" if ThemeManager().config.config.get("theme") == "dark" else "default"
    editor_themes = ThemeManager().editor_themes
    return {
        "bg": editor_themes[theme_key]["console_bg"],
        "fg": editor_themes[theme_key]["console_fg"],
        "cursor": editor_themes[theme_key]["cursor"],
        "selection": editor_themes[theme_key]["selection"]
    }
