"""Проверка основных команд REPL."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReplTests(unittest.TestCase):
    def test_stubs_and_exit(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py")],
            input="ls one two\ncd docs\nunknown\nexit\n",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn("ls: ['one', 'two']", process.stdout)
        self.assertIn("cd: ['docs']", process.stdout)
        self.assertIn("неизвестная команда", process.stdout)


if __name__ == "__main__":
    unittest.main()
