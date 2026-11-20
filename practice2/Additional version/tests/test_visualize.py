"""Проверки ASCII-дерева и PlantUML: этап 5."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from visualize import ascii_tree, plantuml, save_diagram


class VisualizeTests(unittest.TestCase):
    """Проверять структуру рисунка без сетевого обращения в тестах."""

    def test_tree_shared_node_and_cycle(self):
        """Общая вершина и цикл отмечаются по-разному."""
        graph = {"A": ["B", "C"], "B": ["D"], "D": [], "C": ["D"]}
        expected = "A\n+-- B\n|   `-- D\n`-- C\n    `-- D [shown]"
        self.assertEqual(ascii_tree(graph, "A"), expected)
        cycle = ascii_tree({"A": ["B"], "B": ["A"]}, "A")
        self.assertIn("A [cycle]", cycle)
        self.assertEqual(ascii_tree({"A": []}, "A"), "A")

    def test_plantuml_nodes_and_edges(self):
        """Код PlantUML содержит узлы, направление и обратное ребро цикла."""
        text = plantuml({"A": ["B"], "B": ["A"]})
        self.assertIn('component "A" as N0', text)
        self.assertIn("N0 --> N1", text)
        self.assertIn("N1 --> N0", text)
        self.assertTrue(text.startswith("@startuml\n"))
        self.assertTrue(text.endswith("@enduml\n"))

    def test_save_and_browser_open(self):
        """Изображение показывается, а автономный режим не требует сети."""
        with tempfile.TemporaryDirectory() as folder:
            with patch("visualize.render_svg") as render:
                with patch("visualize.webbrowser.open") as browser:
                    save_diagram({"A": []}, "A", folder)
                    render.assert_called_once()
                    browser.assert_called_once()
            self.assertTrue((Path(folder) / "A.puml").exists())
            with patch("visualize.render_svg") as render:
                save_diagram({"A": []}, "A", folder, render=False)
                render.assert_not_called()


if __name__ == "__main__":
    unittest.main()
