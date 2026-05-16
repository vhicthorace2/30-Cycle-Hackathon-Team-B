# """
# DTOs for data received from backend for ML scoring.
# These structures represent what the backend will send to ML endpoints.
# """
# from dataclasses import dataclass, field
# from datetime import datetime
# from typing import Optional, List


# @dataclass
# class CommentMetadata:
#     """Single comment with metadata for sentiment analysis."""
#     comment_id: str
#     text: str
#     author_id: str
#     author_name: str
#     published_at: datetime
#     like_count: int = 0
#     reply_count: int = 0
#     is_from_subscriber: bool = False
#     is_pinned: bool = False


# @dataclass
# class VideoMetricsInput:
#     """Per-video metrics from YouTube Analytics API (free tier optimized)."""
#     video_id: str
#     title: str
#     description: str
#     published_at: datetime
#     view_count: int
#     like_count: int
#     comment_count: int
#     average_view_duration_seconds: int
#     video_duration_seconds: int
#     category_id: str
#     thumbnail_url: Optional[str] = None
#     comments_sample: List[CommentMetadata] = field(default_factory=list)  # 10-20 comment samples max


# @dataclass
# class ChannelMetricsInput:
#     """Channel-level metrics from YouTube APIs."""
#     channel_id: str
#     channel_name: str
#     channel_description: str
#     subscriber_count: int
#     total_view_count: int
#     video_count: int
#     account_creation_date: datetime
#     is_verified: bool
#     profile_picture_url: Optional[str] = None
#     banner_url: Optional[str] = None


# @dataclass
# class AudienceMetricsInput:
#     """Audience analytics from YouTube Analytics API (time-windowed, free tier optimized)."""
#     window_days: int  # 7 or 30 days
#     views: int
#     watch_time_minutes: int
#     subscribers_gained: int
#     subscribers_lost: int
#     average_view_duration_seconds: int
    
#     # Demographics (simplified - 3 key brackets only)
#     age_young_pct: float  # 13-24
#     age_mid_pct: float    # 25-44
#     age_older_pct: float  # 45+
    
#     # Gender (simplified)
#     gender_male_pct: float
#     gender_female_pct: float
    
#     # Top countries (just 2-3 primary)
#     top_countries: List[str] = field(default_factory=list)
    
#     # Traffic sources (consolidated)
#     organic_views: int = 0  # search + suggested combined
#     direct_views: int = 0
    
#     # Device breakdown (simplified)
#     mobile_views_pct: float = 0.0
#     desktop_views_pct: float = 0.0


# @dataclass
# class MLScoringRequest:
#     """
#     Complete request from backend to ML module for scoring.
#     Optimized for free tier API limits - minimal data overhead.
#     """
#     request_id: str
#     creator_id: str
#     channel: ChannelMetricsInput
#     audience: AudienceMetricsInput  # Single 30-day window
#     videos: List[VideoMetricsInput]  # Last 10-15 videos only
#     timestamp: datetime = field(default_factory=datetime.utcnow)


# @dataclass
# class BrandProfileInput:
#     """Brand/SME profile for recommendation matching."""
#     brand_id: str
#     brand_name: str
#     brand_description: str
#     target_audience_age_min: int
#     target_audience_age_max: int
#     target_audience_gender: str  # "all", "male", "female"
#     target_countries: List[str]  # ISO country codes
#     target_interests: List[str]  # Keywords/interests
#     budget_min_usd: float
#     budget_max_usd: float
#     industry: str  # e.g., "fashion", "tech", "health", etc.
#     previous_collaborations: int = 0


# @dataclass
# class RecommendationRequest:
#     """Request for creator recommendations for a brand."""
#     request_id: str
#     brand: BrandProfileInput
#     candidate_creators: List[MLScoringRequest]  # Creators to rank
#     num_recommendations: int = 5  # Top N to return
#     timestamp: datetime = field(default_factory=datetime.utcnow)

"""
DTOs for data received from backend for ML scoring.
OPTIMIZED for minimal YouTube API data usage (free tier).
Uses ONLY YouTube Data API v3 - no Analytics API required.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CommentMetadata:
    """
    Single comment for sentiment analysis.
    Limited to 5-8 comments per video (minimal quota impact).
    """
    comment_id: str
    text: str
    like_count: int
    published_at: datetime
    author_subscriber_count: int  # Key indicator of commenter loyalty
    is_reply: bool = False  # Skip replies to save quota


@dataclass
class VideoMetricsInput:
    """
    Per-video metrics from YouTube Data API only.
    ONE API call per video (videos.list + commentThreads.list).
    """
    video_id: str
    title: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    
    # Engagement quality indicators (available via Data API)
    favorite_count: int  # Underrated engagement signal
    
    # Optional - can skip if quota tight
    tags: List[str] = field(default_factory=list)  # For content categorization
    
    # STRICT LIMIT: Max 5 comments per video (not 10-20)
    comments_sample: List[CommentMetadata] = field(default_factory=list)  # 3-5 comments max


@dataclass
class ChannelMetricsInput:
    """
    Channel-level metrics from YouTube Data API only.
    ONE API call per channel (channels.list).
    """
    channel_id: str
    channel_name: str
    subscriber_count: int  # Primary loyalty signal
    total_view_count: int
    video_count: int
    account_creation_date: datetime  # For growth rate calculation
    is_verified: bool
    country: str  # For local relevance (Nigeria/Africa focus)
    
    # Optional but valuable for African market
    custom_url: Optional[str] = None  # Indicates established creator
    hidden_subscriber_count: bool = False  # Red flag indicator


@dataclass
class PlaylistMetricsInput:
    """
    Playlist data for content consistency scoring.
    Minimal API cost: ONE playlists.list call.
    """
    playlist_id: str
    title: str
    video_count: int  # Consistency indicator
    created_at: datetime
    
    # Key for cross-platform growth behavior
    is_collaboration_playlist: bool = False  # Suggests network effects


@dataclass
class ChannelGrowthInput:
    """
    Growth metrics derived from channel + video timestamps.
    NO EXTRA API CALLS - calculated from existing data.
    """
    days_since_first_video: int
    videos_per_month: float  # Consistency score
    subscriber_growth_rate: float  # Estimated Δsubscribers/day
    upload_frequency_consistency: float  # Standard deviation of intervals


@dataclass
class MLScoringRequest:
    """
    Complete request from backend to ML module for scoring.
    OPTIMIZED: Uses only Data API v3, no Analytics API.
    Total API calls per creator: ~16-20 (within free tier limits)
    """
    request_id: str
    creator_id: str
    channel: ChannelMetricsInput
    videos: List[VideoMetricsInput]  # Last 8-10 videos only (not 15)
    playlists: List[PlaylistMetricsInput] = field(default_factory=list)  # Max 5 playlists
    growth: Optional[ChannelGrowthInput] = None  # Calculated by backend
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MinimalAudienceSignal:
    """
    Audience quality INFERRED from comments + channel metrics.
    NO dedicated audience API calls - derived from existing data.
    """
    # From comment authors
    estimated_subscriber_loyalty: float = 0.0  # % of commenters subscribed
    
    # From video metrics
    avg_like_to_view_ratio: float = 0.0  # Engagement quality proxy
    avg_comment_to_view_ratio: float = 0.0
    
    # From channel metadata
    has_local_relevance: bool = False  # Based on channel.country
    is_verified_creator: bool = False
    
    # Sentiment from comments (processed by ML)
    comment_sentiment_score: float = 0.0  # -1 to +1


@dataclass
class BrandProfileInput:
    """
    Brand/SME profile for recommendation matching.
    Tailored for Nigerian/African market.
    """
    brand_id: str
    brand_name: str
    industry: str  # "fashion", "tech", "beauty", "finance", "gaming", "health", "education", "entertainment"
    
    # Target audience (simplified for African market)
    target_age_range: str  # "13-24", "25-34", "35+", "all"
    target_gender: str  # "all", "male", "female"
    target_countries: List[str]  # "NG", "KE", "GH", "ZA", etc.
    
    # Budget (in local currency or USD)
    budget_range_usd: tuple  # (min, max) e.g., (100, 500)
    
    # Content compatibility
    preferred_content_categories: List[str] = field(default_factory=list)  # Matches video tags
    language_preference: str = "en"  # "en", "pcm"(Nigerian Pidgin), "ha", "yo", "ig"
    
    # Optional engagement metrics
    minimum_subscriber_count: int = 0
    maximum_subscriber_count: int = float('inf')
    minimum_engagement_rate: float = 0.0  # 0-100


@dataclass
class RecommendationRequest:
    """
    Request for creator recommendations for a brand.
    Returns scored and ranked creators based on simple metrics + local relevance.
    """
    request_id: str
    brand: BrandProfileInput
    candidate_scores: List['CreatorScore']  # Pre-calculated scores to rank
    num_recommendations: int = 5
    
    # Local relevance boost (Nigerian/African market)
    prefer_local_creators: bool = True  # Prioritize creators in target_countries
    prefer_pidgin_english: bool = True  # Nigerian market specific
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorScore:
    """
    ML scoring output using the simplified formula from your tasks.
    Score = (Engagement Rate × 0.4) + (Growth Rate × 0.3) + 
            (Post Consistency × 0.2) + (Audience Quality × 0.1)
    """
    creator_id: str
    channel_name: str
    
    # Individual metrics
    engagement_rate: float  # (likes+comments)/views × 100
    growth_rate: float  # subscriber growth per month
    post_consistency: float  # 0-1 (based on variance in upload frequency)
    audience_quality: float  # Derived from comment sentiment + subscriber ratio
    
    # Final score (0-100)
    total_score: float
    
    # Local relevance bonus (African market)
    local_relevance_score: float = 0.0  # Added to total if applicable
    
    # Optional NLP sentiment score from comments
    sentiment_score: float = 0.0  # -1 to +1
    
    # Prediction (simplified)
    predicted_roi_category: str = "medium"  # "low", "medium", "high"
    
    # For debugging/dashboard display
    video_sample_count: int = 0
    analyzed_comment_count: int = 0