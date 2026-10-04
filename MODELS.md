# Locked Community Benchmark models (Log Triage)

Reuse the same locked ART matrix unless a slug disappears from
`kaggle b t models`. Prefer these bare canonical slugs:

| Slug | Tier | Role |
| --- | --- | --- |
| `gemini-3.5-flash` | flash | Primary fast Gemini |
| `gemini-3.7-flash` | flash | Second Gemini flash |
| `gemini-2.5-pro` | heavy | Does cost buy calmer triage? |
| `claude-haiku-4-5-20251001` | flash | Cheap Claude |
| `claude-sonnet-4-5-20250929` | mid | Strong Claude |
| `gemma-4-31b-it` | mid | Open-weights instruct |
| `gpt-5.4-nano-2026-03-17` | flash | Price floor |

```bash
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
