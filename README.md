# Конфигурационное управление, вариант 5

| Работа | Описание | Инструкция |
| --- | --- | --- |
| 1 | Эмулятор оболочки UNIX | [practice1](practice1/README.md) |
| 2, Main version | Основная версия на C++17 | [C++](practice2/Main%20version/README.md) |
| 2, Additional version | Дополнительная версия на Python | [Python](practice2/Additional%20version/README.md) |

## Запуск из корня репозитория

Первая работа: Python 3.9+ и PyYAML.

```powershell
python -m pip install -r practice1/requirements.txt
.\practice1\run.bat
```

Вторая работа, основная версия: Windows, Visual Studio 2022 / Build Tools
с компонентом C++ и Windows SDK. Для изображения нужна Java 8+.

```powershell
& ".\practice2\Main version\build.bat"
& ".\practice2\Main version\run.bat"
```

Вторая работа, дополнительная версия: Python 3.9+; для изображения Java 17+.

```powershell
& ".\practice2\Additional version\run.bat"
```

Для запуска без изображения добавьте --no-image. Настройки, исходники,
тесты и примеры находятся в папке соответствующей версии.

## Проверка

```powershell
python -B -m unittest discover -s practice1/tests -v
python -B -m unittest discover -s "practice2/Additional version/tests" -v
powershell -NoProfile -ExecutionPolicy Bypass -File "practice2/Main version/tests/run.ps1"
```

Этапы разработки обеих реализаций сохранены в истории Git.
Дополнительные практики: [командная строка](practice1/pract1.md)
и [менеджеры пакетов](practice1/pract2.md).
