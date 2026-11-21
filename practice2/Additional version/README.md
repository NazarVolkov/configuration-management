# Анализатор зависимостей NuGet — Python

Дополнительная версия практической работы №2. Строит граф зависимостей NuGet, выполняет обратный поиск и сохраняет диаграммы в `output/`.

## Запуск

Нужен Python 3. Используется стандартная библиотека, установка пакетов через pip не требуется.

Из корня репозитория:

```powershell
cd "practice2/Additional version"
python src/main.py --no-image
```

Стандартный [config.json](config.json) использует локальный тестовый граф. Команда выводит ASCII-дерево и сохраняет файл PlantUML.

Для SVG нужна Java в `PATH`. Запуск без `--no-image` скачает PlantUML при первом использовании, создаст SVG и откроет его в браузере. Флаг `--no-open` отключает открытие изображения.

## Примеры

Из папки этой версии:

```powershell
python src/main.py --stage 3
python src/main.py --stage 4 --reverse D
python src/main.py examples/nuget.json --no-image
```

Последний пример получает зависимости реального пакета через интернет. В `config.json` задаются пакет (`package`), источник (`repository`), тестовый режим (`test_mode`) и вывод дерева (`ascii_tree`).

## Проверка

Из папки этой версии:

```powershell
python -m unittest discover -s tests
```

Сравнение со штатным NuGet описано в [COMPARISON.md](COMPARISON.md).
