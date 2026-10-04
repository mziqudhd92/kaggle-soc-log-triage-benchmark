#!/usr/bin/env python3
"""Publication-quality charts for the SOC Log Triage research article."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig-lt")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/xdg-cache-lt")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# Usable completed LT scores (exclude infra 0.0 / known ERRORED label runs).
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
    ("GPT-5.4 flagship", 0.039, 1.00),
]

# Professional palette (print-safe, not neon AI defaults)
INK = "#1B1F24"
MUTED = "#5C6570"
RULE = "#D7DCE2"
GRID = "#EEF1F4"
CHEAP_C = "#0F6E56"  # deep teal
CHEAP_SOFT = "#D8EFE7"
EXP_C = "#9A3412"  # burnt umber
EXP_SOFT = "#F5E1D6"
ACCENT = "#1D4E89"  # steel blue
WARN = "#B45309"
BG = "#FAFBFC"
FOOTER = "SOC Log Triage Benchmark  ·  Kaggle Community Benchmarks  ·  2026-10-04"
DPI = 220


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "axes.edgecolor": RULE,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.titlesize": 13.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 10.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "legend.frameon": False,
            "figure.dpi": 120,
        }
    )


def _footer(fig, y: float = 0.01) -> None:
    fig.text(0.5, y, FOOTER, ha="center", va="bottom", fontsize=7.5, color=MUTED)


def _save(fig, name: str, rect=(0, 0.04, 1, 1), *, tight: bool = True) -> Path:
    if tight:
        try:
            fig.tight_layout(rect=rect)
        except Exception:
            fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.12)
    else:
        fig.subplots_adjust(left=0.06, right=0.98, top=0.90, bottom=0.10)
    _footer(fig)
    out = ASSETS / name
    fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out


def chart_expensive_vs_cheap_lt() -> Path:
    _style()
    fig, axes = plt.subplots(
        1, 2, figsize=(12.2, 6.0), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.28}
    )

    ax = axes[0]
    rows = [(n, s, "cheap") for n, s, _ in CHEAP] + [
        (n, s, "expensive") for n, s, _ in EXPENSIVE
    ]
    rows = sorted(rows, key=lambda r: r[1])
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [CHEAP_C if r[2] == "cheap" else EXP_C for r in rows]
    y = np.arange(len(rows))

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, lw=1)
    bars = ax.barh(y, vals, color=colors, height=0.68, edgecolor="none", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("LT score  (weighted 4-way accuracy)")
    ax.axvline(0.894, color=MUTED, ls=(0, (4, 3)), lw=1.1, zorder=2)
    ax.text(
        0.894,
        len(rows) - 0.15,
        " best flash 0.894",
        fontsize=8,
        color=MUTED,
        va="bottom",
        ha="left",
    )
    ax.set_title("A. Per-model Log Triage (LT) score", loc="left", pad=10)
    for yi, v, c in zip(y, vals, colors):
        ax.text(min(v + 0.018, 1.08), yi, f"{v:.3f}", va="center", fontsize=8, color=c)

    # Right: tier means
    ax = axes[1]
    cheap_mean = float(np.mean([s for _, s, _ in CHEAP]))
    exp_usable = [s for _, s, _ in EXPENSIVE if s >= 0.5]
    exp_all = [s for _, s, _ in EXPENSIVE]
    means = [cheap_mean, float(np.mean(exp_usable)), float(np.mean(exp_all))]
    labels = [
        "Cheap\nflash / nano",
        "Expensive\n(excl. 0.039)",
        "Expensive\n(all)",
    ]
    cols = [CHEAP_C, EXP_C, "#C47A52"]
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, lw=1)
    x = np.arange(len(means))
    bars = ax.bar(x, means, color=cols, width=0.62, edgecolor="none", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Mean LT score")
    ax.set_title("B. Tier means — price ≠ quality", loc="left", pad=10)
    for b, m in zip(bars, means):
        ax.text(
            b.get_x() + b.get_width() / 2,
            m + 0.035,
            f"{m:.3f}",
            ha="center",
            fontsize=11,
            fontweight="bold",
            color=INK,
        )
    ax.annotate(
        "Best expensive only\n+0.067 vs best flash",
        xy=(1, means[1]),
        xytext=(1.55, 0.42),
        fontsize=8.5,
        color=MUTED,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )

    fig.suptitle(
        "Expensive newest models vs cheap flash/nano on SOC Log Triage",
        fontsize=14.5,
        fontweight="bold",
        color=INK,
        y=1.02,
    )
    from matplotlib.patches import Patch

    fig.legend(
        handles=[
            Patch(facecolor=CHEAP_C, label="Cheap / flash / nano"),
            Patch(facecolor=EXP_C, label="Expensive / newest"),
        ],
        loc="lower center",
        ncol=2,
        bbox_to_anchor=(0.5, -0.02),
        fontsize=9,
    )
    return _save(fig, "expensive_vs_cheap_lt.png", rect=(0, 0.06, 1, 0.96))


def chart_gap_story() -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(10.5, 5.6))

    points = [
        ("Best expensive\nSonnet 5 / GPT-5.6 Luna", 0.961, EXP_C),
        ("Best cheap flash\nGemini 3.8 / 3.7 Flash", 0.894, CHEAP_C),
        ("Cheap open weights\nGemma 4 31B", 0.778, CHEAP_C),
        ("Cheap nano\nGPT-5.4 nano", 0.748, CHEAP_C),
        ("Expensive GPT-5.5", 0.571, EXP_C),
        ("Expensive GPT-5.4 flagship*", 0.039, EXP_C),
    ]
    y = np.arange(len(points))[::-1]
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, lw=1)
    ax.axvspan(0.748, 0.894, color=CHEAP_SOFT, alpha=0.9, zorder=0)
    ax.text(0.821, len(points) - 0.35, "cheap performance band", fontsize=8, color=CHEAP_C, ha="center")

    for yi, (label, score, color) in zip(y, points):
        ax.hlines(yi, 0, score, color=color, lw=2.6, alpha=0.9, zorder=2)
        ax.plot(score, yi, "o", color=color, markersize=10, markeredgecolor="white", markeredgewidth=1.2, zorder=3)
        ax.text(score + 0.025, yi, f"{score:.3f}", va="center", fontsize=10, fontweight="bold", color=color)
        ax.text(-0.03, yi, label, va="center", ha="right", fontsize=9.2, color=INK)

    ax.annotate(
        "",
        xy=(0.961, y[0]),
        xytext=(0.894, y[1]),
        arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.4),
    )
    ax.text(0.928, (y[0] + y[1]) / 2 + 0.15, "Δ +0.067", fontsize=9.5, color=ACCENT, ha="center", fontweight="bold")

    ax.set_xlim(-0.62, 1.15)
    ax.set_ylim(-0.7, len(points) - 0.25)
    ax.set_yticks([])
    ax.set_xlabel("LT score")
    ax.set_title(
        "Gap story: the best expensive models lead by only +0.067 LT",
        loc="left",
        pad=12,
    )
    ax.text(
        0.5,
        -0.62,
        "* GPT-5.4 flagship completed the run but scored near floor — treat as format/ability pathology, still evidence that price ≠ triage quality.",
        transform=ax.get_xaxis_transform(),
        fontsize=7.5,
        color=MUTED,
        ha="center",
    )
    for spine in ("left",):
        ax.spines[spine].set_visible(False)
    return _save(fig, "expensive_vs_cheap_gap.png")


def chart_panic_parity() -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    rows = [(n, p, "cheap") for n, _, p in CHEAP] + [
        (n, p, "expensive") for n, s, p in EXPENSIVE if s >= 0.5
    ]
    rows = sorted(rows, key=lambda r: (r[1], r[0]))
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [CHEAP_C if r[2] == "cheap" else EXP_C for r in rows]
    y = np.arange(len(rows))

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, lw=1)
    ax.barh(y, vals, color=colors, height=0.66, edgecolor="none", zorder=3)
    ax.axvline(1.0, color=ACCENT, ls=(0, (3, 2)), lw=1, alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("Panic-trap score  (1.0 = never false-alarms on noise/misconfig)")
    ax.set_title(
        "False-alarm calmness: cheap models already match expensive ones",
        loc="left",
        pad=12,
    )
    for yi, v, c in zip(y, vals, colors):
        ax.text(min(v + 0.02, 1.08), yi, f"{v:.2f}", va="center", fontsize=8.5, color=c)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(facecolor=CHEAP_C, label="Cheap / flash / nano"),
            Patch(facecolor=EXP_C, label="Expensive / newest"),
        ],
        loc="lower right",
        fontsize=9,
    )
    return _save(fig, "panic_cheap_vs_expensive.png")


def chart_takeaway_board() -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(
        6,
        7.45,
        "SOC Log Triage — does expensive beat cheap?",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        6,
        6.95,
        "First-pass 4-way log labeling on 22 synthetic twin/control bundles",
        ha="center",
        fontsize=10,
        color=MUTED,
    )

    def card(x, y, w, h, edge, fill, title, lines):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.15",
                facecolor=fill,
                edgecolor=edge,
                lw=1.8,
                zorder=1,
            )
        )
        ax.text(x + w / 2, y + h - 0.45, title, ha="center", fontsize=12.5, fontweight="bold", color=edge)
        for i, line in enumerate(lines):
            ax.text(x + w / 2, y + h - 1.15 - i * 0.48, line, ha="center", fontsize=10.5, color=INK)

    card(
        0.5,
        3.1,
        5.2,
        3.3,
        CHEAP_C,
        CHEAP_SOFT,
        "Cheap flash / nano",
        ["Best LT  0.894", "Panic   ≈ 1.00", "Gemini 3.8 / 3.7 Flash"],
    )
    card(
        6.3,
        3.1,
        5.2,
        3.3,
        EXP_C,
        EXP_SOFT,
        "Expensive newest",
        ["Best LT  0.961", "Panic   ≈ 1.00", "Sonnet 5 / GPT-5.6 Luna"],
    )

    ax.add_patch(
        FancyBboxPatch(
            (0.5, 0.55),
            11.0,
            2.2,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor="white",
            edgecolor=RULE,
            lw=1.2,
            zorder=1,
        )
    )
    ax.text(6, 2.25, "Key result", ha="center", fontsize=10, fontweight="bold", color=ACCENT)
    ax.text(
        6,
        1.55,
        "Gap from best cheap → best expensive: only  +0.067  LT on this probe.",
        ha="center",
        fontsize=11.5,
        color=INK,
    )
    ax.text(
        6,
        0.95,
        "Several costly models (GPT-5.5, GPT-5.4) scored worse than nano/flash.\n"
        "Recommendation: default to flash; pay for Sonnet 5 / Luna only if that lift is worth the bill.",
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    return _save(fig, "expensive_vs_cheap_takeaway.png", rect=(0, 0.03, 1, 1), tight=False)


def chart_label_distribution() -> Path:
    """Dataset composition — label base rates + twin/control split."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), gridspec_kw={"wspace": 0.35})

    ax = axes[0]
    labels = ["attack", "misconfig", "noise", "needs_more_data"]
    counts = [9, 5, 5, 3]
    colors = ["#9A3412", "#B45309", "#0F6E56", "#1D4E89"]
    x = np.arange(len(labels))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, lw=1)
    bars = ax.bar(x, counts, color=colors, width=0.62, edgecolor="none", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Item count")
    ax.set_ylim(0, 11)
    ax.set_title("A. Gold-label base rates (N = 22)", loc="left", pad=10)
    for b, c in zip(bars, counts):
        ax.text(
            b.get_x() + b.get_width() / 2,
            c + 0.25,
            f"{c}\n({100 * c / 22:.0f}%)",
            ha="center",
            fontsize=9,
            color=INK,
        )
    ax.text(
        0.5,
        -0.18,
        "Always-attack baseline cannot win: misconfig+noise = 10 vs attack = 9",
        transform=ax.transAxes,
        ha="center",
        fontsize=8,
        color=MUTED,
    )

    ax = axes[1]
    sizes = [16, 6]
    explode = (0.02, 0.02)
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=["Twin pairs\n(8 × 2 = 16)", "Controls\n(6)"],
        colors=[ACCENT, MUTED],
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=2),
        textprops=dict(color=INK, fontsize=10),
        pctdistance=0.75,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
        t.set_color("white")
    ax.set_title("B. Twin pairs vs unpaired controls", loc="left", pad=10)
    ax.text(
        0,
        0,
        "22\nitems",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=INK,
    )

    fig.suptitle("Dataset composition — SOC Log Triage", fontsize=14.5, fontweight="bold", y=1.02)
    return _save(fig, "dataset_composition.png", rect=(0, 0.04, 1, 0.95), tight=False)


def chart_twin_method() -> Path:
    """Schematic: shared scary surface → one control flip → different gold."""
    _style()
    fig, ax = plt.subplots(figsize=(11.8, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(
        6,
        8.5,
        "Twin method: same scary surface, one control fact flips the gold label",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        6,
        7.95,
        "Example twin_wp_probe — WordPress exploit-path grocery list",
        ha="center",
        fontsize=10,
        color=MUTED,
    )

    # Shared surface box
    ax.add_patch(
        FancyBboxPatch(
            (3.2, 5.9),
            5.6,
            1.55,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor="white",
            edgecolor=ACCENT,
            lw=1.6,
        )
    )
    ax.text(6, 7.05, "Shared surface", ha="center", fontsize=9, fontweight="bold", color=ACCENT)
    ax.text(
        6,
        6.4,
        "/wp-login.php  ·  /xmlrpc.php  ·  /.env\n"
        "PHPUnit eval-stdin.php  ·  404 responses",
        ha="center",
        fontsize=9.5,
        color=INK,
    )

    # Arrows down
    ax.annotate("", xy=(2.8, 5.5), xytext=(4.5, 5.9), arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.3))
    ax.annotate("", xy=(9.2, 5.5), xytext=(7.5, 5.9), arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.3))

    # Attack card
    ax.add_patch(
        FancyBboxPatch(
            (0.4, 2.3),
            5.0,
            3.0,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=EXP_SOFT,
            edgecolor=EXP_C,
            lw=1.6,
        )
    )
    ax.text(2.9, 4.9, "Attack twin", ha="center", fontsize=11.5, fontweight="bold", color=EXP_C)
    ax.text(
        2.9,
        3.7,
        "Control flip\n"
        "Many distinct external IPs\n"
        "Mixed browser / curl UAs\n"
        "No allowlist note",
        ha="center",
        fontsize=10,
        color=INK,
    )
    ax.text(2.9, 2.6, "gold →  attack", ha="center", fontsize=11, fontweight="bold", color=EXP_C)

    # Noise card
    ax.add_patch(
        FancyBboxPatch(
            (6.6, 2.3),
            5.0,
            3.0,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=CHEAP_SOFT,
            edgecolor=CHEAP_C,
            lw=1.6,
        )
    )
    ax.text(9.1, 4.9, "Noise twin", ha="center", fontsize=11.5, fontweight="bold", color=CHEAP_C)
    ax.text(
        9.1,
        3.7,
        "Control flip\n"
        "Single CI egress IP\n"
        "UA = IridiumCI/1.0\n"
        "Allowlisted nightly scan note",
        ha="center",
        fontsize=10,
        color=INK,
    )
    ax.text(9.1, 2.6, "gold →  noise", ha="center", fontsize=11, fontweight="bold", color=CHEAP_C)

    ax.add_patch(
        FancyBboxPatch(
            (1.2, 0.35),
            9.6,
            1.5,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor="white",
            edgecolor=RULE,
            lw=1.2,
        )
    )
    ax.text(
        6,
        1.35,
        "Prompt isolation: model sees source hint + log only",
        ha="center",
        fontsize=10.5,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        6,
        0.75,
        "twin_id · twin_role · gold_label · rationale are scoring-only and never appear in the prompt",
        ha="center",
        fontsize=9,
        color=MUTED,
    )
    return _save(fig, "twin_method_schematic.png", rect=(0, 0.03, 1, 1), tight=False)


def chart_scoring_weights() -> Path:
    """LT weight breakdown + panic subset."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0), gridspec_kw={"wspace": 0.3})

    ax = axes[0]
    labels = ["attack\n0.35", "misconfig\n0.25", "noise\n0.20", "needs_more_data\n0.20"]
    weights = [0.35, 0.25, 0.20, 0.20]
    colors = ["#9A3412", "#B45309", "#0F6E56", "#1D4E89"]
    wedges, texts, autotexts = ax.pie(
        weights,
        labels=labels,
        colors=colors,
        autopct=lambda p: f"{p/100:.2f}",
        startangle=90,
        wedgeprops=dict(edgecolor=BG, linewidth=2),
        textprops=dict(fontsize=9.5, color=INK),
        pctdistance=0.55,
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("A. LT score weights", loc="left", pad=10)
    ax.text(
        0.5,
        -0.12,
        "LT = Σ wᵢ · Acc(classᵢ)\nMissed attacks cost more than missed noise",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    ax = axes[1]
    cats = ["Panic-trap\nsubset", "Excluded\n(attack /\nneeds_more_data)"]
    vals = [10, 12]
    cols = [WARN, RULE]
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, lw=1)
    bars = ax.bar(cats, vals, color=cols, width=0.55, edgecolor="none", zorder=3)
    ax.set_ylim(0, 14)
    ax.set_ylabel("Items")
    ax.set_title("B. Panic trap uses only non-attack gold", loc="left", pad=10)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.35, str(v), ha="center", fontsize=12, fontweight="bold")
    ax.text(
        0.5,
        -0.18,
        "Question: confirmed attack right now?  Gold = no\nScore = fraction answered no",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    fig.suptitle("Scoring design", fontsize=14.5, fontweight="bold", y=1.02)
    return _save(fig, "scoring_design.png", rect=(0, 0.05, 1, 0.95), tight=False)


def chart_newest_leaderboard() -> Path:
    """Clean leaderboard for newest cohort."""
    _style()
    fig, ax = plt.subplots(figsize=(10.8, 6.0))

    board = [
        ("Claude Sonnet 5", 0.961, 1.000, "ok"),
        ("GPT-5.6 Luna", 0.961, 1.000, "ok"),
        ("Gemini 3.1 Pro", 0.894, 1.000, "ok"),
        ("Gemini 3.8 Flash", 0.894, 1.000, "ok"),
        ("GPT-5.6 Sol", 0.793, 1.000, "ok"),
        ("Claude Opus 4.8", 0.391, None, "weak"),
        ("Claude Opus 5", 0.000, 1.000, "unusable"),
        ("GPT-6 Astra", 0.000, None, "err"),
        ("Grok 4.6", 0.000, None, "err"),
    ]
    y = np.arange(len(board))[::-1]
    status_color = {
        "ok": CHEAP_C,
        "weak": WARN,
        "unusable": EXP_C,
        "err": MUTED,
    }

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, lw=1)
    for yi, (name, lt, panic, st) in zip(y, board):
        c = status_color[st]
        ax.barh(yi, lt, height=0.62, color=c, alpha=0.9 if st == "ok" else 0.45, edgecolor="none", zorder=3)
        ax.text(-0.02, yi, name, ha="right", va="center", fontsize=10, color=INK)
        label = f"{lt:.3f}"
        if panic is not None:
            label += f"   panic {panic:.2f}"
        elif st == "err":
            label += "   ERR"
        ax.text(max(lt, 0.02) + 0.02, yi, label, va="center", fontsize=8.5, color=c if st == "ok" else MUTED)

    ax.axvline(0.894, color=MUTED, ls=(0, (4, 3)), lw=1)
    ax.text(0.894, len(board) - 0.2, " flash baseline", fontsize=8, color=MUTED, va="bottom")
    ax.set_xlim(-0.55, 1.25)
    ax.set_ylim(-0.6, len(board) - 0.3)
    ax.set_yticks([])
    ax.set_xlabel("LT score")
    ax.set_title("Newest-model leaderboard (primary ranking cohort)", loc="left", pad=12)
    ax.spines["left"].set_visible(False)
    return _save(fig, "newest_leaderboard.png")


def main() -> None:
    outs = [
        chart_expensive_vs_cheap_lt(),
        chart_gap_story(),
        chart_panic_parity(),
        chart_takeaway_board(),
        chart_label_distribution(),
        chart_twin_method(),
        chart_scoring_weights(),
        chart_newest_leaderboard(),
    ]
    for p in outs:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
