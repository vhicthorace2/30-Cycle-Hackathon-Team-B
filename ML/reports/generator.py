"""
Report Generator

Produces structured text and JSON reports from AnalyticsSummary.
Useful for logging, alerting, and downstream integrations.
"""
import json
from datetime import datetime
from typing import Optional

from core.models import FullAnalyticsSnapshot
from core.engine import AnalyticsSummary


class ReportGenerator:

    def text_report(self, snapshot: FullAnalyticsSnapshot, summary: AnalyticsSummary) -> str:
        k   = summary.kpi
        h   = summary.channel_health
        tr  = summary.trend
        ch  = snapshot.channel

        lines = [
            "═" * 60,
            f"  ANALYTICS REPORT — {ch.channel_title}",
            f"  Platform: {ch.platform.upper()} · Generated: {datetime.utcnow():%Y-%m-%d %H:%M UTC}",
            "═" * 60,
            "",
            "── CHANNEL OVERVIEW ─────────────────────────────────",
            f"  Subscribers:       {k['subscribers']:>12,}",
            f"  Total Videos:      {k['total_videos']:>12,}",
            f"  All-time Views:    {k['total_views_all_time']:>12,}",
            "",
            "── WINDOW METRICS (last {k['window_days'] if 'window_days' in k else 30}d) ───────────────────",
            f"  Views:             {k['window_views']:>12,}",
            f"  Watch Hours:       {k['watch_hours']:>12,.1f}",
            f"  Net Subscribers:   {k['net_subscribers']:>+12,}",
            f"    Gained:          {k['subscribers_gained']:>12,}",
            f"    Lost:            {k['subscribers_lost']:>12,}",
            f"  Avg View Duration: {k['avg_view_duration_min']:>12.1f} min",
            f"  Engagement Rate:   {k['engagement_rate_pct']:>12.2f}%",
            "",
            "── CHANNEL HEALTH ───────────────────────────────────",
            f"  Overall:     {h.overall:>6.1f}/100  [{h.label}]",
            f"  Growth:      {h.growth_score:>6.1f}/100",
            f"  Engagement:  {h.engagement_score:>6.1f}/100",
            f"  Consistency: {h.consistency_score:>6.1f}/100",
            f"  Influence:   {h.influence_score:>6.1f}/100",
            "",
            "── TREND ANALYSIS ───────────────────────────────────",
            f"  Direction:   {tr.direction.upper()}",
            f"  Slope:       {tr.slope:+.2f} views/day",
            f"  Volatility:  {tr.volatility:,.0f} (std dev)",
            f"  7-day momt:  {tr.momentum_7d:+.1f}%",
            f"  30-day momt: {tr.momentum_30d:+.1f}%",
            f"  Peak:        {tr.peak_views:,} views on {tr.peak_day}",
            "",
            "── TOP CONTENT ──────────────────────────────────────",
        ]
        for i, c in enumerate(summary.top_performers, 1):
            lines.append(f"  {i}. {c.title[:45]}")
            lines.append(f"     Views: {c.view_count:,}  ·  Engagement: {c.engagement_rate*100:.2f}%  ·  Score: {c.composite_score:.0f}/100")
            lines.append("")

        lines += [
            "── UNDERPERFORMERS ──────────────────────────────────",
        ]
        for i, c in enumerate(summary.underperformers, 1):
            lines.append(f"  {i}. {c.title[:45]}")
            lines.append(f"     Views: {c.view_count:,}  ·  Score: {c.composite_score:.0f}/100 (P{c.percentile_rank:.0f})")
            lines.append("")

        lines.append("═" * 60)
        return "\n".join(lines)

    def json_report(self, snapshot: FullAnalyticsSnapshot, summary: AnalyticsSummary) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "channel": {
                "platform":      snapshot.channel.platform,
                "id":            snapshot.channel.channel_id,
                "title":         snapshot.channel.channel_title,
                "subscribers":   snapshot.channel.subscriber_count,
                "video_count":   snapshot.channel.video_count,
                "total_views":   snapshot.channel.total_view_count,
            },
            "kpi": summary.kpi,
            "health": {
                "overall":      summary.channel_health.overall,
                "label":        summary.channel_health.label,
                "growth":       summary.channel_health.growth_score,
                "engagement":   summary.channel_health.engagement_score,
                "consistency":  summary.channel_health.consistency_score,
                "influence":    summary.channel_health.influence_score,
            },
            "trend": {
                "direction":     summary.trend.direction,
                "slope":         summary.trend.slope,
                "volatility":    summary.trend.volatility,
                "momentum_7d":   summary.trend.momentum_7d,
                "momentum_30d":  summary.trend.momentum_30d,
                "peak_day":      summary.trend.peak_day,
                "peak_views":    summary.trend.peak_views,
            },
            "content": [
                {
                    "id":              c.content_id,
                    "title":           c.title,
                    "views":           c.view_count,
                    "engagement_rate": c.engagement_rate,
                    "composite_score": c.composite_score,
                    "percentile_rank": c.percentile_rank,
                }
                for c in summary.content_scores
            ],
        }

    def save_json(self, snapshot: FullAnalyticsSnapshot, summary: AnalyticsSummary,
                  path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.json_report(snapshot, summary), f, indent=2)

    def save_text(self, snapshot: FullAnalyticsSnapshot, summary: AnalyticsSummary,
                  path: str) -> None:
        with open(path, "w") as f:
            f.write(self.text_report(snapshot, summary))
