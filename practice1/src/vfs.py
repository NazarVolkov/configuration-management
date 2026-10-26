"""Виртуальная файловая система, полностью размещённая в памяти."""

import os
import posixpath
import time
from pathlib import Path


class VirtualFS:
    """Каталоги хранятся в множестве, содержимое файлов - в словаре."""

    def __init__(self, folder):
        """Один раз прочитать исходную директорию, пропуская ссылки."""
        self.source = Path(folder)
        if not self.source.is_dir():
            raise FileNotFoundError(f"Не найдена директория VFS: {folder}")

        self.name = self.source.name
        self.directories = {"/"}
        self.files = {}
        self.modified = {}

        for current, dirs, files in os.walk(self.source):
            dirs[:] = [
                name for name in dirs
                if not (Path(current) / name).is_symlink()
            ]
            for name in dirs:
                path = Path(current) / name
                self.directories.add(self._virtual_path(path))
            for name in files:
                path = Path(current) / name
                if not path.is_symlink():
                    key = self._virtual_path(path)
                    self.files[key] = path.read_bytes()

    def _virtual_path(self, real_path):
        """Заменить физический путь виртуальным, начинающимся с /."""
        relative = real_path.relative_to(self.source)
        return "/" + relative.as_posix()

    def resolve(self, cwd, value):
        """Пройти путь по компонентам, проверяя промежуточные каталоги."""
        path = "/" if value.startswith("/") else cwd
        for part in value.split("/"):
            if not part:
                continue
            if path not in self.directories:
                raise NotADirectoryError(f"не найден каталог: {path}")
            path = posixpath.normpath(posixpath.join(path, part))
        if value.endswith("/") and path in self.files:
            raise NotADirectoryError(f"Это не каталог: {path}")
        return path

    def contents(self, path):
        """Вернуть отсортированные имена непосредственных потомков."""
        if path in self.files:
            return [posixpath.basename(path)]
        if path not in self.directories:
            raise FileNotFoundError(f"Нет такого файла или каталога: {path}")
        entries = self.directories | self.files.keys()
        return sorted(
            posixpath.basename(item) for item in entries
            if item != "/" and posixpath.dirname(item) == path
        )

    def touch(self, path):
        """Создать пустой файл или обновить его виртуальное время."""
        if path in self.directories:
            raise IsADirectoryError(f"Это каталог: {path}")
        if posixpath.dirname(path) not in self.directories:
            raise FileNotFoundError(f"Нет родительского каталога: {path}")
        self.files.setdefault(path, b"")
        self.modified[path] = time.time()

    def mkdir(self, path):
        """Добавить каталог в множество, не записывая его на диск."""
        if path in self.directories or path in self.files:
            raise FileExistsError(f"Файл или каталог уже существует: {path}")
        if posixpath.dirname(path) not in self.directories:
            raise FileNotFoundError(f"Нет родительского каталога: {path}")
        self.directories.add(path)
