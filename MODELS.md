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

## Popular comparison set (added for broader recognition)

| Slug | Why |
| --- | --- |
| `gpt-5.4-2026-03-05` | Flagship GPT-5.4 |
| `gpt-5.4-mini-2026-03-17` | Popular mid GPT |
| `gpt-5.5-2026-04-23` | Newer GPT flagship |
| `claude-sonnet-4-6-default` | Current popular Sonnet |
| `claude-opus-4-6-default` | Flagship Claude |
| `gemini-2.5-flash` | Widely used Gemini flash |
| `deepseek-r1-0528` | Popular reasoning model |
| `qwen3-next-80b-a3b-instruct` | Popular Qwen instruct |

```bash
# Popular comparison cohort
kaggle b t run log-triage-label \
  -m gpt-5.4-2026-03-05 \
  -m gpt-5.4-mini-2026-03-17 \
  -m gpt-5.5-2026-04-23 \
  -m claude-sonnet-4-6-default \
  -m claude-opus-4-6-default \
  -m gemini-2.5-flash \
  -m deepseek-r1-0528 \
  -m qwen3-next-80b-a3b-instruct \
  --wait
```
