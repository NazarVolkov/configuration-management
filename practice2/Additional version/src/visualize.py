"""ASCII-дерево и диаграмма PlantUML: этап 5."""

import json
import subprocess
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen


PLANTUML_VERSION = "1.2026.9"
PLANTUML_URL = (
    "https://github.com/plantuml/plantuml/releases/download/"
    f"v{PLANTUML_VERSION}/plantuml.jar"
)


def ascii_tree(graph, root):
    """Показать дерево, отметив циклы и уже раскрытые общие зависимости."""
    lines = [root]
    seen = {root}

    def visit(package, prefix, ancestors):
        """Добавить строки потомков с отступами и соединителями."""
        children = graph[package]
        for index, child in enumerate(children):
            last = index == len(children) - 1
            branch = "`-- " if last else "+-- "
            mark = ""
            if child in ancestors:
                mark = " [cycle]"
            elif child in seen:
                mark = " [shown]"
            lines.append(prefix + branch + child + mark)
            if not mark:
                seen.add(child)
                gap = "    " if last else "|   "
                visit(child, prefix + gap, ancestors | {child})

    visit(root, "", {root})
    return "\n".join(lines)


def plantuml(graph):
    """Создать текст диаграммы с отдельными именами узлов и подписями."""
    lines = ["@startuml", "!pragma layout smetana", "left to right direction",
             "skinparam componentStyle rectangle"]
    ids = {name: f"N{index}" for index, name in enumerate(graph)}
    for name, alias in ids.items():
        lines.append(f"component {json.dumps(name)} as {alias}")
    for name, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"{ids[name]} --> {ids[dependency]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def get_plantuml(output):
    """Один раз скачать официальный PlantUML в исключённую из Git папку."""
    jar = output / f"plantuml-{PLANTUML_VERSION}.jar"
    if not jar.exists():
        print("Первый запуск: загрузка PlantUML...")
        with urlopen(PLANTUML_URL, timeout=60) as response:
            jar.write_bytes(response.read())
    return jar


def render_svg(text, destination):
    """Локально построить SVG через Java; Graphviz не нужен."""
    jar = get_plantuml(destination.parent)
    command = ["java", "-Djava.awt.headless=true", "-jar", str(jar),
               "-tsvg", "-pipe"]
    try:
        result = subprocess.run(command, input=text.encode("utf-8"),
                                capture_output=True, timeout=60)
    except subprocess.TimeoutExpired as error:
        raise ValueError("PlantUML не завершился за 60 секунд") from error
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace")
        raise ValueError(f"Ошибка PlantUML: {message}")
    if ET.fromstring(result.stdout).tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("PlantUML вернул не SVG-изображение")
    destination.write_bytes(result.stdout)


def save_diagram(graph, root, output, open_image=True, render=True):
    """Сохранить PlantUML и SVG; при обычном запуске показать изображение."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    name = root.replace("@", "_")
    text = plantuml(graph)
    source = output / f"{name}.puml"
    source.write_text(text, encoding="utf-8")
    print(f"PlantUML: {source}")
    if render:
        image = output / f"{name}.svg"
        render_svg(text, image)
        print(f"Изображение: {image}")
        if open_image:
            webbrowser.open(image.resolve().as_uri())
