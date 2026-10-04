# Log Triage (LT)

AI models are often like over-eager SOC alarms. Show them a scary path in a log — `/wp-admin`, `AccessDenied`, `Failed password` — and they page “ATTACK!” Many cheaper models never ask whether it was a health check, a deploy mistake, or a truncated line that needs more data.

**LT** measures that gap. Models must label short synthetic log bundles as:

| Label | Meaning |
| --- | --- |
| `attack` | Malicious activity / compromise in progress |
| `misconfig` | Wrong setup/deploy; no clear active exploit |
| `noise` | Expected / benign background |
| `needs_more_data` | Interesting but incomplete — don’t guess |

**Headline metric — Panic Gap:** share of `noise`/`misconfig` items wrongly called `attack`. Zero means calm triage; high means alert fatigue.

Sibling project to [ART](../art-benchmark) (code patch-respect). Different subject: **operational log triage**, not code sinks.

## Dataset & scoring

8 minimal-pair log twins + 6 controls (web, auth, cloud, WAF, app). Prompts see **source hint + log only**; twin metadata is scoring-only.

```text
LT = 0.35 × (attack accuracy)
   + 0.25 × (misconfig accuracy)
   + 0.20 × (noise accuracy)
   + 0.20 × (needs_more_data accuracy)
```

**Panic Gap** = `(noise∪misconfig labeled attack) / (noise∪misconfig count)`

## Expensive new vs cheap flash/nano

Article figures (regenerate with `python scripts/make_log_triage_charts.py`):

![Cover](assets/cover_soc_log_triage.jpg)

![Expensive vs cheap LT scores](assets/expensive_vs_cheap_lt.png)

![Gap story: best expensive only +0.07 over best flash](assets/expensive_vs_cheap_gap.png)

![Panic calmness already matched by cheap models](assets/panic_cheap_vs_expensive.png)

![Takeaway board for the article](assets/expensive_vs_cheap_takeaway.png)

![Dataset composition](assets/dataset_composition.png)

![Twin method schematic](assets/twin_method_schematic.png)

![LT formula](assets/lt_formula.png)

![Scoring design](assets/scoring_design.png)

![Newest leaderboard](assets/newest_leaderboard.png)

![Evaluation pipeline](assets/pipeline_diagram.png)

## Core tasks

| Task | What it measures |
| --- | --- |
| `log-triage-label` | 4-way label accuracy → LT score |
| `log-triage-panic-trap` | On noise/misconfig only: “confirmed attack right now?” (gold = no) |

## Repository layout

```text
.
├── README.md
├── LICENSE
├── MODELS.md
├── TASK_SLUGS.md
├── dataset/items.jsonl
├── tasks/
├── scripts/
├── assets/
├── results/
└── dev/SUBMISSION_DRAFT.md
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install 'kaggle>=1.7' kaggle-benchmarks pandas
export KAGGLE_API_TOKEN=…   # https://www.kaggle.com/settings → API
kaggle b init -y --env-file .env
```

Rebuild / validate:

```bash
python scripts/build_log_triage_items.py
python scripts/embed_log_triage_items.py
bash scripts/validate_log_triage_local.sh
```

## Push / run

```bash
kaggle b t push log-triage-label -f tasks/01_log_triage_label.py --wait
kaggle b t push log-triage-panic-trap -f tasks/02_log_triage_panic_trap.py --wait

kaggle b t run log-triage-label \
  -m gemini-3.5-flash \
  -m gemini-2.5-pro \
  -m gemini-3.7-flash \
  -m claude-haiku-4-5-20251001 \
  -m claude-sonnet-4-5-20250929 \
  -m gemma-4-31b-it \
  -m gpt-5.4-nano-2026-03-17 \
  --wait
```

## Safety

Synthetic logs only; defensive research. No real customer telemetry.

## Credit

Repo: https://github.com/mziqudhd92/kaggle-soc-log-triage-benchmark

Companion methodology to [Attacker-Reachable Sink Triage (ART)](https://github.com/mziqudhd92/kaggle-art-benchmark); inspired by proof-over-speculation tooling ([Iridium](https://github.com/mziqudhd92/Iridium)). Standalone MIT project.
