"""Консольный визуализатор зависимостей NuGet, вариант 5."""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from config import load_config
from graph import build_graph, print_graph, reverse_dependencies
from repository import open_repository
from visualize import ascii_tree, save_diagram


CONFIG_STAGE = 1
DIRECT_STAGE = 2
GRAPH_STAGE = 3
REVERSE_STAGE = 4
VISUAL_STAGE = 5


def run(settings, stage, reverse=None, no_open=False, no_image=False):
    """Выполнить выбранный этап работы."""
    if stage == CONFIG_STAGE:
        for key, value in settings.items():
            print(f"{key} = {value}")
        return
    repository = open_repository(settings)
    root = repository.root(settings["package"], settings["version"])
    if stage == DIRECT_STAGE:
        print(root)
        for dependency in repository.dependencies(root):
            print(f"  {dependency}")
        return
    graph = build_graph(root, repository.dependencies)
    if stage == REVERSE_STAGE:
        source = repository.graph if settings["test_mode"] else graph
        graph = reverse_dependencies(source, reverse or root)
    if stage != VISUAL_STAGE:
        print_graph(graph)
        return
    if settings["ascii_tree"]:
        print(ascii_tree(graph, root))
    output = Path(__file__).resolve().parents[1] / "output"
    save_diagram(graph, root, output, not no_open, not no_image)


def main():
    """Прочитать настройки и выполнить выбранный этап."""
    parser = argparse.ArgumentParser(description="Зависимости NuGet")
    parser.add_argument("config", nargs="?", default="config.json")
    parser.add_argument("--stage", type=int,
                        choices=range(CONFIG_STAGE, VISUAL_STAGE + 1),
                        default=VISUAL_STAGE)
    parser.add_argument("--reverse", help="Пакет для обратного поиска этапа 4")
    parser.add_argument("--no-open", action="store_true",
                        help="Сохранить изображение без открытия браузера")
    parser.add_argument("--no-image", action="store_true",
                        help="Без сети: только PlantUML и ASCII-дерево")
    args = parser.parse_args()
    if args.reverse is not None and args.stage != REVERSE_STAGE:
        parser.error("--reverse используется только с --stage 4")
    try:
        settings = load_config(args.config)
        run(settings, args.stage, args.reverse, args.no_open, args.no_image)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
