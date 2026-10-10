"""Проверка команд оболочки."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shell import Shell
from vfs import VirtualFS


class ShellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        (base / "docs").mkdir()
        (base / "docs" / "test.txt").write_text("test")
        self.shell = Shell(VirtualFS(base))

    def tearDown(self):
        self.tmp.cleanup()

    def execute(self, command):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = self.shell.execute(command)
        return result, output.getvalue()

    def test_ls_cd_pwd(self):
        self.assertIn("docs", self.execute("ls")[1])
        self.execute("cd docs")
        self.assertEqual(self.execute("pwd")[1].strip(), "/docs")
        self.assertIn("test.txt", self.execute("ls")[1])
        self.execute("cd ..")
        self.assertEqual(self.shell.cwd, "/")

    def test_touch_and_mkdir_in_memory(self):
        base = Path(self.tmp.name)
        self.execute("mkdir virtual")
        self.execute("cd virtual")
        self.execute("touch file.txt more.txt")
        self.assertIn("file.txt", self.execute("ls")[1])
        self.assertIn("/virtual/more.txt", self.shell.vfs.files)
        self.assertFalse((base / "virtual").exists())
        self.assertIn("уже существует", self.execute("mkdir .")[1])
        self.assertIn("Это каталог", self.execute("touch .")[1])
        self.assertIn("Нет родительского", self.execute(
            "touch /missing/file.txt")[1])

    def test_history_and_errors(self):
        self.execute("pwd")
        self.execute("cd missing")
        self.assertEqual(self.shell.cwd, "/")
        self.assertIn("не найден каталог", self.execute("cd missing")[1])
        self.assertIn("1  pwd", self.execute("history")[1])
        self.assertIn("лишние аргументы", self.execute("exit now")[1])
        self.assertFalse(self.execute("exit")[0])


if __name__ == "__main__":
    unittest.main()
