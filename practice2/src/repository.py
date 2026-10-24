"""Выбор реального NuGet или маленького JSON-репозитория."""

import json
import re
from pathlib import Path

from nuget import NuGetRepository


class TestRepository:
    """Локальный репозиторий вида имя пакета -> список зависимостей."""

    def __init__(self, filename):
        """Прочитать граф и проверить имена и ссылки."""
        self.graph = json.loads(Path(filename).read_text(encoding="utf-8"))
        if not isinstance(self.graph, dict) or not self.graph:
            raise ValueError("Тестовый репозиторий должен быть объектом")
        for name, dependencies in self.graph.items():
            if not re.fullmatch(r"[A-Z]+", name):
                raise ValueError(f"Неверное тестовое имя: {name}")
            if not isinstance(dependencies, list):
                raise ValueError(f"Зависимости {name} должны быть списком")
            for dependency in dependencies:
                if not isinstance(dependency, str):
                    raise ValueError(f"Неверная зависимость у {name}")
                if dependency not in self.graph:
                    raise ValueError(f"Нет описания пакета {dependency}")

    def root(self, package, version=None):
        """Проверить существование выбранного корня."""
        if package not in self.graph:
            raise ValueError(f"Пакет не найден: {package}")
        return package

    def dependencies(self, package):
        """Вернуть прямые зависимости из словаря."""
        return self.graph[package]


def open_repository(settings):
    """Создать источник с одинаковыми методами root и dependencies."""
    if settings["test_mode"]:
        return TestRepository(settings["repository"])
    return NuGetRepository(settings["repository"], settings["framework"])
