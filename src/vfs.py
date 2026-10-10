"""Виртуальная файловая система, полностью размещённая в памяти."""

import os
import posixpath
import time
from pathlib import Path


class VirtualFS:
    def __init__(self, folder):
        self.source = Path(folder)
        if not self.source.is_dir():
            raise FileNotFoundError(f"Не найдена директория VFS: {folder}")

        self.name = self.source.name
        self.directories = {"/"}
        self.files = {}
        self.modified = {}

        for current, dirs, files in os.walk(self.source):
            dirs[:] = sorted(
                name for name in dirs
                if not (Path(current) / name).is_symlink()
            )
            for name in dirs:
                path = Path(current) / name
                self.directories.add(self._virtual_path(path))
            for name in sorted(files):
                path = Path(current) / name
                if not path.is_symlink():
                    key = self._virtual_path(path)
                    self.files[key] = path.read_bytes()

    def _virtual_path(self, real_path):
        relative = real_path.relative_to(self.source)
        return "/" + relative.as_posix()

    def resolve(self, cwd, value):
        if value.startswith("/"):
            return posixpath.normpath(value)
        return posixpath.normpath(posixpath.join(cwd, value))

    def contents(self, path):
        if path in self.files:
            return [posixpath.basename(path)]
        if path not in self.directories:
            raise FileNotFoundError(f"Нет такого файла или каталога: {path}")
        prefix = path.rstrip("/") + "/"
        entries = set()
        for item in self.directories | self.files.keys():
            if item.startswith(prefix):
                relative = item[len(prefix):]
                if relative and "/" not in relative:
                    entries.add(relative)
        return sorted(entries)

    def touch(self, path):
        if path in self.directories:
            raise IsADirectoryError(f"Это каталог: {path}")
        if posixpath.dirname(path) not in self.directories:
            raise FileNotFoundError(f"Нет родительского каталога: {path}")
        self.files.setdefault(path, b"")
        self.modified[path] = time.time()

    def mkdir(self, path):
        if path in self.directories or path in self.files:
            raise FileExistsError(f"Файл или каталог уже существует: {path}")
        if posixpath.dirname(path) not in self.directories:
            raise FileNotFoundError(f"Нет родительского каталога: {path}")
        self.directories.add(path)
