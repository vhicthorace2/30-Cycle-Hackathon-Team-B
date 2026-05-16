"""
YouTube Platform Adapter

Supports two API shapes:
  1. /auth/socials/google/youtube/metrics  (raw Google API passthrough)
  2. /creators/insights/*                  (enriched creator insights endpoints)

Both are normalized into the platform-agnostic core models.
"""
from datetime import datetime
from typing import Optional
import requests

from core.base_adapter import BasePlatformAdapter
from core.models import (
    ChannelProfile, ContentItem, TimeSeriesPoint,
    AudienceMetrics, GrowthWindow, PerformanceReport, FullAnalyticsSnapshot
)


class YouTubeAdapter(BasePlatformAdapter):
    PLATFORM_NAME = "youtube"
    def fetch_snapshot(self, days: int = 30, max_content: int = 10) -> FullAnalyticsSnapshot:
        """
        Orchestrates calls across both endpoint groups and merges the result
        into a single FullAnalyticsSnapshot.
        """
        raw_metrics   = self._fetch_raw_metrics(days=days, max_videos=max_content)
        audience_data = self._fetch_audience_insights(days=days)
        content_data  = self._fetch_content_insights(days=days, limit=max_content)
        perf_data     = self._fetch_performance_insights(days=days, limit=max_content)

        channel  = self._parse_channel(raw_metrics, audience_data)
        audience = self._parse_audience(audience_data)
        content  = self._parse_content(content_data, raw_metrics)
        ts       = self._parse_time_series(perf_data, raw_metrics)
        perf     = self._parse_performance(perf_data, content)

        return FullAnalyticsSnapshot(
            channel=channel,
            audience=audience,
            content_items=content,
            performance=perf,
            raw_time_series=ts,
            fetched_at=datetime.utcnow(),
        )

    def health_check(self) -> bool:
        try:
            self._fetch_raw_metrics(days=1, max_videos=1)
            return True
        except Exception:
            return False

    def _fetch_raw_metrics(self, days: int, max_videos: int) -> dict:
        return self._get(
            "/auth/socials/google/youtube/metrics",
            params={"days": days, "maxVideos": max_videos},
        )

    def _fetch_audience_insights(self, days: int) -> dict:
        return self._get("/creators/insights/audience", params={"days": days})

    def _fetch_content_insights(self, days: int, limit: int) -> dict:
        return self._get("/creators/insights/content", params={"days": days, "limit": limit})

    def _fetch_performance_insights(self, days: int, limit: int = 10) -> dict:
        return self._get("/creators/insights/performance", params={"days": days, "limit": limit})


    def _parse_channel(self, raw: dict, audience: dict) -> ChannelProfile:
        # Raw metrics uses Google's nested structure; insights uses flat
        ch_raw  = raw.get("channel", {})
        ch_ins  = audience.get("channel", {})
        stats   = ch_raw.get("statistics", {})

        return ChannelProfile(
            platform="youtube",
            channel_id=(
                ch_raw.get("id")
                or ch_ins.get("youtubeChannelId", "unknown")
            ),
            channel_title=ch_ins.get("channelTitle", ch_raw.get("snippet", {}).get("title", "Unknown Channel")),
            subscriber_count=int(
                ch_ins.get("subscriberCount")
                or stats.get("subscriberCount", 0)
            ),
            total_view_count=int(
                ch_ins.get("totalViewCount")
                or stats.get("viewCount", 0)
            ),
            video_count=int(
                ch_ins.get("videoCount")
                or stats.get("videoCount", 0)
            ),
        )

    def _parse_audience(self, data: dict) -> AudienceMetrics:
        aud = data.get("audience", {})
        return AudienceMetrics(
            views=aud.get("views", 0),
            estimated_minutes_watched=aud.get("estimatedMinutesWatched", 0),
            average_view_duration_seconds=aud.get("averageViewDurationSeconds", 0),
            subscribers_gained=aud.get("subscribersGained", 0),
            subscribers_lost=aud.get("subscribersLost", 0),
            influence_score=data.get("influenceScore"),
        )

    def _parse_content(self, content_data: dict, raw: dict) -> list[ContentItem]:
        items: list[ContentItem] = []

        # Primary: enriched content insights
        for item in content_data.get("items", []):
            score = item.get("score", {})
            pub = item.get("publishedAt")
            items.append(ContentItem(
                platform="youtube",
                content_id=item.get("youtubeVideoId", ""),
                title=item.get("title", "Untitled"),
                view_count=item.get("viewCount", 0),
                like_count=item.get("likeCount", 0),
                comment_count=item.get("commentCount", 0),
                published_at=datetime.fromisoformat(pub.replace("Z", "+00:00")) if pub else None,
                engagement_score=score.get("engagementScore"),
                growth_score=score.get("growthScore"),
                recommendation_score=score.get("recommendationScore"),
                performance_rank=score.get("performanceRank"),
            ))

        # Fallback: raw video list from /metrics endpoint
        if not items:
            for v in raw.get("videos", []):
                stats = v.get("statistics", {})
                snippet = v.get("snippet", {})
                pub = snippet.get("publishedAt")
                items.append(ContentItem(
                    platform="youtube",
                    content_id=v.get("id", ""),
                    title=snippet.get("title", "Untitled"),
                    view_count=int(stats.get("viewCount", 0)),
                    like_count=int(stats.get("likeCount", 0)),
                    comment_count=int(stats.get("commentCount", 0)),
                    published_at=datetime.fromisoformat(pub.replace("Z", "+00:00")) if pub else None,
                ))

        return items

    def _parse_time_series(self, perf: dict, raw: dict) -> list[TimeSeriesPoint]:
        points: list[TimeSeriesPoint] = []

        # Primary: performance insights time series
        for entry in perf.get("timeSeries", []):
            points.append(TimeSeriesPoint(
                date=entry["date"],
                views=entry.get("views", 0),
                subscribers_gained=entry.get("subscribersGained", 0),
                subscribers_lost=entry.get("subscribersLost", 0),
                estimated_minutes_watched=entry.get("estimatedMinutesWatched", 0),
            ))

        # Fallback: raw analytics rows
        if not points:
            analytics = raw.get("analytics", {})
            headers = [h["name"] for h in analytics.get("columnHeaders", [])]
            for row in analytics.get("rows", []):
                row_dict = dict(zip(headers, row))
                points.append(TimeSeriesPoint(
                    date=row_dict.get("day", row_dict.get("date", "")),
                    views=int(row_dict.get("views", 0)),
                    subscribers_gained=int(row_dict.get("subscribersGained", 0)),
                    subscribers_lost=int(row_dict.get("subscribersLost", 0)),
                    estimated_minutes_watched=int(row_dict.get("estimatedMinutesWatched", 0)),
                ))

        return sorted(points, key=lambda p: p.date)

    def _parse_performance(self, perf: dict, content: list[ContentItem]) -> PerformanceReport:
        def _gw(data: dict) -> GrowthWindow:
            return GrowthWindow(
                window_days=data.get("windowDays", 0),
                follower_growth=data.get("followerGrowth", 0),
                views=data.get("views", 0),
                estimated_minutes_watched=data.get("estimatedMinutesWatched", 0),
            )

        weekly  = _gw(perf.get("weeklyGrowth", {}))
        monthly = _gw(perf.get("monthlyGrowth", {}))

        # Top content from performance endpoint or fall back to our content list
        top_raw = perf.get("topContent", [])
        if top_raw:
            top = []
            for t in top_raw:
                top.append(ContentItem(
                    platform="youtube",
                    content_id=t.get("youtubeVideoId", ""),
                    title=t.get("title", ""),
                    view_count=t.get("viewCount", 0),
                    like_count=t.get("likeCount", 0),
                    comment_count=t.get("commentCount", 0),
                    performance_rank=t.get("performanceRank"),
                ))
        else:
            top = sorted(content, key=lambda c: c.view_count, reverse=True)[:5]

        ts = self._parse_time_series(perf, {})

        return PerformanceReport(
            window_days=perf.get("windowDays", 30),
            weekly_growth=weekly,
            monthly_growth=monthly,
            engagement_rate=perf.get("engagementRate", 0.0),
            time_series=ts,
            top_content=top,
            platform_breakdown=perf.get("platforms", []),
        )
