#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
printf '\n%s\n' '=== Все команды, этап 5 ==='
./run.sh --vfs vfs/demo --startup scripts/startup_stage5.txt </dev/null
printf '\n%s\n' '=== Глубокая VFS ==='
printf 'pwd\nls\ncd level1\nls\ncd level2\nls\nexit\n' | \
  ./run.sh --vfs vfs/deep --startup scripts/startup_demo.txt
