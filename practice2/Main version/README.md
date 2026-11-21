# Анализатор зависимостей NuGet — C++

Основная версия практической работы №2 для Windows. Строит граф зависимостей NuGet, выполняет обратный поиск и сохраняет диаграммы в `output/`.

## Запуск

Нужны Visual Studio или Build Tools с компонентом «Разработка классических приложений на C++» и `curl.exe`. При первой сборке зависимости скачиваются из интернета.

Из корня репозитория:

```powershell
cd "practice2/Main version"
.\build.bat
.\run.bat --no-image
```

Стандартный [config.json](config.json) использует локальный тестовый граф. Команда выводит ASCII-дерево и сохраняет файл PlantUML.

Для PNG нужна Java, доступная через `PATH` или `JAVA_HOME`. Запуск без `--no-image` скачает PlantUML при первом использовании, создаст PNG и откроет его. Флаг `--no-open` отключает открытие изображения.

## Примеры

Из папки этой версии:

```powershell
.\run.bat --stage 3
.\run.bat --stage 4 --reverse D
.\run.bat examples/logging.json --no-image
```

Последний пример получает зависимости реального пакета через интернет. В `config.json` задаются пакет (`package`), источник (`repository`), тестовый режим (`test_mode`) и вывод дерева (`ascii_tree`).

## Проверка

В PowerShell из папки этой версии:

```powershell
.\tests\run.ps1
```
