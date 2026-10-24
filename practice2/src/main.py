"""Консольный визуализатор зависимостей NuGet, вариант 5."""

import argparse
import xml.etree.ElementTree as ET

from config import load_config
from graph import build_graph, print_graph, reverse_dependencies
from repository import open_repository


def run(settings, stage, reverse=None):
    """Показать настройки или прямые зависимости."""
    if stage == 1:
        for key, value in settings.items():
            print(f"{key} = {value}")
        return
    repository = open_repository(settings)
    root = repository.root(settings["package"], settings["version"])
    if stage == 2:
        print(root)
        for dependency in repository.dependencies(root):
            print(f"  {dependency}")
        return
    graph = build_graph(root, repository.dependencies)
    if stage == 4:
        source = repository.graph if settings["test_mode"] else graph
        graph = reverse_dependencies(source, reverse or root)
    print_graph(graph)


def main():
    """Прочитать настройки и выполнить выбранный этап."""
    parser = argparse.ArgumentParser(description="Зависимости NuGet")
    parser.add_argument("config", nargs="?", default="config.json")
    parser.add_argument("--stage", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--reverse", help="Пакет для обратного поиска этапа 4")
    args = parser.parse_args()
    if args.reverse is not None and args.stage != 4:
        parser.error("--reverse используется только с --stage 4")
    try:
        settings = load_config(args.config)
        run(settings, args.stage, args.reverse)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
