#!/usr/bin/env python3
"""Validate dataset/items.jsonl schema, twins, and no label leakage in logs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dataset" / "items.jsonl"
LABELS = {"attack", "misconfig", "noise", "needs_more_data"}
LEAK_TOKENS = (
    "gold_label",
    "this is an attack",
    "label: attack",
    "label: misconfig",
    "label: noise",
    "needs_more_data",
    "PANIC",
    "TRUE POSITIVE",
    "FALSE POSITIVE",
)


def main() -> int:
    if not PATH.is_file():
        print(f"MISSING {PATH}", file=sys.stderr)
        return 1

    errors: list[str] = []
    twin_roles: dict[str, set[str]] = {}
    counts = {label: 0 for label in LABELS}
    n = 0

    with PATH.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            raw = line.rstrip("\n")
            if not raw.strip():
                errors.append(f"L{lineno}: empty line")
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"L{lineno}: json error {exc}")
                continue
            n += 1
            log = obj.get("log")
            if not isinstance(log, str) or not log.strip():
                errors.append(f"L{lineno}: log must be non-empty str")
                continue
            nlines = len(log.strip("\n").splitlines())
            if nlines < 1 or nlines > 40:
                errors.append(f"L{lineno}: log lines={nlines} not in 1..40")
            gold = obj.get("gold_label")
            if gold not in LABELS:
                errors.append(f"L{lineno}: bad gold_label {gold!r}")
            else:
                counts[gold] += 1
            low = log.lower()
            for token in LEAK_TOKENS:
                if token.lower() in low:
                    errors.append(f"L{lineno}: leak token {token!r} in log")
            tid = obj.get("twin_id")
            role = obj.get("twin_role")
            if tid:
                twin_roles.setdefault(str(tid), set()).add(str(role))
                if role != gold:
                    errors.append(
                        f"L{lineno}: twin_role {role!r} != gold_label {gold!r}"
                    )
            for key in ("id", "source", "log_class", "rationale"):
                if not obj.get(key):
                    errors.append(f"L{lineno}: missing {key}")

    for tid, roles in twin_roles.items():
        if len(roles) != 2:
            errors.append(f"twin {tid}: expected 2 roles, got {sorted(roles)}")

    for label in LABELS:
        if counts[label] < 2:
            errors.append(f"label {label}: count={counts[label]} < 2")

    if errors:
        print("FAIL", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(
        f"OK items={n} twins={len(twin_roles)} "
        + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
