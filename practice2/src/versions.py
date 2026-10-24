"""Выбор стабильной версии NuGet без сторонних библиотек: этап 2."""

import re


def version_key(value):
    """Превратить числовую версию в сравнимый кортеж из четырёх чисел."""
    if not re.fullmatch(r"\d+(\.\d+){0,3}", value):
        raise ValueError(f"Нужна стабильная числовая версия: {value}")
    numbers = [int(part) for part in value.split(".")]
    return tuple(numbers + [0] * (4 - len(numbers)))


def bound_matches(value, bound, inclusive, lower):
    """Проверить одну нижнюю или верхнюю границу диапазона."""
    if not bound:
        return True
    limit = version_key(bound)
    if lower:
        return value >= limit if inclusive else value > limit
    return value <= limit if inclusive else value < limit


def interval_matches(value, requirement):
    """Проверить включённые и исключённые границы интервала."""
    if not requirement.endswith(("]", ")")):
        raise ValueError(f"Неверный интервал: {requirement}")
    body = requirement[1:-1]
    if "," not in body:
        if requirement[0] != "[" or requirement[-1] != "]":
            raise ValueError(f"Неверная точная версия: {requirement}")
        return value == version_key(body.strip())
    lower, upper = [part.strip() for part in body.split(",")]
    lower_ok = bound_matches(value, lower, requirement[0] == "[", True)
    upper_ok = bound_matches(value, upper, requirement[-1] == "]", False)
    return lower_ok and upper_ok


def matches(version, requirement):
    """Проверить минимум, точную версию или интервал NuGet."""
    if not requirement:
        return True
    value = version_key(version)
    if requirement.startswith(("[", "(")):
        return interval_matches(value, requirement)
    return value >= version_key(requirement)


def choose_version(versions, requirement=None):
    """Взять последнюю стабильную для корня, минимальную для зависимости."""
    stable = [value for value in versions if "-" not in value]
    allowed = [value for value in stable if matches(value, requirement)]
    if not allowed:
        raise ValueError(f"Нет подходящей стабильной версии: {requirement}")
    if requirement is None:
        return max(allowed, key=version_key)
    return min(allowed, key=version_key)
