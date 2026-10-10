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
            config.write_text("- one\n- two\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_settings(["--config", str(config)])


if __name__ == "__main__":
    unittest.main()
