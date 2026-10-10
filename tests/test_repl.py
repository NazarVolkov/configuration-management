"""Проверки REPL, ошибок и завершения."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReplTests(unittest.TestCase):
    def test_repl_and_exit(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py"),
             "--startup", str(ROOT / "scripts" / "startup_stage4.txt")],
            input="ls\nunknown\npwd\nexit\n",
            text=True,
            capture_output=True,
            check=False,
            cwd=ROOT,
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn("demo:/$ pwd", process.stdout)
        self.assertIn("hello.txt", process.stdout)
        self.assertIn("неизвестная команда", process.stdout)
        self.assertIn("up ", process.stdout)

    def test_unknown_vfs(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py"),
             "--vfs", "/missing-directory-1234"],
            input="",
            text=True,
            capture_output=True,
            check=False,
            cwd=ROOT,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("Ошибка запуска", process.stdout)


if __name__ == "__main__":
    unittest.main()
