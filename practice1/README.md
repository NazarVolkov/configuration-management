# Практическая работа №1

Эмулятор командной оболочки на Python, вариант 5. Работает с виртуальной файловой системой, загруженной из каталога. Изменения хранятся в памяти до завершения программы.

## Запуск

Нужен Python 3. Из корня репозитория:

```powershell
cd practice1
python -m pip install -r requirements.txt
python src/main.py
```

Программа выполнит стартовый скрипт из конфигурации и откроет строку ввода команд.

## Команды и настройки

Поддерживаются `ls`, `cd`, `pwd`, `history`, `uptime`, `touch`, `mkdir` и `exit`.

В [config.yaml](config.yaml) задаются каталог VFS (`vfs_path`) и стартовый скрипт (`startup_script`). Параметры командной строки имеют приоритет:

```powershell
python src/main.py --vfs vfs/minimal --startup scripts/startup_stage2.txt
```

Примеры файловой системы находятся в `vfs/`, стартовые скрипты — в `scripts/`, исходный код — в `src/`.

## Проверка

Из папки `practice1`:

```powershell
python -m unittest discover -s tests
```
