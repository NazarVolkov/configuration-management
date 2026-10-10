#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for layout in minimal few deep; do
    printf '\n=== VFS: %s ===\n' "$layout"
    ./run.sh --vfs "vfs/$layout" \
        --startup scripts/startup_stage3.txt </dev/null
done
