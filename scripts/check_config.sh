#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
printf '%s\n' '=== Конфигурация из YAML ==='
./run.sh --startup scripts/startup_stage2.txt </dev/null
printf '%s\n' '=== Переопределение всех параметров ==='
./run.sh --config config.yaml --vfs vfs/demo \
  --startup scripts/startup_stage2.txt </dev/null
printf '%s\n' '=== Приоритет командной строки над YAML ==='
./run.sh --config config.yaml --vfs vfs/minimal \
  --startup scripts/startup_stage2.txt </dev/null
