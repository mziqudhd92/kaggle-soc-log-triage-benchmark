# Community Benchmark models (SOC Log Triage)

## Core matrix (v1)

| Slug | Tier | Role |
| --- | --- | --- |
| `gemini-3.5-flash` | flash | Primary fast Gemini |
| `gemini-3.7-flash` | flash | Second Gemini flash |
| `gemini-2.5-pro` | heavy | Does cost buy calmer triage? |
| `claude-haiku-4-5-20251001` | flash | Cheap Claude |
| `claude-sonnet-4-5-20250929` | mid | Strong Claude (often 429) |
| `gemma-4-31b-it` | mid | Open-weights instruct |
| `gpt-5.4-nano-2026-03-17` | flash | Price floor |

## Newest flagship cohort (primary ranking)

These are the models that matter for “is this good enough today?” — not the older locked set.

| Slug | Why |
| --- | --- |
| `claude-opus-5-default` | Newest Claude Opus line on catalog |
| `claude-sonnet-5-default` | Newest Claude Sonnet line |
| `claude-opus-4-8-default` | Latest Opus 4.x |
| `gpt-5.6-sol` / `gpt-5.6-luna` | GPT-5.6 variants |
| `gpt-6-astra` | GPT-6 line |
| `gemini-3.8-flash` | Newest Gemini flash on catalog |
| `gemini-3.1-pro-preview` | Newest Gemini pro preview |
| `grok-4.6` | Newest Grok on catalog |

Older slugs (Haiku 4.5, GPT nano, Gemini 2.5, etc.) are **baselines only**, not the verdict.

```bash
kaggle b t run log-triage-label \
  -m claude-opus-5-default \
  -m claude-sonnet-5-default \
  -m claude-opus-4-8-default \
  -m gpt-5.6-sol \
  -m gpt-5.6-luna \
  -m gpt-6-astra \
  -m gemini-3.8-flash \
  -m gemini-3.1-pro-preview \
  -m grok-4.6 \
  --wait
```
