# utils/editor/console.py

def log(self, message):
    self.console.configure(state="normal")
    self.console.insert("end", message + "\n")
    self.console.see("end")
    self.console.configure(state="disabled")
