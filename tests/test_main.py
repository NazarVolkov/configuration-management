"""Проверки запуска, стартового скрипта и интерактивного режима."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MainTests(unittest.TestCase):
    """Проверки приложения как отдельного процесса."""

    def run_app(self, *args, commands=""):
        """Запустить приложение с аргументами и подготовленным вводом."""
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "src" / "main.py"), *args],
            input=commands, text=True, capture_output=True, cwd=ROOT,
        )

    def test_interactive_commands_and_exit(self):
        """Команды выполняются до exit, ошибки не прерывают сеанс."""
        result = self.run_app(
            commands="ls\nunknown\npwd\nuptime\nexit\nignored_after_exit\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("demo:/$ /\n", result.stdout)
        self.assertIn("hello.txt", result.stdout)
        self.assertIn("неизвестная команда", result.stdout)
        self.assertIn("up ", result.stdout)
        self.assertNotIn("ignored_after_exit", result.stdout)

    def test_script_echo_comments_and_errors(self):
        """Скрипт показывает команды и ошибки, пропуская комментарии."""
        result = self.run_app("--startup", "scripts/startup_stage5.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("demo:/$ mkdir new_folder", result.stdout)
        self.assertNotIn("# Этап 5.", result.stdout)
        self.assertIn("уже существует", result.stdout)
        self.assertIn("неизвестная команда", result.stdout)
        self.assertIn("first.txt", result.stdout)

    def test_command_line_overrides_yaml(self):
        """Пути VFS и стартового скрипта можно заменить через CLI."""
        result = self.run_app(
            "--config", "config.yaml", "--vfs", "vfs/minimal",
            "--startup", "scripts/startup_stage3.txt",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("minimal:/$ ls", result.stdout)
        self.assertIn("README.txt", result.stdout)
        self.assertNotIn("hello.txt", result.stdout)

    def test_missing_paths(self):
        """Отсутствующие пути дают понятную ошибку запуска."""
        for option in ("--vfs", "--startup", "--config"):
            with self.subTest(option=option):
                result = self.run_app(option, "not_an_existing_path")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Ошибка запуска", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_bad_yaml_does_not_crash(self):
        """Некорректная конфигурация обрабатывается без traceback."""
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "wrong.yaml"
            for content in ("broken: [\n", "vfs_path: null\n"):
                with self.subTest(content=content):
                    config.write_text(content, encoding="utf-8")
                    result = self.run_app("--config", str(config))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Ошибка запуска", result.stdout)
                    self.assertNotIn("Traceback", result.stderr)

    def test_exit_stops_startup_and_interactive_input(self):
        """Exit в скрипте прекращает скрипт и дальнейший ввод."""
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "exit.txt"
            script.write_text("exit\nunknown_after_exit\n", encoding="utf-8")
            result = self.run_app(
                "--startup", str(script), commands="unknown_from_input\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("unknown_after_exit", result.stdout)
            self.assertNotIn("unknown_from_input", result.stdout)

    @unittest.skipUnless(sys.platform == "win32", "Только Windows")
    def test_windows_check_scripts(self):
        """Проверочные сценарии Windows завершаются успешно."""
        for name in ("check_config.bat", "check_vfs.bat"):
            with self.subTest(name=name):
                result = subprocess.run(
                    ["cmd", "/d", "/c", "scripts\\" + name],
                    text=True, capture_output=True, cwd=ROOT,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("===", result.stdout)


if __name__ == "__main__":
    unittest.main()
