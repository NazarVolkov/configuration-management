# Практическая работа 2. Вариант 5

C++17, Windows, Visual Studio 2022 / Build Tools с компонентом C++. Инструмент анализа зависимостей NuGet.
Этап 1: чтение JSON и вывод параметров в формате ключ-значение.

## Сборка и проверка

```powershell
.\build.bat
.\run.bat
powershell -NoProfile -ExecutionPolicy Bypass -File tests/run.ps1
```

При первой сборке нужен интернет для загрузки nlohmann/json в build/deps.
JSON-парсер разбирает только синтаксис. Ошибки выводятся с префиксом Error.

## Настройки

Обязательные поля config.json: package, repository, test_mode, ascii_tree.
package - имя NuGet или заглавные латинские буквы в тестовом режиме.
repository - URL NuGet V3 либо путь к JSON относительно файла конфигурации.
test_mode и ascii_tree - логические значения.
Необязательные version и framework задают точную стабильную версию и группу
платформы; по умолчанию выбираются последняя стабильная версия и net8.0.

## Функции

config.cpp: valid_name, valid_url проверяют имена и URL; field читает
обязательное поле; check_source проверяет источник; load_settings читает
и проверяет настройки; print_settings выводит их.
versions.cpp: stable_version проверяет формат числовой версии.
main.cpp: wmain обрабатывает путь к конфигурации и ошибки.

Исходники находятся в src, тесты - в tests. build и output исключены
из Git. Коммиты этапов используют Conventional Commits.

## Этап 2: прямые зависимости

```powershell
.\run.bat examples/logging.json --stage 2
```

Nuget::root выбирает версию пакета, Nuget::versions загружает список версий,
Nuget::dependencies читает зависимости из nuspec. package_base находит
PackageBaseAddress в индексе NuGet V3, lower_name нормализует регистр.
read_dependencies читает XML, select_group выбирает группу платформы.
choose_version выбирает подходящую стабильную версию; parse_range,
parse_interval, matches, key, compact, valid_bound разбирают и проверяют
границы. download выполняет HTTP GET, check и body проверяют ответ.
TinyXML-2 разбирает только XML. Готовые средства получения зависимостей
и менеджеры пакетов при анализе не вызываются.

## Этап 3: рекурсивный DFS

```powershell
.\run.bat --stage 1
.\run.bat --stage 3
```

Тестовый JSON содержит словарь «пакет: массив зависимостей». Все ссылки
должны быть описаны; имена состоят из заглавных латинских букв.
load_test_graph читает репозиторий, check_links проверяет его связи.
build_graph запускает рекурсивную visit. Узел добавляется до перехода
к детям, поэтому цикл завершается и все рёбра сохраняются.
print_graph выводит строки вида A -> B C. Прочерк обозначает отсутствие
зависимостей. Тесты включают ветвление, общую зависимость, цикл,
петлю, отдельный узел и ссылку на отсутствующий пакет.

## Этап 4: обратные зависимости

```powershell
.\run.bat --stage 4 --reverse D
.\run.bat --stage 4 --reverse E
.\run.bat --stage 4 --reverse G
```

reverse_graph разворачивает все рёбра и вызывает тот же build_graph/visit.
Цель --reverse выбирается отдельно от корня, без опции используется корень.
В тестовом режиме рассматривается весь JSON, включая входящие связи от
пакетов вне подграфа корня. В реальном режиме рассматривается построенный
граф корня: поиск всех потребителей во всём NuGet не выполняется.
Этапы выбираются через --stage; --reverse разрешён только на этапе 4.
