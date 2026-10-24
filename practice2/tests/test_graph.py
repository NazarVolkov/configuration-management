"""Проверки рекурсивного DFS и тестового репозитория: этап 3."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import build_graph
from repository import TestRepository


class GraphTests(unittest.TestCase):
    """Проверять порядок DFS и остановку на уже посещённых узлах."""

    def test_dfs_and_shared_dependency(self):
        """Общая зависимость посещается один раз и раньше второй ветви."""
        data = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        visited = []

        def dependencies(name):
            """Запомнить порядок запросов к репозиторию."""
            visited.append(name)
            return data[name]

        self.assertEqual(build_graph("A", dependencies), data)
        self.assertEqual(visited, ["A", "B", "D", "C"])

    def test_cycle_self_cycle_and_leaf(self):
        """Цикл и петля не вызывают бесконечную рекурсию."""
        for data in ({"A": ["B"], "B": ["A"]},
                     {"A": ["A"]}, {"A": []}):
            with self.subTest(data=data):
                self.assertEqual(build_graph("A", data.__getitem__), data)

    def test_unreachable_and_duplicate_edges(self):
        """Лишние узлы не обходятся, повторное ребро удаляется."""
        data = {"A": ["B", "B"], "B": [], "Z": []}
        self.assertEqual(build_graph("A", data.__getitem__),
                         {"A": ["B"], "B": []})

    def test_repository_validation(self):
        """Неверные имена, ссылки и типы графа отклоняются."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.json"
            for data in ([], {}, {"a": []}, {"A": "B"},
                         {"A": [3]}, {"A": ["B"]}):
                path.write_text(json.dumps(data))
                with self.subTest(data=data):
                    with self.assertRaises(ValueError):
                        TestRepository(path)
            path.write_text('{"A": []}')
            repo = TestRepository(path)
            with self.assertRaises(ValueError):
                repo.root("Z")


if __name__ == "__main__":
    unittest.main()
