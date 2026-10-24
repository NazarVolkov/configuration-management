"""Чтение NuGet V3 и XML-манифестов через стандартную библиотеку: этап 2."""

import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen

from versions import choose_version


def download(url):
    """Загрузить текстовый ресурс с ограничением времени ожидания."""
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8-sig")


def manifest_dependencies(text, framework):
    """Прочитать зависимости только для явно выбранной платформы."""
    root = ET.fromstring(text)
    dependencies = root.find(".//{*}dependencies")
    if dependencies is None:
        return []
    groups = dependencies.findall("{*}group")
    if groups:
        selected = [group for group in groups if
                    group.get("targetFramework", "").lower() ==
                    framework.lower()]
        if not selected:
            selected = [group for group in groups if
                        not group.get("targetFramework")]
        if not selected:
            raise ValueError(f"В nuspec нет группы платформы {framework}")
        dependencies = selected[0]
    return [
        (item.attrib["id"].lower(), item.get("version", ""))
        for item in dependencies.findall("{*}dependency")
    ]


class NuGetRepository:
    """Самостоятельно получать список версий и читать nuspec пакетов."""

    def __init__(self, source, framework="net8.0"):
        """Найти адрес хранилища пакетов в индексе NuGet V3."""
        index = json.loads(download(source))
        if not isinstance(index, dict):
            raise ValueError("Индекс NuGet должен быть JSON-объектом")
        addresses = [item["@id"] for item in index.get("resources", [])
                     if item.get("@type") == "PackageBaseAddress/3.0.0"]
        if not addresses:
            raise ValueError("В индексе нет PackageBaseAddress/3.0.0")
        self.base = addresses[0].rstrip("/")
        self.framework = framework
        self.versions = {}

    def node(self, package, requirement=None):
        """Выбрать версию и вернуть имя узла package@version."""
        package = package.lower()
        if package not in self.versions:
            url = f"{self.base}/{package}/index.json"
            self.versions[package] = json.loads(download(url))["versions"]
        version = choose_version(self.versions[package], requirement)
        return f"{package}@{version}"

    def root(self, package, version=None):
        """Найти корневой пакет с заданной или последней версией."""
        requirement = f"[{version}]" if version else None
        return self.node(package, requirement)

    def dependencies(self, node):
        """Загрузить XML и получить прямые зависимости выбранной версии."""
        package, version = node.rsplit("@", 1)
        url = f"{self.base}/{package}/{version}/{package}.nuspec"
        items = manifest_dependencies(download(url), self.framework)
        return [self.node(name, requirement) for name, requirement in items]
