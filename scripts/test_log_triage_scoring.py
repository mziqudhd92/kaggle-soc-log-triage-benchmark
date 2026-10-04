#!/usr/bin/env python3
"""Offline checks for LT score + Panic Gap (no Kaggle network)."""

from __future__ import annotations

import functools
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "01_log_triage_label.py"


def _load():
    kbench = types.ModuleType("kaggle_benchmarks")

    class _Task:
        def __init__(self, fn):
            self._fn = fn
            functools.update_wrapper(self, fn)

        def __call__(self, *a, **k):
            return self._fn(*a, **k)

        def run(self, *a, **k):
            return None

        def evaluate(self, *a, **k):
            raise RuntimeError("evaluate not available in unit test stub")

    def task(**_kwargs):
        def deco(fn):
            return _Task(fn)

        return deco

    kbench.task = task
    kbench.llm = None
    sys.modules["kaggle_benchmarks"] = kbench
    # Real pandas is fine if installed; else minimal stub unused by score fns.
    try:
        import pandas  # noqa: F401
    except ImportError:
        sys.modules["pandas"] = types.ModuleType("pandas")

    spec = importlib.util.spec_from_file_location("lt_label", TASK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = _load()
    items = mod.load_items()
    assert len(items) >= 20, len(items)

    hits = {i: True for i in range(len(items))}
    perfect = mod.compute_log_triage_score(items, hits)
    assert abs(perfect - 1.0) < 1e-9, perfect

    zero = mod.compute_log_triage_score(items, {})
    assert abs(zero - 0.0) < 1e-9, zero

    panic_items = [
        row for row in items if row["gold_label"] in ("noise", "misconfig")
    ]
    assert panic_items
    gap = mod.compute_panic_gap(
        [r["gold_label"] for r in panic_items],
        ["attack"] * len(panic_items),
    )
    assert abs(gap - 1.0) < 1e-9, gap

    calm = mod.compute_panic_gap(
        [r["gold_label"] for r in panic_items],
        [r["gold_label"] for r in panic_items],
    )
    assert abs(calm - 0.0) < 1e-9, calm

    hits_one_miss = {i: True for i in range(len(items))}
    hits_one_miss[0] = False
    scored = mod.compute_log_triage_score(items, hits_one_miss)
    assert 0.0 <= scored < 1.0, scored

    print(
        f"OK scoring alignment items={len(items)} perfect={perfect} "
        f"one_miss={scored:.4f} panic_all={gap} panic_none={calm}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
