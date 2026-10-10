# Конфигурационное управление — вариант №5

Учебный эмулятор командной строки UNIX-подобной ОС на Python.

## Этапы 1–4

1. REPL в консоли, имя VFS в приглашении, парсер по пробелам,
   заглушки `ls`, `cd` и команда `exit`.
2. YAML-конфигурация и параметры `--config`, `--vfs`, `--startup`,
   приоритет аргументов CLI, стартовые скрипты с комментариями.
3. Чтение каталога VFS целиком в память (без изменения диска),
   тесты для минимальной, обычной и глубокой структуры папок.
4. Рабочие команды `ls`, `cd`, `history`, `uptime`, `pwd`.
   `uptime` показывает приблизительное время работы ОС по
   монотонным часам, `history` — историю команд этого сеанса.

## Запуск и тесты

```sh
python3 -m pip install -r requirements.txt
./run.sh
./scripts/check_config.sh
./scripts/check_vfs.sh
./run.sh --startup scripts/startup_stage4.txt </dev/null
python3 -m unittest discover -s tests -v
```
