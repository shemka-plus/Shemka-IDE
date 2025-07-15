import subprocess
from pathlib import Path
import os
import re

class AVRCompiler:
    def __init__(self, avr_tools, tools_root=None):
        self.avr_tools = avr_tools
        self.tools_root = Path(tools_root) if tools_root else Path(__file__).parent.parent / "bin"
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

            src_file = output_dir / "sketch.cpp"
            with open(src_file, "w", encoding="utf-8") as f:
                if '#include <Arduino.h>' not in source_code:
                    f.write('#include <Arduino.h>\n\n')
                f.write(source_code)

            specs_file = self.device_specs / f"specs-{mcu}"
            if not specs_file.exists():
                raise FileNotFoundError(f"Файл спецификаций не найден: {specs_file}")

            elf_path = output_dir / "sketch.elf"
            hex_path = output_dir / "sketch.hex"

            env = os.environ.copy()
            env["PATH"] = os.pathsep.join([
                str(self.bin_dir),
                str(self.libexec_dir / "gcc" / "avr" / "7.3.0"),
                str(self.lib_dir),
                env.get("PATH", "")
            ])

            core_files = [
                f for f in self.cores_dir.glob("*.*")
                if f.suffix in [".c", ".cpp", ".S"] and f.name != "wiring_pulse.c"
            ]

            object_files = []

            # Компиляция всех исходников по отдельности
            for file in [src_file] + core_files:
                obj_file = output_dir / (file.stem + ".o")
                object_files.append(obj_file)

                cmd = [
                    str(self.avr_tools['gcc']),
                    "-Wall", "-Os",
                    "-DF_CPU=16000000UL",
                    f"-mmcu={mcu}",
                    "-B", str(self.device_specs),
                    "-I", str(self.include_dir),
                    "-I", str(self.cores_dir),
                    "-c", str(file),
                    "-o", str(obj_file)
                ]

                # Применим -std=gnu++11 только к .cpp
                if file.suffix == ".cpp":
                    cmd.insert(2, "-std=gnu++11")

                result = subprocess.run(cmd, capture_output=True, text=True, env=env)

                if result.returncode != 0:
                    msg = f"Ошибка компиляции {file.name}:\n{result.stderr}"
                    if callback:
                        callback(True, msg, [])
                    return False, msg, []

            # Линковка
            link_cmd = [
                str(self.avr_tools['gcc']),
                "-mmcu=" + mcu,
                "-o", str(elf_path)
            ] + [str(f) for f in object_files]

            print(f"[Линковка] {' '.join(link_cmd)}")
            result = subprocess.run(link_cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                msg = f"Ошибка линковки:\n{result.stderr}"
                if callback:
                    callback(True, msg, [])
                return False, msg, []

            # Преобразование в .hex
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
                    callback(True, msg, [])
                return False, msg, []

            if callback:
                callback(True, "Компиляция завершена успешно", [])
            # Очистка object-файлов
            for obj in object_files:
                try:
                    obj.unlink()
                except Exception as e:
                    print(f"[WARNING] Не удалось удалить {obj.name}: {e}")
            return True, "Компиляция завершена успешно", []

        except Exception as e:
            msg = f"Исключение: {e}"
            if callback:
                callback(False, msg, [])
            return False, msg, []


    def _parse_errors(self, stderr):
        pattern = re.compile(r"(.+?):(\\d+):(\\d+): error: (.+)")
        matches = pattern.findall(stderr)
        return [(fname, int(line), int(col), msg.strip()) for fname, line, col, msg in matches]
