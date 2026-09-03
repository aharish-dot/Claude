#!/usr/bin/env bash
# Thin wrapper: the real loop lives in tools/ (same layout as the .ps1).
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../tools/run_next_case_loop.sh" "$@"
