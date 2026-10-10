"""Эмулятор командной строки: конфигурация и REPL."""

from config import load_settings
from vfs import VirtualFS


def run_line(line):
    parts = line.split()
    if not parts:
        return True

    command, args = parts[0], parts[1:]
    if command == "exit":
        if args:
            print("exit: неверные аргументы")
            return True
        return False
    if command in ("ls", "cd"):
        print(f"{command}: {args}")
    else:
        print(f"Ошибка: неизвестная команда: {command}")
    return True


def main():
    try:
        settings = load_settings()
        print(f"Конфигурация: {settings['config']}")
        print(f"VFS: {settings['vfs']}")
        print(f"Стартовый скрипт: {settings['startup']}")

        vfs = VirtualFS(settings["vfs"])
        name = vfs.name
        prompt = f"{name}:/$ "
        if settings["startup"]:
            with settings["startup"].open(encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    print(prompt + line)
                    if not run_line(line):
                        return
    except (OSError, ValueError) as error:
        print(f"Ошибка запуска: {error}")
        return 1

    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not run_line(line):
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
