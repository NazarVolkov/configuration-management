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
