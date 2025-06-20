import serial
import serial.tools.list_ports
import threading
import customtkinter as ctk
from tkinter import scrolledtext, messagebox, Menu
from datetime import datetime
import time

class UARTMonitorTab(ctk.CTkFrame):
    def __init__(self, parent, avr_tools=None, boards=None, config=None, tools_root=None):
        super().__init__(parent)
        self.avr_tools = avr_tools
        self.boards = boards
        self.config = config
        self.is_running = False
        self.serial_port = None
        self.receive_thread = None
        self.show_timestamp = True
        
        # Настройка сетки
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Создание виджетов
        self.create_widgets()
        self.update_ports_list()
        self.setup_context_menu()
        
        # Уведомление о режиме (внизу)
        self.programmer_notice = ctk.CTkLabel(
            self, 
            text="Для работы переключите программатор в режим UART",
            text_color="#FFA500",
            font=("", 12, "bold")
        )
        self.programmer_notice.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,5))
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм настроек подключения
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # COM-порт
        ctk.CTkLabel(settings_frame, text="COM-порт:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.port_menu = ctk.CTkOptionMenu(settings_frame)
        self.port_menu.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Кнопка обновления портов
        self.refresh_ports_btn = ctk.CTkButton(
            settings_frame, 
            text="Обновить", 
            command=self.update_ports_list,
            width=100
        )
        self.refresh_ports_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # Скорость передачи
        ctk.CTkLabel(settings_frame, text="Скорость (бод):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.baudrate_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["300", "600", "1200", "2400", "4800", "9600", "14400", 
                   "19200", "28800", "38400", "57600", "115200"]
        )
        self.baudrate_menu.set("9600")
        self.baudrate_menu.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Кнопка подключения
        self.connect_btn = ctk.CTkButton(
            settings_frame, 
            text="Подключиться", 
            command=self.toggle_connection,
            width=100
        )
        self.connect_btn.grid(row=1, column=2, padx=5, pady=2)
        
        # Фрейм дополнительных кнопок
        self.tools_frame = ctk.CTkFrame(settings_frame)
        self.tools_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=2, sticky="e")
        
        # Кнопка включения/выключения времени
        self.timestamp_btn = ctk.CTkButton(
            self.tools_frame,
            text="Время: ВКЛ",
            command=self.toggle_timestamp,
            width=100
        )
        self.timestamp_btn.pack(side="left", padx=2)
        
        # Кнопка очистки вывода
        self.clear_btn = ctk.CTkButton(
            self.tools_frame,
            text="Очистить",
            command=self.clear_output,
            width=100
        )
        self.clear_btn.pack(side="left", padx=2)
        
        # Текстовое поле вывода
        self.output_text = scrolledtext.ScrolledText(
            self,
            wrap="word",
            state='disabled',
            font=("Consolas", 10),
            bg='#2b2b2b',
            fg='white',
            insertbackground='white',
            selectbackground='#3b3b3b'
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Настройка тегов для цветного текста
        self.output_text.tag_config("incoming", foreground="#44FF44")  # Зеленый
        self.output_text.tag_config("outgoing", foreground="#FF4444")  # Красный
        self.output_text.tag_config("system", foreground="#66D9EF")    # Голубой
        self.output_text.tag_config("error", foreground="#FF4444")     # Красный
        self.output_text.tag_config("arrow", font=("Arial", 12, "bold"))
        self.output_text.tag_config("timestamp", foreground="#75715E") # Серый
        
        # Фрейм отправки данных
        send_frame = ctk.CTkFrame(self)
        send_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        self.input_entry = ctk.CTkEntry(send_frame)
        self.input_entry.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        self.input_entry.bind("<Return>", lambda e: self.send_data())
        
        self.send_btn = ctk.CTkButton(
            send_frame, 
            text="Отправить", 
            command=self.send_data
        )
        self.send_btn.pack(side="left", padx=5, pady=2)
    
    def setup_context_menu(self):
        """Настройка контекстного меню для поля вывода"""
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_output)
        self.context_menu.add_command(label="Очистить", command=self.clear_output)
        
        # Привязываем меню к правой кнопке мыши
        self.output_text.bind("<Button-3>", self.show_context_menu)
        
        # Горячие клавиши
        self.output_text.bind("<Control-c>", lambda e: self.copy_output())
        self.output_text.bind("<Control-l>", lambda e: self.clear_output())
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_output(self):
        """Копирование выделенного текста в буфер обмена"""
        try:
            text = self.output_text.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(text)
        except:
            pass  # Если ничего не выделено
    
    def clear_output(self):
        """Очистка поля вывода"""
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", "end")
        self.output_text.config(state='disabled')
    
    def toggle_timestamp(self):
        """Переключение отображения времени"""
        self.show_timestamp = not self.show_timestamp
        self.timestamp_btn.configure(text=f"Время: {'ВКЛ' if self.show_timestamp else 'ВЫКЛ'}")
    
    def update_ports_list(self):
        """Обновление списка COM-портов"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu.configure(values=ports)
        if ports:
            self.port_menu.set(ports[0])
    
    def toggle_connection(self):
        """Подключение/отключение от порта"""
        if self.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Начало мониторинга порта"""
        port = self.port_menu.get()
        baudrate = self.baudrate_menu.get()
        
        if not port:
            messagebox.showerror("Ошибка", "Выберите COM-порт!")
            return
        
        try:
            self.serial_port = serial.Serial(port, int(baudrate), timeout=1)
            self.is_running = True
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.receive_thread.start()
            
            self.connect_btn.configure(text="Отключиться")
            self.log_message(f"Подключено к {port} @ {baudrate} бод\n", "system")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться:\n{e}")
    
    def stop_monitoring(self):
        """Остановка мониторинга порта"""
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            if self.receive_thread and self.receive_thread.is_alive():
                self.receive_thread.join()
            self.serial_port.close()
            
            self.connect_btn.configure(text="Подключиться")
            self.log_message("Отключено\n", "system")
    
    def receive_data(self):
        """Получение данных с порта"""
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8', errors='replace').strip()
                    if data:
                        timestamp = datetime.now().strftime("[%H:%M:%S] ") if self.show_timestamp else ""
                        self.log_message(timestamp, "timestamp")
                        self.log_message("← ", "arrow")
                        self.log_message(f"{data}\n", "incoming")
                else:
                    time.sleep(0.01)  # Добавляем небольшую задержку при отсутствии данных
            except Exception as e:
                self.log_message(f"Ошибка чтения: {e}\n", "error")
                break
    
    def send_data(self):
        """Отправка данных в порт"""
        if not self.is_running:
            messagebox.showwarning("Ошибка", "Порт не подключен!")
            return
        
        data = self.input_entry.get()
        if not data:
            return
        
        try:
            self.serial_port.write((data + '\n').encode('utf-8'))
            timestamp = datetime.now().strftime("[%H:%M:%S] ") if self.show_timestamp else ""
            self.log_message(timestamp, "timestamp")
            self.log_message("→ ", "arrow")
            self.log_message(f"{data}\n", "outgoing")
            self.input_entry.delete(0, "end")
        except Exception as e:
            self.log_message(f"Ошибка отправки: {e}\n", "error")
    
    def log_message(self, message, msg_type="system"):
        """Логирование сообщений"""
        self.output_text.config(state='normal')
        self.output_text.insert("end", message, msg_type)
        self.output_text.see("end")
        self.output_text.config(state='disabled')