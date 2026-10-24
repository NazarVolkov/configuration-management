"""Рекурсивный обход графа зависимостей: этап 3."""


def build_graph(root, get_dependencies):
    """Обойти зависимости в глубину, посещая каждый пакет один раз."""
    graph = {}

    def visit(package):
        """Записать узел до рекурсии, чтобы остановить цикл."""
        if package in graph:
            return
        graph[package] = list(dict.fromkeys(get_dependencies(package)))
        for dependency in graph[package]:
            visit(dependency)

    visit(root)
    return graph


def print_graph(graph):
    """Показать список смежности: пакет -> его прямые зависимости."""
    for package, dependencies in graph.items():
        print(f"{package} -> {', '.join(dependencies) or '-'}")


def reverse_dependencies(graph, package):
    """Развернуть рёбра и применить тот же DFS: этап 4."""
    if package not in graph:
        raise ValueError(f"Пакет не найден в загруженном графе: {package}")
    reversed_graph = {name: [] for name in graph}
    for name, dependencies in graph.items():
        for dependency in dependencies:
            reversed_graph[dependency].append(name)
    return build_graph(package, reversed_graph.__getitem__)
