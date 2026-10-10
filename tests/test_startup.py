"""Проверка исполнения стартового файла и порядка источников."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StartupTests(unittest.TestCase):
    def run_app(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py"), *args],
            text=True, input="", capture_output=True, check=False,
            cwd=ROOT,
        )

    def test_script_echo_comments_and_errors(self):
        result = self.run_app(
            "--startup", "scripts/startup_stage5.txt"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("demo:/$ mkdir new_folder", result.stdout)
        self.assertNotIn("# Этап 5.", result.stdout)
        self.assertIn("уже существует", result.stdout)
        self.assertIn("неизвестная команда", result.stdout)
        self.assertIn("first.txt", result.stdout)

    def test_command_line_overrides_yaml(self):
        result = self.run_app(
            "--config", "config.yaml", "--vfs", "vfs/minimal",
            "--startup", "scripts/startup_demo.txt",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("minimal:/$ pwd", result.stdout)
        self.assertIn("README.txt", result.stdout)
        self.assertNotIn("hello.txt", result.stdout)

    def test_missing_startup_file(self):
        result = self.run_app("--startup", "not_a_script.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Ошибка запуска", result.stdout)

    def test_yaml_error(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "wrong.yaml"
            config.write_text("broken: [\n", encoding="utf-8")
            result = self.run_app("--config", str(config))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Ошибка YAML", result.stdout)


if __name__ == "__main__":
    unittest.main()
