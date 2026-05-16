"""
Visualization Module

Generates a multi-panel analytics dashboard using matplotlib/seaborn.
Designed to be replaced by a JS/D3 frontend layer later.
Each chart function is independent and testable in isolation.
"""
import os
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns

from core.models import FullAnalyticsSnapshot
from core.engine import AnalyticsSummary


# ─── Theme ────────────────────────────────────────────────────────────────────

PALETTE = {
    "bg":        "#0D0F14",
    "surface":   "#141720",
    "surface2":  "#1C2030",
    "border":    "#252A3A",
    "accent":    "#4F8EF7",
    "accent2":   "#A78BFA",
    "accent3":   "#34D399",
    "warn":      "#F59E0B",
    "danger":    "#F87171",
    "text":      "#E2E8F0",
    "text_muted":"#64748B",
}

FONT_TITLE   = {"fontsize": 13, "fontweight": "bold",  "color": PALETTE["text"]}
FONT_LABEL   = {"fontsize": 9,  "fontweight": "normal","color": PALETTE["text_muted"]}
FONT_TICK    = {"labelsize": 8,  "labelcolor": PALETTE["text_muted"], "color": PALETTE["border"]}


def _apply_base_style(ax: plt.Axes, title: str = "", xlabel: str = "", ylabel: str = "") -> None:
    ax.set_facecolor(PALETTE["surface"])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["border"])
        spine.set_linewidth(0.5)
    ax.tick_params(**FONT_TICK)
    ax.set_title(title, **FONT_TITLE, pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, **FONT_LABEL)
    if ylabel:
        ax.set_ylabel(ylabel, **FONT_LABEL)
    ax.grid(axis="y", color=PALETTE["border"], linewidth=0.4, alpha=0.6)
    ax.grid(axis="x", visible=False)


# ─── Individual chart builders ────────────────────────────────────────────────

def chart_views_timeseries(ax: plt.Axes, summary: AnalyticsSummary, snap: FullAnalyticsSnapshot) -> None:
    ts   = snap.raw_time_series
    if not ts:
        ax.text(0.5, 0.5, "No time series data", ha="center", va="center",
                color=PALETTE["text_muted"], transform=ax.transAxes)
        return

    dates = [p.date for p in ts]
    views = [p.views for p in ts]
    x     = np.arange(len(dates))

    # Gradient fill
    ax.fill_between(x, views, alpha=0.15, color=PALETTE["accent"])
    ax.plot(x, views, color=PALETTE["accent"], linewidth=1.8, zorder=3)

    # Peak marker
    peak_idx = views.index(max(views))
    ax.scatter([peak_idx], [views[peak_idx]], color=PALETTE["warn"],
               s=60, zorder=5, label=f"Peak: {views[peak_idx]:,}")

    # Trend line
    z = np.polyfit(x, views, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), "--", color=PALETTE["accent2"], linewidth=1, alpha=0.6, label="Trend")

    # X ticks: show ~6 labels
    step = max(1, len(dates) // 6)
    ax.set_xticks(x[::step])
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)],
                       rotation=30, ha="right", fontsize=7, color=PALETTE["text_muted"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))

    trend_arrow = "▲" if summary.trend.direction == "up" else ("▼" if summary.trend.direction == "down" else "→")
    ax.legend(frameon=False, labelcolor=PALETTE["text_muted"], fontsize=7)
    _apply_base_style(ax, title=f"Daily Views  {trend_arrow}  {summary.trend.momentum_30d:+.1f}% (30d momentum)",
                      ylabel="Views")


def chart_subscriber_delta(ax: plt.Axes, snap: FullAnalyticsSnapshot) -> None:
    ts    = snap.raw_time_series
    if not ts:
        return

    dates  = [p.date for p in ts]
    gained = [p.subscribers_gained for p in ts]
    lost   = [-p.subscribers_lost  for p in ts]
    x      = np.arange(len(dates))

    ax.bar(x, gained, color=PALETTE["accent3"], alpha=0.85, label="Gained", width=0.6)
    ax.bar(x, lost,   color=PALETTE["danger"],  alpha=0.75, label="Lost",   width=0.6)
    ax.axhline(0, color=PALETTE["border"], linewidth=0.8)

    step = max(1, len(dates) // 6)
    ax.set_xticks(x[::step])
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)],
                       rotation=30, ha="right", fontsize=7, color=PALETTE["text_muted"])

    ax.legend(frameon=False, labelcolor=PALETTE["text_muted"], fontsize=7)
    _apply_base_style(ax, title="Daily Subscriber Delta", ylabel="Subscribers")


def chart_content_performance(ax: plt.Axes, summary: AnalyticsSummary) -> None:
    scores = summary.content_scores[:10]   # top 10
    if not scores:
        return

    titles    = [s.title[:30] + ("…" if len(s.title) > 30 else "") for s in scores]
    composites = [s.composite_score for s in scores]
    y = np.arange(len(titles))

    colors = [PALETTE["accent3"] if s.percentile_rank >= 70
              else (PALETTE["accent"] if s.percentile_rank >= 40 else PALETTE["danger"])
              for s in scores]

    bars = ax.barh(y, composites, color=colors, alpha=0.85, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(titles, fontsize=7, color=PALETTE["text_muted"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)

    for bar, score in zip(bars, composites):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{score:.0f}", va="center", fontsize=7, color=PALETTE["text_muted"])

    legend_patches = [
        mpatches.Patch(color=PALETTE["accent3"], label="Top Performer (≥P70)"),
        mpatches.Patch(color=PALETTE["accent"],  label="Average (P40–P70)"),
        mpatches.Patch(color=PALETTE["danger"],  label="Underperformer (<P40)"),
    ]
    ax.legend(handles=legend_patches, frameon=False, labelcolor=PALETTE["text_muted"],
              fontsize=6, loc="lower right")
    _apply_base_style(ax, title="Content Composite Score (0–100)", xlabel="Score")


def chart_engagement_scatter(ax: plt.Axes, summary: AnalyticsSummary) -> None:
    scores = summary.content_scores
    if not scores:
        return

    views = [s.view_count for s in scores]
    eng   = [s.engagement_rate * 100 for s in scores]
    comp  = [s.composite_score for s in scores]

    sc = ax.scatter(views, eng, c=comp, cmap="cool", alpha=0.85,
                    s=80, edgecolors=PALETTE["border"], linewidth=0.5, zorder=3)

    cbar = plt.colorbar(sc, ax=ax, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=PALETTE["text_muted"], labelcolor=PALETTE["text_muted"])
    cbar.set_label("Composite Score", color=PALETTE["text_muted"], fontsize=7)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    _apply_base_style(ax, title="Views vs Engagement Rate",
                      xlabel="View Count", ylabel="Engagement Rate (%)")


def chart_watch_time(ax: plt.Axes, snap: FullAnalyticsSnapshot) -> None:
    ts = snap.raw_time_series
    if not ts:
        return

    dates = [p.date for p in ts]
    hours = [p.estimated_minutes_watched / 60 for p in ts]
    x     = np.arange(len(dates))

    ax.fill_between(x, hours, alpha=0.2, color=PALETTE["accent2"])
    ax.plot(x, hours, color=PALETTE["accent2"], linewidth=1.5)

    step = max(1, len(dates) // 6)
    ax.set_xticks(x[::step])
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)],
                       rotation=30, ha="right", fontsize=7, color=PALETTE["text_muted"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}h"))

    _apply_base_style(ax, title="Watch Time (Hours/Day)", ylabel="Hours")


def chart_health_radar(ax: plt.Axes, summary: AnalyticsSummary) -> None:
    health = summary.channel_health
    labels = ["Growth", "Engagement", "Consistency", "Influence"]
    values = [
        health.growth_score,
        health.engagement_score,
        health.consistency_score,
        health.influence_score,
    ]
    N    = len(labels)
    angs = [n / float(N) * 2 * np.pi for n in range(N)]
    angs += angs[:1]
    vals  = [v / 100 for v in values] + [values[0] / 100]

    ax.set_facecolor(PALETTE["surface"])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)
    ax.set_xticks(angs[:-1])
    ax.set_xticklabels(labels, color=PALETTE["text_muted"], fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25", "50", "75", "100"], color=PALETTE["text_muted"], fontsize=6)
    ax.set_ylim(0, 1)
    for spine in ax.spines.values():
        spine.set_color(PALETTE["border"])

    ax.plot(angs, vals, color=PALETTE["accent"], linewidth=2)
    ax.fill(angs, vals, alpha=0.25, color=PALETTE["accent"])

    score_color = (PALETTE["accent3"] if health.overall >= 70
                   else (PALETTE["warn"] if health.overall >= 45 else PALETTE["danger"]))
    radar_title_font = {k: v for k, v in FONT_TITLE.items() if k != "color"}
    ax.set_title(f"Channel Health · {health.overall:.0f}/100\n{health.label}",
                 **radar_title_font, color=score_color, pad=20)


def chart_kpi_tiles(fig: plt.Figure, gs_slot, summary: AnalyticsSummary, snap: FullAnalyticsSnapshot) -> None:
    """Renders a row of KPI tiles inside a GridSpecFromSubplotSpec."""
    kpi = summary.kpi
    tiles = [
        ("Subscribers",     f"{kpi['subscribers']:,}",             PALETTE["accent"]),
        ("Window Views",    f"{kpi['window_views']:,}",            PALETTE["accent2"]),
        ("Watch Hours",     f"{kpi['watch_hours']:,.0f}h",         PALETTE["accent3"]),
        ("Net Subs (win.)", f"{kpi['net_subscribers']:+,}",        PALETTE["accent3"] if kpi['net_subscribers'] >= 0 else PALETTE["danger"]),
        ("Engagement",      f"{kpi['engagement_rate_pct']:.2f}%",  PALETTE["warn"]),
        ("Health Score",    f"{kpi['health_score']:.0f} / 100",    PALETTE["accent3"] if kpi['health_score'] >= 70 else PALETTE["warn"]),
    ]

    inner = gridspec.GridSpecFromSubplotSpec(1, len(tiles), subplot_spec=gs_slot, wspace=0.08)
    for i, (label, value, color) in enumerate(tiles):
        ax = fig.add_subplot(inner[i])
        ax.set_facecolor(PALETTE["surface2"])
        for spine in ax.spines.values():
            spine.set_color(color)
            spine.set_linewidth(1.2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=14,
                fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.25, label, ha="center", va="center", fontsize=7,
                color=PALETTE["text_muted"], transform=ax.transAxes)


# ─── Dashboard Assembler ──────────────────────────────────────────────────────

def build_dashboard(
    snapshot: FullAnalyticsSnapshot,
    summary: AnalyticsSummary,
    output_path: Optional[str] = None,
    show: bool = False,
) -> str:
    plt.rcParams.update({
        "figure.facecolor":  PALETTE["bg"],
        "text.color":        PALETTE["text"],
        "axes.labelcolor":   PALETTE["text_muted"],
        "xtick.color":       PALETTE["text_muted"],
        "ytick.color":       PALETTE["text_muted"],
        "font.family":       "monospace",
    })

    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor(PALETTE["bg"])

    # Master grid: [header] [kpis] [row1: 3 charts] [row2: 3 charts]
    outer = gridspec.GridSpec(4, 1, figure=fig,
                              height_ratios=[0.06, 0.10, 0.42, 0.42],
                              hspace=0.38)

    # ── Header ──
    ax_hdr = fig.add_subplot(outer[0])
    ax_hdr.set_facecolor(PALETTE["bg"])
    for spine in ax_hdr.spines.values():
        spine.set_visible(False)
    ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
    ch = snapshot.channel
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    ax_hdr.text(0.0, 0.7, f"◈ {ch.channel_title}",
                fontsize=16, fontweight="bold", color=PALETTE["text"], transform=ax_hdr.transAxes)
    ax_hdr.text(0.0, 0.1,
                f"youtube · {ch.subscriber_count:,} subscribers · {ch.video_count} videos · synced {ts}",
                fontsize=8, color=PALETTE["text_muted"], transform=ax_hdr.transAxes)
    ax_hdr.text(1.0, 0.5,
                f"{'▲' if summary.trend.direction=='up' else '▼' if summary.trend.direction=='down' else '→'}  "
                f"{summary.trend.momentum_30d:+.1f}% 30d · "
                f"{summary.kpi['health_label']}",
                fontsize=10, color=PALETTE["accent2"],
                transform=ax_hdr.transAxes, ha="right", va="center")

    # ── KPI tiles ──
    chart_kpi_tiles(fig, outer[1], summary, snapshot)

    # ── Row 1: Views | Subscriber delta | Health radar ──
    row1 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[2], wspace=0.28)
    chart_views_timeseries(fig.add_subplot(row1[0]), summary, snapshot)
    chart_subscriber_delta(fig.add_subplot(row1[1]), snapshot)
    chart_health_radar(fig.add_subplot(row1[2], polar=True), summary)

    # ── Row 2: Content perf | Engagement scatter | Watch time ──
    row2 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[3], wspace=0.28)
    chart_content_performance(fig.add_subplot(row2[0]), summary)
    chart_engagement_scatter(fig.add_subplot(row2[1]),  summary)
    chart_watch_time(fig.add_subplot(row2[2]), snapshot)

    if output_path is None:
        output_path = f"analytics_dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"

    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
    if show:
        plt.show()
    plt.close(fig)
    return output_path
