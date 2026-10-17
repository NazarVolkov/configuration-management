"""Проверка YAML и приоритета параметров."""

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import load_settings


class ConfigTests(unittest.TestCase):
    def test_yaml_and_override(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            config = base / "settings.yaml"
            config.write_text(
                "vfs_path: example\nstartup_script: start.txt\n",
                encoding="utf-8",
            )
            args = load_settings(["--config", str(config)])
            self.assertEqual(args["vfs"], base / "example")
            self.assertEqual(args["startup"], base / "start.txt")
            args = load_settings([
                "--config", str(config), "--vfs", str(base / "other")
            ])
            self.assertEqual(args["vfs"], base / "other")
            self.assertEqual(args["startup"], base / "start.txt")

    def test_bad_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "bad.yaml"
            for content in ("- one\n- two\n", "[]", "false", "0"):
                with self.subTest(content=content):
                    config.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_settings(["--config", str(config)])

    def test_vfs_path_is_required_but_startup_is_optional(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "settings.yaml"
            for value in ("null", "''", "42"):
                with self.subTest(value=value):
                    config.write_text(
                        f"vfs_path: {value}\n", encoding="utf-8",
                    )
                    with self.assertRaises(ValueError):
                        load_settings(["--config", str(config)])
            config.write_text(
                "vfs_path: example\nstartup_script: null\n", encoding="utf-8",
            )
            settings = load_settings(["--config", str(config)])
            self.assertIsNone(settings["startup"])


if __name__ == "__main__":
    unittest.main()
