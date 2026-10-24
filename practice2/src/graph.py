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
