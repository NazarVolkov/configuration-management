"""Команды учебной виртуальной оболочки."""

import time


MAX_PATH_ARGS = 1


class Shell:
    """Хранит текущий каталог, историю и обработчики команд."""

    def __init__(self, vfs):
        """Начать сеанс в корне VFS."""
        self.vfs = vfs
        self.cwd = "/"
        self.history = []
        self.started = time.monotonic()
        self.commands = {
            "ls": self.do_ls,
            "cd": self.do_cd,
            "pwd": self.do_pwd,
            "history": self.do_history,
            "uptime": self.do_uptime,
            "touch": self.do_touch,
            "mkdir": self.do_mkdir,
        }

    @property
    def prompt(self):
        """Показать имя VFS и текущий виртуальный путь."""
        return f"{self.vfs.name}:{self.cwd}$ "

    def execute(self, line):
        """Разобрать строку; вернуть False только для корректного exit."""
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

        handler = self.commands.get(command)
        if handler is None:
            print(f"Ошибка: неизвестная команда: {command}")
            return True
        try:
            handler(args)
        except (OSError, ValueError) as error:
            print(f"{command}: {error}")
        return True

    def do_ls(self, args):
        """Показать каталог или имя отдельного файла."""
        if len(args) > MAX_PATH_ARGS:
            raise ValueError("нужно не более одного пути")
        path = self.vfs.resolve(self.cwd, args[0] if args else ".")
        print("  ".join(self.vfs.contents(path)))

    def do_cd(self, args):
        """Перейти в каталог; без аргументов перейти в корень."""
        if len(args) > MAX_PATH_ARGS:
            raise ValueError("нужно не более одного пути")
        path = self.vfs.resolve(self.cwd, args[0] if args else "/")
        if path not in self.vfs.directories:
            raise NotADirectoryError(f"не найден каталог: {path}")
        self.cwd = path

    def do_pwd(self, args):
        """Вывести текущий путь."""
        if args:
            raise ValueError("команда не принимает аргументы")
        print(self.cwd)

    def do_history(self, args):
        """Вывести историю текущего сеанса с номерами."""
        if args:
            raise ValueError("команда не принимает аргументы")
        for index, line in enumerate(self.history, 1):
            print(f"{index}  {line}")

    def do_uptime(self, args):
        """Вывести время работы эмулятора в часах, минутах и секундах."""
        if args:
            raise ValueError("команда не принимает аргументы")
        seconds = int(time.monotonic() - self.started)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        print(f"up {hours:02d}:{minutes:02d}:{seconds:02d}")

    def do_touch(self, args):
        """Создать файлы или обновить их время изменения в памяти."""
        if not args:
            raise ValueError("нужно указать файл")
        for name in args:
            if name.endswith("/"):
                raise ValueError("путь к файлу не должен оканчиваться на /")
            path = self.vfs.resolve(self.cwd, name)
            self.vfs.touch(path)

    def do_mkdir(self, args):
        """Создать каталоги с существующими родителями."""
        if not args:
            raise ValueError("нужно указать каталог")
        for name in args:
            path = self.vfs.resolve(self.cwd, name)
            self.vfs.mkdir(path)
