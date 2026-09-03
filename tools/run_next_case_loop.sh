#!/usr/bin/env bash
# Unattended Supply Code loop (Linux/macOS). Same Python orchestrator as the
# Windows .ps1. Claim + finalize stay serial; authoring can run in parallel.
#
# Usage (from repo root):
#   ./tools/run_next_case_loop.sh --count 50 --workers 2
#   ./tools/run_next_case_loop.sh --dry-run --count 1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "python3 not found on PATH" >&2
  exit 1
fi

export PYTHONUTF8=1
exec "$PY" "$ROOT/tools/run_next_case_workers.py" --repo-root "$ROOT" "$@"
