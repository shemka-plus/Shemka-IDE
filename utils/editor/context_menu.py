# utils/editor/context_menu.py
import tkinter as tk
from tkinter import Menu

def bind_context_menu(widget, actions: dict):
    """Привязывает контекстное меню с действиями к виджету"""
    menu = Menu(widget, tearoff=0)
    for name, command in actions.items():
        if name == "---":
            menu.add_separator()
        else:
            menu.add_command(label=name, command=command)
    
    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)
    
    widget.bind("<Button-3>", show_menu)
