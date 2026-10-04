# Newest-model comparison (primary verdict) — 2026-10-04

Older baselines are **not** the claim. Ranking for “is this good enough today?” uses the newest catalog flagships.

## Newest cohort — label + panic

| Model | LT | Panic (calm) | Status |
| --- | ---: | ---: | --- |
| `claude-sonnet-5-default` | **0.961** | **1.000** | OK |
| `gpt-5.6-luna` | **0.961** | **1.000** | OK |
| `gemini-3.1-pro-preview` | 0.894 | 1.000 | OK |
| `gemini-3.8-flash` | 0.894 | 1.000 | OK |
| `gpt-5.6-sol` | 0.793 | 1.000 | OK |
| `claude-opus-4-8-default` | 0.391 | — | Label weak / panic not run (quota family) |
| `claude-opus-5-default` | 0.000 | 1.000 | Label failed or unusable; panic OK |
| `gpt-6-astra` | 0.000 | — | ERRORED |
| `grok-4.6` | 0.000 | — | ERRORED |

## Verdict (newest only)

On this probe, **Claude Sonnet 5** and **GPT-5.6 Luna** are the top usable newest models (LT ≈ 0.96, panic perfect). Newest Gemini flash/pro sit just behind (~0.89). Opus 5 / GPT-6 / Grok did not produce usable label scores in this run (infra or total miss).
