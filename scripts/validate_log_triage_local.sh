#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/validate_log_triage_jsonl.py
python3 scripts/test_log_triage_scoring.py
python3 -m py_compile tasks/01_log_triage_label.py tasks/02_log_triage_panic_trap.py
echo "validate_local OK"
