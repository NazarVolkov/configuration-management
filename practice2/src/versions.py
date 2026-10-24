"""Выбор стабильной версии NuGet без сторонних библиотек: этап 2."""

import re


def version_key(value):
    """Превратить числовую версию в сравнимый кортеж из четырёх чисел."""
    if not re.fullmatch(r"\d+(\.\d+){0,3}", value):
        raise ValueError(f"Нужна стабильная числовая версия: {value}")
    numbers = [int(part) for part in value.split(".")]
    return tuple(numbers + [0] * (4 - len(numbers)))


def matches(version, requirement):
    """Проверить минимум, точную версию или интервал NuGet."""
    if not requirement:
        return True
    value = version_key(version)
    if requirement.startswith(("[", "(")):
        if not requirement.endswith(("]", ")")):
            raise ValueError(f"Неверный интервал: {requirement}")
        body = requirement[1:-1]
        if "," not in body:
            if requirement[0] != "[" or requirement[-1] != "]":
                raise ValueError(f"Неверная точная версия: {requirement}")
            return value == version_key(body.strip())
        lower, upper = [part.strip() for part in body.split(",")]
        lower_ok = not lower or value > version_key(lower)
        upper_ok = not upper or value < version_key(upper)
        if lower and requirement[0] == "[":
            lower_ok = value >= version_key(lower)
        if upper and requirement[-1] == "]":
            upper_ok = value <= version_key(upper)
        return lower_ok and upper_ok
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
