"""Консольный визуализатор зависимостей NuGet, вариант 5."""

import argparse

from config import load_config


def main():
    """Прочитать настройки и выполнить выбранный этап."""
    parser = argparse.ArgumentParser(description="Зависимости NuGet")
    parser.add_argument("config", nargs="?", default="config.json")
    args = parser.parse_args()
    try:
        settings = load_config(args.config)
        for key, value in settings.items():
            print(f"{key} = {value}")
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
