#!/usr/bin/env python3
"""Generate article charts: expensive new vs cheap flash/nano for SOC LT."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig-lt")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# Usable completed LT scores only (exclude infra 0.0 / known ERRORED label runs).
# Panic calm score where available.
CHEAP = [
    ("Gemini 3.8 Flash", 0.894, 1.00),
    ("Gemini 3.7 Flash", 0.894, 1.00),
    ("Claude Haiku 4.5", 0.827, 0.90),
    ("Gemma 4 31B", 0.778, 1.00),
    ("Gemini 3.5 Flash", 0.778, 1.00),
    ("GPT-5.4 nano", 0.748, 1.00),
    ("Gemini 2.5 Flash", 0.748, 0.80),
]

EXPENSIVE = [
    ("Claude Sonnet 5", 0.961, 1.00),
    ("GPT-5.6 Luna", 0.961, 1.00),
    ("Gemini 3.1 Pro", 0.894, 1.00),
    ("GPT-5.6 Sol", 0.793, 1.00),
    ("GPT-5.5", 0.571, 1.00),
    ("GPT-5.4 flagship", 0.039, 1.00),  # completed but near-floor — shown as caution
]

CHEAP_COLOR = "#2A9D8F"
EXPENSIVE_COLOR = "#E76F51"
MUTED = "#6C757D"


def _style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#222222",
            "text.color": "#222222",
            "xtick.color": "#222222",
            "ytick.color": "#222222",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
        }
    )


def chart_expensive_vs_cheap_lt() -> Path:
    """Side-by-side mean + individual bars: expensive new vs cheap flash/nano."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})

    # Left: per-model horizontal bars, grouped
    ax = axes[0]
    rows = [(n, s, "cheap") for n, s, _ in CHEAP] + [
        (n, s, "expensive") for n, s, _ in EXPENSIVE
    ]
    # sort by score for readability
    rows = sorted(rows, key=lambda r: r[1])
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [CHEAP_COLOR if r[2] == "cheap" else EXPENSIVE_COLOR for r in rows]
    y = np.arange(len(rows))
    ax.barh(y, vals, color=colors, height=0.72, edgecolor="white")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("LT score (4-way log triage)")
    ax.axvline(0.894, color=MUTED, ls="--", lw=1, alpha=0.8)
    ax.text(0.90, len(rows) - 0.3, "best flash\n(0.89)", fontsize=8, color=MUTED, ha="right")
    ax.set_title("SOC Log Triage: cheap flash/nano vs expensive new")
    for yi, v in zip(y, vals):
        ax.text(v + 0.015, yi, f"{v:.2f}", va="center", fontsize=8, color="#333")

    # Right: tier means
    ax = axes[1]
    cheap_mean = float(np.mean([s for _, s, _ in CHEAP]))
    exp_usable = [s for _, s, _ in EXPENSIVE if s >= 0.5]  # exclude near-floor flagship anomaly
    exp_all = [s for _, s, _ in EXPENSIVE]
    exp_mean_usable = float(np.mean(exp_usable))
    exp_mean_all = float(np.mean(exp_all))
    labels = [
        "Cheap\nflash / nano / Gemma",
        "Expensive new\n(excl. broken 0.04)",
        "Expensive new\n(incl. GPT-5.4 0.04)",
    ]
    means = [cheap_mean, exp_mean_usable, exp_mean_all]
    cols = [CHEAP_COLOR, EXPENSIVE_COLOR, "#B5654A"]
    bars = ax.bar(labels, means, color=cols, width=0.65, edgecolor="white")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean LT score")
    ax.set_title("Paying more ≠ consistently better")
    for b, m in zip(bars, means):
        ax.text(b.get_x() + b.get_width() / 2, m + 0.03, f"{m:.2f}", ha="center", fontsize=11, fontweight="bold")
    ax.annotate(
        "Best expensive (0.96) only\n+0.07 over best flash (0.89)",
        xy=(1, exp_mean_usable),
        xytext=(0.55, 0.45),
        fontsize=8,
        color="#444",
        arrowprops=dict(arrowstyle="->", color=MUTED),
    )

    # Legend
    from matplotlib.patches import Patch

    fig.legend(
        handles=[
            Patch(facecolor=CHEAP_COLOR, label="Cheap / flash / nano"),
            Patch(facecolor=EXPENSIVE_COLOR, label="Expensive / newest"),
        ],
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out = ASSETS / "expensive_vs_cheap_lt.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_gap_story() -> Path:
    """Dumbbell / paired view: best cheap vs best expensive + underperforming expensive."""
    _style()
    fig, ax = plt.subplots(figsize=(9.5, 4.8))

    points = [
        ("Best expensive\n(Sonnet 5 / GPT-5.6 Luna)", 0.961, EXPENSIVE_COLOR),
        ("Best cheap flash\n(Gemini 3.8 / 3.7 Flash)", 0.894, CHEAP_COLOR),
        ("Cheap open weights\n(Gemma 4 31B)", 0.778, CHEAP_COLOR),
        ("Cheap nano\n(GPT-5.4 nano)", 0.748, CHEAP_COLOR),
        ("Expensive GPT-5.5", 0.571, EXPENSIVE_COLOR),
        ("Expensive GPT-5.4 flagship*", 0.039, EXPENSIVE_COLOR),
    ]
    y = np.arange(len(points))[::-1]
    for yi, (label, score, color) in zip(y, points):
        ax.hlines(yi, 0, score, color=color, lw=3, alpha=0.85)
        ax.plot(score, yi, "o", color=color, markersize=11)
        ax.text(score + 0.02, yi, f"{score:.2f}", va="center", fontsize=10, fontweight="bold")
        ax.text(-0.02, yi, label, va="center", ha="right", fontsize=9)

    ax.axvspan(0.748, 0.894, color=CHEAP_COLOR, alpha=0.08, label="Cheap band")
    ax.set_xlim(-0.55, 1.12)
    ax.set_ylim(-0.6, len(points) - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("LT score")
    ax.set_title("SOC triage: expensive models are not consistently ahead of cheap flash/nano")
    ax.text(
        0.5,
        -0.55,
        "* GPT-5.4 flagship completed but scored near floor — investigate before trusting; still shows price ≠ quality.",
        transform=ax.get_xaxis_transform(),
        fontsize=7.5,
        color=MUTED,
        ha="center",
    )
    # delta callout
    ax.annotate(
        "",
        xy=(0.961, 5),
        xytext=(0.894, 4),
        arrowprops=dict(arrowstyle="<->", color="#333", lw=1.2),
    )
    ax.text(0.93, 4.55, "+0.07", fontsize=9, color="#333", ha="center")

    fig.tight_layout()
    out = ASSETS / "expensive_vs_cheap_gap.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_panic_parity() -> Path:
    """Panic calm scores: cheap and expensive both ~perfect."""
    _style()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    rows = [(n, p, "cheap") for n, _, p in CHEAP] + [
        (n, p, "expensive") for n, s, p in EXPENSIVE if s >= 0.5
    ]
    rows = sorted(rows, key=lambda r: r[1])
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [CHEAP_COLOR if r[2] == "cheap" else EXPENSIVE_COLOR for r in rows]
    y = np.arange(len(rows))
    ax.barh(y, vals, color=colors, height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Panic-trap score (1.0 = never false-alarm on noise/misconfig)")
    ax.set_title("False-alarm calmness: cheap models already match expensive ones")
    for yi, v in zip(y, vals):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    out = ASSETS / "panic_cheap_vs_expensive.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_takeaway_board() -> Path:
    """Simple 2x2 style summary board for the article hero."""
    _style()
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    ax.text(5, 5.4, "SOC Log Triage — does expensive beat cheap?", ha="center", fontsize=14, fontweight="bold")

    boxes = [
        (0.4, 2.2, 4.4, 2.6, CHEAP_COLOR, "Cheap flash / nano", "Best LT ≈ 0.89\nPanic ≈ 1.0\nGemini 3.8 / 3.7 Flash"),
        (5.2, 2.2, 4.4, 2.6, EXPENSIVE_COLOR, "Expensive newest", "Best LT ≈ 0.96\nPanic ≈ 1.0\nSonnet 5 / GPT-5.6 Luna"),
    ]
    for x, y, w, h, color, title, body in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), w, h, fill=True, facecolor=color, alpha=0.15, edgecolor=color, lw=2, zorder=1)
        )
        ax.text(x + w / 2, y + h - 0.45, title, ha="center", fontsize=12, fontweight="bold", color=color)
        ax.text(x + w / 2, y + 0.85, body, ha="center", va="center", fontsize=10)

    ax.text(
        5,
        1.2,
        "Gap from best cheap → best expensive: only +0.07 LT on this probe.\n"
        "Several costly models (GPT-5.5, GPT-5.4) scored worse than nano/flash.",
        ha="center",
        fontsize=10,
        color="#333",
    )
    ax.text(
        5,
        0.35,
        "Conclusion: pay for Sonnet 5 / GPT-5.6 Luna only if that small lift is worth it;\notherwise flash is enough for SOC first-pass triage.",
        ha="center",
        fontsize=9.5,
        fontweight="bold",
        color="#222",
    )
    out = ASSETS / "expensive_vs_cheap_takeaway.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    outs = [
        chart_expensive_vs_cheap_lt(),
        chart_gap_story(),
        chart_panic_parity(),
        chart_takeaway_board(),
    ]
    for p in outs:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
