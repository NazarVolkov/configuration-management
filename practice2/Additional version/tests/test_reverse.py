"""Проверки обратных зависимостей и повторного использования DFS: этап 4."""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import reverse_dependencies


class ReverseTests(unittest.TestCase):
    """Обратный граф содержит прямых и косвенных потребителей пакета."""

    def test_shared_dependency(self):
        """D используется B и C, а через них пакетом A."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        result = reverse_dependencies(graph, "D")
        self.assertEqual(result,
                         {"D": ["B", "C"], "B": ["A"], "A": [],
                          "C": ["A"]})
        self.assertEqual(reverse_dependencies(graph, "A"), {"A": []})

    def test_cycle(self):
        """После разворота цикл также обходится конечное число раз."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        self.assertEqual(reverse_dependencies(graph, "B"),
                         {"B": ["A"], "A": ["C"], "C": ["B"]})

    def test_other_components_and_missing_package(self):
        """Для поиска учитывается весь переданный репозиторий."""
        graph = {"A": [], "Z": ["A"]}
        self.assertEqual(reverse_dependencies(graph, "A"),
                         {"A": ["Z"], "Z": []})
        with self.assertRaises(ValueError):
            reverse_dependencies(graph, "MISSING")


if __name__ == "__main__":
    unittest.main()
