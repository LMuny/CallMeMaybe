#!/usr/bin/env bash
# Usage: ./moul.sh [public|private] [--no-run]
#   public|private : exercise set (default: public)
#   --no-run       : skip your program, only grade the existing output
#
# Env overrides:
#   MOULINETTE_DIR : path to the moulinette project (folder with pyproject.toml)
#   RUN_CMD        : command that runs your program (default: make run if it exists, else uv run python -m src.main)
set -euo pipefail

SET="${1:-public}"
NO_RUN="${2:-}"
if [[ -z "${RUN_CMD:-}" ]]; then
    if [[ -f Makefile ]] && grep -q '^run:' Makefile; then
        RUN_CMD="make run"
    else
        RUN_CMD="uv run python -m src.main"
    fi
fi
OUT="data/output/function_calls.json"

if [[ "$SET" != "public" && "$SET" != "private" ]]; then
    echo "Invalid set '$SET' (public or private)" >&2
    exit 1
fi

# Locate the moulinette
MOUL="${MOULINETTE_DIR:-}"
if [[ -z "$MOUL" ]]; then
    for d in ./moulinette ../moulinette; do
        if [[ -f "$d/pyproject.toml" ]]; then MOUL="$d"; break; fi
    done
fi

if [[ -n "$MOUL" ]]; then
    MOUL_CMD=(uv run --project "$MOUL" python -m moulinette)
else
    MOUL_CMD=(uv run python -m moulinette)   # package copied into your project
fi

echo "==> [1/3] Preparing $SET exercises"
"${MOUL_CMD[@]}" prepare_exercises --set="$SET"

if [[ "$NO_RUN" != "--no-run" ]]; then
    echo "==> [2/3] Running your program"
    mkdir -p data/output
    rm -f "$OUT"   # never grade a stale file
    time $RUN_CMD
fi

if [[ ! -f "$OUT" ]]; then
    echo "Missing $OUT: your program did not produce it" >&2
    exit 1
fi

echo "==> [3/3] Grading ($SET)"
"${MOUL_CMD[@]}" grade_student_answers "$OUT" --set="$SET"
