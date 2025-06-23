# utils/editor/ports.py
import serial.tools.list_ports


def update_ports(self):
    try:
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu.configure(values=ports)
        if ports:
            self.com_var.set(ports[0])
    except Exception as e:
        self.log(f"Ошибка портов: {e}")
