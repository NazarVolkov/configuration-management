"""Чтение и проверка JSON-настроек: этап 1."""

import json
import re
from pathlib import Path
from urllib.parse import urlparse


def check_source(settings, base):
    """Проверить имя пакета и источник данных."""
    package = settings["package"]
    pattern = r"[A-Z]+" if settings["test_mode"] else r"[\w.-]+"
    if not isinstance(package, str) or not re.fullmatch(pattern, package):
        raise ValueError("Неверное имя package")
    source = settings["repository"]
    if not isinstance(source, str) or not source.strip():
        raise ValueError("repository должен быть непустой строкой")
    if settings["test_mode"]:
        path = (base / source).resolve()
        if not path.is_file():
            raise ValueError(f"Тестовый репозиторий не найден: {path}")
        settings["repository"] = str(path)
    else:
        url = urlparse(source)
        if url.scheme not in ("http", "https") or not url.netloc:
            raise ValueError("repository должен быть URL HTTP или HTTPS")


def load_config(filename):
    """Прочитать обязательные параметры и проверить их типы."""
    path = Path(filename).resolve()
    settings = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(settings, dict):
        raise ValueError("Конфигурация должна быть JSON-объектом")
    for key in ("package", "repository", "test_mode", "ascii_tree"):
        if key not in settings:
            raise ValueError(f"Не указан параметр {key}")
    for key in ("test_mode", "ascii_tree"):
        if not isinstance(settings[key], bool):
            raise ValueError(f"{key} должен быть true или false")
    settings.setdefault("framework", "net8.0")
    settings.setdefault("version", None)
    if not isinstance(settings["framework"], str) or not settings["framework"]:
        raise ValueError("framework должен быть непустой строкой")
    version = settings["version"]
    if version is not None and not isinstance(version, str):
        raise ValueError("version должен быть строкой или null")
    check_source(settings, path.parent)
    return settings
