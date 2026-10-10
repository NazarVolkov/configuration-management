"""Команды учебной виртуальной оболочки."""

import time


class Shell:
    def __init__(self, vfs):
        self.vfs = vfs
        self.cwd = "/"
        self.history = []

    @property
    def prompt(self):
        return f"{self.vfs.name}:{self.cwd}$ "

    def execute(self, line):
        parts = line.split()
        if not parts:
            return True
        command, args = parts[0], parts[1:]
        self.history.append(line.strip())

        if command == "exit":
            if args:
                print("exit: лишние аргументы")
                return True
            return False

        handler = getattr(self, f"do_{command}", None)
        if handler is None:
            print(f"Ошибка: неизвестная команда: {command}")
            return True
        try:
            handler(args)
        except (OSError, ValueError) as error:
            print(f"{command}: {error}")
        return True

    def do_ls(self, args):
        if len(args) > 1:
            raise ValueError("нужно не более одного пути")
        path = self.vfs.resolve(self.cwd, args[0] if args else ".")
        print("  ".join(self.vfs.contents(path)))

    def do_cd(self, args):
        if len(args) > 1:
            raise ValueError("нужно не более одного пути")
        path = self.vfs.resolve(self.cwd, args[0] if args else "/")
        if path not in self.vfs.directories:
            raise NotADirectoryError(f"не найден каталог: {path}")
        self.cwd = path

    def do_pwd(self, args):
        if args:
            raise ValueError("команда не принимает аргументы")
        print(self.cwd)

    def do_history(self, args):
        if args:
            raise ValueError("команда не принимает аргументы")
        for index, line in enumerate(self.history, 1):
            print(f"{index}  {line}")

    def do_uptime(self, args):
        if args:
            raise ValueError("команда не принимает аргументы")
        seconds = int(time.monotonic())
        days, rest = divmod(seconds, 86400)
        hours, rest = divmod(rest, 3600)
        minutes = rest // 60
        print(f"up {days} days, {hours:02d}:{minutes:02d}")
