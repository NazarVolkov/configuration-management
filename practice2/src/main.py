"""Консольный визуализатор зависимостей NuGet, вариант 5."""

import argparse
import xml.etree.ElementTree as ET

from config import load_config
from repository import open_repository


def run(settings, stage):
    """Показать настройки или прямые зависимости."""
    if stage == 1:
        for key, value in settings.items():
            print(f"{key} = {value}")
        return
    repository = open_repository(settings)
    root = repository.root(settings["package"], settings["version"])
    print(root)
    for dependency in repository.dependencies(root):
        print(f"  {dependency}")


def main():
    """Прочитать настройки и выполнить выбранный этап."""
    parser = argparse.ArgumentParser(description="Зависимости NuGet")
    parser.add_argument("config", nargs="?", default="config.json")
    parser.add_argument("--stage", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    try:
        settings = load_config(args.config)
        run(settings, args.stage)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
