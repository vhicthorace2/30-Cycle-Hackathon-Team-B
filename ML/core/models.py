"""
Platform-agnostic data models for the analytics platform.
All platform adapters normalize into these structures.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChannelProfile:
    platform: str
    channel_id: str
    channel_title: str
    subscriber_count: int
    total_view_count: int
    video_count: int
    fetched_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentItem:
    platform: str
    content_id: str
    title: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime] = None
    engagement_score: Optional[float] = None
    growth_score: Optional[float] = None
    recommendation_score: Optional[float] = None
    performance_rank: Optional[int] = None

    @property
    def engagement_rate(self) -> float:
        if self.view_count == 0:
            return 0.0
        return (self.like_count + self.comment_count) / self.view_count


@dataclass
class TimeSeriesPoint:
    date: str
    views: int
    subscribers_gained: int = 0
    subscribers_lost: int = 0
    estimated_minutes_watched: int = 0

    @property
    def net_subscribers(self) -> int:
        return self.subscribers_gained - self.subscribers_lost


@dataclass
class AudienceMetrics:
    views: int
    estimated_minutes_watched: int
    average_view_duration_seconds: int
    subscribers_gained: int
    subscribers_lost: int
    influence_score: Optional[float] = None

    @property
    def net_subscribers(self) -> int:
        return self.subscribers_gained - self.subscribers_lost

    @property
    def avg_view_duration_minutes(self) -> float:
        return self.average_view_duration_seconds / 60


@dataclass
class GrowthWindow:
    window_days: int
    follower_growth: int
    views: int
    estimated_minutes_watched: int


@dataclass
class PerformanceReport:
    window_days: int
    weekly_growth: GrowthWindow
    monthly_growth: GrowthWindow
    engagement_rate: float
    time_series: list[TimeSeriesPoint]
    top_content: list[ContentItem]
    platform_breakdown: list[dict]


@dataclass
class FullAnalyticsSnapshot:
    """Complete analytics state for a creator at a point in time."""
    channel: ChannelProfile
    audience: AudienceMetrics
    content_items: list[ContentItem]
    performance: PerformanceReport
    raw_time_series: list[TimeSeriesPoint]
    fetched_at: datetime = field(default_factory=datetime.utcnow)
