# Popular-model comparison (2026-10-04)

Added widely recognized models beyond the v1 matrix.

## Label triage (LT score)

| Model | LT | Notes |
| --- | ---: | --- |
| `claude-opus-4-6-default` | 0.921 | Run reported quota 403 — treat as provisional |
| `gemini-3.7-flash` | 0.894 | v1 |
| `gemini-2.5-pro` | 0.867 | v1 |
| `claude-haiku-4-5-20251001` | 0.827 | v1 |
| `gemini-3.5-flash` / `gemma-4-31b-it` | 0.778 | v1 |
| `gemini-2.5-flash` / `gpt-5.4-nano` | 0.748 | |
| `gpt-5.4-mini-2026-03-17` | 0.581 | popular mid |
| `gpt-5.5-2026-04-23` | 0.571 | popular flagship |
| `claude-sonnet-4-6-default` | 0.530 | popular Sonnet |
| `deepseek-r1-0528` | 0.106 | completed but weak / parse issues likely |
| `gpt-5.4-2026-03-05` | 0.039 | completed but near-floor — investigate transcripts |
| `claude-sonnet-4-5-20250929` | — | 429 |
| `qwen3-next-80b-a3b-instruct` | — | 503 unreachable |

## Panic trap (fraction not over-calling attack)

Most GPT/Gemini models that finished: **1.000**. Haiku 0.900. Gemini 2.5 Flash 0.800. Sonnet-4.6 / DeepSeek / Sonnet-4.5 panic runs ERRORED (0.0).

## Takeaway

Popular flagships are **not** automatically better at calm log triage on this probe. Fast Gemini / Gemma still look strong; several big-name GPT/Claude scores need transcript review before ranking claims.
