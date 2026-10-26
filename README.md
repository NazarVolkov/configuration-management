# Конфигурационное управление, вариант 5

| Работа | Описание | Инструкция |
| --- | --- | --- |
| 1 | Эмулятор оболочки UNIX с файловой системой в памяти | [practice1](practice1/README.md) |
| 2 | Визуализатор зависимостей NuGet, DFS и PlantUML | [practice2](practice2/README.md) |

## Запуск из корня репозитория

Для первой работы нужны Python 3.9+ и PyYAML:

```powershell
python -m pip install -r practice1/requirements.txt
.\practice1\run.bat
```

Для второй работы нужен Python 3.9+, для изображения также Java 17+:

```powershell
.\practice2\run.bat
```

Без построения изображения и обращения к сети:

```powershell
.\practice2\run.bat --no-image
```

При первом построении изображения вторая работа загружает PlantUML.
Исходный код, настройки, примеры и инструкции находятся внутри папки
каждой работы. В истории Git сохранены этапы их разработки.

## Проверка

```powershell
python -B -m unittest discover -s practice1/tests -v
python -B -m unittest discover -s practice2/tests -v
```

Ранее загруженные дополнительные практики перенесены вместе с первой работой:
[командная строка](practice1/pract1.md) и [менеджеры пакетов](practice1/pract2.md).
