#!/usr/bin/env python3
"""Embed dataset/items.jsonl into each task as a Python literal."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "dataset" / "items.jsonl"
BEGIN = "# === BEGIN EMBEDDED_ITEMS ==="
END = "# === END EMBEDDED_ITEMS ==="
PLACEHOLDER = "EMBEDDED_ITEMS = []  # replaced by scripts/embed_log_triage_items.py"

TASKS = [
    ROOT / "tasks" / "01_log_triage_label.py",
    ROOT / "tasks" / "02_log_triage_panic_trap.py",
]


def load_items() -> list[dict]:
    rows = []
    with ITEMS.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def block(items: list[dict]) -> str:
    return f"{BEGIN}\nEMBEDDED_ITEMS = {repr(items)}\n{END}"


def inject(path: Path, blob: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^import json\n", "", text, count=1)
    if BEGIN in text and END in text:
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        text = text[:start] + blob + text[end:]
    elif PLACEHOLDER in text:
        text = text.replace(PLACEHOLDER, blob, 1)
    else:
        raise SystemExit(f"no embed anchor in {path}")
    path.write_text(text, encoding="utf-8")
    print(f"embedded {len(load_items())} items -> {path.name}")


def main() -> None:
    blob = block(load_items())
    for path in TASKS:
        inject(path, blob)


if __name__ == "__main__":
    main()
