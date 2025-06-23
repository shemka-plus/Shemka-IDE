import subprocess
from pathlib import Path
import os

class AVRCompiler:
    def __init__(self, avr_tools, tools_root=None):
        self.avr_tools = avr_tools
        self.tools_root = Path(tools_root) if tools_root else Path(__file__).parent.parent.parent / "bin"
        self.tools_root = self.tools_root.resolve()

        self.bin_dir = self.tools_root / "bin"
        self.device_specs = self.tools_root / "device-specs"
        self.include_dir = self.tools_root / "include"
        self.cores_dir = self.tools_root / "cores" / "arduino"
        self.lib_dir = self.tools_root / "lib"
        self.libexec_dir = self.tools_root / "libexec"

    def compile(self, source_code, mcu, output_dir="build", callback=None):
        try:
            output_dir = Path(output_dir).resolve()
            output_dir.mkdir(exist_ok=True, parents=True)

            # Создание файла .cpp (для Arduino API)
            src_file = output_dir / "sketch.cpp"
            with open(src_file, "w", encoding="utf-8") as f:
                if '#include <Arduino.h>' not in source_code:
                    f.write('#include <Arduino.h>\n\n')
                f.write(source_code)

            # Проверка важных компонентов
            specs_file = self.device_specs / f"specs-{mcu}"
            if not specs_file.exists():
                raise FileNotFoundError(f"Файл спецификаций не найден: {specs_file}")

            if not Path(self.avr_tools['gcc']).exists():
                raise FileNotFoundError(f"Компилятор avr-gcc не найден: {self.avr_tools['gcc']}")

            if not Path(self.avr_tools['objcopy']).exists():
                raise FileNotFoundError(f"Утилита objcopy не найдена: {self.avr_tools['objcopy']}")

            elf_path = output_dir / "sketch.elf"
            hex_path = output_dir / "sketch.hex"

            # Команда компиляции
            cmd_compile = [
                str(self.avr_tools['gcc']),
                "-Wall", "-Os",
                "-std=gnu++11",
                "-DF_CPU=16000000UL",
                f"-mmcu={mcu}",
                "-B", str(self.device_specs),
                "-I", str(self.include_dir),
                "-I", str(self.cores_dir),
                "-o", str(elf_path),
                str(src_file)
            ]

            # Подготовка окружения
            env = os.environ.copy()
            env["PATH"] = os.pathsep.join([
                str(self.bin_dir),
                str(self.libexec_dir / "gcc" / "avr" / "7.3.0"),
                str(self.lib_dir),
                env.get("PATH", "")
            ])

            print(f"[Компиляция] {' '.join(cmd_compile)}")
            result = subprocess.run(cmd_compile, capture_output=True, text=True, env=env)

            if result.returncode != 0:
                msg = f"Ошибка компиляции:\n{result.stderr}"
                if callback:
                    callback(False, msg)
                return False, msg

            # Преобразование ELF → HEX
            cmd_objcopy = [
                str(self.avr_tools['objcopy']),
                "-O", "ihex",
                str(elf_path),
                str(hex_path)
            ]

            print(f"[HEX] {' '.join(cmd_objcopy)}")
            result = subprocess.run(cmd_objcopy, capture_output=True, text=True, env=env)

            if result.returncode != 0:
                msg = f"Ошибка при objcopy:\n{result.stderr}"
                if callback:
                    callback(False, msg)
                return False, msg

            if callback:
                callback(True, "Компиляция завершена успешно")
            return True, "Компиляция завершена успешно"

        except Exception as e:
            msg = f"Исключение: {e}"
            if callback:
                callback(False, msg)
            return False, msg
