"""
Analytics Engine

Computes derived, platform-agnostic metrics from a FullAnalyticsSnapshot.
All statistical computation lives here — adapters only parse/normalize.
"""
import statistics
from dataclasses import dataclass
from typing import Optional

from core.models import FullAnalyticsSnapshot, ContentItem, TimeSeriesPoint


@dataclass
class ContentScore:
    content_id: str
    title: str
    view_count: int
    engagement_rate: float
    composite_score: float       # 0–100 weighted index
    percentile_rank: float       # among all content in snapshot


@dataclass
class ChannelHealthScore:
    overall: float               # 0–100
    growth_score: float
    engagement_score: float
    consistency_score: float
    influence_score: float
    label: str                   # "Excellent" / "Good" / "Needs Attention" / "At Risk"


@dataclass
class TrendAnalysis:
    slope: float                 # views per day trend
    direction: str               # "up" / "down" / "flat"
    volatility: float            # std dev of daily views
    peak_day: str
    peak_views: int
    momentum_7d: float           # % change last 7 days vs prior 7
    momentum_30d: float


@dataclass
class AnalyticsSummary:
    channel_health: ChannelHealthScore
    trend: TrendAnalysis
    content_scores: list[ContentScore]
    top_performers: list[ContentScore]
    underperformers: list[ContentScore]
    kpi: dict                    # flat dict of headline KPIs


class AnalyticsEngine:

    # ──────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────

    def analyze(self, snapshot: FullAnalyticsSnapshot) -> AnalyticsSummary:
        trend          = self._compute_trend(snapshot.raw_time_series)
        content_scores = self._score_content(snapshot.content_items)
        health         = self._compute_health(snapshot, trend, content_scores)
        kpi            = self._build_kpi(snapshot, trend, health)

        ranked = sorted(content_scores, key=lambda c: c.composite_score, reverse=True)
        top    = ranked[:3]
        under  = ranked[-3:] if len(ranked) > 3 else []

        return AnalyticsSummary(
            channel_health=health,
            trend=trend,
            content_scores=content_scores,
            top_performers=top,
            underperformers=under,
            kpi=kpi,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Trend analysis
    # ──────────────────────────────────────────────────────────────────────

    def _compute_trend(self, ts: list[TimeSeriesPoint]) -> TrendAnalysis:
        if not ts:
            return TrendAnalysis(0, "flat", 0, "N/A", 0, 0.0, 0.0)

        views   = [p.views for p in ts]
        dates   = [p.date for p in ts]
        n       = len(views)

        # Linear regression slope
        x    = list(range(n))
        xm   = statistics.mean(x)
        ym   = statistics.mean(views)
        num  = sum((xi - xm) * (yi - ym) for xi, yi in zip(x, views))
        den  = sum((xi - xm) ** 2 for xi in x) or 1
        slope = num / den

        direction = "up" if slope > 2 else ("down" if slope < -2 else "flat")
        volatility = statistics.stdev(views) if n > 1 else 0.0

        peak_idx  = views.index(max(views))
        peak_day  = dates[peak_idx]
        peak_views = views[peak_idx]

        # Momentum: last 7 days vs prior 7
        m7 = self._momentum(views, 7)
        m30 = self._momentum(views, 30)

        return TrendAnalysis(
            slope=round(slope, 2),
            direction=direction,
            volatility=round(volatility, 2),
            peak_day=peak_day,
            peak_views=peak_views,
            momentum_7d=round(m7, 2),
            momentum_30d=round(m30, 2),
        )

    @staticmethod
    def _momentum(views: list[int], window: int) -> float:
        if len(views) < window * 2:
            return 0.0
        recent = sum(views[-window:])
        prior  = sum(views[-window * 2:-window])
        if prior == 0:
            return 0.0
        return (recent - prior) / prior * 100

    # ──────────────────────────────────────────────────────────────────────
    # Content scoring
    # ──────────────────────────────────────────────────────────────────────

    def _score_content(self, items: list[ContentItem]) -> list[ContentScore]:
        if not items:
            return []

        views_all = [c.view_count for c in items]
        max_views = max(views_all) or 1

        scores = []
        for item in items:
            eng_rate  = item.engagement_rate
            view_norm = item.view_count / max_views          # 0–1

            # Weighted composite: 50% views, 30% engagement, 20% algo scores
            algo_bonus = 0.0
            if item.engagement_score is not None:
                algo_bonus += item.engagement_score * 0.1
            if item.recommendation_score is not None:
                algo_bonus += item.recommendation_score * 0.1

            composite = (view_norm * 50) + (min(eng_rate, 0.2) / 0.2 * 30) + (algo_bonus * 20)
            scores.append((item, composite))

        # Percentile ranks
        composites = sorted([s[1] for s in scores])
        result = []
        for item, composite in scores:
            rank = (composites.index(composite) + 1) / len(composites) * 100
            result.append(ContentScore(
                content_id=item.content_id,
                title=item.title,
                view_count=item.view_count,
                engagement_rate=round(item.engagement_rate, 4),
                composite_score=round(composite, 2),
                percentile_rank=round(rank, 1),
            ))

        return sorted(result, key=lambda c: c.composite_score, reverse=True)

    # ──────────────────────────────────────────────────────────────────────
    # Channel health
    # ──────────────────────────────────────────────────────────────────────

    def _compute_health(
        self,
        snap: FullAnalyticsSnapshot,
        trend: TrendAnalysis,
        content_scores: list[ContentScore],
    ) -> ChannelHealthScore:
        aud = snap.audience
        perf = snap.performance

        # Growth score: net subs + momentum
        sub_rate = aud.net_subscribers / max(snap.channel.subscriber_count, 1) * 100
        growth = min(sub_rate * 10 + max(trend.momentum_30d, 0) / 2, 100)

        # Engagement score
        eng = min(perf.engagement_rate * 1000, 100)

        # Consistency score: inverse of volatility relative to mean views
        views = [p.views for p in snap.raw_time_series]
        mean_v = statistics.mean(views) if views else 1
        cv = trend.volatility / mean_v if mean_v else 1
        consistency = max(0, 100 - cv * 100)

        # Influence
        influence = aud.influence_score or 50.0

        overall = (growth * 0.30 + eng * 0.25 + consistency * 0.25 + influence * 0.20)
        overall = round(min(overall, 100), 1)

        label = (
            "Excellent"      if overall >= 80 else
            "Good"           if overall >= 60 else
            "Needs Attention" if overall >= 40 else
            "At Risk"
        )

        return ChannelHealthScore(
            overall=overall,
            growth_score=round(growth, 1),
            engagement_score=round(eng, 1),
            consistency_score=round(consistency, 1),
            influence_score=round(influence, 1),
            label=label,
        )

    # ──────────────────────────────────────────────────────────────────────
    # KPI dict
    # ──────────────────────────────────────────────────────────────────────

    def _build_kpi(
        self,
        snap: FullAnalyticsSnapshot,
        trend: TrendAnalysis,
        health: ChannelHealthScore,
    ) -> dict:
        aud  = snap.audience
        perf = snap.performance
        ch   = snap.channel

        return {
            # Channel
            "subscribers":          ch.subscriber_count,
            "total_videos":         ch.video_count,
            "total_views_all_time": ch.total_view_count,
            # Window
            "window_views":         aud.views,
            "net_subscribers":      aud.net_subscribers,
            "subscribers_gained":   aud.subscribers_gained,
            "subscribers_lost":     aud.subscribers_lost,
            "watch_hours":          round(aud.estimated_minutes_watched / 60, 1),
            "avg_view_duration_min":round(aud.avg_view_duration_minutes, 1),
            # Engagement
            "engagement_rate_pct":  round(perf.engagement_rate * 100, 2),
            "influence_score":      aud.influence_score,
            # Trend
            "trend_direction":      trend.direction,
            "momentum_7d_pct":      trend.momentum_7d,
            "momentum_30d_pct":     trend.momentum_30d,
            "peak_day":             trend.peak_day,
            "peak_views":           trend.peak_views,
            # Health
            "health_score":         health.overall,
            "health_label":         health.label,
            # Growth windows
            "weekly_views":         perf.weekly_growth.views,
            "monthly_views":        perf.monthly_growth.views,
            "weekly_follower_growth": perf.weekly_growth.follower_growth,
            "monthly_follower_growth": perf.monthly_growth.follower_growth,
        }
