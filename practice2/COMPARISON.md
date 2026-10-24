# Сравнение со штатным NuGet

Проверено 24.10.2026 с .NET SDK 8.0.426 для платформы net8.0.
Для каждого корня закреплена версия 8.0.0.

Собственный анализатор получил данные через HTTP и XML стандартной
библиотекой Python. Отдельные проекты из `comparison/` восстановлены
штатным NuGet, после чего выполнен `dotnet list package --include-transitive`.
Наборы идентификаторов и версий совпали для всех трёх примеров.

| Корневой пакет | Вершины с корнем | Рёбра | Сравнение пакетов и версий |
| --- | --- | --- | --- |
| Microsoft.Extensions.Logging | 6 | 7 | Совпали |
| Microsoft.Extensions.Options | 3 | 2 | Совпали |
| Microsoft.Extensions.DependencyInjection | 2 | 1 | Совпали |

У Logging получены DependencyInjection, DependencyInjection.Abstractions,
Logging.Abstractions, Options и Primitives. У Options —
DependencyInjection.Abstractions и Primitives. У DependencyInjection —
DependencyInjection.Abstractions. У всех перечисленных пакетов версия 8.0.0,
полный префикс имени — Microsoft.Extensions.

## Повторить сравнение

Нужен .NET SDK 8 или новее; для обычной работы анализатора он не нужен.
Из папки `practice2`:

```powershell
.\scripts\compare.bat
.\run.bat examples/nuget.json --no-image
.\run.bat examples/options.json --no-image
.\run.bat examples/injection.json --no-image
```

Каждый проект содержит одну ссылку PackageReference. Скрипт вызывает
`dotnet restore`, затем штатный вывод прямых и транзитивных пакетов.
`obj/project.assets.json` содержит рёбра восстановленного графа.
Файлы obj и bin исключены из Git.

## Различия представления

CLI .NET выводит плоский список, а наша программа — дерево и граф.
Общие зависимости в дереве помечены `[shown]`, в PlantUML у них один узел.
Стрелка направлена от пакета к его зависимости. Для выбранных примеров
расхождений в составе пакетов и версиях не обнаружено.

На других пакетах результаты могут отличаться: учебная программа выбирает
версии для каждого ребра отдельно и не воспроизводит разрешение конфликтов
NuGet Restore. Также используется точная группа платформы из nuspec,
без автоматического выбора совместимой. Сравнивать следует одинаковые
версии корня и одинаковую целевую платформу.

Средства .NET используются только для этой независимой проверки,
не для получения зависимостей внутри анализатора.

[Документация штатной команды](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-package-list)
