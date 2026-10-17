"""Проверка команд оболочки."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shell import Shell
from vfs import VirtualFS


class ShellTests(unittest.TestCase):
    """Проверки команд и состояния оболочки."""

    def setUp(self):
        """Подготовить отдельную VFS перед каждым тестом."""
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        (base / "docs").mkdir()
        (base / "docs" / "test.txt").write_text("test")
        self.shell = Shell(VirtualFS(base))

    def tearDown(self):
        """Удалить временную исходную директорию после теста."""
        self.tmp.cleanup()

    def execute(self, command):
        """Выполнить команду и вернуть признак продолжения и вывод."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = self.shell.execute(command)
        return result, output.getvalue()

    def test_ls_cd_pwd(self):
        """Просмотр файлов и переходы используют текущий виртуальный путь."""
        self.assertIn("docs", self.execute("ls")[1])
        self.execute("cd docs")
        self.assertEqual(self.execute("pwd")[1].strip(), "/docs")
        self.assertIn("test.txt", self.execute("ls")[1])
        self.execute("cd ..")
        self.assertEqual(self.shell.cwd, "/")

    def test_touch_and_mkdir_in_memory(self):
        """Создание объектов меняет только память и проверяет ошибки."""
        base = Path(self.tmp.name)
        self.execute("mkdir virtual")
        self.execute("cd virtual")
        self.execute("touch file.txt more.txt")
        self.assertIn("file.txt", self.execute("ls")[1])
        self.assertIn("/virtual/more.txt", self.shell.vfs.files)
        self.assertFalse((base / "virtual").exists())
        self.assertIn("уже существует", self.execute("mkdir .")[1])
        self.assertIn("Это каталог", self.execute("touch .")[1])
        self.assertIn("/missing", self.execute(
            "touch /missing/file.txt")[1])
        self.assertNotIn("/missing/file.txt", self.shell.vfs.files)

    def test_history_and_errors(self):
        """История нумеруется, а ошибка команды сохраняет рабочий сеанс."""
        self.execute("pwd")
        self.execute("cd missing")
        self.assertEqual(self.shell.cwd, "/")
        self.assertIn("не найден каталог", self.execute("cd missing")[1])
        self.assertIn("1  pwd", self.execute("history")[1])
        self.assertIn("лишние аргументы", self.execute("exit now")[1])
        self.assertFalse(self.execute("exit")[0])

    def test_bad_arguments_do_not_stop_shell(self):
        """Неверные аргументы и пути не меняют текущий каталог."""
        commands = (
            "ls one two", "cd one two", "pwd extra", "history extra",
            "uptime extra", "touch", "mkdir", "touch newfile/",
            "cd docs/test.txt/..",
        )
        for command in commands:
            with self.subTest(command=command):
                running, output = self.execute(command)
                self.assertTrue(running)
                self.assertTrue(output.strip())
        self.assertEqual(self.shell.cwd, "/")
        self.assertNotIn("/newfile", self.shell.vfs.files)

    def test_uptime_starts_with_emulator(self):
        """Время работы отсчитывается от момента создания оболочки."""
        with patch("shell.time.monotonic", return_value=self.shell.started):
            self.assertEqual(self.execute("uptime")[1], "up 00:00:00\n")
        later = self.shell.started + 3661
        with patch("shell.time.monotonic", return_value=later):
            self.assertEqual(self.execute("uptime")[1], "up 01:01:01\n")


if __name__ == "__main__":
    unittest.main()
