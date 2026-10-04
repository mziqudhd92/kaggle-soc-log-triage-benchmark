# Task decorator name ↔ CLI push slug (must match exactly)

Project prefix: **`log-triage-`** (full product name, not a cryptic abbreviation).

| File | `@kbench.task(name=...)` / push slug |
| --- | --- |
| `tasks/01_log_triage_label.py` | `log-triage-label` |
| `tasks/02_log_triage_panic_trap.py` | `log-triage-panic-trap` |

Item helpers (`store_task=False`): `log-triage-label-item`, `log-triage-panic-item`.

```bash
kaggle b t push log-triage-label -f tasks/01_log_triage_label.py --wait
kaggle b t push log-triage-panic-trap -f tasks/02_log_triage_panic_trap.py --wait
```
