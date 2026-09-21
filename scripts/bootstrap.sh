#!/usr/bin/env bash
# Thin wrapper around scripts/bootstrap_kit.py (dup/ddown-friendly entrypoint).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "${ROOT}/scripts/bootstrap_kit.py" "$@"
