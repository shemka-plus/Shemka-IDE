from core.launcher import run_ide
from pathlib import Path
import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = Path(get_base_path())

if __name__ == "__main__":
    run_ide()
