# core/compiler_manager.py
from pathlib import Path
import zipfile
import shutil
import os

class CompilerManager:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.bin_path = self.root / "bin"
        self.zips_dir = self.root / "compilers"
        self.required_exe = self.bin_path / "bin" / "avr-gcc.exe"

    def is_installed(self):
        return self.required_exe.exists()

    def available_archives(self):
        return list(self.zips_dir.glob("*.zip"))

    def install_from_archive(self, archive_path):
        if self.bin_path.exists():
            shutil.rmtree(self.bin_path)
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(self.bin_path)

    def uninstall(self):
        if self.bin_path.exists():
            shutil.rmtree(self.bin_path)
