"""Параметры командной строки и YAML-конфигурации."""

import argparse
from pathlib import Path

import yaml


def load_settings(argv=None):
    parser = argparse.ArgumentParser(description="Эмулятор оболочки, вариант 5")
    parser.add_argument("--config", help="Путь к YAML-конфигурации")
    parser.add_argument("--vfs", help="Каталог виртуальной файловой системы")
    parser.add_argument("--startup", help="Путь к стартовому скрипту")
    args = parser.parse_args(argv)

    config_path = Path(args.config or "config.yaml").resolve()
    settings = {}
    if config_path.exists():
        with config_path.open(encoding="utf-8") as file:
            settings = yaml.safe_load(file) or {}
        if not isinstance(settings, dict):
            raise ValueError("YAML должен содержать словарь параметров")
    elif args.config:
        raise FileNotFoundError(f"Конфигурация не найдена: {config_path}")

    def get_path(command_value, key, default=None):
        if command_value is not None:
            return Path(command_value).resolve()
        value = settings.get(key, default)
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"Неверное значение YAML: {key}")
        return (config_path.parent / value).resolve()

    return {
        "config": config_path if config_path.exists() else None,
        "vfs": get_path(args.vfs, "vfs_path", "vfs/demo"),
        "startup": get_path(args.startup, "startup_script"),
    }
