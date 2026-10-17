"""Параметры командной строки и YAML-конфигурации."""

import argparse
from pathlib import Path

import yaml


def read_yaml(path):
    """Прочитать YAML и убедиться, что в нём словарь настроек."""
    try:
        with path.open(encoding="utf-8") as file:
            settings = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Ошибка YAML: {error}") from error
    if settings is None:
        return {}
    if not isinstance(settings, dict):
        raise ValueError("YAML должен содержать словарь параметров")
    return settings


def load_settings(argv=None):
    """Прочитать YAML, затем заменить его значения аргументами CLI."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки, вариант 5")
    parser.add_argument("--config", help="Путь к YAML-конфигурации")
    parser.add_argument("--vfs", help="Каталог виртуальной файловой системы")
    parser.add_argument("--startup", help="Путь к стартовому скрипту")
    args = parser.parse_args(argv)

    config_path = Path(args.config or "config.yaml").resolve()
    settings = {}
    if config_path.exists():
        settings = read_yaml(config_path)
    elif args.config:
        raise FileNotFoundError(f"Конфигурация не найдена: {config_path}")

    def get_path(command_value, key, default=None):
        """Выбрать путь из CLI или YAML и сделать его абсолютным."""
        value = command_value
        if value is None:
            value = settings.get(key, default)
        if value is None and key == "startup_script":
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Нужно указать непустой путь: {key}")
        base = Path.cwd() if command_value is not None else config_path.parent
        return (base / value).resolve()

    return {
        "config": config_path if config_path.exists() else None,
        "vfs": get_path(args.vfs, "vfs_path", "vfs/demo"),
        "startup": get_path(args.startup, "startup_script"),
    }
