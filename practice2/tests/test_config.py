"""Проверки обязательных настроек и ошибок этапа 1."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import load_config


class ConfigTests(unittest.TestCase):
    """Параметры проверяются до обращения к репозиторию."""

    def setUp(self):
        """Создать независимые тестовые файлы."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / "repo.json").write_text('{"A": []}')
        self.path = self.base / "config.json"
        self.settings = {
            "package": "A", "repository": "repo.json",
            "test_mode": True, "ascii_tree": True,
        }

    def load(self, settings):
        """Записать JSON и вызвать проверяемую функцию."""
        self.path.write_text(json.dumps(settings), encoding="utf-8")
        return load_config(self.path)

    def test_valid_and_relative_path(self):
        """Путь отсчитывается от файла конфигурации."""
        result = self.load(self.settings)
        self.assertEqual(result["repository"], str(self.base / "repo.json"))

    def test_each_required_parameter(self):
        """Отсутствие любого обязательного параметра является ошибкой."""
        for key in self.settings:
            with self.subTest(key=key):
                bad = self.settings.copy()
                del bad[key]
                with self.assertRaises(ValueError):
                    self.load(bad)

    def test_invalid_values(self):
        """Неверные имена, пути и типы не принимаются."""
        for key, value in (
            ("package", "a"), ("package", ""), ("package", 5),
            ("repository", "missing.json"), ("repository", 5),
            ("test_mode", "true"), ("ascii_tree", 1),
        ):
            with self.subTest(key=key, value=value):
                bad = dict(self.settings, **{key: value})
                with self.assertRaises(ValueError):
                    self.load(bad)

    def test_real_url(self):
        """В обычном режиме требуется адрес HTTP или HTTPS."""
        real = dict(self.settings, package="Example.Core", test_mode=False)
        with self.assertRaises(ValueError):
            self.load(real)
        real["repository"] = "https://api.nuget.org/v3/index.json"
        self.assertEqual(self.load(real)["package"], "Example.Core")

    def test_bad_json_and_top_level(self):
        """Синтаксическая ошибка JSON и список вместо объекта запрещены."""
        for text in ("{", "[]"):
            self.path.write_text(text)
            with self.assertRaises(ValueError):
                load_config(self.path)


if __name__ == "__main__":
    unittest.main()
