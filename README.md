# Конфигурационное управление — вариант №5

Учебный эмулятор командной строки UNIX-подобной ОС на Python.

## Этапы 1–2

Консольный REPL, имя виртуальной файловой системы в приглашении,
парсер с разделением по пробелам, заглушки `ls`, `cd` и команда `exit`.

Конфигурация задаётся в `config.yaml`, либо через `--config`, `--vfs`,
`--startup`. Параметры командной строки имеют приоритет над YAML.
Стартовый скрипт поддерживает строки-комментарии с `#`.

## Запуск и тесты

```sh
python3 -m pip install -r requirements.txt
./run.sh
./run.sh --config config.yaml --vfs vfs/demo
./scripts/check_config.sh
python3 -m unittest discover -s tests -v
```
