# Changelog

## 2026-10-04 — v1 scaffold

- New sibling project under `kaggle/kaggle-soc-kaggle-soc-log-triage-benchmark` (separate from ART).
- Dataset: 8 minimal-pair log twins + 6 controls (web, auth, cloud, app).
- Core tasks: `log-triage-label` (LT score) and `log-triage-panic-trap` (attack overclaim).
- Task files use full project prefix: `01_log_triage_label.py`, `02_log_triage_panic_trap.py`.
- Headline metric **Panic Gap** = rate of labeling noise/misconfig as `attack`.
