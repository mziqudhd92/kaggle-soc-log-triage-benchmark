---
title: "Paying for Opus won't calm your SOC queue: expensive models vs flash/nano on log triage"
published: false
tags: kagglechallenge, ai, security, machinelearning, soc
cover_image: ../assets/expensive_vs_cheap_takeaway.png
---

*This is a research / Kaggle Benchmarks write-up for **SOC Log Triage (LT)**.*

<!-- Publish checklist:
  1. Upload assets/*.png to DEV CDN; replace ../assets/ paths.
  2. Attach cover (expensive_vs_cheap_takeaway.png or expensive_vs_cheap_lt.png).
  3. Add live Kaggle collection URL under My Benchmark.
  4. Set published: true when ready.
-->

## Abstract

Security teams do not need another model that spots the word `Attack`. They need a model that can look at a messy log line and decide: **real attack**, **broken config**, **benign noise**, or **not enough evidence yet**.

We built **SOC Log Triage (LT)** — a small, leak-free Kaggle Community Benchmark with **8 log twin pairs + 6 controls**. We asked the product question that money actually cares about:

> Do expensive new models beat cheap flash/nano models for SOC first-pass analysis?

**Result:** the best expensive models (Claude Sonnet 5, GPT-5.6 Luna) score about **+0.07 LT** above the best Gemini flash. Several costly models score *worse* than nano/flash. On false-alarm calmness, cheap models already match the expensive ones.

![Takeaway: expensive new vs cheap flash/nano](../assets/expensive_vs_cheap_takeaway.png)

---

## 1. The problem

A junior SOC analyst’s night looks like this:

- 40,000 `/wp-admin` 404s from the internet  
- `AccessDenied` after a deploy  
- one truncated `POST /api/transfer` with no status code  
- a health-check 200 from kube-probe  

If you paste those into an LLM and ask “is this an attack?”, many models panic. That is alert fatigue with a chatbot face.

Public LLM leaderboards rarely measure this. Coding benchmarks ask “did you find a bug?” Chat benchmarks ask “are you helpful?” Neither asks: **did you stay calm when the scary token was noise?**

---

## 2. Research question

**RQ1.** Can frontier LLMs separate `attack` / `misconfig` / `noise` / `needs_more_data` on short synthetic log bundles?

**RQ2.** Do *expensive newest* models outperform *cheap flash/nano* models on that task?

We care about RQ2 because SOC pipelines are cost-sensitive. If Gemini Flash is within a few points of Sonnet 5, the business decision is obvious.

---

## 3. Method

### 3.1 Benchmark design

**SOC Log Triage (LT)** reuses the twin discipline from our earlier ART (code patch-respect) work, but on **logs**, not code:

| Piece | Design |
| --- | --- |
| Unit | Short synthetic log bundle (web, auth, cloud, WAF, app) |
| Labels | `attack`, `misconfig`, `noise`, `needs_more_data` |
| Twins | Same shape; **one observation flips** gold label |
| Prompt | Source hint + log only (no gold, no rationale) |
| N | 8 twin pairs + 6 controls (22 items) |

**Why synthetic?** No customer data. No memorized incident write-ups. Each twin differs by one control fact — the same “minimal pair” idea as ART.

### 3.2 Scoring

```text
LT = 0.35×(attack acc) + 0.25×(misconfig acc)
   + 0.20×(noise acc)  + 0.20×(needs_more_data acc)
```

**Panic-trap** (second task): on noise/misconfig items only, ask “is there a *confirmed* attack right now?” Gold = **no**. Score = fraction answered no.

### 3.3 Proof example (twin)

Same scary paths. Different story.

**Attack twin** — many external IPs probing exploit paths:

```text
203.0.113.44  GET /wp-login.php 404
198.51.100.17 GET /xmlrpc.php 404
203.0.113.88  GET /.env 404
203.0.113.12  GET .../eval-stdin.php 404
```

**Noise twin** — same paths from allowlisted CI scanner UA:

```text
34.102.136.180 GET /wp-login.php 404  "IridiumCI/1.0"
34.102.136.180 GET /xmlrpc.php 404    "IridiumCI/1.0"
# allowlisted CI egress for nightly surface scan
```

A model that labels both `attack` is not a better detector — it is a worse **context reader**.

Other twins cover: IAM deploy vs exfil, truncated API vs sqlmap, SSH background vs compromise chain, app 500 after deploy vs SQLi errors, WAF zgrab vs account takeover, S3 public-read vs payroll theft, incomplete VPN vs MFA-bypass + lateral movement.

### 3.4 Models

**Primary cohort (newest flagships):** Claude Opus 5, Claude Sonnet 5, GPT-5.6 Luna/Sol, GPT-6 Astra, Gemini 3.8 Flash, Gemini 3.1 Pro, Grok 4.6, …

**Cheap / flash baselines:** Gemini 3.x Flash, GPT-5.4 nano, Gemma 4 31B, Claude Haiku 4.5, …

Platform: Kaggle Community Benchmarks (`log-triage-label`, `log-triage-panic-trap`). Infra failures (429/503/quota) are reported separately from ability scores.

---

## 4. Results

### 4.1 Expensive new vs cheap flash/nano

![Per-model LT and tier means](../assets/expensive_vs_cheap_lt.png)

![Gap: best expensive only +0.07 over best flash](../assets/expensive_vs_cheap_gap.png)

| Tier | Best models | Best LT | Panic |
| --- | --- | ---: | ---: |
| Expensive newest (usable) | Claude Sonnet 5, GPT-5.6 Luna | **0.961** | 1.000 |
| Cheap flash | Gemini 3.8 / 3.7 Flash | **0.894** | 1.000 |
| Cheap open / nano | Gemma 4 31B, GPT-5.4 nano | 0.748–0.778 | 1.000 |
| Expensive but weaker here | GPT-5.5, GPT-5.4 flagship | 0.039–0.571 | 1.000* |

\*Panic often perfect even when label score collapses — different failure mode.

**Delta that matters:** best expensive − best cheap flash = **+0.067 LT** on this probe (~one to two items out of the weighted set).

### 4.2 False alarms are already “solved” by cheap models

![Panic trap: cheap matches expensive](../assets/panic_cheap_vs_expensive.png)

When the question is narrowed to “confirmed attack, yes/no?” on noise/misconfig, flash/nano and expensive models that finished both land near **1.0**. Paying more does **not** buy calmer panic behavior on this task — the 4-way label is where models separate.

### 4.3 Newest flagship table (primary ranking)

| Model | LT | Panic | Notes |
| --- | ---: | ---: | --- |
| Claude Sonnet 5 | **0.961** | 1.000 | Top usable |
| GPT-5.6 Luna | **0.961** | 1.000 | Top usable |
| Gemini 3.1 Pro | 0.894 | 1.000 | Ties best flash |
| Gemini 3.8 Flash | 0.894 | 1.000 | Best cheap |
| GPT-5.6 Sol | 0.793 | 1.000 | Behind flash |
| Claude Opus 5 / GPT-6 / Grok 4.6 | — | — | Unusable label run (0.0 / ERR) |

### 4.4 What “proof” means here

We do **not** claim statistical supremacy over all SOC work. We claim a **reproducible diagnostic**:

1. Frozen synthetic dataset in git (`dataset/items.jsonl`)  
2. Deterministic gold scored by `param_id`  
3. Public tasks + downloadable run artifacts  
4. Charts regenerated from those scores (`scripts/make_log_triage_charts.py`)  

N is small on purpose: one miss moves Twin-style gaps loudly. That is a feature for a qualitative probe, not a bug.

---

## 5. Discussion

### 5.1 Answering RQ2

**Expensive new models are not consistently better for SOC first-pass triage.**

- The *best* expensive models win a **small** lift (+0.07 LT).  
- Several expensive models **lose** to nano/flash.  
- Panic/false-alarm calmness is already high for cheap models.

So the rational SOC policy is not “always buy Opus.” It is:

1. Measure on *your* triage distribution (or this probe).  
2. Use flash/nano if within your accuracy budget.  
3. Pay for Sonnet 5 / GPT-5.6 Luna only if that last few points are worth the bill.

### 5.2 Relation to ART

| Benchmark | Question |
| --- | --- |
| ART | Did the model respect the **code patch**? |
| LT | Did the model stay calm on the **log**? |

Same philosophy (false alarms + abstain), different modality. Together they argue that “security AI” quality is about **context discipline**, not scary-token spotting.

### 5.3 Limits

- Synthetic logs, small N.  
- Single-shot structured labels; no tool use, no multi-hour investigations.  
- Some flagship runs failed on platform quota/429 — those are infra, not SOC skill.  
- GPT-5.4 flagship’s near-zero LT completed but looks like a parse/format pathology — needs transcript audit before insulting the model family.

---

## 6. What we would measure next

1. Multi-hop evidence (model must ask for the missing field instead of guessing).  
2. Costed policy score: weight false pages vs missed attacks in dollars.  
3. Diff-aware triage for detection rule PRs.  
4. Larger N once gold adjudication is routine.

---

## 7. Conclusion

SOC analysis is where models waste money by being dramatic.

On **SOC Log Triage**, the evidence says:

- **Best expensive:** Sonnet 5 ≈ GPT-5.6 Luna (LT 0.96)  
- **Best cheap:** Gemini 3.8/3.7 Flash (LT 0.89)  
- **Gap:** ~7 points — real, but not “throw away flash” large  
- **Panic:** cheap already matches expensive  

If your vendor pitch is “our frontier model will fix the SOC queue,” ask for a twin-style log triage score — not a chat demo on one scary line.

---

## My Benchmark

**Source (MIT):** https://github.com/mziqudhd92/kaggle-soc-log-triage-benchmark  

**Kaggle tasks**

- https://www.kaggle.com/benchmarks/tasks/moranzavdi/log-triage-label  
- https://www.kaggle.com/benchmarks/tasks/moranzavdi/log-triage-panic-trap  

```bash
kaggle b t run log-triage-label -m gemini-3.8-flash --wait
kaggle b t run log-triage-label -m claude-sonnet-5-default --wait
```

**Charts:** `assets/expensive_vs_cheap_*.png`, `assets/panic_cheap_vs_expensive.png`  

**Safety:** synthetic logs only; defensive research; no live targeting.

**Credit:** Companion to [ART](https://github.com/mziqudhd92/kaggle-art-benchmark); inspired by proof-over-speculation tooling ([Iridium](https://github.com/mziqudhd92/Iridium)).
