"""Проверки целого CLI-приложения на локальных данных."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    """Внешний запуск проверяет аргументы, режимы и сообщения об ошибках."""

    def run_app(self, *args):
        """Запустить программу без открытия браузера."""
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "src/main.py"), *args],
            cwd=ROOT, text=True, capture_output=True,
        )

    def test_stages_and_reverse(self):
        """Каждый из первых четырёх этапов доступен отдельно."""
        for stage in range(1, 5):
            with self.subTest(stage=stage):
                result = self.run_app("--stage", str(stage))
                self.assertEqual(result.returncode, 0, result.stdout)
        result = self.run_app("--stage", "4", "--reverse", "D")
        self.assertIn("D -> B, C", result.stdout)
        result = self.run_app("--stage", "4", "--reverse", "Z")
        self.assertNotEqual(result.returncode, 0)

    def test_no_image_and_ascii_switch(self):
        """Вывод дерева управляется JSON-параметром."""
        result = self.run_app("--no-image")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("+-- B", result.stdout)
        with tempfile.TemporaryDirectory() as folder:
            settings = json.loads((ROOT / "config.json").read_text())
            settings["repository"] = str(ROOT / "examples/branch.json")
            settings["ascii_tree"] = False
            config = Path(folder) / "config.json"
            config.write_text(json.dumps(settings))
            result = self.run_app(str(config), "--no-image")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("+-- B", result.stdout)

    def test_errors_without_traceback(self):
        """Ошибки параметров сообщаются без падения Python."""
        result = self.run_app("missing-config.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        result = self.run_app("--stage", "2", "--reverse", "A")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
