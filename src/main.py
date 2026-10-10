"""Главный модуль эмулятора оболочки."""

from config import load_settings
from shell import Shell
from vfs import VirtualFS


def run_startup(shell, path):
    if path is None:
        return True
    with path.open(encoding="utf-8") as file:
        for text in file:
            line = text.strip()
            if not line or line.startswith("#"):
                continue
            print(shell.prompt + line)
            if not shell.execute(line):
                return False
    return True


def run_interactive(shell):
    while True:
        try:
            line = input(shell.prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not shell.execute(line):
            break


def main():
    try:
        settings = load_settings()
        print(f"Конфигурация: {settings['config']}")
        print(f"VFS: {settings['vfs']}")
        print(f"Стартовый скрипт: {settings['startup']}")
        shell = Shell(VirtualFS(settings["vfs"]))
        if not run_startup(shell, settings["startup"]):
            return 0
    except (OSError, ValueError) as error:
        print(f"Ошибка запуска: {error}")
        return 1
    run_interactive(shell)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
