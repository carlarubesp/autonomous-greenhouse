#!/usr/bin/env bash
# Type-check each service from its own folder, the same way it runs.
set -euo pipefail

cd "$(dirname "$0")/.."
status=0

echo "mypy: common"
(cd common/src && uv run --frozen mypy -p greenhouse_common) && (cd common && uv run --frozen mypy tests) || status=1

for service in analyzer executor knowledge managed-resources monitor planner; do
    files=$(find "$service" -maxdepth 1 -name '*.py' ! -name '__init__.py' -printf '%f\n')
    echo "mypy: $service"
    (cd "$service" && uv run --frozen mypy $files) || status=1
done
exit $status
