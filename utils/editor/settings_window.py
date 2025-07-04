import customtkinter as ctk
import serial.tools.list_ports
from tkinter import font as tkfont
from PIL import Image
from pathlib import Path

class EditorSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, mcu_var, com_var, boards, font_family="Consolas", font_size=12):
        super().__init__(parent)
        self.title("Настройки редактора")
        self.geometry("400x400")
        self.resizable(False, False)
        
        # Устанавливаем иконку
        icon_path = Path(__file__).parent.parent.parent / "data" / "Schemka-ico.ico"
        if icon_path.exists():
            self.iconbitmap(icon_path)
        
        self.transient(parent)
        self.grab_set()
        
        self.mcu_var = mcu_var
        self.com_var = com_var
        self.boards = boards
        self.font_family = font_family
        self.font_size = font_size
        
        # Создаем вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Добавляем вкладки
        self.tabview.add("Микроконтроллер")
        self.tabview.add("Порт")
        self.tabview.add("Шрифт")
        
        # Настраиваем вкладки
        self._setup_mcu_tab()
        self._setup_port_tab()
        self._setup_font_tab()
        
        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Применить", command=self._apply_settings).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy).pack(side="right", padx=5)
        
        self._center_window()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def _setup_mcu_tab(self):
        tab = self.tabview.tab("Микроконтроллер")
        ctk.CTkLabel(tab, text="Выберите микроконтроллер:").pack(pady=(10, 5))
        
        for mcu in self.boards.keys():
            ctk.CTkRadioButton(
                tab,
                text=mcu,
                variable=self.mcu_var,
                value=mcu
            ).pack(anchor="w", padx=20, pady=2)
    
    def _setup_port_tab(self):
        tab = self.tabview.tab("Порт")
        ctk.CTkLabel(tab, text="Выберите COM-порт:").pack(pady=(10, 5))
        
        try:
            self.ports = [port.device for port in serial.tools.list_ports.comports()]
            if not self.ports:
                ctk.CTkLabel(tab, text="Нет доступных COM-портов").pack()
                return
                
            for port in self.ports:
                ctk.CTkRadioButton(
                    tab,
                    text=port,
                    variable=self.com_var,
                    value=port
                ).pack(anchor="w", padx=20, pady=2)
        except Exception as e:
            ctk.CTkLabel(tab, text=f"Ошибка получения портов: {str(e)}").pack()
            self.ports = []
    
    def _setup_font_tab(self):
        tab = self.tabview.tab("Шрифт")
        
        # Выбор шрифта
        ctk.CTkLabel(tab, text="Шрифт:").pack(pady=(10, 5))
        
        self.font_family_var = ctk.StringVar(value=self.font_family)
        font_families = sorted(tkfont.families())
        ctk.CTkOptionMenu(
            tab,
            values=font_families,
            variable=self.font_family_var
        ).pack(fill="x", padx=20, pady=5)
        
        # Размер шрифта
        ctk.CTkLabel(tab, text="Размер:").pack(pady=(10, 5))
        
        self.font_size_var = ctk.StringVar(value=str(self.font_size))
        ctk.CTkOptionMenu(
            tab,
            values=["8", "10", "12", "14", "16", "18", "20", "22", "24"],
            variable=self.font_size_var
        ).pack(fill="x", padx=20, pady=5)
    
    def _apply_settings(self):
        self.font_family = self.font_family_var.get()
        self.font_size = int(self.font_size_var.get())
        self.destroy()