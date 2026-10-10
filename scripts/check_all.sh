#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
./scripts/check_config.sh
./scripts/check_vfs.sh
./scripts/check_commands.sh
